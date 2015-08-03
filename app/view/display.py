# -*- coding: utf-8 -*-
"""
Created on Mon May 18 12:02:42 2015

@author: DHMZ-Milic
"""
import logging
import pandas as pd
from PyQt4 import QtGui, QtCore, uic
import app.model.konfig_klase as konfig
import app.model.pomocne_funkcije as helperi
import app.model.frejm_model as modeli
import app.model.kalkulator as calc
import app.view.read_file_wizard as datareader
import app.view.canvas as canvas

#TODO! logging i converter tab, refactor
class ColorDelegate(QtGui.QItemDelegate):
    """
    Delegat klasa za tockeView, stupac 6 (promjena boje preko dijaloga)
    """
    def __init__(self, tocke=None, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)
        self.tocke = tocke

    def createEditor(self, parent, option, index):
        """
        Direktni poziv dijaloga i ako se vrati ok boja, direktni setter podataka
        """
        if index.isValid():
            red = index.row()
            oldColor = self.tocke[red].boja.rgba()
            newColor, test = QtGui.QColorDialog.getRgba(oldColor)
            if test:
                color = QtGui.QColor().fromRgba(newColor)
                self.tocke[red].boja = color
                #signaliziraj za refresh viewova
                self.emit(QtCore.SIGNAL('promjena_boje_tocke'))


BASE, FORM = uic.loadUiType('./app/view/uiFiles/display.ui')
class GlavniProzor(BASE, FORM):
    """
    Gui element glavnog prozora
    """
    def __init__(self, cfg=None, parent=None):
        super(BASE, self).__init__(parent)
        self.setupUi(self)
        self.STRETCH = QtGui.QHeaderView.Stretch
        self.uredjaji = {}
        self.postaje = {}
        try:
            self.konfiguracija = konfig.MainKonfig(cfg)
            self.postaje, self.uredjaji = helperi.pripremi_mape_postaja_i_uredjaja(
                self.konfiguracija.uredjajUrl,
                self.konfiguracija.postajeUrl)
        except (TypeError, AttributeError):
            msg = 'Konfig aplikacije ne moze naci trazeni element.'
            logging.error(msg, exc_info=True)
            raise SystemExit('Konfiguracijski file nije ispravan.')

        # inicijalni setup membera
        self.comboDilucija.addItems(self.konfiguracija.get_listu_dilucija())
        self.comboZrak.addItems(self.konfiguracija.get_listu_cistiZrak())
        self.checkLinearnost.setChecked(self.konfiguracija.provjeraLinearnosti)


        #definiranje modela sirovih podataka
        self.siroviPodaci = pd.DataFrame()
        self.siroviPodaciModel = modeli.SiroviFrameModel()
        self.siroviPodaciView.setModel(self.siroviPodaciModel)

        #definiranje modela tocaka
        self.modelTocaka = modeli.TockeModel()
        self.modelTocaka.set_tocke(self.konfiguracija.umjerneTocke)
        self.tockeView.setModel(self.modelTocaka)
        self.tockeView.horizontalHeader().setResizeMode(self.STRETCH)
        self.tockeView.update()

        #prati koja je tocka zadnje selektirana
        self.redTockeZaEdit = None

        #color delegat za tablicu
        self.delegatZaBoju = ColorDelegate(tocke=self.konfiguracija.umjerneTocke)
        self.konverterDelegatZaBoju = ColorDelegate(tocke=self.konfiguracija.konverterTocke)
        #set delegat na svoje mjesto
        self.tockeView.setItemDelegateForColumn(6, self.delegatZaBoju)
        self.konverterTockeView.setItemDelegateForColumn(5, self.konverterDelegatZaBoju)


        #definiranje kalkulatora
        self.kalkulator = calc.RacunUmjeravanja(cfg=self.konfiguracija)

        # rezultat umjeravanja
        self.rezultatUmjeravanja = pd.DataFrame(columns=['cref', 'c', 'sr', 'r', 'UR'])
        self.rezultatModel = modeli.RezultatModel()
        self.rezultatModel.set_frejm(self.rezultatUmjeravanja)
        self.rezultatView.setModel(self.rezultatModel)
        self.rezultatView.horizontalHeader().setResizeMode(self.STRETCH)
        self.rezultatView.update()

        #definiranje modela tocaka za provjeru konvertera
        self.modelTocakaKonverter = modeli.KonverterTockeModel()
        self.modelTocakaKonverter.set_tocke(self.konfiguracija.konverterTocke)
        self.konverterTockeView.setModel(self.modelTocakaKonverter)
        self.konverterTockeView.horizontalHeader().setResizeMode(self.STRETCH)
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
        self.konverterRezultatModel = modeli.RezultatModel()
        self.konverterRezultatModel.set_frejm(self.rezultatUmjeravanja)
        self.konverterRezultatView.setModel(self.konverterRezultatModel)
        self.konverterRezultatView.horizontalHeader().setResizeMode(self.STRETCH)
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
        self.tockeView.clicked.connect(self.odaberi_edit_tocku)

        self.gumbDodajTocku.clicked.connect(self.dodaj_umjernu_tocku)
        self.gumbBrisiTocku.clicked.connect(self.makni_umjernu_tocku)
        self.gumbEditTocku.clicked.connect(self.edit_tocke)

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

        self.connect(self.delegatZaBoju,
                     QtCore.SIGNAL('promjena_boje_tocke'),
                     self.refresh_views)

        self.connect(self.siroviPodaciModel,
                     QtCore.SIGNAL('promjena_vrijednosti_tocke'),
                     self.refresh_views)

        self.connect(self.konverterPodaciModel,
                     QtCore.SIGNAL('promjena_vrijednosti_konverter_tocke'),
                     self.refresh_views)

    def read_data(self):
        """
        ucitavanje sirovih podataka preko wizarda
        """
        self.fileWizard = datareader.CarobnjakZaCitanjeFilea(uredjaji=self.uredjaji,
                                                             postaje=self.postaje,
                                                             parent=self)
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
        self.modelTocaka.set_frejm(self.siroviPodaci)
        self.siroviPodaciView.horizontalHeader().setResizeMode(self.STRETCH)
        self.siroviPodaciView.update()
        self.tockeView.update()
        #postavljanje podataka za provjeru konvertera samo ako je NOX
        testSet = set(['NOx', 'NO', 'NO2'])
        dataSet = set(self.siroviPodaci.columns)
        if testSet.issubset(dataSet):
            self.konverterPodaci = self.siroviPodaci
            self.konverterPodaciModel.set_frejm(self.konverterPodaci)
            self.konverterPodaciModel.set_tocke(self.konfiguracija.konverterTocke)
            self.modelTocakaKonverter.set_frejm(self.konverterPodaci)
            self.konverterPodaciView.horizontalHeader().setResizeMode(self.STRETCH)
            self.konverterPodaciView.update()
            self.konverterTockeView.update()
        else:
            self.konverterPodaci = pd.DataFrame()
            self.konverterPodaciModel.set_frejm(self.konverterPodaci)
            self.konverterPodaciModel.set_tocke(self.konfiguracija.konverterTocke)
            self.modelTocakaKonverter.set_frejm(self.konverterPodaci)
            self.konverterPodaciView.horizontalHeader().setResizeMode(self.STRETCH)
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

    def odaberi_edit_tocku(self, x):
        """
        izbor tocke za editiranje
        """
        red = x.row()
        try:
            naziv = str(self.konfiguracija.umjerneTocke[red])
            nazivEdit = 'Promjeni interval tocke: ' + naziv
            nazivRemove = 'Izbrisi tocku: ' + naziv
            self.gumbEditTocku.setText(nazivEdit)
            self.gumbBrisiTocku.setText(nazivRemove)
            self.redTockeZaEdit = red
        except Exception as err:
            logging.error(str(err), exc_info=True)
            self.gumbEditTocku.setText('Promjeni interval tocke: ')
            self.gumbBrisiTocku.setText('Izbrisi tocku: ')
            self.redTockeZaEdit = None

    def edit_tocke(self, x):
        """
        Metoda sluzi kao switch izmedju dva nacina rada siroviPodaciView.
        1. izbor pocetka umjeravanja
        2. izbor intervala (start end) izabrane tocke.
        """
        if self.gumbEditTocku.isChecked():
            self.gumbDodajTocku.setEnabled(False)
            self.gumbBrisiTocku.setEnabled(False)
            self.siroviPodaciView.clicked.disconnect()
            self.siroviPodaciView.clicked.connect(self.odaberi_novi_interval_izabrane_tocke)
        else:
            self.gumbDodajTocku.setEnabled(True)
            self.gumbBrisiTocku.setEnabled(True)
            self.siroviPodaciView.clicked.disconnect()
            self.siroviPodaciView.clicked.connect(self.odaberi_start_umjeravanja)

    def odaberi_novi_interval_izabrane_tocke(self, x):
        """izbor novih granica tocke

        1. provjeri da li je izabrana neka tocka i dohvati njene podatke (lokaciju)
        2. selection changed...
        """
        if self.redTockeZaEdit is not None:
            indeksi = self.siroviPodaciView.selectedIndexes()
            redovi = set(sorted([i.row() for i in indeksi]))
            #indeksi drugih tocaka
            temp = list(range(len(self.konfiguracija.umjerneTocke)))
            temp.remove(self.redTockeZaEdit)
            testPreklapanja = [self.konfiguracija.umjerneTocke[i].test_indeksi_tocke_se_preklapaju(redovi) for i in temp]
            if True in testPreklapanja:
                return None
            minimalni = min(redovi)
            if len(redovi) >= 15 and minimalni >= self.siroviPodaciModel.startIndeks:
                self.konfiguracija.umjerneTocke[self.redTockeZaEdit].indeksi = redovi
                self.recalculate()

    def refresh_views(self):
        """
        force refresh modela i view-ova nakon promjene podataka
        """
        # umjeravanje
        self.siroviPodaciModel.layoutChanged.emit()
        self.modelTocaka.layoutChanged.emit()
        self.rezultatModel.layoutChanged.emit()
        self.siroviPodaciView.update()
        self.tockeView.update()
        self.rezultatView.update()
        # konverter
        self.konverterPodaciModel.layoutChanged.emit()
        self.modelTocakaKonverter.layoutChanged.emit()
        self.konverterRezultatModel.layoutChanged.emit()
        self.konverterPodaciView.update()
        self.konverterTockeView.update()
        self.konverterRezultatView.update()

    def dodaj_umjernu_tocku(self):
        """
        dodavanje nove umjerne tocke na popis
        """
        if len(self.konfiguracija.umjerneTocke) == 0:
            #ne postoje tocke umjeravanja...napravi novu
            tocka = konfig.Tocka(ime='TOCKA1', start=15, end=45, cref=0.8)
            self.konfiguracija.umjerneTocke.append(tocka)
        else:
            #pronadji max indeks izmedju svih tocaka
            maxIndeks = max([max(tocka.indeksi) for tocka in self.konfiguracija.umjerneTocke])
            ime = "".join(['TOCKA',str(len(self.konfiguracija.umjerneTocke)+1)])
            start = maxIndeks + 15
            end = maxIndeks + 30
            tocka = konfig.Tocka(ime=ime, start=start, end=end, cref=0.0)
            self.konfiguracija.umjerneTocke.append(tocka)
        self.recalculate()

    def makni_umjernu_tocku(self, x):
        """
        Brisanje izabrane tocke...
        """
        if self.redTockeZaEdit is not None:
            try:
                self.konfiguracija.umjerneTocke.pop(self.redTockeZaEdit)
                self.gumbEditTocku.setText('Promjeni interval tocke: ')
                self.gumbBrisiTocku.setText('Izbrisi tocku: ')
                self.redTockeZaEdit = None
                self.recalculate()
            except Exception as err:
                logging.error(str(err), exc_info=True)

    def setup_kalkulator(self):
        """
        Funkcija postavlja priprema kalkulator za racunanje. Predaje mu konfig,
        podatke i stupac s kojim se racuna.
        """
        self.kalkulator.set_uredjaj(self.uredjaji[str(self.labelUredjaj.text())])
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
        # set provjere parametara
        self.labelPonovNula.setText(str(self.kalkulator.provjeri_ponovljivost_stdev_u_nuli()))
        self.labelPonovC.setText((str(self.kalkulator.provjeri_ponovljivost_stdev_za_vrijednost())))
        if self.checkLinearnost.isChecked():
            self.labelOdstNula.setText((str(self.kalkulator.provjeri_odstupanje_od_linearnosti_u_nuli())))
            self.labelOdstMax.setText((str(self.kalkulator.provjeri_maksimalno_relativno_odstupanje_od_linearnosti())))

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
        self.labelPonovNula.setText('n/a')
        self.labelPonovC.setText('n/a')
        self.labelOdstNula.setText('n/a')
        self.labelOdstMax.setText('n/a')

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
