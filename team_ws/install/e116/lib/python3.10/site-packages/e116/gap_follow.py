#!/usr/bin/env python3
import time
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from std_msgs.msg import String
import numpy as np
from ackermann_msgs.msg import AckermannDriveStamped
from tf2_msgs.msg import TFMessage

## parameters ##
SPEED0 = 0.0 #idle speed
SPEED1 = 0.1 #m/s, speed for single-tag tracking
SPEED2 = 0.15 #m/s, speed for driving between two tags
SINGLE_TAG_OFFSET = 0.20 # meters, lateral offset from a single tag (approximates half-track width)
angle_scale = 0.7
t_keep2 = 0.2
t_keep1 = 0.1

class GapFollowNode(Node):
    def __init__(self):
        super().__init__('gap_follow')
        qos = QoSProfile(depth=10)
        self.speed = 0.0
        self.angle = 0.0
        self.ptime1 = time.time()-10
        self.ptime2 = time.time()-10
        self.tag_num = -1
        self.drive_pub = self.create_publisher(AckermannDriveStamped,'e116_ackermann', qos)
        self.tags_sub = self.create_subscription(TFMessage, '/tf', self.callback, qos)
        self.tags_sub   # prevent unused variable warning        

    def callback(self, data):
        tag_transforms = [t for t in data.transforms if ':' in t.child_frame_id]
        if not tag_transforms:
            return
        data.transforms = tag_transforms
        self.printTagInfo(data)
        self.computeAckermann(data)
        self.sendAckermann(self.speed,self.angle)
        
    def printTagInfo(self,data):
        print("======= Found ", len(data.transforms), "tags =======")
        for tags in data.transforms:
            print(tags.child_frame_id)
                    
    def sendAckermann(self, speed: float, angle: float):
        drive_msg = AckermannDriveStamped()
        drive_msg.header.stamp = self.get_clock().now().to_msg()
        drive_msg.header.frame_id = "car"
        drive_msg.drive.steering_angle = angle
        drive_msg.drive.speed = speed
        self.drive_pub.publish(drive_msg)
        
    def computeAckermann(self, data):
        ### TAG FILTER ###
        tag_left = None
        tag_right = None
        #extract detected tag id
        for tags in data.transforms:
            tag_id = int(tags.child_frame_id.split(':')[1])
            if tag_left is None and  tag_id <= 199:
                tag_left = tags
            elif tag_right is None and 200 <= tag_id:
                tag_right = tags
        
        ### TIME UPDATE ###
        ctime = time.time()
        if tag_left and tag_right: 
            self.ptime2 = ctime
            self.ptime1 = ctime
        elif tag_left or tag_right:
            self.ptime1 = ctime
        
        ### FIND GOAL ###
        # case 1: Detected tags on both side
        if tag_left and tag_right: 
            left_pos = tag_left.transform.translation
            right_pos = tag_right.transform.translation
            goal_point = [(left_pos.x + right_pos.x)/2, (left_pos.z + right_pos.z)/2]
            print(f"goal point: {goal_point}")
            self.speed = SPEED2
            #assume a small angle such that tan(angle) ~= angle; avoid computing arctan()
            self.angle = goal_point[0] / goal_point[1] * angle_scale 
            print(f"speed: {self.speed}", f"angle: {self.angle}")
        # case 2: unstable
        elif ctime - self.ptime2 < t_keep2:
            pass
        # case 3: Only left side — steer toward a point offset to the right of the tag
        elif tag_left:
            pos = tag_left.transform.translation
            goal_point = [pos.x + SINGLE_TAG_OFFSET, pos.z]
            print(f"single left tag — goal point: {goal_point}")
            self.speed = SPEED1
            self.angle = goal_point[0] / goal_point[1] * angle_scale
            print(f"speed: {self.speed}", f"angle: {self.angle}")
        # case 4: Only right side — steer toward a point offset to the left of the tag
        elif tag_right:
            pos = tag_right.transform.translation
            goal_point = [pos.x - SINGLE_TAG_OFFSET, pos.z]
            print(f"single right tag — goal point: {goal_point}")
            self.speed = SPEED1
            self.angle = goal_point[0] / goal_point[1] * angle_scale
            print(f"speed: {self.speed}", f"angle: {self.angle}")
        # case 5: unstable
        elif ctime - self.ptime1 < t_keep1:
            pass
        # case 6: Find no tags
        else:
            self.speed= SPEED0
            self.angle = 0.0
        
def main(args=None):
    rclpy.init(args=args)
    node = GapFollowNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == "__main__":
    main()
