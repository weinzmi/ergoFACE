from .version import __version__
from .watt import Load

# if somebody does "from ergoFACE import *", this is what they will
# be able to access:
__all__ = [
    'rpm',
    'pwm',
]
