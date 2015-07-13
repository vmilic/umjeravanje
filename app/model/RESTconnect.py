# -*- coding: utf-8 -*-
"""
Created on Mon May 18 14:37:12 2015

@author: DHMZ-Milic
"""
import logging
import requests
import xml.etree.ElementTree as ET


class RESTZahtjev(object):
    """
    Ova klasa sluzi za komunikaciju sa rest servisom.
    """

    def __init__(self, cfg):
        logging.info('start inicjalizacije RESTZahtjev')
        self.auth = ("", "")
        self.konfig = cfg
        self.base = cfg.get_konfig_element('REST', 'baseurl')
        msg = 'base url --> {0}'.format(str(self.base))
        logging.info(msg)
        self.svePostajeUrl = cfg.get_konfig_element('REST', 'postaje')
        msg = 'relative url, postaje --> {0}'.format(str(self.svePostajeUrl))
        logging.info(msg)
        self.sviUredjajiUrl = cfg.get_konfig_element('REST', 'uredjaji')
        msg = 'relative url, uredjaji --> {0}'.format(str(self.sviUredjajiUrl))
        logging.info(msg)
        self.uredjajUrl = cfg.get_konfig_element('REST', 'infoUredjaj')
        msg = 'relative url, uredjaj --> {0}'.format(str(self.uredjajUrl))
        logging.info(msg)
        logging.info('kraj inicjalizacije RESTZahtjev')

    def set_auth(self, x):
        """setter za autorizacijske podatke"""
        self.auth = x

    def get_sve_postaje(self):
        """getter svih stanica sa REST-a. Vraca listu stanica. U slucaju
        pogreske prilikom rada vraca praznu listu"""
        try:
            url = self.base + self.svePostajeUrl
            r = requests.get(url, auth=self.auth)
            errmsg = 'Bad response, status code:{0}, url:{1}'
            assert r.ok is True, errmsg.format(str(r.status_code), str(r.url))
            return self.parse_xml_postaje(r.text)
        except (AssertionError, requests.RequestException) as err:
            logging.error(err, exc_info=True)
            return []
        except Exception as err1:
            logging.error(err1, exc_info=True)
            return []

    def parse_xml_postaje(self, xmlstring):
        """xml parser za popis postaja, vraca listu"""
        msg = 'requested xml={0}'.format(str(xmlstring))
        logging.debug(msg)
        rezultat = []
        root = ET.fromstring(xmlstring)
        for postaja in root:
            naziv = str(postaja.find('nazivPostaje').text)
            rezultat.append(naziv)
        return rezultat

    def get_svi_uredjaji(self):
        """getter svih uredjaja sa REST-a, vraca listu svih uredjaja. U slucaju
        greske prilikom rada vraca praznu listu"""
        try:
            url = self.base + self.sviUredjajiUrl
            r = requests.get(url, auth=self.auth)
            msg = 'Bad response, status code:{0}, url:{1}'
            assert r.ok is True, msg.format(str(r.status_code), str(r.url))
            return self.parse_xml_uredjaji(r.text)
        except (AssertionError, requests.RequestException) as err:
            logging.error(err, exc_info=True)
            return []
        except Exception as err1:
            logging.error(err1, exc_info=True)
            return []

    def parse_xml_uredjaji(self, xmlstring):
        """xml parser za listu uredjaja, vraca listu"""
        msg = 'requested xml={0}'.format(str(xmlstring))
        logging.debug(msg)
        rezultat = []
        root = ET.fromstring(xmlstring)
        for uredjaj in root:
            serial = str(uredjaj.find('serijskaOznaka').text)
            rezultat.append(serial)
        return rezultat

    def get_lokaciju_uredjaja(self, serial):
        """getter lokacija uredjaja sa REST-a, vraca string lokacije. U slucaju
        pogreske prilikom rada vraca prazan string"""
        try:
            url = self.base + self.uredjajUrl
            url = "/".join([url, str(serial), 'lokacija'])
            r = requests.get(url, auth=self.auth)
            msg = 'Bad response, status code:{0}, url:{1}'
            assert r.ok is True, msg.format(str(r.status_code), str(r.url))
            return self.parse_xml_lokacija_uredjaja(r.text)
        except (AssertionError, requests.RequestException) as err:
            logging.error(err, exc_info=True)
            return ''
        except Exception as err1:
            logging.error(err1, exc_info=True)
            return ''

    def parse_xml_lokacija_uredjaja(self, xmlstring):
        """xml parser za lokaciju uredjaja, vraca string"""
        msg = 'requested xml={0}'.format(str(xmlstring))
        logging.debug(msg)
        root = ET.fromstring(xmlstring)
        return str(root.find('nazivPostaje').text)

    def get_komponente_uredjaja(self, serial):
        """getter komponenti uredjaja sa resta, vraca listu. U slucaju pogreske
        prilikom rada vraca praznu listu."""
        try:
            url = self.base + self.uredjajUrl
            url = "/".join([url, str(serial), 'komponente'])
            r = requests.get(url, auth=self.auth)
            msg = 'Bad response, status code:{0}, url:{1}'
            assert r.ok is True, msg.format(str(r.status_code), str(r.url))
            return self.parse_xml_komponenti_uredjaja(r.text)
        except (AssertionError, requests.RequestException) as err:
            logging.error(err, exc_info=True)
            return []
        except Exception as err1:
            logging.error(err1, exc_info=True)
            return []

    def parse_xml_komponenti_uredjaja(self, xmlstring):
        """xml parser za komponente uredjaja, vraca listu komponenti"""
        msg = 'requested xml={0}'.format(str(xmlstring))
        logging.debug(msg)
        root = ET.fromstring(xmlstring)
        rezultat = []
        for formula in root:
            val = str(formula.find('formula').text)
            rezultat.append(val)
        return rezultat
