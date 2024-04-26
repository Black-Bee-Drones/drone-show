import cvzone
import rclpy
from rclpy.node import Node
from cvzone.PoseModule import PoseDetector
from time import time
from mirela_sdk.image_processing.camera.image_handler import ImageHandler
from mirela_sdk.control.bebop.bebop_api import Bebop



class BicepsController(Node):

    def __init__(self, modelComplexity=1, detectionCon=0.6, trackCon=0.5):
        super().__init__("biceps_controller")

        self.bebop = Bebop(bebop_driver=False)
        
        self.img_handler = ImageHandler(self, 
                            "webcam", 
                            self.move_biceps, 
                            "Biceps detection", 0)
        
        self.detector = PoseDetector(modelComplexity=modelComplexity,
                            detectionCon=detectionCon,
                            trackCon=trackCon)
        
        self.acoes = {(0,0): ("Nada", lambda: self.bebop.offboard_velocity(0.0, 0.0, 0.0, 0.0)),
                      (1,0): ("Direito",lambda: self.bebop.flip(3)),
                      (0,1): ("Esquerdo", lambda: self.bebop.flip(2)),
                      (1,1): ("Toma esse double biceps", lambda: self.bebop.flip(0))}
        
        self.current_action = None
        self.previous_action = None
        self.time_start = None
        self.alreadySent = None
        
        self.img_handler.run()

        
    def move_biceps(self, img):

        self.img_detected = self.detector.findPose(img, True)
        lmList, _ = self.detector.findPosition(self.img_detected, False)

        if lmList:

            isClosedAngleR = self.check_angle(lmList, index1=12, index2=14, index3=16, target=300, offset=20)
            isClosedAngleL = self.check_angle(lmList, index1=11, index2=13, index3=15, target=60, offset=20)
            
            securityRight = self.check_angle(lmList, index1=12, index2=24, index3=16, target=350, offset=10)
            securityLeft = self.check_angle(lmList, index1=11, index2=23, index3=15, target=10, offset=10)
            
            pose = (isClosedAngleR and securityRight, isClosedAngleL and securityLeft)

            biceps, function = self.acoes.get(pose, ("Unknown", None))

            if function:

                self.previous_action = self.current_action
                self.current_action = biceps

                if self.current_action == self.previous_action and self.previous_action != None:
                    if self.time_start == None:
                        self.time_start = time()

                else:
                    self.time_start = None
                    self.alreadySent = False

                if  self.time_start is not None and time()-self.time_start > 0.5:
                    if not self.alreadySent:
                        function()
                        self.alreadySent = True

                cvzone.putTextRect(img, biceps, (20, 40), 2, 2, 
                                colorT=(0,0,0), colorR=(255,255,255))
                
    def check_angle(self, lmList, index1: int, index2: int, 
                       index3:int, target: int, offset: int) -> bool:
        
        angle, self.img_detected =  self.detector.findAngle(lmList[index1][0:2],
                                            lmList[index2][0:2],
                                            lmList[index3][0:2], 
                                            self.img_detected,
                                            (0, 0, 255), 10)
        
        check_angle = self.detector.angleCheck(angle, target, offset)
        
        return check_angle


def main(args = None):
    rclpy.init(args=args)
    biceps = BicepsController()
    rclpy.spin(biceps)

    biceps.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()


