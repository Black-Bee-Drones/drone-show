from setuptools import find_packages, setup
import os
from glob import glob

package_name = "drone_show"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (
            os.path.join("share", package_name, "launch"),
            glob(os.path.join("launch", "*launch.[pxy][yma]*")),
        ),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="samuel",
    maintainer_email="samuellimabraz@gmail.com",
    description="TODO: Package description",
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "gesture_recognizer = drone_show.hand_gesture.gesture_recognizer:main",
            "gesture_controller = drone_show.hand_gesture.gesture_controller:main",
            "frequency_controller = drone_show.note_frequency.frequency_controller:main",
            "note_recognizer = drone_show.note_frequency.note_recognizer:main",
            "aruco_controller = drone_show.aruco.aruco_controller:main",
            "biceps_controller = drone_show.biceps.biceps_controller:main",
        ],
    },
)
