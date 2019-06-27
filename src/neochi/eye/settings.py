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


__author__ = 'Junya Kaneko <junya@mpsamurai.org>'


import os

REDIS_HOST = os.environ.get('NEOCHI_EYE_REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('NEOCHI_EYE_REDIS_PORT', '6379'))

SIZE = (int(os.environ.get('NEOCHI_EYE_CAP_WIDTH', '32')), int(os.environ.get('NEOCHI_EYE_CAP_HEIGHT', '32')))

ROTATION_PC = float(os.environ.get('NEOCHI_EYE_CAP_ROTATION_PC', '0'))
ROTATION_PI = float(os.environ.get('NEOCHI_EYE_CAP_ROTATION_PI', '90'))

FPS = float(os.environ.get('NEOCHI_EYE_CAP_FPS', '0.5'))
