#!/usr/bin/env python
#RMS 2019

import numpy as np
import pandas as pd
import re
from sklearn.base import BaseEstimator, TransformerMixin
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from config import config
import torch 
from torchvision import transforms
from PIL import Image
from datetime import datetime

class FeatureGenerator(BaseEstimator, TransformerMixin):

    """Generate features used to rank posts"""

    def __init__(self) -> None:

        #This hard coding is not ideal - come back and fix once the processing is
        #finalized
        self.variables = config.GENERATED_FEATURES
        self.now = datetime.now()

    def fit(self, X: pd.DataFrame, y: pd.Series = None
            ) -> 'FeatureGenerator':

        """Fit statement to accomodate the sklearn pipeline."""

        self.summary = X[self.variables].groupby('credits').mean().reset_index()

        park_names = list(X['credits'].unique())

        self.names_dir = {}
        i = 1
        for name in park_names:
            self.names_dir[name] = i
            i += 1

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:

        """Apply the transforms to the dataframe."""

        X = X.copy()

        def __image_size_check(image_loc) -> float:

            image = mpimg.imread(image_loc)
            (h,w,n) = image.shape
            if w < 800:
                return np.nan
            else:
                return (h,w,n)

        def __difference_from_mean_likes_per_follower(row) -> float:

            name = row['credits']
            ndays = (self.now - row['postdate']).days

            if ndays < 1:
                ndays = 1

            return (row['nlikes_per_follower'] - \
                self.summary[self.summary['credits']==name]['nlikes_per_follower'].values[0])/(self.summary[self.summary['credits']==name]['nlikes_per_follower'].values[0]*ndays)

        def __difference_from_mean_comments_per_follower(row) -> float:

            name = row['credits']
            ndays = (self.now - row['postdate']).days

            if ndays < 1:
                ndays = 1

            return (row['ncomments_per_follower'] - \
                self.summary[self.summary['credits']==name]['ncomments_per_follower'].values[0])/(self.summary[self.summary['credits']==name]['ncomments_per_follower'].values[0]*ndays)

        def __categorize_parks(parkid) -> int:

            return self.names_dir[parkid]

        def __post_rank(row,likes_weight=config.LIKES_WEIGHT,comments_weight=config.COMMENT_WEIGHT) -> float:

            return row['mean_nlikes_diff']*likes_weight + row['mean_ncomments_diff']*comments_weight


        X['postdate'] = pd.to_datetime(X['postdate'])
        X['mean_nlikes_diff'] = X.apply(lambda row: __difference_from_mean_likes_per_follower(row),axis=1)
        X['mean_ncomments_diff'] = X.apply(lambda row: __difference_from_mean_comments_per_follower(row),axis=1)
        X['park_id'] = X['credits'].apply(__categorize_parks)
        X['rank'] = X.apply(lambda row: __post_rank(row),axis=1)
        X['image_size'] = X['Flocation'].apply(__image_size_check)

        return X



class CaptionConstructor(BaseEstimator,TransformerMixin):

    '''Construct captions and do QC'''

    def __init__(self) -> None:

        return None

    def fit(self, X: pd.DataFrame, y: pd.Series = None) -> 'CaptionConstructor':

        #List of tags that we don't want to include
        self.hashtagQClist = config.HASHTAG_QC
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:

        X = X.copy()

        def __extract_hashtags(string):

            try:
                hashtags = [re.sub(r"(\W+)$", "", j) for j in set([i for i in string.split() if i.startswith("#")])]
            except:
                return np.nan
            if len(hashtags) == 0:
                return np.nan
            else:
                return hashtags

        def __extract_pcredits(row):
            string = row['caption']

            try:
                pcredits = [re.sub(r"(\W+)$", "", j) for j in set([i for i in string.split() if i.startswith("@")])]
                pcredits.append('@'+row['credits'])
            except:
                return np.nan

            return pcredits

        def __hashtagQC(hashtags):
            
            hashstring = ''.join(hashtags).lower()
            for word in self.hashtagQClist:
                if word in hashstring:
                    return np.nan
            return [e.lower() for e in hashtags if len(e) > 1]

        def __generate_repost_caption(row):
    
            caption = row['caption']
            date = row['postdate']
            credit = row['credits']
            a = re.split("[.!]+", caption)[0]+'!'
            a = re.sub('[@$""'']', '', a)
            if '#' in a:
                return np.nan
            else:
                post_date = f"{date.month:02d}-{date.day:02d}-{date.year}"
                
                comment = f'Here is a segment from the original post, by @{credit} on {post_date}: "{a}"'
                return comment


        X['hashtags'] = X['caption'].apply(__extract_hashtags)
        X['pcredits'] = X.apply(lambda row: __extract_pcredits(row),axis=1)
        X['postdate'] = pd.to_datetime(X['postdate'])

        X.dropna(inplace=True)

        X['hashtags'] = X['hashtags'].apply(__hashtagQC)
        X['repost_comment'] = X.apply(lambda row: __generate_repost_caption(row),axis=1)

        X.dropna(inplace=True)
        X.drop_duplicates(inplace=True,keep='first',subset='credits')

        return X


class ContentDetermination(BaseEstimator,TransformerMixin):

    '''Load a pretrained CNN (based in vgg16) and classify the images
    into people, animals, landscapes and buildings (or whatever labels have
    been provided)'''

    def __init__(self) -> None:

        return None

    def fit(self, X: pd.DataFrame, y: pd.Series = None) -> 'ContentDetermination':

        self.mymodel = torch.load(config.CLASSIFIERPATH)


        self.transform_validation = transforms.Compose([transforms.Resize((224,224)),
                                transforms.ToTensor(),
                                transforms.Normalize((0.5,),(0.5,))])

        self.classes = config.IMAGE_CLASSES

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:

        classifications = []

        for image_file in X['Flocation']:

            img = Image.open(image_file)
            img = self.transform_validation(img)
            image_for_model = img.unsqueeze(0)
            output = self.mymodel(image_for_model)
            _, preds = torch.max(output,1)
            
            classifications.append(self.classes[preds.item()])

        X['Image_class'] = classifications

        return X

class ChoosePost(BaseEstimator, TransformerMixin):

    """Chose an image and caption to post"""

    def __init__(self,captions=config.CAPTIONS,tags=config.TAGS) -> None:

        self.captions_land = captions['landscapes']
        self.captions_ani = captions['animals']
        self.captions_people = captions['people']
        self.captions_build = captions['buildings']

        self.tags_loc = tags

    def fit(self, X: pd.DataFrame, y: pd.Series = None
            ) -> 'ChoosePost':
        """Fit statement to accomodate the sklearn pipeline."""

        ranks = X['rank'].values
        ranks = np.nan_to_num(ranks)
        ranks = ranks - min(ranks)

        #probability of choosing that file to post
        self.p = ranks/sum(ranks)

        self.loaded_comments_land = pd.read_csv(self.captions_land,sep='\t',names=['caption'])
        self.loaded_comments_ani = pd.read_csv(self.captions_ani,sep='\t',names=['caption'])
        self.loaded_comments_people = pd.read_csv(self.captions_people,sep='\t',names=['caption'])
        self.loaded_comments_build = pd.read_csv(self.captions_build,sep='\t',names=['caption'])

        self.loaded_tags = pd.read_csv(self.tags_loc,names=['tag'])

        return self

    def transform(self, X: pd.DataFrame,debug=False) -> dict:

        attempts = 0
        error = 1
        chosen_image = None
        X = self._rank_posts(X)

        while error == 1 and attempts < 10:

            #try:

                #Choose one image from those that have passed the QC stage

                pp = np.random.choice(np.arange(len(X)),size=1,replace=False,p=self.p)[0]

                chosen_image = X.iloc[pp]['Flocation']
                chosen_image_caption = X.iloc[pp]['repost_comment']
                chosen_image_hashtags = X.iloc[pp]['hashtags']
                chosen_image_pcredits = X.iloc[pp]['pcredits']
                chosen_image_class = X.iloc[pp]['Image_class']

                repost_comment = self._generate_caption_basic(chosen_image_caption,list(chosen_image_pcredits),\
                    list(chosen_image_hashtags),chosen_image_class)

                #Some QC stage here to determine if the chosen image is OK
                error = 0

            #except:
            #    attempts += 1

        if chosen_image is None:

            print("ERROR!")

        else:

            if debug == True:

                print(repost_comment)

                image = mpimg.imread(chosen_image)
                plt.imshow(image)
                plt.axis('off')
                plt.show()

        return {'Image':chosen_image,'Caption':repost_comment}

    def _rank_posts(self,X,variable='rank') -> pd.DataFrame:

        X.sort_values(by=variable,ascending=False,inplace=True)

        return X

    def _generate_caption_basic(self,base_caption,credits,hashtags,image_class):
        
        """Run this to generate a caption specific to the image that has been chosen"""

        print(f"Image class for chosen image is {image_class}")

        if image_class == 'animals':
            loaded_comments = self.loaded_comments_ani
        elif image_class == 'landscapes':
            loaded_comments = self.loaded_comments_land
        elif image_class == 'people':
            loaded_comments = self.loaded_comments_people
        elif image_class == 'buildings':
            loaded_comments = self.loaded_comments_build
        
        comments_list = list(loaded_comments['caption'])
        tags_list = list(self.loaded_tags['tag'])
        
        chosen_caption = np.random.choice(comments_list,size=1)[0]
        chosen_tags = list(np.random.choice(tags_list,size=20,replace=False))


        if ' - ' in chosen_caption:
            caption_parts = chosen_caption.split(' - ')
            chosen_caption = '"'+caption_parts[0]+'"'+' - '+caption_parts[1]
        
        for hashtag in hashtags:
            if hashtag not in chosen_tags:
                chosen_tags.append(hashtag)
        
        credits = ' '.join(list(set(credits)))
        chosen_tags = ' '.join(chosen_tags)

        tl1 = config.TAG_LINE_1
        tl2 = config.TAG_LINE_2
        tl3 = config.TAG_LINE_3

        repost_caption = f'{chosen_caption}\n\n\n{base_caption}\n📸: {credits}\n\n{tl1}\n\n{tl2}\n\n{tl3}\n\n\n\n\n{chosen_tags}'
        
        return repost_caption
    



