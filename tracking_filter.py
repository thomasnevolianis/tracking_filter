
# Use: Tracking algorithm to filter the undesirable data and
#      take into consideration only the necessary ones

# Author: Thomas Nevolianis

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import moviepy.editor as mpy
import gizeh as gz
import argparse

# Argparse
parser = argparse.ArgumentParser(
    description='This script is a tracking algorithm to filter the undesirable data and take into consideration only the necessary ones.')
parser.add_argument('txt_file', type=str,
                    help='path of the txt file in x, y, width, height')
parser.add_argument('original_video', type=str,
                    help='path of the original video file')
parser.add_argument('ID', type=int,
                    help='provide an ID')
parser.add_argument('--relax_factor', type=float, default=0.1,
                    help='provide a relaxation factor')


args = parser.parse_args()


# Input file as result from tensorflow with columns x, y, width, height
path = args.txt_file
data = np.genfromtxt(path, skip_header=0)

# Find the x center and y center (raw from tensorflow is upper left x and y coordinates)
xs = data[:, 1]
ys = data[:, 2]
width = data[:, 3]
height = data[:, 4]

x_center = []
y_center = []
for l in range(len(xs)):
    x_center = xs + width/2
    y_center = ys + height/2

# relaxation factor: searching range
relaxation = args.relax_factor

# Number of frames
maxFrame = data[len(data[:, 0])-1, 0] - 2

positionX = []
positionY = []
for i in range(2):
    positionX.append(x_center[i])
    positionY.append(y_center[i])


frames = data[:, 0]


def get_pointPosition(ID):
    pointX = []  # holds the correct X points
    pointY = []  # holds the correct Y points
    frame = 1
    i = args.ID  # should be equal to the number of IDs
    while(frame <= maxFrame):
        frame = frame + 1
        dataX = []  # holds all the X points
        dataY = []  # holds all the Y points
        j = 0
        while(data[i + j, 0] == frame):
            dataX.append(x_center[i+j])
            dataY.append(y_center[i+j])
            j = j + 1
        i = i + j
        distance = 1000000
        index = -1
        for k in range(len(dataX)):  # calculate the distance
            if(np.sqrt((positionX[ID] - dataX[k])**2 + (positionY[ID]-dataY[k])**2) < distance):
                distance = np.sqrt(
                    (positionX[ID] - dataX[k])**2 + (positionY[ID]-dataY[k])**2)
                index = k
        pointX.append(dataX[index])
        pointY.append(dataY[index])
        positionX[ID] = (1 - relaxation) * positionX[ID] + \
            relaxation * dataX[index]  # update position
        positionY[ID] = (1 - relaxation) * positionY[ID] + \
            relaxation * dataY[index]
    return pointX, pointY


# Calculate the points from the two desirable IDs
point1X, point1Y = get_pointPosition(0)
point2X, point2Y = get_pointPosition(1)


# Calculate distance between these two IDs and write the results on a txt file
distance = []
time = []
with open('output.txt','w') as myfile:
    for n in range(len(point1X)):
        distance.append(np.sqrt((point2X[n] - point1X[n]) ** 2 + (point2Y[n] - point1Y[n]) ** 2)*0.12951)
        time.append(n*0.0333)
        myfile.write(str(time[n]))
        myfile.write(",")
        myfile.write(str(distance[n]))
        myfile.write("\n")
    myfile.close()


# plot the end-to-end distance versus time
plt.plot(time, distance, 'r')
plt.ylabel("End-to-end distance (um)")
plt.xlabel("Time (s)")
plt.title("Microgel end-to-end distance calculation")
plt.show()


# colours
BLUE = (1, 1, 1)
LOL = (0.2, 0.3, 0.2)


# render the original video with the desired points

original_clip = mpy.VideoFileClip(args.original_video)


def render_text(t):
    surface = gz.Surface(width=640, height=480)
    text = gz.circle(r=4, fill=BLUE, xy=(point1X[int(len(
        point1X)*t/original_clip.duration)], point1Y[int(len(point1Y)*t/original_clip.duration)]))
    text.draw(surface)

    text = gz.circle(r=4, fill=LOL, xy=(point2X[int(len(
        point2X)*t/original_clip.duration)], point2Y[int(len(point2Y)*t/original_clip.duration)]))
    text.draw(surface)

    return surface.get_npimage(transparent=True)


graphics_clip_mask = mpy.VideoClip(lambda t: render_text(t)[:, :, 1],
                                   duration=original_clip.duration, ismask=True)
graphics_clip = mpy.VideoClip(lambda t: render_text(t)[:, :, :1],
                              duration=original_clip.duration).set_mask(graphics_clip_mask)
final_clip = mpy.CompositeVideoClip(
    [original_clip,
     graphics_clip],
    size=(640, 480)
)
final_clip.write_videofile("output_video.mp4", fps=30)
