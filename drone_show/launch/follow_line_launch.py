from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            Node(
                package="use_library",
                executable="use_library",
                name="pid_center_x",
                output="screen",
                parameters=[
                    {"kp": 5.0},
                    {"ki": 0.0},
                    {"kd": 0.1},
                    {"use_sample_time": False},
                    {"sample_time": 2},
                    {"derivative_on_measurement": False},
                    {"remove_ki_bump": False},
                    {"reset_windup": False},
                    {"pid_enabled": True},
                    {"cut_off_freq": 0},
                    {"out_min": -50},
                    {"out_max": 50},
                    {"control_value_topic": "/control_value_center_x"},
                    {"actual_state_topic": "/actual_state_center_x"},
                    {"set_point_topic": "/set_point_center_x"},
                    {"loop_freq": 10},
                ],
            ),
            Node(
                package="use_library",
                executable="use_library",
                name="pid_angle",
                output="screen",
                parameters=[
                    {"kp": 5.0},
                    {"ki": 0.0},
                    {"kd": 0.1},
                    {"use_sample_time": False},
                    {"sample_time": 2},
                    {"derivative_on_measurement": False},
                    {"remove_ki_bump": False},
                    {"reset_windup": False},
                    {"pid_enabled": True},
                    {"cut_off_freq": 0},
                    {"out_min": -50},
                    {"out_max": 50},
                    {"control_value_topic": "/control_value_angle"},
                    {"actual_state_topic": "/actual_state_angle"},
                    {"set_point_topic": "/set_point_angle"},
                    {"loop_freq": 10},
                ],
            ),
            Node(
                package="drone_show",
                executable="line_detector",
                name="line_detector",
                output="screen",
            ),
        ]
    )
