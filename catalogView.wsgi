import sys
path = '/var/www/html/catalogApp'
if path not in sys.path:
    sys.path.append(path)

import models

from catalogView import app as application
