import os
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from skimage import io, exposure, img_as_uint, img_as_float
from scipy.spatial.distance import euclidean

data_path = '/home/dandi/Works/data/TuSimple/2016-06-21_1246'

def convert2img(flow_path, img_type):
    with np.load(flow_path) as flow_data:
        flow = flow_data['data']
        height, width, channel = flow.shape
        if img_type == '2_uint8_PNG' or img_type == 'uint16_PNG' or img_type == 'uint8_JPG':
            flow = (flow - np.amin(flow)) / (np.amax(flow) - np.amin(flow))
            mat = np.array(np.zeros((height, width, 3), dtype=np.float32))
            mat[:, :, :2] = flow
            ori_img = exposure.rescale_intensity(mat, out_range=np.float32)
            img = img_as_uint(ori_img)

            if img_type == '2_uint8_PNG':
                img_path = '.'.join(flow_path.split('/')[-1].split('.')[:-1])
                img_path = os.path.join(data_path, 'img', 'png_splitter', img_path)
                high = cv2.convertScaleAbs(img >> 8)
                low = cv2.convertScaleAbs(img - high * 256)
                # plt.imsave(img_path + '_high.png', high)
                # plt.imsave(img_path + '_low.png', low)
            elif img_type == 'uint16_PNG':
                io.use_plugin('freeimage')
                img_path = '.'.join(flow_path.split('/')[-1].split('.')[:-1]) + '.png'
                img_path = os.path.join(data_path, 'img', 'png', img_path)
                io.imsave(img_path, img)
            elif img_type == 'uint8_JPG':
                img_path = '.'.join(flow_path.split('/')[-1].split('.')[:-1]) + '.jpg'
                img_path = os.path.join(data_path, 'img', 'jpg', img_path)
                # plt.imsave(img_path, img)

            return flow, img_path

        elif img_type == 'float32_TIFF':
            img1 = Image.fromarray(flow[:, :, 0], 'F')
            img2 = Image.fromarray(flow[:, :, 1], 'F')
            img_path = '.'.join(flow_path.split('/')[-1].split('.')[:-1])
            img_path = os.path.join(data_path, 'img', 'tiff', img_path)
            # img1.save(img_path + '_1.tiff')
            # img2.save(img_path + '_2.tiff')
            return flow, img_path

        else:
            raise ValueError('Wrong image type provided!')

def evaluation(flow, img_path, img_type, width=1024, height=768):
    if  img_type == '2_uint8_PNG' or img_type == 'uint16_PNG':
        if img_type == '2_uint8_PNG':
            high = plt.imread(img_path + '_high.png')
            low = plt.imread(img_path + '_low.png')
            img = high[:, :, :3] * 256 + low[:, :, :3]
            img[:, :, :2] = (img[:, :, :2] - np.amin(img[:, :, :2])) / float((np.amax(img[:, :, :2]) - np.amin(img[:, :, :2])))
        else:
            img = img_as_float(io.imread(img_path))
        dis = euclidean(flow.ravel(), img[:, :, :2].ravel())
        return dis, dis/flow.size

    elif img_type == 'uint8_JPG':
        img = plt.imread(img_path)
        img = (img - np.amin(img)) / float((np.amax(img) - np.amin(img)))
        mat = np.array(np.zeros((height, width, 3), dtype=np.float32))
        mat[:, :, :2] = flow
        dis = euclidean(mat.ravel(), img.ravel())
        return dis, dis/mat.size

    elif img_type == 'float32_TIFF':
        img1 = Image.open(img_path + '_1.tiff').getdata()
        img2 = Image.open(img_path + '_2.tiff').getdata()
        dis = euclidean(flow[:, :, 0].ravel(), np.array(img1, np.float32).ravel()) + \
              euclidean(flow[:, :, 1].ravel(), np.array(img2, np.float32).ravel())
        return dis, dis/flow.size

    else:
        raise ValueError('Wrong image type provided!')


