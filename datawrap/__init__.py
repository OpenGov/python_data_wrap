import glob
# Hack to get setup tools to correctly include all python files
__all__ = [module.split('.')[0] for module in glob.glob('*.py') if '__' not in module]
del glob
