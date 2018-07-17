import diva_python_utils
from vital.types import ImageContainer

exp = diva_python_utils.experiment()
exp.read_experiment('./etc/image_experiment.yml')
inp = exp.get_input()

while(inp.has_next_frame()):
  print('I am in the loop')
  frame = inp.get_next_frame()
  print('Frame width : '+str(frame.width()))
  print('Frame height : ' + str(frame.height()))
  bits = frame.asarray()



