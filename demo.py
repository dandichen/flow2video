import os
import fnmatch
import linecache
import numpy as np
import matplotlib.pyplot as plt

data_path = '/mnt/scratch/data/flow_data/car_record/demo/20160621-2/binocular_camera/2016-06-21_124511'
range_path = '/mnt/scratch/jiabin/spark_test'

def main():
    # f = open('range.txt', 'wa')
    # for dir_name, _, file_list in sorted(os.walk(data_path)):
    #     for name in sorted(file_list):
    #         if fnmatch.fnmatch(name, '*.npz'):
    #             with np.load(os.path.join(dir_name, name)) as flow_data:
    #                 flow = flow_data['data']
    #                 print '/'.join([dir_name.split('/')[-1], name]), np.amax(flow), np.amin(flow)
    #                 f.write("%s %s %s\n" % ('/'.join([dir_name.split('/')[-1], name]), np.amax(flow), np.amin(flow)))
    # f.close()

    # max_list, min_list = [], []
    # f = open('range.txt', 'r')
    # for line in iter(f):
    #     max_list.append(float(line.split(' ')[1]))
    #     min_list.append(float(line.split(' ')[-1][:-1]))
    # print np.amax(max_list), np.amin(max_list), np.amax(min_list), np.amin(min_list)        # 422.238 0.831202 -0.538027 -590.261
    # plt.plot(np.arange(len(max_list)), max_list, 'r', label='max value')
    # plt.plot(np.arange(len(min_list)), min_list, 'b', label='min value')
    # plt.legend()
    # plt.waitforbuttonpress()

    max_value, min_value = [], []
    for dir_name, _, file_list in sorted(os.walk(range_path)):
        for name in sorted(file_list):
            if fnmatch.fnmatch(name, '*.txt'):
                f = open(os.path.join(dir_name, name))
                line = f.readlines()[-1]
                # print name, line
                max_value.append(float(line.split(' ')[-1][:-1]))
                min_value.append(float(line.split(' ')[1]))
    max_value = np.clip(max_value, 0, 512)
    min_value = np.clip(min_value, -512, 0)
    print np.amax(max_value), np.amin(max_value), np.amax(min_value), np.amin(min_value)
    plt.plot(np.arange(len(max_value)), max_value, 'r', label='max value')
    plt.plot(np.arange(len(min_value)), min_value, 'b', label='min value')
    plt.legend()
    plt.waitforbuttonpress()


if __name__ == '__main__':
    main()