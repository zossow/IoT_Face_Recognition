import os
from google.cloud import storage
from config import config
import datetime


class Storage:
    def __init__(self):
        self.client = storage.Client()
        self.config = config



    def get_list_of_files(self):
        new_list = []
        list_of_blobs = self.client.list_blobs(self.config.storageBucket)
        for blob in list_of_blobs:
            new_list.append(blob.name)
        return new_list


    def download_all_img(self):
        bucket = self.client.get_bucket(self.config.storageBucket)
        for file in self.get_list_of_files():
            image = bucket.get_blob(file)
            print(datetime.datetime.now().strftime("%H:%M:%S"),
                  "Thread-FirebaseObserverApp:")
            print(f"Download {file}")
            try:
                image.download_to_filename(os.path.join(self.config.picture_folder, file))
            except FileNotFoundError:
                print(datetime.datetime.now().strftime("%H:%M:%S"),
                      "Thread-FirebaseObserverApp:")
                print(f"Directory not exist. Create {self.config.picture_folder} ...")
                os.makedirs(self.config.picture_folder)
                image.download_to_filename(os.path.join(self.config.picture_folder, file))

    def download_single_img(self, name):
        bucket = self.client.bucket(self.config.storageBucket)
        blob = bucket.blob(name)
        blob.download_to_filename(os.path.join(self.config.tmp_picture_folder, name))
        print(datetime.datetime.now().strftime("%H:%M:%S"),
              "Thread-FirebaseObserverApp:")
        print(f"{name} was successfully downloaded.")



