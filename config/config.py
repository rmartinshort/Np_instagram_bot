#!/usr/bin/env python
#RMS 2019

import os


current_dir = os.getcwd()
PACKAGE_ROOT = current_dir
DATASETS = PACKAGE_ROOT+'/data'

#number of hours between posts
POST_FREQ = 8

GENERATED_FEATURES = ['credits','nlikes','ncomments','nfollowers','nlikes_per_follower','ncomments_per_follower']

HASHTAG_QC = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday','protect','law','notrace','litter','invasive']

PROFILES_TO_DOWNLOAD = DATASETS+'/national_park_instaids.csv'

PROFILE_LOGGER = DATASETS+'/profile_log.csv'

PREV_POSTS = DATASETS+'/used_image_files.csv'

CAPTIONS = DATASETS+'/captions_list.csv'

TAGS = DATASETS+'/tags_list.csv'

INSTA_UNAME = 'inspiring_national_parks'
INSTA_PASS = 'nationalparks'


TAG_LINE_1 = "Inspirational Landscapes is a personal blog and not affiliated with the government"
TAG_LINE_2 = "Please tag us in your posts for the chance to be featured!"
TAG_LINE_3 = "Learn more and get the latest updates about national parks at www.nps.gov"
