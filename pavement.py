import glob
import os
import os.path
import hashlib
import binascii

from paver.easy import task, cmdopts, needs, sh, info, error
from paver.tasks import BuildFailure
from paver.path import path
from Crypto.Random import get_random_bytes

try:
    import pkg_resources
    pkg_resources.get_distribution("ensconce_converters")
except:
    raise
    #raise BuildFailure("This pavement script must be run from within a configured virtual environment.")

from ensconce_converters.util.paver.tasks import *
