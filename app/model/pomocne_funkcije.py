# -*- coding: utf-8 -*-
"""
Created on Wed May 13 13:50:05 2015

@author: DHMZ-Milic
"""
import os
import copy
import logging
import xml.etree.ElementTree as ET
import requests


def parse_name_for_serial(fajl):
    """
    File name parser za serial broj uredjaja.
    """
    name = os.path.split(fajl)[1]
    name = name.lower()
    step1 = [element.strip() for element in name.split(sep='-')]
    step2 = [element.lstrip('0') for element in step1]
    if 'conc1min' not in step2:
        return []
    i = step2.index('conc1min')
    step3 = step2[1:i]
    if step3[-1] == 'e':
        serial = step3[-2]
    else:
        serial = step3[-1]
    moguci = []
    moguci.append(serial)
    moguci.append("".join([serial, 'e']))
    moguci.append("".join([serial, 'E']))
    moguci.append("-".join([serial, 'e']))
    moguci.append("-".join([serial, 'E']))
    return moguci

def get_uredjaje(url):
    """
    Funkcija dohvaca sve uredjaje sa REST servisa. Ulazni parametar je url
    do resursa uredjaji, izlaz je lista svih uredjaja.
    """
    try:
        r = requests.get(url)
        if r.ok:
            output = []
            root = ET.fromstring(r.text)
            for uredjaj in root:
                serial = str(uredjaj.find('serijskaOznaka').text)
                output.append(serial)
            return sorted(output)
        else:
            msg = 'Bad request, url={0} , status_code={1}'.format(r.url, r.status_code)
            logging.error(msg)
            return []
    except Exception:
        msg = 'Gruba pogreska kod dohvacanja popisa uredjaja, url={0}'.format(url)
        logging.error(msg, exc_info=True)
        return []

def get_uredjaj_info(url, serial):
    """
    Funkcija dohvaca slozenu mapu podataka za svaki uredjaj. Ulazni parametri su
    url do REST resursa uredjaji i serijska oznaka uredjaja.

    {
    analitickaMetoda :
        kljuc je oznaka komponente
        {
        naziv: naziv analiticke metode (npr. 'Ponovljivnost devijacije u nuli')
        oznaka: oznaka analiticke metode (npr.'Srz')
        min: minimalno odstupanje (npr. 1.0)
        max: maksimalno odstupanje (npr. 15.0)
        }

    komponenta :
        kljuc je formula komponente...
        {
        naziv: naziv komponente (npr. 'ozon)
        mjernaJedinica: mjerna jedinica komponente (npr. 'ug/m3')
        formula: formula komponente (npr O3)
        }

    komponente : lista svih kljuceva dicta komponenta (npr. [NOx,NO,NO2])

    lokacija: sting lokacije uredjaja (npr. 'Plitvicka jezera')
    }
    """
    combinedUrl = "/".join([url, serial])
    try:
        r = requests.get(combinedUrl)
        if r.ok:
            output = {'analitickaMetoda': {},
                      'komponente': [],
                      'komponenta': {},
                      'lokacija': 'None'}
            root = ET.fromstring(r.text)
            # analiticke metode
            tmp1 = {}
            analitickeMetode = root.find('./modelUredjajaId/analitickeMetodeId')
            for metoda in analitickeMetode.findall('dozvoljeneGraniceCollection'):
                naziv = metoda.find('./ispitneVelicine/naziv').text
                oznaka = metoda.find('./ispitneVelicine/oznaka').text
                mjernaJedinica = metoda.find('./mjerneJediniceId/oznaka').text
                try:
                    minGranica = metoda.find('min').text
                except Exception:
                    msg = 'Za uredjaj {0} nije definirana min granica za {1}. Koristim default 0'.format(serial, naziv)
                    minGranica = 0.0
                    logging.error(msg, exc_info=True)
                try:
                    maxGranica = metoda.find('max').text
                except Exception:
                    msg = 'Za uredjaj {0} nije definirana max granica za {1}. Koristim default 400'.format(serial, naziv)
                    maxGranica = 400.0
                    logging.error(msg, exc_info=True)

                tmp1[oznaka] = {
                    'naziv': naziv,
                    'oznaka': oznaka,
                    'mjernaJedinica': mjernaJedinica,
                    'min': minGranica,
                    'max': maxGranica}
            output['analitickaMetoda'] = tmp1
            # komponente
            tmp2 = {}
            komponente = root.find('modelUredjajaId')
            for komponenta in komponente.findall('komponentaCollection'):
                formula = komponenta.find('formula').text
                output['komponente'].append(formula)
                naziv = komponenta.find('naziv').text
                mjernaJedinica = komponenta.find('./mjerneJediniceId/oznaka').text
                tmp2[formula] = {
                    'naziv': naziv,
                    'mjernaJedinica': mjernaJedinica,
                    'formula': formula}
            output['komponenta'] = tmp2
            # output
            output['lokacija'] = get_lokaciju_uredjaja(url, serial)
            return copy.deepcopy(output)
        else:
            msg = 'Bad request, url={0} , status_code={1}'.format(r.url, r.status_code)
            logging.error(msg)
            return {}
    except Exception:
        msg = 'Porblem kod dohvacanja informacije o uredjaju, url={0}'.format(combinedUrl)
        logging.error(msg, exc_info=True)
        return {}

def get_lokaciju_uredjaja(url, serial):
    """
    Za zadani serijski broj i url dohvaca lokaciju uredjaja. U slucaju bilo kakve
    greske sa dohvacanjem podataka, log gresku i vrati 'None'.
    """
    try:
        relurl = "/".join([url,str(serial),'lokacija'])
        r = requests.get(relurl)
        if r.ok:
            root = ET.fromstring(r.text)
            lokacija = root.find('nazivPostaje').text
            return str(lokacija)
        else:
            msg = 'Los request, url={0} , code={1}'.format(r.url, r.status_code)
            logging.error(msg)
            return 'None'
    except Exception:
        msg = 'Pogreska kod trazenja lokacije uredjaja url={0}'.format(relurl)
        logging.error(msg, exc_info=True)
        return 'None'

def get_postaje(url):
    """
    Funkcija dohvaca sve postaje sa REST servisa. Ulazni parametar je url
    do resursa drzavne_mreze/postaje, izlaz je mapa koja za kljuc ima naziv postaje, a
    za vrijednost praznu listu.
    """
    try:
        r = requests.get(url)
        if r.ok:
            output = {}
            root = ET.fromstring(r.text)
            for postaja in root:
                naziv = str(postaja.find('naziv').text)
                output[naziv] = []
            return output
        else:
            msg = 'Bad request, url={0} , status_code={1}'.format(r.url, r.status_code)
            logging.error(msg)
            return {}
    except Exception:
        msg = 'Gruba greska kod dohvacanja postaja, url={0}'.format(url)
        logging.error(msg, exc_info=True)
        return {}

def pripremi_mape_postaja_i_uredjaja(url1, url2):
    """
    Funkcija preuzima podatke sa REST servisa vezanih za uredjaje, njihove
    analiticke metode, komponente.

    Ulazni parametri su dva url-a resursa od REST-a.
    1. url1, resurs uredjaj
    2. url2, resurs drzavna_mreza/postaje

    Funkcija vraca tuple od 2 elementa.
    1. mapu koja povezuje postaje i listu uredjaja na postaji
    2. mapu koja povezuje serijske oznake uredjaja i pdataka o uredjaju.
    """
    logging.info('Sastavljanje mapa postaja i uredjaja')
    sviUredjaji = {}
    svePostaje = get_postaje(url2)
    listaUredjaja = get_uredjaje(url1)
    for serial in listaUredjaja:
        uredjaj = get_uredjaj_info(url1, serial)
        sviUredjaji[serial] = uredjaj
        try:
            lokacija = uredjaj['lokacija']
        except Exception:
            msg = 'Nedostaje kljuc "lokacija", uredjaj={0}'.format(str(uredjaj))
            logging.error(msg, exc_info=True)
            continue
        if lokacija in svePostaje:
            svePostaje[lokacija].append(serial)
        else:
            svePostaje[lokacija] = [serial]
    return svePostaje, sviUredjaji
