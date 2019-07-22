#!/usr/bin/env python
#RMS 2019

#Download posts as part of a cron job

import datadownloaders as dd
from config import config
import time

def main() -> None:

    '''Remove old posts and download the new ones'''

    remove_pipe = dd.RemoveOldPosts()

    download_pipe = dd.DownloadNewPosts()

    remove_pipe.removeoldposts()

    print('Starting download')

    download_pipe.download()

    print('Download complete')


if __name__ == "__main__":

    '''Run the download script and then wait'''

    while True:

        main()

        time.sleep(config.DL_FREQ*3600)


