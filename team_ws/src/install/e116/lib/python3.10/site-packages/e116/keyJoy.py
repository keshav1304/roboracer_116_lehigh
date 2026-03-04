#!/usr/bin/env python3

import pygame
import rclpy
from rclpy.node import Node
from ackermann_msgs.msg import AckermannDriveStamped
from rclpy.qos import QoSProfile

# pygame UI setup (same as your ROS1 file)
pygame.init()
X = 200
Y = 200
screen = pygame.display.set_mode((X, Y))
clock = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf', 32)

# constants
MY_SPEED = 1.50 #meters/second
MY_ANGLE = 0.05 #radians


class KeyJoyNode(Node):
    def __init__(self):
        super().__init__('keyJoy')
        qos = QoSProfile(depth=10)
        # publisher similar to rospy.Publisher(...)
        self.drive_pub = self.create_publisher(AckermannDriveStamped, 'e116_ackermann', qos)

        # create a timer to run at ~10 Hz (replaces rospy.Rate loop)
        self.timer = self.create_timer(0.1, self.timer_callback)

    def timer_callback(self):
        # Poll pygame events and key state (must call event.get() to keep pygame responsive)
        pygame.event.get()
        keys = pygame.key.get_pressed()

        # same key logic as original
        speed = 0.0
        if keys[pygame.K_w]:
            speed = MY_SPEED
        elif keys[pygame.K_s]:
            speed = -MY_SPEED

        angle = 0.0
        if keys[pygame.K_a]:
            angle = -MY_ANGLE
        elif keys[pygame.K_d]:
            angle = MY_ANGLE

        self.send_ackermann(speed, angle)

    def send_ackermann(self, speed: float, angle: float):
        msg = AckermannDriveStamped()
        # rclpy way to stamp header:
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'car'
        msg.drive.steering_angle = angle
        msg.drive.speed = speed
        self.drive_pub.publish(msg)
      
    #def cleanup(self):
        


def main(args=None):
    rclpy.init(args=args)
    node = KeyJoyNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        pygame.quit()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

