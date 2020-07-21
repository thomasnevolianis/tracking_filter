
# Use: Tracking algorithm to to clear the undesirable data and
#      take into consideration only the necessary ones

# Author: Thomas Nevolianis

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import moviepy.editor as mpy
import gizeh as gz
from moviepy.editor import *
import os

# Input file as result from tensorflow with columns x, y, width, height
path = 'test.txt'
data = np.genfromtxt(path, skip_header = 0)

# Find the x center and y center (raw is upper left x and y)
xs=data[:,1]
ys=data[:,2]
width=data[:,3]
height=data[:,4]

x_center=[]
y_center=[]
for l in range(len(xs)):
    x_center = xs + width/2
    y_center = ys + height/2

# relaxation factor: searching range
relaxation = 0.1

# Number of frames
maxFrame = data[len(data[:,0])-1,0] -2

positionX = []
positionY = []
for i in range(2):
    positionX.append(x_center[i])
    positionY.append(y_center[i])


frames = data[:,0]

def get_pointPosition(ID):
    pointX = [] # holds the correct X points
    pointY = [] # holds the correct Y points
    frame = 1
    i = 3 # should be equal to the length of x
    while(frame <= maxFrame):
        frame = frame + 1
        dataX = [] # holds all the X points
        dataY = [] # holds all the Y points
        j = 0
        while(data[i + j,0] == frame):
            dataX.append(x_center[i+j])
            dataY.append(y_center[i+j])
            j = j + 1
        i = i + j 
        distance = 1000000
        index = -1
        for k in range(len(dataX)): # calculate the distance
            if(np.sqrt((positionX[ID] - dataX[k])**2 + (positionY[ID]-dataY[k])**2) < distance):
                 distance = np.sqrt((positionX[ID] - dataX[k])**2 + (positionY[ID]-dataY[k])**2)
                 index = k
        pointX.append(dataX[index])
        pointY.append(dataY[index])
        positionX[ID] = (1 - relaxation) * positionX[ID] + relaxation * dataX[index] #update position
        positionY[ID] = (1 - relaxation) * positionY[ID] + relaxation * dataY[index]
    return pointX, pointY

point1X, point1Y = get_pointPosition(0)
point2X, point2Y = get_pointPosition(1)



#calculate distance
distance = []
time = []
for n in range(len(point1X)):
    distance.append(np.sqrt((point2X[n] - point1X[n]) ** 2 + (point2Y[n] - point1Y[n]) ** 2)*0.12951)
    time.append(n*0.0333)


#plot the end-to-end distance
plt.plot(time,distance, 'r')
plt.ylabel("End-to-end distance (um)")
plt.xlabel("Time (s)")
plt.title("10_5")
plt.show()


# colours
BLUE = (1, 1, 1)
LOL = (0.2, 0.3, 0.2)

# the default video that the tensorflow was used
gelVid = mpy.VideoFileClip('test.mp4') 


# render the original video with the desired points

original_clip = mpy.VideoFileClip("test.mp4")
def render_text(t):
    surface = gz.Surface(width=640, height=480)
    text = gz.circle(r=4, fill=BLUE, xy=(point1X[int(len(point1X)*t/original_clip.duration)], point1Y[int(len(point1Y)*t/original_clip.duration)]))
    text.draw(surface)  
    
    text = gz.circle(r=4, fill=LOL, xy=(point2X[int(len(point2X)*t/original_clip.duration)], point2Y[int(len(point2Y)*t/original_clip.duration)]))
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
final_clip.write_videofile("test_output_video.mp4", fps=30)

