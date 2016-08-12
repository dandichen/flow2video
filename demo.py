import cv2
import os
import base64
import fnmatch
import numpy as np
import matplotlib.pyplot as plt

global_max = 512
global_min = -512

data_path = '/mnt/scratch/yiwan/images'
flow_path = '/mnt/scratch/yiwan/images/flow'
img_path = '/mnt/scratch/jiabin/flow/tmp1.jpg'

def main():
    with np.load('i00000681_cam1_1466484359.968471.npz') as flow_data:
        flow = flow_data['data']
        height, width, channel = flow.shape

        flow = np.clip(flow, global_min, global_max)
        flow = (flow - np.amin(flow)) / (np.amax(flow) - np.amin(flow))
        mat = np.array(np.zeros((height, width, 3), dtype=np.float32))
        mat[:, :, :2] = flow
        buf = cv2.imencode('.jpg', mat)[1]  # buf.shape(13171, 1)
        binary = buf.tostring()
        recover = np.array([np.fromstring(binary, dtype=np.uint8)]).transpose()   # recover.shape(13171, )
        s = base64.b64encode(binary)




def main1():
    # mat = plt.imread('./result/i00000681_cam1_1466484359.968471.png')
    # print mat.dtype
    print 'done'

    for dir_name, _, file_list in os.walk(data_path):
        for name in sorted(file_list):
            if fnmatch.fnmatch(name, '*.npz'):
                print name
                with np.load(os.path.join(dir_name, name)) as flow_data:
                    flow = flow_data['data']
                    height, width, channel = flow.shape

                    flow = np.clip(flow, global_min, global_max)
                    flow = (flow - np.amin(flow)) / (np.amax(flow) - np.amin(flow))
                    mat = np.array(np.zeros((height, width, 3), dtype=np.float32))
                    mat[:, :, :2] = flow
                    # plt.imsave('./result/' + name[:-4] + '.jpg', mat)
                    # binary = cv2.imencode('.jpg', mat)[1].tostring()
                    # s = base64.b64encode(binary)
                    # print s

                    # data = np.clip(flow, global_min, global_max)
                    # data = ((data - global_min) / (global_max - global_min) * 255).astype(int)
                    # img = np.array(np.zeros((height, width, 3), dtype=np.uint8))
                    # img[:, :, :2] = data
                    # plt.imsave('test1.png', img)




if __name__ == '__main__':
    main()


