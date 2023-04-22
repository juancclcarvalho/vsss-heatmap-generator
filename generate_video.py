import cv2
import numpy as np
import random

# Define the image size
width = 1500
height = 1300

# Define the colors
ORANGE = (0, 140, 255)

ball_radius = 20

# Create the video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('ball_tracking.mp4', fourcc, 10, (width, height))

def draw_ball_position(ball_position):
    # Create a blank image
    img = np.full((height, width, 3), 255, np.uint8)
    img[3:height-3, 3:width-3] = [0, 0, 0]
    

    cv2.circle(img, (int(ball_position[0]), int(ball_position[1])), 20, ORANGE, -1)

    return img

def generate_video(ball_positions):
    for ball_position in ball_positions:
        img = draw_ball_position(ball_position)
        out.write(img)

    out.release()


def generate_positions(num_points):
    points = []

    for i in range(num_points):
        while True:
            x = random.randint(0, width)
            y = random.randint(0, height)

            # check if the ball is not too close to the edge
            if x > ball_radius and x < width - ball_radius and y > ball_radius and y < height - ball_radius:
                break

        points.append((x, y))

    return points

if __name__ == '__main__':

    ball_positions = generate_positions(50)

    generate_video(ball_positions)