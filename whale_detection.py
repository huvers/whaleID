__author__ = 'Sean Huver'

import sys
import os
import selectivesearch
from PIL import Image
import numpy as np
import multiprocessing as mp
from multiprocessing import Pool,  Process
from functools import partial
import threading
import Queue

crop_dir = 'whale_crop/'  # folder where new cropped images will go


def make_cropped_img(img, rectangle, file_name, dest_directory):
    # routine that takes rect found by selective search and makes cropped img from it

    # determine where to crop img
    crop_pts = (rectangle[0], rectangle[1], rectangle[2]+rectangle[0], rectangle[3] + rectangle[1])
    print "Found a whale! (Hopefully...)"
    if not os.path.isdir(dest_directory):  # if destination dir doesn't exist, make it
        os.makedirs(dest_directory)
    img.crop(crop_pts).save(dest_directory + '/' + file_name.strip('.jpg') + '.png', "PNG")
    print "Saving cropped image as %s" % dest_directory + file_name


def get_search(file_name, main_dir, sub_dir):

    dir_path = main_dir + sub_dir

    file_path = dir_path + '/' + file_name
    open_img = Image.open('%s' % file_path)
    img = np.array(open_img)

    cropped_dir = crop_dir + sub_dir + '_crp'

    # if file has already been processed, skip to next
    if os.path.isfile(cropped_dir + '/' + file_name.strip('.jpg') + '.png'):
        print "%s already processed, moving to next one..." % (sub_dir + '/' + file_name)
        return

    print "Searching for a whale in %s" % file_path
    # perform selective search
    img_lbl, regions = selectivesearch.selective_search(
        img, scale=500, sigma=0.9, min_size=10)

    print "Regions found: ", len(regions)
    print "Selective search done. Now finding largest area of interest."
    candidates = set()
    rect_size = 0
    # finds largest rectangle of interest - presumed to be whale

    if len(regions) > 1:
        for r in regions:
            if r['rect'] in candidates:
                continue
        # excluding regions smaller than 40k px, or larger than 400k px
            if r['size'] < rect_size or r['size'] < 40000 or r['size'] > 400000:
                continue
        # distorted rects
            x, y, w, h = r['rect']
            if w / h > 1.4 or h / w > 1.4:
                continue
            rect_size = r['size']
            img_rect = r['rect']

    if rect_size > 0:
        print "Largest Size: ", rect_size
        print "Rectangle = ", img_rect
        make_cropped_img(open_img, img_rect, file_name, cropped_dir)
    else:
        # try again under less stringent conditions
        for r in regions:
            if r['rect'] in candidates:
                continue
        # excluding regions smaller than 20000 pixels
            if r['size'] < rect_size or r['size'] < 20000 or r['size'] > 600000:
                continue
        # distorted rects
            x, y, w, h = r['rect']
            if w / h > 2.2 or h / w > 2.2:
                continue
            rect_size = r['size']
            img_rect = r['rect']

        if rect_size > 0:
            print "Largest Size: ", rect_size
            print "Rectangle = ", img_rect
            print "Second pass successful..."
            make_cropped_img(open_img, img_rect, file_name, cropped_dir)
        else:
            print "No potential whales found..."


def main():

    if len(sys.argv) != 2:
        print "No folder given for whale detection."
        print "Usage: whale_detection.py [folder]"
        print "All files in subfolders will by cycled through."
        sys.exit()

    TARGET_DIR = sys.argv[1]
    for sub_dir in os.walk(TARGET_DIR).next()[1]:
        for image in os.listdir(TARGET_DIR + sub_dir):
            get_search(image, TARGET_DIR, sub_dir)

'''
    # Can't get multi-core to work properly
    pool = Pool(6)

    for sub_dir in os.walk(TARGET_DIR).next()[1]:
        for image in os.listdir(TARGET_DIR + sub_dir):
            result = pool.map(get_search, (image, TARGET_DIR, sub_dir , ))
            result.get()
'''
'''
    jobs = []
    # provide directory with images to be cropped
    for sub_dir in os.walk(TARGET_DIR).next()[1]:
        for image in os.listdir(TARGET_DIR + sub_dir):
            p = multiprocessing.Process(target=get_search, args=(image, TARGET_DIR, sub_dir))
            jobs.append(p)
            p.start()
'''
'''
# multi-threading technique - only runs on one processor
q = Queue.Queue()

    for sub_dir in os.walk(TARGET_DIR).next()[1]:
        for image in os.listdir(TARGET_DIR + sub_dir):
            t = threading.Thread(target= get_search, args=(image, TARGET_DIR, sub_dir))
            t.daemon = True
            t.start()

    q.get()
'''
if __name__ == "__main__":
    main()

'''
increasing brightness appears to help determine whale location
increase brightness - find area to crop - then crop from original img?
'''