from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import Shutdown, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "image_source",
                default_value="webcam",
                description="Source of the image",
            ),
            DeclareLaunchArgument(
                "line_color",
                default_value="red",
                description="Color of the line to follow",
            ),
            DeclareLaunchArgument(
                "drone_type",
                default_value="bebop",
                description="Type of the drone",
            ),
            Node(
                package="use_library",
                executable="use_library",
                name="pid_center_x",
                output="screen",
                parameters=[
                    {"kp": 0.2},
                    {"ki": 0.0},
                    {"kd": 0.0},
                    {"use_sample_time": False},
                    {"sample_time": 2},
                    {"derivative_on_measurement": False},
                    {"remove_ki_bump": False},
                    {"reset_windup": False},
                    {"pid_enabled": False},
                    {"cut_off_freq": 0},
                    {"out_min": -1},
                    {"out_max": 1},
                    {"control_value_topic": "/control_value_center_x"},
                    {"actual_state_topic": "/actual_state_center_x"},
                    {"set_point_topic": "/set_point_center_x"},
                    {"loop_freq": 10},
                ],
                on_exit=Shutdown(),
            ),
            Node(
                package="use_library",
                executable="use_library",
                name="pid_angle",
                output="screen",
                parameters=[
                    {"kp": 0.2},
                    {"ki": 0.0},
                    {"kd": 0.0},
                    {"use_sample_time": False},
                    {"sample_time": 2},
                    {"derivative_on_measurement": False},
                    {"remove_ki_bump": False},
                    {"reset_windup": False},
                    {"pid_enabled": False},
                    {"cut_off_freq": 0},
                    {"out_min": -1},
                    {"out_max": 1},
                    {"control_value_topic": "/control_value_angle"},
                    {"actual_state_topic": "/actual_state_angle"},
                    {"set_point_topic": "/set_point_angle"},
                    {"loop_freq": 10},
                ],
                on_exit=Shutdown(),
            ),
            Node(
                package="drone_show",
                executable="line_detector",
                name="line_detector",
                output="screen",
                parameters=[
                    {"image_source": LaunchConfiguration("image_source")},
                    {"line_color": LaunchConfiguration("line_color")},
                ],
                on_exit=Shutdown(),
            ),
            Node(
                package="drone_show",
                executable="follow_line_controller",
                name="follow_controller_node",
                output="screen",
                parameters=[
                    {"drone_type": LaunchConfiguration("drone_type")},
                ],
                on_exit=Shutdown(),
            ),
        ]
    )
