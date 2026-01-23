#!/usr/bin/env python3
"""WSGI entry point for Terrascan - optimized for production"""

import os

# Run setup on import (once per worker)
from setup_configs import setup_system_configs
setup_system_configs()

# Create the app
from web.app import create_app
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
