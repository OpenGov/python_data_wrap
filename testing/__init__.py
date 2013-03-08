import os
import glob
import sys

# Hack to get setup tools to correctly include all python files
__all__ = [module.split('.')[0] for module in glob.glob('*.py') if '__' not in module]
__all__.extend([os.path.split(module)[0] for module in glob.glob('*/__init__.py')])

# Add parent for datawrap import capabilities
sys.path.append(os.path.abspath(os.path.join(__file__, '..')))

del sys
del glob
del os
