# MIT License
#
# Copyright (c) 2019 Morning Project Samurai (MPS)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Based on Junya Kaneko
__author__ = 'Yutaro Kida'


import time
import cv2

try:
    PI_CAMERA = True
    from picamera.array import PiRGBArray
    from picamera import PiCamera
except ImportError:
    PI_CAMERA = False

from neochi.core.dataflow import data


class Capture:
    def __init__(self, size, rotation):
        self._size = size
        self._rotation = rotation
        self._frame = None

    def capture(self):
        ret, frame = self._capture()
        return ret, frame

    def _capture(self):
        raise NotImplementedError


class CvCapture(Capture):
    def __init__(self, size, rotation):
        super().__init__(size, rotation)
        self._cap = cv2.VideoCapture(0)

    def _capture(self):
        ret, frame = self._cap.read()
        if ret and frame is not None:
            self._frame = cv2.cvtColor(cv2.resize(frame, tuple(self._size)), cv2.COLOR_BGR2RGB)
        return ret, self._frame

    def release(self):
        self._cap.release()


class PiCapture(Capture):
    def __init__(self, size, rotation):
        super().__init__(size, rotation)
        self._camera = PiCamera(resolution=size)
        self._camera.rotation = self._rotation
        self._cap = PiRGBArray(self._camera)

    def _capture(self):
        self._camera.capture(self._cap, format='rgb', use_video_port=True)
        frame = self._cap.array
        if frame.shape is None:
            return False, frame
        self._cap.truncate(0)
        self._frame = frame
        return True, self._frame

    def release(self):
        self._camera.close()


def get_capture(size, rotation_pc=0, rotation_pi=90):
    """
    :param image_size:
    :param fps[float]:
    :return image: captured image. array(image_size,3)
    """
    print('START CAPTURE.')
    if not PI_CAMERA:
        print("PC_CAMERA:")
        return CvCapture(size, rotation_pc)
    else:
        print("PI_CAMERA")
        return PiCapture(size, rotation_pi)


def start_capture(redis_server, size, rotation_pc, rotation_pi, fps):
    image = data.eye.Image(redis_server)
    state = data.eye.State(redis_server)
    current_state = {'size': size, 'rotation_pc': rotation_pc, 'rotation_pi': rotation_pi, 'fps': fps}
    cap = None
    while True:
        start_time = time.time()
        if state.changed(current_state) or cap is None:
            current_state = state.value
            cap = get_capture(current_state['size'], current_state['rotation_pc'], current_state['rotation_pi'])
            fps = current_state['fps']
        captured, captured_image = cap.capture()
        if not captured:
            continue
        image.value = captured_image
        sleep_duration = 1. / fps - (time.time() - start_time)
        if sleep_duration > 0:
            time.sleep(sleep_duration)

