import os
import timeit
import fnmatch
import flow2img
import img2video

# img_path = '/mnt/scratch/dandichen/compressedBenchmark/img/png'
video_path = '/mnt/scratch/dandichen/compressedBenchmark/20160621-2/2016-06-21_1249/video/uint8jpg'
data_path = '/mnt/scratch/data/flow_data/car_record/demo/20160621-2/binocular_camera/2016-06-21_124511/2016-06-21_1246'

def main():
    # convert flow to images
    # f = open('distance.txt', 'wa')
    for dir_name, _, file_list in os.walk(data_path):
        for name in sorted(file_list):
            if fnmatch.fnmatch(name, '*.npz'):
                # f.write("%s\n" % name)
                for img_type in ['2_uint8_PNG', 'uint16_PNG', 'uint8_JPG', 'float32_TIFF']:
                    flow, img_path = flow2img.convert2img(os.path.join(dir_name, name), img_type)
                    dis = flow2img.evaluation(flow, img_path, img_type)
                    print name, img_type, dis
    #                 f.write("%s %s\n" % (img_type, dis))
    #         f.write("\n")
    # f.close()

    img_type = 'uint8_JPG'
    video_type = 'MP4'

    # convert images to video
    # img2video.convert2AVI(img_path, video_path, '2_uint8_PNG')
    # img2video.convert2MP4(video_path, img_type)
    # img2video.convert2TiffVideo(img_path, video_path)
    # img2video.evaluation(img_path, video_path, '2_uint8_PNG', 'MP4')
    # img2video.pipe_evaluation(data_path, img_path, video_path, img_type, video_type)

    # img2video.randomAccess(video_path, 10)




if __name__ == '__main__':
    main()