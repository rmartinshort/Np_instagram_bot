#!/usr/bin/env python 
#RMS 2019

import instaloader
import pandas as pd
import numpy as np
import glob
import os
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sklearn.base import BaseEstimator, TransformerMixin
from config import config

class RemoveOldPosts():

    """Looks though downloaded posts and removes those older than given number of days"""

    def __init__(self,profile_list=config.PROFILES_TO_DOWNLOAD,pastdays=14) -> None:

        self.profile_list = pd.read_csv(profile_list,names=['profile_name','profile_id'])
        self.profile_list = list(self.profile_list['profile_id'])    
        self.pastdays = pastdays  
        self.now = datetime.now()
        self.L = instaloader.Instaloader(quiet=True)

    def remove(self) -> None:

        self._removeloop()

    def _removeloop(self) -> None:

        for profileid in self.profile_list:

            posts_data = glob.glob(f'{profileid}/*.json.xz')
            
            for postmeta in posts_data:
                
                post_name = postmeta.split('.')[0]
                post_image_name = post_name+'.jpg'
                
                if os.path.isfile(post_image_name):
                     
                    metadata = instaloader.load_structure_from_file(context=self.L.context,\
                        filename=postmeta)

                    #get the date of of the post
                    postdate = metadata.date

                    post_age = self.now - postdate
                    if post_age.days > self.pastdays:
                        for f in glob.glob(f"{post_name}*"):
                            print(f'Deleting {f}: Post outdated')
                            os.remove(f)



class DownloadNewPosts():
    """Connect to Instagram and get post data from specified profiles"""

    def __init__(self, profile_list=config.PROFILES_TO_DOWNLOAD,download_dir=config.DATASETS,maxdownloadsperprofile=5,pastdays=14) -> None:

        self.profile_list = pd.read_csv(profile_list,names=['profile_name','profile_id'])
        self.profile_list = list(self.profile_list['profile_id'])
        self.download_dir = download_dir
        self.maxdownloadsperprofile = maxdownloadsperprofile
        self.pastdays = pastdays
        self.L = instaloader.Instaloader(quiet=True)
        self.now = datetime.now()

    def download(self) -> None:
        """Do the download across all profiles"""

        for id_number in self.profile_list:

            self._download_recent_posts(id_number)

    def _download_recent_posts(self,profile_id) -> None:
        """For downloading insta posts from one profile"""

        posts = instaloader.Profile.from_id(context=self.L.context,profile_id=profile_id).get_posts()
    
        i = 0
        for post in posts:
            if i < self.maxdownloadsperprofile:
                tsince = self.now - post.date

                if tsince.days <= self.pastdays:
                    self.L.download_post(post,str(profile_id))

                #Remove all in the download directory and redownload
                #os.system('rm -rf %s/*' %self.download_dir)
                #os.system('mv -f %s %s' %(profile_id,self.download_dir))
                i += 1
            else:
                break


class PackMetadata():

    """Generate a dataframe containing metadata of the desired posts"""

    def __init__(self,profile_list=config.PROFILES_TO_DOWNLOAD,prev_posts=config.PREV_POSTS,download_dir=config.DATASETS) -> None:

        self.download_dir = download_dir
        self.L = instaloader.Instaloader(quiet=True)
        profiles = pd.read_csv(profile_list,names=['profile_name','profile_id'])
        self.profiles = list(profiles['profile_id'])

        #Read previous posts so that we don't post the same file multiple times
        prev_posts = pd.read_csv(prev_posts,names=['Name','Date'])
        self.prev_posts = list(prev_posts['Name'])

    def _get_metadata(self,metadatafile) -> None:
    
            username = metadatafile.owner_profile.username
            caption = metadatafile.caption
            caption_hastags = metadatafile.caption_hashtags
            postdate = metadatafile.date
            time_since_postdate = datetime.now() - postdate
            nlikes = metadatafile.likes

            try:
                location_name = metadatafile.location.name
            except:
                location_name = np.nan

            try:
                location_lat = metadatafile.location.lat
                location_lon = metadatafile.location.lng
            except:
                location_lon = np.nan
                location_lat = np.nan

            ncomments = metadatafile.comments
            nfollowers = metadatafile.owner_profile.followers
            nlikes_per_follower = nlikes/nfollowers
            ncomments_per_follower = ncomments/nfollowers
            
            return [username,caption,caption_hastags,postdate,time_since_postdate,\
                   nlikes,location_name,location_lat,\
                   location_lon,ncomments,nfollowers,nlikes_per_follower,ncomments_per_follower]
        
        

    def process_posts(self,debug=False) -> pd.DataFrame:
        
        post_metadata = {
            'Flocation':[],
            'caption':[],
            'credits':[],
            'postdate':[],
            'timesincepost':[],
            'nlikes':[],
            'location':[],
            'lon':[],
            'lat':[],
            'ncomments':[],
            'nfollowers':[],
            'nlikes_per_follower':[],
            'ncomments_per_follower':[]
        }

        for profileid in self.profiles:

            posts_data = glob.glob(f'{profileid}/*.json.xz')
            
            for postmeta in posts_data:
                
                post_name = postmeta.split('.')[0]
                post_image_name = post_name+'.jpg'
                
                if os.path.isfile(post_image_name) and post_image_name not in self.prev_posts:
                    
                    print(f'Found post {postmeta}')
                    
                    if debug == True:
                        post_image = mpimg.imread(post_image_name)
                        plt.imshow(post_image)
                        plt.show()
                        
                    metadata = instaloader.load_structure_from_file(context=self.L.context,\
                        filename=postmeta)
                    
                    #metadata that is useful to us
                    metadata_list = self._get_metadata(metadata)
                    
                    if metadata_list:
                    
                        post_metadata['Flocation'].append(post_image_name)
                        post_metadata['credits'].append(metadata_list[0])
                        post_metadata['caption'].append(metadata_list[1])
                        post_metadata['postdate'].append(metadata_list[3])
                        post_metadata['timesincepost'].append(metadata_list[4])
                        post_metadata['nlikes'].append(metadata_list[5])
                        post_metadata['location'].append(metadata_list[6])
                        post_metadata['lat'].append(metadata_list[7])
                        post_metadata['lon'].append(metadata_list[8])
                        post_metadata['ncomments'].append(metadata_list[9])
                        post_metadata['nfollowers'].append(metadata_list[10])
                        post_metadata['nlikes_per_follower'].append(metadata_list[11])
                        post_metadata['ncomments_per_follower'].append(metadata_list[12])
                        
            
        return pd.DataFrame(post_metadata)


