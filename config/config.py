import os
from os import urandom

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
    SECRET_KEY = os.environ.get("SECRET_KEY") or b'\x02ShpT8\x96\x07\xcc\xe1645\xfb\xc8\x07\x8f-\x01{U\xaf\x1e\x88'

class DevConfig(Config):
    """Dev config"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, "db/local.db")


class ProdConfig(Config):
    """Production config"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, "db/online.db")

information = {
    "Work Ethic": [
        "Reliability: How confident are you that this person will do what they say they will do, when they said they will do it by",
        "Time Management: Is this person on time, with meetings as well as with deadlines",
        "Self Motivation: To what extent is this person enthusiastic about working towards the team’s objectives"
    ],
    "Team Effectiveness": [
        "Likeability: To what extent do you enjoy working with this person",
        "Team Player: To what extent does this person listen and look out to others and put the team’s interest beyond their own",
        "Communication: To what extent is this person open, sincere, and effective in their communication to other members of the team"
    ],
    "Thinking Skills" : [
        "Creativity: How well is this person able to think laterally and generate useful and innovative ideas",
        "Critical Thining: How well is this person able to navigate and make sense of all available information, and/ or deal with the lack of it",
        "Insightfulness: To what extent is this person able to come up with key insights that others don’t"
    ],
    "Competence": [
        "Quality of Work: To what extent does this person produce quality work",
        "Skills: To what extent has this person applied their skills, and/or acquired new skills, to make a meaningful impact on the project",
        "Resourcefulness: How well does this person work under/ around constraints"
    ],
    "Presence": [
        "Commitment: How much commitment does this person display to the team (attending meetings, OHs, etc.)",
        "Indispensability: How much difference would it make to the team if this person were absent from the team",
        "Influence: To what extent is this person able to motivate the team to continually work towards the team’s objectives"
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
    'goldpiggy@berkeley.edu',
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
    'Rachel Hu',
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