import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    package_dir = get_package_share_directory('psr_ros2_tiago')
    tiago_slam_dir = get_package_share_directory('tiago_slam')
    
    # robot launch
    robot_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(package_dir, 'launch', 'robot_launch.py')
        ),
        launch_arguments={
            'world': 'task1.wbt', 
            'use_sim_time': 'True'
        }.items()
    )

    # SLAM node (iris_lama_ros2)
    slam_node = Node(
        package='iris_lama_ros2',    
        executable='slam2d_ros',     
        name='slam2d_ros',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    # teleop node
    teleop_process = ExecuteProcess(
        cmd=[
            'gnome-terminal', '--', 'bash', '-c', 
            'ros2 run psr_ros2_tiago teleop_node; exec bash'
        ],
        output='screen'
    )

    # RViz
    rviz_config_path = os.path.join(tiago_slam_dir, 'rviz', 'slam.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_path],
        parameters=[{'use_sim_time': True}],
    )

    # simple delay to ensure Webots is fully up before starting teleop
    delayed_teleop = TimerAction(
        period=5.0,
        actions=[teleop_process]
    )

    return LaunchDescription([
        robot_launch,
        slam_node, 
        rviz_node,
        delayed_teleop
    ])