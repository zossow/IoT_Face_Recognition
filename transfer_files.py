import logging
import os
import shutil
import datetime
from os import listdir

from config import config


def transfer_files_to_main_directory():
    tmp_directory = [img for img in listdir(config.tmp_picture_folder)]
    main_directory = [main_img for main_img in listdir(config.main_picture_folder)]
    compare = [tmp_files for tmp_files in tmp_directory if tmp_files not in main_directory]
    if compare:
        for image in compare:
            shutil.copy(os.path.join(config.tmp_picture_folder, image), config.main_picture_folder)
        print(datetime.datetime.now().strftime("%H:%M:%S"),
              "Thread-FirebaseObserverApp:")
        print(f" 	{len(compare)} files were copied to main directory. \n {compare}")
    else:
        print(datetime.datetime.now().strftime("%H:%M:%S"),
              "Thread-FirebaseObserverApp:")
        print("No new files copied to main directory")



