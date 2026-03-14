from setuptools import setup
import os
from glob import glob

package_name = 'tiago_perception'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    install_requires=['setuptools'],
    zip_safe=True,
    author='francis88703',
    maintainer='francis88703',
    maintainer_email='francisco300704@gmail.com',
    description='TIAGo perception package',
    license='TODO',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'perception = tiago_perception.color_detector:main',
        ],
    },
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),  # <--- aqui
        ('share/' + package_name + '/rviz', glob('rviz/*.rviz')),
    ],
)

