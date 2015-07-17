# -*- coding: utf-8 -*-
"""
Created on Tue May 12 10:05:56 2015

@author: DHMZ-Milic
"""
import logging
import numpy as np
import pandas as pd
#from app.model.konfig_klase import UKonfig


class RacunUmjeravanja(object):
    """
    Klasa za racunanje parametara umjeravanja.
    """
    def __init__(self, cfg):
        logging.debug('start inicijalizacije RacunUmjeravanja')
        self.generalConfig = cfg
        self.konfig = None
        self.data = None
        self.stupac = 0
        self.reset_results()  # reset membera sa rezultatima na None
        logging.debug('kraj inicijalizacije RacunUmjeravanja')

    def set_konfig(self, cfg):
        """setter konfiga za racunanje"""
        self.konfig = cfg
        msg = 'konfig postavljen, config={0}'.format(str(type(cfg)))
        logging.debug(msg)

    def set_data(self, frejm):
        """
        setter pandas datafrejma podataka za racunanje
        """
        self.data = frejm
        msg = 'frejm sa podacima postavljen. frejm={0}'.format(str(type(frejm)))
        logging.debug(msg)
        logging.debug(str(frejm))

    def set_stupac(self, x):
        """
        Index stupca s kojim racunamo podatke.
        """
        self.stupac = x

    def reset_results(self):
        """
        Reset membera koji sadrze rezultate na defaultnu pocetnu vrijednost
        prije racunanja.
        """
        self.rezultat = None
        self.prilagodbaA = None
        self.prilagodbaB = None
        self.slope = None
        self.offset = None
        logging.debug('All result members reset to None')

    def dohvati_slajs_tocke(self, tocka, stupac):
        """
        Funkcija za dohvacanje slajsa podataka iz ciljanog frejma
        Tocka je jedna od definiranih u konfig objektu
        stupac je integer redni broj stupca s kojim racunamo
        """
        start = tocka.startIndeks
        end = tocka.endIndeks
        zanemari = tocka.brojZanemarenih
        return self.data.iloc[start+zanemari:end, stupac]

    def racunaj(self):
        """
        Glavna funkcija racuna sve parametre umjeravanja. Nakon postavljanja
        konfiga i podataka u objekt, pozovi ovu metoda za racunanje.
        """
        if isinstance(self.data, pd.core.frame.DataFrame):
            testFrejm = len(self.data) > 0
        else:
            testFrejm = False
        #testKonfig = isinstance(self.konfig, UKonfig)
        testKonfig = False #TODO!
        if testFrejm and testKonfig:
            self.reset_results()
            if self.konfig.testLinearnosti is True:
                tocke = self.konfig.tocke
                self.racunaj_vrijednosti_umjeravanja_za_listu_tocaka(tocke)
            else:
                tocke = self.konfig.tocke[:2]
                self.racunaj_vrijednosti_umjeravanja_za_listu_tocaka(tocke)

    def racunaj_vrijednosti_umjeravanja_za_listu_tocaka(self, tocke):
        """
        Racunanje parametara umjeravanja sa provjerom linearnosti.
        Funkcija sprema rezultate u membere:
        -->self.rezultat
            frejm sa rezultatima
        -->self.prilagodbaA
            slope prilagodbe
        -->self.prilagodbaB
            offset prilagodbe
        -->self.slope
            slope dobiven regresijom na pravac metodom najmanjh kvadrata
        -->self.offset
            offset dobiven regresijom na pravac metodom najmanjih kvadrata
        """
        # napravi indekse i stupce za rezultantni frejm
        indeks = [str(tocka) for tocka in tocke]
        columns = ['cref',
                   'c',
                   'delta',
                   'sr',
                   'r',
                   'Cr-cg',
                   'cg(cr-cg)/cr',
                   'ufz',
                   'ufm',
                   'ucr',
                   'ucz',
                   'UR']
        # stvaranje output frejma za tablicu
        self.rezultat = pd.DataFrame(columns=columns, index=indeks)
        for tocka in tocke:
            # Redosljed racunanja je bitan jer funkcije "ispod" ovise o
            # rezulatima funkcija "iznad".
            row = str(tocka)
            self.rezultat.loc[row, 'cref'] = self._izracunaj_cref(tocka)
            self.rezultat.loc[row, 'c'] = self._izracunaj_c(tocka)
            self.rezultat.loc[row, 'delta'] = self._izracunaj_delta(tocka)
            self.rezultat.loc[row, 'sr'] = self._izracunaj_sr(tocka)
        # racun za slope i offset
        if self.konfig.testLinearnosti is True:
            self.slope, self.offset = self._izracunaj_regresijske_koef()
        # racun koeficijenata funkcije prilagodbe
        self.prilagodbaA, self.prilagodbaB = self._izracunaj_prilagodbu()
        for tocka in tocke:
            row = str(tocka)
            if self.konfig.testLinearnosti is True:
                self.rezultat.loc[row, 'r'] = self._izracunaj_r(tocka)
            self.rezultat.loc[row, 'Cr-cg'] = self._izracunaj_step1(tocka)
            self.rezultat.loc[row, 'cg(cr-cg)/cr'] = self._izracunaj_step2(tocka)
            self.rezultat.loc[row, 'ufz'] = self._izracunaj_ufz(tocka)
            self.rezultat.loc[row, 'ufm'] = self._izracunaj_ufm(tocka)
            self.rezultat.loc[row, 'ucr'] = self._izracunaj_ucr(tocka)
            self.rezultat.loc[row, 'ucz'] = self._izracunaj_ucz(tocka)
            self.rezultat.loc[row, 'UR'] = self._izracunaj_UR(tocka)

    def _izracunaj_cref(self, tocka):
        """
        Racunanje cref, za datu tocku umjeravanja.
        """
        value = tocka.crefFaktor * self.konfig.raspon
        return value

    def _izracunaj_c(self, tocka):
        """
        Racunanje c, za izabranu tocku umjeravanje i stupac u podacima.
        stupac je integer vrijednost indeksa stupca u ulaznom pandas
        datafrejmu.
        """
        podaci = list(self.dohvati_slajs_tocke(tocka, self.stupac))
        return np.average(podaci)

    def _izracunaj_delta(self, tocka):
        """
        Racunanje razlike c i cref.
        """
        c = self.rezultat.loc[str(tocka), 'c']
        cref = self.rezultat.loc[str(tocka), 'cref']
        return c-cref

    def _izracunaj_sr(self, tocka):
        """
        Racunanje stdev za tocku,
        """
        podaci = list(self.dohvati_slajs_tocke(tocka, self.stupac))
        return np.std(podaci, ddof=1)

    def _izracunaj_regresijske_koef(self):
        """
        Racunanje slope i offset
        """
        x = list(self.rezultat.loc['TOCKA2':'TOCKA5', 'cref'])
        y = list(self.rezultat.loc['TOCKA2':'TOCKA5', 'c'])
        line = np.polyfit(x, y, 1)
        slope = line[0]
        offset = line[1]
        return slope, offset

    def _izracunaj_prilagodbu(self):
        """
        Racunanje koeficijenata funkcije prilagodbe
        """
        cref1 = self.rezultat.loc['TOCKA1', 'cref']
        c1 = self.rezultat.loc['TOCKA1', 'c']
        c2 = self.rezultat.loc['TOCKA2', 'c']
        A = cref1/(c1-c2)
        B = c1 / A
        return A, B

    def _izracunaj_r(self, tocka):
        if str(tocka) == 'TOCKA1':
            return np.NaN
        elif str(tocka) == 'TOCKA2':
            c = self.rezultat.loc[str(tocka), 'c']
            cref = self.rezultat.loc[str(tocka), 'cref']
            return abs(c - (cref * self.slope + self.offset))
        else:
            c = self.rezultat.loc[str(tocka), 'c']
            cref = self.rezultat.loc[str(tocka), 'cref']
            return abs(c - (cref * self.slope + self.offset)) / cref

    def _izracunaj_step1(self, tocka):
        """
        Funkcija racuna --> Cr - cg
        """
        Cr = self.konfig.cCRM
        cg = self.rezultat.loc[str(tocka), 'cref']
        return Cr-cg

    def _izracunaj_step2(self, tocka):
        """
        Funkcija racuna --> cg(cr-cg)/cr
        """
        cg = self.rezultat.loc[str(tocka), 'cref']
        zagrada = self.rezultat.loc[str(tocka), 'Cr-cg']
        Cr = self.konfig.cCRM
        return cg*zagrada/Cr

    def _izracunaj_ufz(self, tocka):
        value = self.rezultat.loc[str(tocka), 'cg(cr-cg)/cr']
        dilucija = str(self.konfig.izabranaDilucija)
        try:
            U = float(self.generalConfig.get_konfig_element(dilucija, 'MFC_NUL_PLIN_U'))
            return value * U
        except AttributeError as err:
            print(str(err))
            return np.NaN

    def _izracunaj_ufm(self, tocka):
        value = self.rezultat.loc[str(tocka), 'cg(cr-cg)/cr']
        dilucija = str(self.konfig.izabranaDilucija)
        try:
            U = float(self.generalConfig.get_konfig_element(dilucija, 'MFC_KAL_PLIN_U'))
            return value * U
        except AttributeError as err:
            print(str(err))
            return np.NaN

    def _izracunaj_ucr(self, tocka):
        sljedivost = self.konfig.sCRM
        cref = self.rezultat.loc[str(tocka), 'cref']
        return sljedivost*cref/200

    def _izracunaj_ucz(self, tocka):
        zrak = str(self.konfig.izabraniCistiZrak)
        komponenta = str(self.konfig.izabranaKomponenta)
        e1 = self.rezultat.loc[str(tocka), 'Cr-cg']
        e2 = 2 * float(self.generalConfig.get_konfig_element(zrak, komponenta))
        e3 = self.konfig.cCRM
        value = e1 * e2 / e3 / np.sqrt(3)
        return value

    def _izracunaj_UR(self, tocka):
        ufz = self.rezultat.loc[str(tocka), 'ufz']
        ufm = self.rezultat.loc[str(tocka), 'ufm']
        ucr = self.rezultat.loc[str(tocka), 'ucr']
        ucz = self.rezultat.loc[str(tocka), 'ucz']
        value = 2 * np.sqrt(ufz**2+ufm**2+ucr**2+ucz**2+(2*ucz)**2)
        return value

    def provjeri_ponovljivost_stdev_u_nuli(self):
        zrak = str(self.konfig.izabraniCistiZrak)
        komponenta = str(self.konfig.izabranaKomponenta)

        value = self.rezultat.loc['TOCKA2', 'sr']
        norm = 2 * float(self.generalConfig.get_konfig_element(zrak, komponenta))

        if value < norm:
            msg = 'vrijednost={0} , dopusteno odstupanje={1}, Dobro'.format(str(value), str(norm))
            return msg
        else:
            msg = 'vrijednost={0} , dopusteno odstupanje={1}, Lose'.format(str(value), str(norm))
            return msg

    def provjeri_ponovljivost_stdev_za_vrijednost(self):
        komponenta = str(self.konfig.izabranaKomponenta)
        value = self.rezultat.loc['TOCKA1', 'sr']
        cref = self.rezultat.loc['TOCKA1', 'cref']
        e1 = float(self.generalConfig.get_konfig_element(komponenta, 'rz'))
        norm = 0.01 * (e1) * cref
        if value < norm:
            msg = 'vrijednost={0} , dopusteno odstupanje={1}, Dobro'.format(str(value), str(norm))
            return msg
        else:
            msg = 'vrijednost={0} , dopusteno odstupanje={1}, Lose'.format(str(value), str(norm))
            return msg

    def provjeri_odstupanje_od_linearnosti_u_nuli(self):
        value = self.rezultat.loc['TOCKA2', 'r']
        komponenta = str(self.konfig.izabranaKomponenta)
        norm = float(self.generalConfig.get_konfig_element(komponenta, 'rz'))
        if value <= norm:
            msg = 'vrijednost={0} , dopusteno odstupanje={1}, Dobro'.format(str(value), str(norm))
            return msg
        else:
            msg = 'vrijednost={0} , dopusteno odstupanje={1}, Lose'.format(str(value), str(norm))
            return msg


    def provjeri_maksimalno_relativno_odstupanje_od_linearnosti(self):
        r = list(self.rezultat.loc['TOCKA3':'TOCKA5', 'r'])
        najveciR = max(r)
        value = 100 * (najveciR)
        komponenta = str(self.konfig.izabranaKomponenta)
        norm = float(self.generalConfig.get_konfig_element(komponenta, 'rmax'))
        if value <= norm:
            msg = 'vrijednost={0} , dopusteno odstupanje={1}, Dobro'.format(str(value), str(norm))
            return msg
        else:
            msg = 'vrijednost={0} , dopusteno odstupanje={1}, Lose'.format(str(value), str(norm))
            return msg


class ProvjeraKonvertera(object):
    """
    kalkulator za provjeru konvertera
    """
    def __init__(self, cfg):
        logging.debug('start inicijalizacije ProvjeraKonvertera')
        self.generalConfig = cfg
        self.konfig = None
        self.data = None
        self.stupacNO = 1
        self.stupacNOX = 0
        self.reset_results()  # reset membera sa rezultatima na None
        logging.debug('kraj inicijalizacije ProvjeraKonvertera')

    def set_konfig(self, cfg):
        """setter konfiga za racunanje"""
        self.konfig = cfg
        msg = 'konfig postavljen, config={0}'.format(str(type(cfg)))
        logging.debug(msg)

    def set_data(self, frejm):
        """
        setter pandas datafrejma podataka za racunanje
        """
        self.data = frejm
        msg = 'frejm sa podacima postavljen. frejm={0}'.format(str(type(frejm)))
        logging.debug(msg)
        logging.debug(str(frejm))

    def reset_results(self):
        """
        Reset membera koji sadrze rezultate na defaultnu pocetnu vrijednost
        prije racunanja.
        """
        self.rezultat = None
        self.ec1 = None
        self.ec2 = None
        self.ec3 = None
        self.ec = None
        logging.debug('All result members reset to None')

    def set_stupac_NO(self, ind):
        """ setter stupca frejma, NO"""
        self.stupacNO = ind

    def set_stupac_NOX(self, ind):
        """ setter stupca frejma, NOx"""
        self.stupacNOX = ind

    def racunaj(self):
        """
        racunanje provjere konvertera
        """
        if isinstance(self.data, pd.core.frame.DataFrame):
            testFrejm = len(self.data) > 0
        else:
            testFrejm = False
        testKonfig = isinstance(self.konfig, UKonfig)
        if testFrejm and testKonfig:
            self.reset_results()
            tocke = self.konfig.Ktocke
            self.get_provjera_konvertera_za_listu_tocaka(tocke)

    def get_provjera_konvertera_za_listu_tocaka(self, tocke):
        """
        metoda za racunanje rezultata provjere konvertera
        """
        indeks = [str(tocka) for tocka in tocke]
        columns = ['c, R, NOx',
                   'c, R, NO2',
                   'c, NO',
                   'c, NOx']
        # stvaranje output frejma za tablicu
        self.rezultat = pd.DataFrame(columns=columns, index=indeks)
        for tocka in tocke:
            row = str(tocka)
            self.rezultat.loc[row, 'c, R, NOx'] = self._izracunaj_crNOX(tocka)
            self.rezultat.loc[row, 'c, R, NO2'] = self._izracunaj_crNO2(tocka)
            self.rezultat.loc[row, 'c, NO'] = self._izracunaj_cNO(tocka)
            self.rezultat.loc[row, 'c, NOx'] = self._izracunaj_cNOX(tocka)
            self._izracunaj_ec1()
            self._izracunaj_ec2()
            self._izracunaj_ec3()
            self._izracunaj_ec()

    def _izracunaj_crNOX(self, tocka):
        """
        popunjavanje tablice sa ref vrijednostima koncentracije NOX
        """
        if str(tocka) == 'KTOCKA3':
            return 0
        value = self.konfig.raspon / 2
        return value

    def _izracunaj_crNO2(self, tocka):
        """
        popunjavanje tablice sa ref vrijedsnotima koncentracije NO2
        """
        if str(tocka) == 'KTOCKA2':
            return self.konfig.cNOX50
        elif str(tocka) == 'KTOCKA5':
            return self.konfig.cNOX95
        else:
            return 0

    def dohvati_slajs_tocke(self, tocka, stupac):
        """
        Funkcija za dohvacanje slajsa podataka iz ciljanog frejma
        Tocka je jedna od definiranih u konfig objektu
        stupac je integer redni broj stupca s kojim racunamo
        """
        start = tocka.startIndeks
        end = tocka.endIndeks
        zanemari = tocka.brojZanemarenih
        return self.data.iloc[start+zanemari:end, stupac]

    def _izracunaj_cNO(self, tocka):
        """
        funkcija racuna cNO za zadanu tocku (average stabilnih vrijednosti)
        """
        podaci = list(self.dohvati_slajs_tocke(tocka, self.stupacNO))
        return np.average(podaci)

    def _izracunaj_cNOX(self, tocka):
        """
        funkcija racuna cNOX za zadanu tocku (average stabilnih vrijednosti)
        """
        podaci = list(self.dohvati_slajs_tocke(tocka, self.stupacNOX))
        return np.average(podaci)

    def _izracunaj_ec1(self):
        """funckija racuna ec1"""
        numerator = 1 -(self.rezultat.loc['KTOCKA4', 'c, NOx'] - self.rezultat.loc['KTOCKA5', 'c, NOx'])
        denominator = self.rezultat.loc['KTOCKA4', 'c, NO'] - self.rezultat.loc['KTOCKA5', 'c, NO']
        try:
            value = numerator / denominator
        except ZeroDivisionError:
            value = 'NaN'
        finally:
            self.ec1 = str(value)

    def _izracunaj_ec2(self):
        """funckija racuna ec2"""
        numerator = 1 -(self.rezultat.loc['KTOCKA1', 'c, NOx'] - self.rezultat.loc['KTOCKA2', 'c, NOx'])
        denominator = self.rezultat.loc['KTOCKA1', 'c, NO'] - self.rezultat.loc['KTOCKA2', 'c, NO']
        try:
            value = numerator / denominator
        except ZeroDivisionError:
            value = 'NaN'
        finally:
            self.ec2 = str(value)

    def _izracunaj_ec3(self):
        """funckija racuna ec3"""
        numerator = 1 -(self.rezultat.loc['KTOCKA5', 'c, NOx'] - self.rezultat.loc['KTOCKA6', 'c, NOx'])
        denominator = self.rezultat.loc['KTOCKA5', 'c, NO'] - self.rezultat.loc['KTOCKA6', 'c, NO']
        try:
            value = numerator / denominator
        except ZeroDivisionError:
            value = 'NaN'
        finally:
            self.ec3 = str(value)

    def _izracunaj_ec(self):
        """ funkcija vraca najmanji od svih ec-ova"""
        out = set([self.ec1, self.ec2, self.ec3])
        out.discard('NaN')
        out = [float(i) for i in list(out)]
        self.ec = str(min(out))
