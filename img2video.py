import os
import cv2
import fnmatch
import numpy as np
import subprocess as sp
# import tiffcapture as tc
import matplotlib.pyplot as plt
from skimage import io, exposure, img_as_uint, img_as_float
from scipy.spatial.distance import euclidean


def convert2MP4(video_path, img_type, fps=15):
    d = dict(os.environ)
    d['PATH'] = '/mnt/scratch/third-party-packages/libffmpeg/bin:$PATH'
    d['LD_LIBRARY_PATH'] = '/mnt/scratch/third-party-packages/libffmpeg/lib/'

    if img_type == '2_uint8_PNG' or img_type == 'float32_TIFF':
        if img_type == '2_uint8_PNG':
            path1 = os.path.join(video_path, img_type + '_high.mp4')
            path2 = os.path.join(video_path, img_type + '_low.mp4')
            cmd1 = "ffmpeg -framerate " + str(fps) + " -pattern_type glob -i '*high*.png' " \
                  "-c:v libx264 -pix_fmt yuv420p " + path1
            cmd2 = "ffmpeg -framerate " + str(fps) + " -pattern_type glob -i '*low*.png' " \
                       "-c:v libx264 -pix_fmt yuv420p " + path2
        else:
            path1 = os.path.join(video_path, img_type + '_low.mp4')
            path2 = os.path.join(video_path, img_type + '_2.mp4')
            cmd1 = "ffmpeg -framerate " + str(fps) + " -pattern_type glob -i '*_1*.tiff' " \
                   "-c:v libx264 -pix_fmt yuv420p " + path1
            cmd2 = "ffmpeg -framerate " + str(fps) + " -pattern_type glob -i '*_2*.tiff' " \
                   "-c:v libx264 -pix_fmt yuv420p " + path2

        print 'excuting: ' + cmd1
        pipe = sp.Popen(cmd1, shell=True, stdout=sp.PIPE, env=d)
        pipe.wait()

        print 'excuting: ' + cmd2
        pipe = sp.Popen(cmd2, shell=True, stdout=sp.PIPE, env=d)
        pipe.wait()
        return path1, path2

    elif img_type == 'uint16_PNG' or img_type == 'uint8_JPG':
        if img_type == 'uint16_PNG':
            cmd = "ffmpeg -framerate " + str(fps) + " -pattern_type glob -i '*.png' " \
                  "-c:v libx264 -pix_fmt yuv420p " + os.path.join(video_path, img_type + '.mp4')
        else:
            cmd = "ffmpeg -framerate " + str(fps) + " -pattern_type glob -i '*.jpg' " \
                  "-c:v libx264 -pix_fmt yuv420p " + os.path.join(video_path, img_type + '.mp4')
        print 'excuting: ' + cmd
        pipe = sp.Popen(cmd, shell=True, stdout=sp.PIPE, env=d)
        pipe.wait()
        return os.path.join(video_path, img_type + '.mp4')

def convert2AVI(img_path, video_path, img_type, fps=15, width=1024, height=768):
    if cv2.__version__ >= 3.0:
        codec = cv2.VideoWriter_fourcc(*'XVID')
    else:
        codec = cv2.cv.CV_FOURCC(*'XVID')

    if img_type == '2_uint8_PNG':
        cap_high = cv2.VideoWriter(os.path.join(video_path, img_type + '_high.avi'), codec, fps, (width, height))
        cap_low = cv2.VideoWriter(os.path.join(video_path, img_type + '_low.avi'), codec, fps, (width, height))
        for name in sorted(os.listdir(img_path)):
            if fnmatch.fnmatch(name, '*high*.png'):
                print name
                cap_high.write(cv2.imread(os.path.join(img_path, name)))
            if fnmatch.fnmatch(name, '*low*.png'):
                print name
                cap_low.write(cv2.imread(os.path.join(img_path, name)))
        cap_high.release()
        cap_low.release()
        cv2.destroyAllWindows()
        return os.path.join(video_path, img_type + '_high.avi'), os.path.join(video_path, img_type + '_low.avi')

    elif img_type == 'uint16_PNG' or img_type == 'uint8_JPG':
        cap = cv2.VideoWriter(os.path.join(video_path, img_type + '.avi'), codec, fps, (width, height))
        for name in sorted(os.listdir(img_path)):
            print img_type, name
            cap.write(cv2.imread(os.path.join(img_path, name)))
        cap.release()
        cv2.destroyAllWindows()
        return os.path.join(video_path, img_type + '.avi')

    else:
        raise ValueError('Wrong image type provided!')

# def convert2TiffVideo(img_path, video_path):
#     file_list = sorted(os.listdir(img_path))
#     for idx in range(len(file_list)):
#         if fnmatch.fnmatch(file_list[idx], '*_1*.tiff'):
#             _, img1 = tc.opentiff(os.path.join(img_path, file_list[idx])).retrieve()
#             _, img2 = tc.opentiff(os.path.join(img_path, file_list[idx + 1])).retrieve()
#             cv2.namedWindow('video')
#             tempimg = cv2.absdiff(img1, img2)  # bkgnd sub
#             _, tempimg = cv2.threshold(tempimg, 5, 255, cv2.THRESH_BINARY)  # convert to binary
#             cv2.imshow('video', tempimg)
#             cv2.waitKey(0)
#         if fnmatch.fnmatch(file_list[idx], '*_2*.tiff'):
#             _, img1 = tc.opentiff(os.path.join(img_path, file_list[idx])).retrieve()
#             _, img2 = tc.opentiff(os.path.join(img_path, file_list[idx + 1])).retrieve()
#             cv2.namedWindow('video')
#             tempimg = cv2.absdiff(img1, img2)  # bkgnd sub
#             _, tempimg = cv2.threshold(tempimg, 5, 255, cv2.THRESH_BINARY)  # convert to binary
#             cv2.imshow('video', tempimg)
#             cv2.waitKey(0)
#     cv2.destroyAllWindows()

def randomAccess(video_path, img_type, frame_idx, width=1024, height=768):
    cap = cv2.VideoCapture(video_path)
    video_len = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
    if video_len != 0:
        if frame_idx < video_len:
            retval = cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, frame_idx)
            if (retval):
                _, frame = cap.read()
                if img_type == 'uint16_PNG' or img_type == 'uint8_JPG':
                    tmp = np.zeros((height, width, 2), dtype=np.float32)
                    tmp[:, :, 0] = frame[:, :, 2]
                    tmp[:, :, 1] = frame[:, :, 1]
                    return tmp
        else:
            raise ValueError('Frame idx is out of range!')
    else:
        raise ValueError('Wrong video path!')

def evaluation(img_path, video_path, img_type, video_type, width=1024, height=768):
    # f = open('distance.txt', 'wa')
    if img_type == 'uint16_PNG' or img_type == 'uint8_JPG':
        cap = cv2.VideoCapture(video_path)
        # video_len = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_len = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))

        frame_list = []
        if video_len != 0:
            for _ in range(video_len):
                _, cur_frame = cap.read()
                frame_list.append(cur_frame)

            for dir_name, _, file_list in os.walk(img_path):
                file_list = sorted(file_list)
                for idx in range(len(file_list)):
                    print file_list[idx]
                    # f.write("%s\n" % file_list[idx])
                    if img_type == 'uint16_PNG':
                        tmp = io.imread(os.path.join(dir_name, file_list[idx]))
                    elif img_type == 'uint8_JPG':
                        tmp = plt.imread(os.path.join(dir_name, file_list[idx]))
                    ori_img = np.zeros_like(tmp)
                    ori_img[:, :, 0] = tmp[:, :, 2].copy()
                    ori_img[:, :, 1] = tmp[:, :, 1].copy()
                    ori_img[:, :, 2] = tmp[:, :, 0].copy()
                    ori_img = img_as_float(ori_img)
                    ori_img = (ori_img - np.amin(ori_img)) / float((np.amax(ori_img) - np.amin(ori_img)))
                    frame_list[idx] = (frame_list[idx] - np.amin(frame_list[idx])) / \
                                      float(np.amax(frame_list[idx]) - np.amin(frame_list[idx]))
                    dis = euclidean(frame_list[idx].ravel(), ori_img.ravel())
                    print dis, dis/ori_img.size
                    # f.write("%s %s %s\n" % (img_type, dis, dis/ori_img.size))
                    # f.write("\n")
        return frame_list

    elif img_type == '2_uint8_PNG' or img_type == 'float32_TIFF':
        if video_type == 'AVI':
            if img_type == '2_uint8_PNG':
                path1 = os.path.join(video_path, img_type + '_high.avi')
                path2 = os.path.join(video_path, img_type + '_low.avi')
            else:
                path1 = os.path.join(video_path, img_type + '_1.avi')
                path2 = os.path.join(video_path, img_type + '_2.avi')
        if video_type == 'MP4':
            if img_type == '2_uint8_PNG':
                path1 = os.path.join(video_path, img_type + '_high.mp4')
                path2 = os.path.join(video_path, img_type + '_low.mp4')
            else:
                path1 = os.path.join(video_path, img_type + '_1.mp4')
                path2 = os.path.join(video_path, img_type + '_2.mp4')

        cap1 = cv2.VideoCapture(path1)
        cap2 = cv2.VideoCapture(path2)
        # video_len1 = int(cap1.get(cv2.CAP_PROP_FRAME_COUNT))
        # video_len2 = int(cap2.get(cv2.CAP_PROP_FRAME_COUNT))
        video_len1 = int(cap1.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
        video_len2 = int(cap2.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))

        frame_list1, frame_list2 = [], []
        if video_len1 != 0 and video_len2 != 0:
            for _, _ in zip(range(video_len1), range(video_len2)):
                _, cur_frame1 = cap1.read()
                _, cur_frame2 = cap2.read()
                frame_list1.append(cur_frame1)
                frame_list2.append(cur_frame2)

            for dir_name, _, file_list in os.walk(img_path):
                file_list = sorted(file_list)
                for idx in range(len(file_list)):
                    if img_type == '2_uint8_PNG':
                        if fnmatch.fnmatch(file_list[idx], '*high*.png'):
                            print ''
                            print file_list[idx]
                            # f.write("%s\n" % file_list[idx])
                            tmp = plt.imread(os.path.join(dir_name, file_list[idx]))
                            ori_img1 = np.zeros((height, width, 3), dtype=tmp.dtype)
                            ori_img1[:, :, 0] = tmp[:, :, 2].copy()
                            ori_img1[:, :, 1] = tmp[:, :, 1].copy()
                            ori_img1[:, :, 2] = tmp[:, :, 0].copy()
                            ori_img1 = img_as_float(ori_img1)
                            ori_img1 = (ori_img1 - np.amin(ori_img1)) / float((np.amax(ori_img1) - np.amin(ori_img1)))
                            frame_list1[idx/2] = (frame_list1[idx/2] - np.amin(frame_list1[idx/2])) / \
                                              float(np.amax(frame_list1[idx/2]) - np.amin(frame_list1[idx/2]))
                            dis1 = euclidean(frame_list1[idx/2].ravel(), ori_img1.ravel())
                            print dis1, dis1 / ori_img1.size
                            # f.write("%s %s %s\n" % (img_type, dis1, dis1 / ori_img1.size))
                            # f.write("\n")

                        if fnmatch.fnmatch(file_list[idx], '*low*.png'):
                            print ''
                            print file_list[idx]
                            # f.write("%s\n" % file_list[idx])
                            tmp = plt.imread(os.path.join(dir_name, file_list[idx]))
                            ori_img2 = np.zeros((height, width, 3), dtype=tmp.dtype)
                            ori_img2[:, :, 0] = tmp[:, :, 2].copy()
                            ori_img2[:, :, 1] = tmp[:, :, 1].copy()
                            ori_img2[:, :, 2] = tmp[:, :, 0].copy()
                            ori_img2 = img_as_float(ori_img2)
                            ori_img2 = (ori_img2 - np.amin(ori_img2)) / float((np.amax(ori_img2) - np.amin(ori_img2)))
                            frame_list2[(idx - 1)/2] = (frame_list2[(idx - 1)/2] - np.amin(frame_list2[(idx - 1)/2])) / \
                                               float(np.amax(frame_list2[(idx - 1)/2]) - np.amin(frame_list2[(idx - 1)/2]))
                            dis2 = euclidean(frame_list2[(idx - 1)/2].ravel(), ori_img2.ravel())
                            print dis2, dis2 / ori_img2.size
                            # f.write("%s %s %s\n" % (img_type, dis2, dis2 / ori_img2.size))
                            # f.write("\n")
                    else:
                        if fnmatch.fnmatch(file_list[idx], '*_1*.tiff'):
                            tmp = plt.imread(
                                os.path.join(dir_name, file_list[idx]))
                            ori_img1 = np.zeros((height, width, 3), dtype=tmp.dtype)
                            ori_img1[:, :, 0] = tmp[:, :, 2].copy()
                            ori_img1[:, :, 1] = tmp[:, :, 1].copy()
                            ori_img1[:, :, 2] = tmp[:, :, 0].copy()
                            ori_img1 = img_as_float(ori_img1)
                            ori_img1 = (ori_img1 - np.amin(ori_img1)) / float((np.amax(ori_img1) - np.amin(ori_img1)))
                            frame_list1[idx] = (frame_list1[idx] - np.amin(frame_list1[idx])) / \
                                               float(np.amax(frame_list1[idx]) - np.amin(frame_list1[idx]))
                            dis1 = euclidean(frame_list1[idx].ravel(), ori_img1.ravel())
                            print dis1, dis1 / ori_img1.size

                        if fnmatch.fnmatch(file_list[idx], '*_2*.tiff'):
                            tmp = plt.imread(
                                os.path.join(dir_name, file_list[idx]))
                            ori_img2 = np.zeros((height, width, 3), dtype=tmp.dtype)
                            ori_img2[:, :, 0] = tmp[:, :, 2].copy()
                            ori_img2[:, :, 1] = tmp[:, :, 1].copy()
                            ori_img2[:, :, 2] = tmp[:, :, 0].copy()
                            ori_img2 = img_as_float(ori_img2)
                            ori_img2 = (ori_img2 - np.amin(ori_img2)) / float((np.amax(ori_img2) - np.amin(ori_img2)))
                            frame_list2[idx] = (frame_list2[idx] - np.amin(frame_list1[idx])) / \
                                               float(np.amax(frame_list1[idx]) - np.amin(frame_list1[idx]))
                            dis2 = euclidean(frame_list2[idx].ravel(), ori_img2.ravel())

                            print dis2, dis2 / ori_img2.size
                            # f.write("\n")
                return frame_list1, frame_list2
    else:
        raise ValueError('Wrong video path !')
    # f.close()

def pipe_evaluation(data_path, img_path, video_path, img_type, video_type, width=1024, height=768):
    # f = open('distance.txt', 'wa')
    if img_type == 'uint16_PNG' or img_type == 'uint8_JPG':
        cap = cv2.VideoCapture(video_path)
        # video_len = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_len = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))

        frame_list = []
        flow = []
        if video_len != 0:
            for _ in range(video_len):
                _, cur_frame = cap.read()
                frame_list.append(cur_frame)

            for dir_name, _, file_list in os.walk(data_path):
                file_list = sorted(file_list)
                for name in sorted(file_list):
                    if fnmatch.fnmatch(name, '*.npz'):
                        with np.load(os.path.join(data_path, name)) as flow_data:
                            flow.append(flow_data['data'])

            for idx in range(video_len):
                if idx < video_len:
                    print ''
                    print file_list[idx]
                # f.write("%s\n" % file_list[idx])
                tmp = np.zeros_like(flow[idx])
                tmp[:, :, 0] = frame_list[idx][:, :, 2]
                tmp[:, :, 1] = frame_list[idx][:, :, 1]
                tmp = (tmp - np.amin(tmp)) / (np.amax(tmp) - np.amin(tmp))
                temp = (flow[idx] - np.amin(flow[idx])) / (np.amax(flow[idx]) - np.amin(flow[idx]))
                dis = euclidean(tmp.ravel(), temp.ravel())
                print dis, dis / flow[idx].size
                # f.write("%s %s %s\n" % (img_type, dis, dis / flow[idx].size))
                # f.write("\n")
        return frame_list

    elif img_type == '2_uint8_PNG' or img_type == 'float32_TIFF':
        if video_type == 'AVI':
            if img_type == '2_uint8_PNG':
                path1 = os.path.join(video_path, img_type + '_high.avi')
                path2 = os.path.join(video_path, img_type + '_low.avi')
            else:
                path1 = os.path.join(video_path, img_type + '_1.avi')
                path2 = os.path.join(video_path, img_type + '_2.avi')
        if video_type == 'MP4':
            if img_type == '2_uint8_PNG':
                path1 = os.path.join(video_path, img_type + '_high.mp4')
                path2 = os.path.join(video_path, img_type + '_low.mp4')
            else:
                path1 = os.path.join(video_path, img_type + '_1.mp4')
                path2 = os.path.join(video_path, img_type + '_2.mp4')

        cap1 = cv2.VideoCapture(path1)
        cap2 = cv2.VideoCapture(path2)
        # video_len1 = int(cap1.get(cv2.CAP_PROP_FRAME_COUNT))
        # video_len2 = int(cap2.get(cv2.CAP_PROP_FRAME_COUNT))
        video_len1 = int(cap1.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
        video_len2 = int(cap2.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))

        frame_list1, frame_list2 = [], []
        flow = []
        if video_len1 != 0 and video_len2 != 0:
            for _, _ in zip(range(video_len1), range(video_len2)):
                _, cur_frame1 = cap1.read()
                _, cur_frame2 = cap2.read()
                frame_list1.append(cur_frame1)
                frame_list2.append(cur_frame2)

            for dir_name, _, file_list in os.walk(data_path):
                file_list = sorted(file_list)
                for name in sorted(file_list):
                    if fnmatch.fnmatch(name, '*.npz'):
                        with np.load(os.path.join(data_path, name)) as flow_data:
                            flow.append(flow_data['data'])

            if img_type == '2_uint8_PNG':
                for idx, _ in zip(range(video_len1), range(video_len2)):
                    print ''
                    print file_list[idx][:-9]
                    # f.write("%s\n" % file_list[idx][:-9])
                    t = np.array(frame_list1[idx] * 256 + frame_list2[idx], dtype=np.float32)[:, :, 1:3]
                    tmp = np.zeros_like(t)
                    tmp[:, :, 0] = t[:, :, 1]
                    tmp[:, :, 1] = t[:, :, 0]
                    tmp = (tmp - np.amin(tmp)) / (np.amax(tmp) - np.amin(tmp))
                    temp = (flow[idx] - np.amin(flow[idx])) / (np.amax(flow[idx]) - np.amin(flow[idx]))
                    dis = euclidean(tmp.ravel(), temp.ravel())
                    print dis, dis / flow[idx].size
                    # f.write("%s %s %s\n" % (img_type, dis, dis / flow[idx].size))
                    # f.write("\n")
                return frame_list1, frame_list2
    else:
        raise ValueError('Wrong video path !')
    # f.close()