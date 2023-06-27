from app import app, db, mail
from flask import render_template, request, redirect, flash, url_for
from flask_login import current_user, login_user, logout_user, login_required
from models import User
from forms import LoginForm, SignUpForm
from flask_mail import Message
from logic import get_concate_username
from oauth import OAuthSignIn


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/send_mail')
def send_mail():
    msg = Message(subject="Does this work",
                  sender="u.n0wen@yandex.ru",
                  recipients=["1offkinda@gmail.com"])
    msg.body = "Yandex thinks this is spam. I wish :("
    msg.html = "<b>Yandex thinks this is spam. I wish :(</b>"
    mail.send(msg)
    return redirect(url_for("index"))


@app.route('/profile')
@login_required
def profile():
    name = current_user.username
    date = current_user.join_date
    avi = current_user.avatar(150)
    return render_template('profile.html', name=name, date=date, avi=avi)


@app.route('/temp1')
@login_required
def temp_page():
    return render_template('temp1.html')


@app.route('/temp2')
def temp2_page():
    text = request.args.get('text')
    return render_template('temp_page_2.html', text=text)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('temp_page'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('temp_page'))
    form = SignUpForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('temp_page'))
    return render_template("signup.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/userlist')
@login_required
def userlist():
    all_users = User.query.all()
    return render_template("userlist.html", users=all_users)


@app.route('/add_friend/<username>')
def add_friend(username):
    user = User.query.filter_by(username=username).first()
    if not user is None:
        current_user.add_friend(user)
        db.session.commit()
    return redirect(url_for('userlist'))


@app.route('/remove_friend/<username>')
def remove_friend(username):
    user = User.query.filter_by(username=username).first()
    if not user is None:
        current_user.delete_friend(user)
        db.session.commit()
    return redirect(url_for('userlist'))


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('login'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('login'))
    oauth = OAuthSignIn.get_provider(provider)
    user_id, token = oauth.callback()
    if user_id is None:
        flash('Authentication failed.')
        return redirect(url_for('login'))
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        username = get_concate_username(token, user_id)

        user = User(user_id=user_id, token=token, username=username)
        db.session.add(user)
        db.session.commit()

    login_user(user, True)
    return redirect(url_for('login'))
