import sys
import os 
import site
import tempfile
import socket
host = socket.gethostname()


if host == "testing-domain.edu": # testing 
    os.environ['ORACLE_HOME'] = '/path/to/oracle/instantclient_11_2'
    os.environ['TNS_ADMIN'] = '/path/to/oracle/instantclient_11_2'
elif host == "production-domain.edu": # production
    site.addsitedir('/path/to/virtualenv/lib/python2.6/site-packages')
    os.environ['ORACLE_HOME'] = '/path/to/oracle/instantclient_11_2'
    os.environ['TNS_ADMIN'] = '/path/to/oracle/instantclient_11_2'
    sys.path.append('/path/to/repo/transfer/')
else: # local
    os.environ['ORACLE_HOME'] = '/path/to/oracle/instantclient/instantclient_11_2'

# We defer to a DJANGO_SETTINGS_MODULE already in the environment. This breaks
# if running multiple sites in the same mod_wsgi process. To fix this, use
# mod_wsgi daemon mode with each site in its own daemon process, or use

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "transfer.settings")

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


