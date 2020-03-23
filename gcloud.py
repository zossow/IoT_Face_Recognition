import os
from google.cloud import storage
from config import config
import logging


class Storage():
    def __init__(self):
        self.client = storage.Client()
        self.config = config

    def get_list_of_files(self):
        list_of_blobs = self.client.list_blobs(self.config.storageBucket)
        for blob in list_of_blobs:
            yield blob.name

    def download_all_img(self):
        bucket = self.client.get_bucket(self.config.storageBucket)
        for file in self.get_list_of_files():
            image = bucket.get_blob(file)
            print(f"Download {file}")
            try:
                image.download_to_filename(os.path.join(self.config.picture_folder, file))
            except FileNotFoundError:
                print(f"Directory not exist. Create {self.config.picture_folder} ...")
                os.makedirs(self.config.picture_folder)
                image.download_to_filename(os.path.join(self.config.picture_folder, file))

    def download_single_img(self, name):
        bucket = self.client.bucket(self.config.storageBucket)
        blob = bucket.blob(name)
        blob.download_to_filename(os.path.join(self.config.picture_folder, name))
        logging.info(f"{name} was successfully downloaded.")


# if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") is None:
#     path_credential = "/home/wiola/Pobrane/iot-face-recognition-f4f53-firebase-adminsdk-e8ek4-dfb5eb4477.json"
#     print("Set Environment Variable: GOOGLE_APPLICATION_CREDENTIALS")
#     os.environ[
#         "GOOGLE_APPLICATION_CREDENTIALS"] = path_credential
# w = Storage()
# w.download_all_img()
# w.download_single_img('screan_1.jpg')
