#!/usr/bin/env python 
#RMS 2019 

import numpy as np
import instaloader
import pandas as pd
import os
import datetime
from config import config

class ExtractParkStats():

    """Get useful information about each of the park instagram pages"""

    def __init__(self, profile_list=config.PROFILES_TO_DOWNLOAD,download_dir=config.DATASETS,logfile=config.PROFILE_LOGGER) -> None:

        self.profiles = pd.read_csv(profile_list,names=['profile_name','profile_id'])
        self.download_dir = download_dir
        self.logfilename = logfile
        self.L = instaloader.Instaloader(quiet=True)

        if os.path.isfile(logfile):
            self.logfile = pd.read_csv(self.logfilename,sep='\t')
        else:
            self.logfile = 'None'


    def download(self) -> None:
        """Do the download across all profiles"""

        current_data = self._profile_information()

        if isinstance(self.logfile,str):
            current_data.to_csv(self.logfilename,index=False,sep='\t')
        else:
            self.logfile = pd.concat([self.logfile,current_data],axis=0)
            self.logfile.to_csv(self.logfilename,index=False,sep='\t')

    def _profile_information(self) -> pd.DataFrame:
        
        """Grab current profile information and save to a dataframe"""
        
        info = {
            'name':[],
            'userid':[],
            'followers':[],
            'followees':[],
            'bio':[],
            'time':[]
        }
        
        for profile in list(self.profiles['profile_name']):
                   
            #try:
                prof_data = instaloader.Profile.from_username(self.L.context,profile)
                
                ctime = datetime.datetime.now()
                info['name'].append(profile)
                info['time'].append(ctime)
                info['userid'].append(prof_data.userid)
                info['followers'].append(prof_data.followers)
                info['followees'].append(prof_data.followees)
                info['bio'].append(prof_data.biography)
            
            #except:
            #    continue
                
        return pd.DataFrame(info)
