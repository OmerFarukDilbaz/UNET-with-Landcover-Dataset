import os
import cv2
import numpy as np
from glob import glob

from matplotlib import pyplot as plt
from patchify import patchify
import tifffile as tiff
from PIL import Image
import tensorflow as tf
import keras
#import segmentation_models as sm
from keras.metrics import MeanIoU
import random

temp_img = cv2.imread("Dataset\images\M-33-7-A-d-2-3.tif")
plt.imshow(temp_img[:,:,0])
temp_mask = cv2.imread("Dataset\masks\M-33-7-A-d-2-3.tif")
labels, count = np.unique(temp_mask[:,:,0],return_counts=True)
print("Labels are: ",labels,"and the counts are:",count)

root_directory = 'Dataset/'
patch_size = 256

img_dir = root_directory + "images/"
for path, subdirs, files in os.walk(img_dir):
    dirname = path.split(os.path.sep)[-1]
    images = os.listdir(path)

    for i, image_name in enumerate(images):
        if image_name.endswith(".tif"):
            image = cv2.imread(path + "/" + image_name, 1)
            SIZE_X = (image.shape[1]//patch_size)*patch_size
            SIZE_Y = (image.shape[0]//patch_size)*patch_size
            image = Image.fromarray(image)
            image = image.crop((0,0,SIZE_X,SIZE_Y))
            image = np.array(image)

            print("Now patchifying image:", path+"/"+image_name)
            patches_img = patchify(image, (256, 256, 3), step=256) 
    
            for i in range(patches_img.shape[0]):
                for j in range(patches_img.shape[1]):
                    
                    single_patch_img = patches_img[i,j,:,:]

                    single_patch_img = single_patch_img[0]                           
                    
                    cv2.imwrite(root_directory+"256_patches/images/"+
                               image_name+"patch_"+str(i)+str(j)+".tif", single_patch_img)

mask_dir=root_directory+"masks/"
for path, subdirs, files in os.walk(mask_dir):
    dirname = path.split(os.path.sep)[-1] 
    masks = os.listdir(path)  
    for i, mask_name in enumerate(masks):  
        if mask_name.endswith(".tif"):           
            mask = cv2.imread(path+"/"+mask_name, 0)  
            SIZE_X = (mask.shape[1]//patch_size)*patch_size 
            SIZE_Y = (mask.shape[0]//patch_size)*patch_size 
            mask = Image.fromarray(mask)
            mask = mask.crop((0 ,0, SIZE_X, SIZE_Y))
            mask = np.array(mask)             

            print("Now patchifying mask:", path+"/"+mask_name)
            patches_mask = patchify(mask, (256, 256), step=256)  #Step=256 for 256 patches means no overlap
    
            for i in range(patches_mask.shape[0]):
                for j in range(patches_mask.shape[1]):      
                    single_patch_mask = patches_mask[i,j,:,:]                         
                    cv2.imwrite(root_directory+"256_patches/masks/"+
                               mask_name+"patch_"+str(i)+str(j)+".tif", single_patch_mask)


train_img_dir = "Dataset/256_patches/images/"
train_mask_dir = "Dataset/256_patches/masks/"

img_list = os.listdir(train_img_dir)
msk_list = os.listdir(train_mask_dir)

num_images = len(os.listdir(train_img_dir))


img_num = random.randint(0, num_images-1)

img_for_plot = cv2.imread(train_img_dir+img_list[img_num], 1)
img_for_plot = cv2.cvtColor(img_for_plot, cv2.COLOR_BGR2RGB)

mask_for_plot =cv2.imread(train_mask_dir+msk_list[img_num], 0)

plt.figure(figsize=(12, 8))
plt.subplot(121)
plt.imshow(img_for_plot)
plt.title('Image')
plt.subplot(122)
plt.imshow(mask_for_plot, cmap='gray')
plt.title('Mask')
plt.show()


########################################################################################################################################

useless=0  
for img in range(len(img_list)):  
    img_name=img_list[img]
    mask_name = msk_list[img]
    print("Now preparing image and masks number: ", img)
      
    temp_image=cv2.imread(train_img_dir+img_list[img], 1)
   
    temp_mask=cv2.imread(train_mask_dir+msk_list[img], 0)

    val, counts = np.unique(temp_mask, return_counts=True)
    
    if (1 - (counts[0]/counts.sum())) > 0.05:  #At least 5% useful area with labels that are not 0
        print("Save Me")
        cv2.imwrite('Dataset/256_patches/images_with_useful_info/images/'+img_name, temp_image)
        cv2.imwrite('Dataset/256_patches/images_with_useful_info/masks/'+mask_name, temp_mask)
        
    else:
        print("I am useless")   
        useless +=1

print("Total useful images are: ", len(img_list)-useless)  #20,075
print("Total useless images are: ", useless) #21,571
###############################################################

import splitfolders

input_folder = 'Dataset/256_patches/images_with_useful_info/'
output_folder = 'Dataset/data_for_training_and_testing/'

splitfolders.ratio(input_folder, output=output_folder, seed=42, ratio=(.75, .25), group_prefix=None)
