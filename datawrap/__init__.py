import os
import glob
# Hack to get setup tools to correctly include all python files
__all__ = [module.split('.')[0] for module in glob.glob('*.py') if '__' not in module]
__all__.extend([os.path.split(module)[0] for module in glob.glob('*/__init__.py')])
del glob
del os