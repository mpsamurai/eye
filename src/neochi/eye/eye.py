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
import redis
import cv2


try:
    PI_CAMERA = True
    from picamera.array import PiRGBArray
    from picamera import PiCamera
except ImportError:
    PI_CAMERA = False

from neochi.core import settings
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


def start_capture(size, redis_server, rotation_pc=0, rotation_pi=90, fps=0.5):
    def get_next_size(current_state, current_size, default_size):
        if current_state is None or 'image_size' not in current_state:
            if current_size is None:
                return True, default_size
            else:
                return False, current_size
        else:
            if current_size is None or \
                    current_size[0] != current_state['image_size']['width'] or \
                    current_size[1] != current_state['image_size']['height']:
                return True, (current_state['image_size']['width'], current_state['image_size']['height'])
            else:
                return False, current_size

    def update_capture(current_cap, current_state, current_size, default_size):
        is_size_changed, current_size = get_next_size(current_state, current_size, default_size)
        if is_size_changed:
            if current_cap is not None:
                current_cap.release()
            current_cap = get_capture(current_size, rotation_pc, rotation_pi)
        return current_cap, current_size

    cap, current_size = None, None
    image, state = data.eye.Image(redis_server), data.eye.State(redis_server)
    while True:
        start_time = time.time()
        cap, current_size = update_capture(cap, state.value, current_size, size)
        captured, captured_image = cap.capture()
        if not captured:
            continue
        image.value = captured_image
        sleep_duration = 1. / fps - (time.time() - start_time)
        if sleep_duration > 0:
            time.sleep(sleep_duration)


if __name__ == "__main__":
    r = redis.StrictRedis(settings.REDIS_HOST, settings.REDIS_PORT, db=0)
    start_capture(settings.EYE_CAP_SIZE, r, fps=settings.EYE_CAP_FPS)
