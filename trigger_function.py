import os
import re
import subprocess
from os import listdir

from config import config
from gcloud import Storage
from transfer_files import transfer_files_to_main_directory


def parser_logs(output):
    regex = r"File:\s(\D+_\d.j[a-z]?pg)"
    all_img = re.findall(regex, output)
    list_img_witout_duplicates = list(dict.fromkeys(all_img))
    return list_img_witout_duplicates


def check_directory_exist(folder_name):
    if not os.path.exists(folder_name):
        print(f"Create directory {folder_name}")
        os.makedirs(folder_name)


def find_all_adding_img():
    print("Reading logs from Firebase .. ")
    result = subprocess.check_output(["gcloud", "functions", "logs", "read", "--limit", "70"])
    list_firebase_img = parser_logs(result.decode())
    if list_firebase_img:
        print(f"New files uploaded to Firebase: {list_firebase_img} ")
    else:
        print(f"No new files uploaded to Firebase")
    return list_firebase_img


def set_env():
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") is None:
        # path_credential = "/home/wiola/Pobrane/iot-face-recognition-f4f53-firebase-adminsdk-e8ek4-dfb5eb4477.json"
        path_credential = "/root/iot-face-recognition-f4f53-firebase-adminsdk-e8ek4-dfb5eb4477.json"
        print("Set Environment Variable: GOOGLE_APPLICATION_CREDENTIALS")
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
            print("No new files to download")
            return False, None
        else:
            print(f"New files to download: {compare}")
            return True, compare

    def images_to_download(self, new_files):
        for _ in new_files:
            print(f"Start downloading img {_} ...")
            self.storage.download_single_img(_)
        print("All adding images were downloaded")


