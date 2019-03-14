import os
from os import urandom

DUE_DAY = 6
MAIL_USERNAME = '360ieor171@gmail.com'
MAIL_PASSWORD = 'stephentorres'
MONGO_USER = '360App'
MONGO_PASSWORD = 'stephentorres'
MONGO_URI = 'mongodb+srv://{}:{}@cluster0-7qgtl.mongodb.net/test?retryWrites=true'.format(MONGO_USER, MONGO_PASSWORD)

basedir = os.path.abspath(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))

class Auth:
    """Google Project Credentials"""
    CLIENT_ID = ('1022937286771-t7aritjh57ffsh41gkam13cn86h24jpi.apps.googleusercontent.com')
    CLIENT_SECRET = '0VbVco0F7caktc7ULy2OBsC1'
    REDIRECT_URI = 'gCallback'
    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
    USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'
    SCOPE = ['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']

class Config:
    """Base config"""
    APP_NAME = "360App"
    SECRET_KEY = os.environ.get("SECRET_KEY") or b'\xeb9~,p\xc5$,\xf7\xd1\x80\x81\xfcn\x8f\xe4+\xb5h\xfd\x7f_\xbf\x00'
    MONGO_URI = MONGO_URI
    # MONGO_URI = 'mongodb+srv://{}:{}@cluster0-7qgtl.mongodb.net/360App?retryWrites=true'.format(os.environ.get("MONGO_USER"), os.environ.get("MONGO_PASSWORD"))

class DevConfig(Config):
    """Dev config"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, "db/local.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProdConfig(Config):
    """Production config"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, "db/online.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    

information = {
    "Work Ethic": [
        "Reliability: How confident are you that this person will do what he/ she say he/ she will do, by when he/ she said he/ she will do it by?",
        "Time Management: To what extent is this person on time, with meetings as well as with deadlines?",
        "Self Motivation: To what extent is this person enthusiastic about working towards the team’s objectives?"
    ],
    "Team Effectiveness": [
        "Likeability: How much do you enjoy working with this person?",
        "Team Player: To what extent does this person listen and look out to others and put the team’s interest beyond his/ her own?",
        "Communication: How open, sincere, and effective is this person in his/ her communication to other members of the team?"
    ],
    "Thinking Skills" : [
        "Creativity: How well is this person able to think laterally and generate useful and innovative ideas?",
        "Critical Thining: How well is this person able to navigate and make sense of all available information, and/ or deal with the lack of it?",
        "Insightfulness: To what extent is this person able to come up with key insights that others don’t?"
    ],
    "Competence": [
        "Quality of Work: To what extent does this person produce quality work?",
        "Skills: To what extent has this person applied his/ her skills, and/or acquired new skills, to make a meaningful impact on the project?",
        "Resourcefulness: How well does this person work under/ around constraints?"
    ],
    "Presence": [
        "Commitment: How much commitment does this person display to the team (meetings, OHs, etc.)?",
        "Indispensability: How much difference would it make to the team if this person were absent from the team?",
        "Influence: To what extent is this person able to motivate the team to continually work towards the team’s objectives?"
    ]
}

admin_accounts = ['s.t@berkeley.edu', 'awillerman@berkeley.edu', 'gwynevere.hunger@berkeley.edu']

student_accounts = [
    'aryakanand@berkeley.edu',
    'angshijie@berkeley.edu',
    'chaseaplin@berkeley.edu',
    'allisonarvin@berkeley.edu',
    'v.attre@berkeley.edu',
    'fatmanur.aydin@berkeley.edu',
    'smitabalaji@berkeley.edu',
    'sbao04@berkeley.edu',
    'ethanjbarnhart@berkeley.edu',
    'clacerda@berkeley.edu',
    'icenturion@berkeley.edu',
    'jchew021@berkeley.edu',
    'yifan.ding@berkeley.edu',
    'nataliaflores@berkeley.edu',
    'nganesh@berkeley.edu',
    'bobbygill@berkeley.edu',
    'danigoland@berkeley.edu',
    'wgraham@berkeley.edu',
    'aakarshgupta97@berkeley.edu',
    'bismark@berkeley.edu',
    'mads.have@berkeley.edu',
    'ehovagim20@berkeley.edu',
    'dominichugo@berkeley.edu',
    'arthur.h@berkeley.edu',
    'saemalle@berkeley.edu',
    'kunalkak@berkeley.edu',
    'lmkochendoerfer@berkeley.edu',
    'kqkong@berkeley.edu',
    '19lkresl@berkeley.edu',
    'mleruyet@berkeley.edu',
    'fledesma@berkeley.edu',
    'lofgren@berkeley.edu',
    'traceurling@berkeley.edu',
    'jmelizanis@berkeley.edu',
    'nilofer@berkeley.edu',
    'mmohan@berkeley.edu',
    'ambika.mukherjee@berkeley.edu',
    'evelyn_mwangi@berkeley.edu',
    'ilsepaolanb@berkeley.edu',
    'cfnewman@berkeley.edu',
    'emerson.ng@berkeley.edu',
    'chibuzo.nw@berkeley.edu',
    'alanlp@berkeley.edu',
    'rajariahi@berkeley.edu',
    'rainems3@berkeley.edu',
    'dshaby@berkeley.edu',
    'erne0005@berkeley.edu',
    'tans0362@berkeley.edu',
    'adi.tyagi@berkeley.edu',
    'kaautam96@berkeley.edu',
    'vimalaveera@berkeley.edu',
    'jashvora@berkeley.edu',
    'dyee003@berkeley.edu',
    'kimiaz@berkeley.edu',
    'jlzhang@berkeley.edu'
] + [
    'sunnyzhang@berkeley.edu',
    'zzysunny@berkeley.edu',
    'edward.yang98@berkeley.edu',
    'edwardyang@berkeley.edu',
    'edwyang@berkeley.edu',
    'eddy1994@berkeley.edu'
]

students = [
    'Aakarsh Gupta',
    'Aditya Tyagi',
    'Agustin Centurion',
    'Alan Pham',
    'Allison Arvin',
    'Ambika Mukherjee',
    'Arthur Huynh',
    'Arya Anand',
    'Bakhshish Gill',
    'Bismark Haruna',
    'Caroline Newman',
    'Charles Lu',
    'Chase Aplin',
    'Chibuzo Nwokocha',
    'Cristiano Carvalho Lacerda',
    'Dani Goland',
    'Daniel Sebastian Yee',
    'Daniel Shaby',
    'Dominic Hugo',
    'Edward Yang',
    'Eric Hovagim',
    'Ernest Yong En Tan',
    'Ethan Barnhart',
    'Eve Mwangi',
    'Fatmanur Aydin',
    'Francesca Ledesma',
    'Ilse Naranjo Brambila',
    'Jash Vora',
    'Jay Ang',
    'Jianglai Zhang',
    'Jireh Wei En Chew',
    'John Melizanis',
    'Jui Khang Emerson Ng',
    'Kaautam Uthaya Suriyan',
    'Kathy Kong',
    'Kimia Zargari',
    'Kunal Kak',
    'Leah Kochendoerfer',
    'Lucie Kresl',
    'Mads Have',
    'Mehek Mohan',
    'Milan Le Ruyet',
    'Natalia Flores Caseres',
    'Nicholas Lofgren',
    'Nilofer Sultana Mohammad',
    'Niraj Ganesh',
    'Raine Scott',
    'Raja Riahi',
    'Stella Bao',
    'Saehee Im',
    'Si Pei Tan',
    'Smita Balaji',
    'Sunny Zhang',
    'Vimala Veeramachaneni',
    'Viraj Attre',
    'Wesley Graham',
    'Yifan Ding'
]

pro3grouping = [
        {
            'projectNum' : 3,
            'teamNum': 1,
            'members': [
                'Nilofer Sultana Mohammad',
                'Arthur Huynh',
                'Jianglai Zhang',
                'Kaautam Uthaya Suriyan',
                'Natalia Flores Caseres'
            ]
        },
        {
            'projectNum' : 3,
            'teamNum': 2,
            'members': [
                'Jash Vora',
                'Niraj Ganesh',
                'Leah Kochendoerfer',
                'Dani Goland',
                'Daniel Shaby'
            ]
        },
        {
            'projectNum' : 3,
            'teamNum': 3,
            'members': [
                'Daniel Sebastian Yee',
                'Francesca Ledesma',
                'Arya Anand',
                'John Melizanis',
                'Ilse Naranjo Brambila'
            ]
        },
        {
            'projectNum' : 3,
            'teamNum': 4,
            'members': [
                'Jireh Wei En Chew',
                'Milan Le Ruyet',
                'Fatmanur Aydin',
                'Yifan Ding'
            ]
        },
        {
            'projectNum' : 3,
            'teamNum': 5,
            'members': [
                'Ambika Mukherjee',
                'Chase Aplin',
                'Nicholas Lofgren',
                'Si Pei Tan',
                'Stella Bao'
            ]
        },
        {
            'projectNum' : 3,
            'teamNum': 6,
            'members': [
                'Smita Balaji',
                'Saehee Im',
                'Alan Pham',
                'Aditya Tyagi',
                'Raine Scott'
            ]
        },
        {
            'projectNum' : 3,
            'teamNum': 7,
            'members': [
                'Bismark Haruna',
                'Mads Have',
                'Kathy Kong',
                'Eric Hovagim',
                'Caroline Newman'
            ]
        },
        {
            'projectNum' : 3,
            'teamNum': 8,
            'members': [
                'Eve Mwangi',
                'Lucie Kresl',
                'Ethan Barnhart',
                'Vimala Veeramachaneni',
                'Ernest Yong En Tan'
            ]
        },
        {
            'projectNum' : 3,
            'teamNum': 9,
            'members': [
                'Sunny Zhang',
                'Raja Riahi',
                'Charles Lu',
                'Allison Arvin',
                'icenturion@berkeley.edu'
            ]
        },
        {
            'projectNum' : 3,
            'teamNum': 10,
            'members': [
                'Mehek Mohan',
                'Kunal Kak',
                'Jay Ang',
                'Bakhshish Gill'
            ]
        },
        {
            'projectNum' : 3,
            'teamNum': 11,
            'members': [
                'Kimia Zargari',
                'Cristiano Carvalho Lacerda',
                'Wesley Graham',
                'Jui Khang Emerson Ng',
                'Dominic Hugo'
            ]
        },
        {
            'projectNum' : 3,
            'teamNum': 12,
            'members': [
                'Viraj Attre',
                'Chibuzo Nwokocha',
                'Aakarsh Gupta',
                'Edward Yang'
            ]
        }
    ]