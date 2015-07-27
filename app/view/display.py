# -*- coding: utf-8 -*-
"""
Created on Mon May 18 12:02:42 2015

@author: DHMZ-Milic
"""
import logging
import pandas as pd
import numpy as np
from PyQt4 import QtGui, uic
import app.model.frejm_model as modeli
import app.model.konfig_klase as konfiguracija
import app.model.kalkulator as calc
import app.model.pomocne_funkcije as helperi
import app.view.canvas as canvas
import app.view.read_file_wizard as datareader
import app.view.setup_tocke_wizard as wizardTocke

BASE, FORM = uic.loadUiType('./app/view/uiFiles/display_new.ui')


class GlavniProzor(BASE, FORM):
    """
    Gui element glavnog prozora
    """
    def __init__(self, cfg=None, parent=None):
        logging.debug('Pocetak inicijalizacije GlavniProzor')
        super(BASE, self).__init__(parent)
        self.setupUi(self)
        # konstante
        self.STRETCH = QtGui.QHeaderView.Stretch
        # members
        self.kalkulator = None
        self.konfiguracija = None
        self.duljinaSlajsa = 0
        self.konverterDuljinaSlajsa = 0
        self.uredjaji = {}
        self.postaje = {}
        try:
            self.konfiguracija = konfiguracija.MainKonfig(cfg)
            self.postaje, self.uredjaji = helperi.pripremi_mape_postaja_i_uredjaja(
                self.konfiguracija.uredjajUrl,
                self.konfiguracija.postajeUrl)
            self.comboBoxDilucija.addItems(self.konfiguracija.get_listu_dilucija())
            self.comboBoxCistiZrak.addItems(self.konfiguracija.get_listu_cistiZrak())
        except (TypeError, AttributeError):
            msg = 'Konfig aplikacije ne moze naci trazeni element.'
            logging.error(msg, exc_info=True)
            raise SystemExit('Konfiguracijski file nije ispravan.')
        # frejmovi
        self.rawDataRow = 0
        self.konverterRawRow = 0
        self.rawDataFrame = pd.DataFrame()
        self.avgDataFrame = pd.DataFrame()
        self.resultDataFrame = pd.DataFrame()
        self.konverterRawFrame = pd.DataFrame()
        self.konverterAvgFrame = pd.DataFrame()
        self.konverterResultFrame = pd.DataFrame
        # modeli
        self.rawDataModel = modeli.SiroviFrameModel()
        self.avgDataModel = modeli.WorkingFrameModel(cfg=self.konfiguracija)
        self.resultDataModel = modeli.RezultatModel()
        self.konverterRawModel = modeli.SiroviFrameModel()
        self.konverterAvgModel = modeli.KonverterAvgFrameModel(cfg=self.konfiguracija)
        self.konverterResultModel = modeli.RezultatModel()
        # povezivanje model --> view
        self.rawDataView.setModel(self.rawDataModel)
        self.avgDataView.setModel(self.avgDataModel)
        self.resultView.setModel(self.resultDataModel)
        self.konverterRawDataView.setModel(self.konverterRawModel)
        self.konverterAvgDataView.setModel(self.konverterAvgModel)
        self.konverterResultView.setModel(self.konverterResultModel)
        # inicijalizacija i postavljanje kanvasa za grafove.
        meta1 = {'xlabel':'referentna koncentracija, cref',
                 'ylabel':'koncentracija, c',
                 'title':'Cref / koncentracija graf'}
        meta2 = {'xlabel':'vrijeme',
                 'ylabel':'koncentracija, c',
                 'title':'Individualna mjerenja'}
        self.crefCanvas = canvas.Kanvas(meta=meta1)
        self.mjerenjaCanvas = canvas.Kanvas(meta=meta2)
        # dodaj grafove u layout
        self.grafLayout.addWidget(self.crefCanvas)
        self.grafLayout.addWidget(self.mjerenjaCanvas)
        # kalkulator za efikasnost konvertera
        self.konverterKalkulator = calc.ProvjeraKonvertera(self.konfiguracija)
        # kalkulator umjeravanja
        self.kalkulator = calc.RacunUmjeravanja(self.konfiguracija)
        self.kalkulator.set_dilucija(self.comboBoxDilucija.currentText())
        self.kalkulator.set_cistiZrak(self.comboBoxCistiZrak.currentText())
        # definiranje kontrolnih signala
        self.setup_signal_connections()
        logging.debug('Kraj inicijalizacije GlavniProzor')

    def setup_signal_connections(self):
        """
        connect actione i widgete za callbackovima
        """
        self.action_Exit.triggered.connect(self.close)
        self.action_Read_data.triggered.connect(self.read_data)
        self.action_Setup_tocke_umjeravanja.triggered.connect(self.setup_tocke_umjeravanja)
        self.comboBoxMjerenje.currentIndexChanged.connect(self.recalculate)
        self.checkBoxLinearnost.toggled.connect(self.promjena_provjere_linearnosti)
        self.rawDataView.clicked.connect(self.select_pocetak_umjeravanja)
        self.comboBoxMjerenje.currentIndexChanged.connect(self.recalculate)
        self.comboBoxDilucija.currentIndexChanged.connect(self.recalculate)
        self.comboBoxCistiZrak.currentIndexChanged.connect(self.recalculate)
        self.doubleSpinBoxOpseg.valueChanged.connect(self.promjena_opsega)
        self.doubleSpinBoxKoncentracijaCRM.valueChanged.connect(self.recalculate)
        self.doubleSpinBoxSljedivostCRM.valueChanged.connect(self.recalculate)
        #konverter
        self.konverterRawDataView.clicked.connect(self.select_pocetak_provjere_konvertera)

    def closeEvent(self, event):
        """
        Overloadani signal za gasenje aplikacije. Dodatna potvrda za izlaz.
        """
        msg = 'Da li ste sigurni da zelite ugasiti aplikaciju?'
        reply = QtGui.QMessageBox.question(self,
                                           'Potvrdi izlaz:',
                                           msg,
                                           QtGui.QMessageBox.Yes,
                                           QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def read_data(self):
        """
        Metoda radi 2 bitne stvari:
        1.Ucitava sirove podatke uz pomoc wizarda.
            -izbor lokacija filea
            -izbor uredjaja
            -izbor naziva stupaca ucitanih podataka
        2.Postavlja ucitane podatke u model i prikazuje ih u za to predvidjenom
        grafickom widgetu.
        """
        self.fileWizard = datareader.CarobnjakZaCitanjeFilea(uredjaji=self.uredjaji,
                                                             postaje=self.postaje,
                                                             parent=self)
        prihvacen = self.fileWizard.exec_()
        if prihvacen:
            logging.info('Wizard je uspjesno ucitao podatke iz datoteke')
            frejm = self.fileWizard.get_frejm()
            lokacija = self.fileWizard.get_postaja()
            uredjaj = self.fileWizard.get_uredjaj()
            self.kalkulator.set_uredjaj(self.uredjaji[uredjaj]) #setter uredjaja u kalkulator
            try:
                #ako uredjaj ima podatak o opsegu postavi opseg
                opseg = float(self.uredjaji[uredjaj]['analitickaMetoda']['o']['max'])
                self.doubleSpinBoxOpseg.setValue(opseg)
            except LookupError:
                #zanemari gresku (nepostojeci kljuc)
                pass
            path = str(self.fileWizard.get_path_do_filea())
            # postavi info o ucitanom fileu
            self.labelFilePath.setText(path)
            self.labelPostaja.setText(lokacija)
            self.labelUredjaj.setText(uredjaj)
            msg = 'updateani gui elementi, Ucitani file={0} , Postaja={1} , Uredjaj={2}'.format(path, lokacija, uredjaj)
            logging.info(msg)
            # clear tablice i grafove
            self.clear_tablice_prije_ucitavanja_datoteke()
            self.clear_grafove()
            self.postavi_sirove_podatke(frejm)
            # postavljanje ostalih podataka za uredjaj
            self.checkBoxLinearnost.setChecked(self.konfiguracija.provjeraLinearnosti)
            self.comboBoxMjerenje.clear()
            komponente = set(self.uredjaji[uredjaj]['komponente'])
            komponente.remove('None')
            self.comboBoxMjerenje.addItems(list(komponente))
            self.recalculate()

    def clear_tablice_prije_ucitavanja_datoteke(self):
        """
        Nakon ucitavanja novog filea potrebno je 'resetirati' tablice da bi
        se izbjegle potencijalne zabune.
        -memberi koji drze frejmove sa podacima se postavljaju na prazne frejmove
        -update modela za prikaz sa novim frejmovima
        -update view
        """
        # reinicijalizacija frejmova sa podacima
        self.rawDataFrame = pd.DataFrame()
        self.avgDataFrame = pd.DataFrame()
        self.konverterRawFrame = pd.DataFrame()
        self.konverterAvgFrame = pd.DataFrame()
        self.resultDataFrame = pd.DataFrame()
        self.konverterResultFrame = pd.DataFrame()
        logging.debug('Prazni frejmovi postavljeni u membere sa frejmovima.')
        #clear odredjenih membera kalkulatora! data
        self.kalkulator.set_data(pd.DataFrame())
        # update vezanih modela
        self.rawDataModel.set_frejm(self.rawDataFrame)
        self.avgDataModel.set_frejm(self.avgDataFrame)
        self.resultDataModel.set_frejm(self.resultDataFrame)
        self.konverterRawModel.set_frejm(self.konverterRawFrame)
        self.konverterAvgModel.set_frejm(self.konverterAvgFrame)
        self.konverterResultModel.set_frejm(self.konverterResultFrame)
        logging.debug('Update modela za frejmove gotov')
        # update view pojedinacnih modela
        self.rawDataView.update()
        self.avgDataView.update()
        self.resultView.update()
        self.konverterRawDataView.update()
        self.konverterAvgDataView.update()
        self.konverterResultView.update()
        logging.debug('Sve QTableView instance su updateane.')
        # clear konverter labele
        self.labelEc1.setText('NaN')
        self.labelEc2.setText('NaN')
        self.labelEc3.setText('NaN')
        self.labelEc.setText('NaN')
        logging.debug('Labeli u Konverter tabu postavljeni na NaN')
        #clear ostalih labela
        self.clear_result_labels()

    def clear_grafove(self):
        """
        clear grafova nakon ucitavanja novog filea, izbjegavanje potencijalih
        zabuna
        """
        self.crefCanvas.clear_graf()
        self.mjerenjaCanvas.clear_graf()
        logging.debug('Grafovi su ocisceni')

    def postavi_sirove_podatke(self, frejm):
        """
        Metoda postavlja pandas datafrejm (ulazni parametar) u member,
        predaje ga modelu i konacno se updatea view.
        """
        msg = 'Frejm sa sirovim podacima prihvacen, frejm.head()={0}'.format(frejm.head())
        logging.debug(msg)
        logging.info('Popunjavanje tablice sa "sirovim" podacima')
        self.rawDataFrame = frejm
        self.rawDataModel.set_frejm(self.rawDataFrame)
        self.rawDataView.horizontalHeader().setResizeMode(self.STRETCH)
        self.rawDataView.update()
        # provjera za konverter... samo NOx
        stupciFrejma = set(list(frejm.columns))
        stupciZaKonverter = set(['NOx', 'NO2', 'NO'])
        if stupciZaKonverter.issubset(stupciFrejma):
            logging.info('Popunjavanje tablice sa "sirovim" podacima za provjeru konvertera')
            # konverter setup
            self.konverterRawFrame = frejm
            self.konverterRawModel.set_frejm(self.konverterRawFrame)
            self.konverterRawDataView.horizontalHeader().setResizeMode(self.STRETCH)
            self.konverterRawDataView.update()

    def promjena_opsega(self, x):
        """
        Promjena vrijednosti opsega mjerenja. Ponovno izracunaj umjeravanje i
        provjeru konvertera.
        """
        self.recalculate()
        self.konverter_recalculate()

    def select_pocetak_umjeravanja(self, x):
        """
        Izbor pocetka podataka za umjeravanje
        - rade se 3 minutno agregirane vrijednosti
        - postavljaju se u model
        """
        if self.konfiguracija is not None:
            if isinstance(x, int):
                red = x
            else:
                red = x.row()
            msg = 'Izabrani pocetak umjeravanja, red={0}, index={1}'.format(str(red), str(self.rawDataFrame.index[red]))
            logging.info(msg)
            self.rawDataRow = red
            # broj podataka potrebih za racunanje (ovisi o configu, tj.tockama)
            self.duljinaSlajsa = self.get_duljina_slajsa()
            # provjeri da li ima dovoljno podataka u rawDataFrame za umjeravanje
            lenRawData = len(self.rawDataFrame)
            upperBound = red + self.duljinaSlajsa
            if upperBound > lenRawData:
                msg = 'Nema dovoljno sirovih podataka od izabrane tocke.\nZa umjeravanje je potrebno {0} podataka. Postoji samo {1} podataka.'
                msg = msg.format(str(self.duljinaSlajsa), str(lenRawData - red))
                QtGui.QMessageBox.information(self, 'Nedovoljan broj podataka', msg)
                logging.debug(msg)
                return
            # selection highlight modela sirovih podataka (obojaj izabrane)
            logging.debug('bojanje podataka koji se koriste za umjeravanje')
            self.rawDataModel.set_slajs_len(red, self.duljinaSlajsa)
            self.rawDataView.update()
            # dohvati trazeni slajs
            slajs = self.rawDataFrame.iloc[red:upperBound, :]
            # resample na 3 minutne
            self.avgDataFrame = self.resample_frejm(slajs)
            # update avgDataModel
            self.avgDataModel.set_frejm(self.avgDataFrame)
            self.avgDataView.setModel(self.avgDataModel)
            # update view
            self.avgDataView.horizontalHeader().setResizeMode(self.STRETCH)
            self.avgDataView.update()
            # predaj agregirani frejm kalkulatoru
            self.kalkulator.set_data(self.avgDataFrame)
            # predaj listu tocaka kalkulatoru i bool provjere linearnosti
            self.recalculate()

    def get_duljina_slajsa(self):
        """
        Dinamicko racunanje potrebne duljine slajsa sirovih podataka
        za umjeravanje. Koliko podataka trebamo za napraviti 3 minutne
        srednjake za sve potrebne tocke.

        Pretpostavka da se tocke ne preklapaju
        """
        if self.checkBoxLinearnost.isChecked():
            tocke = self.konfiguracija.umjerneTocke
        else:
            tocke = [self.konfiguracija.zeroTocka, self.konfiguracija.spanTocka]
        start = tocke[0].startIndeks
        kraj = tocke[0].endIndeks
        for tocka in tocke:
            if tocka.startIndeks < start:
                start = tocka.startIndeks
            if tocka.endIndeks > kraj:
                kraj = tocka.endIndeks
        duljina = kraj - start
        msg = 'Ukupni broj potrebnih sirovih podataka za umjeravanje, N={0}'.format(duljina*3)
        logging.debug(msg)
        return duljina*3

    def resample_frejm(self, slajs):
        """
        Resample slajsa pandas datafrejma na 3 minutne srednjake.
        slajs : pandas dataframe sa podacima
        """
        msg = 'resample frejma na 3 minutne srednjake, ulazni_frejm=\n{0}'.format(str(slajs))
        logging.debug(msg)
        frejm = slajs.copy()
        listaIndeksa = []
        for i in range(0, len(frejm), 3):
            for column in frejm.columns:
                if i+2 <= len(frejm)-1:
                    kat = frejm.loc[frejm.index[i]:frejm.index[i+2], column]
                    srednjak = np.average(kat)
                    frejm.loc[frejm.index[i], column] = srednjak
                    if frejm.index[i] not in listaIndeksa:
                        listaIndeksa.append(frejm.index[i])
        frejm = frejm[frejm.index.isin(listaIndeksa)]
        msg = 'resample frejma na 3 minutne srednjake, izlazni_frejm=\n{0}'.format(str(frejm))
        logging.debug(msg)
        return frejm

    def promjena_provjere_linearnosti(self, x):
        """
        Promjena vrijednosti chekBox-a za provjeru linearnosti. Ulazni parametar
        x je boolean. Postoji samo zbog signala kojeg emitira comboBox prilikom
        promjene.

        Metoda simulira izbor pocetka umjeravanja na sirovim podacima (koristi
        vec izabranu tocku ili 0'ti index po defaultu). Metoda select_pocetak_umjeravanja
        uzima u obzir stanje checkboxa, te pravilno updatea view.
        """
        if len(self.rawDataFrame) > 0:
            self.select_pocetak_umjeravanja(self.rawDataRow)

    def setup_kalkulator(self):
        """
        Funkcija postavlja priprema kalkulator za racunanje. Predaje mu konfig,
        podatke i stupac s kojim se racuna.
        """
        logging.debug('Priprema kalkulatora za racunanje')
        self.kalkulator.set_data(self.avgDataFrame)
        linearnost = self.checkBoxLinearnost.isChecked()
        if linearnost:
            tocke = self.konfiguracija.umjerneTocke
        else:
            tocke = [self.konfiguracija.zeroTocka, self.konfiguracija.spanTocka]
        self.kalkulator.set_tocke(tocke)
        self.kalkulator.set_zero(self.konfiguracija.zeroTocka)
        self.kalkulator.set_span(self.konfiguracija.spanTocka)
        self.kalkulator.set_linearnost(linearnost)
        self.kalkulator.set_stupac(self.comboBoxMjerenje.currentText())
        self.kalkulator.set_opseg(float(self.doubleSpinBoxOpseg.value()))
        self.kalkulator.set_cCRM(float(self.doubleSpinBoxKoncentracijaCRM.value()))
        self.kalkulator.set_sCRM(float(self.doubleSpinBoxSljedivostCRM.value()))
        self.kalkulator.set_dilucija(self.comboBoxDilucija.currentText())
        self.kalkulator.set_cistiZrak(self.comboBoxCistiZrak.currentText())

    def recalculate(self):
        """
        Pocetna metoda za racunanje i prikaz rezultata umjeravanja.
        """
        if len(self.avgDataFrame)*3 == self.duljinaSlajsa:
            self.setup_kalkulator()
            self.kalkulator.racunaj()
            self.prikazi_rezultate()
        else:
            logging.info('Duljina slajsa ne odgovara za racunanje')

    def prikazi_rezultate(self):
        """
        Metoda sluzi za prikaz rezultata kalkulatora umjeravanja
        """
        self.clear_result_labels()
        # set result data to table view
        self.resultDataFrame = self.kalkulator.rezultat
        self.resultDataModel.set_frejm(self.resultDataFrame)
        self.resultView.setModel(self.resultDataModel)
        self.resultView.horizontalHeader().setResizeMode(self.STRETCH)
        # set slope offset and other data
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
        if self.checkBoxLinearnost.isChecked():
            self.labelOdstNula.setText((str(self.kalkulator.provjeri_odstupanje_od_linearnosti_u_nuli())))
            self.labelOdstMax.setText((str(self.kalkulator.provjeri_maksimalno_relativno_odstupanje_od_linearnosti())))
        # grafovi
        self.prikazi_grafove()

    def clear_result_labels(self):
        """
        clear labele rezultata
        """
        self.labelSlope.setText('NaN')
        self.labelOffset.setText('NaN')
        self.labelA.setText('NaN')
        self.labelB.setText('NaN')
        self.labelPonovNula.setText('NaN')
        self.labelPonovC.setText('NaN')
        self.labelOdstNula.setText('NaN')
        self.labelOdstMax.setText('NaN')
        logging.debug("Labeli sa rezulattima su postavljeni na 'NaN'")

    def prikazi_grafove(self):
        """
        Metoda za crtanje grafova
        """
        if len(self.resultDataFrame) > 0:
            x = list(self.resultDataFrame.loc[:, 'cref'])
            y = list(self.resultDataFrame.loc[:, 'c'])
            self.crefCanvas.crtaj(x, y)
            stupac = str(self.comboBoxMjerenje.currentText())
            if stupac in self.avgDataFrame.columns:
                x = list(self.avgDataFrame.index)
                y = list(self.avgDataFrame.loc[:, stupac])
                self.mjerenjaCanvas.crtaj(x, y)

    def select_pocetak_provjere_konvertera(self, x):
        """
        Izbor pocetne tocke za provjeru konvertera
        """
        if self.konfiguracija is not None:
            # multiple type dispatching (int & QModelIndex)
            if isinstance(x, int):
                red = x
            else:
                red = x.row()
            msg = 'Izabrani pocetak provjere konvertera, red={0}, index={1}'.format(str(red), str(self.konverterRawFrame.index[red]))
            logging.info(msg)
            # broj podataka potrebih za racunanje (ovisi o configu, tj.tockama)
            self.konverterDuljinaSlajsa = self.get_konverter_duljina_slajsa()
            # provjeri da li ima dovoljno podataka u rawDataFrame za umjeravanje
            lenRawData = len(self.konverterRawFrame)
            upperBound = red + self.konverterDuljinaSlajsa
            if upperBound > lenRawData:
                msg = 'Nema dovoljno sirovih podataka od izabrane tocke.\nZa provjeru konvertera je potrebno {0} podataka. Postoji samo {1} podataka.'
                msg = msg.format(str(self.konverterDuljinaSlajsa), str(lenRawData - red))
                QtGui.QMessageBox.information(self, 'Nedovoljan broj podataka', msg)
                logging.debug(msg)
                return
            # selection highlight modela sirovih podataka (obojaj izabrane)
            logging.debug('bojanje podataka koji se koriste za umjeravanje')
            self.konverterRawModel.set_slajs_len(red, self.konverterDuljinaSlajsa)
            self.konverterRawDataView.update()
            # dohvati trazeni slajs
            slajs = self.konverterRawFrame.iloc[red:upperBound, :]
            # resample na 3 minutne
            self.konverterAvgFrame = self.resample_frejm(slajs)
            # update avgDataModel
            self.konverterAvgModel.set_frejm(self.konverterAvgFrame)
            self.konverterAvgDataView.setModel(self.konverterAvgModel)
            # update view
            self.konverterAvgDataView.horizontalHeader().setResizeMode(self.STRETCH)
            self.konverterAvgDataView.update()
            # setup kalkulator objekt
            self.setup_konverter_kalkulator()
            self.konverter_recalculate()

    def get_konverter_duljina_slajsa(self):
        """
        Dinamicko racunanje potrebne duljine slajsa sirovih podataka
        za provjeru konvertera. Pretpostavke da se tocke ne preklapaju i
        da se radi 3 mintni srednjaci
        """
        tocke = self.konfiguracija.konverterTocke
        duljina = 0
        for tocka in tocke:
            duljina += tocka.get_brojPodataka()
        msg = 'Ukupni broj potrebnih sirovih podataka za provjeru konvertera, N={0}'.format(duljina*3)
        logging.debug(msg)
        return duljina*3

    def setup_konverter_kalkulator(self):
        """
        Funkcija postavlja priprema konverter kalkulator za racunanje.
        """
        logging.debug('Priprema konverter kalkulatora za racunanje')
        self.konverterKalkulator.set_data(self.konverterAvgFrame)
        self.konverterKalkulator.set_opseg(float(self.doubleSpinBoxOpseg.value()))

    def konverter_recalculate(self):
        """
        Pocetna metoda za racunanje i prikaz rezultata provjere konvertera.
        """
        if self.comboBoxMjerenje.currentText() in ['NOx', 'NO', 'NO2']:
            if len(self.konverterAvgFrame)*3 == self.konverterDuljinaSlajsa:
                self.setup_konverter_kalkulator()
                self.konverterKalkulator.racunaj()
                self.prikazi_konverter_rezultate()
            else:
                logging.info('Duljina slajsa ne odgovara za racunanje konvertera')

    def prikazi_konverter_rezultate(self):
        """
        Metoda sluzi za prikaz rezultata kalkulatora provjere konvertera
        """
        # set result data to table view
        self.konverterResultFrame = self.konverterKalkulator.rezultat
        self.konverterResultModel.set_frejm(self.konverterResultFrame)
        self.konverterResultView.setModel(self.konverterResultModel)
        self.konverterResultView.horizontalHeader().setResizeMode(self.STRETCH)
        #label setting
        self.labelEc1.setText(self.konverterKalkulator.ec1)
        self.labelEc2.setText(self.konverterKalkulator.ec2)
        self.labelEc3.setText(self.konverterKalkulator.ec3)
        self.labelEc.setText(self.konverterKalkulator.ec)

    def setup_tocke_umjeravanja(self):
        """
        Pokretanje wizarda za izbor tocaka za umjeravanje
        """
        self.tockeWizard = wizardTocke.CarobnjakZaDefiniranjeTocaka(parent=self)
        prihvacen = self.tockeWizard.exec_()
        if prihvacen:
            tocke, zero, span = self.tockeWizard.get_tocke()
            self.konfiguracija.umjerneTocke = tocke
            self.konfiguracija.zeroTocka = zero
            self.konfiguracija.spanTocka = span
            self.promjena_provjere_linearnosti(0) # 0 je placeholder
