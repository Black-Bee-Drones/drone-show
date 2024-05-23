import rclpy
from rclpy.node import Node
from rclpy.publisher import Publisher
from std_msgs.msg import Float32, Bool

import sys

from mirela_interfaces.msg import LineInfo
from drone_show.follow_line.line_detection_node import LineDetectionNode

from mirela_sdk.control.drone import Drone
from mirela_sdk.control.bebop.bebop_api import Bebop
from mirela_sdk.control.mavros.mavros_api import MavDrone


class FollowLine(Node):
    # Forward speed of the drone
    FORWARD_SPEED = 0.0

    def __init__(self, drone_type: str = "bebop") -> None:
        super().__init__("follow_line_node")

        # Setpoint values
        self.setpoint_center_x = Float32(data=LineDetectionNode.IMG_SIZE[0] / 2)
        self.setpoint_angle = Float32(data=0.0)

        # Actual values
        self.actual_state_center_x = Float32()
        self.actual_state_angle = Float32()

        # Control values
        self.control_value_center_x: float = 0.0
        self.control_value_angle: float = 0.0

        # Publishers
        self.pub_actual_state_center_x: Publisher = self.create_publisher(
            Float32, "/actual_state_center_x", 10
        )
        self.pub_actual_state_angle: Publisher = self.create_publisher(
            Float32, "/actual_state_angle", 10
        )
        self.pub_set_point_center_x: Publisher = self.create_publisher(
            Float32, "/set_point_center_x", 10
        )
        self.pub_set_point_angle: Publisher = self.create_publisher(
            Float32, "/set_point_angle", 10
        )

        # Subscribers
        self.sub_control_value_center_x = self.create_subscription(
            Float32, "/control_value_center_x", self.callback_control_center_x, 10
        )
        self.sub_control_value_angle = self.create_subscription(
            Float32, "/control_value_angle", self.callback_control_angle, 10
        )

        self.sub_line_state = self.create_subscription(
            LineInfo, "line_state", self.state_callback, 10
        )
        # self.sub_line_detect = self.create_subscription(
        #     Bool, "line_detect", self.callback_line_detect, 10
        # )

        # Setpoint initialization
        self.pub_set_point_center_x.publish(self.setpoint_center_x)
        self.pub_set_point_angle.publish(self.setpoint_angle)

        # Drone
        self.declare_parameter("drone_type", drone_type)
        self._init_drone(
            self.get_parameter("drone_type").get_parameter_value().string_value
        )

        self.control_activate = {
            "center_x": False,
            "angle": False,
        }

        self.get_logger().info("Follow Line Node init")

    def _init_drone(self, drone_type: str) -> None:
        """
        Initialize the drone object

        :param drone_type: str
            The type of the drone [bebop, mavros]

        :return: None
        """
        if drone_type == "bebop":
            self.drone = Bebop(node=self, driver=False)
        else:
            self.drone = MavDrone(node=self, driver=False)

    def state_callback(self, msg: LineInfo) -> None:
        self.actual_state_center_x.data = msg.center_x
        self.actual_state_angle.data = msg.angle

        self.pub_set_point_center_x.publish(self.setpoint_center_x)
        self.pub_set_point_angle.publish(self.setpoint_angle)

        self.pub_actual_state_center_x.publish(self.actual_state_center_x)
        self.pub_actual_state_angle.publish(self.actual_state_angle)

        self.apply_control()

    def callback_control_center_x(self, msg: Float32) -> None:
        self.control_value_center_x = msg.data
        self.control_activate["center_x"] = True

    def callback_control_angle(self, msg: Float32) -> None:
        self.control_value_angle = msg.data
        self.control_activate["angle"] = True

    def apply_control(self) -> None:

        linear_y = angular_z = 0.0

        if self.should_apply_control("center_x", self.control_value_center_x, 0.025):
            linear_y = self.control_value_center_x
            self.control_activate["center_x"] = False

        if self.should_apply_control("angle", self.control_value_angle, 0.1, 10.0):
            angular_z = self.control_value_angle
            self.control_activate["angle"] = False

        self.drone.offboard_velocity(
            linear_x=self.FORWARD_SPEED,
            linear_y=linear_y,
            linear_z=0.0,
            angular_z=angular_z,
        )

        # self.get_logger().info(f"linear y: {linear_y}, angular_z:{angular_z}")

    def should_apply_control(
        self,
        controller: str,
        effort: float,
        low_threshold: float = 0.1,
        high_threshold: float = 1.0,
    ) -> Bool:
        return (
            self.control_activate[controller]
            and abs(effort) >= low_threshold
            and abs(effort) <= high_threshold
        )


def main(args=None) -> None:
    rclpy.init(args=args)

    follow_line = FollowLine()

    try:
        rclpy.spin(follow_line)
    except KeyboardInterrupt:
        follow_line.destroy_node()
        rclpy.shutdown()
        sys.exit(0)


if __name__ == "__main__":
    main()
