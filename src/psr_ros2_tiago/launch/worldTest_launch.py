import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import ExecuteProcess
from launch.actions import IncludeLaunchDescription


def generate_launch_description():
    package_name = 'psr_ros2_tiago'
    package_dir = get_package_share_directory(package_name)
    
    robot_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(package_dir, 'launch', 'robot_launch.py')
        ),
        launch_arguments={'world': 'task1.wbt'}.items()
    )

    rviz_config = os.path.join(package_dir, 'rviz', 'tiago_view.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}]
    )

    teleop_node = ExecuteProcess(
        cmd=[
            'gnome-terminal', '--',
            'ros2', 'run', 'psr_ros2_tiago', 'teleop_node'
        ],
        output='screen'
    )

    return LaunchDescription([
        robot_launch,
        rviz_node,
        teleop_node
    ])