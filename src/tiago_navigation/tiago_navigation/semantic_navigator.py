
"""
Semantic Navigation Node for TIAGo Robot
Accepts location names and sends NavigateToPose action goals to Nav2
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup

from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String
from std_srvs.srv import Trigger

import yaml
import os
from ament_index_python.packages import get_package_share_directory


class SemanticNavigator(Node):

    def __init__(self):
        super().__init__('semantic_navigator')

        self.callback_group = ReentrantCallbackGroup()

        # Parameters
        self.declare_parameter('locations_file', 'locations.yaml')
        self.declare_parameter('action_server_name', '/navigate_to_pose')

        # Load locations
        self.locations = self.load_locations()
        if not self.locations:
            self.get_logger().error('No locations loaded!')
        else:
            self.get_logger().info(
                f'Loaded locations: {list(self.locations.keys())}'
            )

        # Action client
        self.nav_client = ActionClient(
            self,
            NavigateToPose,
            self.get_parameter('action_server_name').value,
            callback_group=self.callback_group
        )

        # Wait ONCE for Nav2 action server
        self.get_logger().info('Waiting for NavigateToPose action server...')
        self.nav_client.wait_for_server()
        self.get_logger().info('NavigateToPose action server is available!')

        # Topic interface
        self.location_sub = self.create_subscription(
            String,
            'go_to_location',
            self.location_callback,
            10
        )

        # Simple service example
        self.home_service = self.create_service(
            Trigger,
            'navigate_home',
            self.navigate_home_callback
        )

        # Status publisher
        self.status_pub = self.create_publisher(
            String,
            'navigation_status',
            10
        )

        self.current_goal_handle = None
        self.get_logger().info('Semantic Navigator ready.')

    # ------------------ Utilities ------------------

    def load_locations(self):
        try:
            filename = self.get_parameter('locations_file').value
            pkg_dir = get_package_share_directory('psr_ros2_tiago')
            path = os.path.join(pkg_dir, 'config', filename)

            self.get_logger().info(f'Loading locations from: {path}')
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                return data.get('locations', {})

        except Exception as e:
            self.get_logger().error(f'Failed to load locations: {e}')
            return {}

    def create_pose(self, loc):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()

        pose.pose.position.x = float(loc['x'])
        pose.pose.position.y = float(loc['y'])
        pose.pose.position.z = float(loc.get('z', 0.0))

        ori = loc.get('orientation', {})
        pose.pose.orientation.x = float(ori.get('x', 0.0))
        pose.pose.orientation.y = float(ori.get('y', 0.0))
        pose.pose.orientation.z = float(ori.get('z', 0.0))
        pose.pose.orientation.w = float(ori.get('w', 1.0))

        return pose

    def publish_status(self, text):
        msg = String()
        msg.data = text
        self.status_pub.publish(msg)

    # ------------------ Interfaces ------------------

    def location_callback(self, msg):
        location = msg.data.strip().lower()
        self.navigate_to_location(location)

    def navigate_home_callback(self, request, response):
        success = self.navigate_to_location('living_room')
        response.success = success
        response.message = 'Goal sent' if success else 'Failed'
        return response

    # ------------------ Navigation Logic ------------------

    def navigate_to_location(self, location_name):
        if location_name not in self.locations:
            self.get_logger().error(
                f'Unknown location "{location_name}". '
                f'Available: {list(self.locations.keys())}'
            )
            self.publish_status('FAILED: Unknown location')
            return False

        goal = NavigateToPose.Goal()
        goal.pose = self.create_pose(self.locations[location_name])

        self.get_logger().info(f'Sending goal to {location_name}')
        send_goal_future = self.nav_client.send_goal_async(
            goal,
            feedback_callback=self.feedback_callback
        )

        send_goal_future.add_done_callback(
            lambda f: self.goal_response_callback(f, location_name)
        )

        self.publish_status(f'SENT: {location_name}')
        return True

    def goal_response_callback(self, future, location_name):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error(f'Goal to {location_name} rejected')
            self.publish_status('REJECTED')
            return

        self.get_logger().info(f'Goal to {location_name} accepted')
        self.current_goal_handle = goal_handle

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(
            lambda f: self.result_callback(f, location_name)
        )

    def feedback_callback(self, feedback_msg):
        distance = feedback_msg.feedback.distance_remaining
        self.get_logger().info(
            f'Distance remaining: {distance:.2f} m',
            throttle_duration_sec=2.0
        )
        self.publish_status(f'IN_PROGRESS: {distance:.2f} m')

    def result_callback(self, future, location_name):
        status = future.result().status

        if status == 4:
            self.get_logger().info(f'Reached {location_name}')
            self.publish_status('SUCCEEDED')
        elif status == 6:
            self.get_logger().warn('Navigation aborted')
            self.publish_status('ABORTED')
        elif status == 5:
            self.get_logger().warn('Navigation canceled')
            self.publish_status('CANCELED')
        else:
            self.get_logger().error(f'Navigation failed (status {status})')
            self.publish_status('FAILED')


def main(args=None):
    rclpy.init(args=args)
    node = SemanticNavigator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()