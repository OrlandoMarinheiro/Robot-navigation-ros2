from setuptools import find_packages, setup

package_name = 'tiago_navigation'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (
            'share/' + package_name + '/launch',
            ['launch/navigation_launch.py'],
        ),
        (
            'share/' + package_name + '/config',
            [
                'config/nav2_params.yaml',
                'config/locations.yaml',
            ],
        ),
        (
            'share/' + package_name + '/rviz',
            ['rviz/nav2_view.rviz'],
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='marinheiro',
    maintainer_email='orlandomarinheiro@ua.pt',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'cmd_vel_converter = tiago_navigation.cmd_vel_converter:main',
            'semantic_navigator = tiago_navigation.semantic_navigator:main',
        ],
    },
)
