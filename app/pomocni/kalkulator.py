# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 08:59:14 2016

@author: DHMZ-Milic
"""
import copy
import logging
import numpy as np
import pandas as pd
from app.model.tocke import Tocka

def provjeri_ispravnost_tocaka(tocke=None):
    """
    Funkcija provjerava da li su tocke dobro zadane. Vraca True ako su tocke dobro
    zadane, False ako nisu.
    """
    try:
        assert isinstance(tocke, list), 'Ulazni parametar nije lista. tocke={0}.'.format(str(type(tocke)))
        for tocka in tocke:
            assert isinstance(tocka, Tocka), 'U listi tocaka postoji objekt koji nije tipa "Tocka".'
        zeroIndeks = get_indeks_zero_tocke(tocke=tocke)
        spanIndeks = get_indeks_span_tocke(tocke=tocke)
        test = (zeroIndeks != None) and (spanIndeks != None)
        assert test, 'U lista nema "zero" i "span" tocku.'
        return True
    except AssertionError as err:
        logging.error(str(err), exc_info=True)
        return False

def make_nan_frame_umjeravanja(tocke=None):
    """
    Funkcija generira datafrejm sa 6 stupaca i n redaka (n je broj umjernih
    tocaka), radi inicijalnog prikaza tablice rezultata umjeravanja.
    Sve vrijednosti tog datafrejma su np.NaN

    #slicna metoda se nalazi u tab_rezultat
    """
    stupci = ['cref', 'U', 'c', u'\u0394', 'sr', 'r']
    if tocke != None and len(tocke) > 0:
        indeksi = [str(tocka) for tocka in tocke]
        frejm = pd.DataFrame(columns=stupci,
                             index=indeksi)
    else:
        frejm = pd.DataFrame(columns=stupci)
    return frejm

def get_indeks_zero_tocke(tocke=None):
    """
    Input je lista tocaka. Output je indeks zero tocke u listi ili None.
    Funkcija vraca indeks prve tocke sa cref==0.0 ("zero") ili None ako zero tocka ne postoji.
    """
    if tocke == None:
        return None
    crefValues = [i.get_crefFaktor() for i in tocke]
    if 0.0 in crefValues:
        indeks = crefValues.index(0.0)
        return indeks
    else:
        return None

def get_indeks_span_tocke(tocke=None):
    """
    Input je lista tocaka. Output je indeks span tocke u listi.
    Funkcija vraca indeks prve tocke sa cref==0.8 ("span") ako span tocka postoji.
    U slucaju da niti jedna tocka nema vrijednost cref 0.8, vraca indeks tocke
    koja ima najveci cref a da nije 0.0.
    """
    if tocke == None:
        return None
    crefValues = [i.get_crefFaktor() for i in tocke]
    if 0.8 in crefValues:
        return crefValues.index(0.8)
    else:
        najveci = max(crefValues)
        if najveci == 0.0:
            return None
        else:
            return crefValues.index(najveci)

def dohvati_slajs_tocke(data=None, tocka=None):
    """
    Funkcija radi 3 minutne agregirane vrijednosti minutnih podataka.
    Ulazni parametri su:
    -data : lista,  vrijednosti minutnih srednjaka
    -tocka : tocka umjeravanja (objekt "Tocka")
    Output je lista 3 minutno agregiranih vrijednosti podataka (average) gdje
    se vrijednost pridruzuje trecoj minuti niza. U slucaju pogreske, vrati praznu
    listu.
    """
    try:
        indeksi = tocka.get_indeksi()
        start = min(indeksi)
        end = max(indeksi)
        siroviSlajs = data[start:end+1]
        agregiraniSlajs = []
        for i in range(0, len(siroviSlajs), 3):
            s = siroviSlajs[i:i+3]
            if len(s) == 3:
                value = np.average(s)
                agregiraniSlajs.append(value)
        return agregiraniSlajs
    except Exception as err:
        logging.error(str(err), exc_info=True)
        return []

def izracunaj_regresijske_koef(data=None, tocke=None, linearnost=True, opseg=np.NaN):
    """
    Racunanje slope i offset linearne regresije za umjeravanje.
    Ulazni parametri su:
    -data : lista,  vrijednosti minutnih srednjaka
    -tocke : lista, tocke umjeravanja (objekti "Tocka")
    -linearnost : boolean za provjeru linearnosti
    -opseg : float vrijednost opsega mjerenja

    Koristi se np.linalg.lstsq
    #izbacena span vrijednost iz racunice
    """
    try:
        if linearnost:
            spanIndeks = get_indeks_span_tocke(tocke=tocke)
            zeroIndeks = get_indeks_zero_tocke(tocke=tocke)
            dots = copy.deepcopy(tocke)
            zero = dots[spanIndeks]
            span = dots[zeroIndeks]
            del dots[spanIndeks] #makni span iz racunice
            x = [izracunaj_cref(tocka=tocka, opseg=opseg) for tocka in dots]
            y = [izracunaj_c(data=data, zero=zero, span=span, tocka=tocka, linearnost=linearnost) for tocka in dots]
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

def izracunaj_prilagodbu(data=None, tocke=None, opseg=np.NaN):
    """
    Racunanje koeficijenata funkcije prilagodbe. Ulazni parametri su:
    -data : lista,  vrijednosti minutnih srednjaka
    -tocke : lista, tocke umjeravanja (objekti "Tocka")
    -opseg : float vrijednost opsega umjeravanja
    Output je tuple vrijednosti (prilagodbaA, prilagodbaB) ili  tuple (np.NaN, np.NaN)
    """
    try:
        spanIndeks = get_indeks_span_tocke(tocke=tocke)
        zeroIndeks = get_indeks_zero_tocke(tocke=tocke)
        dots = copy.deepcopy(tocke)
        span = dots[spanIndeks]
        zero = dots[zeroIndeks]
        crefSpan = izracunaj_cref(tocka=span, opseg=opseg)
        cSpan = izracunaj_c(data=data, zero=zero, span=span, tocka=span, linearnost=True)
        cZero = izracunaj_c(data=data, zero=zero, span=span, tocka=zero, linearnost=True)
        if np.isnan(cSpan) or np.isnan(cZero):
            return np.NaN, np.NaN
        else:
            A = crefSpan / (cSpan - cZero)
            B = -cZero / A
            return A, B
    except Exception as err:
        logging.error(str(err), exc_info=True)
        return np.NaN, np.NaN

def izracunaj_cref(tocka=None, opseg=np.NaN):
    """
    Funkcija racuna cref value zadane tocke. Ulazni parametri su:
    -tocka : tocka umjeravanja (objekt "Tocka")
    -opseg : trenutno izabrani opseg umjeravanja
    """
    try:
        return tocka.get_crefFaktor() * opseg
    except Exception as err:
        logging.error(str(err), exc_info=True)
        return np.NaN

def izracunaj_c(data=None, zero=None, span=None, tocka=None, linearnost=True):
    """
    Racunanje koncentracije c.
    Ulazni parametri su:
    -data : lista,  vrijednosti minutnih srednjaka
    -zero : tocka "Zero" umjeravanja (objekt "Tocka")
    -span : tocka "Span" umjeravanja (objekt "Tocka")
    -tocka : tocka umjeravanja (objekt "Tocka")
    -linearnost : boolean za provjeru linearnosti
    Output je float vrijednost koncentracije ili np.NaN
    """
    try:
        if not linearnost:
            if tocka == zero or tocka == span:
                podaci = dohvati_slajs_tocke(data=data, tocka=tocka)
                return np.average(podaci)
            else:
                return np.NaN
        else:
            podaci = dohvati_slajs_tocke(data=data, tocka=tocka)
            return np.average(podaci)
    except Exception as err:
        logging.error(str(err), exc_info=True)
        return np.NaN

def izracunaj_sr(data=None, zero=None, span=None, tocka=None, linearnost=True):
    """
    Racun standardne devijacije tocke.
    Ulazni parametri su:
    -data : lista,  vrijednosti minutnih srednjaka
    -zero : tocka "Zero" umjeravanja (objekt "Tocka")
    -span : tocka "Span" umjeravanja (objekt "Tocka")
    -tocka : tocka umjeravanja (objekt "Tocka")
    -linearnost : boolean za provjeru linearnosti
    Output je float vrijednost standardne devijacije tocke ili np.NaN
    """
    try:
        if not linearnost:
            if tocka == zero or tocka == span:
                podaci = dohvati_slajs_tocke(data=data, tocka=tocka)
                return np.std(podaci, ddof=1)
            else:
                return np.NaN
        else:
            podaci = dohvati_slajs_tocke(data=data, tocka=tocka)
            return np.std(podaci, ddof=1)
    except Exception as err:
        logging.error(str(err), exc_info=True)
        return np.NaN

def izracunaj_r(zero=None, span=None, tocka=None, c=np.NaN, cref=np.NaN, linearnost=True, slope=np.NaN, offset=np.NaN):
    """
    Racunanje r za tocku
    Ulazni parametri su:
    -zero : tocka "Zero" umjeravanja (objekt "Tocka")
    -span : tocka "Span" umjeravanja (objekt "Tocka")
    -tocka : tocka umjeravanja (objekt "Tocka")
    -c : float vrijednost koncentracije
    -cref : float vrijednost referentne koncentracije
    -linearnost : boolean za provjeru linearnosti
    -slope : float vrijednost nagiba pravca (linearni fit tocaka)
    -offset : float vrijednost odsjecka na osi y pravca (linearni fit tocaka)

    output je float vrijednost r, ili np.NaN
    """
    try:
        if linearnost:
            if tocka == span:
                return np.NaN
            elif tocka == zero:
                return abs(c - (cref * slope + offset))
            else:
                if cref != 0.0:
                    return abs((c - (cref * slope + offset)) / cref)*100
                else:
                    return np.NaN
        else:
            return np.NaN
    except Exception as err:
        logging.error(str(err), exc_info=True)
        return np.NaN

def izracunaj_UR(cref=np.NaN, cCRM=np.NaN, sCRM=np.NaN, uKal=np.NaN, uNul=np.NaN, plinMaxC=np.NaN):
    """
    Racunanje UR
    Ulazni parametri su:
    -cref : float vrijednost referentne koncentracije
    -cCRM : float koncentracija Certificiranog Referentnog Materijala
    -sCRM : float koncentracija Certificiranog Referentnog Materijala
    -uNul : float MFC_NUL_PLIN U kalibracijske jedinice
    -uKal : float MFC_KAL_PLIN U kalibracijske jedinice
    -plinMaxC : max koncentracija generatora cistog zraka za zadani plin
    """
    try:
        #konverzija uNul iz postotaka
        uNul = (uNul/100)
        ufz = izracunaj_ufz(cref=cref, cCRM=cCRM, uNul=uNul)
        if np.isnan(ufz):
            return np.NaN
        #konverzija uKal iz postotaka
        uKal = (uKal/100)
        ufm = izracunaj_ufm(cref=cref, cCRM=cCRM, uKal=uKal)
        if np.isnan(ufm):
            return np.NaN
        ucr = izracunaj_ucr(cref=cref, sCRM=sCRM)
        if np.isnan(ucr):
            return np.NaN
        ucz = izracunaj_ucz(cref=cref, cCRM=cCRM, plinMaxC=plinMaxC)
        if np.isnan(ucz):
            return np.NaN
        value = 2 * np.sqrt(ufz**2+ufm**2+ucr**2+ucz**2+(2*ucz)**2)
        return value
    except Exception as err:
        logging.error(str(err), exc_info=True)
        return np.NaN

def izracunaj_ufz(cref=np.NaN, cCRM=np.NaN, uNul=np.NaN):
    """
    Pomocna funkcija za racunanje U (ufz).
    Ulazni parametri su:
    -cref : float vrijednost referentne koncentracije
    -cCRM : float koncentracija Certificiranog Referentnog Materijala
    -uNul : MFC_NUL_PLIN U kalibracijske jedinice
    Output je float ili np.NaN
    """
    try:
        value = (cref * (cCRM - cref))/(cCRM)
        return value * uNul
    except Exception as err:
        logging.error(str(err), exc_info=True)
        return np.NaN

def izracunaj_ufm(cref=np.NaN, cCRM=np.NaN, uKal=np.NaN):
    """
    Pomocna funkcija za racunanje U (ufm).
    Ulazni parametri su:
    -cref : float vrijednost referentne koncentracije
    -cCRM : float koncentracija Certificiranog Referentnog Materijala
    -uKal : MFC_KAL_PLIN U kalibracijske jedinice
    Output je float ili np.NaN
    """
    try:
        value = (cref * (cCRM - cref))/(cCRM)
        return value * uKal
    except Exception as err:
        logging.error(str(err), exc_info=True)
        return np.NaN

def izracunaj_ucr(cref=np.NaN, sCRM=np.NaN):
    """
    Pomocna funkcija za racunanje U (ucr).
    Ulazni parametri su:
    -cref : float vrijednost referentne koncentracije
    -sCRM : float sljedivost Certificiranog Referentnog Materijala
    Output je float ili np.NaN
    """
    try:
        return sCRM*cref/200
    except Exception as err:
        logging.error(str(err), exc_info=True)
        return np.NaN

def izracunaj_ucz(cref=np.NaN, cCRM=np.NaN, plinMaxC=np.NaN):
    """
    Pomocna funkcija za racunanje U (ucz).
    Ulazni parametri su:
    -cref : float vrijednost referentne koncentracije
    -sCRM : float koncentracija Certificiranog Referentnog Materijala
    -plinMaxC : max koncentracija generatora cistog zraka za zadani plin
    output je float ili np.NaN
    """
    try:
        e1 = cCRM - cref
        e3 = cCRM
        value = e1 * plinMaxC / e3 / np.sqrt(3)
        return value
    except Exception as err:
        logging.error(str(err), exc_info=True)
        return np.NaN

def provjeri_ponovljivost_stdev_u_nuli(jedinica='n/a', limit=np.NaN, srZero=np.NaN):
    """
    Pomocna funkcija za provjeru ponovljivosti (sr) u zero tocki.
    Ulazni parametri su:
    -jedinica : string , naziv mjerne jedinice
    -limit : float vrijednost granice srz analiticke metode
    -srZero : float vrijednost sr zero tocke

    Rezultat je lista:
    [naziv, tocka norme, kratka oznaka, vrijednost, uvijet prihvatljivosti, ispunjeno]
    """
    try:
        prihvatljivost = " ".join(['<', str(limit), jedinica])
        output = ['Ponovljivost standardne devijacije u nuli',
                  '9.5.1',
                  'S<sub>r,z</sub> =',
                  srZero,
                  prihvatljivost,
                  'DA']
        if srZero < limit and srZero >= 0.0:
            return output
        else:
            output[5] = 'NE'
            return output
    except Exception as err:
        logging.debug(str(err), exc_info=True)
        output = ['Ponovljivost standardne devijacije u nuli',
                  '9.5.1',
                  'S<sub>r,z</sub> =',
                  np.NaN,
                  '',
                  'NE']
        return output

def provjeri_ponovljivost_stdev_za_vrijednost(jedinica='n/a', limit=np.NaN, srSpan=np.NaN):
    """
    Pomocna funkcija za provjeru ponovljivosti (sr) u span tocki.
    Ulazni parametri su:
    -jedinica : string , naziv mjerne jedinice
    -limit : float vrijednost granice srz analiticke metode
    -srSpan : sr vrijednost span tocke

    Rezultat je lista:
    [naziv, tocka norme, kratka oznaka, vrijednost, uvijet prihvatljivosti, ispunjeno]
    """
    try:
        prihvatljivost = " ".join(['<', str(limit), jedinica])
        output = ['Ponovljivost standardne devijacije pri koncentraciji ct',
                  '9.5.1',
                  'S<sub>r,ct</sub> =',
                  srSpan,
                  prihvatljivost,
                  'DA']
        if srSpan < limit and srSpan >= 0.0:
            return output
        else:
            output[5] = 'NE'
            return output
    except Exception as err1:
        logging.debug(str(err1), exc_info=True)
        output = ['Ponovljivost standardne devijacije pri koncentraciji ct',
                  '9.5.1',
                  'S<sub>r,ct</sub> =',
                  np.NaN,
                  '',
                  'NE']
        return output

def provjeri_odstupanje_od_linearnosti_u_nuli(jedinica='n/a', limit=np.NaN, rZero=np.NaN):
    """
    Pomocna funkcija za provjeru odstupanja od linearnosti za koncentraciju 0
    Ulazni parametri su:
    -jedinica : string , naziv mjerne jedinice
    -limit : float vrijednost granice srz analiticke metode
    -rZero : r vrijednost zero tocke

    rezultat je lista:
    [naziv, tocka norme, kratka oznaka, vrijednost, uvijet prihvatljivosti, ispunjeno]
    """
    try:
        prihvatljivost = " ".join(['\u2264', str(limit), jedinica])
        output = ['Odstupanje od linearnosti u nuli',
                  '9.6.2',
                  'r<sub>z</sub> =',
                  rZero,
                  prihvatljivost,
                  'DA']
        if rZero <= limit and rZero >= 0.0:
            return output
        else:
            output[5] = 'NE'
            return output
    except Exception as err1:
        logging.debug(str(err1), exc_info=True)
        output = ['Odstupanje od linearnosti u nuli',
                  '9.6.2',
                  'r<sub>z</sub> =',
                  np.NaN,
                  '',
                  'NE']
        return output

def provjeri_maksimalno_relativno_odstupanje_od_linearnosti(jedinica='n/a', limit=np.NaN, rMax=np.NaN):
    """
    Pomocna funkcija za provjeru max relativno odstupanje od linearnosti.
    Ulazni parametri su:
    -jedinica : string , naziv mjerne jedinice
    -limit : float vrijednost granice srz analiticke metode
    -rMax : maksimalna vrijednost r

    rezultat je lista:
    [naziv, tocka norme, kratka oznaka, vrijednost, uvijet prihvatljivosti, ispunjeno]
    """
    try:
        prihvatljivost = " ".join(['\u2264', str(limit), '%'])
        output = ['Maksimalno relativno odstupanje od linearnosti',
                  '9.6.2',
                  'r<sub>z,rel</sub> =',
                  rMax,
                  prihvatljivost,
                  'DA']
        if rMax <= limit and rMax >= 0.0:
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

def racun_umjeravanja(tocke=None,
                      data=None,
                      linearnost=True,
                      opseg=np.NaN,
                      cCRM=np.NaN,
                      sCRM=np.NaN,
                      uNul=np.NaN,
                      uKal=np.NaN,
                      plinMaxC=np.NaN,
                      ponovljivost=True,
                      jedinica='n/a',
                      srzlimit=np.NaN,
                      srslimit=np.NaN,
                      rzlimit=np.NaN,
                      rmaxlimit=np.NaN):
    """
    Funkcija koja racuna rezultate umjeravanja. Ulazni parametri su:
    -tocke : lista, tocke umjeravanja (objekti "Tocka")
    -data : lista,  vrijednosti minutnih srednjaka
    -linearnost : boolean za provjeru linearnosti
    -opseg : opseg umjeravanja
    -cCRM : float, koncentracija certificiranog referentnog materijala
    -sCRM : sljedivost certificiranog referentnog materijala
    -uNul : MFC_NUL_PLIN U kalibracijske jedinice
    -uKal : MFC_KAL_PLIN U kalibracijske jedinice
    -plinMaxC : max koncentracija generatora cistog zraka za zadani plin
    -ponovljivost : boolean za provjeru ponovljivosti
    -jedinica : string mjerne jedinice
    -srzlimit : gornja granica Srz analiticke metode
    -srslimit : gornja granica Srs analiticke metode
    -rzlimit : gornja granica rz analiticke metode
    -rmaxlimit : gornja granica rmax analiticke metode
    """
    if tocke == None:
        tocke = []
    #rezultatni frejm
    rezultat = make_nan_frame_umjeravanja(tocke=tocke)
    # racun za slope i offset
    slope, offset = izracunaj_regresijske_koef(data=data, tocke=tocke, linearnost=linearnost, opseg=opseg)
    # racun koeficijenata funkcije prilagodbe
    prilagodbaA, prilagodbaB = izracunaj_prilagodbu(data=data, tocke=tocke, opseg=opseg)
    #zero i span tocke...
    spanIndeks = get_indeks_span_tocke(tocke=tocke)
    zeroIndeks = get_indeks_zero_tocke(tocke=tocke)
    zero = tocke[spanIndeks]
    span = tocke[zeroIndeks]
    #vrijednosti u tablici rezultata
    for tocka in tocke:
        red = str(tocka)
        cref = izracunaj_cref(tocka=tocka,
                              opseg=opseg)
        c = izracunaj_c(data=data,
                        zero=zero,
                        span=span,
                        tocka=tocka,
                        linearnost=linearnost)
        sr = izracunaj_sr(data=data,
                          zero=zero,
                          span=span,
                          tocka=tocka,
                          linearnost=linearnost)
        r = izracunaj_r(zero=zero,
                        span=span,
                        tocka=tocka,
                        c=c,
                        cref=cref,
                        linearnost=linearnost,
                        slope=slope,
                        offset=offset)
        ur = izracunaj_UR(cref=cref,
                          cCRM=cCRM,
                          sCRM=sCRM,
                          uKal=uKal,
                          uNul=uNul,
                          plinMaxC=plinMaxC)
        #upisi rezultate u tablicu
        rezultat.loc[red, 'cref'] = cref
        rezultat.loc[red, 'c'] = c
        rezultat.loc[red, u'\u0394'] = c - cref
        rezultat.loc[red, 'sr'] = sr
        rezultat.loc[red, 'r'] = r
        rezultat.loc[red, 'U'] = ur
    #testovi
    testovi = {}
    if ponovljivost:
        #ponovljivost u nuli
        srZero = rezultat.loc[str(zero),'sr']
        srz = provjeri_ponovljivost_stdev_u_nuli(jedinica=jedinica,
                                                 limit=srzlimit,
                                                 srZero=srZero)
        testovi['srz'] = srz
        #ponovljivost pri spanu
        srSpan = rezultat.loc[str(span), 'sr']
        srs = provjeri_ponovljivost_stdev_za_vrijednost(jedinica=jedinica,
                                                        limit=srslimit,
                                                        srSpan=srSpan)
        testovi['srs'] = srs
    if linearnost:
        #odstupanje of linearnosti u nuli
        rZero = rezultat.loc[str(zero), 'r']
        rz = provjeri_odstupanje_od_linearnosti_u_nuli(jedinica=jedinica,
                                                       limit=rzlimit,
                                                       rZero=rZero)
        testovi['rz'] = rz
        #max relativno odstupanje of linearnosti
        try:
            #izbacujemo zero i span tocku
            slajs = rezultat.drop(str(zero))
            slajs = slajs.drop(str(span))
        except Exception as err:
            logging.error(str(err), exc_info=True)
            slajs = rezultat
        rMax = max(slajs.loc[:,'r'])
        rmax = provjeri_maksimalno_relativno_odstupanje_od_linearnosti(jedinica=jedinica,
                                                                       limit=rmaxlimit,
                                                                       rMax=rMax)
        testovi['rmax'] = rmax
    #pakiranje rezultata u mapu
    output = {}
    output['umjeravanje'] = rezultat
    output['prilagodba'] = {'slope':slope, 'offset':offset, 'prilagodbaA':prilagodbaA, 'prilagodbaB':prilagodbaB}
    output['testovi'] = testovi
    return output

#funkcije za racunanje konvertera.
def make_nan_frame_konverter(tocke=None):
    """
    metoda generira datafrejm sa 4 stupca i 6 redaka radi inicijalnog prikaza
    tablice rezultata umjeravanja. Sve vrijednosti tog datafrejma su np.NaN

    #slicna metoda se nalazi u tab_konverter
    """
    indeks = [str(tocka) for tocka in tocke]
    frejm = pd.DataFrame(
        columns=['c, R, NOx', 'c, R, NO2', 'c, NO', 'c, NOx'],
        index=indeks)
    return frejm

def izracunaj_crNOx(tocke=None, tocka=None, opseg=np.NaN):
    """
    racunanje podataka za tablicu sa ref vrijednostima koncentracije NOX
    -tocke : lista objekata "Tocka", sve tocke provjere konvertera
    -tocka : objekt "Tocka" , tocka konvertera za koju se racuna vrijednost
    -opseg : float, opseg provjere
    """
    try:
        imena = [str(dot) for dot in tocke]
        ind = imena.index(str(tocka))
        if ind == 2:
            return 0
        else:
            value = opseg / 2
            return value
    except Exception as err:
        logging.warning(str(err))
        return np.NaN

def izracunaj_crNO2(tocke=None, tocka=None, opseg=np.NaN, cnox50=np.NaN, cnox95=np.NaN):
    """
    racunanje podataka za tablicu sa ref vrijedsnotima koncentracije NO2
    -tocke : lista objekata "Tocka", sve tocke provjere konvertera
    -tocka : objekt "Tocka" , tocka konvertera za koju se racuna vrijednost
    -opseg : float, opseg provjere
    -cnox50 : float, parametar cNOx50
    -cnox95 : float, parametar cNOx95
    """
    try:
        imena = [str(dot) for dot in tocke]
        ind = imena.index(str(tocka))
        if ind == 1:
            return cnox50
        elif ind == 4:
            return cnox95
        else:
            return 0
    except Exception as err:
        logging.warning(str(err))
        return np.NaN

def izracunaj_cNO(frejm=None, tocka=None):
    """
    funkcija racuna cNO za zadanu tocku (average stabilnih vrijednosti)
    -frejm : pandas dataframe ulaznih podataka (stupci NO, NOx, NO2)
    -tocka : objekt "Tocka" , tocka konvertera za koju se racuna vrijednost
    """
    try:
        data = list(frejm['NO']) #samo NO stupac frejma
        podaci = list(dohvati_slajs_tocke(data=data, tocka=tocka))
        return np.average(podaci)
    except Exception as err:
        logging.warning(str(err))
        return np.NaN

def izracunaj_cNOX(frejm=None, tocka=None):
    """
    funkcija racuna cNOX za zadanu tocku (average stabilnih vrijednosti)
    -frejm : pandas dataframe ulaznih podataka (stupci NO, NOx, NO2)
    -tocka : objekt "Tocka" , tocka konvertera za koju se racuna vrijednost
    """
    try:
        data = list(frejm['NOx']) #samo NOx stupac frejma
        podaci = list(dohvati_slajs_tocke(data=data, tocka=tocka))
        return np.average(podaci)
    except Exception as err:
        logging.warning(str(err))
        return np.NaN

def izracunaj_ec1(rezultat):
    """
    funckija racuna ec1
    -rezultat : pandas dataframe rezultata
    """
    try:
        numerator = rezultat.iloc[3, 3] - rezultat.iloc[4, 3]
        denominator = rezultat.iloc[3, 2] - rezultat.iloc[4, 2]
        value = 1 - (numerator / denominator)
        return abs(value * 100)
    except Exception as err:
        logging.warning(str(err))
        return np.NaN

def izracunaj_ec2(rezultat):
    """
    funckija racuna ec2
    -rezultat : pandas dataframe rezultata
    """
    try:
        numerator = rezultat.iloc[0, 3] - rezultat.iloc[1, 3]
        denominator = rezultat.iloc[0, 2] - rezultat.iloc[1, 2]
        value = 1 - (numerator / denominator)
        return abs(value * 100)
    except Exception as err:
        logging.warning(str(err))
        return np.NaN

def izracunaj_ec3(rezultat):
    """
    funckija racuna ec3
    -rezultat : pandas dataframe rezultata
    """
    try:
        numerator = rezultat.iloc[4, 3] - rezultat.iloc[5, 3]
        denominator = rezultat.iloc[4, 2] - rezultat.iloc[5, 2]
        value = 1 - (numerator / denominator)
        return abs(value * 100)
    except Exception as err:
        logging.warning(str(err))
        return np.NaN

def izracunaj_ec(rezultat):
    """
    funkcija racuna ec1, ec2 i ec3 te vraca najmanji rezultat
    -rezultat : pandas dataframe rezultata
    """
    out = [izracunaj_ec1(rezultat), izracunaj_ec2(rezultat), izracunaj_ec3(rezultat)]
    out = [i for i in out if not np.isnan(i)]
    if len(out):
        return min(out)
    else:
        return np.NaN

def racunaj_vrijednosti_provjere_konvertera(tocke=None,
                                            opseg=np.NaN,
                                            frejm=None,
                                            cnox50=np.NaN,
                                            cnox95=np.NaN,
                                            ecmin=np.NaN,
                                            ecmax=np.NaN):
    """
    metoda za racunanje rezultata provjere konvertera
    -tocke : lista tocaka za provjeru konvertera (objekti "Tocka")
    -opseg : opseg provjere
    -frejm : pandas dataframe ulaznih podataka (stupci NO, NOx, NO2)
    -cnox50 : float parametar cNOx50
    -cnox95 : float parametar cNOx95
    -ecmin : float, donja granica prihvatljivosti efikasnosti konvertera
    -ecmax : float, gornja granica prihvatljivosti efikasnosti konvertera
    """
    if tocke == None:
        tocke = []
    #rezultat frame
    rezultat = make_nan_frame_konverter(tocke=tocke)
    for tocka in tocke:
        row = str(tocka)
        rezultat.loc[row, 'c, R, NOx'] = izracunaj_crNOx(tocke=tocke, tocka=tocka, opseg=opseg)
        rezultat.loc[row, 'c, R, NO2'] = izracunaj_crNO2(tocke=tocke, tocka=tocka, opseg=opseg, cnox50=cnox50, cnox95=cnox95)
        rezultat.loc[row, 'c, NO'] = izracunaj_cNO(frejm=frejm, tocka=tocka)
        rezultat.loc[row, 'c, NOx'] = izracunaj_cNOX(frejm=frejm, tocka=tocka)
    ec1 = izracunaj_ec1(rezultat)
    ec2 = izracunaj_ec2(rezultat)
    ec3 = izracunaj_ec3(rezultat)
    ec = izracunaj_ec(rezultat)
    if np.isnan(ec) and np.isnan(ecmin) and np.isnan(ecmax):
        kriterij = ['Efikasnost konvertera dušikovih oksida',
                    '',
                    'Ec =',
                    np.NaN,
                    '{0}% \u2264 {1}% \u2264 {2}%'.format(str(ecmin), str(np.NaN), str(ecmax)),
                    'NE']
    else:
        value = ec*100
        kriterij = ['Efikasnost konvertera dušikovih oksida',
                    '9.6.2',
                    'Ec =',
                    value,
                    '{0}% \u2264 {1}% \u2264 {2}%'.format(str(ecmin), str(round(value, 2)), str(ecmax)),
                    'DA']
        if ec < ecmin or ec > ecmax or np.isnan(ec):
            kriterij[5] = 'NE'

    #pakiranje rezultata u mapu
    output = {}
    output['rezultat'] = rezultat
    output['efikasnost'] = [ec1, ec2, ec3, ec]
    output['ec_kriterij'] = kriterij
    return output
