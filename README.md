# Np_instagram_bot
An automated tool that scrapes national park instagram images and reposts

## Function  

This tool is designed to scape recent posts from any number of instagram accounts (account names and id numbers in data/national_park_instaids.csv). It ranks the posts based on a weighted sum of likes/follower/day and comments/follower/day, performs QC and then chooses an image to repost. 

It will also design a caption for reposting.
It can be instructed to automatically post at a user-provided frequency.  

## Use  

The driver script is called run_download.py. This contains driver functions for extacting and saving the current status of the instagram profiles
we repost from, deleting outdated posts in our repo, downloading new posts, designing a new post and actually putting it online. 

All the user-defined parameters are set in config.py  

datadownloaders.py: Classes for obtaining images and organizing their metadata    
preprocessing.py: Classes for generating features, post QC, designing new captions etc.   
pipeline.py: The processing pipleline. We try to keep the steps in an sklearn pipeline format as far as possible  
ProfileManip.py: This is not actually needed, but will gather metadata about the profiles themselves and save to a file  
bot_script.py: Uses instabot_py to like, follow and unfollow other profiles. Run this in the background. 

## How to run  

- Adjust parameters in config.py to your liking  
- Run bot_script.py in the backgound  
- Run run_download.py. Every x hours, a post will be generated  

## Ideas/to-do list  

- Logging followers of the profile though time - how do people respond to different content?   
- Choose content based on recent history of responses to previous posts
- Image classification for better caption design  
- Style transfer for artistic images  
- NLP on the original captions and comments to try to extract sentiment/improve captioning  



