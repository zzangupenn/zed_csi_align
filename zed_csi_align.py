# 20210222
# Jugaad Labs
#
# This code is for aligning the frames in .avi and .svo.
# This code only works with original filenames from recordings.
# This code outputs all frames into .mat file so the file can be very large.
# In the ZED .mat file:
#   depth is the depth info in meters stored in float.
#   time_diff is the time difference in seconds between the ZED frame and the CSI frame.
#   zed_frame is the color frame from the left ZED camera.
# CSI frames are stored in the CSI .mat file.
#
# Call this code as this:
#   python3 zed_csi_align.py <RECORD_DIR> <OUTPUT_DIR>
#       or
#   python3 zed_csi_align.py <RECORD_DIR>
#   (when OUTPUT_DIR is empty, the output will save in RECORD_DIR)
# For example:
#   python3 zed_csi_align.py recordings/
#   (this command will process all files in recordings/)
# Please config RECORD_DIR to the target .svo file or a directory containing .svo files.
# It's better to process file individually.

# compressing the output .mat file takes longer time but reduces the size
COMPRESS_MAT_FILE = True

import numpy as np
import os
import glob
import cv2
import pickle as pkl
import pyzed.sl as sl
import bisect
# from tqdm import tqdm
import scipy.io as sio
import sys

def main(argv):

    if len(argv) == 1:
        RECORD_DIR = argv[0]
        OUTPUT_DIR = os.path.dirname(RECORD_DIR)
    elif len(argv) == 2:
        RECORD_DIR = argv[0]
        OUTPUT_DIR = argv[1]
    else:
        print('unkown argv format')
        quit()

    # check contents of the given directory
    if os.path.isdir(RECORD_DIR):  
        filenames = sorted(glob.glob(os.path.join(RECORD_DIR, '*.svo')))
    elif os.path.isfile(RECORD_DIR):  
        filenames = [RECORD_DIR]
    else:
        print("Cannot read the directory or file." )
        quit()
    if len(filenames) == 0:
        print("Cannot read the directory or file." )
        quit()
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    for filename in filenames:
        print('Processing', filename)

        # check the CSI .avi files and .pkl files
        CSI_VIDEO = filename[:-27] + 'CSI' + filename[-24:-4] + '.avi'
        if not os.path.isfile(CSI_VIDEO):
            print('Cannot find CSI .avi file for', filename)
            continue
        CSI_PKL = filename[:-27] + 'CSI' + filename[-24:-4] + '.pkl'
        if not os.path.isfile(CSI_PKL):
            print('Cannot find CSI .pkl file for', filename)
            continue
        vidcap = cv2.VideoCapture(CSI_VIDEO)
        vidcap.isOpened()
        out_csi = []
        with open(CSI_PKL, 'rb') as f:
            csi_timestamps = np.array(pkl.load(f))
        num_frame = len(csi_timestamps)
        corrupted_frame_num = 0
        for ind in range(num_frame):
            ret, img = vidcap.read()
            if ret:
                out_csi.append(cv2.cvtColor(cv2.resize(img, (480, 640)), cv2.COLOR_BGR2RGB))
            else:
                corrupted_frame_num += 1
        num_frame = num_frame - corrupted_frame_num
        print('loaded', num_frame, 'frames in' , csi_timestamps[num_frame-1] - csi_timestamps[0], 'seconds.')
        vidcap.release()
        out_mat = {}
        out_mat['csi_frame'] = out_csi
        out_mat['csi_timestamps'] = csi_timestamps
        sio.savemat(os.path.join(OUTPUT_DIR, 'CSI' + filename[-24:-4] + '_aligned.mat'), out_mat, do_compression=COMPRESS_MAT_FILE)
        print('Saved', os.path.join(OUTPUT_DIR, 'CSI' + filename[-24:-4] + '_aligned.mat'))

        resolution = (1280, 720)
        init_parameters = sl.InitParameters()
        init_parameters.set_from_svo_file(filename)
        zed = sl.Camera()
        err = zed.open(init_parameters)
        runtime = sl.RuntimeParameters()
        svo_image = sl.Mat(resolution[1], resolution[0], sl.MAT_TYPE.U8_C4)
        depth_map = sl.Mat(resolution[1], resolution[0], sl.MAT_TYPE.F32_C1)
        out_depth = []
        out_timediff = np.ones([num_frame]) * float('inf')
        out_zed = []
        for i in range(zed.get_svo_number_of_frames()):
            if zed.grab() == sl.ERROR_CODE.SUCCESS:
                # grab the zed image and depth map
                zed.retrieve_image(svo_image, sl.VIEW.LEFT)
                zed.retrieve_measure(depth_map, sl.MEASURE.DEPTH, sl.MEM.CPU)
                # svo_position = zed.get_svo_position()
                zed_timestamp = zed.get_timestamp(sl.TIME_REFERENCE.IMAGE).get_nanoseconds()/1e9
                # finds the closest frame, usually correct to a few milliseconds
                frame_idx = bisect.bisect_left(csi_timestamps, zed_timestamp)
                time_diff = csi_timestamps[frame_idx] - zed_timestamp
                if frame_idx < num_frame:
                    if out_timediff[frame_idx] > time_diff:
                        if len(out_depth) == frame_idx + 1:
                            out_depth.pop()
                            out_zed.pop()
                        out_depth.append(depth_map.get_data())
                        out_zed.append(cv2.cvtColor(svo_image.get_data(), cv2.COLOR_BGR2RGB))
                        out_timediff[frame_idx] = time_diff
                
        out_mat = {}
        out_mat['depth'] = out_depth
        out_mat['time_diff'] = out_timediff
        out_mat['zed_frame'] = out_zed
        print('Saving depth .mat file for', filename)
        sio.savemat(os.path.join(OUTPUT_DIR, filename[-27:-4] + '_aligned.mat'), out_mat, do_compression=COMPRESS_MAT_FILE)
        print('Saved', os.path.join(OUTPUT_DIR, filename[-27:-4] + '_aligned.mat'))

if __name__ == "__main__":
   main(sys.argv[1:])