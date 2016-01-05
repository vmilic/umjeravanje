# -*- coding: utf-8 -*-
"""
Created on Tue May 12 10:05:56 2015

@author: DHMZ-Milic
"""
import logging
import numpy as np
import pandas as pd

class Kalkulator(object):
    """klasa za racunanje rezultata umjeravanja, ponovljivosti, linearnosti"""
    def __init__(self, doc=None, mjerenje=None):
        """inicijalizacija sa:
        1. doc
            -instancom dokumenta
            -potrebna zbog globalnih postavki za racunanje
        2. mjerenje
            -string koji definira s kojom komponentom se racuna
        """
        self.set_dokument(doc)
        self.set_mjerenje(mjerenje)
        self.reset_results()

    def set_mjerenje(self, x):
        """setter izabranog mjerenja"""
        self.izabranoMjerenje = x

    def get_mjerenje(self):
        """getter izabranog mjerenja"""
        return self.izabranoMjerenje

    def set_dokument(self, x):
        """setter instance dokumenta"""
        self.doc = x

    def get_dokument(self):
        """getter instance dokumenta"""
        return self.doc

    def reset_results(self):
        """
        Reset membera koji sadrze rezultate na defaultnu pocetnu vrijednost
        prije racunanja.
        """
        self.tocke = self.doc.init_tockeUmjeravanja()
        self.frejm = pd.DataFrame()
        self.rezultat = self.generiraj_nan_frejm_rezultata_umjeravanja()
        self.prilagodbaA = np.NaN
        self.prilagodbaB = np.NaN
        self.slope = np.NaN
        self.offset = np.NaN
        self.srz = ['Ponovljivost standardne devijacije u nuli',
                    '',
                    'S<sub>r,z</sub> =',
                    np.NaN,
                    '',
                    'NE']
        self.srs = ['Ponovljivost standardne devijacije pri koncentraciji ct',
                    '',
                    'S<sub>r,ct</sub> =',
                    np.NaN,
                    '',
                    'NE']
        self.rz = ['Odstupanje od linearnosti u nuli',
                   '',
                   'r<sub>z</sub> =',
                   np.NaN,
                   '',
                   'NE']
        self.rmax = ['Maksimalno relativno odstupanje od linearnosti',
                     '',
                     'r<sub>z,rel</sub> =',
                     np.NaN,
                     '',
                     'NE']
        self.rezultatiTestova = {'srs':self.srs,
                                 'srz':self.srz,
                                 'rz':self.rz,
                                 'rmax':self.rmax}
        logging.debug('All result members reset to np.NaN')

    def generiraj_nan_frejm_rezultata_umjeravanja(self):
        """
        metoda generira datafrejm sa 6 stupaca i n redaka (n je broj umjernih
        tocaka prezuetih iz konfiga), radi inicijalnog prikaza tablice
        rezultata umjeravanja. Sve vrijednosti tog datafrejma su np.NaN
        """
        frejm = pd.DataFrame(
            columns=['cref', 'U', 'c', u'\u0394', 'sr', 'r'],
            index=list(range(len(self.tocke))))
        return frejm

    def provjeri_ispravnost_parametara(self):
        """
        Funkcija provjerava ispravnost parametara za racunanje umjeravanja.
        Funkcija vraca True ako sve valja, False inace
        """
        try:
            model = self.doc.get_model(mjerenje=self.izabranoMjerenje)
            tocke = model.get_tocke()
            frejm = model.get_frejm()
            opseg = self.doc.get_opseg()
            cCRM = self.doc.get_koncentracijaCRM()
            sCRM = self.doc.get_sljedivostCRM()
            cf = [float(tocka.crefFaktor) for tocka in tocke]
            negativniFaktori = [faktor for faktor in cf if faktor < 0]
            dilucija = self.doc.get_izabranaDilucija()
            zrak = self.doc.get_izabraniZrak()
            #provjere
            assert(isinstance(frejm, pd.core.frame.DataFrame)), 'Podaci nisu dobro zadani.'
            assert(len(frejm) > 0), 'Nema podataka.'
            assert(len(tocke) >= 2), 'Zadano je manje od dvije tocke za umjeravanje.'
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

    def racunaj_vrijednosti_umjeravanja_za_listu_tocaka(self):
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
        indeks = [str(tocka) for tocka in self.tocke]
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
        for tocka in self.tocke:
            row = str(tocka)
            self.rezultat.loc[row, 'cref'] = self._izracunaj_cref(tocka)
            self.rezultat.loc[row, 'c'] = self._izracunaj_c(tocka)
            self.rezultat.loc[row, u'\u0394'] = self._izracunaj_delta(tocka)
            self.rezultat.loc[row, 'sr'] = self._izracunaj_sr(tocka)
            self.rezultat.loc[row, 'r'] = self._izracunaj_r(tocka)
            self.rezultat.loc[row, 'U'] = self._izracunaj_UR(tocka)

        # sklapanje rezultata testova
        if self.doc.get_provjeraPonovljivost():
            self.srz = self._provjeri_ponovljivost_stdev_u_nuli()
            self.srs = self._provjeri_ponovljivost_stdev_za_vrijednost()
            self.rezultatiTestova['srz'] = self.srz
            self.rezultatiTestova['srs'] = self.srs
        if self.doc.get_provjeraLinearnost():
            self.rz = self._provjeri_odstupanje_od_linearnosti_u_nuli()
            self.rmax = self._provjeri_maksimalno_relativno_odstupanje_od_linearnosti()
            self.rezultatiTestova['rz'] = self.rz
            self.rezultatiTestova['rmax'] = self.rmax

    def racunaj(self):
        """
        Glavna funkcija racuna sve parametre umjeravanja. Nakon postavljanja
        konfiga i podataka u objekt, pozovi ovu metoda za racunanje.
        """
        self.reset_results()
        if self.provjeri_ispravnost_parametara():
            model = self.doc.get_model(mjerenje=self.izabranoMjerenje)
            self.tocke = model.get_tocke()
            self.frejm = model.get_frejm()
            self.racunaj_vrijednosti_umjeravanja_za_listu_tocaka()

    def pronadji_zero_span(self):
        """
        Metoda pronalazi indekse za zero i span.

        Zero je prva tocka koja ima crefFaktor jednak 0.0, a ako niti jedna
        tocka nema taj crefFaktor, onda se uzima ona sa najmanjim crefFaktorom.
        Span je prva tocka sa crefFaktorom 0.8, a ako niti jedna tocka nema
        taj crefFaktor, onda se uzima ona sa najvecim crefFaktorom
        """
        cf = [float(tocka.crefFaktor) for tocka in self.tocke]
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
        zeroIndeks, spanIndeks = self.pronadji_zero_span()
        zero = self.tocke[zeroIndeks]
        span = self.tocke[spanIndeks]
        return zero, span

    def dohvati_slajs_tocke(self, tocka):
        """
        Funkcija za dohvacanje slajsa podataka iz ciljanog frejma
        Tocka je jedna od definiranih u konfig objektu

        output je lista 3 minutno agregiranih vrijednosti podataka u slajsu
        """
        cols = list(self.frejm.columns)
        ind = cols.index(self.izabranoMjerenje)
        start = min(tocka.indeksi)
        end = max(tocka.indeksi)
        siroviSlajs = self.frejm.iloc[start:end+1, ind]
        agregiraniSlajs = []
        for i in range(0, len(siroviSlajs), 3):
            s = siroviSlajs[i:i+3]
            if len(s) == 3:
                value = np.average(s)
                agregiraniSlajs.append(value)
        return agregiraniSlajs

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
            lin = self.doc.get_provjeraLinearnost()
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
            lin = self.doc.get_provjeraLinearnost()
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
            lin = self.doc.get_provjeraLinearnost()
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
            lin = self.doc.get_provjeraLinearnost()
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
            sljedivost = self.doc.get_sljedivostZrak()
            e1 = cCRM - self._izracunaj_cref(tocka)
            e3 = cCRM
            value = e1 * sljedivost / e3 / np.sqrt(3)
            return value
        except Exception as err:
            logging.error(str(err), exc_info=True)
            return np.NaN

    def _izracunaj_regresijske_koef(self):
        """
        Racunanje slope i offset linearne regresije.
        Koristi se np.linalg.lstsq

        #izbacena span vrijednost iz racunice
        """
        try:
            lin = self.doc.get_provjeraLinearnost()
            if lin:
                zero, span = self.pronadji_zero_span_tocke()
                dots = [tocka for tocka in self.tocke if tocka != span]
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
            output = ['Ponovljivost standardne devijacije u nuli',
                      '',
                      'S<sub>r,z</sub> =',
                      np.NaN,
                      '',
                      'NE']
            return output

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
            output = ['Ponovljivost standardne devijacije pri koncentraciji ct',
                      '',
                      'S<sub>r,ct</sub> =',
                      np.NaN,
                      '',
                      'NE']
            return output

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
            output = ['Odstupanje od linearnosti u nuli',
                      '',
                      'r<sub>z</sub> =',
                      np.NaN,
                      '',
                      'NE']
            return output

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
            uredjaji = self.doc.get_uredjaji()
            uredjaj = self.doc.get_izabraniUredjaj()
            normMin = float(uredjaji[uredjaj]['analitickaMetoda']['rmax']['min'])
            normMax = float(uredjaji[uredjaj]['analitickaMetoda']['rmax']['max'])
            zero, span = self.pronadji_zero_span_tocke()
            dots = [tocka for tocka in self.tocke if (tocka != zero and tocka != span)]
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
            output = ['Maksimalno relativno odstupanje od linearnosti',
                      '9.6.2',
                      'r<sub>z,rel</sub> =',
                      np.NaN,
                      '',
                      'NE']
            return output

    def get_provjeru_parametara(self):
        """
        Metoda vraca dict rezultata testova. kljucevi su : 'srz', 'srs', 'rz', 'rmax'

        Svaki element mape je lista sa elemetima :
        [naziv, tocka norme, kratka oznaka, vrijednost, uvijet prihvatljivosti, ispunjeno]
        """
        return self.rezultatiTestova

    def get_slope_and_offset_map(self):
        """
        Metoda vraca mapu sa kljucevima: slope, offset, prilagodbaA, prilagodbaB
        """
        output = {'slope':self.slope,
                  'offset':self.offset,
                  'prilagodbaA':self.prilagodbaA,
                  'prilagodbaB':self.prilagodbaB}
        return output

    def get_tablicu_rezultata(self):
        """metoda vraca tablicu rezultata umjeravanja"""
        return self.rezultat
################################################################################
################################################################################
class KonverterKalkulator(object):
    """
    kalkulator za provjeru konvertera
    """
    def __init__(self, doc=None, parent=None):
        self.doc = doc
        self.reset_results()

    def reset_results(self):
        """
        Reset membera koji sadrze rezultate na defaultnu pocetnu vrijednost
        prije racunanja.
        """
        self.tocke = self.doc.init_tockeKonverter()
        self.frejm = pd.DataFrame()

        self.rezultat = self.generiraj_nan_frejm_rezultata_konvertera()
        self.ec1 = np.NaN
        self.ec2 = np.NaN
        self.ec3 = np.NaN
        self.ec = np.NaN

    def set_dokument(self, x):
        """Setter dokumenta u kalkulator"""
        self.doc = x

    def get_dokument(self):
        """Getter dokumenta iz kalkulatora"""
        return self.doc

    def generiraj_nan_frejm_rezultata_konvertera(self):
        """
        metoda generira datafrejm sa 4 stupca i 6 redaka radi inicijalnog prikaza
        tablice rezultata umjeravanja. Sve vrijednosti tog datafrejma su np.NaN
        """
        indeks = [str(tocka) for tocka in self.tocke]
        frejm = pd.DataFrame(
            columns=['c, R, NOx', 'c, R, NO2', 'c, NO', 'c, NOx'],
            index=indeks)
        return frejm

    def provjeri_parametre_prije_racunanja(self):
        """
        Funkcija provjerava ispravnost parametara za provjeru konvertera.
        Funkcija vraca True ako sve valja, False inace.
        """
        try:
            model = self.doc.get_model(mjerenje='konverter')
            frejm = model.get_frejm()
            tocke = model.get_tocke()
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
            assert(len(tocke) == 6), 'Za provjeru konvertera nuzno je tocno 6 tocaka. zadano ih je {0}'.format(len(tocke))
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
        if self.provjeri_parametre_prije_racunanja():
            model = self.doc.get_model(mjerenje='konverter')
            self.tocke = model.get_tocke()
            self.frejm = model.get_frejm()
            self.racunaj_vrijednosti_provjere_konvertera()

    def racunaj_vrijednosti_provjere_konvertera(self):
        """
        metoda za racunanje rezultata provjere konvertera
        """
        for tocka in self.tocke:
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
        opseg = self.doc.get_opseg()
        imena = [str(dot) for dot in self.tocke]
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
        cnox50 = self.doc.get_cNOx50()
        cnox95 = self.doc.get_cNOx95()
        imena = [str(dot) for dot in self.tocke]
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
        try:
            numerator = self.rezultat.iloc[3, 3] - self.rezultat.iloc[4, 3]
            denominator = self.rezultat.iloc[3, 2] - self.rezultat.iloc[4, 2]
            value = 1 - (numerator / denominator)
            self.ec1 = value * 100
        except ZeroDivisionError:
            self.ec1 = np.NaN

    def _izracunaj_ec2(self):
        """funckija racuna ec2"""
        try:
            numerator = self.rezultat.iloc[0, 3] - self.rezultat.iloc[1, 3]
            denominator = self.rezultat.iloc[0, 2] - self.rezultat.iloc[1, 2]
            value = 1 - (numerator / denominator)
            self.ec2 = value * 100
        except ZeroDivisionError:
            self.ec2 = np.NaN

    def _izracunaj_ec3(self):
        """funckija racuna ec3"""
        try:
            numerator = self.rezultat.iloc[4, 3] - self.rezultat.iloc[5, 3]
            denominator = self.rezultat.iloc[4, 2] - self.rezultat.iloc[5, 2]
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
        columns = list(self.frejm.columns)
        ind = columns.index(stupac)
        start = min(tocka.indeksi)
        end = max(tocka.indeksi)
        siroviSlajs = self.frejm.iloc[start:end+1, ind]
        agregiraniSlajs = []
        for i in range(0, len(siroviSlajs), 3):
            s = siroviSlajs[i:i+3]
            if len(s) == 3:
                value = np.average(s)
                agregiraniSlajs.append(value)
        return agregiraniSlajs

    def get_rezultate_konvertera(self):
        """vrati frejm tablicom rezultata provjere konvertera"""
        return self.rezultat

    def get_listu_efikasnosti(self):
        """
        vrati listu provjere efikasnosti, [self.ec1, self.ec2, self.ec3, self.ec]
        """
        return [self.ec1, self.ec2, self.ec3, self.ec]

    def get_ec_parametar(self):
        """metoda vraca formatirani parametar za procjenu efikasnosti konvertera"""
        if np.isnan(self.ec):
            output = ['Efikasnost konvertera dušikovih oksida',
                      '',
                      'Ec =',
                      np.NaN,
                      '\u2265 95 %',
                      'NE']
            return output
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
