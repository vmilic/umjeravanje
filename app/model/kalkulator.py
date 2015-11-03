# -*- coding: utf-8 -*-
"""
Created on Tue May 12 10:05:56 2015

@author: DHMZ-Milic
"""
import logging
import numpy as np
import pandas as pd
from PyQt4 import QtCore


class RacunUmjeravanja(QtCore.QObject):
    """
    Klasa za racunanje parametara umjeravanja.
    """
    def __init__(self, doc=None, parent=None):
        QtCore.QObject.__init__(self, parent=parent)
        self.doc = doc #dokument sa podacima za racunanje
        self.reset_results()

    def reset_results(self):
        """
        Reset membera koji sadrze rezultate na defaultnu pocetnu vrijednost
        prije racunanja.
        """
        self.rezultat = self.doc.generiraj_nan_frejm_rezultata_umjeravanja()
        self.prilagodbaA = np.NaN
        self.prilagodbaB = np.NaN
        self.slope = np.NaN
        self.offset = np.NaN
        self.srz = ['', '', '', np.NaN, '', 'NE']
        self.srs = ['', '', '', np.NaN, '', 'NE']
        self.rz = ['', '', '', np.NaN, '', 'NE']
        self.rmax = ['', '', '', np.NaN, '', 'NE']
        logging.debug('All result members reset to np.NaN')

    def set_dokument(self, x):
        """Setter dokumenta u kalkulator"""
        self.doc = x

    def get_dokument(self):
        """Getter dokumenta iz kalkulatora"""
        return self.doc

    def dohvati_slajs_tocke(self, tocka):
        """
        Funkcija za dohvacanje slajsa podataka iz ciljanog frejma
        Tocka je jedna od definiranih u konfig objektu

        output je lista 3 minutno agregiranih vrijednosti podataka u slajsu
        """
        frejm = self.doc.get_siroviPodaci()
        cols = list(frejm.columns)
        ind = cols.index(self.doc.get_izabranoMjerenje())
        start = min(tocka.indeksi)
        end = max(tocka.indeksi)
        siroviSlajs = frejm.iloc[start:end+1, ind]
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
            frejm = self.doc.get_siroviPodaci()
            udots = self.doc.get_tockeUmjeravanja()
            mjerenje = self.doc.get_izabranoMjerenje()
            opseg = self.doc.get_opseg()
            cCRM = self.doc.get_koncentracijaCRM()
            sCRM = self.doc.get_sljedivostCRM()
            cf = [float(tocka.crefFaktor) for tocka in udots]
            negativniFaktori = [faktor for faktor in cf if faktor < 0]
            dilucija = self.doc.get_izabranaDilucija()
            zrak = self.doc.get_izabraniZrak()
            #provjere
            assert(isinstance(frejm, pd.core.frame.DataFrame)), 'Podaci nisu dobro zadani.'
            assert(len(frejm) > 0), 'Nema podataka.'
            assert(len(udots) >= 2), 'Zadano je manje od dvije tocke za umjeravanje.'
            assert(mjerenje in list(frejm.columns)), 'Podaci nemaju trazenu komponentu. komponenta={0}.'.format(str(mjerenje))
            assert(opseg is not None and opseg > 0), 'Opseg nije dobro definiran.'
            assert(cCRM is not None and cCRM > 0), 'Koncentracija CRM nije dobro definirana.'
            assert(sCRM is not None and sCRM >= 0), 'Sljedivost CRM nije dobro definirana.'
            assert(len(negativniFaktori) == 0), 'Barem jedan od cref Faktora je negativan.'
            assert(0.0 in cf), 'Nedostaje ZERO tocka.'
            assert(sum(cf) != 0.0), 'Nedostaje SPAN tocka.'
            assert(dilucija is not None), 'Dilucijska jedinica nije izabrana.'
            assert(zrak is not None), 'Generator cistog zraka nije izabran.'
            return True
        except Exception as e:
            msg = ". ".join(['Parametri za racunanje nisu ispravni',str(e)])
            logging.debug(msg, exc_info=True)
            return False

    def racunaj(self):
        """
        Glavna funkcija racuna sve parametre umjeravanja. Nakon postavljanja
        konfiga i podataka u objekt, pozovi ovu metoda za racunanje.
        """
        self.reset_results()
        if self.provjeri_ispravnost_parametara():
            tocke = self.doc.get_tockeUmjeravanja()
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
                   'U',
                   'c',
                   u'\u0394',
                   'sr',
                   'r']
        # stvaranje output frejma za tablicu
        self.rezultat = pd.DataFrame(columns=columns, index=indeks)
        # racun za slope i offset
        self.slope, self.offset = self._izracunaj_regresijske_koef()
        # racun koeficijenata funkcije prilagodbe
        self.prilagodbaA, self.prilagodbaB = self._izracunaj_prilagodbu()
        # racunanje parametara umjeravanja
        for tocka in tocke:
            row = str(tocka)
            self.rezultat.loc[row, 'cref'] = self._izracunaj_cref(tocka)
            self.rezultat.loc[row, 'c'] = self._izracunaj_c(tocka)
            self.rezultat.loc[row, u'\u0394'] = self._izracunaj_delta(tocka)
            self.rezultat.loc[row, 'sr'] = self._izracunaj_sr(tocka)
            self.rezultat.loc[row, 'r'] = self._izracunaj_r(tocka)
            self.rezultat.loc[row, 'U'] = self._izracunaj_UR(tocka)

        # provjera ispravnosti parametara umjeravanja u odnosu na normu
        self.srz = self._provjeri_ponovljivost_stdev_u_nuli()
        self.srs = self._provjeri_ponovljivost_stdev_za_vrijednost()
        self.rz = self._provjeri_odstupanje_od_linearnosti_u_nuli()
        self.rmax = self._provjeri_maksimalno_relativno_odstupanje_od_linearnosti()

    def _izracunaj_regresijske_koef(self):
        """
        Racunanje slope i offset linearne regresije.
        Koristi se np.linalg.lstsq

        #izbacena span vrijednost iz racunice
        """
        try:
            lin = self.doc.get_provjeraLinearnosti()
            udots = self.doc.get_tockeUmjeravanja()
            if lin:
                zero, span = self.pronadji_zero_span_tocke()
                dots = [tocka for tocka in udots if tocka != span]
                x = [self._izracunaj_cref(tocka) for tocka in dots]
                y = [self._izracunaj_c(tocka) for tocka in dots]
                # sastavljanje matrice koeficijenata linearnog sustava
                const = np.ones(len(x))
                A = np.vstack([x, const])
                A = A.T
                slope, offset = np.linalg.lstsq(A, y)[0]
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
            zero, span = self.pronadji_zero_span_tocke()
            crefSpan = self._izracunaj_cref(span)
            cSpan = self._izracunaj_c(span)
            cZero = self._izracunaj_c(zero)
            A = crefSpan / (cSpan - cZero)
            B = -cZero / A
            return A, B
        except Exception as err:
            logging.error(str(err), exc_info=True)
            return np.NaN, np.NaN

    def _izracunaj_cref(self, tocka):
        """
        Racunanje cref, za datu tocku umjeravanja.
        """
        try:
            opseg = self.doc.get_opseg()
            return tocka.crefFaktor * opseg
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
            lin = self.doc.get_provjeraLinearnosti()
            if not lin:
                zero, span = self.pronadji_zero_span_tocke()
                if tocka == zero or tocka == span:
                    podaci = list(self.dohvati_slajs_tocke(tocka))
                    return np.average(podaci)
                else:
                    return np.NaN
            else:
                podaci = list(self.dohvati_slajs_tocke(tocka))
                return np.average(podaci)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            return np.NaN

    def _izracunaj_delta(self, tocka):
        """
        Racunanje razlike izmjerene koncentracije i referentne vrijednosti
        """
        try:
            lin = self.doc.get_provjeraLinearnosti()
            if not lin:
                zero, span = self.pronadji_zero_span_tocke()
                if tocka == zero or tocka == span:
                    return self._izracunaj_c(tocka) - self._izracunaj_cref(tocka)
                else:
                    return np.NaN
            else:
                return self._izracunaj_c(tocka) - self._izracunaj_cref(tocka)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            return np.NaN

    def _izracunaj_sr(self, tocka):
        """
        Racunanje stdev za tocku
        """
        try:
            lin = self.doc.get_provjeraLinearnosti()
            if not lin:
                zero, span = self.pronadji_zero_span_tocke()
                if tocka == zero or tocka == span:
                    podaci = list(self.dohvati_slajs_tocke(tocka))
                    return np.std(podaci, ddof=1)
                else:
                    return np.NaN
            else:
                podaci = list(self.dohvati_slajs_tocke(tocka))
                return np.std(podaci, ddof=1)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            return np.NaN

    def _izracunaj_r(self, tocka):
        """
        racunanje r za zadanu tocku.
        """
        try:
            lin = self.doc.get_provjeraLinearnosti()
            if lin:
                zero, span = self.pronadji_zero_span_tocke()
                if tocka == span:
                    return np.NaN
                elif tocka == zero:
                    c = self._izracunaj_c(tocka)
                    cref = self._izracunaj_cref(tocka)
                    return abs(c - (cref * self.slope + self.offset))
                else:
                    c = self._izracunaj_c(tocka)
                    cref = self._izracunaj_cref(tocka)
                    if cref != 0:
                        return abs((c - (cref * self.slope + self.offset)) / cref)*100
                    else:
                        return np.NaN
            else:
                return np.NaN
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
                return np.NaN
            if np.isnan(ufm):
                return np.NaN
            if np.isnan(ucr):
                return np.NaN
            if np.isnan(ucz):
                return np.NaN
            value = 2 * np.sqrt(ufz**2+ufm**2+ucr**2+ucz**2+(2*ucz)**2)
            return value
        except Exception as err:
            logging.error(str(err), exc_info=True)
            return np.NaN

    def _izracunaj_ufz(self, tocka):
        """pomocna funkcija za racunanje U"""
        try:
            dilucija = self.doc.get_izabranaDilucija()
            cCRM = self.doc.get_koncentracijaCRM()
            cref = self._izracunaj_cref(tocka)
            value = (cref * (cCRM - cref))/(cCRM)
            U = float(self.doc.cfg.get_konfig_element(dilucija, 'MFC_NUL_PLIN_U'))
            return value * U
        except Exception as err:
            logging.error(str(err), exc_info=True)
            return np.NaN

    def _izracunaj_ufm(self, tocka):
        """pomocna funkcija za racunanje U"""
        try:
            dilucija = self.doc.get_izabranaDilucija()
            cCRM = self.doc.get_koncentracijaCRM()
            cref = self._izracunaj_cref(tocka)
            value = (cref * (cCRM - cref))/(cCRM)
            U = float(self.doc.cfg.get_konfig_element(dilucija, 'MFC_KAL_PLIN_U'))
            return value * U
        except Exception as err:
            logging.error(str(err), exc_info=True)
            return np.NaN

    def _izracunaj_ucr(self, tocka):
        """pomocna funkcija za racunanje U"""
        try:
            sljedivost = self.doc.get_sljedivostCRM()
            cref = self._izracunaj_cref(tocka)
            return sljedivost*cref/200
        except Exception as err:
            logging.error(str(err), exc_info=True)
            return np.NaN

    def _izracunaj_ucz(self, tocka):
        """pomocna funkcija za racunanje U"""
        try:
            cCRM = self.doc.get_koncentracijaCRM()
            sljedivost = self.doc.get_sljedivostCistiZrak()
            e1 = cCRM - self._izracunaj_cref(tocka)
            e3 = cCRM
            value = e1 * sljedivost / e3 / np.sqrt(3)
            return value
        except Exception as err:
            logging.error(str(err), exc_info=True)
            return np.NaN

    def _provjeri_ponovljivost_stdev_u_nuli(self):
        """
        provjera ponovljivosti (sr) u zero tocki

        rezultat je lista:
        [naziv,
        tocka norme,
        kratka oznaka,
        vrijednost,
        uvijet prihvatljivosti,
        ispunjeno]
        """
        try:
            uredjaji = self.doc.get_uredjaji()
            uredjaj = self.doc.get_izabraniUredjaj()
            jedinica = self.doc.get_mjernaJedinica()
            normMin = float(uredjaji[uredjaj]['analitickaMetoda']['Srz']['min'])
            normMax = float(uredjaji[uredjaj]['analitickaMetoda']['Srz']['max'])
            zero, span = self.pronadji_zero_span_tocke()
            value = self._izracunaj_sr(zero)
            prihvatljivost = " ".join(['<', str(normMax), jedinica])
            output = ['Ponovljivost standardne devijacije u nuli',
                      '9.5.1',
                      'S<sub>r,z</sub> =',
                      value,
                      prihvatljivost,
                      'DA']
            if value < normMax and value >= normMin:
                return output
            else:
                output[5] = 'NE'
                return output
        except Exception as err1:
            logging.debug(str(err1), exc_info=True)
            return ['', '', '', np.NaN, '', 'NE']

    def _provjeri_ponovljivost_stdev_za_vrijednost(self):
        """
        provjera ponovljivosti za zadanu koncentraciju c

        rezultat je lista:
        [naziv,
        tocka norme,
        kratka oznaka,
        vrijednost,
        uvijet prihvatljivosti,
        ispunjeno]
        """
        try:
            uredjaji = self.doc.get_uredjaji()
            uredjaj = self.doc.get_izabraniUredjaj()
            jedinica = self.doc.get_mjernaJedinica()
            normMin = float(uredjaji[uredjaj]['analitickaMetoda']['Srs']['min'])
            normMax = float(uredjaji[uredjaj]['analitickaMetoda']['Srs']['max'])
            zero, span = self.pronadji_zero_span_tocke()
            value = self._izracunaj_sr(span)
            prihvatljivost = " ".join(['<', str(normMax), jedinica])
            output = ['Ponovljivost standardne devijacije pri koncentraciji ct',
                      '9.5.1',
                      'S<sub>r,ct</sub> =',
                      value,
                      prihvatljivost,
                      'DA']
            if value < normMax and value >= normMin:
                return output
            else:
                output[5] = 'NE'
                return output
        except Exception as err1:
            logging.debug(str(err1), exc_info=True)
            return ['', '', '', np.NaN, '', 'NE']

    def _provjeri_odstupanje_od_linearnosti_u_nuli(self):
        """
        provjera odstupanja od linearnosti za koncentraciju 0

        rezultat je lista:
        [naziv,
        tocka norme,
        kratka oznaka,
        vrijednost,
        uvijet prihvatljivosti,
        ispunjeno]
        """
        try:
            uredjaji = self.doc.get_uredjaji()
            uredjaj = self.doc.get_izabraniUredjaj()
            jedinica = self.doc.get_mjernaJedinica()
            normMin = float(uredjaji[uredjaj]['analitickaMetoda']['rz']['min'])
            normMax = float(uredjaji[uredjaj]['analitickaMetoda']['rz']['max'])
            zero, span = self.pronadji_zero_span_tocke()
            value = self._izracunaj_r(zero)
            prihvatljivost = " ".join(['\u2264', str(normMax), jedinica])
            output = ['Odstupanje od linearnosti u nuli',
                      '9.6.2',
                      'r<sub>z</sub> =',
                      value,
                      prihvatljivost,
                      'DA']
            if value <= normMax and value >= normMin:
                return output
            else:
                output[5] = 'NE'
                return output
        except Exception as err1:
            logging.debug(str(err1), exc_info=True)
            return ['', '', '', np.NaN, '', 'NE']

    def _provjeri_maksimalno_relativno_odstupanje_od_linearnosti(self):
        """
        max relativno odstupanje od linearnosti

        rezultat je lista:
        [naziv,
        tocka norme,
        kratka oznaka,
        vrijednost,
        uvijet prihvatljivosti,
        ispunjeno]
        """
        try:
            udots = self.doc.get_tockeUmjeravanja()
            uredjaji = self.doc.get_uredjaji()
            uredjaj = self.doc.get_izabraniUredjaj()
            normMin = float(uredjaji[uredjaj]['analitickaMetoda']['rmax']['min'])
            normMax = float(uredjaji[uredjaj]['analitickaMetoda']['rmax']['max'])
            zero, span = self.pronadji_zero_span_tocke()
            dots = [tocka for tocka in udots if (tocka != zero and tocka != span)]
            r = [self._izracunaj_r(tocka) for tocka in dots]
            value = max(r)
            prihvatljivost = " ".join(['\u2264', str(normMax), '%'])
            output = ['Maksimalno relativno odstupanje od linearnosti',
                      '9.6.2',
                      'r<sub>z,rel</sub> =',
                      value,
                      prihvatljivost,
                      'DA']
            if value <= normMax and value >= normMin:
                return output
            else:
                output[5] = 'NE'
                return output
        except Exception as err1:
            logging.debug(str(err1), exc_info=True)
            return ['', '', '', np.NaN, '', 'NE']

    def pronadji_zero_span(self):
        """
        Metoda pronalazi indekse za zero i span.

        Zero je prva tocka koja ima crefFaktor jednak 0.0, a ako niti jedna
        tocka nema taj crefFaktor, onda se uzima ona sa najmanjim crefFaktorom.
        Span je prva tocka sa crefFaktorom 0.8, a ako niti jedna tocka nema
        taj crefFaktor, onda se uzima ona sa najvecim crefFaktorom
        """
        udots = self.doc.get_tockeUmjeravanja()
        cf = [float(tocka.crefFaktor) for tocka in udots]
        if 0.0 in cf:
            zero = cf.index(0.0)
        else:
            zero = cf.index(min(cf))
        if 0.8 in cf:
            span = cf.index(0.8)
        else:
            span = cf.index(max(cf))
        return zero, span

    def pronadji_zero_span_tocke(self):
        """
        metoda vraca tuple zero i span tocke
        """
        udots = self.doc.get_tockeUmjeravanja()
        zeroIndeks, spanIndeks = self.pronadji_zero_span()
        zero = udots[zeroIndeks]
        span = udots[spanIndeks]
        return zero, span

    def get_provjeru_parametara(self):
        """
        Metoda dohvaca listu provjera kao nested listu.

        Svaki element liste je lista sa elemetima :
        [naziv, tocka norme, kratka oznaka, vrijednost, uvijet prihvatljivosti, ispunjeno]

        Elementi se dodaju samo ako su odredjene vrijednosti izracunate.
        """
        out = []
        if self.srz[0] != '':
            out.append(self.srz)
        if self.srs[0] != '':
            out.append(self.srs)
        if self.rz[0] != '':
            out.append(self.rz)
        if self.rmax[0] != '':
            out.append(self.rmax)
        return out

    def get_slope_and_offset_list(self):
        """
        Metoda vraca listu [slope, offset, prilagodbaA, prilagodbaB]
        """
        return [self.slope, self.offset, self.prilagodbaA, self.prilagodbaB]


class ProvjeraKonvertera(object):
    """
    kalkulator za provjeru konvertera
    """
    def __init__(self, doc=None, parent=None):
        self.doc = doc #dokument sa podacima za racunanje
        self.reset_results()

    def reset_results(self):
        """
        Reset membera koji sadrze rezultate na defaultnu pocetnu vrijednost
        prije racunanja.
        """
        self.rezultat = self.doc.generiraj_nan_frejm_rezultata_konvertera()
        self.ec1 = np.NaN
        self.ec2 = np.NaN
        self.ec3 = np.NaN
        self.ec = np.NaN
        self.ec_list = [self.ec1, self.ec2, self.ec3, self.ec]

    def set_dokument(self, x):
        """Setter dokumenta u kalkulator"""
        self.doc = x

    def get_dokument(self):
        """Getter dokumenta iz kalkulatora"""
        return self.doc

    def provjeri_parametre_prije_racunanja(self):
        """
        Funkcija provjerava ispravnost parametara za provjeru konvertera.
        Funkcija vraca True ako sve valja, False inace.
        """
        try:
            frejm = self.doc.get_siroviPodaci()
            kdots = self.doc.get_tockeKonverter()
            opseg = self.doc.get_opseg()
            cnox50 = self.doc.get_cNOx50()
            cnox95 = self.doc.get_cNOx95()
            # provjera
            assert(self.doc is not None), 'Konfig objekt nije dobro zadan'
            assert(isinstance(frejm, pd.core.frame.DataFrame)), 'Frejm nije pandas dataframe.'
            assert(len(frejm) > 0), 'Frejm nema podataka (prazan)'
            assert('NOx' in frejm.columns), 'Frejmu nedostaje stupac NOx'
            assert('NO' in frejm.columns), 'Frejmu nedostaje stupac NO'
            assert('NO2' in frejm.columns), 'Frejmu nedostaje stupac NO2'
            assert(len(kdots) != 6), 'Za provjeru konvertera nuzno je tocno 6 tocaka. zadano ih je {0}'.format(len(kdots))
            assert(opseg > 0), 'Opseg nije dobro zadan'
            assert(cnox50 > 0), 'cNOx50 nije dobro zadan'
            assert(cnox95 > 0), 'cNOx95 nije dobro zadan'
            return True
        except (AssertionError, AttributeError, TypeError) as e:
            msg = ".".join(['Parametri za racunanje nisu ispravni',str(e)])
            logging.debug(msg, exc_info=True)
            return False

    def racunaj(self):
        """
        racunanje provjere konvertera
        """
        self.reset_results()
        if self.provjeri_parametre_prije_racunanja:
            test = self.doc.get_provjeraKonvertera()
            if test:
                kdots = self.doc.get_tockeKonverter()
                self.get_provjera_konvertera_za_listu_tocaka(kdots)

    def get_provjera_konvertera_za_listu_tocaka(self, tocke):
        """
        metoda za racunanje rezultata provjere konvertera
        """
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
        self.ec_list = [self.ec1, self.ec2, self.ec3, self.ec]

    def _izracunaj_crNOX(self, tocka):
        """
        popunjavanje tablice sa ref vrijednostima koncentracije NOX
        """
        kdots = self.doc.get_tockeKonverter()
        opseg = self.doc.get_opseg()
        imena = [str(dot) for dot in kdots]
        ind = imena.index(str(tocka))
        if ind == 2:
            return 0
        else:
            value = opseg / 2
            return value

    def _izracunaj_crNO2(self, tocka):
        """
        popunjavanje tablice sa ref vrijedsnotima koncentracije NO2
        """
        kdots = self.doc.get_tockeKonverter()
        cnox50 = self.doc.get_cNOx50()
        cnox95 = self.doc.get_cNOx95()
        imena = [str(dot) for dot in kdots]
        ind = imena.index(str(tocka))
        if ind == 1:
            return cnox50
        elif ind == 4:
            return cnox95
        else:
            return 0

    def _izracunaj_cNO(self, tocka):
        """
        funkcija racuna cNO za zadanu tocku (average stabilnih vrijednosti)
        """
        try:
            podaci = list(self.dohvati_slajs_tocke(tocka, 'NO'))
            return np.average(podaci)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            return np.NaN

    def _izracunaj_cNOX(self, tocka):
        """
        funkcija racuna cNOX za zadanu tocku (average stabilnih vrijednosti)
        """
        try:
            podaci = list(self.dohvati_slajs_tocke(tocka, 'NOx'))
            return np.average(podaci)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            return np.NaN

    def _izracunaj_ec1(self):
        """funckija racuna ec1"""
        numerator = self.rezultat.iloc[3, 3] - self.rezultat.iloc[4, 3]
        denominator = self.rezultat.iloc[3, 2] - self.rezultat.iloc[4, 2]
        try:
            value = 1 - (numerator / denominator)
            self.ec1 = value * 100
        except ZeroDivisionError:
            self.ec1 = np.NaN

    def _izracunaj_ec2(self):
        """funckija racuna ec2"""
        numerator = self.rezultat.iloc[0, 3] - self.rezultat.iloc[1, 3]
        denominator = self.rezultat.iloc[0, 2] - self.rezultat.iloc[1, 2]
        try:
            value = 1 - (numerator / denominator)
            self.ec2 = value * 100
        except ZeroDivisionError:
            self.ec2 = np.NaN

    def _izracunaj_ec3(self):
        """funckija racuna ec3"""
        numerator = self.rezultat.iloc[4, 3] - self.rezultat.iloc[5, 3]
        denominator = self.rezultat.iloc[4, 2] - self.rezultat.iloc[5, 2]
        try:
            value = 1 - (numerator / denominator)
            self.ec3 = value * 100
        except ZeroDivisionError:
            self.ec3 = np.NaN

    def _izracunaj_ec(self):
        """ funkcija vraca najmanji od svih ec-ova"""
        out = [self.ec1, self.ec2, self.ec3]
        out = [i for i in out if not np.isnan(i)]
        if len(out):
            self.ec = min(out)
        else:
            self.ec = np.NaN

    def dohvati_slajs_tocke(self, tocka, stupac):
        """
        Funkcija za dohvacanje slajsa podataka iz ciljanog frejma
        Tocka je jedna od definiranih u konfig objektu
        stupac je string (stupac u datafrejmu)
        """
        frejm = self.doc.get_siroviPodaci()
        columns = list(frejm.columns)
        ind = columns.index(stupac)
        start = min(tocka.indeksi)
        end = max(tocka.indeksi)
        siroviSlajs = frejm.iloc[start:end+1, ind]
        agregiraniSlajs = []
        for i in range(0, len(siroviSlajs), 3):
            s = siroviSlajs[i:i+3]
            if len(s) == 3:
                value = np.average(s)
                agregiraniSlajs.append(value)
        return agregiraniSlajs

    def get_listu_efikasnosti(self):
        """
        vrati listu provjere efikasnosti, [self.ec1, self.ec2, self.ec3, self.ec]
        """
        return self.ec_list

    def get_ec_parametar(self):
        """metoda vraca formatirani parametar za procjenu efikasnosti konvertera"""
        if np.isnan(self.ec):
            return None
        else:
            value = self.ec*100
            output = ['Efikasnost konvertera dušikovih oksida',
                      '9.6.2',
                      'Ec =',
                      value,
                      '\u2265 95 %',
                      'DA']
            if self.ec < 0.95:
                output[5] = 'NE'
            return output
