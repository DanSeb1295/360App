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
	'submittedAt': datetime,
	'projectNum': int,
	'referenceFeedback': str,
	'sentimentScore': float
}

ratings_schema = {
	'givenBy': str,
	'submittedAt': datetime,
	'projectNum': int,
	'teamNum': int,
	'givenTo': str,
	'ratings': {
		'workEthic': {
			'q1': float,
			'q2': float,
			'q3': float
		},
		'teamEffectiveness': {
			'q4': float,
			'q5': float,
			'q6': float
		},
		'thinkingSkills': {
			'q7': float,
			'q8': float,
			'q9': float
		},
		'competence': {
			'q10': float,
			'q11': float,
			'q12': float
		},
		'presence': {
			'q13': float,
			'q14': float,
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