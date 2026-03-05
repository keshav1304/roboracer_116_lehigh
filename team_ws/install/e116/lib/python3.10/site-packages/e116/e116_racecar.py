#!/usr/bin/env python3
import time
import RPi.GPIO as GPIO

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from ackermann_msgs.msg import AckermannDriveStamped

# hardware pins (keep as module-level constants)
SERVO_PIN = 15
MOTOR_PIN = 33
DEADMAN_PIN = 40
PWM_FREQ= 200
MOTOR_FORWARD_START_DEFAULT=31.61
MOTOR_BACKWARD_START_DEFAULT=28.71
SERVO_CENTER_DEFAULT=29.70

class e116RacecarNode(Node):
    def __init__(self):
        super().__init__('e116_racecar')

        # --- declare parameters with same defaults as your ROS2 node ---
        self.declare_parameter('servo_min', SERVO_CENTER_DEFAULT-8)
        self.declare_parameter('servo_max', SERVO_CENTER_DEFAULT+8)
        self.declare_parameter('servo_center', SERVO_CENTER_DEFAULT)

        self.declare_parameter('motor_range', 0.6)
        self.declare_parameter('motor_forward_start', MOTOR_FORWARD_START_DEFAULT)
        self.declare_parameter('motor_backward_start', MOTOR_BACKWARD_START_DEFAULT)

        self.declare_parameter('speed_scale', 0.75)
        self.declare_parameter('angle_scale', 25.00)
        self.declare_parameter('speed_dead_area', 0.1)

        # --- read parameters into instance variables ---
        self.servo_min = float(self.get_parameter('servo_min').value)
        self.servo_max = float(self.get_parameter('servo_max').value)
        self.servo_center = float(self.get_parameter('servo_center').value)

        self.motor_range = float(self.get_parameter('motor_range').value)
        self.motor_forward_start = float(self.get_parameter('motor_forward_start').value)
        self.motor_backward_start = float(self.get_parameter('motor_backward_start').value)
        self.motor_init = (self.motor_forward_start + self.motor_backward_start) / 2.0

        self.Ackermann_speed_scale = float(self.get_parameter('speed_scale').value)
        self.Ackermann_angle_scale = float(self.get_parameter('angle_scale').value)
        self.Ackermann_dead_area = float(self.get_parameter('speed_dead_area').value)

        # --- GPIO setup (done in constructor to avoid import-time side-effects) ---
        GPIO.setmode(GPIO.BOARD)
        #GPIO.setup(SERVO_PIN, GPIO.OUT)
        #GPIO.setup(MOTOR_PIN, GPIO.OUT)
        #GPIO.setup(DEADMAN_PIN, GPIO.IN)

        # start PWM
        GPIO.setup(SERVO_PIN, GPIO.OUT)
        self.servo_pwm = GPIO.PWM(SERVO_PIN, PWM_FREQ)
        self.servo_pwm.start(self.servo_center)
        
        GPIO.setup(MOTOR_PIN, GPIO.OUT)
        self.motor_pwm = GPIO.PWM(MOTOR_PIN, PWM_FREQ)
        self.motor_pwm.start(self.motor_init)
        
        GPIO.setup(DEADMAN_PIN, GPIO.IN)
	
        # subscription (QoS depth ~ queue_size 10)
        qos = QoSProfile(depth=10)
        self.sub = self.create_subscription(
            AckermannDriveStamped,
            'e116_ackermann',
            self.callback,
            qos
        )

        self.get_logger().info('e116_racecar node started')

    def speed2duty(self, speed: float) -> float:
        motor_duty = self.motor_init
        if abs(speed) < self.Ackermann_dead_area:
            motor_duty = self.motor_init
        elif speed > 0:
            motor_duty = self.motor_forward_start + (speed - self.Ackermann_dead_area) * self.Ackermann_speed_scale
        else:
            motor_duty = self.motor_backward_start + (speed + self.Ackermann_dead_area) * self.Ackermann_speed_scale

        # clamp
        max_duty = self.motor_forward_start + self.motor_range
        min_duty = self.motor_backward_start - self.motor_range
        if motor_duty > max_duty:
            motor_duty = max_duty
        if motor_duty < min_duty:
            motor_duty = min_duty
        return motor_duty

    def angle2duty(self, angle: float) -> float:
        servo_duty = self.servo_center + angle * self.Ackermann_angle_scale
        if servo_duty > self.servo_max:
            servo_duty = self.servo_max
        if servo_duty < self.servo_min:
            servo_duty = self.servo_min
        return servo_duty

    def callback(self, msg: AckermannDriveStamped):
        speed = msg.drive.speed
        angle = msg.drive.steering_angle

        if GPIO.input(DEADMAN_PIN):
            self.servo_pwm.ChangeDutyCycle(self.angle2duty(angle))
            self.motor_pwm.ChangeDutyCycle(self.speed2duty(speed))
        else:
            # safe: go to zero commands
            self.servo_pwm.ChangeDutyCycle(self.angle2duty(0.0))
            self.motor_pwm.ChangeDutyCycle(self.speed2duty(0.0))
            # keep a log instead of raw print
            self.get_logger().warn(f'!!DeadMan Disabled!! {time.ctime()}')

def main(args=None):
    rclpy.init(args=args)
    node = e116RacecarNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # tidy up hardware before exit
        try:
            node.get_logger().info('Stopping PWM and cleaning up GPIO')
        except Exception:
            pass
        try:
            node.servo_pwm.stop()
            node.motor_pwm.stop()
        except Exception:
            pass
        GPIO.cleanup()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
