# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 09:41:20 2015

@author: DHMZ-Milic

"""
import gc
import sip
import logging
import copy
import numpy as np
from PyQt4 import QtGui, QtCore, uic
import app.reportgen.reportgen as pdfreport
import app.model.konfig_klase as konfig
import app.model.model as doc
import app.model.kalkulator as calc
import app.model.frejm_model as modeli
import app.view.read_file_wizard as datareader
import app.view.dijalog_edit_tocke as dotedit
import app.view.tab_rezultat as rezultat
import app.view.tab_postavke as postavke
import app.view.tab_kolektor as kolektor
import app.view.tab_konverter as konverter


BASE, FORM = uic.loadUiType('./app/view/uiFiles/display.ui')
class GlavniProzor(BASE, FORM):
    """
    Gui element glavnog prozora
    """
    def __init__(self, cfg=None, parent=None):
        super(BASE, self).__init__(parent)
        self.setupUi(self)

        ### setup konfig elemente ###
        try:
            self.konfiguracija = konfig.MainKonfig(cfg=cfg)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            raise SystemExit('Konfiguracijski file nije ispravan.')

        ### setup dokument ###
        self.dokument = doc.DokumentModel(cfg=self.konfiguracija)

        ### setup objekte za racunanje ###
        self.kalkulator = calc.RacunUmjeravanja(doc=self.dokument)
        self.konverterKalkulator = calc.ProvjeraKonvertera(doc=self.dokument)

        ### setup membere ###
        self.dictTabRezultata = {}
        self.otvoreniProzori = {}
        self.idCounter = 1

        ### setup konstantne tabove ###
        self.tabPostavke = postavke.PostavkeTab(dokument=self.dokument)
        self.tabKonverter = konverter.KonverterPanel(dokument=self.dokument)

        self.glavniTabWidget.addTab(self.tabPostavke, 'Postavke')

        ### Setup modela za prikaz sirovih podataka###
        self.siroviPodaciModel = modeli.SiroviFrameModel()
        self.siroviPodaciView.setModel(self.siroviPodaciModel)
        self.siroviPodaciView.horizontalHeader().setStretchLastSection(True)

        ### Setup signala i slotova ###
        self.setup_signal_connections()

        ### inicijalni setup dokumenta ###
        self.dokument.init_listaDilucija()
        self.dokument.init_listaZrak()

    def otvori_prozor(self):
        """otvori prozor, spoji sa necim"""
        #create prozor i spremi ga u mapu sa unikatnim id
        prozor = kolektor.Kolektor(dokument=self.dokument, uid=self.idCounter)
        tekst = 'Prikupljanje podataka {0}'.format(str(self.idCounter))
        prozor.setWindowTitle(tekst)
        self.otvoreniProzori[self.idCounter] = prozor
        self.otvoreniProzori[self.idCounter].show()
        #connect signal i slot
        self.connect(self.otvoreniProzori[self.idCounter],
                     QtCore.SIGNAL('spremi_preuzete_podatke(PyQt_PyObject)'),
                     self.aktiviraj_ucitane_podatke)
        self.idCounter = self.idCounter + 1

    def setup_signal_connections(self):
        """definiranje komunikacije iumedju objekata"""
        ### actions ###
        self.action_otvori_kolektor.triggered.connect(self.otvori_prozor)
        self.action_Exit.triggered.connect(self.close)
        self.action_ucitaj_podatke.triggered.connect(self.read_data_from_csv)
        self.action_spremi.triggered.connect(self.save_umjeravanje_to_file)
        self.action_ucitaj.triggered.connect(self.load_umjeravanje_from_file)
        self.action_Napravi_pdf_report.triggered.connect(self.napravi_pdf_report)

        ### gui widgeti###
        self.glavniTabWidget.currentChanged.connect(self.promjena_aktivnog_taba)
        self.siroviPodaciView.clicked.connect(self.odaberi_pocetak_podataka)

        ### zahtjevi za ponovnim racunanjem podataka ###
        self.connect(self.tabPostavke,
                     QtCore.SIGNAL('postavke_request_recalculate'),
                     self.recalculate)
        self.connect(self.tabKonverter,
                     QtCore.SIGNAL('konverter_request_recalculate'),
                     self.recalculate_konverter)
        self.connect(self.dokument,
                     QtCore.SIGNAL('dokument_request_recalculate'),
                     self.recalculate)

        ### povratne informacije iz dokumenta ###
        # update tablice sirovih podataka - [tocke, start, boolean za recalculate]
        self.connect(self.dokument,
                     QtCore.SIGNAL('update_tablicu_sirovihPodataka_umjeravanje(PyQt_PyObject)'),
                     self.update_tablice_sirovih_podataka)
        self.connect(self.dokument,
                     QtCore.SIGNAL('update_tablicu_sirovihPodataka_konverter(PyQt_PyObject)'),
                     self.update_tablice_sirovih_podataka)
        # dodavanje, brisanje i editiranje tocaka umjeravanja
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_tockeUmjeravanja(PyQt_PyObject)'),
                     self.update_tablice_sirovih_podataka)
        # load ucitanih podataka
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_siroviPodaci(PyQt_PyObject)'),
                     self.set_ucitane_sirove_podatke_load)
        #promjena izabrani uredjaj
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_izabraniUredjaj(PyQt_PyObject)'),
                     self.set_labelUredjaj)
        #promjena izabrana postaja
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_izabranaPostaja(PyQt_PyObject)'),
                     self.set_labelPostaja)
        #promjena izabrani csv file
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_izabraniPathCSV(PyQt_PyObject)'),
                     self.set_labelDatoteka)

        ### toggle tabova ###
        self.connect(self.tabPostavke,
                     QtCore.SIGNAL('enable_tab_konverter(PyQt_PyObject)'),
                     self.toggle_tab_konverter)

    def clear_tabove_rezultata(self):
        """
        Metoda je zaduzena za uklanjanje tabova sa rezultatima iz QTabWidgeta,
        (self.glavniTabWidget).
        """
        # prebaci aktivni tab na 'Postavke' jer se on nikada ne brise
        self.glavniTabWidget.setCurrentWidget(self.tabPostavke)
        # makni tabove sa reultatima
        for tab in self.dictTabRezultata:
            widget = self.dictTabRezultata[tab]
            self.glavniTabWidget.removeTab(self.glavniTabWidget.indexOf(widget))
        # izbrisi sve objekte sa rezultatima
        for key in self.dictTabRezultata:
            sip.delete(self.dictTabRezultata[key])
            self.dictTabRezultata[key] = None
        # clear dicta tabova
        self.dictTabRezultata.clear()
        gc.collect() #force garbage collection

    def test_for_nox(self):
        """metoda provjerava da li u stupcima sirovih podataka postoje nox
        komponente. Metoda vraca boolean"""
        frejm = self.dokument.get_siroviPodaci()
        stupci = list(frejm.columns)
        set1 = set([str(i).lower() for i in stupci])
        set2 = set(['no','nox','no2'])
        if len(set2.intersection(set1)) != 0:
            return True
        else:
            return False

    def postavi_tabove_rezultata(self):
        """
        Metoda je zaduzena za postavljanje tabova sa rezultatima u QTabWidget.
        Po potrebi se postavlja tab za provjeru konvertera (u slucaju NOx)

        siroviPodaci moraju biti postavljeni u dokumentu prije poziva ove metode
        """
        frejm = self.dokument.get_siroviPodaci()
        stupci = sorted(list(frejm.columns))
        for stupac in stupci:
            tab = rezultat.RezultatPanel(dokument=self.dokument, plin=str(stupac))
            naziv = "-".join(['Rezultat', str(stupac)])
            self.dictTabRezultata[str(stupac)] = tab
            self.glavniTabWidget.addTab(tab, naziv)
            self.connect(tab,
                         QtCore.SIGNAL('panel_dodaj_umjernu_tocku'),
                         self.add_red_umjeravanje)
            self.connect(tab,
                         QtCore.SIGNAL('panel_makni_umjernu_tocku(PyQt_PyObject)'),
                         self.remove_red_umjeravanje)
            self.connect(tab,
                         QtCore.SIGNAL('panel_edit_umjernu_tocku(PyQt_PyObject)'),
                         self.edit_red_umjeravanje)
            #zahtjev za ponovnim racunanjem podataka iz taba rezultata
            self.connect(tab,
                         QtCore.SIGNAL('rezultat_request_recalculate'),
                         self.recalculate)

    def set_ucitane_sirove_podatke_load(self, x):
        """setter sirovih podataka ucitanih iz spremljenog filea umjeravanja.
        Ulazni parametar x je pandas frejm podataka"""
        self.siroviPodaciModel.set_frejm(x)
        self.siroviPodaciView.update()
        #generiraj potrebne tabove
        self.postavi_tabove_rezultata()

    def read_data_from_csv(self):
        """ucitavanje sirovih podataka iz csv filea putem wizarda"""
        self.fileWizard = datareader.CarobnjakZaCitanjeFilea(uredjaji=self.dokument.get_uredjaji(),
                                                             postaje=self.dokument.get_postaje())
        prihvacen = self.fileWizard.exec_()
        if prihvacen:
            frejm = self.fileWizard.get_frejm()
            lokacija = self.fileWizard.get_postaja()
            uredjaj = self.fileWizard.get_uredjaj()
            path = str(self.fileWizard.get_path_do_filea())
            # postavi info o ucitanom fileu
            self.dokument.set_izabraniUredjaj(uredjaj)
            self.dokument.set_izabranaPostaja(lokacija)
            self.dokument.set_izabraniPathCSV(path)
            self.clear_tabove_rezultata()
            self.dokument.set_siroviPodaci(frejm)
            #reset start umjeravanja na 0 ... reinit tocke i start
            self.dokument.reinitialize_tocke_i_start(recalculate=False)
            #update combobox za izbor mjerenja
            komponente = set(self.dokument.uredjaji[uredjaj]['komponente'])
            komponente.remove('None')
            komponente = list(komponente)
            self.dokument.set_listaMjerenja(komponente)
            self.recalculate()

    def add_red_umjeravanje(self):
        """metoda (slot) za dodavanje tocaka u dokument"""
        self.dokument.dodaj_umjernu_tocku()

    def remove_red_umjeravanje(self, x):
        """metoda za brisanje tocke za umjeravanje iz dokumenta, x je broj redka"""
        red = int(x)
        self.dokument.makni_umjernu_tocku(red)

    def edit_red_umjeravanje(self, x):
        """metoda za editiranje umjerne tocke uz pomoc dijaloga"""
        red = int(x)
        self.edit_tocku_dijalog(red)

    def edit_tocku_dijalog(self, indeks):
        """
        Poziv dijaloga za edit vrijednosti parametara izabrane tocke.
        ulazni parametar indeks je indeks pod kojim se ta tocka nalazi
        u listi self.konfiguracija.umjerneTocke
        """
        tocke = copy.deepcopy(self.dokument.get_tockeUmjeravanja())
        podaci = self.dokument.get_siroviPodaci().copy()
        start = self.dokument.get_siroviPodaciStart()
        self.dijalog = dotedit.EditTockuDijalog(indeks=indeks,
                                                tocke=tocke,
                                                frejm=podaci,
                                                start=start,
                                                parent=None)
        if self.dijalog.exec_():
            dots = self.dijalog.get_tocke()
            tocka = dots[indeks]
            self.dokument.zamjeni_umjernu_tocku(indeks, tocka)

    def izracunaj_rezultat_umjeravanja_za_plin(self, plin):
        """
        Racunanje rezultata za plin.
        input - string plina (stupac u frejmu dokument.siroviPodaci)
        output - mapa {'rezultat':frejm rezultata,
                       'slopeData':podaci za slope i offset,
                       'kriterij':kriterij prilagodbe}
        """
        stariPlin = self.dokument.get_izabranoMjerenje()
        self.dokument.block_all_signals()
        # direktno manipuliranje dokumentom
        self.dokument.izabranoMjerenje = plin
        #racunanje potrebnih vrijednosti
        self.kalkulator.racunaj()
        rez = self.kalkulator.rezultat
        slopedata = self.kalkulator.get_slope_and_offset_list()
        kriterij = self.kalkulator.get_provjeru_parametara()
        mapa = {'rezultat':rez,
                'slopeData':slopedata,
                'kriterij':kriterij}
        #vrati dokument u po etno stanje
        self.dokument.izabranoMjerenje = stariPlin
        self.dokument.unblock_all_signals()
        return mapa


    def recalculate(self):
        """
        racunanje umjeravanja za sve stupce u sirovim podacima
        """
        print('recalculating')
        #potrebne postavke
        plin = self.dokument.get_izabranoMjerenje()
        frejm = self.dokument.get_siroviPodaci()
        stupci = sorted(list(frejm.columns))
        #inicijalizacija i postavljanje panela
        for gas in stupci:
            izabraniPanel = self.dictTabRezultata[gas]
            mapa = self.izracunaj_rezultat_umjeravanja_za_plin(gas)
            #update rezultata za layout
            izabraniPanel.update_rezultat(mapa)
        #restore dokument i kalkulator u pocetno stanje
        self.dokument.izabranoMjerenje = plin
        if self.test_for_nox():
            self.recalculate_konverter()

    def recalculate_konverter(self):
        """metoda racuna provjeru konvertera, i postavlja rezultate u gui"""
        self.konverterKalkulator.racunaj()
        rezultatKonverter = self.konverterKalkulator.rezultat
        listaEfikasnosti = self.konverterKalkulator.get_listu_efikasnosti()
        mapa = {'rezultat':rezultatKonverter,
                'efikasnost':listaEfikasnosti}
        self.tabKonverter.update_rezultat(mapa)


    def is_konverter_tab_active(self):
        """
        metoda vraca True ako je aktivan konverter tab, false inace
        """
        return self.glavniTabWidget.currentWidget() == self.tabKonverter

    def promjena_aktivnog_taba(self, x):
        """slot koji se kativira prilikom promjene aktivnog taba. Prebacuje tablicu
        sa sirovim podacima izmedju 'normalnog' i 'konverter' prikaza."""
        if self.is_konverter_tab_active():
            start = self.dokument.get_konverterPodaciStart()
            tocke = self.dokument.get_tockeKonverter()
        else:
            start = self.dokument.get_siroviPodaciStart()
            tocke = self.dokument.get_tockeUmjeravanja()
        self.update_tablice_sirovih_podataka([tocke, start, False])

    def odaberi_pocetak_podataka(self, x):
        """
        Metoda sluzi za odabir pocetnog indeksa (ljevi klik na tablicu sa sirovim
        podacima). Vrijednost se postavlja u dokument
        """
        self.siroviPodaciView.clearSelection()
        if self.is_konverter_tab_active():
            self.dokument.set_konverterPodaciStart(x)
        else:
            self.dokument.set_siroviPodaciStart(x)

    def update_tablice_sirovih_podataka(self, x):
        """
        update izgleda tablice sa novim podacima preuzetim iz dokumenta.
        x je lista [self.tockeUmjeravanja, self.siroviPodaciStart, recalculate]
        """
        tocke = x[0]
        start = x[1]
        recalculate = x[2]
        self.siroviPodaciModel.set_tocke(tocke)
        self.siroviPodaciModel.set_start(start)
        self.siroviPodaciView.update()
        if recalculate:
            if self.is_konverter_tab_active():
                self.recalculate_konverter()
            else:
                self.recalculate()

    def save_umjeravanje_to_file(self):
        """
        spremanje dokumenta u file
        """
        filepath = QtGui.QFileDialog.getSaveFileName(parent=self,
                                                     caption='Spremi file',
                                                     filter='Umjeravanje save files (*.usf);;all (*.*)')
        if filepath:
            self.dokument.save_dokument(filepath)

    def load_umjeravanje_from_file(self):
        """ucitavanje dokumenta iz spremljenog filea"""
        filepath = QtGui.QFileDialog.getOpenFileName(parent=self,
                                                     caption='Ucitaj file',
                                                     filter='Umjeravanje save files (*.usf);;all (*.*)')
        if filepath:
            self.clear_tabove_rezultata() #potrebno je makuti tabove...
            self.dokument.load_dokument(filename=filepath)

    def set_labelUredjaj(self, tekst):
        """Setter serijskog broja uredjaja (tekst) u label"""
        self.labelUredjaj.setText(tekst)

    def set_labelPostaja(self, tekst):
        """Setter naziva postaje na kojoj je smjesten uredjaj u label"""
        self.labelPostaja.setText(tekst)

    def set_labelDatoteka(self, tekst):
        """Setter punog patha i naziva fajla sa sirovim csv podacima"""
        self.labelDatoteka.setText(tekst)

    def napravi_pdf_report(self):
        """metoda je zaduzena za generiranje pdf reporta umjeravanja.
        - podaci se preuzimaju u obliku dicta od dokumenta (mapa)
        - ime filea se dobiva uz pomoc dijaloga
        """
        ime = QtGui.QFileDialog.getSaveFileName(parent=self,
                                                caption='Spremi pdf report',
                                                filter = 'pdf file (*.pdf)')
        if ime:
            mapa = self.dokument.dokument_to_dict()
            mapa = copy.deepcopy(mapa)
            #rezultati svih komponenti
            rezultati = self.pripremi_rezultate_za_report()
            report = pdfreport.ReportGenerator()
            try:
                report.generiraj_report(ime, mapa, rezultati)
            except Exception as err:
                logging.error(str(err), exc_info=True)
                msg = "\n".join(['Izvještaj nije uspješno generiran.', str(err)])
                QtGui.QMessageBox.information(self, 'Problem', msg)

    def pripremi_rezultate_za_report(self):
        """
        Pripremanje rezultata za generiranje reporta (fezultati, prilagodbe...)
        Izlaz je mapa
        """
        frejm = self.dokument.get_siroviPodaci()
        stupci = sorted(list(frejm.columns))
        output = {}
        for plin in stupci:
            mapa = self.izracunaj_rezultat_umjeravanja_za_plin(plin)
            if plin == 'NO' and self.dokument.provjeraKonvertera:
                ecKonverter = self.konverterKalkulator.get_ec_parametar()
                if ecKonverter != None:
                    if not np.isnan(ecKonverter[3]):
                        mapa['kriterij'].append(ecKonverter)
            output[plin] = copy.deepcopy(mapa)
        return output

    def aktiviraj_ucitane_podatke(self, mapa):
        """
        Metoda preuzima mapu sa ucitanim podacima i postavlja je u dokument.
        dict mapa sadrzi :
        {'podaci':frejm sa podacima,
         'uredjaj':string, naziv uredjaja}
        """
        frejm = mapa['podaci']
        lokacija = 'učitani podaci'
        uredjaj = mapa['uredjaj']
        path = 'učitani podaci'
        # postavi info o ucitanom fileu
        self.dokument.set_izabraniUredjaj(uredjaj)
        self.dokument.set_izabranaPostaja(lokacija)
        self.dokument.set_izabraniPathCSV(path)
        self.clear_tabove_rezultata()
        self.dokument.set_siroviPodaci(frejm)
        #reset start umjeravanja na 0 ... reinit tocke i start
        self.dokument.reinitialize_tocke_i_start(recalculate=False)
        #update combobox za izbor mjerenja
        komponente = set(self.dokument.uredjaji[uredjaj]['komponente'])
        komponente.remove('None')
        komponente = list(komponente)
        self.dokument.set_listaMjerenja(komponente)
        self.recalculate()

    def toggle_tab_konverter(self, x):
        """prikaz taba za provjeru konvertera ovisno o booleanu x"""
        if x:
            self.glavniTabWidget.addTab(self.tabKonverter, 'Provjera konvertera')
        else:
            indeks = self.glavniTabWidget.indexOf(self.tabKonverter) # -1 if not found
            if indeks != -1:
                self.glavniTabWidget.removeTab(indeks)
