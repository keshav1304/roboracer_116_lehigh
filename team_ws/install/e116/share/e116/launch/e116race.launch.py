import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource, FrontendLaunchDescriptionSource


def generate_launch_description():
    # Get the path to your package's share directory
    pkg0_share_dir = get_package_share_directory('apriltag_ros')
    # Define the path to your .launch.yaml file
    yml_launch_file = os.path.join(pkg0_share_dir, 'launch', 'rs2camera_tag.launch.yml')

    pkg_share = get_package_share_directory('e116')
    config_file = os.path.join(pkg_share, 'config', 'e116.yaml')
    
    gap_follow_node = Node(
            package='e116',
            executable='gap_follow', # matches entry-point in setup.py
            name='gap_follw',
            output='screen',
            parameters=[config_file]
        )
        
#    OLED_node = Node(
#            package='e116',
#            executable='e116_OLED', # matches entry-point in setup.py
#            name='e116_OLED',
#            output='screen',
#            parameters=[config_file]
#        )
        
    racecar_node= Node(
            package='e116',
            executable='e116_racecar',
            name='e116_racecar',
            output='screen',
            parameters=[config_file]
        )
        
    return LaunchDescription([
        #FrontendLaunchDescriptionSource(yml_launch_file),
        #IncludeLaunchDescription(
        #        YAMLLaunchDescriptionSource(yml_launch_file)
        #        ),
#        OLED_node,
        racecar_node,
        gap_follow_node,
    ])
