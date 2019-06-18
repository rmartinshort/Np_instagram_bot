#!/usr/bin/env python
#RMS 2019

#Logging tool that allows a user to moniter their own account over time

import instaloader
import datetime
import numpy as np
from config import config
import time

def profile_information(profile):
    
    """Grab current profile information and save to a dataframe"""

    L = instaloader.Instaloader()
    
    info = {
        'name':np.nan,
        'userid':np.nan,
        'followers':np.nan,
        'followees':np.nan, 
        'time_since_last_post':np.nan,
        'likes_of_last_post':np.nan,
        'comments_of_last_post':np.nan,
        'time':np.nan,
        'time_of_last_post':np.nan
    }
    
        
    try:
	    prof_data = instaloader.Profile.from_username(L.context,profile)

	    ctime = datetime.datetime.now()
	    info['name'] = profile
	    info['time'] = ctime
	    info['userid'] = prof_data.userid
	    info['followers'] = prof_data.followers
	    info['followees'] = prof_data.followees

	    #Get posts
	    myposts = prof_data.get_posts()

	    #This is not efficient when the number of posts and likes gets large. Need to change. 
	    i = 0
	    for post in myposts:

	        if i == 0:
	            info['time_since_last_post']=(ctime-post.date).seconds
	            info['likes_of_last_post']=post.likes
	            info['comments_of_last_post']=post.comments
	            info['time_of_last_post']=post.date
	            i += 1
	        else:
	            break
    except:
        pass
            
            
    return info


def write_info(info,logfile=config.MYPROFILELOG):
    
    infile = open(logfile,'a+')
    
    for key in info:
        infile.write(str(info[key])+',')
    
    infile.write('\n')
    
    infile.close()

def main():

	while True:

		print("Logging!")
		info = profile_information(config.INSTA_UNAME)
		write_info(info)
		time.sleep(3600*config.LOG_FREQ)

if __name__ == "__main__":

	main()


