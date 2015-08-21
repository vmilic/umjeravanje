# -*- coding: utf-8 -*-
"""
Created on Mon May 18 12:02:42 2015

@author: DHMZ-Milic
"""
import logging
import pickle
import copy
import pandas as pd
from PyQt4 import QtGui, QtCore, uic
import app.model.konfig_klase as konfig
import app.model.pomocne_funkcije as helperi
import app.model.frejm_model as modeli
import app.model.kalkulator as calc
import app.view.read_file_wizard as datareader
import app.view.canvas as canvas
import app.view.dijalog_edit_tocke as dotedit

#TODO! refresh rest data? podatke o uredjajima...gumb? akcija?
#TODO! pisanje u template


class TableViewRezultata(QtGui.QTableView):
    """
    view za rezultate...podrska za kontekstni menu
    """
    def __init__(self, parent=None):
        QtGui.QTableView.__init__(self, parent=parent)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                             QtGui.QSizePolicy.Preferred))
        self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

    def contextMenuEvent(self, event):
        """
        event koji definira kontekstni menu..
        """
        self.selected = self.selectionModel().selection().indexes()
        #define context menu items
        menu = QtGui.QMenu()
        dodaj = QtGui.QAction('Dodaj tocku', self)
        makni = QtGui.QAction('Makni tocku', self)
        postavke = QtGui.QAction('Postavke tocke', self)
        menu.addAction(dodaj)
        menu.addAction(makni)
        menu.addSeparator()
        menu.addAction(postavke)
        #connect context menu items
        dodaj.triggered.connect(self.emit_add)
        makni.triggered.connect(self.emit_remove)
        postavke.triggered.connect(self.emit_edit)
        #display context menu
        menu.exec_(self.mapToGlobal(event.pos()))

    def emit_add(self, x):
        """
        Metoda emitira zahtjev za dodavanjem nove tocke
        """
        #za sada nemam pametniju ideju
        if len(self.model().dataFrejm):
            self.emit(QtCore.SIGNAL('dodaj_tocku'))

    def emit_remove(self, x):
        """
        Metoda emitira zahtjev za brisanjem tocke
        """
        selektirani = self.selectedIndexes()
        if selektirani:
            indeks = selektirani[0].row()
            self.emit(QtCore.SIGNAL('makni_tocku(PyQt_PyObject)'), indeks)

    def emit_edit(self, x):
        """
        Metoda salje zahtjev za promjenom parametara selektirane tocke
        """
        selektirani = self.selectedIndexes()
        if selektirani:
            indeks = selektirani[0].row()
            self.emit(QtCore.SIGNAL('edit_tocku(PyQt_PyObject)'), indeks)


BASE, FORM = uic.loadUiType('./app/view/uiFiles/display.ui')
class GlavniProzor(BASE, FORM):
    """
    Gui element glavnog prozora
    """
    def __init__(self, cfg=None, parent=None):
        super(BASE, self).__init__(parent)
        self.setupUi(self)
        self.uredjaji = {}
        self.postaje = {}
        #citanje podataka iz konfiga
        try:
            self.konfiguracija = konfig.MainKonfig(cfg=cfg)
            self.postaje, self.uredjaji = helperi.pripremi_mape_postaja_i_uredjaja(
                self.konfiguracija.uredjajUrl,
                self.konfiguracija.postajeUrl)
        except (TypeError, AttributeError):
            msg = 'Konfig aplikacije ne moze naci trazeni element.'
            logging.error(msg, exc_info=True)
            raise SystemExit('Konfiguracijski file nije ispravan.')
        ### popunjavanje comboboxeva ###
        self.comboDilucija.addItems(self.konfiguracija.get_listu_dilucija())
        self.comboZrak.addItems(self.konfiguracija.get_listu_cistiZrak())
        ### stanje checkboxeva ###
        self.checkLinearnost.setChecked(self.konfiguracija.provjeraLinearnosti)
        #definiranje kalkulatora
        self.kalkulator = calc.RacunUmjeravanja(cfg=self.konfiguracija)

        # view-ovi
        ### tablica sa ucitanim podacima ###
        self.siroviPodaciView.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        ### tablica rezultata ###
        self.rezultatView = TableViewRezultata()
        self.rezultatView.setMinimumSize(300,250)
        self.rezultatViewLayout.addWidget(self.rezultatView)
        self.rezultatView.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        ### tablica za prikaz slope i offset###
        self.slopeOffsetView = QtGui.QTableView()
        self.slopeOffsetView.setMinimumSize(200, 90)
        self.slopeOffsetView.setMaximumSize(350, 90)
        self.rezultatViewLayout.addWidget(self.slopeOffsetView)
        self.slopeOffsetView.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        ### tablica sa testom analitickih metoda ###
        self.rezultatParametriView = QtGui.QTableView()
        self.rezultatParametriView.setMinimumSize(350,150)
        self.rezultatViewLayout.addWidget(self.rezultatParametriView)
        self.rezultatParametriView.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

        # modeli
        ### model za ucitane podatke ###
        self.siroviPodaci = pd.DataFrame()
        self.siroviPodaciModel = modeli.SiroviFrameModel()
        self.siroviPodaciView.setModel(self.siroviPodaciModel)
        self.siroviPodaciView.update()
        ### model za rezultate ###
        self.rezultatUmjeravanja = pd.DataFrame(columns=['cref', 'c', 'sr', 'r', 'UR'])
        self.rezultatModel = modeli.RezultatModel(tocke=self.konfiguracija.umjerneTocke)
        self.rezultatModel.set_frejm(self.rezultatUmjeravanja)
        self.rezultatView.setModel(self.rezultatModel)
        self.rezultatView.update()
        ### model za test analitickih metoda ###
        initialDefault = self.kalkulator.get_provjeru_parametara()
        self.rezultatParametriModel = modeli.RezultatParametriModel(lista=initialDefault)
        self.rezultatParametriView.setModel(self.rezultatParametriModel)
        self.rezultatParametriView.update()
        ### model za prikaz slope/offset, te parametre funkcije prilagodbe (A, B) ###
        initialDefault = self.kalkulator.get_slope_and_offset_list()
        self.slopeOffsetModel = modeli.SlopeOffsetABModel(lista=initialDefault)
        self.slopeOffsetView.setModel(self.slopeOffsetModel)
        self.slopeOffsetView.update()

        #definiranje modela podataka za provjeru konvertera
        self.konverterPodaci = pd.DataFrame()
        self.konverterPodaciModel = modeli.SiroviFrameModel(tocke=self.konfiguracija.konverterTocke)
        self.konverterPodaciView.setModel(self.konverterPodaciModel)
        self.konverterPodaciView.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.konverterPodaciView.update()

        #setup postavki za racunanje konvertera
        self.konverterOpseg.setValue(400.0)
        try:
            c50 = float(self.konfiguracija.get_konfig_element('KONVERTER_META','cNOX50'))
            c95 = float(self.konfiguracija.get_konfig_element('KONVERTER_META','cNOX95'))
            self.cnox50SpinBox.setValue(c50)
            self.cnox95SpinBox.setValue(c95)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            self.cnox50SpinBox.setValue(200.0)
            self.cnox95SpinBox.setValue(180.0)

        #kalkulator za provjeru konvertera
        self.konverterKalkulator = calc.ProvjeraKonvertera(cfg=self.konfiguracija)

        # rezultat provjere konvertera
        self.konverterRezultat = pd.DataFrame(columns=['c, R, NOx', 'c, R, NO2', 'c, NO', 'c, NOx'])
        self.konverterRezultatModel = modeli.RezultatModel(tocke=self.konfiguracija.konverterTocke)
        self.konverterRezultatModel.set_frejm(self.konverterRezultat)
        self.konverterRezultatView.setModel(self.konverterRezultatModel)
        self.konverterRezultatView.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.konverterRezultatView.update()

        ###model za prikaz tablice efikasnosti konvertera###
        initialDefault = self.konverterKalkulator.get_listu_efikasnosti()
        self.konverterEfikasnostModel = modeli.EfikasnostKonverteraModel(lista=initialDefault)
        self.konverterEfikasnostView.setModel(self.konverterEfikasnostModel)
        self.konverterEfikasnostView.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.konverterEfikasnostView.update()

        self.inicijalizacija_grafova()
        self.setup_signal_connections()

    def inicijalizacija_grafova(self):
        """inicijalizacija i postavljanje kanvasa za grafove u layout."""
        meta1 = {'xlabel':'referentna koncentracija, cref',
                 'ylabel':'koncentracija, c',
                 'title':'Cref / koncentracija graf'}
        meta2 = {'xlabel':'vrijeme',
                 'ylabel':'koncentracija, c',
                 'title':'Individualna mjerenja'}
        self.crefCanvas = canvas.Kanvas(meta=meta1)
        self.mjerenjaCanvas = canvas.KanvasMjerenja(meta=meta2)
        self.grafoviLayout.addWidget(self.crefCanvas)
        self.grafoviLayout.addWidget(self.mjerenjaCanvas)

    def setup_signal_connections(self):
        """
        connect actione i widgete za callbackovima
        """
        self.action_Exit.triggered.connect(self.close)
        self.action_ucitaj_podatke.triggered.connect(self.read_data)
        self.action_spremi.triggered.connect(self.save_umjeravanje_to_file)
        self.action_ucitaj.triggered.connect(self.load_umjeravanje_from_file)

        self.siroviPodaciView.clicked.connect(self.odaberi_start_umjeravanja)

        self.comboMjerenje.currentIndexChanged.connect(self.promjena_mjerenja)
        self.comboDilucija.currentIndexChanged.connect(self.recalculate)
        self.comboZrak.currentIndexChanged.connect(self.recalculate)
        self.checkLinearnost.toggled.connect(self.recalculate)
        self.doubleSpinBoxOpseg.valueChanged.connect(self.recalculate)
        self.doubleSpinBoxKoncentracijaCRM.valueChanged.connect(self.recalculate)
        self.doubleSpinBoxSljedivostCRM.valueChanged.connect(self.recalculate)

        self.konverterPodaciView.clicked.connect(self.odaberi_start_provjere_konvertera)

        self.konverterOpseg.valueChanged.connect(self.recalculate_konverter)
        self.cnox50SpinBox.valueChanged.connect(self.recalculate_konverter)
        self.cnox95SpinBox.valueChanged.connect(self.recalculate_konverter)

        self.connect(self.rezultatView,
                     QtCore.SIGNAL('dodaj_tocku'),
                     self.konfiguracija.dodaj_tocku)

        self.connect(self.konfiguracija,
                     QtCore.SIGNAL('promjena_umjernih_tocaka'),
                     self.recalculate)

        self.connect(self.rezultatView,
                     QtCore.SIGNAL('makni_tocku(PyQt_PyObject)'),
                     self.konfiguracija.makni_tocku)

        self.connect(self.konfiguracija,
                     QtCore.SIGNAL('promjena_umjernih_tocaka'),
                     self.recalculate)

        self.connect(self.rezultatView,
                     QtCore.SIGNAL('edit_tocku(PyQt_PyObject)'),
                     self.edit_tocku_dijalog)

    def update_mjerne_jedinice(self, uredjaj, komponenta):
        """
        update mjerne jedinice za zadani uredjaj i komponentu.

        mj-komponenta --> uredjaj[SERIAL]['komponenta'][FORMULA]['mjernaJedinica']
        mj-analiticka metoda --> uredjaj[SERIAL]['analitickaMetoda'][NAZIV]['mjernaJedinica']
        """
        try:
            mj = self.uredjaji[uredjaj]['komponenta'][komponenta]['mjernaJedinica']
        except LookupError:
            print('fail lookup mjerne jedinice komponente, ure={0}, komp={1}'.format(uredjaj, komponenta))
            mj = '[n/a]'
        try:
            mjOpseg = self.uredjaji[uredjaj]['analitickaMetoda']['o']['mjernaJedinica']
        except LookupError:
            print('fail lookup mjerne jedinice opsega analitickeMetode, ure={0}, komp={1}'.format(uredjaj, komponenta))
            mjOpseg = mj
        self.labelJedinicaOpseg.setText(mjOpseg)
        self.labelJedinicaCCRM.setText(mjOpseg)
        self.rezultatModel.set_mjerna_jedinica(mjOpseg)
        self.rezultatParametriModel.set_mjerna_jedinica(mjOpseg)
        self.slopeOffsetModel.set_mjerna_jedinica(mjOpseg)
        self.konverterRezultatModel.set_mjerna_jedinica(mjOpseg)

    def promjena_mjerenja(self, x):
        """
        Promjena mjerenja (stupca za racunanje). Prema potrebi se mjenja:
        - mjerna jedinica
        - opseg mjerenja
        """
        try:
            self.doubleSpinBoxOpseg.blockSignals(True)
            uredjaj = self.labelUredjaj.text()
            opseg = float(self.uredjaji[uredjaj]['analitickaMetoda']['o']['max'])
            self.doubleSpinBoxOpseg.setValue(opseg)
        except LookupError:
            pass
        finally:
            self.doubleSpinBoxOpseg.blockSignals(False)
        self.recalculate()

    def edit_tocku_dijalog(self, indeks):
        """
        Poziv dijaloga za edit vrijednosti parametara izabrane tocke.
        ulazni parametar indeks je indeks pod kojim se ta tocka nalazi
        u listi self.konfiguracija.umjerneTocke
        """
        tocke = copy.deepcopy(self.konfiguracija.umjerneTocke)
        self.dijalog = dotedit.EditTockuDijalog(indeks=indeks,
                                                tocke=tocke,
                                                frejm=self.siroviPodaci,
                                                start=self.siroviPodaciModel.startIndeks,
                                                parent=self)
        if self.dijalog.exec_():
            tocke = self.dijalog.get_tocke()
            self.konfiguracija.umjerneTocke = tocke
            self.recalculate()

    def read_data(self):
        """
        ucitavanje sirovih podataka preko wizarda
        """
        self.fileWizard = datareader.CarobnjakZaCitanjeFilea(uredjaji=self.uredjaji,
                                                             postaje=self.postaje)
        prihvacen = self.fileWizard.exec_()
        if prihvacen:
            frejm = self.fileWizard.get_frejm()
            lokacija = self.fileWizard.get_postaja()
            uredjaj = self.fileWizard.get_uredjaj()
            path = str(self.fileWizard.get_path_do_filea())
            # postavi info o ucitanom fileu
            self.labelDatoteka.setText(path)
            self.labelPostaja.setText(lokacija)
            self.labelUredjaj.setText(uredjaj)
            self.postavi_sirove_podatke(frejm)
            self.comboMjerenje.blockSignals(True)
            self.comboMjerenje.clear()
            komponente = set(self.uredjaji[uredjaj]['komponente'])
            komponente.remove('None')
            self.comboMjerenje.addItems(list(komponente))
            if 'NOx' in komponente:
                ind = self.comboMjerenje.findText('NOx')
                self.comboMjerenje.setCurrentIndex(ind)
            self.comboMjerenje.blockSignals(False)
            try:
                #ako uredjaj ima podatak o opsegu postavi opseg
                opseg = float(self.uredjaji[uredjaj]['analitickaMetoda']['o']['max'])
                self.doubleSpinBoxOpseg.blockSignals(True)
                self.doubleSpinBoxOpseg.setValue(opseg)
            except LookupError:
                #zanemari gresku (nepostojeci kljuc)
                pass
            finally:
                self.doubleSpinBoxOpseg.blockSignals(False)
            self.recalculate()

    def postavi_sirove_podatke(self, frejm):
        """
        Metoda postavlja pandas datafrejm (ulazni parametar) u member,
        predaje ga modelu i updatea view sa ucitanim podacima.
        """
        self.siroviPodaci = frejm
        self.siroviPodaciModel.set_frejm(self.siroviPodaci)
        self.siroviPodaciModel.set_tocke(self.konfiguracija.umjerneTocke)
        self.siroviPodaciView.update()
        #postavljanje podataka za provjeru konvertera samo ako je NOX
        testSet = set(['NOx', 'NO', 'NO2'])
        dataSet = set(self.siroviPodaci.columns)
        if testSet.issubset(dataSet):
            self.konverterPodaci = self.siroviPodaci.copy()
            self.konverterPodaciModel.set_frejm(self.konverterPodaci)
            self.konverterPodaciModel.set_tocke(self.konfiguracija.konverterTocke)
            self.konverterPodaciView.setModel(self.konverterPodaciModel)
            self.konverterPodaciView.update()
        else:
            self.konverterPodaci = pd.DataFrame()
            self.konverterPodaciModel.set_frejm(self.konverterPodaci)
            self.konverterPodaciModel.set_tocke(self.konfiguracija.konverterTocke)
            self.konverterPodaciView.setModel(self.konverterPodaciModel)
            self.konverterPodaciView.update()

    def odaberi_start_umjeravanja(self, x):
        """
        Metoda sluzi za odabir pocetnog indeksa (ljevi klik na tablicu sa sirovim
        podacima)
        """
        self.siroviPodaciView.clearSelection()
        self.siroviPodaciModel.set_start(x)
        self.recalculate()

    def odaberi_start_provjere_konvertera(self, x):
        """
        Metoda sluzi za odabir pocetnog indeksa provjere konvertera.
        """
        self.konverterPodaciView.clearSelection()
        self.konverterPodaciModel.set_start(x)
        self.recalculate_konverter()

    def refresh_views(self):
        """
        force refresh modela i view-ova nakon promjene podataka
        """
        # umjeravanje
        self.rezultatUmjeravanja = self.kalkulator.rezultat
        self.rezultatModel.set_frejm(self.rezultatUmjeravanja)
        self.siroviPodaciModel.set_tocke(self.konfiguracija.umjerneTocke)
        self.rezultatModel.set_tocke(self.konfiguracija.umjerneTocke)
        self.rezultatParametriModel.set_lista(self.kalkulator.get_provjeru_parametara())
        self.slopeOffsetModel.set_lista(self.kalkulator.get_slope_and_offset_list())
        #mjerne jedinice
        komponenta = self.comboMjerenje.currentText()
        uredjaj = self.labelUredjaj.text()
        self.update_mjerne_jedinice(uredjaj, komponenta)
        #update view-s
        self.siroviPodaciView.update()
        self.rezultatView.update()
        self.rezultatParametriView.update()
        self.slopeOffsetView.update()
        # clear and redraw grafove
        self.crefCanvas.clear_graf()
        self.mjerenjaCanvas.clear_graf()
        self.prikazi_grafove()

    def setup_kalkulator(self):
        """
        Funkcija postavlja priprema kalkulator za racunanje. Predaje mu konfig,
        podatke i stupac s kojim se racuna.
        """
        try:
            self.kalkulator.set_uredjaj(self.uredjaji[str(self.labelUredjaj.text())])
        except LookupError:
            QtGui.QMessageBox.warning(self, 'Problem', 'Nedostaju podaci za izabrani uredjaj.')
            logging.debug('Uredjaj nije definiran (n/a)', exc_info=True)
        self.kalkulator.set_linearnost(self.checkLinearnost.isChecked())
        self.kalkulator.set_data(self.siroviPodaci)
        self.kalkulator.set_stupac(self.comboMjerenje.currentText())
        self.kalkulator.set_dilucija(self.comboDilucija.currentText())
        self.kalkulator.set_cistiZrak(self.comboZrak.currentText())
        self.kalkulator.set_opseg(float(self.doubleSpinBoxOpseg.value()))
        self.kalkulator.set_cCRM(float(self.doubleSpinBoxKoncentracijaCRM.value()))
        self.kalkulator.set_sCRM(float(self.doubleSpinBoxSljedivostCRM.value()))

    def setup_konverter_kalkulator(self):
        """
        Funkcija priprema kalkulator za racunjanje provjere konvertera.
        """
        self.konverterKalkulator.set_data(self.konverterPodaci)
        self.konverterKalkulator.set_opseg(self.konverterOpseg.value())
        self.konverterKalkulator.set_cnox50(self.cnox50SpinBox.value())
        self.konverterKalkulator.set_cnox95(self.cnox95SpinBox.value())

    def recalculate(self):
        """
        Pocetna metoda za racunanje i prikaz rezultata umjeravanja.
        """
        self.setup_kalkulator()
        self.kalkulator.racunaj()
        self.refresh_views()

    def recalculate_konverter(self):
        """
        Poceta metoda za racunanje i prikaz rezultata provjere konvertera
        """
        self.setup_konverter_kalkulator()
        self.konverterKalkulator.racunaj()
        self.refresh_konverter_views()

    def refresh_konverter_views(self):
        """
        update rezultata provjere konvertera
        """
        self.konverterRezultat = self.konverterKalkulator.rezultat
        self.konverterRezultatModel.set_frejm(self.konverterRezultat)
        efikasnost = self.konverterKalkulator.get_listu_efikasnosti()
        self.konverterEfikasnostModel.set_lista(efikasnost)
        self.konverterRezultatView.update()
        self.konverterPodaciView.update()
        self.konverterEfikasnostView.update()

    def prikazi_grafove(self):
        """
        Metoda za crtanje grafova
        """
        if len(self.rezultatUmjeravanja) > 0:
            x = list(self.rezultatUmjeravanja.loc[:, 'cref'])
            y = list(self.rezultatUmjeravanja.loc[:, 'c'])
            if self.checkLinearnost.isChecked():
                self.crefCanvas.set_slope_offset(self.kalkulator.slope, self.kalkulator.offset)
            else:
                self.crefCanvas.set_slope_offset(None, None)
            self.crefCanvas.crtaj(x, y)
            """
            1. sklepaj strukturu (tocke, frejm)
            2. metoda crtaj mora sklepati intervale tocaka x, y
            3. metoda crtaj mora prilagoditi boju tocke na grafu
            """
            stupac = str(self.comboMjerenje.currentText())
            if stupac in self.siroviPodaci.columns:
                frejm = self.siroviPodaci.loc[:,stupac]
                if self.checkLinearnost.isChecked():
                    self.mjerenjaCanvas.crtaj(frejm, self.konfiguracija.umjerneTocke)
                else:
                    zs = self.get_zero_span_tocke()
                    self.mjerenjaCanvas.crtaj(frejm, zs)

    def get_zero_span_tocke(self):
        """
        Metoda pronalazi indekse za zero i span.

        Zero je prva tocka koja ima crefFaktor jednak 0.0
        Span je prva tocka sa crefFaktorom 0.8, a ako niti jedna tocka nema
        taj crefFaktor, onda se uzima ona sa najvecim crefFaktorom
        """
        if len(self.konfiguracija.umjerneTocke) >= 2:
            cf = [float(tocka.crefFaktor) for tocka in self.konfiguracija.umjerneTocke]
            zero = cf.index(0.0)
            if 0.8 in cf:
                span = cf.index(0.8)
            else:
                span = cf.index(max(cf))
            out = [self.konfiguracija.umjerneTocke[zero],
                   self.konfiguracija.umjerneTocke[span]]
            return out
        else:
            return []

    def blokiraj_signale(self):
        """
        blokiranje signala radi izbjegavanja nepotrebnog racunanja
        """
        self.comboMjerenje.blockSignals(True)
        self.comboDilucija.blockSignals(True)
        self.comboZrak.blockSignals(True)
        self.checkLinearnost.blockSignals(True)
        self.doubleSpinBoxOpseg.blockSignals(True)
        self.doubleSpinBoxKoncentracijaCRM.blockSignals(True)
        self.doubleSpinBoxSljedivostCRM.blockSignals(True)

    def odblokiraj_signale(self):
        """
        odblokiranje signala radi omogucavanja racunanja
        """
        self.comboMjerenje.blockSignals(False)
        self.comboDilucija.blockSignals(False)
        self.comboZrak.blockSignals(False)
        self.checkLinearnost.blockSignals(False)
        self.doubleSpinBoxOpseg.blockSignals(False)
        self.doubleSpinBoxKoncentracijaCRM.blockSignals(False)
        self.doubleSpinBoxSljedivostCRM.blockSignals(False)

    def save_umjeravanje_to_file(self):
        """
        serijalizacija objekata uz pomoc modula pickle u file.
        """
        outputMapa = {}
        #tocke
        tocke = copy.deepcopy(self.konfiguracija.umjerneTocke)
        outputMapa['umjerneTocke'] = []
        for tocka in tocke:
            obj = {}
            obj['ime'] = tocka.ime
            obj['indeksi'] = tocka.indeksi
            obj['crefFaktor'] = tocka.crefFaktor
            obj['rgba'] = (tocka.boja.red(), tocka.boja.green(), tocka.boja.blue(), tocka.boja.alpha())
            outputMapa['umjerneTocke'].append(obj)
        #konverter tocke
        konverterTocke = copy.deepcopy(self.konfiguracija.konverterTocke)
        outputMapa['konverterTocke'] = []
        for tocka in konverterTocke:
            obj = {}
            obj['ime'] = tocka.ime
            obj['indeksi'] = tocka.indeksi
            obj['crefFaktor'] = tocka.crefFaktor
            obj['rgba'] = (tocka.boja.red(), tocka.boja.green(), tocka.boja.blue(), tocka.boja.alpha())
            outputMapa['konverterTocke'].append(obj)
        # ucitani podaci...frejm
        outputMapa['frejmPodataka'] = self.siroviPodaci
        # start indeks u modelu
        outputMapa['pocetniIndeks'] = self.siroviPodaciModel.startIndeks
        #start indeks za konverter
        outputMapa['konverterPocetniIndeks'] = self.konverterPodaciModel.startIndeks
        # REST postaje
        outputMapa['postajeREST'] = self.postaje
        # REST uredjaji
        outputMapa['uredjajiREST'] = self.uredjaji
        #file path
        outputMapa['izabraniFile'] = str(self.labelDatoteka.text())
        #izabrana postaja
        outputMapa['izabranaPostaja'] = str(self.labelPostaja.text())
        #izabrani uredjaj
        outputMapa['izabraniUredjaj'] = str(self.labelUredjaj.text())
        # provjera linearnosti
        outputMapa['provjeraLinearnosti'] = self.checkLinearnost.isChecked()
        # combo mjerenje
        mjerenja = list(set(self.uredjaji[str(self.labelUredjaj.text())]['komponente']))
        mjerenja = [str(mjerenje) for mjerenje in mjerenja if str(mjerenje) != 'None']
        outputMapa['listaMjerenje'] = mjerenja
        # combo dilucija
        outputMapa['listaDilucija'] = self.konfiguracija.get_listu_dilucija()
        # combo cisti zrak
        outputMapa['listaZrak'] = self.konfiguracija.get_listu_cistiZrak()
        #izbor combo mjerenje
        outputMapa['izborMjerenje'] = self.comboMjerenje.currentText()
        #izbor combo dilucija
        outputMapa['izborDilucija'] = self.comboDilucija.currentText()
        #izbor combo cisti zrak
        outputMapa['izborZrak'] = self.comboZrak.currentText()
        # opseg
        outputMapa['opseg'] = self.doubleSpinBoxOpseg.value()
        # koncentracija CRM
        outputMapa['cCRM'] = self.doubleSpinBoxKoncentracijaCRM.value()
        #sljedivost CRM
        outputMapa['sCRM'] = self.doubleSpinBoxSljedivostCRM.value()
        #spremanje mape uz pomoc pickle
        filepath = QtGui.QFileDialog.getSaveFileName(parent=self,
                                                     caption='Spremi file',
                                                     filter='Umjeravanje save files (*.usf);;all (*.*)')
        if filepath:
            with open(filepath, mode='wb') as fajl:
                try:
                    pickle.dump(outputMapa, fajl)
                except Exception as err:
                    QtGui.QMessageBox.information(self, 'Problem', 'Spremanje datoteke nije uspjelo.')
                    logging.error(str(err), exc_info=True)

    def load_umjeravanje_from_file(self):
        """
        ucitavanje umjeravanja iz filea
        """
        filepath = QtGui.QFileDialog.getOpenFileName(parent=self,
                                                     caption='Ucitaj file',
                                                     filter='Umjeravanje save files (*.usf);;all (*.*)')
        if filepath:
            with open(filepath, mode='rb') as fajl:
                try:
                    #block signlale
                    self.blokiraj_signale()
                    outputMapa = pickle.load(fajl)
                    # REST postaje
                    self.postaje = outputMapa['postajeREST']
                    # REST uredjaji
                    self.uredjaji = outputMapa['uredjajiREST']
                    #file path
                    self.labelDatoteka.setText(outputMapa['izabraniFile'])
                    #izabrana postaja
                    self.labelPostaja.setText(outputMapa['izabranaPostaja'])
                    #izabrani uredjaj
                    self.labelUredjaj.setText(outputMapa['izabraniUredjaj'])
                    # combo mjerenje
                    self.comboMjerenje.clear()
                    self.comboMjerenje.addItems(outputMapa['listaMjerenje'])
                    # combo dilucija
                    self.comboDilucija.clear()
                    self.comboDilucija.addItems(outputMapa['listaDilucija'])
                    # combo cisti zrak
                    self.comboZrak.clear()
                    self.comboZrak.addItems(outputMapa['listaZrak'])
                    #tocke
                    tocke = outputMapa['umjerneTocke']
                    outTocke = []
                    for tocka in tocke:
                        dot = konfig.Tocka()
                        dot.ime = tocka['ime']
                        dot.indeksi = tocka['indeksi']
                        dot.crefFaktor = tocka['crefFaktor']
                        r, g, b, a = tocka['rgba']
                        dot.boja = QtGui.QColor(r, g, b, a)
                        outTocke.append(dot)
                    self.konfiguracija.umjerneTocke = outTocke
                    #konverter tocke
                    konverterTocke = outputMapa['konverterTocke']
                    outTocke = []
                    for tocka in konverterTocke:
                        dot = konfig.Tocka()
                        dot.ime = tocka['ime']
                        dot.indeksi = tocka['indeksi']
                        dot.crefFaktor = tocka['crefFaktor']
                        r, g, b, a = tocka['rgba']
                        dot.boja = QtGui.QColor(r, g, b, a)
                        outTocke.append(dot)
                    self.konfiguracija.konverterTocke = outTocke
                    # ucitani podaci (frejm) za umjeravanje i konverter
                    self.postavi_sirove_podatke(outputMapa['frejmPodataka'])
                    # start indeks u modelu
                    self.siroviPodaciModel.set_start(outputMapa['pocetniIndeks'])
                    #start indeks konverter modela
                    self.konverterPodaciModel.set_start(outputMapa['konverterPocetniIndeks'])
                    # provjera linearnosti
                    self.checkLinearnost.setChecked(outputMapa['provjeraLinearnosti'])
                    # opseg
                    self.doubleSpinBoxOpseg.setValue(outputMapa['opseg'])
                    # koncentracija CRM
                    self.doubleSpinBoxKoncentracijaCRM.setValue(outputMapa['cCRM'])
                    #sljedivost CRM
                    self.doubleSpinBoxSljedivostCRM.setValue(outputMapa['sCRM'])
                    #izbor combo mjerenje
                    ind = self.comboMjerenje.findText(outputMapa['izborMjerenje'])
                    self.comboMjerenje.setCurrentIndex(ind)
                    #izbor combo dilucija
                    ind = self.comboDilucija.findText(outputMapa['izborDilucija'])
                    self.comboDilucija.setCurrentIndex(ind)
                    #izbor combo cisti zrak
                    ind = self.comboZrak.findText(outputMapa['izborZrak'])
                    self.comboZrak.setCurrentIndex(ind)
                    #unblock signale i recalculate
                    self.odblokiraj_signale()
                    self.update_mjerne_jedinice(outputMapa['izabraniUredjaj'],
                                                outputMapa['izborMjerenje'])
                    self.recalculate()
                    self.recalculate_konverter()
                except Exception as err:
                    QtGui.QMessageBox.information(self, 'Problem', 'Ucitavanje datoteke nije uspjelo.')
                    logging.error(str(err), exc_info=True)
