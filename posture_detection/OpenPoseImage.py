import cv2
import time
import numpy as np
import math
import base64
import io
from PIL import Image


class Pose():
    def __init__(self, frame, frameCopy, frameWidth, frameHeight, threshold):
        self.frameWidth = frameWidth
        self.frameHeight = frameHeight
        self.frame = frame
        self.frameCopy = frameCopy
        self.threshold = 0.1
        MODE = "COCO"

        if MODE is "COCO":
            protoFile = "pose/coco/pose_deploy_linevec.prototxt"
            weightsFile = "pose/coco/pose_iter_440000.caffemodel"
            self.nPoints = 18
            self.POSE_PAIRS = [ [1,0],[1,2],[1,5],[2,3],[3,4],[5,6],[6,7],[1,8],[8,9],[9,10],[1,11],[11,12],[12,13],[0,14],[0,15],[14,16],[15,17]]

        elif MODE is "MPI" :
            protoFile = "pose/mpi/pose_deploy_linevec_faster_4_stages.prototxt"
            weightsFile = "pose/mpi/pose_iter_160000.caffemodel"
            self.nPoints = 15
            self.POSE_PAIRS = [[0,1], [1,2], [2,3], [3,4], [1,5], [5,6], [6,7], [1,14], [14,8], [8,9], [9,10], [14,11], [11,12], [12,13] ]

        self.net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)

        self.t = time.time()
        # input image dimensions for the network
        self.inWidth = 368
        self.inHeight = 368
        self.inpBlob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (self.inWidth, self.inHeight),
                                (0, 0, 0), swapRB=False, crop=False)

        self.net.setInput(self.inpBlob)

        self.output = self.net.forward()
        #print("time taken by network : {:.3f}".format(time.time() - t))

        self.H = self.output.shape[2]
        self.W = self.output.shape[3]

        # Empty list to store the detected keypoints
        self.points = []

        for i in range(self.nPoints):
            # confidence map of corresponding body's part.
            probMap = self.output[0, i, :, :]

            # Find global maxima of the probMap.
            minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)
            
            # Scale the point to fit on the original image
            x = (self.frameWidth * point[0]) / self.W
            y = (self.frameHeight * point[1]) / self.H

            if prob > threshold : 
                cv2.circle(frameCopy, (int(x), int(y)), 8, (0, 255, 255), thickness=-1, lineType=cv2.FILLED)
                cv2.putText(frameCopy, "{}".format(i), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, lineType=cv2.LINE_AA)

                # Add the point to the list if the probability is greater than the threshold
                self.points.append((int(x), int(y)))
            else :
                self.points.append(None)
        #print(self.points) 
        self.dist = math.sqrt((self.points[1][0] - self.points[5][0])**2 + (self.points[1][1] - self.points[5][1])**2) 
        self.slope = (self.points[1][1] - self.points[5][1]) / (self.points[1][0] - self.points[5][0])
        #print("slope", self.slope)
        #print("distance", self.dist)
        # Compare with baseline


        # Draw Skeleton
        for pair in self.POSE_PAIRS:
            partA = pair[0]
            partB = pair[1]
            if self.points[partA] and self.points[partB]:
                
                cv2.line(self.frame, self.points[partA], self.points[partB], (0, 255, 255), 2)
                cv2.circle(self.frame, self.points[partA], 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)


        #cv2.imshow('Output-Keypoints', self.frameCopy)
        #cv2.imshow('Output-Skeleton', self.frame)


       # cv2.imwrite('Output-Keypoints.jpg', self.frameCopy)
        #cv2.imwrite('Output-Skeleton.jpg', self.frame)

        #print("Total time taken : {:.3f}".format(time.time() - t))

        

def simulate():

    b = b'data:image/jpeg;base64,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'
    z = b[b.find(b'/9'):]
    im = Image.open(io.BytesIO(base64.b64decode(z))).save('test_image_1.jpg')
    frame = cv2.imread("test_image_1.jpg")
    frameCopy = np.copy(frame)
    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]
    pose = Pose(frame, frameCopy, frameWidth, frameHeight, 0.1)
    distance_1 = pose.dist
    frame = frame = cv2.imread("test_image_2.jpeg")
    frameCopy = np.copy(frame)
    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]
    pose = Pose(frame, frameCopy, frameWidth, frameHeight, 0.1)
    distance_2 = pose.dist
    distance = distance_2 - distance_1
    #print(distance)
    if distance <= 0:
        print("DONT SLOUCH")
    return

if __name__ == "__main__":
    simulate()