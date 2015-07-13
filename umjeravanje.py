# -*- coding: utf-8 -*-
"""
Created on Mon May 18 12:21:15 2015

@author: DHMZ-Milic
"""
import sys
import logging
import configparser
from PyQt4 import QtGui
from app.view import display


def main():
    """Aplication starter"""
    logformat = '{levelname}:::{asctime}:::{module}:::{funcName}:::{message}'
    logging.basicConfig(level=logging.INFO,
                        format=logformat,
                        style='{')
    config = configparser.ConfigParser()
    try:
        config.read('umjeravanje_konfig.cfg')
    except OSError:
        logging.error('Error prilikom citanja konfiga', exc_info=True)
        raise SystemExit('Pogreska prilikom ucitavanja konfiguracije.')
    aplikacija = QtGui.QApplication(sys.argv)
    mainwindow = display.GlavniProzor(cfg=config)
    mainwindow.show()
    sys.exit(aplikacija.exec_())

if __name__ == '__main__':
    main()
