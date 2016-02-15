# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 13:10:55 2016

@author: DHMZ-Milic
"""
import pickle
import logging
import configparser
from app.model.uredjaj import Uredjaj
from app.model.konfig_objekt import MainKonfig

################################################################################
################################################################################
class OdazivTabData(object):
    """podaci za tab odaziv"""
    def __init__(self, naziv, frejm=None, minlimit=10.0, maxlimit=90.0):
        self.rezultat = None
        self.naziv = naziv
        self.frejm = frejm
        self.minlimit = minlimit
        self.maxlimit = maxlimit

    def get_naziv(self):
        return self.naziv

    def set_frejm(self, frejm):
        self.frejm = frejm

    def get_frejm(self):
        return self.frejm

    def set_minlimit(self, x):
        self.minlimit = x

    def get_minlimit(self):
        return self.minlimit

    def set_maxlimit(self, x):
        self.maxlimit = x

    def get_maxlimit(self):
        return self.maxlimit

    def set_rezultat(self, mapa):
        self.rezultat = mapa

    def get_rezultat(self):
        return self.rezultat
################################################################################
################################################################################
class RezultatTabData(object):
    """podaci za tab rezultata"""
    def __init__(self, naziv, frejm=None, startIndeks=0, tocke=None):
        self.rezultat = None
        self.naziv = naziv
        self.frejm = frejm
        self.startIndeks = startIndeks
        if tocke == None:
            self.tocke = []
        else:
            self.tocke = tocke

    def get_naziv(self):
        return self.naziv

    def set_frejm(self, frejm):
        self.frejm = frejm

    def get_frejm(self):
        return self.frejm

    def set_tocke(self, tocke):
        self.tocke = tocke

    def get_tocke(self):
        return self.tocke

    def set_startIndeks(self, start):
        self.startIndeks = start

    def get_startIndeks(self):
        return self.startIndeks

    def set_rezultat(self, mapa):
        self.rezultat = mapa

    def get_rezultat(self):
        return self.rezultat
################################################################################
################################################################################
class KonverterTabData(object):
    def __init__(self, frejm=None, startIndeks=0, tocke=None, cNOx50=0.0, cNOx95=0.0):
        self.rezultat = None
        self.naziv = 'konverter'
        self.frejm = frejm
        self.startIndeks = startIndeks
        if tocke == None:
            self.tocke = []
        else:
            self.tocke = tocke
        self.cNOx50 = cNOx50
        self.cNOx95 = cNOx95

    def get_naziv(self):
        return self.naziv

    def set_frejm(self, frejm):
        self.frejm = frejm

    def get_frejm(self):
        return self.frejm

    def set_tocke(self, tocke):
        self.tocke = tocke

    def get_tocke(self):
        return self.tocke

    def set_startIndeks(self, start):
        self.startIndeks = start

    def get_startIndeks(self):
        return self.startIndeks

    def set_cNOc50(self, x):
        self.cNOx50 = x

    def get_cNOc50(self):
        return self.cNOx50

    def set_cNOc95(self, x):
        self.cNOx95 = x

    def get_cNOc95(self):
        return self.cNOx95

    def set_rezultat(self, mapa):
        self.rezultat = mapa

    def get_rezultat(self):
        return self.rezultat
################################################################################
################################################################################
class DataStore(object):
    """
    Ova klasa predstavlja interni dokument pojedinog prozora umjeravanja.
    Objekt cuva state pojedinih elemenata za jedno umjeravanje.
    """
    def __init__(self, uredjaj=None, dilucije=None, generatori=None, postaje=None, cfg=None):
        self.uredjaj = uredjaj
        self.dilucije = dilucije
        self.generatori = generatori
        self.postaje = postaje
        #config file
        if isinstance(cfg, MainKonfig):
            self.konfig = cfg
        else:
            config = configparser.ConfigParser()
            config.read(cfg, encoding='utf-8')
            self.konfig = MainKonfig(cfg=config)
        ###TAB POSTAVKE###
        self.izabraniOpseg = 0.0 #s tim se racuna
        self.checkUmjeravanje = True
        self.checkPonovljivost = False
        self.checkLinearnost = False
        self.checkOdaziv = False
        self.chekcKonverter = False
        self.isNOx = False
        self.izabranaPostaja = str(self.get_uredjaj().get_lokacija())
        self.izabranaDilucija = 'n/a'
        self.izabraniGenerator = 'n/a'
        self.izabranaVrstaCRM = 'n/a'
        self.koncentracijaCRM = 1.0
        self.sljedivostCRM = ''
        self.UCRM = 2.0
        self.izabranaTemperatura = 0.0
        self.izabranaVlaga = 0.0
        self.izabraniTlak = 0.0
        self.izabranaOznakaIzvjesca = 'n/a'
        self.izabranaRevizijaIzvjesca = 'n/a'
        self.izabraniBrojObrasca = 'n/a'
        self.izabranaNormaObrasca = 'n/a'
        self.izabraniOpisMetode = 'n/a'
        self.izabranaNapomena = ''
        self.izabraniDatum = ''
        self.izabranaMjernaJedinica = self.get_uredjaj().get_analitickaMetoda().get_jedinica()
        self.cNOx50 = float(self.konfig.get_konfig_element('KONVERTER_META', 'cNOX50'))
        self.cNOx95 = float(self.konfig.get_konfig_element('KONVERTER_META', 'cNOX95'))
        ###OSTALI TABOVI###
        self.tabData = {}
        try:
            opseg = self.get_uredjaj().get_analitickaMetoda().get_o()
            minlimit = opseg * 0.1
            maxlimit = opseg * 0.9
        except Exception:
            minlimit = 10.0
            maxlimit = 90.0
        komponente = list(self.get_uredjaj().get_komponente().keys())
        if 'NOx' in komponente:
            self.tabData['NO'] = RezultatTabData('NO', tocke=self.init_tockeUmjeravanja())
            self.tabData['NOx'] = RezultatTabData('NOx', tocke=self.init_tockeUmjeravanja())
            self.tabData['NO-odaziv'] = OdazivTabData('NO-odaziv', minlimit=minlimit, maxlimit=maxlimit)
            self.tabData['NOx-odaziv'] = OdazivTabData('NOx-odaziv', minlimit=minlimit, maxlimit=maxlimit)
            self.tabData['konverter'] = KonverterTabData(tocke=self.init_tockeKonverter(), cNOx50=self.cNOx50, cNOx95=self.cNOx95)
        else:
            for komponenta in komponente:
                tmp = "-".join([komponenta, 'odaziv'])
                self.tabData[komponenta] = RezultatTabData(komponenta, tocke=self.init_tockeUmjeravanja())
                self.tabData[tmp] = OdazivTabData(tmp, minlimit=minlimit, maxlimit=maxlimit)
        #inicijalni setup iz konfiga prodji kroz komponente i citaj konfig
        self.init_from_konfig()
################################################################################
    def init_tockeUmjeravanja(self):
        return self.konfig.get_tockeUmjeravanja()

    def init_tockeKonverter(self):
        return self.konfig.get_tockeKonverter()

    def get_tocke(self, naziv):
        return self.tabData[naziv].get_tocke()

    def set_tocke(self, naziv, tocke):
        self.tabData[naziv].set_tocke(tocke)

    def init_from_konfig(self):
        komponente = self.uredjaj.get_listu_komponenti()
        if 'NOx' in komponente:
            self.setup_konfig_elements('NOx')
            self.isNOx = True
        elif 'SO2' in komponente:
            self.setup_konfig_elements('SO2')
        elif 'CO' in komponente:
            self.setup_konfig_elements('CO')
        elif 'O3' in komponente:
            self.setup_konfig_elements('O3')
        elif 'C6H6' in komponente:
            self.setup_konfig_elements('BTX')

    def setup_konfig_elements(self, section):
        """Metoda postavlja elemente za report u membere koje pokusava ucitati iz
        konfiga."""
        #izvor
        try:
            izvor = self.konfig.get_konfig_element(section, 'izvor')
            self.set_izabranaVrstaCRM(izvor)
        except Exception as err:
            logging.warning(str(err))
        try:
            revizija = self.konfig.get_konfig_element(section, 'revizija')
            self.set_izabranaRevizijaIzvjesca(revizija)
        except Exception as err:
            logging.warning(str(err))
        try:
            brojObrasca = self.konfig.get_konfig_element(section, 'oznaka')
            self.set_izabraniBrojObrasca(brojObrasca)
        except Exception as err:
            logging.warning(str(err))
        try:
            norma = self.konfig.get_konfig_element(section, 'norma')
            self.set_izabranaNormaObrasca(norma)
        except Exception as err:
            logging.warning(str(err))
        try:
            opisMetode = self.konfig.get_konfig_element(section, 'naziv')
            self.set_izabraniOpisMetode(opisMetode)
        except Exception as err:
            logging.warning(str(err))

    def set_izabranaMjernaJedinica(self, x):
        """Setter izabrane mjerne jedinice"""
        x = str(x)
        if x != self.izabranaMjernaJedinica:
            self.izabranaMjernaJedinica = x

    def get_izabranaMjernaJedinica(self):
        """Getter izabrane mjerne jedinice"""
        return self.izabranaMjernaJedinica

    def set_checkKonverter(self, x):
        """setter provjere konvertera"""
        x = bool(x)
        if x != self.chekcKonverter:
            self.chekcKonverter = x

    def get_checkKonverter(self):
        """getter provjere konvertera"""
        return self.chekcKonverter

    def set_checkOdaziv(self, x):
        """setter provjere odaziva"""
        x = bool(x)
        if x != self.checkOdaziv:
            self.checkOdaziv = x

    def get_checkOdaziv(self):
        """getter provjere odaziva"""
        return self.checkOdaziv

    def set_checkLinearnost(self, x):
        """setter provjere linearnosti"""
        x = bool(x)
        if x != self.checkLinearnost:
            self.checkLinearnost = x

    def get_checkLinearnost(self):
        """getter provjere linearnosti"""
        return self.checkLinearnost

    def set_checkPonovljivost(self, x):
        """setter provjere ponovljivosti"""
        x = bool(x)
        if x != self.checkPonovljivost:
            self.checkPonovljivost = x

    def get_checkPonovljivost(self):
        """getter provjere ponovljivosti"""
        return self.checkPonovljivost

    def set_checkUmjeravanje(self, x):
        """setter provjere umjeravanja"""
        x = bool(x)
        if x != self.checkUmjeravanje:
            self.checkUmjeravanje = x

    def get_checkUmjeravanje(self):
        """getter provjere umjeravanja"""
        return self.checkUmjeravanje

    def set_izabraniDatum(self, x):
        """Setter izabranog datuma za report"""
        x = str(x)
        if x != self.izabraniDatum:
            self.izabraniDatum = x

    def get_izabraniDatum(self):
        """Getter izabranog datuma za report"""
        return self.izabraniDatum

    def set_izabranaNapomena(self, x):
        """Setter izabranog teksta napomene za report"""
        x = str(x)
        if x != self.izabranaNapomena:
            self.izabranaNapomena = x

    def get_izabranaNapomena(self):
        """Getter izabranog teksta napomene za report"""
        return self.izabranaNapomena

    def set_izabraniOpseg(self, x):
        """Setter opsega s kojim se racuna"""
        x = float(x)
        if x != self.izabraniOpseg:
            self.izabraniOpseg = x

    def get_izabraniOpseg(self):
        """Getter opsega s kojim se racuna"""
        return self.izabraniOpseg

    def set_izabraniOpisMetode(self, x):
        """Setter opisa metode za report"""
        x = str(x)
        if x != self.izabraniOpisMetode:
            self.izabraniOpisMetode = x

    def get_izabraniOpisMetode(self):
        """Getter opisa metode za report"""
        return self.izabraniOpisMetode

    def set_izabranaNormaObrasca(self, x):
        """Setter norme za report"""
        x = str(x)
        if x != self.izabranaNormaObrasca:
            self.izabranaNormaObrasca = x

    def get_izabranaNormaObrasca(self):
        """Getter norme za report"""
        return self.izabranaNormaObrasca

    def set_izabraniBrojObrasca(self, x):
        """Setter broja obrasca za report"""
        x = str(x)
        if x != self.izabraniBrojObrasca:
            self.izabraniBrojObrasca = x

    def get_izabraniBrojObrasca(self):
        """Getter broja obrasca za report"""
        return self.izabraniBrojObrasca

    def set_izabranaRevizijaIzvjesca(self, x):
        """Setter revizije izvjesca za report"""
        x = str(x)
        if x != self.izabranaRevizijaIzvjesca:
            self.izabranaRevizijaIzvjesca = x

    def get_izabranaRevizijaIzvjesca(self):
        """Getter revizije izvjesca za report"""
        return self.izabranaRevizijaIzvjesca

    def set_izabranaOznakaIzvjesca(self, x):
        """Setter oznake izvjesca za report"""
        x = str(x)
        if x != self.izabranaOznakaIzvjesca:
            self.izabranaOznakaIzvjesca = x

    def get_izabranaOznakaIzvjesca(self):
        """Getter oznake izvjesca za report"""
        return self.izabranaOznakaIzvjesca

    def set_izabranaTemperatura(self, x):
        """Setter izabrane temperature"""
        x = float(x)
        if x != self.izabranaTemperatura:
            self.izabranaTemperatura = x

    def get_izabranaTemperatura(self):
        """Getter izabrane temperature"""
        return self.izabranaTemperatura

    def set_izabranaVlaga(self, x):
        """Setter izabrane relativne vlage"""
        x = float(x)
        if x != self.izabranaVlaga:
            self.izabranaVlaga = x

    def get_izabranaVlaga(self):
        """Getter izabrane relativne vlage"""
        return self.izabranaVlaga

    def set_izabraniTlak(self, x):
        """Setter izabranog tlaka zraka"""
        x = float(x)
        if x != self.izabraniTlak:
            self.izabraniTlak = x

    def get_izabraniTlak(self):
        """Getter izabranog tlaka zraka"""
        return self.izabraniTlak

    def set_sljedivostCRM(self, x):
        """setter sljedivosti CRM"""
        if x != self.sljedivostCRM:
            self.sljedivostCRM = x

    def get_sljedivostCRM(self):
        """getter sljedivosti CRM"""
        return self.sljedivostCRM

    def set_UCRM(self, x):
        """Setter U CRM"""
        if x != self.UCRM:
            self.UCRM = x

    def get_UCRM(self):
        """Getter U CRM"""
        return self.UCRM

    def set_koncentracijaCRM(self, x):
        """Setter koncentracije CRM"""
        if x != self.koncentracijaCRM:
            self.koncentracijaCRM = x

    def get_koncentracijaCRM(self):
        """Getter koncentracije CRM"""
        return self.koncentracijaCRM

    def set_izabranaVrstaCRM(self, x):
        """Setter izabrane vrste CRM"""
        if x != self.izabranaVrstaCRM:
            self.izabranaVrstaCRM = x

    def get_izabranaVrstaCRM(self):
        """Getter izabrane vrste CRM"""
        return self.izabranaVrstaCRM

    def set_uredjaj(self, x):
        """Setter uredjaja"""
        if x != self.uredjaj and isinstance(x, Uredjaj):
            self.uredjaj = x

    def get_uredjaj(self):
        """Getter uredjaja"""
        return self.uredjaj

    def get_konfig(self):
        """setter konfig objekta"""
        return self.konfig

    def set_dilucije(self, x):
        """Setter kalibracijske jedinice"""
        if x != self.dilucije and isinstance(x, dict):
            self.dilucije = x

    def get_dilucije(self):
        """Getter kalibracijske jedinice"""
        return self.dilucije

    def get_listu_dilucija(self):
        """Getter liste dilucijskih jedinica"""
        return sorted(list(self.dilucije.keys()))

    def set_izabranaDilucija(self, x):
        """Setter izabrane dilucije (kljuca u mapi pod kojim je spremljen objekt)"""
        if x in self.dilucije.keys() and x != self.izabranaDilucija:
            self.izabranaDilucija = x

    def get_izabranaDilucija(self):
        """Getter izabrane dilucije (kljuca u mapi pod kojim je spremljen objekt)"""
        return self.izabranaDilucija

    def get_objekt_izabrane_dilucije(self, key):
        """Getter objekta iz mape dilucija. Ulazni parametar je kljuc pod kojim je
        objekt spremljen u mapi dilucija."""
        if key in self.dilucije.keys():
            return self.dilucije[key]

    def set_generatori(self, x):
        """Setter generatora cistog zraka"""
        if x != self.generatori and isinstance(x, dict):
            self.generatori = x

    def get_generatori(self):
        """Getter generatora cistog zraka"""
        return self.generatori

    def get_listu_generatora(self):
        """Getter liste generatora cistog zraka"""
        return sorted(list(self.generatori.keys()))

    def set_izabraniGenerator(self, key):
        """Setter izabranog generatora cistog zraka (kljuc u mapi pod kojim je spremljen objekt)"""
        if key in self.generatori.keys() and key != self.izabraniGenerator:
            self.izabraniGenerator = key

    def get_izabraniGenerator(self):
        """Getter izabranog generatora cistog zraka (kljuc u mapi pod kojim je spremljen objekt)"""
        return self.izabraniGenerator

    def get_objekt_izabranog_generatora(self, key):
        """Getter objekta iz mape generatora. Ulazni parametar je kljuc pod kojim je
        objekt spremljen u mapi generatora cistog zraka"""
        if key in self.generatori.keys():
            return self.generatori[key]

    def set_postaje(self, x):
        """Setter postaja"""
        if x != self.postaje and isinstance(x, list):
            self.postaje = x

    def get_postaje(self):
        """Getter postaja"""
        return self.postaje

    def set_izabranaPostaja(self, x):
        """setter izabrane postaje"""
        if x != self.izabranaPostaja:
            self.izabranaPostaja = x

    def get_izabranaPostaja(self):
        """getter izabrane postaje"""
        return self.izabranaPostaja

    def set_cNOx50(self, x):
        """setter metapodatka cNOx50 za provjeru konvertera"""
        if x != self.cNOx50:
            self.cNOx50 = x

    def get_cNOx50(self):
        """getter metapodatka cNOx50 za provjeru konvertera"""
        return self.cNOx50

    def set_cNOx95(self, x):
        """setter metapodatka cNOx95 za provjeru konvertera"""
        if x != self.cNOx95:
            self.cNOx95 = x

    def get_cNOx95(self):
        """getter metapodatka cNOx95 za provjeru konvertera"""
        return self.cNOx95
################################################################################
    def serialize(self):
        """
        metoda serijalizira cijeli datastore uz pomoc modula pickle. output
        """
        out = pickle.dumps(self)
        return out
################################################################################