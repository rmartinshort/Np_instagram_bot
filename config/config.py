#!/usr/bin/env python
#RMS 2019

import os
import pandas as pd
import torch 

#Do we want to use a pretrained classifier
#right now it determines people, animals, landscapes and buildings
USE_CLASSIFIER = True

#must be in this order!
IMAGE_CLASSES = ("animals","buildings","landscapes","people")

current_dir = os.getcwd()
PACKAGE_ROOT = current_dir
DATASETS = PACKAGE_ROOT+'/data'
MODELS = PACKAGE_ROOT+'/classifiers'


if USE_CLASSIFIER == True:
	LOADED_CLASSIFIER = torch.load(MODELS+'/NP_insta_model_v1.pkl')

#number of hours between posts
POST_FREQ = 8
#number of hours between logging attempts
LOG_FREQ = 1

#weightings for generating the image ranks
LIKES_WEIGHT = 1
COMMENT_WEIGHT = 1

# maxiumum number of images to download from each profile 
# at a time
MAX_PROFILE_DL = 5
# number of days in the past from which to scape data. A smaller 
# number will lead to more 'up to date' posts, but fewer of them
PAST_DAYS_DL = 14

#list of features that we expect to be created by FeatureGenerator
GENERATED_FEATURES = ['credits','nlikes','ncomments','nfollowers','nlikes_per_follower','ncomments_per_follower']

#Hashtags that will disqualify an image 
HASHTAG_QC = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday','protect','law','notrace','litter','invasive']

#Datafiles that the progam uses
PROFILES_TO_DOWNLOAD = DATASETS+'/national_park_instaids.csv'

PROFILE_LOGGER = DATASETS+'/profile_log.csv'

PREV_POSTS = DATASETS+'/used_image_files.csv'

CAPTIONS = DATASETS+'/captions_list.csv'

TAGS = DATASETS+'/tags_list.csv'

MYPROFILELOG = DATASETS + '/myprofiledata.dat'

#Read username and password
upass = pd.read_csv(DATASETS+'/upass.csv',names=['uname','id','pass'])

INSTA_UNAME = upass.iloc[0]['uname']
INSTA_PASS =  upass.iloc[0]['pass']
INSTA_ID = upass.iloc[0]['id']

#Tag line information used in every post
TAG_LINE_1 = "Inspirational Landscapes is a personal blog and not affiliated with the government."
TAG_LINE_2 = "Please tag us in your posts for the chance to be featured!"
TAG_LINE_3 = "Learn more and get the latest updates about national parks at www.nps.gov"
