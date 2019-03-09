import os
import json
import datetime
from flask import Flask, url_for, redirect, render_template, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, UserMixin
from requests_oauthlib import OAuth2Session
from requests.exceptions import HTTPError
from config.config import Auth, DevConfig, ProdConfig, admin_accounts, student_accounts, students, information
from util.data import visualise, wordcloud

config = {
    "dev": DevConfig,
    "prod": ProdConfig,
    "default": DevConfig
}

"""APP creation and configuration"""
app = Flask(__name__)
app.config.from_object(config['dev'])
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"

""" DB Models """
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    admin = db.Column(db.Integer, default=0)
    avatar = db.Column(db.String(200))
    tokens = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


""" OAuth Session creation """
def get_google_auth(state=None, token=None):
    if token:
        return OAuth2Session(Auth.CLIENT_ID, token=token)
    if state:
        return OAuth2Session(
            Auth.CLIENT_ID,
            state=state,
            redirect_uri=Auth.REDIRECT_URI)
    oauth = OAuth2Session(
        Auth.CLIENT_ID,
        redirect_uri=Auth.REDIRECT_URI,
        scope=Auth.SCOPE)
    return oauth

@app.route('/')
# @login_required
def home():
	return redirect(url_for('home'))
	if not current_user.is_authenticated:
		return redirect(url_for('login'))
	return render_template('home.html', current_user=current_user, students=students)

@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    google = get_google_auth()
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline')
    session['oauth_state'] = state
    return redirect(auth_url)

@app.route('/gCallback')
def callback():
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('home'))
    if 'error' in request.args:
        if request.args.get('error') == 'access_denied':
            return 'You are denied access.'
        return 'Error encountered.'
    if 'code' not in request.args and 'state' not in request.args:
        return redirect(url_for('login'))
    else:
        google = get_google_auth(state=session['oauth_state'])
        try:
            token = google.fetch_token(
                Auth.TOKEN_URI,
                client_secret=Auth.CLIENT_SECRET,
                authorization_response=request.url)
        except HTTPError:
            return 'HTTPError occurred.'
        google = get_google_auth(token=token)
        resp = google.get(Auth.USER_INFO)
        if resp.status_code == 200:
            user_data = resp.json()
            email = user_data['email']
            print(len(student_accounts), len(admin_accounts))
            if email not in student_accounts and email not in admin_accounts:
            	return redirect(url_for('login'))
            user = User.query.filter_by(email=email).first()
            if user is None:
                user = User()
                user.email = email
                if email in admin_accounts:
                	user.admin = 1
            user.name = user_data['name']
            print('TOKEN:', token)
            user.tokens = json.dumps(token)
            user.avatar = user_data['picture']
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('home'))
        return 'Could not fetch your information.'

@app.route('/ranking')
@login_required
def ranking():
	dataplots = visualise()[0]
	return render_template('ranking.html', dataplots=dataplots, current_user=current_user, students=students)

@app.route('/profile/<string:name>')
@login_required
def profile(name):
	profile = None
	for s in students:
		if name.lower() in s.lower().replace(' ', ''):
			profile = s
	wcloud = wordcloud(profile)
	dataplots = visualise()
	return render_template('profile.html', profile=profile, dataplots=dataplots, wordcloud=wcloud, current_user=current_user, students=students)

@app.route('/statistics')
@login_required
def statistics():
	dataplots = visualise()
	return render_template('/statistics.html', dataplots=dataplots, current_user=current_user, students=students)

@app.route('/info')
@login_required
def info():
	return render_template('/info.html', info=information, current_user=current_user, students=students)

@app.route('/logout')
@login_required
def logout():
	# session.pop('username')
	logout_user()
	return redirect(url_for('home'))

if __name__ == '__main__':
	# app.run(debug=True)
	app.run(debug=True)
