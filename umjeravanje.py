#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 18 12:21:15 2015

@author: DHMZ-Milic
"""

import sys
import os
from PyQt4 import QtGui
from app.control import kontroler

def main():
    """Pokretac aplikacije"""
    aplikacija = QtGui.QApplication(sys.argv)
    workingFolder = os.path.dirname(__file__)
    runner = kontroler.Kontroler()
    runner.set_workingFolder(workingFolder)
    sys.exit(aplikacija.exec_())

if __name__ == '__main__':
    main()