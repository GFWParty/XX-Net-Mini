#!/usr/bin/env python
# coding:utf-8

import sys
import os
import re
import glob
import shutil

TEMPLATE1 = '''\
def __bootstrap__():
   global __bootstrap__, __loader__, __file__
   import pkg_resources, imp
   __file__ = pkg_resources.resource_filename(__name__,'%s')
   __loader__ = None; del __bootstrap__, __loader__
   imp.load_dynamic(__name__,__file__)
try:
   __bootstrap__()
except (ImportError, LookupError):
   raise ImportError('No module named %%s' %% __name__)
'''

TEMPLATE2 = '''\
def __bootstrap__():
   global __bootstrap__, __loader__, __file__
   import sysconfig, pkg_resources, imp
   __file__ = pkg_resources.resource_filename(__name__,'%s-%%s.so' %% sysconfig.get_platform().split('-')[-1])
   __loader__ = None; del __bootstrap__, __loader__
   imp.load_dynamic(__name__,__file__)
try:
   __bootstrap__()
except (ImportError, LookupError):
   raise ImportError('No module named %%s' %% __name__)
'''

TEMPLATE3 = '''\
def __bootstrap__():
   global __bootstrap__, __loader__, __file__
   import _memimporter, sys
   _memimporter.set_find_proc(lambda x: __loader__.get_data(r'%s%s' % (__loader__.prefix, x)))
   __file__ = r'%s%s.pyd' % (__loader__.prefix, __name__.split('.')[-1])
   mod = _memimporter.import_module(__loader__.get_data(__file__), 'init'+__name__.split('.')[-1], __name__, __file__)
   mod.__file__ = __file__
   mod.__loader__ = __loader__
   sys.modules[__name__] = mod
   del __bootstrap__, __loader__, __file__, _memimporter, sys
__bootstrap__()
'''

def main():
    for root, dirs, names in os.walk('.'):
        for name in names:
            if name.endswith(('.so', '.pyd')):
                fullname = os.path.join(root, name)
                sys.stderr.write(fullname+os.linesep)
                if name.endswith('.pyd'):
                    pyname = re.sub(r'\.[a-z]+$', '', name)
                    pycode = TEMPLATE3
                elif '-' not in name:
                    pyname = re.sub(r'\.[a-z]+$', '', name)
                    pycode = TEMPLATE1 % name
                else:
                    pyname = re.sub(r'\-[a-z\_0-9]+\.[a-z]+$', '', name)
                    pycode = TEMPLATE2 % pyname
                with open(os.path.join(root, pyname+'.py'), 'wb') as fp:
                    fp.write(pycode.encode())
                if os.path.basename(root) == pyname:
                    pycount = len(glob.glob(os.path.join(root, '*.py')))
                    pycount -= sum(1 if os.path.exists(os.path.join(root, x+'.py')) else 0 for x in ('__init__', pyname))
                    if pycount <= 0:
                        shutil.move(os.path.join(root, pyname+'.py'), os.path.join(root, '__init__.py'))


if __name__ == '__main__':
    main()
