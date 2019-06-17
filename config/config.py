#!/usr/bin/env python
#RMS 2019

import os


current_dir = os.getcwd()
PACKAGE_ROOT = current_dir
DATASETS = PACKAGE_ROOT+'/data'

#number of hours between posts
POST_FREQ = 8

#weightings for generating the image ranks
LIKES_WEIGHT = 1
COMMENTS_WEIGHT = 1

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

#Username and password
INSTA_UNAME = 
INSTA_PASS = 

#Tag line information used in every post
TAG_LINE_1 = "Inspirational Landscapes is a personal blog and not affiliated with the government"
TAG_LINE_2 = "Please tag us in your posts for the chance to be featured!"
TAG_LINE_3 = "Learn more and get the latest updates about national parks at www.nps.gov"
