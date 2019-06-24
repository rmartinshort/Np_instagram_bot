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

def run_remove_posts() -> None:

	'''Remove old posts from the database'''

	pipeline.remove_pipe.removeoldposts()

	print("Done remove old posts")

def run_download() -> None:

	t0 = time.time()

	pipeline.download_pipe.download()

	print("Done download")

	t1 = time.time()

	print(f'Time taken: {t1-t0} seconds')

	#Delete any prevously posted files that still exist in the repo

	pipeline.remove_pipe.removepreviousposts()

def choose_post() -> dict:

	"""Returns a dictionary containing the path of the image
	to be posted and the caption to accompany it"""

	#X is a dataframe containing the metadata for each of the downloaded posts, ready for processing
	X = pipeline.metadata_gen.process_posts()

	#This processing pipeline will produce the file that we want to repost and its
	#associated caption and credits

	result = pipeline.process_pipe.fit_transform(X)
	#result = pipeline.process_pipe.transform(X)
	
	return result

def generate_post(post_meta,post_online=True) -> None:

	'''This uploads a selected image and caption to instagram'''

	username = config.INSTA_UNAME
	password = config.INSTA_PASS

	image_file = post_meta['Image']
	print(image_file)
	image_caption = post_meta['Caption']

	print(image_file)
	print(image_caption)

	print(username,password)


	if post_online == True:

		with client(username, password, write_cookie_file=True) as cli:
			cli.upload(image_file, image_caption)

	used_image_file = open(config.PREV_POSTS,'a')
	used_image_file.write(f"{image_file},{datetime.now()}\n")
	used_image_file.close()
	os.remove(image_file)


def download_wrapper() -> None:

	'''For automated downloads'''

	while True:

		run_remove_posts()
		run_extract_stats()
		run_download()
		post = choose_post()

		print(post)

		if post['Image'] == "no_image":
			print('Image inventory empty. Waiting to try again')
			time.sleep(3600*config.POST_FREQ)
		else:
			generate_post(post,post_online=True)
			time.sleep(3600*config.POST_FREQ)





if __name__ == '__main__':

	#For testing

	#run_remove_posts()

	#run_extract_stats()

	#run_download()

	#post = choose_post()
	#generate_post(post,post_online=False)

	#For use 
	download_wrapper()
