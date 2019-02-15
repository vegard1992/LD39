import sys
from cx_Freeze import setup, Executable

addtional_mods = ['numpy.core._methods', 'numpy.lib.format']
setup(name='Notpong',
      version='0.1',
      description='xyz script',
      options = {'build_exe': {'includes': addtional_mods}},
      executables = [Executable('main.py')]
    )
