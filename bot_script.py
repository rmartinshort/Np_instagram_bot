#!/usr/bin/env python3
#RMS 2019

from instabot_py import InstaBot
from config import config

bot = InstaBot(
    login=config.INSTA_UNAME,  # Enter username (lowercase). Do not enter email!
    password=config.INSTA_PASS,
    like_per_day=1000,
    comments_per_day=0,
    tag_list=['nationalparks', 'nps', 'nature', 'planetearth', 'naturelover', 'travel',
              'naturephotography', 'wanderlust', 'preservation', 'roadtrip', 'findyourpark',
              'usa', 'america', 'adventure', 'tourism', 'inspiration', 'art',
              'wonder', 'majesty', 'nationalparksusa', 'hiking', 'camping',
              'backpacking', 'sublime', 'preservation', 'environment', 'animals', 'igersnature'],
    tag_blacklist=[],
    user_blacklist={},
    max_like_for_one_tag=50,
    follow_per_day=100,
    follow_time=24 * 60 * 60 * 2,
    unfollow_per_day=100,
    unlike_per_day=0,
    unfollow_recent_feed=True,
    # If True, the bot will also unfollow people who dont follow you using the recent feed. Default: True
    time_till_unlike=3 * 24 * 60 * 60,  # 3 days
    unfollow_break_min=15,
    unfollow_break_max=30,
    user_max_follow=1000,
    # session_file=False, # Set to False to disable persistent session, or specify custom session_file (ie ='myusername.session')
    user_min_follow=0,
    log_mod=0,
    proxy="",
    # List of list of words, each of which will be used to generate comment
    # For example: "This shot feels wow!"
    comment_list=[],
    # Use unwanted_username_list to block usernames containing a string
    # Will do partial matches; i.e. 'mozart' will block 'legend_mozart'
    # 'free_followers' will be blocked because it contains 'free'
    unwanted_username_list=[],
    unfollow_whitelist=[],
    # Enable the following to schedule the bot. Uses 24H
    end_at_h = 13, # Hour you want the bot to stop
    end_at_m = 30, # Minute you want the bot stop, in this example 23:30
    start_at_h = 3, # Hour you want the bot to start
    start_at_m = 30, # Minute you want the bot to start, in this example 9:10 (am).
)

bot.mainloop()