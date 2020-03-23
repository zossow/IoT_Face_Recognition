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


def find_all_adding_img():
    logging.info("Execute command to see storage logs .. ")
    result = subprocess.check_output(["gcloud", "functions", "logs", "read", "--limit", "50"])
    print(result.decode())
    list_firebase_img = parser_logs(result.decode())
    logging.info(f"Storage images: \n {list_firebase_img} \n")
    return list_firebase_img


class TriggerFunction:
    def __init__(self):
        self.config = config
        self.storage = Storage()

    def local_list_of_img(self):
        list_local_img = [img for img in listdir(self.config.picture_folder)]
        logging.info(f"Local images: \n {list_local_img} \n")
        return list_local_img

    def images_to_download(self):
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

    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") is None:
        path_credential = "/home/wiola/Pobrane/iot-face-recognition-f4f53-firebase-adminsdk-e8ek4-dfb5eb4477.json"
        # path_credential = "/root/IoT_Face_Recognition"
        logging.info("Set Environment Variable: GOOGLE_APPLICATION_CREDENTIALS")
        os.environ[
            "GOOGLE_APPLICATION_CREDENTIALS"] = path_credential
    # trigger.find_all_adding_img()
    trigger = TriggerFunction()
    trigger.images_to_download()
