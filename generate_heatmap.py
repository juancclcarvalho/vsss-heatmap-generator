import cv2
import numpy as np
import matplotlib.pyplot as plt

class HeatmapGenerator:
    def __init__(self, video_path, width=1500, height=1300, heatmap_width=10, heatmap_height=10):
        self.video_path = video_path
        self.width = width
        self.height = height
        self.ball_positions = []
        self.heatmap = np.zeros((width, height))
        self.cap = cv2.VideoCapture(video_path)
        self.done = False
        self.corners = []
        self.frame = None
        self.crop_frame = None
        self.M = None

    def run(self):
        self.mark_corners()
        self.get_ball_positions()
        self.generate_heatmap()

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.corners.append([x, y])
                
            # stop after the 4 corners are marked
            if len(self.corners) == 4:
                self.done = True

    def mark_corners(self):
        # get the first frame
        _, self.frame = self.cap.read()

        cv2.namedWindow('corners')
        cv2.setMouseCallback('corners', self.mouse_callback)
        cv2.imshow('corners', self.frame)

        # wait until all 4 corners are marked
        while not self.done:
            cv2.waitKey(10)

        cv2.destroyWindow('corners')

        # calculate the perspective transform
        pts1 = np.float32(self.corners)
        pts2 = np.float32([[0,0],[self.width,0],[self.width,self.height],[0,self.height]])
        self.M = cv2.getPerspectiveTransform(pts1, pts2)

    def get_ball_positions(self):
        while True:
            ret, self.frame = self.cap.read()
            if not ret:
                break

           # apply the perspective transform
            self.crop_frame = cv2.warpPerspective(self.frame, self.M, (self.width, self.height))


            hsv = cv2.cvtColor(self.crop_frame, cv2.COLOR_BGR2HSV)
            # define range of orange color in HSV
            lower_orange = np.array([5, 100, 100])
            upper_orange = np.array([15, 255, 255])
            # create a mask that ignores everything except the orange color
            mask = cv2.inRange(hsv, lower_orange, upper_orange)
            # find the contours of the orange color
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)

            for cnt in contours:
                (x, y), radius = cv2.minEnclosingCircle(cnt)
                center = (int(x), int(y))
                radius = int(radius)
                
                if radius > 10:
                    self.ball_positions.append(center)
                    cv2.circle(self.crop_frame, center, radius, (0, 255, 0), 2)
                    break


            # display the transformed frame
            cv2.namedWindow('transform', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('transform', (800, 600))
            cv2.imshow('transform', self.crop_frame)

            # exit if q is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

    def generate_heatmap(self):
        x, y = zip(*self.ball_positions)
        heatmap, xedges, yedges = np.histogram2d(x, y, bins=10)
        
        extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]

        plt.clf()

        plt.imsave('heatmap.png', heatmap.T, cmap='hot')
        plt.imshow(heatmap.T, extent=extent, origin='lower', cmap='hot')
        plt.show()

if __name__ == '__main__':
    heatmap_generator = HeatmapGenerator('cin_vs_ita.mp4')
    heatmap_generator.run()
