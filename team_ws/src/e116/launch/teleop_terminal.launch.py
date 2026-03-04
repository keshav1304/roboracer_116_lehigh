from launch import LaunchDescription
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_share = get_package_share_directory('e116')
    config_file = os.path.join(pkg_share, 'config', 'e116.yaml')

    return LaunchDescription([
        Node(
            package='e116',
            executable='keyJoyTerminal',  # terminal-based teleop
            name='keyJoyTerminal',
            output='screen',
            parameters=[config_file]
        ),
        Node(
            package='e116',
            executable='e116_racecar',
            name='e116_racecar',
            output='screen',
            parameters=[config_file]
        ),
    ])

