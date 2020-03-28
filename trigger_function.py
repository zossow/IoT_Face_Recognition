import logging
import os
import re
import subprocess
from os import listdir

from config import config
from gcloud import Storage

from firebase import firebase


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
        logging.info(f"Local images: \n {list_local_img} \n")
        return list_local_img

    def images_to_download(self):
        check_directory_exist(self.config.picture_folder)
        list_storage_img = find_all_adding_img()
        for _ in list_storage_img:
            if _ in self.local_list_of_img():
                logging.info(f"{_} exist in local base")
            else:
                logging.info(f"{_} no exist. Start downloading img ...")
                self.storage.download_single_img(_)
        logging.info("All adding images were downloaded")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    set_env()
    # trigger.find_all_adding_img()
    trigger = TriggerFunction()

    trigger.images_to_download()
