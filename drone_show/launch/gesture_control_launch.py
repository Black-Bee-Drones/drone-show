from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, Shutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "image_source",
                default_value="webcam",
                description="Source of the image",
            ),
            Node(
                package="drone_show",
                executable="gesture_recognizer",
                name="recognizer",
                parameters=[{"image_source": LaunchConfiguration("image_source")}],
                on_exit=Shutdown(),
            ),
            Node(
                package="drone_show",
                executable="gesture_controller",
                name="controller",
                on_exit=Shutdown(),
            ),
            Node(
                package="mirela_sdk",
                executable="gui",
                name="gui",
                on_exit=Shutdown(),
            ),
        ]
    )
