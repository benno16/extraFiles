"""
The flask application package.
"""

from flask import Flask
from flask_jsonrpc import JSONRPC

app = Flask(__name__)
jsonrpc = JSONRPC(app, '/api',enable_web_browsable_api=True)

import ModStorage.views
import ModStorage.api
import ModStorage.ModVizX2Api