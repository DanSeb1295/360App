from datetime import datetime

project_groupings_schema = {
	'projectNum' : int,
	'teamNum': int,
	'members': list
}

comments_schema = {
	'commentText': str,
	'givenBy': str,
	'givenTo': str,
	'datetime': datetime,
	'referenceFeedback': int,
	'sentimentScore': float
}

ratings_schema = {
	'givenBy': str,
	'datetime': datetime,
	'projectNum': int,
	'teamNum': int,
	'givenTo': str,
	'ratings': {
		'workEthic': {
			'q1': float,
			'q6': float,
			'q11': float
		},
		'teamEffectiveness': {
			'q2': float,
			'q7': float,
			'q12': float
		},
		'thinkingSkills': {
			'q3': float,
			'q8': float,
			'q13': float
		},
		'competence': {
			'q4': float,
			'q9': float,
			'q14': float
		},
		'presence': {
			'q5': float,
			'q10': float,
			'q15': float
		}	
	}
}

articles_schema = {
	'latest': bool,
	'URLs': {
		'workEthicURL': str,
		'teamEffectivenessURL': str,
		'thinkingSkillsURL': str,
		'competenceURL': str,
		'presenceURL': str
	}
}