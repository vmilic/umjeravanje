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
        self.config = None
        self.duljinaSlajsa = None
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
        self.konverterAvgModel = modeli.WorkingFrameModel(cfg=self.konfiguracija)
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
        # kalkulatori
        self.konverterKalkulator = calc.ProvjeraKonvertera(self.konfiguracija)
        self.kalkulator = calc.RacunUmjeravanja(self.konfiguracija)
        self.setup_signal_connections()
        logging.debug('Kraj inicijalizacije GlavniProzor')

    def setup_signal_connections(self):
        """
        connect actione i widgete za callbackovima
        """
        self.action_Exit.triggered.connect(self.close)
        self.action_Read_data.triggered.connect(self.read_data)
        self.comboBoxMjerenje.currentIndexChanged.connect(self.promjena_mjerenja)
        self.checkBoxLinearnost.toggled.connect(self.testni)
#        self.action_Read_config.triggered.connect(self.read_config)
#        self.rawDataView.clicked.connect(self.select_pocetak_umjeravanja)
#        self.tableViewKonverterRaw.clicked.connect(self.select_pocetak_konvertera)
#        self.comboBoxKomponenta.currentIndexChanged.connect(self.recalculate)
#        self.comboBoxDilucija.currentIndexChanged.connect(self.recalculate)
#        self.comboBoxCistiZrak.currentIndexChanged.connect(self.recalculate)
#        self.checkBoxProvjeraLinearnosti.toggled.connect(self.recalculate)
#        self.doubleSpinBoxRasponMjerenja.valueChanged.connect(self.recalculate)
#        self.doubleSpinBoxKoncentracijaCRM.valueChanged.connect(self.recalculate)
#        self.doubleSpinBoxSljedivostCRM.valueChanged.connect(self.recalculate)
#        self.comboBoxStupac.currentIndexChanged.connect(self.recalculate)
#        self.comboBoxNOXstupac.currentIndexChanged.connect(self.recalculate_konverter)
#        self.comboBoxNOstupac.currentIndexChanged.connect(self.recalculate_konverter)

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
            path = str(self.fileWizard.get_path_do_filea())
            # postavi info o ucitanom fileu
            self.labelFilePath.setText(path)
            self.labelPostaja.setText(lokacija)
            self.labelUredjaj.setText(uredjaj)
            msg = 'updateani gui elementi, Ucitani file={0} , Postaja={1} , Uredjaj={2}'.format(path, lokacija, uredjaj)
            logging.info(msg)
            # clear tablice i grafove
            self.clear_tablice_nakon_ucitavanja_datoteke()
            self.clear_grafove()
            self.postavi_sirove_podatke(frejm)
            # postavljanje ostalih podataka za uredjaj
            self.checkBoxLinearnost.setChecked(self.konfiguracija.provjeraLinearnosti)
            self.comboBoxMjerenje.clear()
            komponente = set(self.uredjaji[uredjaj]['komponente'])
            komponente.remove('None')
            self.comboBoxMjerenje.addItems(list(komponente))
            self.promjena_mjerenja(0) #ulazni parametar 0 postoji samo kao placeholder

    def clear_tablice_nakon_ucitavanja_datoteke(self):
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

    def promjena_mjerenja(self, x):
        """
        Promjena komponente mjerenja u gui-u
        """
        komp = str(self.comboBoxMjerenje.currentText())
        try:
            self.konfiguracija.set_mjerenje(komp)
        except AttributeError:
            msg = 'Opseg nije definiran za komponentu, komponenta={0}'.format(komp)
            logging.error(msg)
            self.konfiguracija.opseg = 0
        self.doubleSpinBoxOpseg.setValue(float(self.konfiguracija.opseg))
        self.doubleSpinBoxKoncentracijaCRM.setValue(self.konfiguracija.koncentracijaCRM)
        self.doubleSpinBoxSljedivostCRM.setValue(self.konfiguracija.sljedivostCRM)

    def testni(self, x):
        #TODO! remove later
        print(x)








#
#    def update_frejma_sirovih_podataka(self, frejm):
#        """
#        puno toga...logging
#        """
#        self.rawDataFrame = frejm
#        self.rawDataRow = None
#        #TODO!
#        pass
#
#    def update_frejma_konvertera(self, frejm):
#        """
#        puno toga...logging
#        """
#        #TODO!
#        pass
#
#    def promjena_mjerenja(self):
#        """
#        Promjena vrijednosti komponente za umjeravanje (ulazni parmetar x je
#        indeks pod kojim se nalazi izabrana vrijednost)
#        """
#        logging.debug('Pozvana promjena komponente')
#        komponenta = str(self.labelMjerenje.text())
#        if komponenta != 'None':
#            try:
#                self.konfiguracija.set_mjerenje(komponenta)
#                #reset novu vrijednost opsega za izabrano mjerenje prema normi
#                self.labelOpseg.clear()
#                opseg = str(self.konfiguracija.opseg)
#                self.labelOpseg.setText(opseg)
#                msg = 'Update gui elementa za opseg mjerenja, vrijednost={0}'.format(opseg)
#                logging.info(msg)
#            except AttributeError:
#                logging.error('fail kod dohvacanja opsega ili komponente', exc_info=True)
#
#    def read_data(self):
#        """
#        ucitaj sirove podatke
#
#        1. get path
#        2. try to read data into pandas dataframe
#        3. update labels acordingly
#        4. create and display models
#        """
#        self.fileWizard = datareader.CarobnjakZaCitanjeFilea(cfg=self.konfiguracija,
#                                                             parent=self)
#        prihvacen = self.fileWizard.exec_()
#        if prihvacen:
#            print('ok rezultat')
#            frejm = self.fileWizard.get_frejm()
#            print(frejm.head())
#            print('ok rezultat')
#            path = self.fileWizard.get_path_do_filea()
#            print(path)
#        else:
#            print('nije ok rezultat')
#            path = self.fileWizard.get_path_do_filea()
#            print(path)

#        path = QtGui.QFileDialog.getOpenFileName(self, 'Otvori file')
#        if path:
#            try:
#                self.rawDataFrame = self.read_csv_file(path)
#                msg = str(path)
#                self.dataFilePath.setText(msg)
#            except Exception:
#                msg = 'Nije moguce ucitati trazeni file.'
#                QtGui.QMessageBox.critical(self, 'Error', msg)
#                logging.error(msg, exc_info=True)
#                self.rawDataRow = None
#                self.dataFilePath.setText('None')
#            finally:
#                #reset konverter average frame
#                self.konverterRawRow = None
#                self.konverterAvgFrame = pd.DataFrame()
#                self.konverterAvgModel = None
#                #TODO! treba smisliti bolju ideju za provjeru NOX frejma...
#                if len(self.rawDataFrame.columns) == 3:
#                    self.konverterRawFrame = self.rawDataFrame.copy()
#                else:
#                    self.konverterRawFrame = pd.DataFrame()
#                #comboboxevi za izbor stupca konvertera
#                self.comboBoxNOXstupac.clear()
#                self.comboBoxNOstupac.clear()
#                self.comboBoxNOXstupac.addItems(list(self.konverterRawFrame.columns))
#                self.comboBoxNOstupac.addItems(list(self.konverterRawFrame.columns))
#                self.create_and_display_avg_konverter()
#                self.create_and_display_raw_model_data()
#
#    def create_and_display_raw_model_data(self):
#        """
#        Metoda postavlja ucitane podatke iz pandas frejmova (raw) u modele.
#        """
#        self.rawDataModel.set_frejm(self.rawDataFrame)
#        self.rawDataView.horizontalHeader().setResizeMode(self.STRETCH)
#        self.rawDataView.update()
#        #set opcije za stupac frejma
#        self.comboBoxStupac.clear()
#        cols = [str(i) for i in list(self.rawDataFrame.columns)]
#        self.comboBoxStupac.addItems(cols)
#        # try to set avgDataModel
#        if self.rawDataRow is not None:
#            self.select_pocetak_umjeravanja(self.rawDataRow)
#        else:
#            self.create_and_display_avg_model_data()
#            self.recalculate()
#        # konverter setup
#        self.konverterRawModel.set_frejm(self.konverterRawFrame)
#        self.tableViewKonverterRaw.horizontalHeader().setResizeMode(self.STRETCH)
#        self.tableViewKonverterRaw.update()
#
#    def create_and_display_avg_model_data(self):
#        """
#        metoda postavlja frame u avgDataModel te updatea view.
#        """
#        if self.config is not None:
#            # update avgDataModel
#            self.avgDataModel = modeli.WorkingFrameModel(cfg=self.config)
#            self.avgDataModel.set_frejm(self.avgDataFrame)
#            self.avgDataView.setModel(self.avgDataModel)
#            # update view
#            self.avgDataView.horizontalHeader().setResizeMode(self.STRETCH)
#            self.avgDataView.update()
#
#    def create_and_display_avg_konverter(self):
#        """
#        Metoda postavlja agregirani frejm podataka konvertera u model i updatea
#        odgovarajuci view
#        """
#        if self.config is not None:
#            self.konverterAvgModel = modeli.KonverterAvgFrameModel(cfg=self.config)
#            self.konverterAvgModel.set_frejm(self.konverterAvgFrame)
#            self.tableViewKonverterAvg.setModel(self.konverterAvgModel)
#            self.tableViewKonverterAvg.horizontalHeader().setResizeMode(self.STRETCH)
#            self.tableViewKonverterAvg.update()
#
#
#    def select_pocetak_umjeravanja(self, x):
#        """
#        Izbor pocetka podataka za umjeravanje
#        - rade se 3 minutno agregirane vrijednosti
#        - postavljaju se u working model
#        """
#        if self.config is not None:
#            # multiple type dispatching (int & QModelIndex)
#            if isinstance(x, int):
#                red = x
#            else:
#                red = x.row()
#            self.rawDataRow = red
#            # broj podataka potrebih za racunanje (ovisi o configu)
#            self.duljinaSlajsa = self.get_duljina_slajsa()
#            # provjeri da li ima dovoljno podataka u rawDataFrame za umjeravanje
#            lenRawData = len(self.rawDataFrame)
#            upperBound = red + self.duljinaSlajsa
#            if upperBound > lenRawData:
#                msg = 'Za umjeravanje je potrebno {0} podataka. Postoji samo {1} podataka od izabranog podatka'
#                msg = msg.format(str(self.duljinaSlajsa), str(lenRawData - red))
#                QtGui.QMessageBox.information(self, 'Nedovoljan broj podataka', msg)
#                logging.debug(msg)
#                return
#            # selection highlight
#            self.rawDataModel.set_slajs_len(red, self.duljinaSlajsa)
#            self.rawDataView.update()
#            # dohvati trazeni slajs
#            slajs = self.rawDataFrame.iloc[red:upperBound, :]
#            # resample na 3 minutne
#            self.avgDataFrame = self.resample_frejm(slajs)
#            # set frejm to model
#            self.create_and_display_avg_model_data()
#            #recalculate results
#            self.recalculate()
#
#    def select_pocetak_konvertera(self, x):
#        """
#        Izbor pocetka podataka za provjeru konvertera
#        -rade se 3 minutno agregirane vrijednosti
#        -rezultat se postavlja u self.konverterAvgFrame
#        """
#        if self.config is not None:
#            # multiple type dispatching (int & QModelIndex)
#            if isinstance(x, int):
#                red = x
#            else:
#                red = x.row()
#            self.konverterRawRow = red
#            self.konverterDuljinaSlajsa = self.get_konverter_duljina_slajsa()
#            lenRawData = len(self.konverterRawFrame)
#            upperBound = red + self.konverterDuljinaSlajsa
#            if upperBound > lenRawData:
#                msg = 'Za provjeru konvertera potrebno je {0} podataka. Postoji samo {1} podataka od izabranog podatka'
#                msg = msg.format(str(self.konverterDuljinaSlajsa), str(lenRawData - red))
#                QtGui.QMessageBox.information(self, 'Nedovoljan broj podataka', msg)
#                logging.debug(msg)
#                return
#            # selection highlight
#            self.konverterRawModel.set_slajs_len(red, self.konverterDuljinaSlajsa)
#            self.tableViewKonverterRaw.update()
#            slajs = self.konverterRawFrame.iloc[red:upperBound, :]
#            self.konverterAvgFrame = self.resample_frejm(slajs)
#            self.create_and_display_avg_konverter()
#            self.recalculate_konverter()
#
#    def recalculate(self):
#        """
#        Pocetna metoda za racunanje i prikaz rezultata.
#        """
#        if self.config is not None and len(self.avgDataFrame) > 0:
#            self.update_konfig()
#            if len(self.avgDataFrame)*3 == self.duljinaSlajsa:
#                self.setup_kalkulator()
#                self.kalkulator.racunaj()
#                self.prikazi_rezultate()
#            else:
#                print('error... broj podataka u agregiranom slajsu ne valja')
#                print('moguce da duljina slajsa nije definirana jer podaci nisu ucitani')
#
#    def recalculate_konverter(self):
#        """
#        racunanje rezultata konvertera i prikaz
#        """
#        if self.config is not None and len(self.konverterAvgFrame) > 0:
#            if len(self.konverterAvgFrame)*3 == self.konverterDuljinaSlajsa:
#                #setup kalkulator konvertera
#                #izbor stupaca NOX
#                stupacNOX = self.comboBoxNOXstupac.currentText()
#                if stupacNOX in self.konverterAvgFrame.columns:
#                    ind = list(self.konverterAvgFrame.columns).index(stupacNOX)
#                else:
#                    ind = 0
#                self.konverterKalkulator.set_stupac_NOX(ind)
#                #izbor stupca NO
#                stupacNO = self.comboBoxNOstupac.currentText()
#                if stupacNO in self.konverterAvgFrame.columns:
#                    ind = list(self.konverterAvgFrame.columns).index(stupacNO)
#                else:
#                    ind = 0
#                self.konverterKalkulator.set_stupac_NO(ind)
#                #postavaljanje ostalih parametara
#                self.konverterKalkulator.set_konfig(self.config)
#                self.konverterKalkulator.set_data(self.konverterAvgFrame)
#                #TODO! check and setup stupac
#                self.konverterKalkulator.racunaj()
#                self.prikazi_konverter_rezultate()
#            else:
#                print('error... broj podataka u agregiranom slajsu ne valja')
#                print('moguce da duljina slajsa nije definirana jer podaci nisu ucitani')
#
#    def setup_kalkulator(self):
#        """
#        Funkcija postavlja priprema kalkulator za racunanje. Predaje mu konfig,
#        podatke i stupac s kojim se racuna.
#        """
#        self.kalkulator.set_konfig(self.config)
#        self.kalkulator.set_data(self.avgDataFrame)
#        stupac = self.comboBoxStupac.currentText()
#        msg = 'Racunanje sa stupcem: stupac={0}'.format(str(stupac))
#        logging.debug(msg)
#        if stupac in self.avgDataFrame.columns:
#            ind = list(self.avgDataFrame.columns).index(stupac)
#        else:
#            ind = 0
#        self.kalkulator.set_stupac(ind)
#
#    def clear_result_labels(self):
#        """
#        clear labele rezultata
#        """
#        self.labelSlope.setText('NaN')
#        self.labelOffset.setText('NaN')
#        self.labelA.setText('NaN')
#        self.labelB.setText('NaN')
#        self.labelPonovNula.setText('NaN')
#        self.labelPonovC.setText('NaN')
#        self.labelOdstNula.setText('NaN')
#        self.labelOdstMax.setText('NaN')
#        pass
#
#    def clear_konverter_labels(self):
#        """ clear rezultata konvertera """
#        self.labelEc1.setText('NaN')
#        self.labelEc2.setText('NaN')
#        self.labelEc3.setText('NaN')
#        self.labelEc.setText('NaN')
#
#    def prikazi_rezultate(self):
#        """
#        Metoda sluzi za prikaz rezultata kalkulatora
#        """
#        self.clear_result_labels()
#        # set result data to table view
#        self.resultDataFrame = self.kalkulator.rezultat
#        self.resultDataModel.set_frejm(self.resultDataFrame)
#        self.resultView.setModel(self.resultDataModel)
#        self.resultView.horizontalHeader().setResizeMode(self.STRETCH)
#        # set slope offset and other data
#        slope = self.kalkulator.slope
#        if slope is not None:
#            self.labelSlope.setText(str(round(slope, 3)))
#        offset = self.kalkulator.offset
#        if offset is not None:
#            self.labelOffset.setText(str(round(offset, 3)))
#        prilagodbaA = self.kalkulator.prilagodbaA
#        if prilagodbaA is not None:
#            self.labelA.setText(str(round(prilagodbaA, 3)))
#        prilagodbaB = self.kalkulator.prilagodbaB
#        if prilagodbaB is not None:
#            self.labelB.setText(str(round(prilagodbaB, 3)))
#        # set provjere parametara
#        self.labelPonovNula.setText(str(self.kalkulator.provjeri_ponovljivost_stdev_u_nuli()))
#        self.labelPonovC.setText((str(self.kalkulator.provjeri_ponovljivost_stdev_za_vrijednost())))
#        if self.checkBoxProvjeraLinearnosti.isChecked():
#            self.labelOdstNula.setText((str(self.kalkulator.provjeri_odstupanje_od_linearnosti_u_nuli())))
#            self.labelOdstMax.setText((str(self.kalkulator.provjeri_maksimalno_relativno_odstupanje_od_linearnosti())))
#        # grafovi
#        self.prikazi_grafove()
#
#    def prikazi_konverter_rezultate(self):
#        """
#        prikaz rezultata provjere konvertera
#        """
#        self.clear_konverter_labels()
#        # set result data to table view
#        self.konverterResultFrame = self.konverterKalkulator.rezultat
#        self.konverterResultModel.set_frejm(self.konverterResultFrame)
#        self.tableViewKonverterResult.setModel(self.konverterResultModel)
#        self.tableViewKonverterResult.horizontalHeader().setResizeMode(self.STRETCH)
#        self.labelEc1.setText(self.konverterKalkulator.ec1)
#        self.labelEc2.setText(self.konverterKalkulator.ec2)
#        self.labelEc3.setText(self.konverterKalkulator.ec3)
#        self.labelEc.setText(self.konverterKalkulator.ec)
#
#    def prikazi_grafove(self):
#        """
#        Metoda za crtanje grafova
#        """
#        x = list(self.resultDataFrame.loc[:, 'cref'])
#        y = list(self.resultDataFrame.loc[:, 'c'])
#        self.crefCanvas.crtaj(x, y)
#        stupac = str(self.comboBoxStupac.currentText())
#        if stupac in self.avgDataFrame.columns:
#            x = list(self.avgDataFrame.index)
#            y = list(self.avgDataFrame.loc[:, stupac])
#            self.mjerenjaCanvas.crtaj(x, y)
#
#    def update_konfig(self):
#        """
#        update konfig prema gui vrijednostima
#        """
#        #get values
#        komponenta = self.comboBoxKomponenta.currentText()
#        dilucija = self.comboBoxDilucija.currentText()
#        cistiZrak = self.comboBoxCistiZrak.currentText()
#        linearnost = self.checkBoxProvjeraLinearnosti.isChecked()
#        raspon = self.doubleSpinBoxRasponMjerenja.value()
#        cCRM = self.doubleSpinBoxKoncentracijaCRM.value()
#        sCRM = self.doubleSpinBoxSljedivostCRM.value()
#        # set values
#        self.config.set_komponenta(komponenta)
#        self.config.set_dilucija(dilucija)
#        self.config.set_cistiZrak(cistiZrak)
#        self.config.set_testLinearnosti(linearnost)
#        self.config.set_raspon(raspon)
#        self.config.set_cCRM(cCRM)
#        self.config.set_sCRM(sCRM)
#
#    def update_gui(self, konfig):
#        """
#        update gui elemenata prema konfigu
#        """
#        # block signals da se izbjegne pozivanje recalculate
#        self.comboBoxKomponenta.blockSignals(True)
#        self.comboBoxDilucija.blockSignals(True)
#        self.comboBoxCistiZrak.blockSignals(True)
#        self.checkBoxProvjeraLinearnosti.blockSignals(True)
#        self.doubleSpinBoxRasponMjerenja.blockSignals(True)
#        self.doubleSpinBoxKoncentracijaCRM.blockSignals(True)
#        self.doubleSpinBoxSljedivostCRM.blockSignals(True)
#        #update komponenta
#        komponenta = konfig.izabranaKomponenta
#        ind = self.comboBoxKomponenta.findText(komponenta)
#        self.comboBoxKomponenta.setCurrentIndex(ind)
#        #update dilucija
#        dilucija = konfig.izabranaDilucija
#        ind = self.comboBoxDilucija.findText(dilucija)
#        self.comboBoxDilucija.setCurrentIndex(ind)
#        #update cisti zrak
#        zrak = konfig.izabraniCistiZrak
#        ind = self.comboBoxCistiZrak.findText(zrak)
#        self.comboBoxCistiZrak.setCurrentIndex(ind)
#        #update checkbox linearnost
#        self.checkBoxProvjeraLinearnosti.setChecked(konfig.testLinearnosti)
#        #update raspon mjerenja
#        self.doubleSpinBoxRasponMjerenja.setValue(konfig.raspon)
#        #update koncentracija CRM
#        self.doubleSpinBoxKoncentracijaCRM.setValue(konfig.cCRM)
#        #update sljedivost CRM
#        self.doubleSpinBoxSljedivostCRM.setValue(konfig.sCRM)
#        # unblock signals
#        self.comboBoxKomponenta.blockSignals(False)
#        self.comboBoxDilucija.blockSignals(False)
#        self.comboBoxCistiZrak.blockSignals(False)
#        self.checkBoxProvjeraLinearnosti.blockSignals(False)
#        self.doubleSpinBoxRasponMjerenja.blockSignals(False)
#        self.doubleSpinBoxKoncentracijaCRM.blockSignals(False)
#        self.doubleSpinBoxSljedivostCRM.blockSignals(False)
#
#    def read_config(self):
#        """konfig file za umjeravanje"""
#        path = QtGui.QFileDialog.getOpenFileName(self, 'Otvori file')
#        if path:
#            msg = str(path)
#            self.configFilePath.setText(msg)
#            try:
#                cfg = configparser.ConfigParser()
#                cfg.read(path)
#                self.config = konfiguracija.UKonfig(cfg)
#                self.update_gui(self.config)
#            except Exception:
#                msg = 'Error prilikom ucitavanja konfig filea'
#                logging.error(msg, exc_info=True)
#                QtGui.QMessageBox.critical(self, 'Error', msg)
#                self.config = None
#                self.configFilePath.setText('None')
#                self.avgDataModel = None
#            finally:
#                # try to restore document settings with new data
#                self.create_and_display_raw_model_data()
#                if self.rawDataRow is not None:
#                    self.create_and_display_avg_model_data()
#                self.recalculate()

#    def read_csv_file(self, path):
#        """
#        reader csv filea sirovih podataka
#        """
#        frejm = pd.read_csv(path,
#                            index_col=0,
#                            parse_dates=[0],
#                            dayfirst=True,
#                            header=0,
#                            sep=",",
#                            encoding="iso-8859-1")
#        return frejm
#
#    def get_duljina_slajsa(self):
#        """
#        Dinamicko racunanje potrebne duljine slajsa sirovih podataka
#        za umjeravanje. Koliko podataka trebamo za napraviti 3 minutne
#        srednjake za sve potrebne tocke.
#        """
#        if self.checkBoxProvjeraLinearnosti.isChecked():
#            tocke = self.config.tocke
#        else:
#            tocke = self.config.tocke[:2]
#        duljina = 0
#        for tocka in tocke:
#            duljina += tocka.brojPodataka
#        return duljina*3
#
#    def get_konverter_duljina_slajsa(self):
#        """
#        Dinamicko racunanje potrebne duljine slajsa sirovih podataka za
#        provjeru konvertera. Ukupan broj podataka za 3 minutne srednjake za
#        sve tocke.
#        """
#        tocke = self.config.Ktocke
#        duljina = 0
#        for tocka in tocke:
#            duljina += tocka.brojPodataka
#        return duljina*3
#
#    def resample_frejm(self, slajs):
#        """
#        Resample slajsa pandas datafrejma na 3 minutne srednjake.
#        slajs : pandas dataframe sa podacima
#        """
#        frejm = slajs.copy()
#        listaIndeksa = []
#        for i in range(0, len(frejm), 3):
#            for column in frejm.columns:
#                if i+2 <= len(frejm)-1:
#                    kat = frejm.loc[frejm.index[i]:frejm.index[i+2], column]
#                    srednjak = np.average(kat)
#                    frejm.loc[frejm.index[i], column] = srednjak
#                    if frejm.index[i] not in listaIndeksa:
#                        listaIndeksa.append(frejm.index[i])
#        frejm = frejm[frejm.index.isin(listaIndeksa)]
#        return frejm
#
#    def closeEvent(self, event):
#        """
#        Overloadani signal za gasenje aplikacije. Dodatna potvrda za izlaz.
#        """
#        msg = 'Da li ste sigurni da zelite ugasiti aplikaciju?'
#        reply = QtGui.QMessageBox.question(self,
#                                           'Potvrdi izlaz:',
#                                           msg,
#                                           QtGui.QMessageBox.Yes,
#                                           QtGui.QMessageBox.No)
#        if reply == QtGui.QMessageBox.Yes:
#            event.accept()
#        else:
#            event.ignore()
