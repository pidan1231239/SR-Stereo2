import os
import os.path
from utils import myUtils
import random


IMG_EXTENSIONS = [
    '.jpg', '.JPG', '.jpeg', '.JPEG',
    '.png', '.PNG', '.ppm', '.PPM', '.bmp', '.BMP',
]


def is_image_file(filename):
    return any(filename.endswith(extension) for extension in IMG_EXTENSIONS)

def dataloader(filepath):

  left_fold  = 'colored_0/'
  right_fold = 'colored_1/'
  disp_noc   = 'disp_occ/'

  image = [img for img in os.listdir(os.path.join(filepath, left_fold)) if img.find('_10') > -1]
  image.sort()

  train = image[:160]
  val   = image[160:]

  left_train  = [os.path.join(filepath, left_fold, img) for img in train]
  right_train = [os.path.join(filepath, right_fold, img) for img in train]
  disp_train = [os.path.join(filepath, disp_noc, img) for img in train]


  left_val  = [os.path.join(filepath, left_fold, img) for img in val]
  right_val = [os.path.join(filepath, right_fold, img) for img in val]
  disp_val = [os.path.join(filepath, disp_noc, img) for img in val]

  return left_train, right_train, disp_train, None, left_val, right_val, disp_val, None
