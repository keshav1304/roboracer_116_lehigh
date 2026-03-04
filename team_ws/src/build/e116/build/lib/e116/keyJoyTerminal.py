#!/usr/bin/env python3
"""
Terminal-based teleop node for the E116 racecar.
Same functionality as keyJoy.py but uses raw terminal input instead of pygame.
Controls: W=forward, S=reverse, A=steer left, D=steer right, Q=quit
"""

import sys
import tty
import termios
import select

import rclpy
from rclpy.node import Node
from ackermann_msgs.msg import AckermannDriveStamped
from rclpy.qos import QoSProfile

# Same constants as keyJoy.py
MY_SPEED = 1.50   # meters/second
MY_ANGLE = 0.05   # radians

USAGE = """
Terminal Teleop for E116 Racecar
--------------------------------
   W
 A   D
   S

W/S : forward/backward (speed = ±{speed} m/s)
A/D : steer left/right  (angle = ±{angle} rad)
Q   : quit
""".format(speed=MY_SPEED, angle=MY_ANGLE)


class KeyJoyTerminalNode(Node):
    def __init__(self):
        super().__init__('keyJoyTerminal')
        qos = QoSProfile(depth=10)
        self.drive_pub = self.create_publisher(
            AckermannDriveStamped, 'e116_ackermann', qos
        )

        # Save original terminal settings so we can restore them on exit
        self.old_settings = termios.tcgetattr(sys.stdin)

        # Put terminal into raw mode (no echo, no line buffering)
        tty.setraw(sys.stdin.fileno())

        # Timer at 10 Hz – same rate as keyJoy.py
        self.timer = self.create_timer(0.1, self.timer_callback)

        self._last_speed = 0.0
        self._last_angle = 0.0

    def _get_key(self):
        """Non-blocking read of a single character from stdin."""
        if select.select([sys.stdin], [], [], 0.0)[0]:
            return sys.stdin.read(1)
        return None

    def timer_callback(self):
        key = self._get_key()

        speed = 0.0
        angle = 0.0

        if key is not None:
            key = key.lower()
            if key == 'q' or key == '\x03':  # q or Ctrl-C
                raise KeyboardInterrupt

            if key == 'w':
                speed = MY_SPEED
            elif key == 's':
                speed = -MY_SPEED

            if key == 'a':
                angle = -MY_ANGLE
            elif key == 'd':
                angle = MY_ANGLE

        # Only log when values change to avoid spamming
        if speed != self._last_speed or angle != self._last_angle:
            self._write_status(speed, angle)
            self._last_speed = speed
            self._last_angle = angle

        self.send_ackermann(speed, angle)

    def send_ackermann(self, speed: float, angle: float):
        msg = AckermannDriveStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'car'
        msg.drive.steering_angle = angle
        msg.drive.speed = speed
        self.drive_pub.publish(msg)

    def _write_status(self, speed: float, angle: float):
        """Write status to terminal while in raw mode."""
        # \r moves cursor to start of line; ANSI escape clears the line
        line = f'\r\x1b[Kspeed: {speed:+.2f} m/s  |  angle: {angle:+.4f} rad'
        sys.stdout.write(line)
        sys.stdout.flush()

    def restore_terminal(self):
        """Restore the terminal to its original (cooked) settings."""
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)


def main(args=None):
    # Print usage BEFORE entering raw mode so it renders properly
    print(USAGE)

    rclpy.init(args=args)
    node = KeyJoyTerminalNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.restore_terminal()
        # Print a clean newline after raw-mode output
        print('\nShutting down keyJoyTerminal.')
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

