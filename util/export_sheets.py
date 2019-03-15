import os
import math
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config.config import basedir

client_secret = os.path.join(basedir, 'config/client_secret.json')
scope = ['https://spreadsheets.google.com/feeds',
		 'https://www.googleapis.com/auth/drive']

def export_to_sheet(ranked_list):
	creds = ServiceAccountCredentials.from_json_keyfile_name(client_secret, scope)
	client = gspread.authorize(creds)

	# Find a workbook by name and open the first sheet
	# Make sure you use the right name here.
	sheet = client.open("IEOR171 Team Grades").sheet1

	# Extract and print all of the values
	cell_list = sheet.range('A2:G58')
	
	for i, cell in enumerate(cell_list):
		student_number = math.floor(i / 7)
		item_numer = i % 7

		student_dict = {
			0: ranked_list[student_number]['name'],
			1: ranked_list[student_number]['ratings']['workEthicGrade'],
			2: ranked_list[student_number]['ratings']['teamEffectivenessGrade'],
			3: ranked_list[student_number]['ratings']['thinkingSkillsGrade'],
			4: ranked_list[student_number]['ratings']['competenceGrade'],
			5: ranked_list[student_number]['ratings']['presenceGrade'],
			6: ranked_list[student_number]['ratings']['grade']
		}

		cell.value = student_dict[item_numer]

	sheet.update_cells(cell_list)