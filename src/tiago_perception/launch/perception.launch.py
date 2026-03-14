from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    webots_package = get_package_share_directory('psr_ros2_tiago')
    webots_launch = os.path.join(
        webots_package,
        'launch',
        'robot_launch.py'
    )

    rviz_config = os.path.join(
        get_package_share_directory('tiago_perception'),
        'rviz',
        'perception.rviz'
    )

    return LaunchDescription([

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(webots_launch)
        ),

        Node(
            package='tiago_perception',
            executable='perception',
            name='tiago_perception',
            output='screen'
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            output='screen'
        ),
    ])

