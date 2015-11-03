# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 14:30:19 2015

@author: DHMZ-Milic
"""

import serial
import datetime

BYTESIZES = {5:serial.FIVEBITS,
             6:serial.SIXBITS,
             7:serial.SEVENBITS,
             8:serial.EIGHTBITS}

PARITIES = {'none':serial.PARITY_NONE,
            'even':serial.PARITY_EVEN,
            'odd':serial.PARITY_ODD,
            'mark':serial.PARITY_MARK,
            'space':serial.PARITY_SPACE}

STOPBITS = {1:serial.STOPBITS_ONE,
            1.5:serial.STOPBITS_ONE_POINT_FIVE,
            2:serial.STOPBITS_TWO}

class RS232Veza(object):
    def __init__(self):
        #veza
        self.connection = serial.Serial()

    def setup_veze(self,
                   port=None,
                   baudrate=19200,
                   bytesize=8,
                   parity='none',
                   stopbits=1,
                   timeout=1):
        """Otvaranje RS232 veze. Parametar postavke sadrzi podatke za konfiguraciju
        veze.
        --> port
            - string naziv serijskog porta
        --> baudrate
            - dopustene vrijednosti : [50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800,
                                       2400, 4800, 9600, 19200, 38400, 57600, 115200]
        --> bytesize
            - dopustene vrijednosti : [5, 6, 7, 8]
        --> parity
            - dopustene vrijednosti : ['none', 'odd', 'even', 'mark', 'space']
        --> stopbits
            - dopustene vrijednosti : [1, 1.5, 2]
        --> timeout
            - dopustene vrijednosti : None (blocking),  0 (non blocking), n sekundi (float)
        """
        bytesize = BYTESIZES[bytesize]
        stopbits = STOPBITS[stopbits]
        parity = PARITIES[parity]

        self.connection.setPort(port)
        self.connection.setBaudrate(baudrate)
        self.connection.setByteSize(bytesize)
        self.connection.setParity(parity)
        self.connection.setStopbits(stopbits)
        self.connection.setTimeout(timeout)
        self.connection.setWriteTimeout(timeout)

    def otvori_vezu(self):
        """ otvaranje veze """
        if not self.connection.isOpen():
            self.connection.open()

    def zatvori_vezu(self):
        """ zatvaranje veze"""
        if self.connection.isOpen():
            self.connection.close()

    def salji(self, data):
        """ slanje zahtjeva preko veze """
        if self.connection.isOpen():
            self.connection.write(data)

    def primi(self):
        """ zaprimanje zahtjeva preko veze. Ouptut je lista [poruka, vrijeme zaprimanja] """
        if self.connection.isOpen():
            data = self.connection.readline()
            dt = datetime.datetime.now()
            return [data, dt]
        else:
            return [None, None]
