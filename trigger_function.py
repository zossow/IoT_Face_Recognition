import logging
import os
import re
import subprocess
from os import listdir

from config import config
from gcloud import Storage


logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m-%d-%Y %I:%M:%S')

def parser_logs(output):
    regex = r"File:\s([a-zA-Z]*_\d+.j[a-z]?pg)"
    all_img = re.findall(regex, output, flags=re.IGNORECASE)
    list_img_witout_duplicates = list(dict.fromkeys(all_img))
    return list_img_witout_duplicates


def check_directory_exist(folder_name):
    if not os.path.exists(folder_name):
        logging.warning(f"Create directory {folder_name}")
        os.makedirs(folder_name)


def find_all_adding_img():
    logging.warning("Reading logs from Firebase ...")
    result = subprocess.check_output(["gcloud", "functions", "logs", "read", "--limit", "60"])
    # logging.warning(result.decode())
    list_firebase_img = parser_logs(result.decode())
    if list_firebase_img:
        logging.warning(f"New files uploaded to Firebase: {list_firebase_img} ")
    else:
        logging.warning(f"No new files uploaded to Firebase")
    return list_firebase_img


def set_env():
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") is None:
        # path_credential = "/home/wiola/Pobrane/iot-face-recognition-f4f53-firebase-adminsdk-e8ek4-dfb5eb4477.json"
        path_credential = "/root/iot-face-recognition-f4f53-firebase-adminsdk-e8ek4-dfb5eb4477.json"
        os.environ[
            "GOOGLE_APPLICATION_CREDENTIALS"] = path_credential


class TriggerFunction:
    def __init__(self):
        self.config = config
        self.storage = Storage()

    def local_list_of_img(self):
        list_local_img = [img for img in listdir(self.config.tmp_picture_folder)]
        return list_local_img

    def check_if_new_file(self):
        check_directory_exist(self.config.tmp_picture_folder)
        list_storage_img = find_all_adding_img()
        compare = [serv_files for serv_files in list_storage_img if serv_files not in self.local_list_of_img()]
        if not compare:
            logging.warning("Files exist in temporary directory")
            return False, None
        else:
            logging.warning(f"New files downloading to temporary directory: {compare}")
            return True, compare

    def images_to_download(self, new_files):
        for _ in new_files:
            logging.warning(f"Start downloading imgage {_} ...")
            self.storage.download_single_img(_)
        logging.warning("All adding images were downloaded")

