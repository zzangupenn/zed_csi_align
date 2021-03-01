# 20210226
# Jugaad Labs
#
# This is a simple python code that converts .svo files to .avi files.
# Note that this is only for visualization purpose. The .avi depth video only 8 bit and not to scale.
# 
# Call this code as this:
#   python3 svo2avi.py <RECORD_DIR> <OUTPUT_DIR>
#       or
#   python3 svo2avi.py <RECORD_DIR>
#   (when OUTPUT_DIR is empty, the output will save in RECORD_DIR)
# For example:
#   python3 svo2avi.py recordings/
#   (this command will process all files in recordings/)
# Please config RECORD_DIR to the target .svo file or a directory containing .svo files.
# It's better to process file individually.

import sys
import os
import numpy as np
import glob
import cv2
import pickle as pkl
import pyzed.sl as sl
import bisect
from tqdm import tqdm

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
        OUTPUT_DIR = RECORD_DIR
    elif os.path.isfile(RECORD_DIR):  
        filenames = [RECORD_DIR]
        OUTPUT_DIR = os.path.dirname(RECORD_DIR)
    else:  
        print("Cannot read the directory or file." )
        quit()
    if len(filenames) == 0:
        print("Cannot read the directory or file." )
        quit()
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    # convert to .avi files
    framerate = 20
    resolution = (1280, 720)
    for filename in filenames:
        print(filename)
        color_out_filename = os.path.join(OUTPUT_DIR, filename[-27:-4] + '_color.avi')
        colorVideoOut = cv2.VideoWriter(color_out_filename, fourcc, framerate, resolution)
        depth_out_filename = os.path.join(OUTPUT_DIR, filename[-27:-4] + '_depth.avi')
        depthVideoOut = cv2.VideoWriter(depth_out_filename, fourcc, framerate, resolution)

        init_parameters = sl.InitParameters()
        init_parameters.set_from_svo_file(filename)

        zed = sl.Camera()
        err = zed.open(init_parameters)
        runtime = sl.RuntimeParameters()
        svo_image = sl.Mat(resolution[1], resolution[0], sl.MAT_TYPE.U8_C4)
        depth_map = sl.Mat(resolution[1], resolution[0], sl.MAT_TYPE.U8_C4)
        i = 0
        for i in tqdm(range(zed.get_svo_number_of_frames())):
            if zed.grab(runtime) == sl.ERROR_CODE.SUCCESS:
                i+=1
                zed.retrieve_image(svo_image, sl.VIEW.LEFT, sl.MEM.CPU)
                zed.retrieve_image(depth_map, sl.VIEW.DEPTH, sl.MEM.CPU)
                colorNumpy = svo_image.get_data()
                colorNumpy = cv2.resize(colorNumpy, resolution, cv2.INTER_AREA)
                colorNumpy = cv2.cvtColor(colorNumpy, cv2.COLOR_RGBA2RGB)
                colorVideoOut.write(colorNumpy)

                depthNumpy = depth_map.get_data()
                depthNumpy = cv2.resize(depthNumpy, resolution, cv2.INTER_AREA)
                depthNumpy = cv2.cvtColor(depthNumpy, cv2.COLOR_BGR2RGB)
                depthVideoOut.write(depthNumpy)
                t = zed.get_timestamp(sl.TIME_REFERENCE.IMAGE).get_nanoseconds()/1e9
            else:
                break
        depthVideoOut.release()
        colorVideoOut.release()
    print("Videos saved")

if __name__ == "__main__":
   main(sys.argv[1:])