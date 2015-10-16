__author__ = 'Sean Huver'

import os
import sys
import csv

# train.csv should be in same directory as python file. User points to img directory.

def main():

    if len(sys.argv) < 2:
        print "No folder given to create image list."
        print "Usage: python list_images.py [directory]"
        sys.exit()

    target_dir = sys.argv[1]

    with open('train.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        tempID = 'temp'
        for row in reader:
            print row['whaleID']
            mypath = target_dir + '/' + row['whaleID']
            if not os.path.isdir(mypath):
                if tempID != row['whaleID']:  # if new whaleID - Make whaleID folder
                    if not os.path.isdir(mypath):  # if dir doesn't exist, make it
                        os.makedirs(mypath)
                    print row['Image'], mypath + '/' + row['Image']
                    os.rename(target_dir + '/' + row['Image'], mypath + '/' + row['Image'])
                    tempID = row['whaleID']
            else:  # else move image to folder that exists
                if os.path.isfile(target_dir + '/' + row['Image']):  # if image exists, move it
                    os.rename(target_dir + '/' + row['Image'], mypath + '/' + row['Image'])

if __name__ == "__main__":
    main()
