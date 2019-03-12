import os
import sys
import logging
import json
import datetime
import time
from flask import Flask, flash, url_for, redirect, render_template, session, request, jsonify
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, UserMixin
from pymongo import MongoClient
from requests_oauthlib import OAuth2Session
from requests.exceptions import HTTPError
from config.config import Auth, DevConfig, ProdConfig, admin_accounts, student_accounts, students, information, DUE_DAY, MAIL_USERNAME, MAIL_PASSWORD, MONGO_URI
from models.schemas import project_groupings_schema, comments_schema, ratings_schema, articles_schema
from util.data import visualise, wordcloud

config = {
	"dev": DevConfig,
	"prod": ProdConfig,
	"default": DevConfig
}

"""APP creation and configuration"""
app = Flask(__name__)
app.config.from_object(config['dev'])
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', config['dev'].SQLALCHEMY_DATABASE_URI)
app.secret_key = app.config['SECRET_KEY']
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
db = SQLAlchemy(app)
mongoClient = MongoClient(app.config['MONGO_URI'])
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

	@property
	def serialize(self):
		"""Return object data in easily serializable format"""
		return {
			'id' : self.id,
			'email': self.email,
			'name': self.name,
			'avatar': self.avatar,
			# 'tokens': self.tokens,
			# 'admin': self.admin,
			# 'created_at': self.created_at.__str__
			}

@login_manager.user_loader
def load_user(user_id):
	try:
		return User.query.get(int(user_id))
	except User.DoesNotExist:
		return None

""" OAuth Session creation """
def get_google_auth(state=None, token=None):
	if token:
		return OAuth2Session(Auth.CLIENT_ID, token=token)
	if state:
		return OAuth2Session(
			Auth.CLIENT_ID,
			state=state,
			redirect_uri=request.url_root + Auth.REDIRECT_URI)
	oauth = OAuth2Session(
		Auth.CLIENT_ID,
		redirect_uri=request.url_root + Auth.REDIRECT_URI,
		scope=Auth.SCOPE)
	return oauth

@app.context_processor
def users_db():
	users_db = json.dumps([i.serialize for i in User.query.order_by(User.name).all()])
	return dict(users_db=json.loads(users_db))

@app.route('/')
@login_required
def home():
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
	session.modified = True
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
		google = get_google_auth(state=session.get('oauth_state', None))
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
			if email not in student_accounts and email not in admin_accounts:
				return redirect(url_for('login'))
			session['unauthorized'] = False
			user = User.query.filter_by(email=email).first()
			if user is None:
				user = User()
				user.email = email
			user.admin = 1 if email in admin_accounts else 0
			user.name = user_data['name']
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
			break
		else:
			redirect(url_for('home'))
	dataplots = visualise()
	return render_template('profile.html', profile=profile, dataplots=dataplots, current_user=current_user, students=students)

# @app.route('/statistics')
# @login_required
# def statistics():
# 	dataplots = visualise()
# 	return render_template('/statistics.html', dataplots=dataplots, current_user=current_user, students=students)

@app.route('/info')
@login_required
def info():
	return render_template('/info.html', info=information, current_user=current_user, students=students)

@app.route('/logout')
@login_required
def logout():
	session.clear()
	session.pop('username', None)
	logout_user()
	return redirect(url_for('home'))

def automail():
	if datetime.datetime.today().weekday() != DUE_DAY - 1:
		return None

	mail_settings = {
		"MAIL_SERVER": 'smtp.gmail.com',
		"MAIL_PORT": 465,
		"MAIL_USE_TLS": False,
		"MAIL_USE_SSL": True,
		"MAIL_USERNAME": os.environ.get('MAIL_USERNAME', MAIL_USERNAME),
		"MAIL_PASSWORD": os.environ.get('MAIL_PASSWORD', MAIL_PASSWORD)
	}

	app.config.update(mail_settings)
	mail = Mail(app)
	message = {"subject": "<IEOR171 REMINDER> 360 TEAMMATE REVIEW",
				"sender": mail_settings["MAIL_USERNAME"],
				"bcc": ["dyee003@berkeley.edu", "daniel-sebastian95@hotmail.com"],
				"body": "Greetings from IEOR171 Tech Firm Leadership.\n\nWe noticed that you have yet to submit your reviews for all your teammates to 360 this week. Please do so before the deadline.\n\nHave a nice day!"
				}

	with app.app_context():
		msg = Message(**message)
		mail.send(msg)

@app.route('/getwordcloud', methods=['POST'])
@login_required
def getwordcloud():
	wcloud = wordcloud(request.form['profile'])
	return jsonify({'src': wcloud})

@app.route('/mongotest')
@login_required
def mongotest():
	return 'POSTED'

@app.context_processor
def access_db():
	def get_avatar(profile):
		user = User.query.filter_by(name=profile).first()
		if user:
			return jsonify({'avatar': user.avatar})
		else:
			return jsonify({'avatar': url_for("static", filename="images/placeholder.png")})
	return dict(get_avatar=get_avatar)

@app.route('/getranking', methods=['GET'])
def get_ranking():
	# return jsonify({'ranked_list': ['DANIEL', 'SEBASTIAN', 'YEE']})
	
	db = mongoClient['360DB']
	comments_collection = db['comments']
	comments = []
	for comment in comments_collection.find({}):
		comments.append(comment)

	ratings_collection = db['ratings']
	ratings = []
	for rating in ratings_collection.find({}):
		ratings.append(rating)

	ranking_dict = {}
	for s in students:
		ranking_dict[s] = compute_rating_sentiment(s, comments, ratings)
	
	ranked_list = sorted(ranking_dict.keys(), key=lambda x: (ranking_dict[x]['average_rating'], ranking_dict[x]['average_sentiment']), reverse=True)
	# import random
	# random.shuffle(ranked_list)
	return jsonify({'ranked_list': ranked_list})

def compute_rating_sentiment(student, comments, ratings):
	all_sentiments = [float(comment['sentimentScore']) for comment in comments if comment['givenTo'] == student]
	all_ratings = [float(rate[1]) for rating in ratings if rating['givenTo'] == 'hi' for category in rating['ratings'].keys() for rate in rating['ratings'][category].items()]
	average_sentiment = sum(all_sentiments) / len(all_sentiments) if all_sentiments else 0
	average_rating = sum(all_ratings) / len(all_ratings) if all_ratings else 0
	return {'average_rating': average_rating, 'average_sentiment': average_sentiment}


if __name__ == '__main__':
	app.run(debug=True, ssl_context=('./ssl.crt', './ssl.key'))
