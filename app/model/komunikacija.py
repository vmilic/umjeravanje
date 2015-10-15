# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 09:18:27 2015

@author: DHMZ-Milic
"""
import datetime
import random
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
        self.stopValue = True
        self.sampleRate = 1 #sample rate u sekundama

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
        self.stopValue = False
        self.veza.otvori()
        try:
            while True:
                if self.stopValue == False:
                    podatak = self.dohvati_podatak()
                    self.emit(QtCore.SIGNAL('nova_vrijednost_od_veze(PyQt_PyObject)'),
                              podatak)
                    time.sleep(self.sampleRate)
                else:
                    break
        except Exception as err:
            logging.error(str(err), exc_info=True)
        finally:
            self.veza.zatvori()

    def stop_prikupljati_podatke(self):
        self.stopValue = True

    def dohvati_podatak(self):
        podatak = self.protokol.prikupi_podatke(self.veza)
        return podatak


class Protokol(object):
    def __init__(self, postavke=None):
        self.postavke = postavke

    def prikupi_podatke(self, veza):
        veza.posalji('neka naredba')
        podatak = veza.citaj()
        output = self.adaptiraj_rezultat(podatak)
        return output

    def adaptiraj_rezultat(self, podatak):
        t = podatak[0] #podatak o vremenu, datetime objekt
        x = str(podatak[1]) #podatak o vrijednosti

        value = x.split(sep=' ') #rastavi string, space je delimiter
        nplin = int(value[0][2:]) #ukupan broj plinova
        values = value[1:]
        output = {}
        for i in range(nplin):
            temp = values[0:6]
            plin = temp[0]
            value = temp[1]
            value = self.adapt_number(value)
            status = temp[2]
            fail = temp[3]
            instrumentId = temp[4]
            spare = temp[5]
            output[plin] = [t, plin, value, status, fail, instrumentId, spare]
            values = values[6:]
        return output

    def adapt_number(self, num):
        if num[0] == '+':
            p1 = 1
        else:
            p1 = -1
        if num[5] == '+':
            p2 = 1
        else:
            p2 = -1
        rezultat = (p1*int(num[1:5])/1000)*(10**(p2*int(num[6:])))
        return round(rezultat, 3)


class Veza(object):
    def __init__(self, postavke=None):
        self.postavke = postavke
        self.statusVeze = False
        # jedan kanal
        self.dummyData = ['MD01 051 +3724+00 42 00 400 000000',
                          'MD01 051 +5168-00 42 00 400 000000',
                          'MD01 051 +5612+00 42 00 400 000000',
                          'MD01 051 +5612+00 42 00 400 000000',
                          'MD01 051 +5612+00 42 00 400 000000',
                          'MD01 051 +4812+00 42 00 400 000000',
                          'MD01 051 +5316+00 42 00 400 000000',
                          'MD01 051 +5865+00 40 01 400 000000',
                          'MD01 051 +3865+00 40 01 400 000000',
                          'MD01 051 +5612+00 42 00 400 000000',
                          'MD01 051 +1544+01 40 05 400 000000',
                          'MD01 051 +1544+01 40 05 400 000000',
                          'MD01 051 +1544+01 40 05 400 000000',
                          'MD01 051 +1469+00 40 00 400 000000',
                          'MD01 051 +1623+00 40 00 400 000000']
        # tri kanala
        self.dummyData1 = [
            'MD03 200 +4100+02 40 00 123 000000 201 +3810+02 40 00 123 000000 202 +2500+02 40 00 123 000000',
            'MD03 200 +4300+02 40 00 123 000000 201 +3820+02 40 00 123 000000 202 +2600+02 40 00 123 000000',
            'MD03 200 +4300+02 40 00 123 000000 201 +3810+02 40 00 123 000000 202 +2500+02 40 00 123 000000',
            'MD03 200 +4200+02 40 00 123 000000 201 +3820+02 40 00 123 000000 202 +2500+02 40 00 123 000000',
            'MD03 200 +4300+02 40 00 123 000000 201 +3800+02 40 00 123 000000 202 +2500+02 40 00 123 000000',
            'MD03 200 +4200+02 40 00 123 000000 201 +3800+02 40 00 123 000000 202 +2600+02 40 00 123 000000',
            'MD03 200 +4100+02 40 00 123 000000 201 +3800+02 40 00 123 000000 202 +2300+02 40 00 123 000000',
            'MD03 200 +4030+02 40 00 123 000000 201 +3810+02 40 00 123 000000 202 +2200+02 40 00 123 000000',
            'MD03 200 +4020+02 40 00 123 000000 201 +3830+02 40 00 123 000000 202 +2200+02 40 00 123 000000',
            'MD03 200 +4010+02 40 00 123 000000 201 +3840+02 40 00 123 000000 202 +2100+02 40 00 123 000000']

    def is_open(self):
        return self.statusVeze

    def otvori(self):
        self.statusVeze = True

    def zatvori(self):
        self.statusVeze = False

    def citaj(self):
        t = datetime.datetime.now()
        value = random.choice(self.dummyData)
        #value = random.choice(self.dummyData1)
        return [t, value]

    def posalji(self, zahtjev):
        pass
