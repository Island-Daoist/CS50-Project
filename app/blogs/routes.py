from app.blogs import bp
from app import db
from flask import render_template, url_for, flash, redirect, request, current_app
from flask_login import login_required, fresh_login_required, current_user
from app.blogs.forms import CreateBlogForm, UpdateBlogForm
from app.models import Users, Blogs


@bp.route('/blogs', methods=['GET'])
def view_blogs():
    page = request.args.get('page', 1, type=int)
    blogs_list = Blogs.query.order_by(Blogs.timestamp.desc()).paginate(
            page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('blogs.view_blogs', blog_page=blogs_list.next_num) if blogs_list.has_next else None
    prev_url = url_for('blogs.view_blogs', blog_page=blogs_list.prev_num) if blogs_list.has_prev else None
    return render_template('blogs/view_blogs.html', title='View Blogs',
                           blogs_list=blogs_list.items, prev_url=prev_url, next_url=next_url)


@bp.route('/blogs/<blog_id>', methods=['GET'])
def blog(blog_id):
    blog_viewed = Blogs.query.filter_by(id=blog_id).first()
    if blog_viewed is None:
        flash('Sorry, but this blog could not be opened')
        return redirect(url_for('blogs.view_blogs'))
    return render_template('blogs/blog.html', title=f'Blog {blog_viewed.title}',
                           blog_viewed=blog_viewed)


@bp.route('/<username>/blogs')
@login_required
def view_own_blogs(username):
    user = Users.query.filter_by(username=username).first()
    if user is None or user != current_user:
        flash('Sorry, could not load page')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    user_blogs = Blogs.query.filter_by(author=user).order_by(Blogs.timestamp.desc()).paginate(
            page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('blogs.view_blogs', blog_page=user_blogs.next_num) if user_blogs.has_next else None
    prev_url = url_for('blogs.view_blogs', blog_page=user_blogs.prev_num) if user_blogs.has_prev else None
    return render_template('blogs/view_blogs.html', title=f'{current_user.username}\'s Blogs!',
                           blogs_list=user_blogs.items, prev_url=prev_url, next_url=next_url)


@bp.route('/<username>/create-blog', methods=['GET', 'POST'])
@login_required
def create_blog(username):
    user = Users.query.filter_by(username=username).first_or_404()
    if user != current_user:
        flash('This is not your page!')
        return redirect(url_for('main.index'))
    form = CreateBlogForm()
    if form.validate_on_submit():
        blog = Blogs(title=form.title.data, synopsis=form.synopsis.data,
                     body=form.body.data, author=current_user)
        db.session.add(blog)
        db.session.commit()
        flash('Your blog has been posted!')
        return redirect(url_for('main.index'))
    return render_template('blogs/create_blog.html', title='Write a Blog!',
                           form=form)


@bp.route('/<username>/update-blog/<blog_id>', methods=['GET', 'POST'])
@fresh_login_required
def update_blog(username, blog_id):
    user = Users.query.filter_by(username=username).first()
    if current_user != user:
        flash('Sorry, you are not the author of this blog')
        return redirect(url_for('main.index'))
    blog = Blogs.query.filter_by(id=blog_id).first()
    if blog is None:
        flash('Could not open this blog to edit')
        return redirect(url_for('blogs.view_blogs'))
    form = UpdateBlogForm(obj=blog, original_title=blog.title)
    if form.validate_on_submit():
        form.populate_obj(blog)
        db.session.commit()
        flash('Your blog has been updated!')
        return redirect(url_for('blogs.blog', blog_id=blog.id))
    return render_template('blogs/update_blog.html', title=f'Update Blog {blog.title}',
                           form=form)
