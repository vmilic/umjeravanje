# -*- coding: utf-8 -*-
"""
Created on Tue May 12 10:05:56 2015

@author: DHMZ-Milic
"""
import logging
import numpy as np
import pandas as pd


class RacunUmjeravanja(object):
    """
    Klasa za racunanje parametara umjeravanja.
    """
    def __init__(self, cfg):
        logging.debug('start inicijalizacije RacunUmjeravanja')
        self.konfig = cfg  # konfig objekt sa podacima o tockama, postavkama...
        self.uredjaj = {}  # mapa sa podacima o uredjaju
        self.data = None  # pandas datafrejm sa usrednjenim podacima za racunanje
        self.linearnost = False  # provjera linearnosti boolean
        self.stupac = 0  #stupac frejma STRING
        self.opseg = 0  #opseg mjerenja
        self.cCRM = 0  # koncentracija CRM-a
        self.sCRM = 0  # sljedivost CRM-a
        self.dilucija = None  # izabrana dilucijska jedinica
        self.cistiZrak = None  # izabran generator cistog zraka
        self.reset_results()
        logging.debug('kraj inicijalizacije RacunUmjeravanja')

    def set_uredjaj(self, uredjaj):
        """
        Setter uredjaja (mape sa opisom mjerenja....)
        """
        self.uredjaj = uredjaj
        logging.info('Postavljene informacije o uredjaju')
        logging.debug(str(uredjaj))

    def set_data(self, frejm):
        """
        Setter pandas datafrejma podataka za racunanje (nisu 3 minutni srednjaci).
        """
        self.data = frejm
        logging.info('Postavljen frejm sa sirovim podacima.')
        logging.debug(str(frejm))

    def set_stupac(self, x):
        """
        Setter indeksa stupca s kojim racunamo podatke.
        """
        self.stupac = x
        msg = 'Postavljan stupac za racunanje, stupac={0}'.format(x)
        logging.info(msg)

    def set_linearnost(self, x):
        """
        Setter za provjeru linearnosti
        """
        self.linearnost = x
        msg = 'Postavljen check za provjeru linearnosti, provjera linearnosti={0}'.format(x)
        logging.info(msg)

    def set_opseg(self, x):
        """
        Setter opsega metode umjeravanja
        """
        self.opseg = x
        msg = 'Postavljen opseg mjerenja, opseg={0}'.format(x)
        logging.info(msg)

    def set_cCRM(self, x):
        """
        Setter koncentracije certificiranog referentnog materijala
        """
        self.cCRM = x
        msg = 'Postavljena koncentracija CRM, cCRM={0}'.format(x)
        logging.info(msg)

    def set_sCRM(self, x):
        """
        Setter sljedivosti certificiranog referentnog materijala
        """
        self.sCRM = x
        msg = 'Postavljena sljedivost CRM, sCRM={0}'.format(x)
        logging.info(msg)

    def set_dilucija(self, x):
        """
        Setter izabrane dilucijske jedinice
        """
        self.dilucija = x
        msg = 'Postavljena dilucijska jedinica, dilucija={0}'.format(x)
        logging.info(msg)

    def set_cistiZrak(self, x):
        """
        Setter izabranog generatora cistog zraka
        """
        self.cistiZrak = x
        msg = 'Postavljan generator cistog zraka, cistiZrak={0}'.format(x)
        logging.info(msg)

    def reset_results(self):
        """
        Reset membera koji sadrze rezultate na defaultnu pocetnu vrijednost
        prije racunanja.
        """
        self.rezultat = pd.DataFrame()
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
        cols = list(self.data.columns)
        ind = cols.index(self.stupac)
        start = min(tocka.indeksi)
        end = max(tocka.indeksi)
        siroviSlajs = self.data.iloc[start:end+1, ind]
        agregiraniSlajs = []
        for i in range(0, len(siroviSlajs), 3):
            s = siroviSlajs[i:i+3]
            if len(s) == 3:
                value = np.average(s)
                agregiraniSlajs.append(value)
        return agregiraniSlajs

    def provjeri_ispravnost_parametara(self):
        """
        Funkcija provjerava ispravnost parametara za racunanje umjeravanja.
        Funkcija vraca True ako sve valja, False inace
        """
        try:
            assert(isinstance(self.data, pd.core.frame.DataFrame)), 'Frejm nije pandas dataframe.'
            assert(len(self.data) > 0), 'Frejm nema podataka (prazan)'
            assert(len(self.konfig.umjerneTocke) >= 2), 'Zadano je manje od dvije tocke za umjeravanje'
            assert(self.stupac in list(self.data.columns)), 'Frejm nema trazeni stupac. stupac={0}'.format(self.stupac)
            assert(self.opseg is not None and self.opseg > 0), 'Opseg nije dobro definiran'
            assert(self.cCRM is not None and self.cCRM > 0), 'Koncentracija CRM nije dobro definirana'
            assert(self.sCRM is not None and self.sCRM >= 0), 'Sljedivost CRM nije dobro definirana'
            cf = [float(tocka.crefFaktor) for tocka in self.konfig.umjerneTocke]
            assert(0.0 in cf), 'Nedostaje ZERO tocka'
            assert(sum(cf) != 0.0), 'Nedostaje SPAN tocka'
            assert(self.dilucija is not None), 'Dilucijska jedinica nije izabrana'
            assert(self.cistiZrak is not None), 'Generator cistog zraka nije definiran'
            return True
        except (AssertionError, AttributeError, TypeError) as e:
            msg = ".".join(['Parametri za racunanje nisu ispravni',str(e)])
            logging.debug(msg, exc_info=True)
            return False

    def racunaj(self):
        """
        Glavna funkcija racuna sve parametre umjeravanja. Nakon postavljanja
        konfiga i podataka u objekt, pozovi ovu metoda za racunanje.
        """
        if self.provjeri_ispravnost_parametara():
            self.reset_results()
            if self.linearnost:
                self.racunaj_vrijednosti_umjeravanja_za_listu_tocaka(self.konfig.umjerneTocke)
            else:
                zero, span = self.pronadji_zero_span()
                tocke = [self.konfig.umjerneTocke[span], self.konfig.umjerneTocke[zero]]
                self.racunaj_vrijednosti_umjeravanja_za_listu_tocaka(tocke)

    def _izracunaj_cref(self, tocka):
        """
        Racunanje cref, za datu tocku umjeravanja.
        """
        try:
            value = tocka.crefFaktor * self.opseg
            return round(value, 3)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            return np.NaN

    def _izracunaj_c(self, tocka):
        """
        Racunanje c, za izabranu tocku umjeravanje i stupac u podacima.
        stupac je integer vrijednost indeksa stupca u ulaznom pandas
        datafrejmu.
        """
        try:
            podaci = list(self.dohvati_slajs_tocke(tocka, self.stupac))
            return round(np.average(podaci), 3)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            return np.NaN

    def _izracunaj_sr(self, tocka):
        """
        Racunanje stdev za tocku,
        """
        try:
            podaci = list(self.dohvati_slajs_tocke(tocka, self.stupac))
            return round(np.std(podaci, ddof=1), 3)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            return np.NaN

    def _izracunaj_regresijske_koef(self):
        """
        Racunanje slope i offset, samo ako je ukljucena opcija za provjeru linearnosti
        """
        try:
            if self.linearnost:
                x = list(self.rezultat.loc[:, 'cref'])
                y = list(self.rezultat.loc[:, 'c'])
                line = np.polyfit(x, y, 1)
                slope = round(line[0], 3)
                offset = round(line[1], 3)
                return slope, offset
            else:
                return np.NaN, np.NaN
        except Exception as err:
            logging.error(str(err), exc_info=True)
            return np.NaN, np.NaN

    def _izracunaj_prilagodbu(self):
        """
        Racunanje koeficijenata funkcije prilagodbe
        """
        try:
            zero, span = self.pronadji_zero_span()
            s = str(self.konfig.umjerneTocke[span])
            z = str(self.konfig.umjerneTocke[zero])
            cref1 = self.rezultat.loc[s, 'cref']
            c1 = self.rezultat.loc[s, 'c']
            c2 = self.rezultat.loc[z, 'c']
            A = round(cref1/(c1-c2), 3)
            B = round(c1 / A, 3)
            return A, B
        except Exception as err:
            logging.error(str(err), exc_info=True)
            return np.NaN, np.NaN

    def _izracunaj_r(self, tocka):
        """
        racunanje r za zadanu tocku.
        """
        try:
            if self.linearnost:
                zero, span = self.pronadji_zero_span()
                z = self.konfig.umjerneTocke[zero]
                if tocka == z:
                    c = self._izracunaj_c(tocka)
                    cref = self._izracunaj_cref(tocka)
                    return round(abs(c - (cref * self.slope + self.offset)),3)
                else:
                    c = self._izracunaj_c(tocka)
                    cref = self._izracunaj_cref(tocka)
                    return round(abs(c - (cref * self.slope + self.offset)) / cref,3)
            else:
                return np.NaN
        except Exception as err:
            logging.error(str(err), exc_info=True)
            return np.NaN

    def _izracunaj_ufz(self, tocka):
        """pomocna funkcija za racunanje U"""
        try:
            cref = self._izracunaj_cref(tocka)
            value = (cref * (self.cCRM - cref))/(self.cCRM)
            d = str(self.dilucija)
            U = float(self.konfig.get_konfig_element(d, 'MFC_NUL_PLIN_U'))
            return round(value * U, 3)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            return np.NaN

    def _izracunaj_ufm(self, tocka):
        """pomocna funkcija za racunanje U"""
        try:
            cref = self._izracunaj_cref(tocka)
            value = (cref * (self.cCRM - cref))/(self.cCRM)
            d = str(self.dilucija)
            U = float(self.konfig.get_konfig_element(d, 'MFC_KAL_PLIN_U'))
            return round(value * U, 3)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            return np.NaN

    def _izracunaj_ucr(self, tocka):
        """pomocna funkcija za racunanje U"""
        try:
            sljedivost = self.sCRM
            cref = self._izracunaj_cref(tocka)
            return round(sljedivost*cref/200, 3)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            return np.NaN

    def _izracunaj_ucz(self, tocka):
        """pomocna funkcija za racunanje U"""
        try:
            zrak = str(self.cistiZrak)
            komponenta = str(self.stupac)
            e1 = self.cCRM - self._izracunaj_cref(tocka)
            e2 = 2 * float(self.konfig.get_konfig_element(zrak, komponenta))
            e3 = self.cCRM
            value = e1 * e2 / e3 / np.sqrt(3)
            return round(value, 3)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            return np.NaN

    def _izracunaj_UR(self, tocka):
        """
        Racunanje UR
        """
        try:
            ufz = self._izracunaj_ufz(tocka)
            ufm = self._izracunaj_ufm(tocka)
            ucr = self._izracunaj_ucr(tocka)
            ucz = self._izracunaj_ucz(tocka)
            if np.isnan(ufz):
                return 'NaN'
            if np.isnan(ufm):
                return 'NaN'
            if np.isnan(ucr):
                return 'NaN'
            if np.isnan(ucz):
                return 'NaN'
            value = 2 * np.sqrt(ufz**2+ufm**2+ucr**2+ucz**2+(2*ucz)**2)
            return round(value, 3)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            return np.NaN

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
                   'sr',
                   'r',
                   'UR']
        # stvaranje output frejma za tablicu
        self.rezultat = pd.DataFrame(columns=columns, index=indeks)
        for tocka in tocke:
            # Redosljed racunanja je bitan jer funkcije "ispod" ovise o
            # rezulatima funkcija "iznad".
            row = str(tocka)
            self.rezultat.loc[row, 'cref'] = self._izracunaj_cref(tocka)
            self.rezultat.loc[row, 'c'] = self._izracunaj_c(tocka)
            self.rezultat.loc[row, 'sr'] = self._izracunaj_sr(tocka)

        # racun za slope i offset
        self.slope, self.offset = self._izracunaj_regresijske_koef()
        # racun koeficijenata funkcije prilagodbe
        self.prilagodbaA, self.prilagodbaB = self._izracunaj_prilagodbu()
        for tocka in tocke:
            row = str(tocka)
            self.rezultat.loc[row, 'r'] = self._izracunaj_r(tocka)
            self.rezultat.loc[row, 'UR'] = self._izracunaj_UR(tocka)

    def provjeri_ponovljivost_stdev_u_nuli(self):
        """
        provjera ponovljivosti (sr) pri koncentraciji 0
        """
        if len(self.rezultat) > 0:
            try:
                zero, span = self.pronadji_zero_span()
                value = self.rezultat.loc[str(self.konfig.umjerneTocke[zero]), 'sr']
                normMin = round(float(self.uredjaj['analitickaMetoda']['Srz']['min']), 3)
                norm = round(float(self.uredjaj['analitickaMetoda']['Srz']['max']), 3)
            except (TypeError, AttributeError, LookupError) as err1:
                logging.debug(str(err1), exc_info=True)
                return 'Uredjaj nema poststavke za ponovljivost stdev u nuli'
            if value < norm and value >= normMin:
                msg = 'vrijednost={0} , dopusteno odstupanje={1}, Dobro'.format(str(value), str(norm))
                return msg
            else:
                msg = 'vrijednost={0} , dopusteno odstupanje={1}, Lose'.format(str(value), str(norm))
                return msg
        else:
            return 'NaN'

    def provjeri_ponovljivost_stdev_za_vrijednost(self):
        """
        provjera ponovljivosti za zadanu koncentraciju c
        """
        if len(self.rezultat) > 0:
            try:
                zero, span = self.pronadji_zero_span()
                value = self.rezultat.loc[str(self.konfig.umjerneTocke[span]), 'sr']
                normMin = round(float(self.uredjaj['analitickaMetoda']['Srs']['min']), 3)
                norm = round(float(self.uredjaj['analitickaMetoda']['Srs']['max']), 3)
            except (TypeError, AttributeError, LookupError) as err1:
                logging.debug(str(err1), exc_info=True)
                return 'Uredjaj nema poststavke za ponovljivost stdev za span'
            if value < norm  and value >= normMin:
                msg = 'vrijednost={0} , dopusteno odstupanje={1}, Dobro'.format(str(value), str(norm))
                return msg
            else:
                msg = 'vrijednost={0} , dopusteno odstupanje={1}, Lose'.format(str(value), str(norm))
                return msg
        else:
            return 'NaN'

    def provjeri_odstupanje_od_linearnosti_u_nuli(self):
        """
        provjera odstupanja od linearnosti za koncentraciju 0
        """
        if len(self.rezultat) > 0 and self.linearnost:
            try:
                zero, span = self.pronadji_zero_span()
                value = self.rezultat.loc[str(self.konfig.umjerneTocke[zero]), 'r']
                normMin = round(float(self.uredjaj['analitickaMetoda']['rz']['min']), 3)
                norm = round(float(self.uredjaj['analitickaMetoda']['rz']['max']), 3)
            except (TypeError, AttributeError, LookupError) as err1:
                logging.debug(str(err1), exc_info=True)
                return 'Uredjaj nema poststavke za odstupanje od linearnosti u nuli'
            if value <= norm and value >= normMin:
                msg = 'vrijednost={0} , dopusteno odstupanje={1}, Dobro'.format(str(value), str(norm))
                return msg
            else:
                msg = 'vrijednost={0} , dopusteno odstupanje={1}, Lose'.format(str(value), str(norm))
                return msg
        else:
            return 'NaN'

    def provjeri_maksimalno_relativno_odstupanje_od_linearnosti(self):
        """
        max relativno odstupanje od linearnosti
        """
        if len(self.rezultat) > 0 and self.linearnost:
            try:
                r = list(self.rezultat.loc[:, 'r'])
                #ignore zero i span
                indZero, indSpan = self.pronadji_zero_span()
                r[indZero] = 0.0
                najveciR = max(r)
                value = 100 * (najveciR)
                normMin = round(float(self.uredjaj['analitickaMetoda']['rmax']['min']), 3)
                norm = round(float(self.uredjaj['analitickaMetoda']['rmax']['max']), 3)
            except (TypeError, AttributeError, LookupError) as err1:
                logging.debug(str(err1), exc_info=True)
                return 'Uredjaj nema poststavke za maksimalno odstupanje od linearnosti'
            if value <= norm and value >= normMin:
                msg = 'vrijednost={0} , dopusteno odstupanje={1}, Dobro'.format(str(value), str(norm))
                return msg
            else:
                msg = 'vrijednost={0} , dopusteno odstupanje={1}, Lose'.format(str(value), str(norm))
                return msg
        else:
            return 'NaN'

    def pronadji_zero_span(self):
        """
        Metoda pronalazi indekse za zero i span.

        Zero je prva tocka koja ima crefFaktor jednak 0.0
        Span je prva tocka sa crefFaktorom 0.8, a ako niti jedna tocka nema
        taj crefFaktor, onda se uzima ona sa najvecim crefFaktorom
        """
        cf = [float(tocka.crefFaktor) for tocka in self.konfig.umjerneTocke]
        zero = cf.index(0.0)
        if 0.8 in cf:
            span = cf.index(0.8)
        else:
            span = cf.index(max(cf))
        return zero, span



class ProvjeraKonvertera(object):
    """
    kalkulator za provjeru konvertera
    """
    def __init__(self, cfg):
        logging.debug('start inicijalizacije ProvjeraKonvertera')
        self.konfig = cfg
        self.data = pd.DataFrame(columns=['NOx', 'NO2', 'NO'])
        self.opseg = 0.0
        self.cnox50 = 0.0
        self.cnox95 = 0.0
        self.reset_results()
        logging.debug('kraj inicijalizacije ProvjeraKonvertera')

    def set_data(self, frejm):
        """
        setter pandas datafrejma podataka za racunanje
        """
        self.data = frejm
        msg = 'frejm sa podacima postavljen. frejm={0}'.format(str(type(frejm)))
        logging.info(msg)
        logging.debug(str(frejm))

    def set_opseg(self, x):
        """Setter opsega mjerenja za provjeru konvertera"""
        self.opseg = float(x)
        msg = 'Postavljen novi opseg za provjeru konvertera, opseg={0}'.format(self.opseg)
        logging.info(msg)

    def set_cnox50(self, x):
        """Setter cnox50 za provjeru konvertera"""
        self.cnox50 = float(x)
        msg = 'Postavljen cNOx50 za provjeru konvertera, value={0}'.format(self.cnox50)
        logging.info(msg)

    def set_cnox95(self, x):
        """Setter cnox50 za provjeru konvertera"""
        self.cnox95 = float(x)
        msg = 'Postavljen cNOx95 za provjeru konvertera, value={0}'.format(self.cnox95)
        logging.info(msg)

    def reset_results(self):
        """
        Reset membera koji sadrze rezultate na defaultnu pocetnu vrijednost
        prije racunanja.
        """
        self.rezultat = pd.DataFrame()
        self.ec1 = 'n/a'
        self.ec2 = 'n/a'
        self.ec3 = 'n/a'
        self.ec = 'n/a'
        logging.debug('All result members reset to "n/a"')

    def provjeri_parametre_prije_racunanja(self):
        """
        Funkcija provjerava ispravnost parametara za provjeru konvertera.
        Funkcija vraca True ako sve valja, False inace.
        """
        try:
            assert(self.konfig is not None), 'Konfig objekt nije dobro zadan'
            assert(isinstance(self.data, pd.core.frame.DataFrame)), 'Frejm nije pandas dataframe.'
            assert(len(self.data) > 0), 'Frejm nema podataka (prazan)'
            assert('NOx' in self.data.columns), 'Frejmu nedostaje stupac NOx'
            assert('NO' in self.data.columns), 'Frejmu nedostaje stupac NO'
            assert('NO2' in self.data.columns), 'Frejmu nedostaje stupac NO2'
            assert(len(self.konfig.konverterTocke) != 6), 'Za provjeru konvertera nuzno je tocno 6 tocaka. zadano ih je {0}'.format(len(self.konfig.konverterTocke))
            assert(self.opseg > 0), 'Opseg nije dobro zadan'
            assert(self.cnox50 > 0), 'cNOx50 nije dobro zadan'
            assert(self.cnox95 > 0), 'cNOx95 nije dobro zadan'
            return True
        except (AssertionError, AttributeError, TypeError) as e:
            msg = ".".join(['Parametri za racunanje nisu ispravni',str(e)])
            logging.debug(msg, exc_info=True)
            return False

    def racunaj(self):
        """
        racunanje provjere konvertera
        """
        if self.provjeri_parametre_prije_racunanja:
            self.reset_results()
            self.get_provjera_konvertera_za_listu_tocaka(self.konfig.konverterTocke)

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
        imena = [str(dot) for dot in self.konfig.konverterTocke]
        ind = imena.index(str(tocka))
        if ind == 2:
            return 0
        else:
            value = self.opseg / 2
            value = round(value, 3)
            return value

    def _izracunaj_crNO2(self, tocka):
        """
        popunjavanje tablice sa ref vrijedsnotima koncentracije NO2
        """
        imena = [str(dot) for dot in self.konfig.konverterTocke]
        ind = imena.index(str(tocka))
        if ind == 1:
            return round(float(self.cnox50), 3)
        elif ind == 4:
            return round(float(self.cnox95), 3)
        else:
            return 0

    def dohvati_slajs_tocke(self, tocka, stupac):
        """
        Funkcija za dohvacanje slajsa podataka iz ciljanog frejma
        Tocka je jedna od definiranih u konfig objektu
        stupac je integer redni broj stupca s kojim racunamo
        """
        columns = list(self.data.columns)
        ind = columns.index(stupac)
        start = min(tocka.indeksi)
        end = max(tocka.indeksi)
        siroviSlajs = self.data.iloc[start:end+1, ind]
        agregiraniSlajs = []
        for i in range(0, len(siroviSlajs), 3):
            s = siroviSlajs[i:i+3]
            if len(s) == 3:
                value = np.average(s)
                agregiraniSlajs.append(value)
        return agregiraniSlajs

    def _izracunaj_cNO(self, tocka):
        """
        funkcija racuna cNO za zadanu tocku (average stabilnih vrijednosti)
        """
        try:
            podaci = list(self.dohvati_slajs_tocke(tocka, 'NO'))
            return round(np.average(podaci), 3)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            return np.NaN

    def _izracunaj_cNOX(self, tocka):
        """
        funkcija racuna cNOX za zadanu tocku (average stabilnih vrijednosti)
        """
        try:
            podaci = list(self.dohvati_slajs_tocke(tocka, 'NOx'))
            return round(np.average(podaci), 3)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            return np.NaN

    def _izracunaj_ec1(self):
        """funckija racuna ec1"""
        numerator = 1 -(self.rezultat.iloc[3, 3] - self.rezultat.iloc[4, 3])
        denominator = self.rezultat.iloc[3, 2] - self.rezultat.iloc[4, 2]
        try:
            value = numerator / denominator
            value = round(float(value), 3)
            self.ec1 = str(value)
        except ZeroDivisionError:
            self.ec1 = 'n/a'

    def _izracunaj_ec2(self):
        """funckija racuna ec2"""
        numerator = 1 -(self.rezultat.iloc[0, 3] - self.rezultat.iloc[1, 3])
        denominator = self.rezultat.iloc[0, 2] - self.rezultat.iloc[1, 2]
        try:
            value = numerator / denominator
            value = round(float(value), 3)
            self.ec2 = str(value)
        except ZeroDivisionError:
            self.ec2 = 'n/a'

    def _izracunaj_ec3(self):
        """funckija racuna ec3"""
        numerator = 1 -(self.rezultat.iloc[4, 3] - self.rezultat.iloc[5, 3])
        denominator = self.rezultat.iloc[4, 2] - self.rezultat.iloc[5, 2]
        try:
            value = numerator / denominator
            value = round(float(value), 3)
            self.ec3 = str(value)
        except ZeroDivisionError:
            self.ec3 = 'n/a'

    def _izracunaj_ec(self):
        """ funkcija vraca najmanji od svih ec-ova"""
        out = set([self.ec1, self.ec2, self.ec3])
        out.discard('NaN')
        out = [float(i) for i in list(out)]
        self.ec = str(min(out))
