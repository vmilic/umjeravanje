# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 14:30:38 2015

@author: DHMZ-Milic
"""


def checksum(string):
    """xor svih elemenata iterable objekta string, vraca integer"""
    c = 0
    for i in list(string):
        c=c^ord(i)
    return c


class Hessen(object):
    """Base class za Hessen tip protokola"""
    def __init__(self):
        self.naredba_get = 'DA'

    def generiraj_upit(self, device=None):
        """
        Formiranje zahtjeva za podacima. Ulaz je id komponente ili uredjaja.
        Output je pravilno formatiran upit koji se salje preko veze
        """
        raise NotImplemented

    def parse_rezultat(self, data):
        """
        Adaptiranje preuzetih podataka.
        Parametar data je lista sa 2 elementa --> [poruka, vrijeme zaprimanja poruke].
        Izlaz su pripremljeni podaci.
        """
        raise NotImplemented

    def adapt_number(self, num):
        """
        Adaptiranje koncentracije u float zaokruzen na 3 decimale

        +4523+01 --> 45.23
        """
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


class HessenText(Hessen):
    def __init__(self):
        Hessen.__init__(self)

    def generiraj_upit(self, device=None):
        """
        Metoda vraca pravilno slozeni zahtjev za podacima. Parametar
        device je 3 digit device ili gas ID
        """
        if device == None:
            msg = self.naredba_get
        else:
            msg = "".join([self.naredba_get, str(device)])
        return msg

    def parse_rezultat(self, data):
        """
        Metoda adaptira primljenu poruku od veze.
        Parametar data je lista sa 2 elementa --> [poruka, vrijeme zaprimanja poruke].
        Metoda vraca mapu gdje je kljuc ID plina (komponente) a vrijednosti su lista:
        [vrijeme, plinID, vrijednost, status bitovi, fail bitovi, instrumentID, spare bitovi]
        """
        poruka = data[0]
        vrijeme = data[1]
        output = self.adapt_poruku(poruka, vrijeme)
        return output

    def adapt_poruku(self, poruka, vrijeme):
        """
        metoda adaptira tekstualnu poruku u listu sa sljedecim elementima:

        [vrijeme, plinID, vrijednost, status bitovi, fail bitovi, instrumentID, spare bitovi]
        """
        poruka = poruka.split(sep=' ') #rastavi string, space je delimiter
        nplin = int(poruka[0][2:]) #ukupan broj plinova
        values = poruka[1:]
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
            output[plin] = [vrijeme, plin, value, status, fail, instrumentId, spare]
            values = values[6:]
        return output


class HessenBCC(Hessen):
    def __init__(self):
        Hessen.__init__(self)
        self.start = '\x02'
        self.end = '\x03'

    def generiraj_upit(self, device=None):
        """ Metoda vraca pravilno slozeni zahtjev za podacima. Parametar
        device je 3 digit device ili gas ID"""
        if device == None:
            msg = "".join([self.start, self.naredba_get, self.end])
        else:
            msg = "".join([self.start, self.naredba_get, str(device), self.end])
        #dodavanje <BCC> checksum
        output = msg + format(checksum(msg),'02x')
        return str.encode(output)

    def parse_rezultat(self, data):
        """
        Metoda adaptira primljenu poruku od veze.

        Parametar data je lista sa 2 elementa --> [poruka, vrijeme zaprimanja poruke].

        Metoda vraca mapu gdje je kljuc ID plina (komponente) a vrijednosti su lista:
        [vrijeme, plinID, vrijednost, status bitovi, fail bitovi, instrumentID, spare bitovi]
        """
        poruka = data[0]
        vrijeme = data[1]
        poruka = self._get_tekst_poruke(poruka)
        output = self.adapt_poruku(poruka, vrijeme)
        return output

    def _get_tekst_poruke(self, poruka):
        """metoda razdvaja poruku na dva elementa, tekst poruke i bcc te provjerava
        da li checksum odgovara. U slucaju loseg formata poruke ili ako checksum
        nije dobar raise ValueError"""
        poruka2=poruka.decode("utf-8")
        print("eee:"+poruka2)
        s = poruka2.find(self.start)
        e = poruka2.find(self.end)
        #razdvajanje na start i end dio
        if s != -1 and e != -1:
            msg = poruka2[s:e+1]
            bcc = int(poruka2[e+1:e+3], 16) #convert hex to int
        else:
            tekst = 'Krivo formatirana poruka : ' + poruka2
            raise ValueError(tekst)
        #provjera checksuma poruke
        check = checksum(msg)
        if check == bcc:
            pass
        else:
            tekst = 'Block Check Code poruke ne odgovara : poruka = {0} \n{1} != {2}'.format(poruka, bcc, check)
            raise ValueError(tekst)
        return msg

    def adapt_poruku(self, poruka, vrijeme):
        """
        metoda adaptira tekstualnu poruku u listu sa sljedecim elementima:

        [vrijeme, plinID, vrijednost, status bitovi, fail bitovi, instrumentID, spare bitovi]
        """
        poruka = poruka[1:-1] #makni <stx> i <etx> iz poruke
        poruka = poruka.split(sep=' ') #rastavi string, space je delimiter
        nplin = int(poruka[0][2:]) #ukupan broj plinova
        values = poruka[1:]
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
            output[plin] = [vrijeme, plin, value, status, fail, instrumentId, spare]
            values = values[6:]
        return output
