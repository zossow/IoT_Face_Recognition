import os
import cv2
import random
import numpy as np
from skimage.util import img_as_ubyte, random_noise
from skimage.transform import rotate
from skimage.io import imsave
from  tqdm import tqdm
        
def horizontal_flip(img):
    return np.fliplr(img)

def vertical_flip(img):
    return np.flipud(img)

def add_random_noise(img):
    return random_noise(img)

def random_rotate(img):
    random_degree = random.uniform(-25, 25)
    return rotate(img, random_degree)

transformations = {'horizontal flip': horizontal_flip,
                    'vertical flip': vertical_flip,
                    'random noise': add_random_noise,
                    'random rotate': random_rotate
                    }
    
def collect_path_to_images(folder_with_images):
    filepaths = []
    for root, dirs, files in os.walk(folder_with_images):
        for name in files:
            if name.endswith('.jpg'):
                path_to_image = os.path.join(root,name)
                filepaths.append(path_to_image)
    return filepaths
    
def create_new_images(path_to_image, transformations):
    img = cv2.imread(path_to_image)
    for i,transformation_key in enumerate(transformations):
        transformed_img = transformations[transformation_key](img)
        transformed_img = img_as_ubyte(transformed_img)
        transformed_img = cv2.cvtColor(transformed_img, cv2.COLOR_BGR2RGB)
        imsave(path_to_image[:-4] + str(i) + '.jpg',transformed_img)
        
def image_data_augmentation(folder_with_images, transformations):
    filepaths = collect_path_to_images(folder_with_images)
    filepaths = sorted(filepaths)
    for filepath in tqdm(filepaths):
        create_new_images(filepath, transformations)

if __name__ == "__main__":
    image_data_augmentation(folder_with_images='tmp/Pictures', transformations=transformations)