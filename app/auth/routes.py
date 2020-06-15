from app.auth import bp
from flask import render_template, url_for, g, flash, redirect, request
from app.auth.forms import LoginForm, RegisterForm, ValidateUser, ResetPassword, ResetPasswordRequest
from app.auth.email import send_password_reset_email
from flask_login import current_user, login_user, logout_user, confirm_login
from app.models import Users
from app import db
from werkzeug.urls import url_parse


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Login', form=form)


@bp.route('/validate', methods=['GET', 'POST'])
def validate():
    form = ValidateUser()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if not user or user.username != current_user.username:
            flash('Please enter your username to validate your account.')
            return redirect(url_for('auth.validate'))
        if not user.check_password(form.password.data):
            flash('Your password is incorrect, please try again.')
            return redirect(url_for('auth.validate'))
        confirm_login()
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/validate', title='Validate your Account', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = Users(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you have been registered!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequest()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for instructions on how to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', title='Reset Your Password',
                           form=form)


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = Users.verify_password_reset_token(token)
    if not user:
        return redirect(url_for('auth.login'))
    form = ResetPassword()
    if form.validate_on_submit():
        user.set_password(form.password_1.data)
        db.session.commit()
        flash('Your password has been reset')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', title='Reset your Password',
                           form=form)
