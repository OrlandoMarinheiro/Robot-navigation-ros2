from setuptools import setup

package_name = "psr_ros2_tiago"
data_files = []
data_files.append(
    ("share/ament_index/resource_index/packages", ["resource/" + package_name])
)

data_files.append(
    (
        "share/" + package_name + "/launch",
        [
            "launch/robot_launch.py",
            "launch/worldTest_launch.py",
        ],
    )
)

data_files.append(
    (
        "share/" + package_name + "/resource",
        [
            "resource/tiago_webots.urdf",
            "resource/ros2_control.yml",
        ],
    )
)

data_files.append(("share/" + package_name, ["package.xml"]))

data_files.append(
    (
        "share/" + package_name + "/worlds",
        [
            "worlds/default.wbt",
            "worlds/.default.wbproj",
            "worlds/task1.wbt",
            "worlds/.task1.wbproj",
        ],
    )
)

data_files.append((
    ("share/" + package_name + "/rviz", ["rviz/tiago_view.rviz"])
))

setup(
    name=package_name,
    version="2025.0.1",
    packages=[package_name],
    data_files=data_files,
    install_requires=["setuptools", "launch"],
    zip_safe=True,
    author="Cyberbotics",
    author_email="support@cyberbotics.com",
    maintainer="Cyberbotics",
    maintainer_email="support@cyberbotics.com",
    keywords=["ROS", "Webots", "Robot", "Simulation", "Examples", "TIAGo"],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Topic :: Software Development",
    ],
    description="TIAGo robots ROS2 interface for Webots.",
    license="Apache License, Version 2.0",
    tests_require=["pytest"],
    # entry_points={"launch.frontend.launch_extension": ["launch_ros = launch_ros"]},
    entry_points={
        'console_scripts': [
            'teleop_node = psr_ros2_tiago.teleop_node:main',
        ],
    },
)
