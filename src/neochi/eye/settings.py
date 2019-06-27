import os

REDIS_HOST = os.environ.get('NEOCHI_EYE_REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('NEOCHI_EYE_REDIS_PORT', '6379'))

SIZE = (int(os.environ.get('NEOCHI_EYE_CAP_WIDTH', '32')), int(os.environ.get('NEOCHI_EYE_CAP_HEIGHT', '32')))

ROTATION_PC = float(os.environ.get('NEOCHI_EYE_CAP_ROTATION_PC', '0'))
ROTATION_PI = float(os.environ.get('NEOCHI_EYE_CAP_ROTATION_PI', '90'))

FPS = float(os.environ.get('NEOCHI_EYE_CAP_FPS', '0.5'))
