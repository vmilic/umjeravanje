#!/usr/bin/python3
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

def setup_logging(file='applog.log', mode='a', lvl='INFO'):
    """
    Inicijalizacija loggera
    """
    DOZVOLJENI = {'DEBUG': logging.DEBUG,
                  'INFO': logging.INFO,
                  'WARNING': logging.WARNING,
                  'ERROR': logging.ERROR,
                  'CRITICAL': logging.CRITICAL}
    # lvl parametar
    if lvl in DOZVOLJENI:
        lvl = DOZVOLJENI[lvl]
    else:
        lvl = logging.ERROR
    #filemode
    if mode not in ['a', 'w']:
        mode = 'a'
    try:
        logging.basicConfig(level=lvl,
                            filename=file,
                            filemode=mode,
                            format='{levelname}:::{asctime}:::{module}:::{funcName}:::LOC:{lineno}:::{message}',
                            style='{')
    except Exception as err:
        print('Pogreska prilikom konfiguracije loggera.')
        print(err)
        raise SystemExit('Kriticna greska, izlaz iz aplikacije.')

def main():
    """Pokretac aplikacije"""
    config = configparser.ConfigParser()
    try:
        config.read('umjeravanje_konfig.cfg')
    except OSError:
        logging.error('Pogreska prilikom ucitavanja konfiguracije.', exc_info=True)
        raise SystemExit('Kriticna pogreska, izlaz iz aplikacije.')
    # dohvati postavke za logger
    filename = config.get('LOG_SETUP', 'file', fallback='applog.log')
    filemode = config.get('LOG_SETUP', 'mode', fallback='a')
    level = config.get('LOG_SETUP', 'lvl', fallback='INFO')
    #setup logging
    setup_logging(file=filename, mode=filemode, lvl=level)
    aplikacija = QtGui.QApplication(sys.argv)
    mainwindow = display.GlavniProzor(cfg=config)
    mainwindow.show()
    sys.exit(aplikacija.exec_())

if __name__ == '__main__':
    main()
