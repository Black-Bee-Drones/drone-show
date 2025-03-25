import rclpy
from rclpy.node import Node
from std_msgs.msg import Int16
from geometry_msgs.msg import Twist
from turtlesim.srv import Spawn, Kill


class TurtleGestureController(Node):

    def __init__(self) -> None:
        super().__init__("turtle_gesture_controller")

        # Create a publisher for turtle movement
        self.cmd_vel_pub = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)

        # Create a subscription to the hand gesture topic
        self.create_subscription(
            Int16, "/bebop/hands_action", self._moviment_callback, 10
        )

        # Track action state
        self.action_counter: int = 0
        self.previous_action: int = 0
        self.current_action: int = 0
        self.already_sent: bool = False

        # Define continuous and single actions for turtlesim
        self.continuous_actions: dict[int, tuple[str, callable]] = {
            -1: ("Stop", self._stop),
            2: ("Move Up", lambda: self._move_turtle(0.0, 1.0)),  # Sobe
            3: ("Move Down", lambda: self._move_turtle(0.0, -1.0)),  # Desce
            4: ("Move Left", lambda: self._move_turtle(-1.0, 0.0)),  # Esquerda
            5: ("Move Right", lambda: self._move_turtle(1.0, 0.0)),  # Direita
            11: (
                "Move Backward",
                lambda: self._move_turtle(-1.0, 0.0),
            ),  # Anda pra trás
            12: (
                "Move Forward",
                lambda: self._move_turtle(1.0, 0.0),
            ),  # Anda pra frente
            13: ("Rotate Clockwise", self._rotate_clockwise),  # Yaw Horário
            14: (
                "Rotate Counterclockwise",
                self._rotate_counterclockwise,
            ),  # Yaw Anti-Horário
        }

        self.single_actions: dict[int, tuple[str, callable]] = {
            1: ("Spawn New Turtle", self._spawn_turtle),
            6: ("Kill Turtle", self._kill_turtle),
            10: ("Clear Traces", self._clear_traces),
            15: ("Reset Turtle", self._reset_turtle),
        }

    def _move_turtle(self, linear_x: float, linear_y: float) -> None:
        """
        Move the turtle in a specific direction.

        :param linear_x: Movement along x-axis
        :param linear_y: Movement along y-axis
        """
        twist = Twist()
        twist.linear.x = linear_x
        twist.linear.y = linear_y
        self.cmd_vel_pub.publish(twist)

    def _stop(self) -> None:
        """Stop the turtle's movement"""
        twist = Twist()
        twist.linear.x = 0.0
        twist.linear.y = 0.0
        twist.angular.z = 0.0
        self.cmd_vel_pub.publish(twist)

    def _rotate_clockwise(self) -> None:
        """Rotate the turtle clockwise"""
        twist = Twist()
        twist.angular.z = -1.0
        self.cmd_vel_pub.publish(twist)

    def _rotate_counterclockwise(self) -> None:
        """Rotate the turtle counterclockwise"""
        twist = Twist()
        twist.angular.z = 1.0
        self.cmd_vel_pub.publish(twist)

    def _spawn_turtle(self) -> None:
        """Spawn a new turtle at a random location"""
        spawn_client = self.create_client(Spawn, "/spawn")

        if not spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().error("Spawn service not available")
            return

        request = Spawn.Request()
        request.x = 5.0  # Default x position
        request.y = 5.0  # Default y position
        request.name = f"turtle{self.action_counter}"

        future = spawn_client.call_async(request)
        future.add_done_callback(self._spawn_turtle_callback)

        self.action_counter += 1

    def _spawn_turtle_callback(self, future):
        """Callback for spawn service"""
        try:
            response = future.result()
            self.get_logger().info(f"Spawned turtle: {response.name}")
        except Exception as e:
            self.get_logger().error(f"Error spawning turtle: {e}")

    def _kill_turtle(self) -> None:
        """Kill the last spawned turtle"""
        if self.action_counter > 0:
            kill_client = self.create_client(Kill, "/kill")

            if not kill_client.wait_for_service(timeout_sec=1.0):
                self.get_logger().error("Kill service not available")
                return

            request = Kill.Request()
            request.name = f"turtle{self.action_counter - 1}"

            future = kill_client.call_async(request)
            future.add_done_callback(self._kill_turtle_callback)

            self.action_counter -= 1

    def _kill_turtle_callback(self, future):
        """Callback for kill service"""
        try:
            future.result()
            self.get_logger().info("Turtle killed successfully")
        except Exception as e:
            self.get_logger().error(f"Error killing turtle: {e}")

    def _clear_traces(self) -> None:
        """Clear the traces of the turtle"""
        clear_client = self.create_client(Kill, "/clear")

        if not clear_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().error("Clear service not available")
            return

        request = Kill.Request()
        clear_client.call_async(request)
        self.get_logger().info("Cleared turtle traces")

    def _reset_turtle(self) -> None:
        """Reset the turtle to its initial state"""
        reset_client = self.create_client(Kill, "/reset")

        if not reset_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().error("Reset service not available")
            return

        request = Kill.Request()
        reset_client.call_async(request)
        self.get_logger().info("Reset turtle")

    def _moviment_callback(self, msg: Int16) -> None:
        """
        Callback function for the gesture recognizer node.

        :param msg (Int16): The message received from the gesture recognizer node.
        """
        self.previous_action = self.current_action
        self.current_action = msg.data

        # Similar to the original implementation, add a small delay to prevent spam
        from time import time

        if self.previous_action == self.current_action and self.previous_action != 0:
            if not hasattr(self, "start_time") or self.start_time is None:
                self.start_time = time()
        else:
            self.start_time = None
            self.already_sent = False

        if (
            hasattr(self, "start_time")
            and self.start_time is not None
            and time() - self.start_time >= 0.5
        ):
            try:
                # Check continuous actions first
                action_name, action_func = self.continuous_actions.get(
                    self.current_action, ("Unknown", None)
                )
                if action_func:
                    self.get_logger().info(f"Action: {action_name}")
                    action_func()

                # Then check single actions
                action_name, action_func = self.single_actions.get(
                    self.current_action, ("Unknown", None)
                )
                if action_func and not self.already_sent:
                    self.get_logger().info(f"Action: {action_name}")
                    action_func()
                    self.already_sent = True
            except Exception as e:
                self.get_logger().error(f"{e}")


def main(args=None):
    rclpy.init(args=args)

    controller = TurtleGestureController()

    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        pass
    finally:
        controller.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
