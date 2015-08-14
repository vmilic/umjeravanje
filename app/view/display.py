# -*- coding: utf-8 -*-
"""
Created on Mon May 18 12:02:42 2015

@author: DHMZ-Milic
"""
import logging

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

#TODO! sredi neke boje u konfigu za tocke
#TODO! neki save/load mehanizam (qt data stream?)
#TODO! refresh rest data? podatke o uredjajima...gumb? akcija?
#TODO! treba prilagoditi konverter na nesto smislenije
#TODO! mjerne jedinice na sve
#TODO! prilagodi gui da izgleda ako predlozak.
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
        # inicijalni setup membera
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
        ### tablica sa testom analitickih metoda ###
        self.rezultatParametriView = QtGui.QTableView()
        self.rezultatParametriView.setMinimumSize(300,250)
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

        #definiranje modela tocaka za provjeru konvertera
        self.modelTocakaKonverter = modeli.KonverterTockeModel()
        self.modelTocakaKonverter.set_tocke(self.konfiguracija.konverterTocke)
        self.konverterTockeView.setModel(self.modelTocakaKonverter)
        self.konverterTockeView.update()

        #definiranje modela podataka za provjeru konvertera
        self.konverterPodaci = pd.DataFrame()
        self.konverterPodaciModel = modeli.KonverterFrameModel()
        self.konverterPodaciView.setModel(self.konverterPodaciModel)

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
        self.konverterRezultatModel.set_frejm(self.rezultatUmjeravanja)
        self.konverterRezultatView.setModel(self.konverterRezultatModel)
        self.konverterRezultatView.update()

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
        self.grafoviGroupBox.layout().addWidget(self.crefCanvas)
        self.grafoviGroupBox.layout().addWidget(self.mjerenjaCanvas)

    def setup_signal_connections(self):
        """
        connect actione i widgete za callbackovima
        """
        self.action_Exit.triggered.connect(self.close)
        self.action_ucitaj_podatke.triggered.connect(self.read_data)

        self.siroviPodaciView.clicked.connect(self.odaberi_start_umjeravanja)

        self.comboMjerenje.currentIndexChanged.connect(self.recalculate)
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

        self.connect(self.siroviPodaciModel,
                     QtCore.SIGNAL('promjena_vrijednosti_tocke'),
                     self.refresh_views)

        self.connect(self.konverterPodaciModel,
                     QtCore.SIGNAL('promjena_vrijednosti_konverter_tocke'),
                     self.refresh_views)

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
            self.comboMjerenje.clear()
            komponente = set(self.uredjaji[uredjaj]['komponente'])
            komponente.remove('None')
            self.comboMjerenje.addItems(list(komponente))
            if 'NOx' in komponente:
                ind = self.comboMjerenje.findText('NOx')
                self.comboMjerenje.setCurrentIndex(ind)
            try:
                #ako uredjaj ima podatak o opsegu postavi opseg
                opseg = float(self.uredjaji[uredjaj]['analitickaMetoda']['o']['max'])
                self.doubleSpinBoxOpseg.setValue(opseg)
            except LookupError:
                #zanemari gresku (nepostojeci kljuc)
                pass
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
            self.konverterPodaci = self.siroviPodaci
            self.konverterPodaciModel.set_frejm(self.konverterPodaci)
            self.konverterPodaciModel.set_tocke(self.konfiguracija.konverterTocke)
            self.modelTocakaKonverter.set_frejm(self.konverterPodaci)
            self.konverterPodaciView.update()
            self.konverterTockeView.update()
        else:
            self.konverterPodaci = pd.DataFrame()
            self.konverterPodaciModel.set_frejm(self.konverterPodaci)
            self.konverterPodaciModel.set_tocke(self.konfiguracija.konverterTocke)
            self.modelTocakaKonverter.set_frejm(self.konverterPodaci)
            self.konverterPodaciView.update()
            self.konverterTockeView.update()

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
        self.siroviPodaciModel.set_tocke(self.konfiguracija.umjerneTocke)
        self.rezultatModel.set_tocke(self.konfiguracija.umjerneTocke)
        self.rezultatParametriModel.set_lista(self.kalkulator.get_provjeru_parametara())
        self.siroviPodaciView.update()
        self.rezultatView.update()
        self.rezultatParametriView.update()
        # konverter
        self.konverterPodaciModel.set_tocke(self.konfiguracija.konverterTocke)
        self.modelTocakaKonverter.layoutChanged.emit()
        self.konverterRezultatModel.set_tocke(self.konfiguracija.konverterTocke)
        self.konverterPodaciView.update()
        self.konverterTockeView.update()
        self.konverterRezultatView.update()
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
        #clear labele
        self.clear_result_labels()
        #clear grafove
        self.crefCanvas.clear_graf()
        self.mjerenjaCanvas.clear_graf()
        self.setup_kalkulator()
        self.kalkulator.racunaj()
        self.prikazi_rezultate()
        self.prikazi_grafove()
        self.refresh_views()

    def recalculate_konverter(self):
        """
        Poceta metoda za racunanje i prikaz rezultata provjere konvertera
        """
        self.clear_konverter_result_labels()
        self.setup_konverter_kalkulator()
        self.konverterKalkulator.racunaj()
        self.prikazi_rezultate_konvertera()
        self.refresh_views()


    def prikazi_rezultate(self):
        """
        Metoda sluzi za prikaz rezultata kalkulatora umjeravanja
        """
        # set result data to table view
        self.rezultatUmjeravanja = self.kalkulator.rezultat
        self.rezultatModel.set_frejm(self.rezultatUmjeravanja)
        #slope offset i funkcija prilagodbe
        slope = self.kalkulator.slope
        if slope is not None:
            self.labelSlope.setText(str(round(slope, 3)))
        offset = self.kalkulator.offset
        if offset is not None:
            self.labelOffset.setText(str(round(offset, 3)))
        prilagodbaA = self.kalkulator.prilagodbaA
        if prilagodbaA is not None:
            self.labelA.setText(str(round(prilagodbaA, 3)))
        prilagodbaB = self.kalkulator.prilagodbaB
        if prilagodbaB is not None:
            self.labelB.setText(str(round(prilagodbaB, 3)))

    def prikazi_rezultate_konvertera(self):
        # set result data to table view
        self.konverterRezultat = self.konverterKalkulator.rezultat
        self.konverterRezultatModel.set_frejm(self.konverterRezultat)
        # postavi labele
        self.labelEc1.setText(str(self.konverterKalkulator.ec1))
        self.labelEc2.setText(str(self.konverterKalkulator.ec2))
        self.labelEc3.setText(str(self.konverterKalkulator.ec3))
        self.labelEc.setText(str(self.konverterKalkulator.ec))

    def clear_result_labels(self):
        """
        clear labele rezultata
        """
        self.labelSlope.setText('n/a')
        self.labelOffset.setText('n/a')
        self.labelA.setText('n/a')
        self.labelB.setText('n/a')

    def clear_konverter_result_labels(self):
        """
        clear labele rezultata za provjeru konvertera
        """
        self.labelEc1.setText('n/a')
        self.labelEc2.setText('n/a')
        self.labelEc3.setText('n/a')
        self.labelEc.setText('n/a')

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

    def save_umjeravanje_to_file(self):
        """
        pickle se lomi sa QObject...
        #ucitani podaci
        - kontrolni elementi (combo, spinbox)
        - labeli
        - ...
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
        # ucitani podaci...frejm
        outputMapa['frejmPodataka'] = self.siroviPodaci
        # start indeks u modelu
        outputMapa['pocetniIndeks'] = self.siroviPodaciModel.startIndeks
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

        # combo mjerenje

        # combo dilucija

        # combo cisti zrak

        #izbor combo mjerenje

        #izbor combo dilucija

        #izbor combo cisti zrak

        # opseg

        # koncentracija CRM

        #sljedivost CRM

        #TODO! pickle to some file

    def load_umjeravanje_from_file(self, file):
        #TODO! dohvati mapu objekta van!
    pass

