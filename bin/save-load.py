#! /usr/bin/env python
import sys
import _mypath

import drinkz

from drinkz.db import save_db, load_db

def main(args):
   filename = args[1]
	
   save_db(filename)
   load_db(filename)

if __name__ == '__main__':
   main(sys.argv)