import os, sys

# get the current working directory
thisdir = os.path.dirname(__file__)

# build path to directory containing drinkz/ lib directory for imports
libdir = os.path.join(thisdir, '../')
libdir = os.path.abspath(libdir)

# add it into sys.path first, so that 'import' will find it first.
sys.path.insert(0, libdir)
