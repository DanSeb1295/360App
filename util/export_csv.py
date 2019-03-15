import os
from config.config import basedir

csv_path = os.path.join(basedir, 'csv/IEOR171_Team_Grades.csv')

def export_csv(ranked_list):
	csv_file = open(csv_path, 'w+')

	headers = ','.join(['Name', 'Work Ethic', 'Team Effectiveness', 'Thinking Skills', 'Competence', 'Presence', 'Overall Grade'])
	csv_file.write(headers)
	
	for student in ranked_list:
		new_entry = ','.join(['\n' +
							student['name'],
							student['ratings']['workEthicGrade'],
							student['ratings']['teamEffectivenessGrade'],
							student['ratings']['thinkingSkillsGrade'],
							student['ratings']['competenceGrade'],
							student['ratings']['presenceGrade'],
							student['ratings']['grade']
							])
		csv_file.write(new_entry)
	csv_file.close()
