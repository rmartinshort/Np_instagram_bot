#!/usr/bin/env python 
#RMS 2019

import instaloader
import pandas as pd
import numpy as np
import glob
import os
from datetime import datetime, timedelta
from sklearn.base import BaseEstimator, TransformerMixin
from config import config
import shutil

class RemoveOldPosts():

    """Looks though downloaded posts and removes those older than given number of days"""

    def __init__(self,\
        profile_list=config.PROFILES_TO_DOWNLOAD,\
        pastdays=config.PAST_DAYS_DL,\
        used_files=config.PREV_POSTS,
        username=config.INSTA_UNAME,
        password=config.INSTA_PASS) -> None:

        profile_list = pd.read_csv(profile_list,names=['profile_name','profile_id'])
        self.profile_list = list(profile_list['profile_id'])   

        self.pastdays = pastdays  
        self.now = datetime.now()
        self.used_files = used_files
        self.L = instaloader.Instaloader(quiet=True)
        self.username=username
        self.password=password


    def removeoldposts(self) -> None:

        self._removeloop()

    def removepreviousposts(self) -> None:

        prev_posts = pd.read_csv(self.used_files,names=['filename','post_date'])
        self.prev_posts = list(prev_posts['filename']) 

        self._remove_old_posts()

    def _removeloop(self) -> None:

        self.L.login(user=self.username,passwd=self.password)

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
                            #print(f'Deleting {f}: Post outdated')
                            os.remove(f)

    def _remove_old_posts(self) -> None:

        '''Remove image files that are known to have already been posted'''

        for image_file in self.prev_posts:

            if os.path.exists(image_file):

                os.remove(image_file)
                print(f'Deleting {image_file}: post already used')

            else:

                print(f"Tried to delete {image_file}, but file not found!")



class DownloadNewPosts():

    """Connect to Instagram and get post data from specified profiles"""

    def __init__(self, username=config.INSTA_UNAME,password=config.INSTA_PASS,\
        profile_list=config.PROFILES_TO_DOWNLOAD,\
        download_dir=config.DATASETS,\
        maxdownloadsperprofile=config.MAX_PROFILE_DL,\
        pastdays=config.PAST_DAYS_DL,repo=config.POSTS) -> None:

        self.profile_list = pd.read_csv(profile_list,names=['profile_name','profile_id'])
        self.profile_list = list(self.profile_list['profile_id'])
        self.download_dir = download_dir
        self.maxdownloadsperprofile = maxdownloadsperprofile
        self.pastdays = pastdays
        self.L = instaloader.Instaloader(quiet=False,download_videos=False)

        self.username = username
        self.password = password
        self.repo = repo

    def download(self) -> None:
        """Do the download across all profiles"""

        for id_number in self.profile_list:

            self._download_recent_posts(id_number)

        self._move_to_repo()

    def _download_recent_posts(self,profile_id) -> None:
        """For downloading insta posts from one profile"""

        self.now = datetime.now()

        #New as of Aug 2019 - need to log in for better download
        self.L.login(user=self.username,passwd=self.password)

        posts = instaloader.Profile.from_id(context=self.L.context,profile_id=str(profile_id)).get_posts()
    
        i = 0
        for post in posts:
            if i < self.maxdownloadsperprofile:
                tsince = self.now - post.date

                if tsince.days <= self.pastdays:
                    #print(post,profile_id)
                    try:
                        self.L.download_post(post,str(profile_id))
                    except:
                        print('Could not download post %s for profile %i' (post,profileid))

                #Remove all in the download directory and redownload
                #os.system('rm -rf %s/*' %self.download_dir)
                #os.system('mv -f %s %s' %(profile_id,self.download_dir))
                i += 1
            else:
                break

    def _move_to_repo(self) -> None:

        '''Generate a repository that contains material to be considered for posting'''

        #regenerate the repo directory. This is needed so that the system does not post the duplicate files

        print("Removing and remaking post database")

        try:
            shutil.rmtree(self.repo)
            os.mkdir(self.repo)
        except:
            print('Cannnot remove repo at the present time - it is likely being used by another script')

        for profileid in self.profile_list:

            posts_data = glob.glob(f'{profileid}/*.json.xz')
            
            for postmeta in posts_data:
                
                post_name = postmeta.split('.')[0]
                post_image_name = post_name+'.jpg'

                print(post_image_name)
                
                if os.path.isfile(post_image_name):

                    post_meta_name_new = self.repo + '/' + str(profileid) + '_' + postmeta.split('/')[1]
                    post_image_name_new = self.repo + '/' + str(profileid) + '_' + post_image_name.split('/')[1]

                    print(post_image_name,post_image_name_new)
                    print(postmeta,post_meta_name_new)

                    print('moving files')
                    os.system('mv %s %s' %(post_image_name,post_image_name_new))
                    os.system('mv %s %s' %(postmeta,post_meta_name_new))

                else:

                    print('file not found')




class PackMetadata():

    """Generate a dataframe containing metadata of the desired posts"""

    def __init__(self,download_dir=config.DATASETS,repo=config.POSTS,prev_posts=config.PREV_POSTS,
        username=config.INSTA_UNAME,password=config.INSTA_PASS) -> None:

        self.download_dir = download_dir
        self.repo = repo
        self.L = instaloader.Instaloader(quiet=True)
        self.username=username
        self.password=password
        self.used_files = prev_posts

    def _get_metadata(self,metadatafile) -> None:
    
            username = metadatafile.owner_profile.username
            caption = metadatafile.caption
            caption_hastags = metadatafile.caption_hashtags
            postdate = metadatafile.date
            time_since_postdate = datetime.now() - postdate
            nlikes = metadatafile.likes

            ncomments = metadatafile.comments
            nfollowers = metadatafile.owner_profile.followers
            nlikes_per_follower = nlikes/nfollowers
            ncomments_per_follower = ncomments/nfollowers
            
            return [username,caption,caption_hastags,postdate,time_since_postdate,\
                   nlikes,ncomments,nfollowers,nlikes_per_follower,ncomments_per_follower]
        
        

    def process_posts(self,debug=False) -> pd.DataFrame:

        self.L.login(user=self.username,passwd=self.password)

        prev_posts = pd.read_csv(self.used_files,names=['filename','post_date'])
        self.prev_posts = list(prev_posts['filename'])

        
        post_metadata = {
            'Flocation':[],
            'caption':[],
            'credits':[],
            'postdate':[],
            'timesincepost':[],
            'nlikes':[],
            'ncomments':[],
            'nfollowers':[],
            'nlikes_per_follower':[],
            'ncomments_per_follower':[]
        }

        #Get all metadata from the repo

        allmeta = glob.glob(self.repo+'/*.json.xz')

        for postmeta in allmeta:
            
            post_name = postmeta.split('.')[0]
            post_image_name = post_name+'.jpg'
            
            if os.path.isfile(post_image_name) and post_image_name not in prev_posts:
                
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
                    post_metadata['ncomments'].append(metadata_list[6])
                    post_metadata['nfollowers'].append(metadata_list[7])
                    post_metadata['nlikes_per_follower'].append(metadata_list[8])
                    post_metadata['ncomments_per_follower'].append(metadata_list[9])
                        
            
        return pd.DataFrame(post_metadata)


