#!/usr/bin/python3
#
# Lazy loader for optional third-party packaging backends.
#
# PackMyPayload supports a number of output containers, each one backed by a
# different third party package. Importing all of them at module scope means a
# single uninstallable dependency makes the entire tool unusable - notably
# pyminizip, which ships no wheels and fails to build against modern
# setuptools, yet is only ever needed for password protected ZIPs.
#
# Every backend is therefore resolved on first use and the failure is reported
# against the format that needs it, together with the command to fix it.
#

import importlib

#
# format/feature name -> (module to import, pip requirement to suggest)
#
BACKENDS = {
    'zip-password' : ('pyminizip',  'pyminizip'),
    '7zip'         : ('py7zr',      'py7zr'),
    'iso'          : ('pycdlib',    'pycdlib'),
    'cabinet'      : ('cabarchive', 'cabarchive'),
}


class MissingDependency(Exception):
    '''Raised when an optional packaging backend is not installed.'''

    def __init__(self, feature, module, requirement, original = None):
        self.feature = feature
        self.module = module
        self.requirement = requirement
        self.original = original

        super().__init__(
            f'Support for "{feature}" requires the "{module}" package, which is not installed.\n'
            f'    Install it with:  pip install {requirement}'
        )


_cache = {}

def require(feature):
    '''
    Import and return the backend module backing `feature`.

    Raises MissingDependency with an actionable message when unavailable, so
    that callers can degrade one format instead of aborting the whole program.
    '''

    if feature not in BACKENDS:
        raise KeyError(f'Unknown packaging backend: {feature}')

    if feature in _cache:
        return _cache[feature]

    module, requirement = BACKENDS[feature]

    try:
        mod = importlib.import_module(module)

    except ImportError as e:
        raise MissingDependency(feature, module, requirement, e) from e

    _cache[feature] = mod
    return mod


def available(feature):
    '''Return True when `feature`'s backend can be imported.'''

    try:
        require(feature)
        return True
    except (MissingDependency, KeyError):
        return False
