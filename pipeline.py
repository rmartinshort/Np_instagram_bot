#!/usr/bin/env python
#RMS 2019

from sklearn.pipeline import Pipeline
import datadownloaders as dd
import ProfileManip as pm
import preprocessing as pp
from config import config

#download the profiles
profiles_pipe = pm.ExtractParkStats()

#metadata generation
metadata_gen = dd.PackMetadata()

#preprecessing
#add any content classification and caption generation stages here 

if config.USE_CLASSIFIER == True: 

	process_pipe = Pipeline(

		[
		('feature_generation',
			pp.FeatureGenerator()),
		('caption_construction',
			pp.CaptionConstructor()),
		('image_classification',
		    pp.ContentDetermination()),
		('content_classification',
			pp.CaptionTopicModelling()),
		('image_choice',
			pp.ChoosePost())
		]
	)
	
else:

	process_pipe = Pipeline(

		[
		('feature_generation',
			pp.FeatureGenerator()),
		('caption_construction',
			pp.CaptionConstructor()),
		('content_classification',
			pp.CaptionTopicModelling()),
		('image_choice',
			pp.ChoosePost())
		]
	)
