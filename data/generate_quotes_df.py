#!/usr/bin/env python
#RMS 2019 

#One time script to collect all the quotes files into a single dataframe. Run this if you've added some quotes and want them 
#to be considered for classification 

import pickle
import pandas as pd
import numpy as np
import glob


def prep_quote(quote):

    return quote.lower()


def main():

    LDA_model = pickle.load(open('../classifiers/LDA_basemodel.pkl','rb'))
    cv_model = pickle.load(open('../classifiers/cv_basemodel.pkl','rb'))

    quotes = list(sorted(glob.glob('captions_list*')))

    dfs = []

    for infile in quotes:
        description = infile.split('_')[-1].split('.')[0]

        if description not in ['people','animals','landscapes','buildings']:
            description = 'general'

        df = pd.read_csv(infile,sep='\t',names=['quote'])
        df['imageclass'] = [description]*len(df)
        dfs.append(df)

    allquotes = pd.concat(dfs)
    allquotes['prepped_quote'] = allquotes['quote'].apply(prep_quote)

    #Use the count vectorizer model to prep the quotes
    dtm = cv_model.transform(allquotes['prepped_quote'])
    
    #Apply the loaded LDA model
    quote_probs = LDA_model.transform(dtm)

    #Determine the class of each quote
    quote_class = np.argmax(quote_probs,axis=1)

    allquotes['quoteclass'] = quote_class

    #Write file containing each quote and its class
    allquotes[['quote','quoteclass','imageclass']].to_csv('all_captions_with_class.csv',index=False,sep='\t')

if __name__ == "__main__":

    main()


