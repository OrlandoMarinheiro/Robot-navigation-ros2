#!/usr/bin/env python3

import sys
import termios
import tty
import select

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import TwistStamped


def get_key():
    """Read a single keypress from stdin and discard the rest to avoid lag."""
    key = None
    while select.select([sys.stdin], [], [], 0)[0]:
        key = sys.stdin.read(1)
    return key


class TeleopPSR(Node):

    def __init__(self):
        super().__init__('teleop_psr')

        # max speeds
        self.vx_max = 1.0
        self.vw_max = 1.5

        self.linear_speed = 0.5
        self.angular_speed = 1.0

        self.pub = self.create_publisher(TwistStamped, "/cmd_vel", 1)

        self.timer = self.create_timer(0.05, self.update)

        self.get_logger().info(
            "\nTeleopPSR (keyboard) initialized!\n"
            "w/s → forward/backward\n"
            "a/d → rotate left/right\n"
            "1/2/3 → slow/normal/fast\n"
            "ESC → exit\n"
        )

    def update(self):
        key = get_key()

        twist = TwistStamped()
        twist.header.stamp = self.get_clock().now().to_msg()
        twist.header.frame_id = "base_link"

        if key == 'w':
            twist.twist.linear.x = self.linear_speed
        elif key == 's':
            twist.twist.linear.x = -self.linear_speed
        elif key == 'a':
            twist.twist.angular.z = self.angular_speed
        elif key == 'd':
            twist.twist.angular.z = -self.angular_speed

        elif key == '1':
            self.linear_speed = 0.2
            self.angular_speed = 0.4
            self.get_logger().info("Velocity SLOW")
        elif key == '2':
            self.linear_speed = 1.0
            self.angular_speed = 1.0
            self.get_logger().info("Velocity NORMAL")
        elif key == '3':
            self.linear_speed = 2.0
            self.angular_speed = 2.0
            self.get_logger().info("Velocity FAST")

        elif key == 27:
            self.get_logger().info("Teleop finished.")
            rclpy.shutdown()
            return

        self.pub.publish(twist)


def main(args=None):
    # save terminal settings
    settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())

    rclpy.init(args=args)

    teleop = TeleopPSR()

    try:
        rclpy.spin(teleop)
    except KeyboardInterrupt:
        pass

    teleop.destroy_node()
    rclpy.shutdown()
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

if __name__ == '__main__':
    main()