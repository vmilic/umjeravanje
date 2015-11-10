# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 09:18:27 2015

@author: DHMZ-Milic
"""

import datetime
import time
import logging
from PyQt4 import QtCore

class KomunikacijskiObjekt(QtCore.QObject):
    """
    Objekt zaduzen za komunikaciju preko serial porta ili TCP veze.
    """
    def __init__(self, veza=None, protokol=None, parent=None):
        QtCore.QObject.__init__(self, parent=parent)
        self.veza = veza
        self.protokol = protokol
        self.sampleRate = 5 #sample rate u sekundama
        self.stopValue = True

    def set_veza(self, x):
        self.veza = x

    def get_veza(self):
        return self.veza

    def set_protokol(self, x):
        self.protokol = x

    def get_protokol(self):
        return self.protokol

    def set_sample_rate(self, value):
        self.sampleRate = value

    def start_prikupljati_podatke(self):
        try:
            self.stopValue = False
            self.veza.otvori_vezu()
            while self.stopValue == False:
                start = datetime.datetime.now()
                #posalji request za podacima
                upit = self.protokol.generiraj_upit()

                #sys.stdout.buffer.write(upit)
                self.veza.salji(upit)
                time.sleep(0.2)
                #prezumi podatke
                response=self.veza.primi()
                #sys.stdout.buffer.write(response[0])
                podatak = self.protokol.parse_rezultat(response)
                #emitiraj vrijednost podatka slusateljima
                self.emit(QtCore.SIGNAL('nova_vrijednost_od_veze(PyQt_PyObject)'),
                          podatak)
                delta = datetime.datetime.now() - start
                time.sleep(self.sampleRate - delta.total_seconds())
        except Exception as err:
            logging.error(str(err), exc_info=True)
            tekst = 'Problem sa prikupljanjem podataka.\n'+str(err)
            self.emit(QtCore.SIGNAL('problem_sa_prikupljanjem_podataka(PyQt_PyObject)'),
                      tekst)
        finally:
            self.veza.zatvori_vezu()

    def stop_prikupljati_podatke(self):
        self.stopValue = True
