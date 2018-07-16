import vital
import numpy as np
from PIL import Image as PILImage
from vital.types import ImageContainer
from vital.util import VitalPIL
from numpy.core.multiarray import array

import diva_python_utils

exp = diva_python_utils.experiment()
exp.read_experiment('C:/Programming/builds/diva-release/install/etc/image_experiment.yml')
inp = exp.get_input()

print('I am looping frames')
b = inp.has_next_frame()
print b
print('I am in the loop')
img = inp.get_next_frame()
print('Image width'+img.width)