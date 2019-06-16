#!/usr/bin/env python
#RMS 2019

from sklearn.pipeline import Pipeline
import datadownloaders as dd
import ProfileManip as pm
import preprocessing as pp

#download the profiles
profiles_pipe = pm.ExtractParkStats()

#remove old posts
remove_pipe = dd.RemoveOldPosts()

#download the posts
download_pipe = dd.DownloadNewPosts()

#metadata generation
metadata_gen = dd.PackMetadata()

#preprecessing
process_pipe = Pipeline(

	[
	('feature_generation',
		pp.FeatureGenerator()),
	('caption_construction',
		pp.CaptionConstructor()),
	('image_choice',
		pp.ChoosePost())
    
	]
)