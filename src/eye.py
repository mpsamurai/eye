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
import json
import redis
import cv2
import numpy as np

try:
    PI_CAMERA = True
    from picamera.array import PiRGBArray
    from picamera import PiCamera
except ImportError:
    PI_CAMERA = False
### from neochi.neochi import settings
### from neochi.eye import caches

from neochi.core.dataflow.data import eye


class Capture:
    def __init__(self, shape, rotation):
        # self._state = cache_server.state
        # self._image = cache_server.image
        self._shape = shape
        self._rotation = rotation
        self._frame = None

    def capture(self):
        ret, frame = self._capture()
        return ret, frame

    def _capture(self):
        raise NotImplementedError

    # TODO: Delete following commented code
    # @property
    # def state(self):
    #     return self._state.get()
    #
    # @property
    # def image(self):
    #     return self._state.get()
    #

    # def cache(self):
    #     if self._frame is not None:
    #         self._image.set(self._frame)


# TODO: Need to update
class CvCapture(Capture):
    def __init__(self, shape, rotation):
        super().__init__(shape, rotation)
        self._cap = cv2.VideoCapture(0)

    def _capture(self):
        ret, frame = self._cap.read()
        if ret and frame is not None:
            self._frame = cv2.cvtColor(cv2.resize(frame, tuple(self._shape)), cv2.COLOR_BGR2RGB)
        return ret, frame

    def release(self):
        self._cap.release()


class PiCapture(Capture):
    def __init__(self, shape, rotation):
        super().__init__(shape, rotation)
        self._camera = PiCamera(resolution=shape)
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


def start_capture(shape):
    """
    :param image_size:
    :param fps[float]:
    :return image: captured image. array(image_size,3)
    """
    print('START CAPTURE.')
    if not PI_CAMERA:
        print("PC_CAMERA:")  # TODO:Need to update
        cap = CvCapture(shape, 0)
        # return cap.capture()
        return 0, np.zeros([shape[0], shape[1]])
    else:
        ### cap = PiCapture(caches.server, settings.eye_settings.get()['shape'], 90)
        print("PI_CAMERA")

        cap = PiCapture(shape, 90)
        return cap
        # return cap.capture()


def get_img_size(eye_state):
    if eye_state.value is not None:
        image_size_dict = json.loads(eye_state.value)
    else:
        image_size_dict = {"image_size": {"width": 90, "height": 90}}

    width = image_size_dict["image_size"]["width"]
    height = image_size_dict["image_size"]["height"]
    image_size = [width, height]

    return image_size


if __name__ == "__main__":
    # Local var
    fps = 0.5

    # Redis Connect
    r = redis.StrictRedis("redis", 6379, db=0)
    ###r = redis.StrictRedis("raspberrypi.local", 6379, db=0)
    eye_image = eye.Image(r)
    eye_state = eye.State(r)

    # Receive image size
    img_size = get_img_size(eye_state)

    cap = start_capture(img_size)

    i = 0
    while True:
        i = i + 1
        print(i)

        img_size = get_img_size(eye_state)

        # Get Image
        bool_cap, captured_img = cap.capture()
        print(bool_cap)

        print("captured_img:", captured_img)

        # Transmit
        ndarray_img = np.array(captured_img, dtype=np.int32)
        # TODO: Remove following debugging comment
        # print("ndarray_img type:", type(ndarray_img))
        # print("ndarray_img:", ndarray_img)
        # print("ndarray_img_shape:", ndarray_img.shape)
        # print("ndarray_img:", ndarray_img.tostring().decode('utf-8'))

        # 暫定対応。ndarray_imgが128を越えるとeye_image.valueのByteへのdecode時にエラーする
        # DataTypeが更新されたら削除する
        print("max of ndarray:", ndarray_img.max())
        ndarray_img_filt = np.where(ndarray_img < 127, ndarray_img, 127)
        print("max of ndarray_filtered:", ndarray_img_filt.max())

        try:
            eye_image.value = ndarray_img_filt
        except:
            print('error')

        time.sleep(1. / fps)
