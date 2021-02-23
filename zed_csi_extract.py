# 20210222
# Jugaad Labs
#
# This code extracts all info of a frame number from .avi, .pkl and .svo files
# This code only works with original filenames from recordings.
# This code outputs the info into one .mat file.
# Call this code as this:
#   python3 zed_csi_extract.py <RECORD_DIR> <OUTPUT_DIR> <FRAME_IDX>
#       or
#   python3 zed_csi_extract.py <RECORD_DIR> <FRAME_IDX> 
#   (when OUTPUT_DIR is empty, the output will save in RECORD_DIR)
# For example:
#   python3 zed_csi_extract.py recordings/ZED_2020-11-30-02-00-08.svo 20
#   (this command will get you all info of frame 20 in both ZED and CSI recordings)

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

    if len(argv) == 2:
        RECORD_DIR = argv[0]
        OUTPUT_DIR = os.path.dirname(RECORD_DIR)
        FRAME_IDX = int(argv[1])
    elif len(argv) == 3:
        RECORD_DIR = argv[0]
        OUTPUT_DIR = argv[1]
        FRAME_IDX = int(argv[2])
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
    # fourcc = cv2.VideoWriter_fourcc(*'XVID')

    filename = filenames[0]
    print('Processing', filename)

    # check the CSI .avi files and .pkl files
    CSI_VIDEO = filename[:-27] + 'CSI' + filename[-24:-4] + '.avi'
    if not os.path.isfile(CSI_VIDEO):
        print('Cannot find CSI .avi file for', filename)
    CSI_PKL = filename[:-27] + 'CSI' + filename[-24:-4] + '.pkl'
    if not os.path.isfile(CSI_PKL):
        print('Cannot find CSI .pkl file for', filename)
    vidcap = cv2.VideoCapture(CSI_VIDEO)
    vidcap.isOpened()

    with open(CSI_PKL, 'rb') as f:
        csi_timestamps = np.array(pkl.load(f))
    num_frame = len(csi_timestamps)
    if FRAME_IDX > num_frame:
        print('Cannot find CSI frame or frame corrupted.')
        quit()
    for ind in range(num_frame):
        ret, img = vidcap.read()
        if ret and ind == FRAME_IDX:
            csi_image = cv2.cvtColor(cv2.resize(img, (480, 640)), cv2.COLOR_BGR2RGB)
            csi_timestamp = csi_timestamps[FRAME_IDX]

    resolution = (1280, 720)
    init_parameters = sl.InitParameters()
    init_parameters.set_from_svo_file(filename)
    zed = sl.Camera()
    err = zed.open(init_parameters)
    runtime = sl.RuntimeParameters()
    svo_image = sl.Mat(resolution[1], resolution[0], sl.MAT_TYPE.U8_C4)
    depth_map = sl.Mat(resolution[1], resolution[0], sl.MAT_TYPE.F32_C1)
    out_timediff = float('inf')
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
            if frame_idx == FRAME_IDX:
                if out_timediff > time_diff:
                    out_depth = depth_map.get_data()
                    out_zed = cv2.cvtColor(svo_image.get_data(), cv2.COLOR_BGR2RGB)
                    out_timediff = time_diff
            if frame_idx > FRAME_IDX:
                if out_zed is None:
                    print('Cannot find ZED frame or frame corrupted.')
                    quit()
                else:
                    break
            
    out_mat = {}
    out_mat['frame_idx' + '_'  + 'extracted'] = FRAME_IDX
    out_mat['depth' + '_'  + 'extracted'] = out_depth
    out_mat['time_diff' + '_'  + 'extracted'] = out_timediff
    out_mat['zed_frame' + '_'  + 'extracted'] = out_zed
    out_mat['csi_frame' + '_'  + 'extracted'] = csi_image
    out_mat['csi_timestamp' + '_'  + 'extracted'] = csi_timestamp
    print('Saving depth .mat file for', filename, str(FRAME_IDX), 'frame')
    sio.savemat(os.path.join(OUTPUT_DIR, filename[-27:-4] + '_'  + 'extracted' + str(FRAME_IDX) + '.mat'), out_mat, do_compression=COMPRESS_MAT_FILE)
    print('Saved', os.path.join(OUTPUT_DIR, filename[-27:-4] + '_' + 'extracted' + str(FRAME_IDX) + '.mat'))

if __name__ == "__main__":
   main(sys.argv[1:])