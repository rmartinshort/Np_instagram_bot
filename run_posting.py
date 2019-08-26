#!/usr/bin/env python 
#RMS 2019 

import pipeline 
import pandas as pd
from instapy_cli import client
from datetime import datetime
import os
import time
from config import config
import numpy as np


def run_extract_stats() -> None:

	'''Get the latest stats on the accounts we want to download from'''

	pipeline.profiles_pipe.download()

	print("Done extract stats")

def choose_post() -> dict:

	"""Returns a dictionary containing the path of the image
	to be posted and the caption to accompany it"""

	#X is a dataframe containing the metadata for each of the downloaded posts, ready for processing
	X = pipeline.metadata_gen.process_posts()

	if X.shape[0] < 2:

		return {'Image':'no_image','Caption':np.nan}

	else:

		#This processing pipeline will produce the file that we want to repost and its
		#associated caption and credits

		result = pipeline.process_pipe.fit_transform(X)
		#result = pipeline.process_pipe.transform(X)
		
		return result

def generate_post(post_meta,post_online=False) -> None:

	'''This uploads a selected image and caption to instagram'''

	username = config.INSTA_UNAME
	password = config.INSTA_PASS

	image_file = post_meta['Image']
	print(image_file)
	image_caption = post_meta['Caption']

	print(image_file)

	print('caption: ----- ')
	print(image_caption)
	print('--------------')

	print(username,password)


	if post_online == True:

		with client(username, password, write_cookie_file=False) as cli:
			try:
				cli.upload(image_file, image_caption)
			except:
				print('Issue: unable to upload at this time!')

	#append to previous posts 
	used_image_file = open(config.PREV_POSTS,'a')
	used_image_file.write(f"{image_file},{datetime.now()}\n")
	used_image_file.close()

	#remove the image file so that it can't be included in the next round of image collection
	os.remove(image_file)


def posting_wrapper(error_check=False) -> None:

	'''For automated downloads'''

	while True:

		if error_check == True:

			try:

				_postloop()

			except:

				print('Something went wrong while assembling the next post! This should not happen! Waiting a while to try again')
				time.sleep(3600*config.POST_FREQ/8)

		else:

			_postloop()


def _postloop() -> None:
    
        #run_extract_stats()
	post = choose_post()

	print(post)

	if post['Image'] == "no_image":
		print('Image inventory empty. Waiting for a new download cycle to try again')
		time.sleep(1*config.POST_FREQ)
	else:
		generate_post(post,post_online=True)
		time.sleep(1*config.POST_FREQ)




if __name__ == '__main__':

	#For testing

	#run_remove_posts()

	#run_extract_stats()

	#run_download()

	#post = choose_post()
	#generate_post(post,post_online=False)

	#For use 
	posting_wrapper(error_check=False)
