#!/usr/bin/env python3
"""
Terminal-based teleop node for the E116 racecar.
Uses raw terminal input instead of pygame.

Controls (simultaneous OK):
  W / S  — drive forward / backward  (speed persists while held)
  A / D  — steer left / right        (angle resets to 0 when released)
  Q      — quit
"""

import sys
import tty
import termios
import select

import rclpy
from rclpy.node import Node
from ackermann_msgs.msg import AckermannDriveStamped
from rclpy.qos import QoSProfile

MY_SPEED = 1.5   # meters/second  (reduced for safety)
MY_ANGLE = 0.15   # radians

USAGE = """
Terminal Teleop for E116 Racecar
--------------------------------
   W
 A   D
   S

W/S   : drive forward/backward ({speed} m/s) — STAYS on until stopped
A/D   : steer left/right ({angle} rad) — resets when released
SPACE : stop driving
Q     : quit
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

        # Timer at 10 Hz
        self.timer = self.create_timer(0.1, self.timer_callback)

        # Persistent state — speed is "sticky", angle is per-tick
        self._speed = 0.0
        self._prev_speed = None
        self._prev_angle = None

    def _drain_keys(self):
        """Read ALL buffered characters from stdin (non-blocking)."""
        keys = set()
        while select.select([sys.stdin], [], [], 0.0)[0]:
            ch = sys.stdin.read(1)
            if ch:
                keys.add(ch.lower())
        return keys

    def timer_callback(self):
        keys = self._drain_keys()

        # Quit on 'q' or Ctrl-C
        if 'q' in keys or '\x03' in keys:
            raise KeyboardInterrupt

        # --- Speed: STICKY — persists until changed by W/S/Space ---
        if 'w' in keys:
            self._speed = MY_SPEED
        elif 's' in keys:
            self._speed = -MY_SPEED
        elif ' ' in keys:
            self._speed = 0.0

        # --- Angle: MOMENTARY — only non-zero while A/D is in buffer ---
        angle = 0.0
        if 'a' in keys:
            angle = -MY_ANGLE
        elif 'd' in keys:
            angle = MY_ANGLE

        # Update display only on change
        if self._speed != self._prev_speed or angle != self._prev_angle:
            self._write_status(self._speed, angle)
            self._prev_speed = self._speed
            self._prev_angle = angle

        self.send_ackermann(self._speed, angle)

    def send_ackermann(self, speed: float, angle: float):
        msg = AckermannDriveStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'car'
        msg.drive.steering_angle = angle
        msg.drive.speed = speed
        self.drive_pub.publish(msg)

    def _write_status(self, speed: float, angle: float):
        """Write status to terminal while in raw mode."""
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
        print('\nShutting down keyJoyTerminal.')
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

