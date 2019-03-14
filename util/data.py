import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from wordcloud import WordCloud, STOPWORDS
from PIL import Image
from flask_login import current_user
from math import pi

base_path = save_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
matplotlib.use('Agg')

def visualise():
	dataplots = [
		radar_chart(),
		scatter_3D()
		]
	return dataplots

def radar_chart():
	# Set data
	df = pd.DataFrame({
	'group': ['A','B','C','D'],
	'var1': [38, 1.5, 30, 4],
	'var2': [29, 10, 9, 34],
	'var3': [8, 39, 23, 24],
	'var4': [7, 31, 33, 14],
	'var5': [28, 15, 32, 14]
	})
	 
	# number of variable
	categories=list(df)[1:]
	N = len(categories)
	 
	# We are going to plot the first line of the data frame.
	# But we need to repeat the first value to close the circular graph:
	values=df.loc[0].drop('group').values.flatten().tolist()
	values += values[:1]
	values
	 
	# What will be the angle of each axis in the plot? (we divide the plot / number of variable)
	angles = [n / float(N) * 2 * pi for n in range(N)]
	angles += angles[:1]
	 
	# Initialise the spider plot
	ax = plt.subplot(111, polar=True)
	 
	# Draw one axe per variable + add labels labels yet
	plt.xticks(angles[:-1], categories, color='grey', size=8)
	 
	# Draw ylabels
	ax.set_rlabel_position(0)
	plt.yticks([10,20,30], ["10","20","30"], color="grey", size=7)
	plt.ylim(0,40)
	 
	# Plot data
	ax.plot(angles, values, linewidth=1, linestyle='solid')
	 
	# Fill area
	ax.fill(angles, values, 'b', alpha=0.1)

	# Save Img
	img_path = '/static/dataplots/radar_chart.png'
	plt.savefig(base_path + img_path, transparent=True)
	
	return img_path

def scatter_3D():
	# Dataset
	df=pd.DataFrame({'X': range(1,101), 'Y': np.random.randn(100)*15+range(1,101), 'Z': (np.random.randn(100)*15+range(1,101))*2 })
	 
	# plot
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')
	ax.scatter(df['X'], df['Y'], df['Z'], c='skyblue', s=60)
	ax.view_init(30, 185)

	# Save Img
	img_path = '/static/dataplots/3D_scatter.png'
	plt.savefig(base_path + img_path, transparent=True)
	
	return img_path

def wordcloud(profile, word_string):
	# Create a list of word (https://en.wikipedia.org/wiki/Data_visualization)
	text1="This is a sample wordcloud that is being displayed because you have not received any comments yet."
	text=word_string if word_string else text1
	# Load the image
	# cloud_mask = np.array(Image.open(base_path + '/static/images/cloud.png'))
	 
	# Make the figure
	wordcloud = WordCloud(background_color="#efefef", width=1600, height=400, stopwords=STOPWORDS).generate(text)

	# Save Img
	if not profile:
		return None
	img_path = '/static/dataplots/wordclouds/wordcloud_{}.png'.format(profile.replace(' ', ''))
	wordcloud.to_file(base_path + img_path)
	
	return img_path

 

