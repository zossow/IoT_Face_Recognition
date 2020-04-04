import logging
import os
import re
import subprocess
from os import listdir

from config import config
from gcloud import Storage




def parser_logs(output):
    regex = r"File:\s(\D+_\d.j[a-z]?pg)"
    all_img = re.findall(regex, output)
    list_img_witout_duplicates = list(dict.fromkeys(all_img))
    return list_img_witout_duplicates


def check_directory_exist(folder_name):
    if not os.path.exists(folder_name):
        logging.info(f"Create directory {folder_name}")
        os.makedirs(folder_name)


def find_all_adding_img():
    logging.info("Execute command to see storage logs .. ")
    result = subprocess.check_output(["gcloud", "functions", "logs", "read", "--limit", "100"])
    logging.info(result.decode())
    list_firebase_img = parser_logs(result.decode())
    logging.info(f"Storage images: \n {list_firebase_img} \n")
    return list_firebase_img


def set_env():
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") is None:
        #path_credential = "/home/wiola/Pobrane/iot-face-recognition-f4f53-firebase-adminsdk-e8ek4-dfb5eb4477.json"
        path_credential = "/root/iot-face-recognition-f4f53-firebase-adminsdk-e8ek4-dfb5eb4477.json"
        logging.info("Set Environment Variable: GOOGLE_APPLICATION_CREDENTIALS")
        os.environ[
            "GOOGLE_APPLICATION_CREDENTIALS"] = path_credential


class TriggerFunction:
    def __init__(self):
        self.config = config
        self.storage = Storage()

    def local_list_of_img(self):
        list_local_img = [img for img in listdir(self.config.picture_folder)]

        return list_local_img

    def check_if_new_file(self):
        check_directory_exist(self.config.picture_folder)
        list_storage_img = find_all_adding_img()
        compare = [serv_files for serv_files in list_storage_img if serv_files not in self.local_list_of_img()]
        if not compare:
            logging.info("Not new files to download")
            return False, None
        else:
            logging.info(f"New files to download: {compare}")
            return True, compare

    def images_to_download(self, new_files):
        for _ in new_files:
            logging.info(f"Start downloading img {_} ...")
            self.storage.download_single_img(_)
        logging.info("All adding images were downloaded")



