import rclpy
from rclpy.node import Node
from time import time
from mirela_sdk.control.bebop.bebop_api import Bebop
from mirela_sdk.image_processing.aruco.aruco_detect import Aruco
from mirela_sdk.image_processing.camera.image_handler import ImageHandler


class ArucoController(Node):
    def __init__(self):
        super().__init__("aruco_controller")

        self.bebop = Bebop(self, driver=False)
        self.aruco = Aruco(5, 20)
        self.img = ImageHandler(self, "/bebop/camera/image_raw", self.run, "Aruco detection")

        self.currentID = None
        self.previousID = None
        self.already_sent = False
        self.t_start = None

        self.continuous_actions: dict[int, tuple[str, callable]] = {
            0: ("Frente", lambda: self.bebop.offboard_velocity(0.3, 0.0, 0.0, 0.0)),
            600: ("Trás", lambda: self.bebop.offboard_velocity(-0.3, 0.0, 0.0, 0.0)),
            200: ("Direita", lambda: self.bebop.offboard_velocity(0.0, 0.3, 0.0, 0.0)),
            900: ("Esquerda", lambda: self.bebop.offboard_velocity(0.0, -0.3, 0.0, 0.0)),
            800: ("Sobe", lambda: self.bebop.offboard_velocity(0.0, 0.0, 0.3, 0.0)),
            700: ("Desce", lambda: self.bebop.offboard_velocity(0.0, 0.0, -0.3, 0.0)),
            

            
        }

        self.single_actions: dict[int, tuple[str, callable]] = {
            -9: ("Flip frente", lambda: self.bebop.flip(0)),
            -9: ("Flip direita", lambda: self.bebop.flip(2)),
            -8: ("Flip tras", lambda: self.bebop.flip(1)),
        }

        self.img.run()

    def run(self, img):

        cam = img
        _, id = self.aruco.detect(cam, True)
        print(id)

        if id is not None:
            self.previousID = self.currentID
            self.currentID = id

            if self.previousID == self.currentID and self.previousID is not None:
                if self.t_start is None:
                    self.t_start = time()

            else:
                self.already_sent = False
                self.t_start = None

            if self.t_start is not None and time() - self.t_start >= 0.5:
                action_name, action_func = self.continuous_actions.get(
                    self.currentID, ("Unknown", None)
                )
                if action_func:
                    self.get_logger().info(f"{action_name}")
                    action_func()

                action_name, action_func = self.single_actions.get(
                    self.currentID, ("Unknown", None)
                )
                if action_func and not self.already_sent:
                    action_func()
                    self.already_sent = True
        else:
            self.bebop.offboard_velocity(0.0, 0.0, 0.0, 0.0)

def main(args=None):
    rclpy.init(args=args)
    aruco_node = ArucoController()

    rclpy.spin(aruco_node)
    aruco_node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
