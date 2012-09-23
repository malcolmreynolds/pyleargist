from distutils.core import setup, Extension
import sys, os

version = file('VERSION.txt').read().strip()

setup(name='pyleargist',
      version=version,
      description="GIST Image descriptor for scene recognition",
      long_description=file('README.txt').read(),
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords=('image-processing computer-vision scene-recognition'),
      author='Olivier Grisel',
      author_email='olivier.grisel@ensta.org',
      url='http://www.bitbucket.org/ogrisel/pyleargist/src/tip/',
      license='GPL',
      package_dir={'': 'src'},
      packages=['leargist'],
      ext_modules=[
          Extension(
              'leargist._gist', [
                  'lear_gist/standalone_image.c',
                  'lear_gist/gist.c',
              ],
              libraries=['m', 'fftw3f'],
              extra_compile_args=['-DUSE_GIST', '-DSTANDALONE_GIST'],
          ),
      ],
      )
