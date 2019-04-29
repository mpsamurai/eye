import time
import json
import redis
import cv2

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
        self.cache()
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
        print("PI_CAMERA:") # TODO:Need to update
        ### cap = CvCapture(caches.server, settings.eye_settings.get()['shape'], 0)
    else:
        ### cap = PiCapture(caches.server, settings.eye_settings.get()['shape'], 90)
        cap = PiCapture(shape, 90)
        return cap.capture()


if __name__ == "__main__":
    # Local var
    fps = 2

    # RedisとのConnect
    r = redis.StrictRedis("redis", 6379, db=0)
    eye_image = eye.Image(r)
    eye_state = eye.State(r)

    while True:
        # Receive
        image_size_dict = json.loads(eye_state.value)

        width = image_size_dict["image_size"]["width"]
        height = image_size_dict["image_size"]["height"]
        image_size = [width, height]

        # Get Image
        _, captured_image = start_capture(image_size)

        # Transmit
        eye_image.value = captured_image

        time.sleep(1. /fps)