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
	dataplots = []
	return dataplots

def wordcloud(profile, word_string):
	# Create a list of word (https://en.wikipedia.org/wiki/Data_visualization)
	# text1="This is a sample wordcloud that is being displayed because you have not received any comments yet."
	text=word_string if word_string else "WordCloud"
	 
	# Make the figure
	wordcloud = WordCloud(background_color="rgba(255, 255, 255, 0)", mode="RGBA", width=1600, height=400, stopwords=STOPWORDS).generate(text)

	# Save Img
	if not profile:
		return None
	img_path = '/static/dataplots/wordclouds/wordcloud_{}.png'.format(profile.replace(' ', ''))
	wordcloud.to_file(base_path + img_path)
	
	return img_path

 

