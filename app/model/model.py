# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 12:04:06 2015

@author: DHMZ-Milic
"""
import logging
import pickle
import copy
import numpy as np
import pandas as pd
from PyQt4 import QtGui, QtCore
from app.model.konfig_klase import Tocka
import app.model.pomocne_funkcije as helperi


class DokumentModel(QtCore.QObject):
    """
    Dokument model za umjeravanje
    """
    def __init__(self, cfg=None, parent=None):
        QtCore.QObject.__init__(self, parent=parent)
        self.cfg = cfg  # MainKonfig objekt
        """svaki od membera ispod ima vlastiti setter i getter"""
        self.izabraniUredjaj = ''
        self.izabranaPostaja = ''
        self.izabraniPathCSV = ''
        self.mjernaJedinica = 'n/a'
        self.init_tockeUmjeravanja() #self.tockeUmjeravanja
        self.init_tockeKonverter() #self.tockeKonverter
        self.postaje = {}
        self.uredjaji = {}
        self.listaMjerenja = []
        self.listaDilucija = []
        self.listaZrak = []
        self.izabranoMjerenje = ''
        self.izabranaDilucija = ''
        self.izabraniZrak = ''
        self.opseg = 1.0
        self.provjeraLinearnosti = False
        self.provjeraKonvertera = False
        self.cNOx50 = 200.0
        self.cNOx95 = 180.0
        self.rezultatUmjeravanja = self.generiraj_nan_frejm_rezultata_umjeravanja()
        self.siroviPodaci = pd.DataFrame()
        self.siroviPodaciStart = 0
        self.konverterPodaci = pd.DataFrame()
        self.konverterPodaciStart = 0
        self.konverterRezultat = self.generiraj_nan_frejm_rezultata_konvertera()
        self.izvorCRM = ''
        self.koncentracijaCRM = 1.0
        self.sljedivostCRM = 2.0
        self.proizvodjacDilucija = ''
        self.sljedivostDilucija = ''
        self.proizvodjacCistiZrak = ''
        self.sljedivostCistiZrak = 0.0
        self.norma = ''
        self.oznakaIzvjesca = ''
        self.brojObrasca = ''
        self.revizija = ''
        self.datumUmjeravanja = ''
        self.temperatura = 0.0
        self.vlaga = 0.0
        self.tlak = 0.0
        self.napomena = ''
        self.pocetakUmjeravanja = ''
        self.krajUmjeravanja = ''
        self.parametriRezultata = [] #lista: srz, srs, rz, rmax, ec
        self.slopeData = [np.NaN, np.NaN, np.NaN, np.NaN]
        self.reportSlope = {'n/a':[np.NaN, np.NaN, np.NaN, np.NaN]}
        self.listaEfikasnostiKonvertera = [np.NaN, np.NaN, np.NaN, np.NaN]
        #dodatne informacije o uredjaju
        self.oznakaModelaUredjaja = ''
        self.proizvodjacUredjaja = ''
        #inicijalizacija postaja i uredjaja sa REST servisa
        self.init_uredjaje_i_postaje_sa_REST()

    def dict_to_dokument(self, mapa):
        """
        Metoda je zaduzena za upisivanje podataka iz mape u membere.

        P.S.
        Load order stvari je bitan. npr. umjerne tocke se moraju definirati
        prije postavljanja sirovih podataka jer setter za sirove podatke
        indirektno ovisi o umjernim tockama
        """
        self.set_postaje(mapa['postaje'])
        self.set_uredjaji(mapa['uredjaji'])
        self.set_listaMjerenja(mapa['listaMjerenja'], recalculate=False)
        self.set_listaDilucija(mapa['listaDilucija'])
        self.set_listaZrak(mapa['listaZrak'])
        #potrebno je rekonstruirati objekt Tocka()
        umjerneTocke = []
        tocke = mapa['tockeUmjeravanja']
        for tocka in tocke:
            dot = Tocka()
            dot.ime = tocka['ime']
            dot.indeksi = tocka['indeksi']
            dot.crefFaktor = tocka['crefFaktor']
            r, g, b, a = tocka['rgba']
            dot.boja = QtGui.QColor(r, g, b, a)
            umjerneTocke.append(dot)
        self.set_tockeUmjeravanja(umjerneTocke)
        konverterTocke = []
        tocke = mapa['tockeKonverter']
        for tocka in tocke:
            dot = Tocka()
            dot.ime = tocka['ime']
            dot.indeksi = tocka['indeksi']
            dot.crefFaktor = tocka['crefFaktor']
            r, g, b, a = tocka['rgba']
            dot.boja = QtGui.QColor(r, g, b, a)
            konverterTocke.append(dot)
        self.set_tockeKonverter(konverterTocke)
        self.set_siroviPodaciStart(mapa['siroviPodaciStart'], recalculate=False)
        self.set_siroviPodaci(mapa['siroviPodaci'])
        self.set_konverterPodaciStart(mapa['konverterPodaciStart'], recalculate=False)
        self.set_konverterPodaci(mapa['konverterPodaci'])
        self.set_izabraniUredjaj(mapa['izabraniUredjaj'])
        self.set_izabranaPostaja(mapa['izabranaPostaja'])
        self.set_izabraniPathCSV(mapa['izabraniPathCSV'])
        self.set_mjernaJedinica(mapa['mjernaJedinica'])
        self.set_izabranoMjerenje(mapa['izabranoMjerenje'], recalculate=False)
        self.set_izabranaDilucija(mapa['izabranaDilucija'], recalculate=False)
        self.set_izabraniZrak(mapa['izabraniZrak'], recalculate=False)
        self.set_provjeraLinearnosti(mapa['provjeraLinearnosti'], recalculate=False)
        self.set_provjeraKonvertera(mapa['provjeraKonvertera'], recalculate=False)
        self.set_cNOx50(mapa['cNOx50'])
        self.set_cNOx95(mapa['cNOx95'])

        self.set_proizvodjacDilucija(mapa['proizvodjacDilucija'])
        self.emit(QtCore.SIGNAL('promjena_proizvodjacDilucija(PyQt_PyObject)'),
                  self.proizvodjacDilucija)

        self.set_sljedivostDilucija(mapa['sljedivostDilucija'])
        self.emit(QtCore.SIGNAL('promjena_sljedivostDilucija(PyQt_PyObject)'),
                  self.sljedivostDilucija)

        self.set_proizvodjacCistiZrak(mapa['proizvodjacCistiZrak'])
        self.emit(QtCore.SIGNAL('promjena_proizvodjacCistiZrak(PyQt_PyObject)'),
                  self.proizvodjacCistiZrak)

        self.set_sljedivostCistiZrak(mapa['sljedivostCistiZrak'], recalculate=False)

        self.set_norma(mapa['norma'])
        self.emit(QtCore.SIGNAL('promjena_norma(PyQt_PyObject)'),
                  self.norma)

        self.set_oznakaIzvjesca(mapa['oznakaIzvjesca'])
        self.emit(QtCore.SIGNAL('promjena_oznakaIzvjesca(PyQt_PyObject)'),
                  self.oznakaIzvjesca)

        self.set_brojObrasca(mapa['brojObrasca'])
        self.emit(QtCore.SIGNAL('promjena_brojObrasca(PyQt_PyObject)'),
                  self.brojObrasca)

        self.set_revizija(mapa['revizija'])
        self.emit(QtCore.SIGNAL('promjena_revizija(PyQt_PyObject)'),
                  self.revizija)

        self.set_datumUmjeravanja(mapa['datumUmjeravanja'])
        self.emit(QtCore.SIGNAL('promjena_datumUmjeravanja(PyQt_PyObject)'),
                  self.datumUmjeravanja)

        self.set_temperatura(mapa['temperatura'])
        self.set_vlaga(mapa['vlaga'])
        self.set_tlak(mapa['tlak'])

        self.set_napomena(mapa['napomena'])
        self.emit(QtCore.SIGNAL('promjena_napomena(PyQt_PyObject)'),
                  self.napomena)

        self.set_pocetakUmjeravanja(mapa['pocetakUmjeravanja'])
        self.set_krajUmjeravanja(mapa['krajUmjeravanja'])
        self.set_rezultatUmjeravanja(mapa['rezultatUmjeravanja'])
        self.set_konverterRezultat(mapa['konverterRezultat'])

        self.set_izvorCRM(mapa['izvorCRM'])
        self.emit(QtCore.SIGNAL('promjena_izvorCRM(PyQt_PyObject)'),
                  self.izvorCRM)

        self.set_koncentracijaCRM(mapa['koncentracijaCRM'], recalculate=False)
        self.set_sljedivostCRM(mapa['sljedivostCRM'], recalculate=False)
        self.set_listaEfikasnostiKonvertera(mapa['listaEfikasnostiKonvertera'])
        self.set_slopeData(mapa['slopeData'])
        self.set_reportSlope(mapa['reportSlope'])
        self.set_parametriRezultata(mapa['parametriRezultata'])
        self.set_opseg(mapa['opseg'], recalculate=False)
        self.set_oznakaModelaUredjaja(mapa['oznakaModelaUredjaja'])
        self.set_proizvodjacUredjaja(mapa['proizvodjacUredjaja'])

        self.signal_recalculate()

    def dokument_to_dict(self):
        """
        Metoda je zaduzena za generiranje mape sa memberima objekta radi
        lakse serijalizacije i generiranja fileova.
        """
        output = {}
        output['listaEfikasnostiKonvertera'] = self.listaEfikasnostiKonvertera
        output['slopeData'] = self.slopeData
        output['reportSlope'] = self.reportSlope
        output['izabraniUredjaj'] = self.izabraniUredjaj
        output['izabranaPostaja'] = self.izabranaPostaja
        output['izabraniPathCSV'] = self.izabraniPathCSV
        output['mjernaJedinica'] = self.mjernaJedinica
        output['postaje'] = self.postaje
        output['uredjaji'] = self.uredjaji
        output['listaMjerenja'] = self.listaMjerenja
        output['listaDilucija'] = self.listaDilucija
        output['listaZrak'] = self.listaZrak
        output['izabranoMjerenje'] = self.izabranoMjerenje
        output['izabranaDilucija'] = self.izabranaDilucija
        output['izabraniZrak'] = self.izabraniZrak
        output['provjeraLinearnosti'] = self.provjeraLinearnosti
        output['provjeraKonvertera'] = self.provjeraKonvertera
        output['cNOx50'] = self.cNOx50
        output['cNOx95'] = self.cNOx95
        output['rezultatUmjeravanja'] = self.rezultatUmjeravanja
        output['siroviPodaci'] = self.siroviPodaci
        output['siroviPodaciStart'] = self.siroviPodaciStart
        output['konverterPodaci'] = self.konverterPodaci
        output['konverterPodaciStart'] = self.konverterPodaciStart
        output['konverterRezultat'] = self.konverterRezultat
        output['izvorCRM'] = self.izvorCRM
        output['koncentracijaCRM'] = self.koncentracijaCRM
        output['sljedivostCRM'] = self.sljedivostCRM
        output['proizvodjacDilucija'] = self.proizvodjacDilucija
        output['sljedivostDilucija'] = self.sljedivostDilucija
        output['proizvodjacCistiZrak'] = self.proizvodjacCistiZrak
        output['sljedivostCistiZrak'] = self.sljedivostCistiZrak
        output['norma'] = self.norma
        output['oznakaIzvjesca'] = self.oznakaIzvjesca
        output['brojObrasca'] = self.brojObrasca
        output['revizija'] = self.revizija
        output['datumUmjeravanja'] = self.datumUmjeravanja
        output['temperatura'] = self.temperatura
        output['vlaga'] = self.vlaga
        output['tlak'] = self.tlak
        output['napomena'] = self.napomena
        output['pocetakUmjeravanja'] = self.pocetakUmjeravanja
        output['krajUmjeravanja'] = self.krajUmjeravanja
        #nije moguce seirjalizirati QObject sa pickle, workaround
        output['tockeUmjeravanja'] = []
        for tocka in self.tockeUmjeravanja:
            obj = {}
            obj['ime'] = tocka.ime
            obj['indeksi'] = tocka.indeksi
            obj['crefFaktor'] = tocka.crefFaktor
            obj['rgba'] = (tocka.boja.red(), tocka.boja.green(), tocka.boja.blue(), tocka.boja.alpha())
            output['tockeUmjeravanja'].append(obj)
        output['tockeKonverter'] = []
        for tocka in self.tockeKonverter:
            obj = {}
            obj['ime'] = tocka.ime
            obj['indeksi'] = tocka.indeksi
            obj['crefFaktor'] = tocka.crefFaktor
            obj['rgba'] = (tocka.boja.red(), tocka.boja.green(), tocka.boja.blue(), tocka.boja.alpha())
            output['tockeKonverter'].append(obj)
        output['parametriRezultata'] = self.parametriRezultata
        output['opseg'] = self.opseg
        output['oznakaModelaUredjaja'] = self.oznakaModelaUredjaja
        output['proizvodjacUredjaja'] = self.proizvodjacUredjaja
        return output

    def save_dokument(self, filename):
        """
        Metoda je zaduzena sa serijalizaciju dokumenta u file koristeci pickle.
        Sastavlja se mapa postojecih polja koja se serijalizira.
        """
        mapa = self.dokument_to_dict()
        if filename:
            with open(filename, mode='wb') as fajl:
                try:
                    pickle.dump(mapa, fajl)
                except Exception as err:
                    logging.error(str(err), exc_info=True)
                    QtGui.QMessageBox.information(self, 'Problem', 'Spremanje datoteke nije uspjelo.')

    def load_dokument(self, filename=None):
        """
        Metoda je zaduzena za ucitavanje dokumenta. Parametar filename sluzi za
        ucitavanje spremljenog dokumenta. Ako filename=None, koristi se konfig
        file da se popune neke vrijednosti.
        """
        if filename == None:
            #stvari iz konfiga
            lz = self.cfg.get_listu_cistiZrak()
            self.set_listaZrak(lz)
            ld = self.cfg.get_listu_dilucija()
            self.set_listaDilucija(ld)
            izborZrak = lz[0]
            self.set_izabraniZrak(izborZrak)
            izborDilucija = ld[0]
            self.set_izabranaDilucija(izborDilucija)
            try:
                t1 = self.cfg.get_konfig_element(str(izborDilucija), 'MFC_NUL_Plin_sljedivost')
                t2 = self.cfg.get_konfig_element(str(izborDilucija), 'MFC_KAL_Plin_sljedivost')
                t3 = self.cfg.get_konfig_element(str(izborDilucija), 'GENERATOR_OZONA_sljedivost')
                tekst = ", ".join([t1, t2, t3])
            except AttributeError as err:
                logging.error(str(err), exc_info=True)
                tekst = ''
            self.set_sljedivostDilucija(tekst)
            self.emit(QtCore.SIGNAL('promjena_sljedivostDilucija(PyQt_PyObject)'),
                      self.sljedivostDilucija)
            try:
                tekst = self.cfg.get_konfig_element(str(izborDilucija), 'proizvodjac')
            except AttributeError as err:
                logging.error(str(err), exc_info=True)
                tekst = ''
            self.set_proizvodjacDilucija(tekst)
            self.emit(QtCore.SIGNAL('promjena_proizvodjacDilucija(PyQt_PyObject)'),
                      self.proizvodjacDilucija)
            try:
                tekst = self.cfg.get_konfig_element(str(izborZrak), 'proizvodjac')
            except AttributeError as err:
                logging.error(str(err), exc_info=True)
                tekst = ''
            self.set_proizvodjacCistiZrak(tekst)
            self.emit(QtCore.SIGNAL('promjena_proizvodjacCistiZrak(PyQt_PyObject)'),
                      self.proizvodjacCistiZrak)

            self.set_rezultatUmjeravanja(self.generiraj_nan_frejm_rezultata_umjeravanja())
            self.set_konverterRezultat(self.generiraj_nan_frejm_rezultata_konvertera())
            self.emit(QtCore.SIGNAL('postavi_usporedna_mjerenja'))
        else:
            with open(filename, mode='rb') as fajl:
                try:
                    mapa = pickle.load(fajl)
                    self.dict_to_dokument(mapa)
                    self.emit(QtCore.SIGNAL('postavi_usporedna_mjerenja'))
                except Exception as err:
                    logging.error(str(err), exc_info=True)
                    QtGui.QMessageBox.information(self, 'Problem', 'Ucitavanje datoteke nije uspjelo.')

    def signal_recalculate(self):
        """metoda signalizira potrebu za ponovnim racunanjem rezultata"""
        self.emit(QtCore.SIGNAL('dokument_request_recalculate'))

    def set_opseg(self, x, recalculate=True):
        """Setter max opsega mjerenja. Ulazna vrijednost je tipa float"""
        x = float(x)
        if x != self.opseg:
            self.opseg = x
            output = [self.opseg, recalculate]
            self.emit(QtCore.SIGNAL('promjena_opseg(PyQt_PyObject)'),
                      output)

    def get_opseg(self):
        """Getter max opsega mjerenja"""
        return self.opseg

    def set_parametriRezultata(self, x):
        """Setter parametara umjeravanja. Ulazna vrijednost je dict parametara
        sa kljucevima 'srs', 'srz', 'prilagodbaA', ..."""
        if x != self.parametriRezultata:
            self.parametriRezultata = x
            self.emit(QtCore.SIGNAL('promjena_parametriRezultata(PyQt_PyObject)'),
                      self.parametriRezultata)

    def get_parametriRezultata(self):
        """Getter dicta parametara rezultata."""
        return self.parametriRezultata

    def set_reportSlope(self, x):
        """setter dicta za pdf report prilagodbe rezultata ako ima vise plinova.
        x je dictionary,  {plin:[slope, offset, prilagodbaA, prilagodbaB]}.
        Svi elementi liste su float, plin je tipa string"""
        self.reportSlope = copy.deepcopy(x)

    def get_reportSlope(self):
        """getter dicta za pdf report prilagodbe rezultata"""
        return self.reportSlope

    def set_slopeData(self, x):
        """Seter liste sa slope parametrima za umjeravanje (lista float).
        [slope, offset, prilagodbaA, prilagodbaB]"""
        if x != self.slopeData:
            self.slopeData = x
            self.emit(QtCore.SIGNAL('promjena_slopeData(PyQt_PyObject)'),
                      self.slopeData)

    def get_slopeData(self):
        """Getter liste sa slope parametrima za umjeravanje"""
        return self.slopeData

    def zamjeni_umjernu_tocku(self, indeks, tocka):
        """
        Metoda mjenja postojecu tocku sa zadanom tockom. Lokacija je zadana
        sa indeksom u listi
        """
        tocke = copy.deepcopy(self.tockeUmjeravanja)
        tocke[indeks] = tocka
        self.set_tockeUmjeravanja(tocke)

    def dodaj_umjernu_tocku(self):
        """
        Metoda dodaje tocku na popis tocaka. Dodaje je iza vec definiranih
        tocaka, ukupno 30 indeksa, prvih 15 zanemarenih, random boja.

        Nakon promjene emitira se informacija da je doslo do promjene
        """
        ime = 'TOCKA'+str(len(self.tockeUmjeravanja)+1)
        indeks = max([max(tocka.indeksi) for tocka in self.tockeUmjeravanja])
        start = indeks+15
        end = start+15
        cref = 0.0
        novaTocka = Tocka(ime=ime, start=start, end=end, cref=cref)
        self.tockeUmjeravanja.append(novaTocka)
        self.set_vremenske_granice_umjernih_tocaka()
        self.emit(QtCore.SIGNAL('promjena_tockeUmjeravanja'))

    def makni_umjernu_tocku(self, indeks):
        """
        Metoda brise tocku zadanu indeksom iz liste self.umjerneTocke.
        Metoda mjenja nazive ostalih tocaka radi konzistencije.

        Nakon promjene emitira se informacija da je doslo do promjene
        """
        try:
            self.tockeUmjeravanja.pop(indeks)
            #rename tocke
            for i in range(len(self.tockeUmjeravanja)):
                self.tockeUmjeravanja[i].ime = 'TOCKA'+str(i+1)
                self.set_vremenske_granice_umjernih_tocaka()
            self.emit(QtCore.SIGNAL('promjena_tockeUmjeravanja'))
        except IndexError as err:
            logging.error(str(err), exc_info=True)

    def set_tockeUmjeravanja(self, x):
        """Setter liste tockaka umjeravanja. Ulazni parametar je lista objekata
        (Tocka)"""
        if x != self.tockeUmjeravanja:
            self.tockeUmjeravanja = x
            self.set_vremenske_granice_umjernih_tocaka()
            self.emit(QtCore.SIGNAL('redraw_rezultateUmjeravanja'))
            #self.emit(QtCore.SIGNAL('promjena_tockeUmjeravanja'))

    def get_tockeUmjeravanja(self):
        """Getter liste tocaka umjeravanja"""
        return self.tockeUmjeravanja

    def set_tockeKonverter(self, x):
        """Setter liste tocaka za provjeru konvertera. Ulazni parametar je lista
        objekata (Tocka)"""
        if x != self.tockeKonverter:
            self.tockeKonverter = x
            self.emit(QtCore.SIGNAL('promjena_tockeKonverter'))

    def get_tockeKonverter(self):
        """Getter tocaka za provjeru konvertera."""
        return self.tockeKonverter

    def init_tockeUmjeravanja(self, tocke=None):
        """
        Inicijalizacija umjernih tocaka. Keyword argment tocke definira da li
        koristimo postojece tocke, ili radimo novu listu iz konfiga.
        """
        if tocke == None:
            self.tockeUmjeravanja = self.cfg.get_tockeUmjeravanja()
        else:
            self.tockeUmjeravanja = tocke
        self.emit(QtCore.SIGNAL('promjena_tockeUmjeravanja'))

    def init_tockeKonverter(self, tocke=None):
        """
        Inicijalizacija tocaka za provjeru konvertera. Keyword argument tocke
        definira da li koristimo postojece tocke, ili radimo novu listu iz konfiga.
        """
        if tocke == None:
            self.tockeKonverter = self.cfg.get_tockeKonverter()
        else:
            self.tockeKonverter = tocke
        self.emit(QtCore.SIGNAL('promjena_tockeKonverter'))

    def set_krajUmjeravanja(self, x):
        """Setter kraja umjeravanja (vrijeme). Ulazni parametar je string"""
        x = str(x)
        if x != self.krajUmjeravanja:
            self.krajUmjeravanja = x
            self.emit(QtCore.SIGNAL('promjena_krajUmjeravanja(PyQt_PyObject)'),
                      self.krajUmjeravanja)

    def get_krajUmjeravanja(self):
        """Getter kraja umjeravanja (vrijeme)"""
        return self.krajUmjeravanja

    def set_pocetakUmjeravanja(self, x):
        """Setter pocetka umjeravanja (vrijeme). Ulazni parametar je string"""
        x = str(x)
        if x != self.pocetakUmjeravanja:
            self.pocetakUmjeravanja = x
            self.emit(QtCore.SIGNAL('promjena_pocetakUmjeravanja(PyQt_PyObject)'),
                      self.pocetakUmjeravanja)

    def get_pocetakUmjeravanja(self):
        """Getter pocetka umjeravanja (vrijeme)"""
        return self.pocetakUmjeravanja

    def set_napomena(self, x):
        """Setter napomene umjeravanja. Ulazna vrijednost je string"""
        x = str(x)
        if x != self.napomena:
            self.napomena = x

    def get_napomena(self):
        """Getter napomena umjeravanja"""
        return self.napomena

    def set_tlak(self, x):
        """Setter okolisnih uvijeta, tlak. Ulazna vrijednost je float"""
        x = float(x)
        if x != self.tlak:
            self.tlak = x
            self.emit(QtCore.SIGNAL('promjena_tlak(PyQt_PyObject)'),
                      self.tlak)

    def get_tlak(self):
        """Getter okolisnih uvijeta, tlak"""
        return self.tlak

    def set_vlaga(self, x):
        """Setter okolisnih uvijeta, vlaga. Ulazna vrijednost je float"""
        x = float(x)
        if x != self.vlaga:
            self.vlaga = x
            self.emit(QtCore.SIGNAL('promjena_vlaga(PyQt_PyObject)'),
                      self.vlaga)

    def get_vlaga(self):
        """Getter okolisnih uvijeta, vlaga."""
        return self.vlaga

    def set_temperatura(self, x):
        """Setter okolisnih uvijeta, temperatura. Ulazna vrijednost je float"""
        x = float(x)
        if x != self.temperatura:
            self.temperatura = x
            self.emit(QtCore.SIGNAL('promjena_temperatura(PyQt_PyObject)'),
                      self.temperatura)

    def get_temperatura(self):
        """Gettter okolisnih uvijeta, temperatura"""
        return self.temperatura

    def set_datumUmjeravanja(self, x):
        """Setter datuma umjeravanja. Ulazna vrijednost je string"""
        x = str(x)
        if x != self.datumUmjeravanja:
            self.datumUmjeravanja = x

    def get_datumUmjeravanja(self):
        """Getter datuma umjeravanja"""
        return self.datumUmjeravanja

    def set_revizija(self, x):
        """Setter broja revizije. Ulazni parametar je tipa string"""
        x = str(x)
        if x != self.revizija:
            self.revizija = x

    def get_revizija(self):
        """Getter broja revizije"""
        return self.revizija

    def set_brojObrasca(self, x):
        """Setter broja obrasca. Ulazni parametar je tipa string"""
        x = str(x)
        if x != self.brojObrasca:
            self.brojObrasca = x

    def get_brojObrasca(self):
        """Getter broj obrasca"""
        return self.brojObrasca

    def set_oznakaIzvjesca(self, x):
        """Setter oznake izvjesca. Ulazna vrijednost je tipa."""
        x = str(x)
        if x != self.oznakaIzvjesca:
            self.oznakaIzvjesca = x

    def get_oznakaIzvjesca(self):
        """Getter oznake izvjesca"""
        return self.oznakaIzvjesca

    def set_norma(self, x):
        """Setter norme mjerenja (norma + naziv). Ulazna vrijednost je tipa string."""
        x = str(x)
        if x != self.norma:
            self.norma = x

    def get_norma(self):
        """Getter norme mjerenja (norma + naziv)"""
        return self.norma

    def set_sljedivostCistiZrak(self, x, recalculate=True):
        """Setter sljedivosti generatora cistog zraka. Ulazna vrijednost je tipa
        float"""
        x = float(x)
        if x != self.sljedivostCistiZrak:
            self.sljedivostCistiZrak = x
            output = [self.sljedivostCistiZrak, recalculate]
            self.emit(QtCore.SIGNAL('promjena_sljedivostCistiZrak(PyQt_PyObject)'),
                      output)

    def get_sljedivostCistiZrak(self):
        """Getter sljedivosti generatora cistog zraka"""
        return self.sljedivostCistiZrak

    def set_proizvodjacCistiZrak(self, x):
        """Setter proizvodjaca generatora cistog zraka. Ulazna vrijednost je tipa
        string"""
        x = str(x)
        if x != self.proizvodjacCistiZrak:
            self.proizvodjacCistiZrak = x

    def get_proizvodjacCistiZrak(self):
        """Getter proizvodjaca generatora cistog zraka"""
        return self.proizvodjacCistiZrak

    def set_sljedivostDilucija(self, x):
        """Setter sljedivosti dilucijske (kalibracijske) jedinice. Ulazna vrijednost
        je tipa string"""
        x = str(x)
        if x != self.sljedivostDilucija:
            self.sljedivostDilucija = x

    def get_sljedivostDilucija(self):
        """Getter sljedivosti dilucijske (kalibracijske) jedinice"""
        return self.sljedivostDilucija

    def set_proizvodjacDilucija(self, x):
        """Setter proizvodjaca dilucijske (kalibracijske) jedinice. Ulazna vrijednost
        je tipa string"""
        x = str(x)
        if x != self.proizvodjacDilucija:
            self.proizvodjacDilucija = x


    def get_proizvodjacDilucija(self):
        """Getter proizvodjaca dilucijske (kalibracijske) jedinice."""
        return self.proizvodjacDilucija

    def set_sljedivostCRM(self, x, recalculate=True):
        """Setter sljedivosti certificiranog referentnog materijala. Ulazna vrijednost
        je tipa float"""
        x = float(x)
        if x != self.sljedivostCRM:
            self.sljedivostCRM = x
            output = [self.sljedivostCRM, recalculate]
            self.emit(QtCore.SIGNAL('promjena_sljedivostCRM(PyQt_PyObject)'),
                      output)

    def get_sljedivostCRM(self):
        """Getter sljedivosti certificiranog referentnog materijala"""
        return self.sljedivostCRM

    def set_koncentracijaCRM(self, x, recalculate=True):
        """Setter koncentracije certificiranog referentnog materijala. Ulazna
        vrijednost je tipa float"""
        x = float(x)
        if x != self.koncentracijaCRM:
            self.koncentracijaCRM = x
            output = [self.koncentracijaCRM, recalculate]
            self.emit(QtCore.SIGNAL('promjena_koncentracijaCRM(PyQt_PyObject)'),
                      output)

    def get_koncentracijaCRM(self):
        """Getter koncentracije certificiranog referentnog materijala"""
        return self.koncentracijaCRM

    def set_izvorCRM(self, x):
        """Setter izvora certificiranog referentnog materijala. Ulazna vrijednost
        je string"""
        x = str(x)
        if x != self.izvorCRM:
            self.izvorCRM = x

    def get_izvorCRM(self):
        """Getter izvora certificiranog referentnog materijala."""
        return self.izvorCRM

    def set_listaEfikasnostiKonvertera(self, x):
        """Setter liste (4 float-a) efikasnosti konvertera"""
        if x != self.listaEfikasnostiKonvertera:
            self.listaEfikasnostiKonvertera = x
            self.emit(QtCore.SIGNAL('promjena_listaEfikasnostiKonvertera(PyQt_PyObject)'),
                      self.listaEfikasnostiKonvertera)

    def get_listaEfikasnostiKonvertera(self):
        """getter liste efikasnosti konvertera"""
        return self.listaEfikasnostiKonvertera

    def set_konverterRezultat(self, x):
        """Setter pandas datafrejma rezultata provjere konvertera"""
        if not isinstance(x, pd.core.frame.DataFrame):
            msg = 'Ulazna vrijednost mora biti pandas DataFrame'
            raise TypeError(msg)
        if not x.equals(self.konverterRezultat):
            self.konverterRezultat = x
            self.emit(QtCore.SIGNAL('promjena_konverterRezultat(PyQt_PyObject)'),
                      self.konverterRezultat)

    def get_konverterRezultat(self):
        """Getter pandas frejma rezultata provjere konvertera"""
        return self.konverterRezultat

    def set_konverterPodaciStart(self, x, recalculate=True):
        """Setter pocetka provjere konvertera. Ulazni parametar je integer, redni
        broj indeksa konverter podataka od kojeg se krece sa kontrolom konvertera."""
        if isinstance(x, QtCore.QModelIndex):
            x = x.row()
        x = int(x)
        if x != self.konverterPodaciStart:
            self.konverterPodaciStart = x
            output = [self.konverterPodaciStart, recalculate]
            self.emit(QtCore.SIGNAL('promjena_konverterPodaciStart(PyQt_PyObject)'),
                      output)

    def get_konverterPodaciStart(self):
        """Getter pocetka provjere konvertera. Output je integer, redni broj indeksa
        konverter podataka od kojeg se krece sa kontrolom konvertera."""
        return self.konverterPodaciStart

    def set_konverterPodaci(self, x):
        """Setter pandas datafrejma sirovih konverter podataka ucitanih iz csv filea."""
        if not isinstance(x, pd.core.frame.DataFrame):
            msg = 'Ulazna vrijednost mora biti pandas DataFrame'
            raise TypeError(msg)
        if not x.equals(self.konverterPodaci):
            self.konverterPodaci = x
            output = {'frejm':self.konverterPodaci, 'start':self.konverterPodaciStart}
            self.emit(QtCore.SIGNAL('promjena_konverterPodaci(PyQt_PyObject)'),
                      output)

    def get_konverterPodaci(self):
        """Getter konverter sirovih podataka ucitanih iz csv filea"""
        return self.konverterPodaci

    def set_siroviPodaciStart(self, x, recalculate=True):
        """Setter pocetka umjeravanja. Ulazni parametar je integer, redni broj
        indeksa sirovih podataka od kojeg se krece sa umjeravanjem"""
        if isinstance(x, QtCore.QModelIndex):
            x = x.row()
        x = int(x)
        if x != self.siroviPodaciStart:
            self.siroviPodaciStart = x
            output = [self.siroviPodaciStart, recalculate]
            self.set_vremenske_granice_umjernih_tocaka()
            self.emit(QtCore.SIGNAL('promjena_siroviPodaciStart(PyQt_PyObject)'),
                      output)

    def get_siroviPodaciStart(self):
        """Getter pocetka umjeravanja. Izlazni parametar je integer, redni broj
        indeksa sirovih podataka od kojeg se krece sa umjeravanjem"""
        return self.siroviPodaciStart

    def set_vremenske_granice_umjernih_tocaka(self):
        """Metoda vraca tuple stringova (min vrijeme, max vrijeme)
        ovisno o zadanim tockama"""
        minindeks = min(self.tockeUmjeravanja[0].indeksi)
        maxindeks = max(self.tockeUmjeravanja[0].indeksi)
        for tocka in self.tockeUmjeravanja:
            value = min(tocka.indeksi)
            if value < minindeks:
                minindeks = value
            value = max(tocka.indeksi)
            if value > maxindeks:
                maxindeks = value
        try:
            tmin = str(self.siroviPodaci.index[minindeks])
            tmax = str(self.siroviPodaci.index[maxindeks])
            self.set_pocetakUmjeravanja(tmin)
            self.set_krajUmjeravanja(tmax)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            self.set_pocetakUmjeravanja('')
            self.set_krajUmjeravanja('')


    def set_siroviPodaci(self, x):
        """Setter pandas datafrejma sirovih podataka ucitanih iz csv filea."""
        if not isinstance(x, pd.core.frame.DataFrame):
            msg = 'Ulazna vrijednost mora biti pandas DataFrame'
            raise TypeError(msg)
        if not x.equals(self.siroviPodaci):
            self.siroviPodaci = x
            output = {'frejm':self.siroviPodaci, 'start':self.siroviPodaciStart}
            self.emit(QtCore.SIGNAL('promjena_siroviPodaci(PyQt_PyObject)'),
                      output)

    def get_siroviPodaci(self):
        """Getter sirovih podataka ucitanih iz csv filea"""
        return self.siroviPodaci

    def set_rezultatUmjeravanja(self, x):
        """Setter za pandas datafrejm rezultata umjeravanja.
        """
        if not isinstance(x, pd.core.frame.DataFrame):
            msg = 'Parametar mora biti pandas DataFrame'
            raise TypeError(msg)
        if not x.equals(self.rezultatUmjeravanja):
            self.rezultatUmjeravanja = x
            self.emit(QtCore.SIGNAL('promjena_rezultatUmjeravanja'))

    def get_rezultatUmjeravanja(self):
        """Getter za rezultat umjeravanja"""
        return self.rezultatUmjeravanja

    def set_cNOx95(self, x):
        """Setter za parametar cNOx95. Ulazna vrijednost je float"""
        x = float(x)
        if x != self.cNOx95:
            self.cNOx95 = x
            self.emit(QtCore.SIGNAL('promjena_cNOx95(PyQt_PyObject)'),
                      self.cNOx95)

    def get_cNOx95(self):
        """Getter za vijednost cNOx95 parametra"""
        return self.cNOx95

    def set_cNOx50(self, x):
        """Setter za parametar cNOx50. Ulazna vrijednost je float"""
        x = float(x)
        if x != self.cNOx50:
            self.cNOx50 = x
            self.emit(QtCore.SIGNAL('promjena_cNOx50(PyQt_PyObject)'),
                      self.cNOx50)

    def get_cNOx50(self):
        """Getter za vijednost cNOx50 parametra"""
        return self.cNOx50

    def set_provjeraLinearnosti(self, x, recalculate=True):
        """Setter za provjeru linearnosti prilikom racunanja umjeravanja. Ulazni
        parametar x je boolean"""
        x = bool(x)
        if x != self.provjeraLinearnosti:
            self.provjeraLinearnosti = x
            output = [self.provjeraLinearnosti, recalculate]
            self.emit(QtCore.SIGNAL('promjena_provjeraLinearnosti(PyQt_PyObject)'),
                      output)

    def get_provjeraLinearnosti(self):
        """Getter za boolean provjere linearnosti"""
        return self.provjeraLinearnosti

    def set_provjeraKonvertera(self, x, recalculate=True):
        """Setter za boolean koji definira da li se radi provjera konvertera."""
        x = bool(x)
        if x != self.provjeraKonvertera:
            self.provjeraKonvertera = x
            output = [self.provjeraKonvertera, recalculate]
            self.emit(QtCore.SIGNAL('promjena_provjeraKonvertera(PyQt_PyObject)'),
                      output)

    def get_provjeraKonvertera(self):
        """Getter za boolean provjere konvertera"""
        return self.provjeraKonvertera

    def set_izabraniZrak(self, x, recalculate=True):
        """Setter izabranog generatora cistog zraka. Ulazna vrijednost je string"""
        x = str(x)
        if not x in self.listaZrak:
            msg = '{0} se ne nalazi na popisu mogucih generatora cistog zraka {1}'.format(x, str(self.listaZrak))
            raise ValueError(msg)
        if x != self.izabraniZrak:
            self.izabraniZrak = x
            output = [self.izabraniZrak, recalculate]
            # promjena povezanih polja
            try:
                # proizvodjac
                value = self.cfg.get_konfig_element(self.izabraniZrak, 'proizvodjac')
                self.set_proizvodjacCistiZrak(value)
                self.emit(QtCore.SIGNAL('promjena_proizvodjacCistiZrak(PyQt_PyObject)'),
                          self.proizvodjacCistiZrak)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            try:
                # sljedivost
                komponenta = self.izabranoMjerenje
                if komponenta.startswith('NO'):
                    komponenta = 'NOx'
                value = self.cfg.get_konfig_element(self.izabraniZrak, komponenta)
                value = 2*float(value) #get_konfig_element vraca string..za U(k=1)
                self.set_sljedivostCistiZrak(value, recalculate=False)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            self.emit(QtCore.SIGNAL('promjena_izabraniZrak(PyQt_PyObject)'),
                      output)

    def get_izabraniZrak(self):
        """Getter izabranog generatora cistog zraka"""
        return self.izabraniZrak

    def set_izabranaDilucija(self, x, recalculate=True):
        """Setter izabrane dilucijske jedinice. Ulazna vrijednost je string."""
        x = str(x)
        if not x in self.listaDilucija:
            msg = '{0} se ne nalazi na popisu mogucih dilucijskih jedinica {1}'.format(x, str(self.listaDilucija))
            raise ValueError(msg)
        if x != self.izabranaDilucija:
            self.izabranaDilucija = x
            output = [self.izabranaDilucija, recalculate]
            #promjena povezanih polja
            # dilucija proizvodjac
            try:
                value = self.cfg.get_konfig_element(self.izabranaDilucija, 'proizvodjac')
                self.set_proizvodjacDilucija(value)
                self.emit(QtCore.SIGNAL('promjena_proizvodjacDilucija(PyQt_PyObject)'),
                          self.proizvodjacDilucija)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            # dilucija sljedivost
            try:
                part1 = self.cfg.get_konfig_element(self.izabranaDilucija, 'MFC_NUL_Plin_sljedivost')
                part2 = self.cfg.get_konfig_element(self.izabranaDilucija, 'MFC_KAL_PLIN_sljedivost')
                part3 = self.cfg.get_konfig_element(self.izabranaDilucija, 'GENERATOR_OZONA_sljedivost')
                value = ", ".join([part1, part2, part3])
                self.set_sljedivostDilucija(value)
                self.emit(QtCore.SIGNAL('promjena_sljedivostDilucija(PyQt_PyObject)'),
                          self.sljedivostDilucija)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            self.emit(QtCore.SIGNAL('promjena_izabranaDilucija(PyQt_PyObject)'),
                      output)

    def get_izabranaDilucija(self):
        """Getter izabrane dilucijske jedinice"""
        return self.izabranaDilucija

    def set_izabranoMjerenje(self, x, recalculate=True):
        """Setter izabranog mjerenja (komponente). Ulazna vrijednost je string"""
        x = str(x)
        if not x in self.listaMjerenja:
            msg = '{0} se ne nalazi na popisu mogucih mjerenja {1}'.format(x, str(self.listaMjerenja))
            raise ValueError(msg)
        if x != self.izabranoMjerenje:
            self.izabranoMjerenje = x
            output = [self.izabranoMjerenje, recalculate]
            #promjena povezanih polja
            try:
                # promjena mjerne jedinice
                value = self.uredjaji[self.izabraniUredjaj]['komponenta'][self.izabranoMjerenje]['mjernaJedinica']
                self.set_mjernaJedinica(value)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            try:
                # promjena izvora certificiranog referentnog materijala
                value = self.cfg.get_konfig_element(self.izabranoMjerenje, 'izvor')
                self.set_izvorCRM(value)
                self.emit(QtCore.SIGNAL('promjena_izvorCRM(PyQt_PyObject)'),
                          self.izvorCRM)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            try:
                # promjena max opsega mjerenja
                value = self.uredjaji[self.izabraniUredjaj]['analitickaMetoda']['o']['max']
                self.set_opseg(value, recalculate=False)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            try:
                # promjena norme
                part1 = self.cfg.get_konfig_element(self.izabranoMjerenje, 'norma')
                part2 = self.cfg.get_konfig_element(self.izabranoMjerenje, 'naziv')
                value = " - ".join([part1, part2])
                self.set_norma(value)
                self.emit(QtCore.SIGNAL('promjena_norma(PyQt_PyObject)'),
                          self.norma)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            try:
                # promjena brojObrasca
                value = self.cfg.get_konfig_element(self.izabranoMjerenje, 'oznaka')
                self.set_brojObrasca(value)
                self.emit(QtCore.SIGNAL('promjena_brojObrasca(PyQt_PyObject)'),
                          self.brojObrasca)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            try:
                # promjena revizija
                value = self.cfg.get_konfig_element(self.izabranoMjerenje, 'revizija')
                self.set_revizija(value)
                self.emit(QtCore.SIGNAL('promjena_revizija(PyQt_PyObject)'),
                          self.revizija)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            try:
                #sljedivost cistog zraka ovisi o komponenti
                komponenta = self.izabranoMjerenje
                if komponenta.startswith('NO'):
                    komponenta = 'NOx'
                value = self.cfg.get_konfig_element(self.izabraniZrak, komponenta)
                value = 2 * float(value) #radi se U(k=2)
                self.set_sljedivostCistiZrak(value, recalculate=False)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            #emit promjenu
            self.emit(QtCore.SIGNAL('promjena_izabranoMjerenje(PyQt_PyObject)'),
                      output)

    def get_izabranoMjerenje(self):
        """Getter izabranog mjerenja"""
        return self.izabranoMjerenje

    def set_listaZrak(self, x):
        """Setter liste generatora cistog zraka. Ulazna vrijednost je lista stringova"""
        if x != self.listaZrak:
            self.listaZrak = x
            self.emit(QtCore.SIGNAL('promjena_listaZrak(PyQt_PyObject)'),
                      self.listaZrak)
            if self.listaZrak:
                #ako lista nije prazna izaberi prvi element
                self.set_izabraniZrak(self.listaZrak[0], recalculate=False)
            else:
                self.set_izabraniZrak('None', recalculate=False)


    def get_listaZrak(self):
        """Getter liste generatora cistog zraka"""
        return self.listaZrak

    def init_listaZrak(self):
        """inicijalna postavka izbora generatora cistog zraka"""
        lista = self.cfg.get_listu_cistiZrak()
        self.set_listaZrak(lista)

    def set_listaDilucija(self, x):
        """Setter liste dilucijskih (kalibracijskih) jedinica. Ulazna vrijednost
        je lista stringova"""
        if x != self.listaDilucija:
            self.listaDilucija = x
            self.emit(QtCore.SIGNAL('promjena_listaDilucija(PyQt_PyObject)'),
                      self.listaDilucija)
            #ako lista nije prazna izaberi prvi element
            if self.listaDilucija:
                self.set_izabranaDilucija(self.listaDilucija[0], recalculate=False)
            else:
                self.set_izabranaDilucija('None', recalculate=False)

    def get_listaDilucija(self):
        """Gettet liste dilucijskih jedinica"""
        return self.listaDilucija

    def init_listaDilucija(self):
        lista = self.cfg.get_listu_dilucija()
        self.set_listaDilucija(lista)

    def set_listaMjerenja(self, x, recalculate=True):
        """Setter liste mjerenja (komponente). Ulazna vrijednost je list"""
        if x != self.listaMjerenja:
            self.listaMjerenja = x
            self.emit(QtCore.SIGNAL('promjena_listaMjerenja(PyQt_PyObject)'),
                      self.listaMjerenja)
            #ako lista nije prazna izaberi prvi element
            if self.listaMjerenja:
                self.set_izabranoMjerenje(self.listaMjerenja[0], recalculate=recalculate)
            else:
                self.set_izabranoMjerenje('None', recalculate=False)

    def get_listaMjerenja(self):
        """Getter za listu mjerenja"""
        return self.listaMjerenja

    def set_izabraniPathCSV(self, x):
        """Setter izabranog patha do csv filea sa sirovim podacima. Ulazna
        vrijednost je string."""
        if x != self.izabraniPathCSV:
            self.izabraniPathCSV = str(x)
            self.emit(QtCore.SIGNAL('promjena_izabraniPathCSV(PyQt_PyObject)'),
                      self.izabraniPathCSV)

    def get_izabraniPathCSV(self):
        """Getter izabranog patha do csv filea sa sirovim podacima."""
        return self.izabraniPathCSV

    def set_izabranaPostaja(self, x):
        """Setter izabrane postaje. Ulazna vrijednost je string."""
        if x != self.izabranaPostaja:
            self.izabranaPostaja = str(x)
            self.emit(QtCore.SIGNAL('promjena_izabranaPostaja(PyQt_PyObject)'),
                      self.izabranaPostaja)

    def get_izabranaPostaja(self):
        """Getter izabrane postaje"""
        return self.izabranaPostaja

    def set_izabraniUredjaj(self, x):
        """Setter izabranog uredjaja. Ulazna vrijednost je string."""
        if x != self.izabraniUredjaj:
            self.izabraniUredjaj = str(x)
            #postavi novog proizvodjaca i model uredjaja
            value = str(self.uredjaji[self.izabraniUredjaj]['oznakaModela'])
            self.set_oznakaModelaUredjaja(value)
            value = str(self.uredjaji[self.izabraniUredjaj]['proizvodjac'])
            self.set_proizvodjacUredjaja(value)
            self.emit(QtCore.SIGNAL('promjena_izabraniUredjaj(PyQt_PyObject)'),
                      self.izabraniUredjaj)

    def get_izabraniUredjaj(self):
        """Getter izabranog uredjaja"""
        return self.izabraniUredjaj

    def set_uredjaji(self, x):
        """Setter uredjaja. Ulazna vrijednost je mapa uredjaja.
        Kljucevi mape su serijski brojevi uredjaja."""
        if x != self.uredjaji:
            self.uredjaji = x
            self.emit(QtCore.SIGNAL('promjena_uredjaji(PyQt_PyObject)'),
                      self.uredjaji)

    def get_uredjaji(self):
        """Getter svih uredjaja"""
        return self.uredjaji

    def set_postaje(self, x):
        """Setter postaja. Ulazna vrijednost je mapa postaja
        {postaja1:[uredjaj, uredjaj2], postaja2:[uredjaj3], postaja3:[]...}"""
        if x != self.postaje:
            self.postaje = x
            self.emit(QtCore.SIGNAL('promjena_postaje(PyQt_PyObject)'),
                      self.postaje)

    def get_postaje(self):
        """Getter postaja"""
        return self.postaje

    def set_oznakaModelaUredjaja(self, x):
        """Setter oznake modela izabranog uredjaja"""
        x = str(x)
        if x != self.oznakaModelaUredjaja:
            self.oznakaModelaUredjaja = x
            self.emit(QtCore.SIGNAL('promjena_oznakaModelaUredjaja(PyQt_PyObject)'),
                      self.oznakaModelaUredjaja)

    def get_oznakaModelaUredjaja(self):
        """getter oznake modela uredjaja"""
        return self.oznakaModelaUredjaja

    def set_proizvodjacUredjaja(self, x):
        """setter proizvodjaca izabranog uredjaja"""
        x = str(x)
        if x != self.proizvodjacUredjaja:
            self.proizvodjacUredjaja = x
            self.emit(QtCore.SIGNAL('promjena_proizvodjacUredjaja(PyQt_PyObject)'),
                      self.proizvodjacUredjaja)

    def get_proizvodjacUredjaja(self):
        """getter proizvodjaca izabranog uredjaja"""
        return self.proizvodjacUredjaja

    def set_mjernaJedinica(self, x):
        """Setter mjerne jedinice. Ulazna vrijednost je tipa string."""
        if x != self.mjernaJedinica:
            self.mjernaJedinica = str(x)
            self.emit(QtCore.SIGNAL('promjena_mjernaJedinica(PyQt_PyObject)'),
                      self.mjernaJedinica)

    def get_mjernaJedinica(self):
        """Getter mjerne jedinice, Izlazna vrijednost je tipa string."""
        return self.mjernaJedinica

    def block_all_signals(self):
        """Sprijecava emitiranje signala iz objekta."""
        self.blockSignals(True)

    def unblock_all_signals(self):
        """Omogucava emitiranje signala iz objekta."""
        self.blockSignals(False)

    def generiraj_nan_frejm_rezultata_umjeravanja(self):
        """
        metoda generira datafrejm sa 6 stupaca i n redaka (n je broj umjernih
        tocaka prezuetih iz konfiga), radi inicijalnog prikaza tablice
        rezultata umjeravanja. Sve vrijednosti tog datafrejma su np.NaN
        """
        frejm = pd.DataFrame(
            columns=['cref', 'U', 'c', u'\u0394', 'sr', 'r'],
            index=list(range(len(self.tockeUmjeravanja))))
        return frejm

    def generiraj_nan_frejm_rezultata_konvertera(self):
        """
        metoda generira datafrejm sa 4 stupca i 6 redaka radi inicijalnog prikaza
        tablice rezultata umjeravanja. Sve vrijednosti tog datafrejma su np.NaN
        """
        indeks = [str(tocka) for tocka in self.tockeKonverter]
        frejm = pd.DataFrame(
            columns=['c, R, NOx', 'c, R, NO2', 'c, NO', 'c, NOx'],
            index=indeks)
        return frejm

    def init_uredjaje_i_postaje_sa_REST(self):
        """Inicijalno popunjavanje podataka o uredjajima i postajama sa podacima
        preuzetim od REST servisa"""
        try:
            urlUredjaji = self.cfg.get_konfig_element('REST', 'uredjaj')
            urlPostaje = self.cfg.get_konfig_element('REST', 'postaje')
            pos, ure = helperi.pripremi_mape_postaja_i_uredjaja(urlUredjaji,
                                                                urlPostaje)
            self.set_uredjaji(ure)
            self.set_postaje(pos)
        except Exception as err:
            logging.error(str(err), exc_info=True)

    def get_zero_span_tocke(self):
        """
        Metoda pronalazi indekse za zero i span.

        Zero je prva tocka koja ima crefFaktor jednak 0.0
        Span je prva tocka sa crefFaktorom 0.8, a ako niti jedna tocka nema
        taj crefFaktor, onda se uzima ona sa najvecim crefFaktorom
        """
        if len(self.tockeUmjeravanja) >= 2:
            cf = [float(tocka.crefFaktor) for tocka in self.tockeUmjeravanja]
            zero = cf.index(0.0)
            if 0.8 in cf:
                span = cf.index(0.8)
            else:
                span = cf.index(max(cf))
            out = [self.tockeUmjeravanja[zero],
                   self.tockeUmjeravanja[span]]
            return out
        else:
            return []


