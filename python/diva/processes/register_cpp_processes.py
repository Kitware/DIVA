import os

import diva


def get_cpp_path():
    module_path = os.path.dirname(os.path.abspath(diva.__file__))
    return os.path.join(module_path, "lib", "processes")
