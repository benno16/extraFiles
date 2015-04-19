PYTHON_CHERRYPY_VERSION = 3.6.0
PYTHON_CHERRYPY_SOURCE = cherrypy-3.6.0.tar.gz
PYTHON_CHERRYPY_SITE = https://github.com/benno16/extraFiles/blob/master/package/sources
PYTHON_CHERRYPY_LICENSE = BSD-3c
PYTHON_CHERRYPY_LICENSE_FILES = LICENSE
PYTHON_CHERRYPY_SETUP_TYPE = setuptools

$(eval $(python-package))