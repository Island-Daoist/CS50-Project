from app.main import bp
from app import db
from flask import render_template, url_for, flash, redirect, request, current_app
from flask_login import login_required, fresh_login_required, current_user
from app.main.forms import UpdateProfileForm, StatusForm, MessageForm
from app.models import Users, Status, Messages, Blogs
from datetime import datetime


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    form = StatusForm()
    # if request.method == 'POST' and form.submit():
    if form.validate_on_submit():
        status = Status(body=form.status.data, author=current_user)
        db.session.add(status)
        db.session.commit()
        flash('Your status has been updated!')
        return redirect(url_for('main.index'))
    # verbose version of following line of operating code
    # if current_user.is_authenticated:
    #     user_status = Status.query.filter_by(user_id=current_user.id).order_by(Status.timestamp.desc())
    # else:
    #     user_status = Status.query.order_by(Status.timestamp.desc())

    if current_user.is_authenticated:
        post_page = request.args.get('post_page', 1, type=int)
        shown_posts = current_user.related_posts().paginate(
            post_page, current_app.config['POSTS_PER_PAGE'], False, max_per_page=10)
        if not shown_posts.items:
            shown_posts = Status.query.order_by(Status.timestamp.desc()).paginate(
                post_page, current_app.config['POSTS_PER_PAGE'], False, max_per_page=10)
        post_next_url = url_for('main.index', post_page=shown_posts.next_num) if shown_posts.has_next else None
        post_prev_url = url_for('main.index', post_page=shown_posts.prev_num) if shown_posts.has_prev else None
    else:
        post_page = request.args.get('post_page', 1, type=int)
        shown_posts = Status.query.order_by(Status.timestamp.desc()).paginate(
            post_page, current_app.config['POSTS_PER_PAGE'], False, max_per_page=10)
        post_next_url = url_for('main.index', post_page=shown_posts.next_num) if shown_posts.has_next else None
        post_prev_url = url_for('main.index', post_page=shown_posts.prev_num) if shown_posts.has_prev else None
    blog_page = request.args.get('blog_page', 1, type=int)
    blogs = Blogs.query.order_by(Blogs.timestamp.desc()).paginate(
        blog_page, current_app.config['POSTS_PER_PAGE'], False, max_per_page=10)
    blog_next_url = url_for('main.index', blog_page=blogs.next_num) if blogs.has_next else None
    blog_prev_url = url_for('main.index', blog_page=blogs.prev_num) if blogs.has_prev else None
    return render_template('main/index.html', title='Welcome to the Blog!', form=form,
                           shown_posts=shown_posts.items, post_next_url=post_next_url, post_prev_url=post_prev_url,
                           blogs=blogs.items, blog_next_url=blog_next_url, blog_prev_url=blog_prev_url)


@bp.route('/user/<username>')
@login_required
def profile(username):
    user = Users.query.filter_by(username=username).first_or_404()
    status_page = request.args.get('status_page', 1, type=int)
    statuses = user.status.order_by(Status.timestamp.desc()).paginate(
        status_page, current_app.config["POSTS_PER_PAGE"], False)
    status_next_url = url_for('main.profile', username=username,
                              status_page=statuses.next_num) if statuses.has_next else None
    status_prev_url = url_for('main.profile', username=username,
                              status_page=statuses.prev_num) if statuses.has_prev else None
    blog_page = request.args.get('blog_page', 1, type=int)
    blogs = Blogs.query.filter_by(user_id=user.id).paginate(
        blog_page, current_app.config['POSTS_PER_PAGE'], False)
    blog_next_url = url_for('main.profile', username=username,
                            blog_page=blogs.next_num) if blogs.has_next else None
    blog_prev_url = url_for('main.profile', username=username,
                            blog_page=blogs.next_num) if blogs.has_next else None
    return render_template('main/profile.html', title='Profile', user=user,
                           statuses=statuses.items, status_next_url=status_next_url,
                           status_prev_url=status_prev_url,
                           blogs=blogs.items, blog_next_url=blog_next_url, blog_prev_url=blog_prev_url)


@bp.route('/user/<username>/update', methods=['GET', 'POST'])
@fresh_login_required
def update_profile(username):
    user = Users.query.filter_by(username=username).first()
    if current_user != user:
        flash('This is not your profile!')
        return redirect(url_for('main.index'))
    form = UpdateProfileForm(obj=user, original_username=current_user.username)
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        flash('Your profile has been updated!')
        return redirect(url_for('main.profile', username=current_user.username))
    return render_template('main/update_profile.html', title='Update your Profile', form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = Users.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} was not found.')
        return redirect(url_for('main.index'))
    if current_user == user:
        flash('You cannot follow yourself!')
        return redirect(url_for('main.index'))
    current_user.follow(user)
    db.session.commit()
    flash(f'You are now following {username}!')
    return redirect(url_for('main.profile', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = Users.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} was not found.')
        return redirect(url_for('main.index'))
    if current_user == user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('main.index'))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You are no longer following {username}.')
    return redirect(url_for('main.profile', username=username))


@bp.route('/friend-request/<username>')
@login_required
def friend_request(username):
    user = Users.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} could not be found.')
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot send yourself a friend request!')
        return redirect(url_for('main.index'))
    user.add_friend_request(current_user)
    db.session.commit()
    flash(f'You have sent a friend request to {username}.')
    return redirect(url_for('main.profile', username=username))


@bp.route('/requests/<username>', methods=['GET', 'POST'])
@login_required
def pending_requests(username):
    if request.method == 'POST':
        user = Users.query.filter_by(id=request.form.get('accept')).first() if request.form.get('accept') \
            else Users.query.filter_by(id=request.form.get('deny')).first()
        if user is not None and user in current_user.pending_friend_requests:
            if request.form.get('accept'):
                flash(f'On your way to accepting friend request from {user.username}!')
                current_user.add_friend(user)
                current_user.pending_friend_requests.remove(user)
                db.session.commit()
                return redirect(url_for('main.index'))
            elif request.form.get('deny'):
                flash(f'You are readying to deny a friend request from {user.username}.')
                current_user.pending_friend_requests.remove(user)
                db.session.commit()
                return redirect(url_for('main.index'))
    user = Users.query.filter_by(username=username).first()
    if user is None:
        flash(f'Could not find user {username}.')
        return redirect(url_for('main.index'))
    if user != current_user:
        flash('This is not your page!')
        return redirect(url_for('main.index'))
    pending_friend_requests = user.pending_friend_requests.all()
    return render_template('main/pending_requests.html', title='View Your Pending Requests',
                           user=user, requests=pending_friend_requests)


@bp.route('/unfriend/<username>')
@login_required
def unfriend(username):
    user = Users.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} could not be found.')
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfriend yourself!')
        return redirect(url_for('main.index'))
    current_user.unfriend(user)
    db.session.commit()
    flash(f'You are no longer friends with {username}.')
    return redirect(url_for('main.profile', username=username))


@bp.route('/send-message/<user>', methods=['GET', 'POST'])
@login_required
def send_message(user):
    user = Users.query.filter_by(username=user).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        message = Messages(
            author=current_user,
            recipient=user,
            body=form.message.data)
        db.session.add(message)
        db.session.commit()
        flash('Your message was sent.')
        return redirect(url_for('main.profile', username=user.username))
    return render_template('main/send_message.html', title='Send a Message',
                           form=form, user=user)


@bp.route('/messages')
@login_required
def messages():
    current_user.message_last_read_time = datetime.utcnow()
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    messages = current_user.messages_received.order_by(
        Messages.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('main.messages', page=messages.prev_num) \
        if messages.has_prev else None
    return render_template('main/view_messages.html', messages=messages.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/<user>/user-popup')
@login_required
def user_popup(user):
    user = Users.query.filter_by(username=user).first_or_404()
    return render_template('user_popup.html', user=user)
