# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 12:04:06 2015

@author: DHMZ-Milic
"""
import logging
import copy
import pandas as pd
from PyQt4 import QtGui, QtCore
from app.model.konfig_klase import Tocka
import app.model.pomocne_funkcije as helperi
import app.model.frejm_model as qtmodeli
import app.model.kalkulator as calc


class DokumentModel(QtCore.QObject):
    def __init__(self, cfg=None, parent=None):
        QtCore.QObject.__init__(self, parent=parent)
        self.cfg = cfg  # MainKonfig objekt

        self.postaje = {} #mapa sa podacima o postajama (postaja: [lista uredjaja na njoj])
        self.uredjaji = {} #mapa sa podacima o uredjaju (komponente, metode...)
        self.listaMjerenja = [] #lista svih mjerenja
        self.listaDilucija = [] #lista svih dilucijskih jedinica
        self.listaZrak = [] #lista svih generatora cistog zraka

        self.mjerenja = {} #mapa sa podacima za pojedini tab rezultata

        self.postavke = {'mjernaJedinica':'n/a',
                         'izabranoMjerenje':'n/a',
                         'izabranaPostaja':'',
                         'izabraniUredjaj':'',
                         'izabranaDilucija':'',
                         'izabraniZrak':'',
                         'opseg':1.0,
                         'izvorCRM':'',
                         'koncentracijaCRM':1.0,
                         'sljedivostCRM':2.0,
                         'proizvodjacDilucija':'',
                         'sljedivostDilucija':'',
                         'proizvodjacCistiZrak':'',
                         'sljedivostCistiZrak':0.0,
                         'norma':'',
                         'oznakaIzvjesca':'',
                         'brojObrasca':'',
                         'revizija':'',
                         'datumUmjeravanja':'',
                         'temperatura':0.0,
                         'vlaga':0.0,
                         'tlak':0.0,
                         'napomena':'',
                         'oznakaModelaUredjaja':'',
                         'proizvodjacUredjaja':''}

        #globalni izbor testova
        self.provjeraKonvertera = False
        self.provjeraOdaziv = False
        self.provjeraUmjeravanje = True
        self.provjeraPonovljivost = False
        self.provjeraLinearnost = False

        self.init_uredjaje_i_postaje_sa_REST()

    def block_all_signals(self):
        """Sprijecava emitiranje signala iz objekta."""
        self.blockSignals(True)

    def unblock_all_signals(self):
        """Omogucava emitiranje signala iz objekta."""
        self.blockSignals(False)

    def init_tockeUmjeravanja(self):
        """
        Inicijalizacija umjernih tocaka uz pomoc konfiga. Output je lista
        tocaka
        """
        return self.cfg.get_tockeUmjeravanja()

    def init_tockeKonverter(self):
        """
        Inicijalizacija tocaka za provjeru konvertera uz pomoc konfiga. Output
        je lista tocaka.
        """
        return self.cfg.get_tockeKonverter()

    def init_listaDilucija(self):
        """inicijalni setup liste dilucijskih jedinica iz konfiga"""
        lista = self.cfg.get_listu_dilucija()
        self.set_listaDilucija(lista)

    def init_listaZrak(self):
        """inicijalna postavka izbora generatora cistog zraka"""
        lista = self.cfg.get_listu_cistiZrak()
        self.set_listaZrak(lista)

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

    def mjerenje_isValid(self, mjerenje):
        """helper metoda za provjeru da li je zadano mjerenje validno"""
        if mjerenje != None and mjerenje in self.mjerenja:
            return True
        else:
            return False

    def usporedi_mjerenja(self, tabMap):
        """
        Provjera da li mapa mjerenja (tabmap) odgovara trenutnom setu mjerenja u dokumentu.
        """
        incomingSet = set(tabMap.keys())
        currentSet = set(self.mjerenja.keys())

        if incomingSet == currentSet:
            return True
        else:
            return False

    def get_mjerenja(self):
        """getter za mapu mjerenja"""
        return self.mjerenja
################################################################################
    @helperi.activate_wait_spinner
    def set_ucitane_podatke_za_mjerenje(self, data, mjerenje=None):
        """
        Metoda postavlja podatke model za zadano mjerenje.
        """
        if mjerenje == 'konverter':
            self.mjerenja['konverter'] = self.pripremi_konverter_za_rad(data)
        elif mjerenje.endswith('-odaziv'):
            self.mjerenja[mjerenje] = self.pripremi_odaziv_za_rad(data, mjerenje)
        else:
            self.mjerenja[mjerenje] = self.pripremi_ucitano_mjerenje_za_rad(data)
        self.recalculate_tab_umjeravanja(mjerenje=mjerenje)
################################################################################
    @helperi.activate_wait_spinner
    def set_ucitane_podatke(self, frejm, tabMap):
        """
        Metoda postavlja u dokument pandas datafrejm podataka. Mapa tabMap
        ima popis mjerenje u koje treba postaviti ucitani frejm (ili njegov slice)
        """
        if not isinstance(frejm, pd.core.frame.DataFrame):
            msg = 'Ulazna vrijednost mora biti pandas DataFrame'
            raise TypeError(msg)
        if self.usporedi_mjerenja(tabMap):
            #update samo izabrana mjerenja
            for mjerenje in tabMap:
                if tabMap[mjerenje] == True:
                    if mjerenje == 'konverter':
                        model = self.get_model(mjerenje='konverter')
                        model.set_start(0)
                        model.set_frejm(frejm)
                    elif mjerenje.endswith('-odaziv'):
                        stupac = mjerenje[:-7]
                        slajs = frejm.loc[:,stupac]
                        model = self.get_model(mjerenje=mjerenje)
                        model.set_slajs(slajs, stupac)
                    else:
                        slajs = frejm.loc[:,mjerenje]
                        adFrejm = pd.DataFrame({mjerenje:slajs})
                        model = self.get_model(mjerenje=mjerenje)
                        model.set_start(0)
                        model.set_frejm(adFrejm)
                else:
                    pass
        else:
            #zamjeni sve tabove iz pocetka
            self.mjerenja = {}
            for mjerenje in tabMap:
                if tabMap[mjerenje] == True:
                    if mjerenje == 'konverter':
                        self.set_ucitane_podatke_za_mjerenje(frejm, mjerenje='konverter')
                    elif mjerenje.endswith('-odaziv'):
                        stupac = mjerenje[:-7]
                        slajs = frejm.loc[:,stupac]
                        self.set_ucitane_podatke_za_mjerenje(slajs, mjerenje=mjerenje)
                    else:
                        slajs = frejm.loc[:,mjerenje]
                        self.set_ucitane_podatke_za_mjerenje(slajs, mjerenje=mjerenje)
                else:
                    if mjerenje == 'konverter':
                        mockFrejm = pd.DataFrame(columns=['NO', 'NOx', 'NO2'])
                        self.set_ucitane_podatke_za_mjerenje(mockFrejm, mjerenje='konverter')
                    elif mjerenje.endswith('-odaziv'):
                        stupac = mjerenje[:-7]
                        mockSlajs = pd.Series(name=stupac)
                        self.set_ucitane_podatke_za_mjerenje(mockSlajs, mjerenje=mjerenje)
                    else:
                        mockSlajs = pd.Series(name=mjerenje)
                        self.set_ucitane_podatke_za_mjerenje(mockSlajs, mjerenje=mjerenje)
################################################################################
    def pripremi_odaziv_za_rad(self, slajs, naziv):
        """
        Definiranje output mape sa podacima za provjeru odaziva.

        Ulazni parametar je slajs frejma (pd.Series) zadanog stupca i puni naziv
        taba (ukljucijuci '-odaziv')
        """
        output = {}
        output['mjerenje'] = naziv
        plin = naziv[:-7] #treba maknuti '-odaziv' sa kraja za naziv komponente

        output['highLimit'] = 90
        output['lowLimit'] = 10
        model = qtmodeli.RiseFallModel(slajs=slajs,
                                       naziv=plin)
        model.set_high_limit(output['highLimit'])
        model.set_low_limit(output['lowLimit'])
        output['model'] = model
        cols = ['Naziv', 'Pocetak', 'Kraj', 'Delta']
        rez = pd.DataFrame(columns=cols)
        output['rezultatStupci'] = cols
        output['rezultatFrejm'] = rez

        output['generateReportCheck'] = False
        return output
################################################################################
    def pripremi_konverter_za_rad(self, frejm):
        """
        Definiranje output mape sa podacima za provjeru konvertera.

        Ulazni parametar je pandas.DataFrame() podataka sa stupcima
        za 'NO', 'NOx', 'NO2'.

        output mapa ima sljedece kljuceve:
        'mjerenje'
            -> string 'konverter'
        'cNOx50'
            -> parametar za racunanje efikasnosti konvertera
        'cNOx95'
            -> parametar za racunanje efikasnosti konvertera
        'model'
            -> qt model za view podataka
            -> sluzi za jednostavnije prebacivanje prikaza
        'kalkulator'
            -> instanca objekta za racunanje
        'generateReportCheck'
            -> boolean, test da li se konverter ukljucuje u report
        """
        output = {}

        tocke = self.init_tockeKonverter()
        output['mjerenje'] = 'konverter'
        output['cNOx50'] = 200.0
        output['cNOx95'] = 180.0

        model = qtmodeli.SiroviFrameModel(frejm=frejm,
                                          tocke=tocke,
                                          start=0)
        output['model'] = model
        output['generateReportCheck'] = False
        output['kalkulator'] = calc.KonverterKalkulator(doc=self)
        return output
################################################################################
    def pripremi_ucitano_mjerenje_za_rad(self, slajs):
        """
        Definiranje output mape sa podacima jedinstvenim za zadanu komponentu.
        Ulazni parametar je pandas.Series() podataka (slajs komponente).

        output mapa ima sljedece kljuceve:
        'mjerenje'
            -> string, naziv komponente
        'model'
            -> qt model za view podataka
            -> sluzi za jednostavnije prebacivanje prikaza
        'startUmjeravanja'
            -> timestamp pocetka umjeravanja
        'krajUmjeravanja'
            -> timestamp kraja umjeravanja
        'kalkulator'
            -> instanca objekta za racunanje
        'testUmjeravanje'
            -> boolean za check provjere umjeravanja
        'testPonovljivost'
            -> boolean za check provjere ponovljivosti
        'testLinearnost':
            -> boolean za check provjere linearnosti
        """
        output = {}
        ### naziv ###
        naziv = slajs.name
        output['mjerenje'] = naziv
        ### frejm podataka ###
        frejm = pd.DataFrame({naziv:slajs})
        ### tocke umjeravanja ###
        tocke = self.init_tockeUmjeravanja()
        ### model sa sirovim podacima za ljevi dio gui-a ###
        model = qtmodeli.SiroviFrameModel(frejm=frejm,
                                          tocke=tocke,
                                          start=0)
        output['model'] = model
        ### vrijeme pocetka i kraja umjeravanja ###
        try:
            #try blok zbog potencijalnog problema kod nedovoljnog broja podataka
            output['startUmjeravanja'] = frejm.index[model.get_start()] #timestamps
            output['krajUmjeravanja'] = frejm.index[model.get_kraj()] #timestamps
        except Exception as err:
            logging.error(str(err), exc_info=True)
            output['startUmjeravanja'] = pd.NaT
            output['krajUmjeravanja'] = pd.NaT
        ### kalkulator ###
        output['kalkulator'] = calc.Kalkulator(doc=self, mjerenje=naziv)
        ### testovi vezani za tab sa rezultatima pojedine komponente ###
        output['testUmjeravanje'] = self.get_provjeraUmjeravanje()
        output['testPonovljivost'] = self.get_provjeraPonovljivost()
        output['testLinearnost'] = self.get_provjeraLinearnost()
        ### test za generiranje reporta ###
        output['generateReportCheck'] = False
        return output

    def set_rezulatFrejm_odaziva(self, value, mjerenje=None):
        """setter frejma rezultata odaziva (tablica sa pocetkom, krajem i
        razlikom vremena)"""
        if self.mjerenje_isValid(mjerenje):
            self.mjerenja[mjerenje]['rezultatFrejm'] = value
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)
################################################################################
    def set_generateReportCheck(self, value, mjerenje=None):
        """
        Setter boolean vrijednosti koja odredjuje da li mjerenje treba biti u
        reportu.
        """
        if self.mjerenje_isValid(mjerenje):
            self.mjerenja[mjerenje]['generateReportCheck'] = value
            output = {'value':value,
                      'mjerenje':mjerenje}
            self.emit(QtCore.SIGNAL('promjena_generateReportCheck(PyQt_PyObject)'),
                      output)
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)

    def get_generateReportCheck(self, mjerenje=None):
        """
        Getter boolean vrijednosti koja odredjuje da li mjerenje treba biti u
        reportu.
        """
        if self.mjerenje_isValid(mjerenje):
            return self.mjerenja[mjerenje]['generateReportCheck']
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)
################################################################################
    def set_start(self, indeks, mjerenje=None, recalculate=True):
        """setter pocetnog indeksa od kojeg se krece sa umjeravanjem"""
        if self.mjerenje_isValid(mjerenje):
            if indeks != self.get_start(mjerenje=mjerenje):
                self.mjerenja[mjerenje]['model'].set_start(indeks)
                # update pocetak i kraj umjeravanja
                self.update_vremena_pocetka_i_kraja_umjeravanja(mjerenje=mjerenje)
                #recalculate
                if recalculate:
                    self.recalculate_tab_umjeravanja(mjerenje=mjerenje)
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)

    def get_start(self, mjerenje=None):
        """getter pocetnog indeksa od kojeg se krece sa umjeravanjem"""
        if self.mjerenje_isValid(mjerenje):
            return self.mjerenja[mjerenje]['model'].get_start()
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)
            return None

    def set_tocke(self, tocke, mjerenje=None, recalculate=True):
        """setter tocaka umjeravanja za mjerenje (tab)"""
        if self.mjerenje_isValid(mjerenje):
            if tocke != self.get_tocke(mjerenje=mjerenje):
                # modificiranje modela za novi prikaz
                self.mjerenja[mjerenje]['model'].set_tocke(tocke)
                # update pocetak i kraj umjeravanja
                self.update_vremena_pocetka_i_kraja_umjeravanja(mjerenje=mjerenje)
                #recalculate
                if recalculate:
                    self.recalculate_tab_umjeravanja(mjerenje=mjerenje)
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)

    def get_tocke(self, mjerenje=None):
        if self.mjerenje_isValid(mjerenje):
            return self.mjerenja[mjerenje]['model'].get_tocke()
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)
            return None

    def zamjeni_umjernu_tocku(self, indeks, tocka, mjerenje=None, recalculate=True):
        """
        Metoda mjenja postojecu tocku sa zadanom tockom. Lokacija je zadana
        sa indeksom u listi. Zamjena je samo u tockama za odredjeni tab.
        """
        if self.mjerenje_isValid(mjerenje):
            tocke = copy.deepcopy(self.get_tocke(mjerenje=mjerenje))
            tocke[indeks] = tocka
            self.set_tocke(tocke, mjerenje=mjerenje, recalculate=True)
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)

    def dodaj_umjernu_tocku(self, mjerenje=None, recalculate=True):
        """
        Metoda dodaje tocku na popis tocaka za mjerenje(tab). Dodaje je iza vec
        definiranih tocaka, ukupno 30 indeksa, prvih 15 zanemarenih, random boja.
        """
        if self.mjerenje_isValid(mjerenje):
            tocke = copy.deepcopy(self.get_tocke(mjerenje=mjerenje))
            ime = 'TOCKA' + str(len(tocke)+1)
            indeks = max([max(tocka.indeksi) for tocka in tocke])
            start = indeks+15
            end = start+15
            cref = 0.0
            novaTocka = Tocka(ime=ime, start=start, end=end, cref=cref)
            tocke.append(novaTocka)
            self.set_tocke(tocke, mjerenje=mjerenje, recalculate=True)
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)

    def makni_umjernu_tocku(self, indeks, mjerenje=None, recalculate=True):
        """
        Metoda brise tocku zadanu indeksom sa popisa tocaka za mjerenje(tab)
        Metoda mjenja nazive ostalih tocaka radi konzistencije.
        """
        if self.mjerenje_isValid(mjerenje):
            tocke = copy.deepcopy(self.get_tocke(mjerenje=mjerenje))
            tocke.pop(indeks)
            for i in range(len(tocke)):
                tocke[i].ime = 'TOCKA' + str(i+1)
            self.set_tocke(tocke, mjerenje=mjerenje, recalculate=True)
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)
################################################################################
    def update_vremena_pocetka_i_kraja_umjeravanja(self, mjerenje=None):
        """update timestampova za pocetak i kraj umjeravanja"""
        if self.mjerenje_isValid(mjerenje):
            s = self.mjerenja[mjerenje]['model'].get_startUmjeravanja()
            e = self.mjerenja[mjerenje]['model'].get_krajUmjeravanja()
            self.set_startUmjeravanja(s, mjerenje=mjerenje)
            self.set_krajUmjeravanja(e, mjerenje=mjerenje)
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)
################################################################################
    def set_startUmjeravanja(self, timestamp, mjerenje=None):
        """setter timestampa pocetka umjeravanja za izabrano mjerenje"""
        if self.mjerenje_isValid(mjerenje):
            self.mjerenja[mjerenje]['startUmjeravanja'] = timestamp
            output = {'value':timestamp,
                      'mjerenje':mjerenje}
            self.emit(QtCore.SIGNAL('promjena_startUmjeravanja(PyQt_PyObject)'),
                      output)
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)

    def get_startUmjeravanja(self, mjerenje=None):
        """getter timestampa pocetka umjeravanja za izabrano mjerenje"""
        if self.mjerenje_isValid(mjerenje):
            return self.mjerenja[mjerenje]['startUmjeravanja']
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)
            return None
################################################################################
    def set_krajUmjeravanja(self, timestamp, mjerenje=None):
        """setter timestampa kraja umjeravanja za izabrano mjerenje"""
        if self.mjerenje_isValid(mjerenje):
            self.mjerenja[mjerenje]['krajUmjeravanja'] = timestamp
            output = {'value':timestamp,
                      'mjerenje':mjerenje}
            self.emit(QtCore.SIGNAL('promjena_krajUmjeravanja(PyQt_PyObject)'),
                      output)
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)

    def get_krajUmjeravanja(self, mjerenje=None):
        """getter timestampa kraja umjeravanja za izabrano mjerenje"""
        if self.mjerenje_isValid(mjerenje):
            return self.mjerenja[mjerenje]['krajUmjeravanja']
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)
            return None
################################################################################
    def set_testUmjeravanje(self, x, mjerenje=None, recalculate=True):
        """Setter booleana provjere umjeravanja (x) za zadano mjerenje."""
        if self.mjerenje_isValid(mjerenje):
            if x != self.get_testUmjeravanje(mjerenje=mjerenje):
                self.mjerenja[mjerenje]['testUmjeravanje'] = x
            #recalculate
            if recalculate:
                self.recalculate_tab_umjeravanja(mjerenje=mjerenje)
            #emit change
            output = {'value':x,
                      'mjerenje':mjerenje}
            self.emit(QtCore.SIGNAL('promjena_testUmjeravanje(PyQt_PyObject)'),
                      output)
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)

    def get_testUmjeravanje(self, mjerenje=None):
        """Getter booleana provjere umjeravanja za zadano mjerenje."""
        if self.mjerenje_isValid(mjerenje):
            return self.mjerenja[mjerenje]['testUmjeravanje']
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)
################################################################################
    def set_testPonovljivost(self, x, mjerenje=None, recalculate=True):
        """Setter booleana provjere ponovljivosti (x) za zadano mjerenje."""
        if self.mjerenje_isValid(mjerenje):
            if x != self.get_testPonovljivost(mjerenje=mjerenje):
                self.mjerenja[mjerenje]['testPonovljivost'] = x
            #recalculate
            if recalculate:
                self.recalculate_tab_umjeravanja(mjerenje=mjerenje)
            #emit change
            output = {'value':x,
                      'mjerenje':mjerenje}
            self.emit(QtCore.SIGNAL('promjena_testPonovljivost(PyQt_PyObject)'),
                      output)
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)

    def get_testPonovljivost(self, mjerenje=None):
        """Getter booleana provjere ponovljivosti za zadano mjerenje."""
        if self.mjerenje_isValid(mjerenje):
            return self.mjerenja[mjerenje]['testPonovljivost']
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)
################################################################################
    def set_testLinearnost(self, x, mjerenje=None, recalculate=True):
        """Setter booleana provjere linearnosti (x) za zadano mjerenje."""
        if self.mjerenje_isValid(mjerenje):
            if x != self.get_testLinearnost(mjerenje=mjerenje):
                self.mjerenja[mjerenje]['testLinearnost'] = x
            #recalculate
            if recalculate:
                self.recalculate_tab_umjeravanja(mjerenje=mjerenje)
            #emit change
            output = {'value':x,
                      'mjerenje':mjerenje}
            self.emit(QtCore.SIGNAL('promjena_testLinearnost(PyQt_PyObject)'),
                      output)
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)

    def get_testLinearnost(self, mjerenje=None):
        """Getter booleana provjere linearnosti za zadano mjerenje."""
        if self.mjerenje_isValid(mjerenje):
            return self.mjerenja[mjerenje]['testLinearnost']
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)
################################################################################
    def set_model(self, model, mjerenje=None, recalculate=True):
        """setter instance modela za mjerenje"""
        if self.mjerenje_isValid(mjerenje):
            self.mjerenja[mjerenje]['model'] = model
            if recalculate:
                self.recalculate_tab_umjeravanja(self, mjerenje=mjerenje)
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)
################################################################################
    def get_model(self, mjerenje=None):
        """ getter instance modela za mjerenje """
        if self.mjerenje_isValid(mjerenje):
            return self.mjerenja[mjerenje]['model']
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)
################################################################################
    @helperi.activate_wait_spinner
    def recalculate_tab_umjeravanja(self, mjerenje=None):
        """metoda koja racuna parametre za tab s mjerenjem, za zadano mjerenje"""
        print('recalculating tab : ', str(mjerenje))
        if self.mjerenje_isValid(mjerenje):
            if mjerenje == 'konverter':
                kal = self.mjerenja['konverter']['kalkulator']
                kal.racunaj()
                tablica1 = kal.get_rezultate_konvertera()
                lista1 = kal.get_listu_efikasnosti()
                kriterij = kal.get_ec_parametar()
                output = {'rezultat':tablica1,
                          'kriterij':kriterij,
                          'lista_efikasnosti':lista1,
                          'tab':'konverter'}
                self.emit(QtCore.SIGNAL('update_tab_konverter(PyQt_PyObject)'),
                          output)
            elif mjerenje.endswith('-odaziv'):
                output = {'tab':mjerenje}
                self.emit(QtCore.SIGNAL('update_tab_odaziv(PyQt_PyObject)'),
                          output)
            else:
                kal = self.mjerenja[mjerenje]['kalkulator']
                kal.racunaj()
                tablica1 = kal.get_tablicu_rezultata()
                tablica2 = kal.get_provjeru_parametara()
                tablica3 = kal.get_slope_and_offset_map()
                output = {'umjeravanje':tablica1,
                          'testovi':tablica2,
                          'prilagodba':tablica3,
                          'tab':mjerenje}
                self.emit(QtCore.SIGNAL('update_tab_results(PyQt_PyObject)'),
                          output)
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)
################################################################################
    def set_opseg(self, value, recalculate=True):
        """setter opsega mjerenje (value) za zadano mjerenje"""
        value = float(value)
        if value != self.get_opseg():
                self.postavke['opseg'] = value
                if recalculate:
                    for mjerenje in self.mjerenja:
                        self.recalculate_tab_umjeravanja(mjerenje=mjerenje)
                        self.recalculate_tab_umjeravanja(mjerenje='konverter')
                output = {'value':value,
                          'recalculate':recalculate}
                self.emit(QtCore.SIGNAL('promjena_opseg(PyQt_PyObject)'),
                          output)

    def get_opseg(self):
        """getter opsega za zadano mjerenje"""
        return self.postavke['opseg']
################################################################################
    def set_postaje(self, x):
        """Setter postaja. Ulazna vrijednost je mapa postaja
        {postaja1:[uredjaj, uredjaj2], postaja2:[uredjaj3], postaja3:[]...}"""
        if x != self.postaje:
            self.postaje = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_postaje(PyQt_PyObject)'),
                      output)

    def get_postaje(self):
        """Getter postaja"""
        return self.postaje
################################################################################
    def set_uredjaji(self, x):
        """Setter uredjaja. Ulazna vrijednost je mapa uredjaja.
        Kljucevi mape su serijski brojevi uredjaja."""
        if x != self.uredjaji:
            self.uredjaji = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_uredjaji(PyQt_PyObject)'),
                      output)

    def get_uredjaji(self):
        """Getter svih uredjaja"""
        return self.uredjaji
################################################################################
    def set_listaMjerenja(self, x, recalculate=True):
        """Setter liste mjerenja (komponente). Ulazna vrijednost je list"""
        if x != self.listaMjerenja:
            self.listaMjerenja = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_listaMjerenja(PyQt_PyObject)'),
                      output)
            #ako lista nije prazna izaberi prvi element
            if self.listaMjerenja:
                self.set_izabranoMjerenje(self.listaMjerenja[0], recalculate=recalculate)
            else:
                self.set_izabranoMjerenje('None', recalculate=False)

    def get_listaMjerenja(self):
        """Getter za listu mjerenja"""
        return self.listaMjerenja
################################################################################
    def set_listaDilucija(self, x):
        """Setter liste dilucijskih (kalibracijskih) jedinica. Ulazna vrijednost
        je lista stringova"""
        if x != self.listaDilucija:
            self.listaDilucija = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_listaDilucija(PyQt_PyObject)'),
                      output)
            #ako lista nije prazna izaberi prvi element
            if self.listaDilucija:
                self.set_izabranaDilucija(self.listaDilucija[0], recalculate=False)
            else:
                self.set_izabranaDilucija('None', recalculate=False)

    def get_listaDilucija(self):
        """Gettet liste dilucijskih jedinica"""
        return self.listaDilucija
################################################################################
    def set_listaZrak(self, x):
        """Setter liste generatora cistog zraka. Ulazna vrijednost je lista stringova"""
        if x != self.listaZrak:
            self.listaZrak = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_listaZrak(PyQt_PyObject)'),
                      output)
            if self.listaZrak:
                #ako lista nije prazna izaberi prvi element
                self.set_izabraniZrak(self.listaZrak[0], recalculate=False)
            else:
                self.set_izabraniZrak('None', recalculate=False)

    def get_listaZrak(self):
        """Getter liste generatora cistog zraka"""
        return self.listaZrak
################################################################################
    def set_postavke(self, mapa):
        """Setter mape postavki. Primarno se koristi prilikom ucitavanja dokumenta
        iz filea."""
        try:
            self.set_mjernaJedinica(mapa['mjernaJedinica'])
            self.set_izabraniUredjaj(mapa['izabraniUredjaj'])
            self.set_izabranoMjerenje(mapa['izabranoMjerenje'])
            self.set_izabranaPostaja(mapa['izabranaPostaja'])
            self.set_izabranaDilucija(mapa['izabranaDilucija'])
            self.set_izabraniZrak(mapa['izabraniZrak'])
            self.set_opseg(mapa['opseg'])
            self.set_izvorCRM(mapa['izvorCRM'])
            self.set_koncentracijaCRM(mapa['koncentracijaCRM'])
            self.set_sljedivostCRM(mapa['sljedivostCRM'])
            self.set_proizvodjacDilucija(mapa['proizvodjacDilucija'])
            self.set_sljedivostDilucija(mapa['sljedivostDilucija'])
            self.set_proizvodjacCistiZrak(mapa['proizvodjacCistiZrak'])
            self.set_sljedivostCistiZrak(mapa['sljedivostCistiZrak'])
            self.set_norma(mapa['norma'])
            self.set_oznakaIzvjesca(mapa['oznakaIzvjesca'])
            self.set_brojObrasca(mapa['brojObrasca'])
            self.set_revizija(mapa['revizija'])
            self.set_datumUmjeravanja(mapa['datumUmjeravanja'])
            self.set_temperatura(mapa['temperatura'])
            self.set_vlaga(mapa['vlaga'])
            self.set_tlak(mapa['tlak'])
            self.set_napomena(mapa['napomena'])
            self.set_oznakaModelaUredjaja(mapa['oznakaModelaUredjaja'])
            self.set_proizvodjacUredjaja(mapa['proizvodjacUredjaja'])
        except Exception as err:
            logging.error(str(err), exc_info=True)
            #default fallback
            self.set_mjernaJedinica('n/a')
            self.set_izabraniUredjaj('')
            self.set_izabranoMjerenje('n/a')
            self.set_izabranaPostaja('')
            self.set_izabranaDilucija('')
            self.set_izabraniZrak('')
            self.set_opseg(1.0)
            self.set_izvorCRM('')
            self.set_koncentracijaCRM(1.0)
            self.set_sljedivostCRM(2.0)
            self.set_proizvodjacDilucija('')
            self.set_sljedivostDilucija('')
            self.set_proizvodjacCistiZrak('')
            self.set_sljedivostCistiZrak(0.0)
            self.set_norma('')
            self.set_oznakaIzvjesca('')
            self.set_brojObrasca('')
            self.set_revizija('')
            self.set_datumUmjeravanja('')
            self.set_temperatura(0.0)
            self.set_vlaga(0.0)
            self.set_tlak(0.0)
            self.set_napomena('')
            self.set_oznakaModelaUredjaja('')
            self.set_proizvodjacUredjaja('')

    def get_postavke(self):
        """Geter mape postavke. Primarno se koristi prilikom spremanja dokumenta
        iz filea"""
        return self.postavke
################################################################################
    def set_mjernaJedinica(self, x):
        """Setter mjerne jedinice. Ulazna vrijednost je tipa string."""
        if x != self.postavke['mjernaJedinica']:
            x = str(x)
            self.postavke['mjernaJedinica'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_mjernaJedinica(PyQt_PyObject)'),
                      output)

    def get_mjernaJedinica(self):
        """Getter mjerne jedinice, Izlazna vrijednost je tipa string."""
        return self.postavke['mjernaJedinica']
################################################################################
    def set_izabranoMjerenje(self, x, recalculate=True):
        """Setter izabranog mjerenja (komponente). Ulazna vrijednost je string"""
        x = str(x)
        uredjaj = self.get_izabraniUredjaj()
        izabraniZrak = self.get_izabraniZrak()

        if not x in self.listaMjerenja:
            msg = '{0} se ne nalazi na popisu mogucih mjerenja {1}'.format(x, str(self.listaMjerenja))
            raise ValueError(msg)
        if x != self.postavke['izabranoMjerenje']:
            self.postavke['izabranoMjerenje'] = x

            #promjena povezanih polja
            try:
                # promjena mjerne jedinice
                value = self.uredjaji[uredjaj]['komponenta'][x]['mjernaJedinica']
                self.set_mjernaJedinica(value)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            try:
                # promjena izvora certificiranog referentnog materijala
                value = self.cfg.get_konfig_element(x, 'izvor')
                self.set_izvorCRM(value)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            try:
                # promjena max opsega mjerenja
                value = self.uredjaji[uredjaj]['analitickaMetoda']['o']['max']
                self.set_opseg(value, recalculate=False)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            try:
                # promjena norme
                part1 = self.cfg.get_konfig_element(x, 'norma')
                part2 = self.cfg.get_konfig_element(x, 'naziv')
                value = " - ".join([part1, part2])
                self.set_norma(value)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            try:
                # promjena brojObrasca
                value = self.cfg.get_konfig_element(x, 'oznaka')
                self.set_brojObrasca(value)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            try:
                # promjena revizija
                value = self.cfg.get_konfig_element(x, 'revizija')
                self.set_revizija(value)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            try:
                #sljedivost cistog zraka ovisi o komponenti i generatoru cistog zraka
                value = self.cfg.get_konfig_element(izabraniZrak, x)
                value = 2 * float(value) #radi se U(k=2)
                self.set_sljedivostCistiZrak(value, recalculate=False)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            #emit promjenu
            output = {'value':x,
                      'recalculate':recalculate}
            self.emit(QtCore.SIGNAL('promjena_izabranoMjerenje(PyQt_PyObject)'),
                      output)

    def get_izabranoMjerenje(self):
        """Getter izabranog mjerenja"""
        return self.postavke['izabranoMjerenje']
################################################################################
    def set_izabranaPostaja(self, x):
        """Setter izabrane postaje. Ulazna vrijednost je string."""
        if x != self.postavke['izabranaPostaja']:
            x = str(x)
            self.postavke['izabranaPostaja'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_izabranaPostaja(PyQt_PyObject)'),
                      output)

    def get_izabranaPostaja(self):
        """Getter izabrane postaje"""
        return self.postavke['izabranaPostaja']
################################################################################
    def set_izabraniUredjaj(self, x, recalculate=True):
        """Setter izabranog uredjaja. Ulazna vrijednost je string."""
        if x != self.postavke['izabraniUredjaj']:
            x = str(x)
            self.postavke['izabraniUredjaj'] = x
            #postavi novog proizvodjaca i model uredjaja
            value = str(self.uredjaji[x]['oznakaModela'])
            self.set_oznakaModelaUredjaja(value)
            value = str(self.uredjaji[x]['proizvodjac'])
            self.set_proizvodjacUredjaja(value)
            #postavi opseg
            try:
                opseg = self.uredjaji[x]['analitickaMetoda']['o']['max']
                self.set_opseg(opseg, recalculate=False)
            except Exception as err:
                msg = '\nGreska prilikom dohvacanja vrijednosti opsega za uredjaj {0}'.format(str(x))
                logging.error(set(err)+msg, exc_info=True)
            #recalculate all tabs
            if recalculate:
                for mjerenje in self.mjerenja:
                    self.recalculate_tab_umjeravanja(mjerenje=mjerenje)
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_izabraniUredjaj(PyQt_PyObject)'),
                      output)

    def get_izabraniUredjaj(self):
        """Getter izabranog uredjaja"""
        return self.postavke['izabraniUredjaj']
################################################################################
    def set_izabranaDilucija(self, x, recalculate=True):
        """Setter izabrane dilucijske jedinice. Ulazna vrijednost je string."""
        x = str(x)
        if not x in self.listaDilucija:
            msg = '{0} se ne nalazi na popisu mogucih dilucijskih jedinica {1}'.format(x, str(self.listaDilucija))
            raise ValueError(msg)
        if x != self.postavke['izabranaDilucija']:
            self.postavke['izabranaDilucija'] = x
            #promjena povezanih polja
            try:
                # dilucija proizvodjac
                value = self.cfg.get_konfig_element(x, 'proizvodjac')
                self.set_proizvodjacDilucija(value)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            try:
                # dilucija sljedivost
                part1 = self.cfg.get_konfig_element(x, 'MFC_NUL_Plin_sljedivost')
                part2 = self.cfg.get_konfig_element(x, 'MFC_KAL_PLIN_sljedivost')
                part3 = self.cfg.get_konfig_element(x, 'GENERATOR_OZONA_sljedivost')
                value = ", ".join([part1, part2, part3])
                self.set_sljedivostDilucija(value)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            #recalculate all tabs
            if recalculate:
                for mjerenje in self.mjerenja:
                    self.recalculate_tab_umjeravanja(mjerenje=mjerenje)
            #emit change
            output = {'value':x,
                      'recalculate':recalculate}
            self.emit(QtCore.SIGNAL('promjena_izabranaDilucija(PyQt_PyObject)'),
                      output)

    def get_izabranaDilucija(self):
        """Getter izabrane dilucijske jedinice"""
        return self.postavke['izabranaDilucija']
################################################################################
    def set_izabraniZrak(self, x, recalculate=True):
        """Setter izabranog generatora cistog zraka. Ulazna vrijednost je string"""
        x = str(x)
        izabranoMjerenje = self.get_izabranoMjerenje()
        if not x in self.listaZrak:
            msg = '{0} se ne nalazi na popisu mogucih generatora cistog zraka {1}'.format(x, str(self.listaZrak))
            raise ValueError(msg)
        if x != self.postavke['izabraniZrak']:
            self.postavke['izabraniZrak'] = x
            # promjena povezanih polja
            try:
                # proizvodjac
                value = self.cfg.get_konfig_element(x, 'proizvodjac')
                self.set_proizvodjacCistiZrak(value)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            try:
                # sljedivost
                value = self.cfg.get_konfig_element(x, izabranoMjerenje)
                value = 2*float(value) #get_konfig_element vraca string..za U(k=2)
                self.set_sljedivostCistiZrak(value, recalculate=False)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            #recalculate all tabs
            if recalculate:
                for mjerenje in self.mjerenja:
                    self.recalculate_tab_umjeravanja(mjerenje=mjerenje)
            #emit change
            output = {'value':x,
                      'recalculate':recalculate}
            self.emit(QtCore.SIGNAL('promjena_izabraniZrak(PyQt_PyObject)'),
                      output)

    def get_izabraniZrak(self):
        """Getter izabranog generatora cistog zraka"""
        return self.postavke['izabraniZrak']
################################################################################
    def set_koncentracijaCRM(self, x, recalculate=True):
        """Setter koncentracije certificiranog referentnog materijala. Ulazna
        vrijednost je tipa float"""
        x = float(x)
        if x != self.postavke['koncentracijaCRM']:
            self.postavke['koncentracijaCRM'] = x
            #recalculate all tabs
            if recalculate:
                for mjerenje in self.mjerenja:
                    self.recalculate_tab_umjeravanja(mjerenje=mjerenje)
            #emit change
            output = {'value':x,
                      'recalculate':recalculate}
            self.emit(QtCore.SIGNAL('promjena_koncentracijaCRM(PyQt_PyObject)'),
                      output)

    def get_koncentracijaCRM(self):
        """Getter koncentracije certificiranog referentnog materijala"""
        return self.postavke['koncentracijaCRM']
################################################################################
    def set_sljedivostCRM(self, x, recalculate=True):
        """Setter sljedivosti certificiranog referentnog materijala. Ulazna vrijednost
        je tipa float"""
        x = float(x)
        if x != self.postavke['sljedivostCRM']:
            self.postavke['sljedivostCRM'] = x
            #recalculate all tabs
            if recalculate:
                for mjerenje in self.mjerenja:
                    self.recalculate_tab_umjeravanja(mjerenje=mjerenje)
            #emit change
            output = {'value':x,
                      'recalculate':recalculate}
            self.emit(QtCore.SIGNAL('promjena_sljedivostCRM(PyQt_PyObject)'),
                      output)

    def get_sljedivostCRM(self):
        """Getter sljedivosti certificiranog referentnog materijala"""
        return self.postavke['sljedivostCRM']
################################################################################
    def set_proizvodjacDilucija(self, x):
        """Setter proizvodjaca dilucijske (kalibracijske) jedinice. Ulazna vrijednost
        je tipa string"""
        x = str(x)
        if x != self.postavke['proizvodjacDilucija']:
            self.postavke['proizvodjacDilucija'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_proizvodjacDilucija(PyQt_PyObject)'),
                      output)

    def get_proizvodjacDilucija(self):
        """Getter proizvodjaca dilucijske (kalibracijske) jedinice."""
        return self.postavke['proizvodjacDilucija']
################################################################################
    def set_sljedivostDilucija(self, x):
        """Setter sljedivosti dilucijske (kalibracijske) jedinice. Ulazna vrijednost
        je tipa string"""
        x = str(x)
        if x != self.postavke['sljedivostDilucija']:
            self.postavke['sljedivostDilucija'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_sljedivostDilucija(PyQt_PyObject)'),
                      output)

    def get_sljedivostDilucija(self):
        """Getter sljedivosti dilucijske (kalibracijske) jedinice"""
        return self.postavke['sljedivostDilucija']
################################################################################
    def set_proizvodjacCistiZrak(self, x):
        """Setter proizvodjaca generatora cistog zraka. Ulazna vrijednost je tipa
        string"""
        x = str(x)
        if x != self.postavke['proizvodjacCistiZrak']:
            self.postavke['proizvodjacCistiZrak'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_proizvodjacCistiZrak(PyQt_PyObject)'),
                      output)

    def get_proizvodjacCistiZrak(self):
        """Getter proizvodjaca generatora cistog zraka"""
        return self.postavke['proizvodjacCistiZrak']
################################################################################
    def set_sljedivostCistiZrak(self, x, recalculate=True):
        """Setter sljedivosti generatora cistog zraka. Ulazna vrijednost je tipa
        float"""
        x = float(x)
        if x != self.postavke['sljedivostCistiZrak']:
            self.postavke['sljedivostCistiZrak'] = x
            #recalculate all tabs
            if recalculate:
                for mjerenje in self.mjerenja:
                    self.recalculate_tab_umjeravanja(mjerenje=mjerenje)
            #emit change
            output = {'value':x,
                      'recalculate':recalculate}
            self.emit(QtCore.SIGNAL('promjena_sljedivostCistiZrak(PyQt_PyObject)'),
                      output)

    def get_sljedivostCistiZrak(self):
        """Getter sljedivosti generatora cistog zraka"""
        return self.postavke['sljedivostCistiZrak']
################################################################################
    def set_norma(self, x):
        """Setter norme mjerenja (norma + naziv). Ulazna vrijednost je tipa string."""
        x = str(x)
        if x != self.postavke['norma']:
            self.postavke['norma'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_norma(PyQt_PyObject)'),
                      output)

    def get_norma(self):
        """Getter norme mjerenja (norma + naziv)"""
        return self.postavke['norma']
################################################################################
    def set_oznakaIzvjesca(self, x):
        """Setter oznake izvjesca. Ulazna vrijednost je tipa."""
        x = str(x)
        if x != self.postavke['oznakaIzvjesca']:
            self.postavke['oznakaIzvjesca'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_oznakaIzvjesca(PyQt_PyObject)'),
                      output)

    def get_oznakaIzvjesca(self):
        """Getter oznake izvjesca"""
        return self.postavke['oznakaIzvjesca']
################################################################################
    def set_brojObrasca(self, x):
        """Setter broja obrasca. Ulazni parametar je tipa string"""
        x = str(x)
        if x != self.postavke['brojObrasca']:
            self.postavke['brojObrasca'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_brojObrasca(PyQt_PyObject)'),
                      output)

    def get_brojObrasca(self):
        """Getter broj obrasca"""
        return self.postavke['brojObrasca']
################################################################################
    def set_revizija(self, x):
        """Setter broja revizije. Ulazni parametar je tipa string"""
        x = str(x)
        if x != self.postavke['revizija']:
            self.postavke['revizija'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_revizija(PyQt_PyObject)'),
                      output)

    def get_revizija(self):
        """Getter broja revizije"""
        return self.postavke['revizija']
################################################################################
    def set_datumUmjeravanja(self, x):
        """Setter datuma umjeravanja. Ulazna vrijednost je string"""
        x = str(x)
        if x != self.postavke['datumUmjeravanja']:
            self.postavke['datumUmjeravanja'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_datumUmjeravanja(PyQt_PyObject)'),
                      output)

    def get_datumUmjeravanja(self):
        """Getter datuma umjeravanja"""
        return self.postavke['datumUmjeravanja']
################################################################################
    def set_temperatura(self, x):
        """Setter okolisnih uvijeta, temperatura. Ulazna vrijednost je float"""
        x = float(x)
        if x != self.postavke['temperatura']:
            self.postavke['temperatura'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_temperatura(PyQt_PyObject)'),
                      output)

    def get_temperatura(self):
        """Gettter okolisnih uvijeta, temperatura"""
        return self.postavke['temperatura']
################################################################################
    def set_vlaga(self, x):
        """Setter okolisnih uvijeta, vlaga. Ulazna vrijednost je float"""
        x = float(x)
        if x != self.postavke['vlaga']:
            self.postavke['vlaga'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_vlaga(PyQt_PyObject)'),
                      output)

    def get_vlaga(self):
        """Getter okolisnih uvijeta, vlaga."""
        return self.postavke['vlaga']
################################################################################
    def set_tlak(self, x):
        """Setter okolisnih uvijeta, tlak. Ulazna vrijednost je float"""
        x = float(x)
        if x != self.postavke['tlak']:
            self.postavke['tlak'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_tlak(PyQt_PyObject)'),
                      output)

    def get_tlak(self):
        """Getter okolisnih uvijeta, tlak"""
        return self.postavke['tlak']
################################################################################
    def set_napomena(self, x):
        """Setter napomene umjeravanja. Ulazna vrijednost je string"""
        x = str(x)
        if x != self.postavke['napomena']:
            self.postavke['napomena'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_napomena(PyQt_PyObject)'),
                      output)

    def get_napomena(self):
        """Getter napomena umjeravanja"""
        return self.postavke['napomena']
################################################################################
    def set_oznakaModelaUredjaja(self, x):
        """Setter oznake modela izabranog uredjaja"""
        x = str(x)
        if x != self.postavke['oznakaModelaUredjaja']:
            self.postavke['oznakaModelaUredjaja'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_oznakaModelaUredjaja(PyQt_PyObject)'),
                      output)

    def get_oznakaModelaUredjaja(self):
        """getter oznake modela uredjaja"""
        return self.postavke['oznakaModelaUredjaja']
################################################################################
    def set_proizvodjacUredjaja(self, x):
        """setter proizvodjaca izabranog uredjaja"""
        x = str(x)
        if x != self.postavke['proizvodjacUredjaja']:
            self.postavke['proizvodjacUredjaja'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_proizvodjacUredjaja(PyQt_PyObject)'),
                      output)

    def get_proizvodjacUredjaja(self):
        """getter proizvodjaca izabranog uredjaja"""
        return self.postavke['proizvodjacUredjaja']
################################################################################
    def set_cNOx50(self, x, recalculate=True):
        """Setter za parametar cNOx50. Ulazna vrijednost je float"""
        x = float(x)
        if self.mjerenje_isValid('konverter'):
            if x != self.mjerenja['konverter']['cNOx50']:
                self.mjerenja['konverter']['cNOx50'] = x
                #recalculate konverter
                self.recalculate_tab_umjeravanja(mjerenje='konverter')
                output = {'value':x,
                          'recalculate':recalculate}
                self.emit(QtCore.SIGNAL('promjena_cNOx50(PyQt_PyObject)'),
                          output)
        else:
            msg = 'ne postoji mapa konverter'
            logging.warning(msg)


    def get_cNOx50(self):
        """Getter za vijednost cNOx50 parametra"""
        return self.mjerenja['konverter']['cNOx50']

    def set_cNOx95(self, x, recalculate=True):
        """Setter za parametar cNOx95. Ulazna vrijednost je float"""
        x = float(x)
        if self.mjerenje_isValid('konverter'):
            if x != self.mjerenja['konverter']['cNOx95']:
                self.mjerenja['konverter']['cNOx95'] = x
                output = {'value':x,
                          'recalculate':recalculate}
                #recalculate konverter
                self.recalculate_tab_umjeravanja(mjerenje='konverter')
                self.emit(QtCore.SIGNAL('promjena_cNOx95(PyQt_PyObject)'),
                          output)
        else:
            msg = 'ne postoji mapa konverter'
            logging.warning(msg)

    def get_cNOx95(self):
        """Getter za vijednost cNOx95 parametra"""
        return self.mjerenja['konverter']['cNOx95']
################################################################################
    def set_provjeraKonvertera(self, x):
        """
        Setter za "globalnu" provjeru konvertera (check za prikaz taba).
        Ulazni parametar je boolean.
        """
        if x != self.provjeraKonvertera:
            self.provjeraKonvertera = x
            self.emit(QtCore.SIGNAL('display_konverter(PyQt_PyObject)'),
                      x)

    def get_provjeraKonvertera(self):
        """
        Getter za globalnu provjeru konvertera (check za prikaz taba).
        """
        return self.provjeraKonvertera
################################################################################
    def set_provjeraOdaziv(self, x):
        """
        Setter za "globalnu" provjeru odaziva (check za prikaz tabova odaziva).
        Ulazni parametar je boolean.
        """
        if x != self.provjeraOdaziv:
            self.provjeraOdaziv = x
            self.emit(QtCore.SIGNAL('display_odaziv(PyQt_PyObject)'),
                      x)

    def get_provjeraOdaziv(self):
        """
        Getter za "globalnu" provjeru odaziva (check za prikaz tabova odaziva).
        """
        return self.provjeraOdaziv
################################################################################
    def set_provjeraUmjeravanje(self, x):
        """
        Setter za provjeru umjeravanja. Ulazni parametar je boolean.
        """
        if x != self.provjeraUmjeravanje:
            self.provjeraUmjeravanje = x
            self.emit(QtCore.SIGNAL('display_umjeravanje(PyQt_PyObject)'),
                      x)

    def get_provjeraUmjeravanje(self):
        """Getter z provjeru umjeravanja"""
        return self.provjeraUmjeravanje
################################################################################
    def set_provjeraPonovljivost(self, x):
        """
        Setter za provjeru ponovljivosti. Ulazni parametar je boolean.
        """
        if x != self.provjeraPonovljivost:
            self.provjeraPonovljivost = x
            self.emit(QtCore.SIGNAL('display_ponovljivost(PyQt_PyObject)'),
                      x)

    def get_provjeraPonovljivost(self):
        """Getter z provjeru ponovljivosti"""
        return self.provjeraPonovljivost
################################################################################
    def set_provjeraLinearnost(self, x):
        """
        Setter za provjeru linearnosti. Ulazni parametar je boolean.
        """
        if x != self.provjeraLinearnost:
            self.provjeraLinearnost = x
            self.emit(QtCore.SIGNAL('display_linearnost(PyQt_PyObject)'),
                      x)

    def get_provjeraLinearnost(self):
        """
        Getter za provjeru linearnosti.
        """
        return self.provjeraLinearnost
################################################################################
    def set_izvorCRM(self, x):
        """Setter izvora certificiranog referentnog materijala. Ulazna vrijednost
        je string"""
        x = str(x)
        if x != self.postavke['izvorCRM']:
            self.postavke['izvorCRM'] = x
            self.emit(QtCore.SIGNAL('promjena_izvorCRM(PyQt_PyObject)'),
                      x)

    def get_izvorCRM(self):
        """Getter izvora certificiranog referentnog materijala."""
        return self.postavke['izvorCRM']
################################################################################
    def dokument_to_dict(self):
        """
        Metoda je zaduzena za generiranje mape sa podacima stanja objekta.
        """
        output = {}
        output['konfig'] = self.cfg
        output['postaje'] = self.get_postaje()
        output['uredjaji'] = self.get_uredjaji()
        output['listaMjerenja'] = self.get_listaMjerenja()
        output['listaDilucija'] = self.get_listaDilucija()
        output['listaZrak'] = self.get_listaZrak()
        output['postavke'] = self.get_postavke()
        output['provjeraKonvertera'] = self.get_provjeraKonvertera()
        output['provjeraOdaziv'] = self.get_provjeraOdaziv()
        output['provjeraUmjeravanje'] = self.get_provjeraUmjeravanje()
        output['provjeraPonovljivost'] = self.get_provjeraPonovljivost()
        output['provjeraLinearnost'] = self.get_provjeraLinearnost()
        #podaci za rekonstrukciju pojedinih tabova...
        mjer = {}
        for mjerenje in self.mjerenja:
            if mjerenje == 'konverter':
                mjer['konverter'] = {}
                mjer['konverter']['mjerenje'] = self.mjerenja[mjerenje]['mjerenje']
                mjer['konverter']['cNOx50'] = self.mjerenja[mjerenje]['cNOx50']
                mjer['konverter']['cNOx95'] = self.mjerenja[mjerenje]['cNOx95']
                mjer['konverter']['generateReportCheck'] = self.mjerenja[mjerenje]['generateReportCheck']
                #podaci vezani za model
                model = self.mjerenja[mjerenje]['model']
                tocke = model.get_tocke()
                frejm = model.get_frejm()
                start = model.get_start()
                mjer['konverter']['model'] = {}
                mjer['konverter']['model']['start'] = start
                mjer['konverter']['model']['frejm'] = frejm
                mjer['konverter']['model']['tocke'] = []
                for tocka in tocke:
                    obj = {}
                    obj['ime'] = tocka.ime
                    obj['indeksi'] = tocka.indeksi
                    obj['crefFaktor'] = tocka.crefFaktor
                    obj['rgba'] = (tocka.boja.red(), tocka.boja.green(), tocka.boja.blue(), tocka.boja.alpha())
                    mjer['konverter']['model']['tocke'].append(obj)
            elif mjerenje.endswith('-odaziv'):
                mjer[mjerenje] = {}
                mjer[mjerenje]['mjerenje'] = self.mjerenja[mjerenje]['mjerenje']
                mjer[mjerenje]['highLimit'] = self.mjerenja[mjerenje]['highLimit']
                mjer[mjerenje]['lowLimit'] = self.mjerenja[mjerenje]['lowLimit']
                mjer[mjerenje]['generateReportCheck'] = self.mjerenja[mjerenje]['generateReportCheck']
                mjer[mjerenje]['rezultatStupci'] = self.mjerenja[mjerenje]['rezultatStupci']
                #nedostaje feedback prilikom loadanja... frejm ostaje isti
                mjer[mjerenje]['rezultatFrejm'] = self.mjerenja[mjerenje]['rezultatFrejm']
                #podaci vezani za model
                model = self.mjerenja[mjerenje]['model']
                frejm = model.get_frejm()
                naziv = mjerenje[:-7]
                mjer[mjerenje]['naziv'] = naziv
                mjer[mjerenje]['frejm'] = frejm
            else:
                mjer[mjerenje] = {}
                mjer[mjerenje]['mjerenje'] = self.mjerenja[mjerenje]['mjerenje']
                mjer[mjerenje]['testUmjeravanje'] = self.mjerenja[mjerenje]['testUmjeravanje']
                mjer[mjerenje]['testPonovljivost'] = self.mjerenja[mjerenje]['testPonovljivost']
                mjer[mjerenje]['testLinearnost'] = self.mjerenja[mjerenje]['testLinearnost']
                mjer[mjerenje]['generateReportCheck'] = self.mjerenja[mjerenje]['generateReportCheck']
                #podaci za model...
                model = self.mjerenja[mjerenje]['model']
                frejm = model.get_frejm()
                tocke = model.get_tocke()
                start = model.get_start()
                mjer[mjerenje]['model'] = {}
                mjer[mjerenje]['model']['start'] = start
                mjer[mjerenje]['model']['frejm'] = frejm
                mjer[mjerenje]['model']['tocke'] = []
                for tocka in tocke:
                    obj = {}
                    obj['ime'] = tocka.ime
                    obj['indeksi'] = tocka.indeksi
                    obj['crefFaktor'] = tocka.crefFaktor
                    obj['rgba'] = (tocka.boja.red(), tocka.boja.green(), tocka.boja.blue(), tocka.boja.alpha())
                    mjer[mjerenje]['model']['tocke'].append(obj)
        output['mjerenja'] = mjer
        return output
################################################################################
    def dict_to_dokument(self, mapa):
        """
        Metoda je zaduzena za upisivanje podataka iz mape u membere.
        """
        #TODO! METODA KREPA PRILIKOM PREBACIVANJA LINEARNOSTI, ODAZIV SE NE UPDEJTA DOBRO
        #tab postavke
        self.cfg = mapa['konfig']
        self.set_postaje(mapa['postaje'])
        self.set_uredjaji(mapa['uredjaji'])
        self.set_listaMjerenja(mapa['listaMjerenja'])
        self.set_listaDilucija(mapa['listaDilucija'])
        self.set_listaZrak(mapa['listaZrak'])
        self.set_postavke(mapa['postavke'])
        #opceniti checkovi
        self.set_provjeraUmjeravanje(mapa['provjeraUmjeravanje'])
        self.set_provjeraPonovljivost(mapa['provjeraPonovljivost'])
        self.set_provjeraLinearnost(mapa['provjeraLinearnost'])
        #postavke pojedinih tabova
        mjer = mapa['mjerenja']
        for mjerenje in mjer:
            if mjerenje == 'konverter':
                self.set_cNOx50(mjer['konverter']['cNOx50'])
                self.set_cNOx95(mjer['konverter']['cNOx95'])
                self.set_generateReportCheck(mjer['konverter']['generateReportCheck'], mjerenje='konverter')
                #rekonstrukcija objekta tocke
                tocke = []
                for tocka in mjer['konverter']['model']['tocke']:
                    dot = Tocka()
                    dot.ime = tocka['ime']
                    dot.indeksi = tocka['indeksi']
                    dot.crefFaktor = tocka['crefFaktor']
                    r, g, b, a = tocka['rgba']
                    dot.boja = QtGui.QColor(r, g, b, a)
                    tocke.append(dot)
                #update modela
                model = self.get_model(mjerenje='konverter')
                model.set_frejm(mjer['konverter']['model']['frejm'])
                model.set_tocke(tocke)
                model.set_start(mjer['konverter']['model']['start'])
            elif mjerenje.endswith('-odaziv'):
                self.set_generateReportCheck(mjer[mjerenje]['generateReportCheck'])
                self.mjerenja[mjerenje]['highLimit'] = mjer[mjerenje]['highLimit']
                self.mjerenja[mjerenje]['lowLimit'] = mjer[mjerenje]['lowLimit']
                self.mjerenja[mjerenje]['rezultatStupci'] = mjer[mjerenje]['rezultatStupci']
                self.mjerenja[mjerenje]['rezultatFrejm'] = mjer[mjerenje]['rezultatFrejm']
                model = self.get_model(mjerenje=mjerenje)
                model.set_frejm(mjer[mjerenje]['frejm'])
                model.set_high_limit(mjer[mjerenje]['highLimit'])
                model.set_low_limit(mjer[mjerenje]['lowLimit'])
                #reinicijaliziraj tab sa odazivom.
                out = {'mjerenje':mjerenje}
                self.emit(QtCore.SIGNAL('reinitialize_tab_odaziv(PyQt_PyObject)'),
                          out)
            else:
                tocke = []
                for tocka in mjer[mjerenje]['model']['tocke']:
                    dot = Tocka()
                    dot.ime = tocka['ime']
                    dot.indeksi = tocka['indeksi']
                    dot.crefFaktor = tocka['crefFaktor']
                    r, g, b, a = tocka['rgba']
                    dot.boja = QtGui.QColor(r, g, b, a)
                    tocke.append(dot)
                frejm = mjer[mjerenje]['model']['frejm']
                start = mjer[mjerenje]['model']['start']
                model = self.get_model(mjerenje=mjerenje)
                model.set_frejm(frejm)
                model.set_tocke(tocke)
                model.set_start(start)
                #update checkova
                self.set_generateReportCheck(mjer[mjerenje]['generateReportCheck'], mjerenje=mjerenje)
                self.set_testUmjeravanje(mjer[mjerenje]['testUmjeravanje'], mjerenje=mjerenje, recalculate=False)
                self.set_testPonovljivost(mjer[mjerenje]['testPonovljivost'], mjerenje=mjerenje, recalculate=False)
                self.set_testLinearnost(mjer[mjerenje]['testLinearnost'], mjerenje=mjerenje, recalculate=False)
        self.set_provjeraOdaziv(mapa['provjeraOdaziv'])
        self.set_provjeraKonvertera(mapa['provjeraKonvertera'])
################################################################################