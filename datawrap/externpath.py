import sys
import os

# Add parent import capabilities
externdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'external'))
if externdir not in sys.path:
    sys.path.insert(0, externdir)
