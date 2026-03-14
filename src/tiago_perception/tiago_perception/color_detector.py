import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
import numpy as np
from visualization_msgs.msg import Marker, MarkerArray

class Perception(Node):
    def __init__(self):
        super().__init__('tiago_perception')
        self.bridge = CvBridge()
        
        # Stores the latest depth image
        self.depth_image = None

        # Publishers
        self.pub = self.create_publisher(String, '/detected_objects', 10)
        self.marker_pub = self.create_publisher(MarkerArray,'/detected_objects_markers',10)

        # Subscribers
        self.create_subscription(Image, '/Tiago_Lite/Astra_rgb/image_color', self.img_callback, 10)
        self.create_subscription(Image, '/Tiago_Lite/Astra_depth/image', self.depth_callback, 10)

    def depth_callback(self, msg):
        try:
            self.depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
        except Exception as e:
            self.get_logger().error(f"Depth error: {e}")

    def img_callback(self, msg):
        try:
            cv_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f"RGB Falid: {e}")
            return

        hsv_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
        self.process_color(hsv_image, 'red')
        self.process_color(hsv_image, 'blue')

    def get_distance(self, cx, cy):
        if self.depth_image is None:
            return 1.0 # Default if no depth
            
        try:
            # Access depth pixel (y, x)
            d = self.depth_image[cy, cx]
            
            # If uint16 (mm), convert to meters
            if self.depth_image.dtype == np.uint16:
                d = d / 1000.0
                
            # Filter invalid values
            if np.isnan(d) or np.isinf(d) or d <= 0.1:
                return 1.0
                
            return float(d)
        except:
            return 1.0

    def process_color(self, hsv, color_name):
        if color_name == 'red':
            # Range for RED
            lower1, upper1 = np.array([170, 10, 10]), np.array([180, 255, 255])
            lower2, upper2 = np.array([0, 10, 10]), np.array([7, 255, 255])
            mask = cv2.inRange(hsv, lower1, upper1) + cv2.inRange(hsv, lower2, upper2)
            marker_color = (1.0, 0.0, 0.0)
            marker_id_base = 0
        else:
            # Range for BLUE
            lower, upper = np.array([90, 0, 20]), np.array([130, 255, 255])
            mask = cv2.inRange(hsv, lower, upper)
            marker_color = (0.0, 0.0, 1.0)
            marker_id_base = 100

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        marker_array = MarkerArray()
        
        count = 0
        for contour in contours:
            if cv2.contourArea(contour) < 200:
                continue
                
            x, y, w, h = cv2.boundingRect(contour)
            cx = x + w // 2
            cy = y + h // 2
            area = w * h
            
            # Get real distance using depth
            dist = self.get_distance(cx, cy)
            
            # Publish string
            msg = String()
            msg.data = f"{color_name} cx={cx} cy={cy} dist={dist:.2f}"
            self.pub.publish(msg)
            
            # Create marker
            marker = self.create_marker(cx, cy, dist, marker_color, marker_id_base + count)
            marker_array.markers.append(marker)
            count += 1
            
        if marker_array.markers:
            self.marker_pub.publish(marker_array)

    def create_marker(self, cx, cy, dist, color, marker_id):
        marker = Marker()
        marker.header.frame_id = "base_link"
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = "detected_objects"
        marker.id = marker_id
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD

        # -- Position Logic --
        # X: Forward Distance (Depth)
        marker.pose.position.x = dist
        # Y: Left/Right
        marker.pose.position.y = -(cx - 320) / 320.0 * dist 
        # Z: Height
        # Fixed at 0.5m to be on top of the objects
        marker.pose.position.z = 0.5

        marker.pose.orientation.w = 1.0
        marker.scale.x = 0.2
        marker.scale.y = 0.2
        marker.scale.z = 0.2
        
        marker.color.r = color[0]
        marker.color.g = color[1]
        marker.color.b = color[2]
        marker.color.a = 1.0
        marker.lifetime.sec = 1
        return marker

def main():
    rclpy.init()
    node = Perception()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

