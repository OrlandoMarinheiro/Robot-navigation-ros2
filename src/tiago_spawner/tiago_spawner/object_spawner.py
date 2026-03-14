import rclpy
from rclpy.node import Node
from webots_ros2_msgs.srv import SpawnNodeFromString
from tiago_spawn_service.srv import SpawnObject
import random
import math


def quat(roll: float, pitch: float, yaw: float):
    # Roll, pitch, yaw conversion to quaternion (x, y, z, w)
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)

    qw = cr * cp * cy + sr * sp * sy
    qx = sr * cp * cy - cr * sp * sy
    qy = cr * sp * cy + sr * cp * sy
    qz = cr * cp * sy - sr * sp * cy
    return qx, qy, qz, qw


def axis_angle(qx: float, qy: float, qz: float, qw: float):
    #Quaternion conversion to axis-angle (ax, ay, az, angle).
    norm = math.sqrt(qx*qx + qy*qy + qz*qz + qw*qw)
    if norm == 0.0:
        return 0.0, 0.0, 1.0, 0.0
    qx, qy, qz, qw = qx / norm, qy / norm, qz / norm, qw / norm

    qw = max(-1.0, min(1.0, qw))
    angle = 2.0 * math.acos(qw)

    s = math.sqrt(1.0 - qw*qw)  # = sin(angle/2)
    if s < 1e-8:
        return 0.0, 0.0, 1.0, 0.0

    ax = qx / s
    ay = qy / s
    az = qz / s
    return ax, ay, az, angle


class Spawner(Node):
    def __init__(self):
        super().__init__('proto_spawner')

        self.srv = self.create_service(SpawnObject, '/spawn_object', self.spawn_callback)

        self.client = self.create_client(
            SpawnNodeFromString,
            '/Ros2Supervisor/spawn_node_from_string'
        )
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for Webots supervisor service...')

        self.get_logger().info('Spawner ready!')

    def spawn_callback(self, request, response):
        shape = (request.shape or "box").strip().lower()
        #SIZES
        if shape == "sphere":
            radius = 0.5
            geometry = f"Sphere {{ radius {radius} }}"
            bounding = f"Sphere {{ radius {radius} }}"
            default_z = radius
        else:
            sx, sy, sz = 1.0, 1.0, 1.0
            geometry = f"Box {{ size {sx} {sy} {sz} }}"
            bounding = f"Box {{ size {sx} {sy} {sz} }}"
            default_z = sz / 2.0

        # POSE RANGE FOR RANDOM SPAWNING
        if request.random:
            x = random.uniform(0.5, 2.0)
            y = random.uniform(0.5, 2.0)
            z = default_z
            roll = 0.0
            pitch = 0.0
            yaw = random.uniform(-math.pi, math.pi)
        else:
            x = float(request.x)
            y = float(request.y)
            z = float(request.z)
            roll = float(request.roll)
            pitch = float(request.pitch)
            yaw = float(request.yaw)

        # NAME GENERATION
        base_name = request.name.strip() if request.name else ""
        if not base_name:
            base_name = shape
        name = f"{base_name}_{random.randint(0, 9999)}"

        qx, qy, qz, qw = quat(roll, pitch, yaw)
        ax, ay, az, angle = axis_angle(qx, qy, qz, qw)

        #COLORS
        if shape == "sphere":
            color_r, color_g, color_b = 0.0, 0.0, 1.0   # blue
        else:
            color_r, color_g, color_b = 1.0, 0.0, 0.0   # red

        #PROTO STRING TEMPLATE
        proto_string = f"""
        Solid {{
            translation {x} {y} {z}
            rotation {ax} {ay} {az} {angle}
            name "{name}"
            children [
                Shape {{
                    appearance PBRAppearance {{
                        baseColor {color_r} {color_g} {color_b}
                    }}
                    geometry {geometry}
                }}
            ]
            boundingObject {bounding}
        }}
        """

        req = SpawnNodeFromString.Request()
        req.data = proto_string

        future = self.client.call_async(req)

        def done(fut):  #Spawn success or failure info
            try:
                res = fut.result()
            except Exception as e:
                self.get_logger().error(f"Supervisor call failed: {e}")
                return

            if res.success:
                self.get_logger().info(
                    f"Spawned '{name}' ({shape}) at ({x:.2f},{y:.2f},{z:.2f}) "
                    f"rpy=({roll:.2f},{pitch:.2f},{yaw:.2f})"
                )
            else:
                self.get_logger().error(f"Spawn failed: {res.message}")

        future.add_done_callback(done)

        response.success = True
        response.message = f"Spawn request sent for {shape}"
        return response


def main(args=None):
    rclpy.init(args=args)
    node = Spawner()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

