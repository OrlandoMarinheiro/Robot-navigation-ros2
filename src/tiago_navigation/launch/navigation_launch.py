

"""
Task 3 – Navigation Launch File
Starts:
- Webots simulation (TIAGo)
- Nav2 (map_server, AMCL, planner, controller)
- RViz
- Semantic navigation node
- Cmd Vel Converter Node (Twist to TwistStamped)
"""

import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node
from nav2_common.launch import RewrittenYaml


def generate_launch_description():

    # ------------------ Package directories ------------------
    tiago_nav_dir = get_package_share_directory('tiago_navigation')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    tiago_main_dir = get_package_share_directory('psr_ros2_tiago')
    tiago_slam_dir = get_package_share_directory('tiago_slam')

    # ------------------ Files ------------------
    map_file = os.path.join(
        tiago_slam_dir,
        'maps',
        'my_map.yaml',
    )

    nav2_params_file = os.path.join(
        tiago_nav_dir,
        'config',
        'nav2_params.yaml',
    )

    locations_file = os.path.join(
        tiago_nav_dir,
        'config',
        'locations.yaml'
    )

    rviz_config = os.path.join(
        tiago_nav_dir,
        'rviz',
        'nav2_view.rviz'

    )

    # ------------------ Launch arguments ------------------
    use_sim_time = LaunchConfiguration('use_sim_time')
    map_yaml_file = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    autostart = LaunchConfiguration('autostart')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation time'
    )

    declare_map = DeclareLaunchArgument(
        'map',
        default_value=map_file,
        description='Full path to map yaml file'
    )

    declare_params = DeclareLaunchArgument(
        'params_file',
        default_value=nav2_params_file,
        description='Full path to Nav2 parameters file'
    )

    declare_autostart = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Autostart Nav2 lifecycle nodes'
    )

    # ------------------ Rewrite params ------------------
    configured_nav2_params = RewrittenYaml(
        source_file=params_file,
        root_key='',
        param_rewrites={'yaml_filename': map_yaml_file},
        convert_types=True
    )

    # ------------------ Webots ------------------
    webots_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(tiago_main_dir, 'launch', 'robot_launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )


    # ------------------ Nav2 ------------------
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'bringup_launch.py')
        ),  
        launch_arguments={
            'map': map_file,
            'use_sim_time': use_sim_time,
            'params_file': configured_nav2_params,
            'autostart': autostart
        }.items()        
    )

    # ------------------ Semantic Navigator ------------------
    semantic_navigator = Node(
        package='tiago_navigation',
        executable='semantic_navigator',
        name='semantic_navigator',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'locations_file': locations_file}
        ]
    )

    # Cmd Vel Converter Node (Twist to TwistStamped)
    converter = Node(
        package='tiago_navigation',
        executable='cmd_vel_converter',
        name='cmd_vel_converter',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # ------------------ RViz ------------------
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # ------------------ Launch Description ------------------
    ld = LaunchDescription()

    ld.add_action(SetEnvironmentVariable(
        'RCUTILS_LOGGING_BUFFERED_STREAM', '1'
    ))

    ld.add_action(declare_use_sim_time)
    ld.add_action(declare_map)
    ld.add_action(declare_params)
    ld.add_action(declare_autostart)

    ld.add_action(webots_launch)
    ld.add_action(nav2_launch)
    ld.add_action(semantic_navigator)
    ld.add_action(converter)
    ld.add_action(rviz)

    return ld