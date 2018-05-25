import os
import sys

import gfhttpva
from gfhttpva import create_app
from gfhttpva import config
from gfhttpva.gfhttpva import TIMEZONE

sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                )
