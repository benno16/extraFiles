"""
This script runs the ModStorage application using a development server.
"""

from ModStorage import app

if __name__ == '__main__':
    app.run("0.0.0.0", 5010)
