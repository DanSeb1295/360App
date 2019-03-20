import os
import sys
import logging
import json
import datetime
import time
import math
import json
import pygal
from threading import Thread
from flask import Flask, flash, url_for, redirect, render_template, session, request, jsonify
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, UserMixin
from pymongo import MongoClient
from requests_oauthlib import OAuth2Session
from requests.exceptions import HTTPError
from config.config import Auth, DevConfig, ProdConfig, admin_accounts, student_accounts, students, information, DUE_DAY, MAIL_USERNAME, MAIL_PASSWORD, MONGO_URI, GRADES, IBM_API, IBM_URL, WEEK, pygal_style, student_email_dict
from models.schemas import project_groupings_schema, comments_schema, ratings_schema, articles_schema
from util.export_sheets import export_to_sheet
from util.data import wordcloud
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, SentimentOptions

""" Config Setup"""
config = {
	"dev": DevConfig,
	"prod": ProdConfig,
	"default": DevConfig
}

mail_settings = {
		"MAIL_SERVER": 'smtp.gmail.com',
		"MAIL_PORT": 465,
		"MAIL_USE_TLS": False,
		"MAIL_USE_SSL": True,
		"MAIL_USERNAME": os.environ.get('MAIL_USERNAME', MAIL_USERNAME),
		"MAIL_PASSWORD": os.environ.get('MAIL_PASSWORD', MAIL_PASSWORD)
	}

natural_language_understanding = NaturalLanguageUnderstandingV1(
    version='2018-11-16',
    iam_apikey=IBM_API,
    url=IBM_URL
)

""" APP creation and Configuration """
app = Flask(__name__)
app.config.from_object(config['dev'])
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', config['dev'].SQLALCHEMY_DATABASE_URI)
app.secret_key = app.config['SECRET_KEY']
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.config.update(mail_settings)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"
mail = Mail(app)
mongoClient = MongoClient(app.config['MONGO_URI'])
mongodb = mongoClient['360DB']
cur_user_team_list = []

""" DB Models """
class User(db.Model, UserMixin):
	__tablename__ = "users"
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(100), unique=True, nullable=False)
	name = db.Column(db.String(100), nullable=True)
	admin = db.Column(db.Integer, default=0)
	avatar = db.Column(db.String(200))
	tokens = db.Column(db.Text)
	created_at = db.Column(db.DateTime, default=datetime.datetime.now())

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

@app.route('/feedback')
@login_required
def feedback():
	cur_user_team_list = get_teams_from_mongo(current_user.name)
	return render_template('feedback.html', info=information, teamlist=cur_user_team_list, current_user=current_user, students=students)

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

@app.route('/')
@login_required
def home():
	if not current_user.is_authenticated:
		return redirect(url_for('login'))
	return render_template('ranking.html', teamlist=cur_user_team_list, current_user=current_user, students=students)

@app.route('/admin')
@login_required
def admin():
	if not current_user.admin:
		return redirect(url_for('home'))
	return render_template('admin.html', teamlist=cur_user_team_list, current_user=current_user, students=students)

@app.route('/submissions')
@login_required
def submissions():
	if not current_user.admin:
		return redirect(url_for('home'))
	return render_template('submissions.html', teamlist=cur_user_team_list, current_user=current_user, students=students)

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
	return render_template('profile.html', teamlist=cur_user_team_list, profile=profile, current_user=current_user, students=students)

@app.route('/info')
@login_required
def info():
	return render_template('/info.html', teamlist=cur_user_team_list, info=information, current_user=current_user, students=students)

@app.route('/extracredit')
@login_required
def extra_credit():
	return render_template('/extra_credit.html', teamlist=cur_user_team_list, info=information, current_user=current_user, students=students)

@app.route('/logout')
@login_required
def logout():
	session.clear()
	session.pop('username', None)
	logout_user()
	return redirect(url_for('login'))

def mail_notif(receiver, feedback):
	email = student_email_dict[receiver]
	print(email)

	message = {"subject": "<IEOR171 NOTIFICATION> 360 FEEDBACK RECEIVED",
				"sender": mail_settings["MAIL_USERNAME"],
				"bcc": [email],
				}

	msg = Message(**message)
	msg.html = render_template('email/email_notification.html', receiver=receiver, feedback=feedback)

	Thread(target=send_async_email, args=(app, msg)).start()

def send_async_email(app, msg):
	print('>>>>>> MAIL SENT IN BACKGROUND')
	with app.app_context():
		mail.send(msg)

def email_reminder(project_num, email_list=[]):
	message = {"subject": "<IEOR171 REMINDER> 360 TEAMMATE REVIEW",
				"sender": mail_settings["MAIL_USERNAME"],
				"bcc": email_list,
				}

	msg = Message(**message)
	msg.html = render_template('email/email_reminder.html', project_num=project_num)

	Thread(target=send_async_email, args=(app, msg)).start()

def automail():
	if datetime.datetime.today().weekday() != (DUE_DAY - 1) % 7:
		return None

	message = {"subject": "<IEOR171 REMINDER> 360 TEAMMATE REVIEW",
				"sender": mail_settings["MAIL_USERNAME"],
				"bcc": ["dyee003@berkeley.edu"],
				"body": "Greetings from IEOR171 Tech Firm Leadership.\n\nWe noticed that you have yet to submit your reviews for all your teammates to 360 this week. Please do so before the deadline.\n\nHave a nice day!"
				}

	with app.app_context():
		msg = Message(**message)
		mail.send(msg)

@app.route('/getwordcloud', methods=['POST'])
@login_required
def getwordcloud():
	comments = get_comments_from_mongo({'givenTo': request.form['profile']})
	ratings = get_ratings_from_mongo({'givenTo': request.form['profile']})
	word_string = ' '.join([comment['commentText'] for comment in comments])
	wcloud = wordcloud(request.form['profile'], word_string)
	return jsonify({'src': wcloud})

def get_sentiment_score(comment):
	try:
		response = natural_language_understanding.analyze(text=comment,
			features=Features(sentiment=SentimentOptions())).get_result()

		return float(response['sentiment']['document']['score'])
	except:
		pass

	return float(0)

@app.route('/submitcomment', methods=['POST'])
@login_required
def submitcomment():
	cur_time = datetime.datetime.now()
	new_comment_id = None

	try:
		# Creates mongodb comment object according to schema
		comment = comments_schema.copy()
		comment['givenBy'] = str(request.form['givenBy'])
		comment['givenTo'] = str(request.form['givenTo'])
		comment['projectNum'] = int(request.form['projectNum'])
		comment['commentText'] = str(request.form['commentText'])

		comment['submittedAt'] = cur_time
		comment['sentimentScore'] = get_sentiment_score(comment['commentText'])

		comment_is_valid = validate_comment(comment)

		if comment['givenTo'] not in students:
			response = 'Invalid Target'
		elif comment['givenTo'] ==  comment['givenBy']:
			response = 'Self-Review'
		elif comment_is_valid:
			comment['referenceFeedback'] = ''
			new_comment_id = str(mongodb['comments'].insert_one(comment).inserted_id)

			if new_comment_id:
				response = 'Success'
				mail_notif(comment['givenTo'], comment['commentText'])
			else:
				response = 'Server/ Database Error'
		else:
			response = 'Invalid'
	except:
		response = 'Error: Cannot Submit Post'
	
	return jsonify({'response': response, 'new_comment_id': new_comment_id})

@app.route('/submitform', methods=['POST'])
@login_required
def submitform():
	cur_time = datetime.datetime.now()
	new_rating_id = None
	new_comment_id = None

	try: 
		# Creates mongodb rating object according to schema
		rating = ratings_schema.copy()
		rating['givenBy'] = str(request.form['givenBy'])
		rating['givenTo'] = str(request.form['givenTo'])
		rating['projectNum'] = int(request.form['projectNum'])
		rating['teamNum'] = int(request.form['teamNum'])
		rating['submittedAt'] = cur_time
		for i in range(1, 4):
			q_num = 'q{}'.format(i)
			val = float(request.form['ratings[{}]'.format(q_num)])
			rating['ratings']['workEthic'][q_num] = val
		for i in range(4, 7):
			q_num = 'q{}'.format(i)
			val = float(request.form['ratings[{}]'.format(q_num)])
			rating['ratings']['teamEffectiveness'][q_num] = val
		for i in range(7, 10):
			q_num = 'q{}'.format(i)
			val = float(request.form['ratings[{}]'.format(q_num)])
			rating['ratings']['thinkingSkills'][q_num] = val
		for i in range(10, 13):
			q_num = 'q{}'.format(i)
			val = float(request.form['ratings[{}]'.format(q_num)])
			rating['ratings']['competence'][q_num] = val
		for i in range(13, 16):
			q_num = 'q{}'.format(i)
			val = float(request.form['ratings[{}]'.format(q_num)])
			rating['ratings']['presence'][q_num] = val

		# Creates mongodb comment object according to schema
		comment = comments_schema.copy()
		comment['givenBy'] = str(request.form['givenBy'])
		comment['givenTo'] = str(request.form['givenTo'])
		comment['projectNum'] = int(request.form['projectNum'])
		comment['commentText'] = str(request.form['commentText'])
		comment['submittedAt'] = cur_time
		comment['sentimentScore'] = get_sentiment_score(comment['commentText'])

		rating_is_valid = validate_rating(rating)
		comment_is_valid = validate_comment(comment)
		
		submitted = False
		prev_submissions = []
		for entry in mongodb['ratings'].find({'givenTo': comment['givenTo'], 'givenBy': comment['givenBy'], 'projectNum': comment['projectNum']}):
			prev_submissions.append(entry)
		
		if rating['projectNum'] != 4:
			submitted = True if prev_submissions else False
		else:
			submittedAt = rating['submittedAt']
			newSubmittedAt = {
							WEEK[10] <= submittedAt < WEEK[11]: 4.1,
							WEEK[11] <= submittedAt < WEEK[12]: 4.2,
							WEEK[12] <= submittedAt < WEEK[13]: 4.3,
							WEEK[13] <= submittedAt < WEEK[14]: 4.4,
							}[True]

			for submission in prev_submissions:
				postSubmittedAt = submission['submittedAt']	
				oldPostSubmittedAt = {
							WEEK[10] <= submittedAt < WEEK[11]: 4.1,
							WEEK[11] <= submittedAt < WEEK[12]: 4.2,
							WEEK[12] <= submittedAt < WEEK[13]: 4.3,
							WEEK[13] <= submittedAt < WEEK[14]: 4.4,
							}[True]
				if oldPostSubmittedAt == newSubmittedAt:
					submitted = True
					break

		if submitted:
			response = 'Duplicate Submission'
		elif rating_is_valid and comment_is_valid:
			new_rating_id = str(mongodb['ratings'].insert_one(rating).inserted_id)
			comment['referenceFeedback'] = new_rating_id
			new_comment_id = str(mongodb['comments'].insert_one(comment).inserted_id)

			if new_rating_id and new_comment_id:
				response = 'Success'
				mail_notif(comment['givenTo'], comment['commentText'])
			else:
				response = 'Server/ Database Error'
		else:
			response = 'Invalid'
		
	except:
		response = 'Error: Cannot Submit Post'

	return jsonify({'response': response, 'new_rating_id': new_rating_id, 'new_comment_id': new_comment_id})

def validate_rating(rating):
	try:
		if rating['givenBy'] == rating['givenTo']:
			return False
		if rating['givenBy'] and isinstance(rating['givenBy'], str):
			if rating['givenTo'] and isinstance(rating['givenTo'], str):
				if rating['projectNum'] and isinstance(rating['projectNum'], int):
					if rating['teamNum'] and isinstance(rating['teamNum'], int):
						for category, responses in rating['ratings'].items():
							for question, value in responses.items():
								if value and isinstance(value, float) and not math.isnan(value):
									continue
								else:
									return False
						return True
	except:
		return False
	return False

def validate_comment(comment):
	if comment['givenBy'] == comment['givenTo']:
		return False
	if comment['commentText'] and isinstance(comment['commentText'], str):
		if comment['givenBy'] and isinstance(comment['givenBy'], str):
			if comment['givenTo'] and isinstance(comment['givenTo'], str):
				if (comment['projectNum'] or comment['projectNum'] == 0) and isinstance(comment['projectNum'], int):
					if isinstance(comment['sentimentScore'], float):
						return True
	return False

@app.context_processor
def access_db():
	def get_avatar(profile):
		user = User.query.filter_by(name=profile).first()
		if user:
			return jsonify({'avatar': user.avatar})
		else:
			return jsonify({'avatar': url_for("static", filename="images/placeholder.png")})
	return dict(get_avatar=get_avatar)

@app.route('/getratings', methods=['POST'])
def get_ratings():
	profile = request.form['profile']
	ratings = get_ratings_from_mongo({'givenTo': profile})
	for rating in ratings:
		rating.pop('_id', None)

	result = compute_rating_sentiment(profile, ratings)
	chart_data = compute_chart_data(profile, ratings)

	line_chart = pygal.Bar(stroke=False, style=pygal_style, legend_at_bottom=True, legend_at_bottom_columns=5, legend_box_size=18)
	line_chart.title = 'Team Ratings Across Projects'
	line_chart.x_labels = 'Project 1', 'Project 2', 'Project 3', 'Project 4'
	line_chart.y_labels = range(11)
	line_chart.add('Work Ethic', [chart_data['workEthic'][1], chart_data['workEthic'][2], chart_data['workEthic'][3], chart_data['workEthic'][4]], rounded_bars=2)
	line_chart.add('Team Effectiveness', [chart_data['teamEffectiveness'][1], chart_data['teamEffectiveness'][2], chart_data['teamEffectiveness'][3], chart_data['teamEffectiveness'][4]], rounded_bars=2)
	line_chart.add('Thinking Skills', [chart_data['thinkingSkills'][1], chart_data['thinkingSkills'][2], chart_data['thinkingSkills'][3], chart_data['thinkingSkills'][4]], rounded_bars=2)
	line_chart.add('Competence', [chart_data['competence'][1], chart_data['competence'][2], chart_data['competence'][3], chart_data['competence'][4]], rounded_bars=2)
	line_chart.add('Presence', [chart_data['presence'][1], chart_data['presence'][2], chart_data['presence'][3], chart_data['presence'][4]], rounded_bars=2)
	line_chart.render()
	scatter_plot = line_chart.render_data_uri()
	
	return jsonify({'ratings': result, 'scatter_plot': scatter_plot})

def compute_chart_data(profile, ratings):
	chart_data ={
		'workEthic': {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0},
		'teamEffectiveness': {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0},
		'thinkingSkills': {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0},
		'competence': {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0},
		'presence': {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
	}

	no_entries = {
		1: 0,
		2: 0,
		3: 0,
		4: 0
	}

	for rating in ratings:
		if rating['givenTo'] == profile:
			no_entries[rating['projectNum']] += 1

	for rating in ratings:
		if rating['givenTo'] == profile:
			for category, responses in rating['ratings'].items():
				for question, answer in responses.items():
					chart_data[category][rating['projectNum']] += answer / (3 * no_entries[rating['projectNum']])
	
	return chart_data

@app.route('/getcomments', methods=['POST'])
def get_comments():
	feedbacks = get_comments_from_mongo({'givenTo': request.form['profile']})
	for feedback in feedbacks:
		feedback.pop('_id', None)

	sorted_feedback = sorted(feedbacks, key=lambda x: x.get('submittedAt'), reverse=True)
	return jsonify({'feedback': sorted_feedback})

@app.route('/getranking', methods=['GET'])
def get_ranking():
	comments = get_comments_from_mongo()
	ratings = get_ratings_from_mongo()

	ranking_dict = {}
	for s in students:
		ranking_dict[s] = compute_rating_sentiment(s, ratings, comments)
	
	ranked_namelist = sorted(ranking_dict.keys(), key=lambda x: (ranking_dict[x]['average_rating'], ranking_dict[x]['average_sentiment']), reverse=True)
	ranked_list = [{'name': student, 'ratings': ranking_dict[student]} for student in ranked_namelist]
	
	return jsonify({'ranked_list': ranked_list})

@app.route('/sendreminder', methods=['POST'])
def send_reminder():
	projectNum = str(request.form['projectNum'])
	class_submissions = get_submissions().get_json()['class_submissions']
	
	emails_to_send = []
	for student in class_submissions:
		if student['submissions'][projectNum]['submittedFor'] < student['submissions'][projectNum]['teamSize']:
			emails_to_send.append(student_email_dict[student['name']])

	email_reminder(projectNum, emails_to_send)

	return jsonify({'sentTo': len(emails_to_send), 'projectNum': projectNum})

@app.route('/getsubmissions', methods=['GET'])
def get_submissions():
	class_tracker = {}
	for s in students:
		groups = get_teams_from_mongo(s)
		individual_tracker = {
							1: {'teamSize': max(len(groups.get(1, {'members': []})['members']) - 1, 0), 'submittedFor': 0},
							2: {'teamSize': max(len(groups.get(2, {'members': []})['members']) - 1, 0), 'submittedFor': 0},
							3: {'teamSize': max(len(groups.get(3, {'members': []})['members']) - 1, 0), 'submittedFor': 0},
							4.1: {'teamSize': max(len(groups.get(4, {'members': []})['members']) - 1, 0), 'submittedFor': 0},
							4.2: {'teamSize': max(len(groups.get(4, {'members': []})['members']) - 1, 0), 'submittedFor': 0},
							4.3: {'teamSize': max(len(groups.get(4, {'members': []})['members']) - 1, 0), 'submittedFor': 0},
							4.4: {'teamSize': max(len(groups.get(4, {'members': []})['members']) - 1, 0), 'submittedFor': 0}
						}
		class_tracker[s] = individual_tracker

	ratings = get_ratings_from_mongo()

	for rating in ratings:
		submission_num = rating['projectNum']
		submitted_at = rating['submittedAt']
		submitted_for = {
						submission_num == 1: submission_num,
						submission_num == 2: submission_num,
						submission_num == 3: submission_num,
						submission_num == 4 and WEEK[10] <= submittedAt < WEEK[11]: 4.1,
						submission_num == 4 and WEEK[11] <= submittedAt < WEEK[12]: 4.2,
						submission_num == 4 and WEEK[12] <= submittedAt < WEEK[13]: 4.3,
						submission_num == 4 and WEEK[13] <= submittedAt < WEEK[14]: 4.4,
						}[True]

		class_tracker[rating['givenBy']][submitted_for]['submittedFor'] += 1
	
	class_submissions = []
	for s in students:
		class_submissions.append({'name': s, 'submissions': class_tracker[s]})

	return jsonify({'class_submissions': class_submissions})

@app.route('/exportsheet', methods=['GET'])
def export_sheet():
	comments = get_comments_from_mongo()
	ratings = get_ratings_from_mongo()

	ranking_dict = {}
	for s in students:
		ranking_dict[s] = compute_rating_sentiment(s, ratings, comments)
	
	ranked_namelist = sorted(ranking_dict.keys(), key=lambda x: (ranking_dict[x]['average_rating'], ranking_dict[x]['average_sentiment']), reverse=True)
	ranked_list = [{'name': student, 'ratings': ranking_dict[student]} for student in ranked_namelist]
	
	export_to_sheet(ranked_list)

	return jsonify({'ranked_list': ranked_list})

def get_comments_from_mongo(query_filter={}):
	comments_collection = mongodb['comments']
	comments = []
	for comment in comments_collection.find(query_filter):
		comments.append(comment)
	return comments

def get_ratings_from_mongo(query_filter={}):
	ratings_collection = mongodb['ratings']
	ratings = []
	for rating in ratings_collection.find(query_filter):
		ratings.append(rating)
	return ratings

def get_teams_from_mongo(name):
	project_groupings_collection = mongodb['project_groupings']
	project_groupings = {}
	for project_grouping in project_groupings_collection.find({ 'members': name}):
		project_groupings[project_grouping['projectNum']] = {'team_num': project_grouping['teamNum'], 'members': project_grouping['members']}
	return project_groupings

def compute_rating_sentiment(student, ratings, comments=[]):
	all_sentiments = [float(comment['sentimentScore']) for comment in comments if comment['givenTo'] == student]
	all_ratings = [float(rate[1]) for rating in ratings if rating['givenTo'] == student for category in rating['ratings'].keys() for rate in rating['ratings'][category].items()]
	cur_rating = {
		'workEthic': {'numQuestions': 0, 'runningTotal': float(0)},
		'teamEffectiveness': {'numQuestions': 0, 'runningTotal': float(0)},
		'thinkingSkills': {'numQuestions': 0, 'runningTotal': float(0)},
		'competence': {'numQuestions': 0, 'runningTotal': float(0)},
		'presence': {'numQuestions': 0, 'runningTotal': float(0)},
		'total': {'numQuestions': 0, 'runningTotal': float(0)}
	}

	for rating in ratings:
		if rating['givenTo'] == student:
			for category in rating['ratings']:
				for question in rating['ratings'][category].items():
					cur_rating[category]['runningTotal'] += question[1]
					cur_rating[category]['numQuestions'] += 1
					cur_rating['total']['runningTotal'] += question[1]
					cur_rating['total']['numQuestions'] += 1

	average_sentiment = sum(all_sentiments) / len(all_sentiments) if all_sentiments else 0
	average_rating = cur_rating['total']['runningTotal'] / cur_rating['total']['numQuestions'] if cur_rating['total']['numQuestions'] > 0 else 0

	workEthicRaw = cur_rating['workEthic']['runningTotal'] / cur_rating['workEthic']['numQuestions'] if cur_rating['workEthic']['numQuestions'] > 0 else 0
	teamEffectivenessRaw = cur_rating['teamEffectiveness']['runningTotal'] / cur_rating['teamEffectiveness']['numQuestions'] if cur_rating['teamEffectiveness']['numQuestions'] > 0 else 0
	thinkingSkillsRaw = cur_rating['thinkingSkills']['runningTotal'] / cur_rating['thinkingSkills']['numQuestions'] if cur_rating['thinkingSkills']['numQuestions'] > 0 else 0
	competenceRaw = cur_rating['competence']['runningTotal'] / cur_rating['competence']['numQuestions'] if cur_rating['competence']['numQuestions'] > 0 else 0
	presenceRaw = cur_rating['presence']['runningTotal'] / cur_rating['presence']['numQuestions'] if cur_rating['presence']['numQuestions'] > 0 else 0

	workEthic = round(workEthicRaw)
	teamEffectiveness = round(teamEffectivenessRaw)
	thinkingSkills = round(thinkingSkillsRaw)
	competence = round(competenceRaw)
	presence = round(presenceRaw)

	cur_grade = GRADES.get(round(average_rating), 'D')
	workEthicGrade = GRADES.get(workEthic, 'D')
	teamEffectivenessGrade = GRADES.get(teamEffectiveness, 'D')
	thinkingSkillsGrade = GRADES.get(thinkingSkills, 'D')
	competenceGrade = GRADES.get(competence, 'D')
	presenceGrade = GRADES.get(presence, 'D')

	return {'average_rating': average_rating, 'average_sentiment': average_sentiment, 'grade': cur_grade,
			'workEthic': workEthic, 'teamEffectiveness': teamEffectiveness, 'thinkingSkills': thinkingSkills,
			'competence': competence, 'presence': presence, 'workEthicGrade': workEthicGrade,
			'teamEffectivenessGrade': teamEffectivenessGrade, 'thinkingSkillsGrade': thinkingSkillsGrade,
			'competenceGrade': competenceGrade, 'presenceGrade': presenceGrade, 'workEthicRaw': workEthicRaw,
			'teamEffectivenessRaw': teamEffectivenessRaw, 'thinkingSkillsRaw': thinkingSkillsRaw, 'competenceRaw': competenceRaw,
			'presenceRaw': presenceRaw}


if __name__ == '__main__':
	app.run(debug=True, ssl_context=('./ssl.crt', './ssl.key'))
