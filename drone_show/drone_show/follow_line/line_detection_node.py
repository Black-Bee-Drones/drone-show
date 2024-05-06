#!/usr/bin/env python3

import sys
import os

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool

import cv2
from math import isnan
import numpy as np

from mirela_sdk.image_processing.camera.image_handler import ImageHandler
from mirela_interfaces.msg import LineInfo
from drone_show.follow_line.line_detector import LineDetector, RotatedRect


class LineDetectionNode(Node):
    # Constants for topic names
    LINE_STATE_TOPIC = "line_state"
    LINE_DETECTED_TOPIC = "line_detect"

    # Constants for image processing
    IMG_SIZE = (640, 480)
    DETECTION_ZONE = (600, 130)

    def __init__(self, line_color: str = None, image_source: str = None):
        super().__init__("line_detection_node")

        self.declare_parameter("line_color", "blue")
        self.declare_parameter("image_source", "webcam")

        if line_color is None:
            # Get detection parameters (line_color and image_source) from the command line
            line_color = (
                self.get_parameter("line_color").get_parameter_value().string_value
            )

        if image_source is None:
            image_source = (
                self.get_parameter("image_source").get_parameter_value().string_value
            )

        self.line_color = line_color
        self.image_source = image_source

        self.get_logger().info(
            f"\nDetection Node init: {self.line_color}, {self.image_source}"
        )

        # Initialize the line detector
        self.line_detector = LineDetector(
            color=self.line_color, estimation_method=RotatedRect
        )

        self.line_detected = Bool()
        self.line_detected_pub = self.create_publisher(
            Bool, self.LINE_DETECTED_TOPIC, 10
        )

        self.line_state_msg = LineInfo()
        self.center_x = self.angle = float()
        self.state_pub = self.create_publisher(LineInfo, self.LINE_STATE_TOPIC, 10)

        self.image_handler = ImageHandler(
            self,
            image_source,
            self.process_image,
        )
        self.image_handler.run()

    def process_image(self, img: np.ndarray):
        # Process the image and perform line detection
        try:
            cv2.resize(img, self.IMG_SIZE, dst=img)
            (
                img,
                self.center_x,
                self.angle,
            ) = self.line_detector.detect_line(img, region=self.DETECTION_ZONE)

            # Publish line states
            if not isnan(self.center_x) and not isnan(self.angle):
                # print(type(self.center_x), type(self.angle))
                self.line_state_msg.center_x = float(self.center_x)
                self.line_state_msg.angle = float(self.angle)
                self.state_pub.publish(self.line_state_msg)

                self.line_detected.data = True
            else:
                self.line_detected.data = False

            self.line_detected_pub.publish(self.line_detected)

            cv2.circle(
                img,
                (self.IMG_SIZE[0] // 2, self.IMG_SIZE[1] // 2),
                2,
                (0, 255, 0),
                3,
            )

            cv2.imshow("Detection", img)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.get_logger().info("Shutting down line detection node")
                self.cleanup()
                sys.exit(0)

        except Exception as e:
            self.get_logger().error(f"Error in line detection: {e}")

    def cleanup(self):
        self.image_handler.cleanup()
        cv2.destroyAllWindows()
        self.destroy_node()


def main(args=None):
    rclpy.init(args=args)

    detector = LineDetectionNode()

    try:
        # Start the line detection
        rclpy.spin(detector)
    except rclpy.exceptions.ROSInterruptException:
        pass
    finally:
        # Clean up resources before shutdown
        detector.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
