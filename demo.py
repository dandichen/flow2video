import os
import fnmatch
import numpy as np
import subprocess as sp
import matplotlib.pyplot as plt

data_path = '/mnt/scratch/data/flow_data/car_record/demo/20160621-2/binocular_camera/2016-06-21_124511'
bench_path = '/mnt/scratch/dandichen/compressedBenchmark/globalRange/20160621-2'


def flow2img(flow_path, img_path, flow_max=512, flow_min=-512, height = 768, width = 1024):
    with np.load(flow_path) as flow_data:
        flow = flow_data['data']
        flow = np.clip(flow, flow_min, flow_max)
        flow = (flow - np.amin(flow)) / (np.amax(flow) - np.amin(flow))
        mat = np.array(np.zeros((height, width, 3), dtype=np.uint8))
        mat[:, :, :2] = flow * 255
        plt.imsave(img_path, mat)

def img2video(video_path, fps=15):
    d = dict(os.environ)
    d['PATH'] = '/mnt/scratch/third-party-packages/libffmpeg/bin:$PATH'
    d['LD_LIBRARY_PATH'] = '/mnt/scratch/third-party-packages/libffmpeg/lib/'

    cmd = "ffmpeg -framerate " + str(fps) + " -pattern_type glob -i '*.png' -c:v libx264 -pix_fmt yuv420p " + os.path.join(video_path, 'uint8_PNG.mp4')
    print 'excuting: ' + cmd
    pipe = sp.Popen(cmd, shell=True, stdout=sp.PIPE, env=d)
    pipe.wait()

def main():
    for dir_name, _, file_list in os.walk(data_path):
        date = dir_name.split('/')[-1]
        if date in ['2016-06-21_1246', '2016-06-21_1247', '2016-06-21_1248', '2016-06-21_1249']:
            for name in sorted(file_list):
                if fnmatch.fnmatch(name, '*.npz'):
                    print date, name
                    flow2img(os.path.join(dir_name, name),  os.path.join(bench_path, date, 'img/uint8png', '.'.join(name.split('.')[:-1]) + '.png'))

    # img2video(os.path.join(bench_path, '2016-06-21_1249', 'video'))
    img2video('./')
if __name__ == '__main__':
    main()







