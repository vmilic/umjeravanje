# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 09:00:51 2015

@author: DHMZ-Milic

Sve potrebno za tab 'Prikupljanje podataka'
"""
import ipaddress
import datetime
import logging
import pandas as pd
import numpy as np
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigCanvas
from matplotlib.figure import Figure
from PyQt4 import QtCore, QtGui
import app.model.komunikacija as kom

class Kolektor(QtGui.QWidget):
    """
    Gui widget klasa zaduzena za prikupljanje sirovih podataka
    """
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent=parent)
        self.komThread = QtCore.QThread() #odvojeni thread za komunikacijski objekt
        self.veza = kom.Veza()
        self.protokol = kom.Protokol()
        self.komObjekt = kom.KomunikacijskiObjekt(veza=self.veza,
                                                  protokol=self.protokol,
                                                  parent=None)
        self.frejm = pd.DataFrame()
        self.komObjekt.moveToThread(self.komThread)
        #gui & layout dio
        self.startButton = QtGui.QPushButton('Start')
        self.stopButton = QtGui.QPushButton('Stop')
        self.spremiButton = QtGui.QPushButton('Spremi')
        self.clearButton = QtGui.QPushButton('Reset')
        self.postavkeButton = QtGui.QPushButton('Postavke')
        self.opisLabel = QtGui.QLabel('Placeholder za opis veze')
        self.sampleLabel = QtGui.QLabel('Period uzorkovanja (s):')
        self.sampleCombo = QtGui.QComboBox()
        lista = ['1', '5', '10', '15', '20', '25', '30', '60']
        self.sampleCombo.addItems(lista)
        self.meta = {'xlabel':'vrijeme',
                     'ylabel':'koncentracija',
                     'title':'neki naslov grafa'}
        self.graf = GrafMjerenja(meta=self.meta)

        self.dataTableView = QtGui.QTableView()
        self.bareFrejmModel = BareFrameModel(frejm=self.frejm)
        self.dataTableView.setModel(self.bareFrejmModel)
        self.dataTableView.horizontalHeader().setStretchLastSection(True)

        self.mainlayout = QtGui.QHBoxLayout()
        self.hlayout1 = QtGui.QVBoxLayout()
        self.hlayout2 = QtGui.QVBoxLayout()
        self.hlayout3 = QtGui.QHBoxLayout()

        self.hlayout1.addWidget(self.opisLabel)
        self.hlayout1.addWidget(self.graf)
        self.hlayout3.addWidget(self.startButton)
        self.hlayout3.addWidget(self.stopButton)
        self.hlayout3.addWidget(self.spremiButton)
        self.hlayout3.addWidget(self.clearButton)
        self.hlayout3.addWidget(self.postavkeButton)
        self.hlayout3.addWidget(self.sampleLabel)
        self.hlayout3.addWidget(self.sampleCombo)
        self.hlayout3.addStretch(-1)
        self.hlayout1.addLayout(self.hlayout3)
        self.hlayout1.addStretch(-1)

        self.hlayout2.addWidget(self.dataTableView)

        self.mainlayout.addLayout(self.hlayout1)
        self.mainlayout.addLayout(self.hlayout2)
        self.setLayout(self.mainlayout)

        self.setup_connections()

        self.stopButton.setEnabled(False)

    def setup_connections(self):
        self.startButton.clicked.connect(self.start_handle)
        self.stopButton.clicked.connect(self.stop_handle)
        self.sampleCombo.currentIndexChanged.connect(self.promjeni_period_uzorkovanja)
        self.clearButton.clicked.connect(self.reset_frejm)
        self.spremiButton.clicked.connect(self.spremi_frejm)
        self.postavkeButton.clicked.connect(self.prikazi_wizard_postavki)

        self.connect(self,
                     QtCore.SIGNAL('start_prikupljanje_podataka'),
                     self.komObjekt.start_prikupljati_podatke)

        self.connect(self.komObjekt,
                     QtCore.SIGNAL('nova_vrijednost_od_veze(PyQt_PyObject)'),
                     self.dodaj_vrijednost_frejmu)


    def start_handle(self):
        """
        metoda zapocinje prikupljanje podataka
        """
        #enable & disable some buttons
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.sampleCombo.setEnabled(False)
        self.clearButton.setEnabled(False)
        self.spremiButton.setEnabled(False)
        self.postavkeButton.setEnabled(False)
        self.komThread.start()
        self.emit(QtCore.SIGNAL('start_prikupljanje_podataka'))

    def stop_handle(self):
        """
        metoda prekida skupljanje podataka
        """
        self.komThread.exit()
        self.komObjekt.stop_prikupljati_podatke()
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.sampleCombo.setEnabled(True)
        self.clearButton.setEnabled(True)
        self.spremiButton.setEnabled(True)
        self.postavkeButton.setEnabled(True)

    def dodaj_vrijednost_frejmu(self, value):
        """
        metoda dodaje preuzetu vrijednost komunikacijskog objekta u frejm
        """
        plinovi = list(value.keys())
        indeks = value[plinovi[0]][0] #podatak o vremenu
        row = {}
        for plin in plinovi:
            row[plin] = float(value[plin][2])
        tmp = pd.DataFrame(row, index=[indeks])
        self.frejm = self.frejm.append(tmp)
        self.graf.crtaj(frejm=self.frejm, raspon=60)
        self.bareFrejmModel.set_frejm(self.frejm)
        self.dataTableView.update()


    def promjeni_period_uzorkovanja(self, x):
        value = int(self.sampleCombo.currentText())
        self.komObjekt.set_sample_rate(value)

    def reset_frejm(self):
        """clear trenutnih podataka u frejmu...nema backupa"""
        self.frejm = pd.DataFrame()
        self.bareFrejmModel.set_frejm(self.frejm)
        self.dataTableView.update()
        self.graf.reset_graf()


    def spremi_frejm(self):
        """spremanje frejma... po potrebi resample na minutni raspon, koristeci
        average

        #TODO! nije potpuno gotovo jer nisam 100% siguran sto jos treba poslati
        sa preuzetim podacima... npr.
        - trebati ce serijski broj uredjaja
        - potrebno je preimenovati stupce u frejmu da odgovaraju plinovima
        """
        tempFrejm = self.frejm.copy()
        tempFrejm = tempFrejm.resample('1min', how=np.average, closed='right', label='right')
        #TODO! emitiranje signala
        print(tempFrejm)
#        output = {'podaci':tempFrejm}
#        self.emit(QtCore.SIGNAL('spremi_preuzete_podatke(PyQt_PyObject)'), output)

    def prikazi_wizard_postavki(self):
        """
        Promjena postavki veze. Ovisno o rezultatima wizarda treba inicijalizirati
        nove objekte Protokol() i Veza() te ih postaviti u komunikacijski objekt

        #TODO! nije potpuno gotovo jer objekti veza i protokol su placeholderi
        """
        wiz = PostavkeVezeWizard()
        prihvacen = wiz.exec_()
        if prihvacen:
            veza = wiz.get_postavke_veze()
            print('postavke veze:')
            for i in veza:
                print(str(i), ' --> ', str(veza[i]))

class GrafMjerenja(FigCanvas):
    """kanvas za graficki prikaz preuzetih podataka"""
    def __init__(self, meta=None, parent=None, width=9, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        FigCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigCanvas.setSizePolicy(self,
                                QtGui.QSizePolicy.MinimumExpanding,
                                QtGui.QSizePolicy.Fixed)
        FigCanvas.updateGeometry(self)
        self.meta = meta
        self.setup_labels()
        self.fig.set_tight_layout(True)
        #dodatni niz random boja za graf
        self.randomBoje = [
            (0.09, 0.58, 0.58),
            (0.09, 0.09, 0.58),
            (0.09, 0.58, 0.09),
            (0.58, 0.09, 0.09)]
        rc = [tuple(np.random.random(size=3)) for i in range(10)]
        for i in rc:
            self.randomBoje.append(i)

    def setup_labels(self):
        try:
            self.axes.set_xlabel(self.meta['xlabel'], fontsize=8)
            self.axes.set_ylabel(self.meta['ylabel'], fontsize=8)
            self.axes.set_title(self.meta['title'], fontsize=10)
        except (KeyError, ValueError, TypeError):
            pass

    def clear_graf(self):
        """
        clear graf & redo labels
        """
        self.axes.clear()
        self.setup_labels()

    def reset_graf(self):
        self.clear_graf()
        self.draw()

    def crtaj(self, frejm=None, raspon=None):
        """
        metoda za crtanje podataka na graf
        frejm --> pandas datafrejm sa podacima
        raspon --> integer broj minuta za prikaz na grafu
        """
        self.clear_graf()
        zadnji = frejm.index[-1] #zadnji indeks
        prvi = zadnji - datetime.timedelta(minutes=raspon) #prvi indeks
        prozor = frejm[(frejm.index >= prvi) & (frejm.index <= zadnji)]
        vrijeme = list(prozor.index)
        for column in prozor.columns:
            y = prozor.loc[:, column]
            i = list(prozor.columns).index(column)
            boja = self.randomBoje[i]
            #plot
            txt=" ".join(['Plin',str(column)])
            self.axes.plot(vrijeme,
                           y,
                           linewidth=1,
                           color=boja,
                           alpha=0.5,
                           label=txt)
        minimum = max(vrijeme) - datetime.timedelta(minutes=raspon)
        maksimum = max(vrijeme)
        delta = (maksimum - minimum) / 20
        minimum = minimum - delta
        maksimum = maksimum + delta
        self.axes.set_xlim((minimum, maksimum))
        allXLabels = self.axes.get_xticklabels(which='both') #dohvati sve labele
        for label in allXLabels:
            label.set_rotation(20)
            label.set_fontsize(8)

        self.legenda = self.axes.legend(loc=1,
                                        fontsize=8,
                                        fancybox=True)
        self.draw()

class BareFrameModel(QtCore.QAbstractTableModel):
    """
    Model za prikaz preuzetih podataka
    """
    def __init__(self, frejm=None, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        if frejm is None:
            frejm = pd.DataFrame()
        self.set_frejm(frejm)

    def set_frejm(self, frejm):
        self.dataFrejm = frejm
        self.layoutChanged.emit()

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.dataFrejm)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.dataFrejm.columns)

    def flags(self, index):
        if index.isValid():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role):
        if not index.isValid():
            return None
        row = index.row()
        col = index.column()
        if role == QtCore.Qt.DisplayRole:
            return round(float(self.dataFrejm.iloc[row, col]), 1)
        if role == QtCore.Qt.ToolTipRole:
            return str(self.dataFrejm.iloc[row, col])

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                return str(self.dataFrejm.index[section].time())
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return str(self.dataFrejm.columns[section])


class PostavkeVezeWizard(QtGui.QWizard):
    """
    Wizard klasa postavke veze sa uredjajem kojeg umjeravamo
    """
    def __init__(self, parent=None, uredjaji=None):
        QtGui.QWizard.__init__(self, parent)
        if uredjaji == None:
            self.uredjaji = []
        else:
            self.uredjaji = uredjaji
        # opcije
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.setMinimumSize(600, 600)
        self.setWindowTitle("Postavke veze uredjaja")
        self.setOption(QtGui.QWizard.IndependentPages, on=False)
        # stranice wizarda
        self.izborUredjaja = PageIzborUredjaja(parent=self)
        self.izborVeze = PageIzborVeze(parent=self)
        self.izborProtokola = PageIzborProtokola(parent=self)
        self.setPage(1, self.izborUredjaja)
        self.setPage(2, self.izborVeze)
        self.setPage(3, self.izborProtokola)
        self.setStartId(1)

    def get_postavke_veze(self):
        mapa = self.izborProtokola.get_postavke()
        return mapa

class PageIzborUredjaja(QtGui.QWizardPage):
    """
    Stranice za izbor uredjaja s kojim se pokusavamo spojiti. (stranica1)
    """
    def __init__(self, parent = None):
        QtGui.QWizard.__init__(self, parent)
        self.setTitle('Izabor uredjaja')
        self.setSubTitle('Izaberi uredjaj s kojim se pokusavas spojiti')
        self.izabraniUredjaj = None
        # widgets
        self.labelOpis = QtGui.QLabel('Uredjaji :')
        self.comboBoxUredjaji = QtGui.QComboBox()
        # layout
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.labelOpis)
        layout.addWidget(self.comboBoxUredjaji)
        layout.addStretch(-1)
        self.setLayout(layout)

        self.comboBoxUredjaji.currentIndexChanged.connect(self.promjena_uredjaja)

    def promjena_uredjaja(self, x):
        tekst = self.comboBoxUredjaji.currentText()
        self.izabraniUredjaj = tekst

    def initializePage(self):
        self.comboBoxUredjaji.clear()
        uredjaji = ['uredjaj1', 'uredjaj2', 'uredjaj3', 'uredjaj4']
        self.comboBoxUredjaji.addItems(uredjaji)
        self.izabraniUredjaj = self.comboBoxUredjaji.currentText()

    def validatePage(self):
        return True


class PageIzborVeze(QtGui.QWizardPage):
    """Stranica wizarda za izbor tipa veze (stranica2)"""
    def __init__(self, parent=None):
        QtGui.QWizardPage.__init__(self, parent)
        self.setTitle('Izbor veze')
        self.setSubTitle('Izaberi nacin spajanja sa uredjajem')
        self.labelVeza = QtGui.QLabel('Tip veze :')
        self.comboBoxVeza = QtGui.QComboBox()
        self.izabranaVeza = None

        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.labelVeza)
        layout.addWidget(self.comboBoxVeza)
        layout.addStretch(-1)
        self.setLayout(layout)

        self.comboBoxVeza.currentIndexChanged.connect(self.promjena_veze)

    def promjena_veze(self, x):
        tekst = self.comboBoxVeza.currentText()
        self.izabranaVeza = tekst

    def initializePage(self):
        self.comboBoxVeza.clear()
        veze = ['TCP', 'RS-232']
        self.comboBoxVeza.addItems(veze)
        self.izabranaVeza = self.comboBoxVeza.currentText()

    def validatePage(self):
        return True

class PageIzborProtokola(QtGui.QWizardPage):
    """Stranica za izbor protokola veze (stranica3)"""
    def __init__(self, parent=None):
        QtGui.QWizardPage.__init__(self, parent)
        self.setTitle('Izbor protokola')
        self.setSubTitle('Izaberi postavke komunikacijskog protokola')
        self.postavkeProtokola = {}

        self.ipAddressLabel = QtGui.QLabel('IP adresa :')
        self.ipAddress = QtGui.QLineEdit()

        self.tipRS232vezeLabel = QtGui.QLabel('Tip RS-232 veze :')
        self.tipRS232veze = QtGui.QComboBox()
        tipoviRS232veze = ['Hessen', 'Standard']
        self.tipRS232veze.addItems(tipoviRS232veze)

        self.portLabel = QtGui.QLabel('Port :')
        self.port = QtGui.QLineEdit()

        self.brzinaLabel = QtGui.QLabel('Brzina (Baud Rate):')
        self.brzina = QtGui.QSpinBox()
        self.brzina.setRange(50, 5000000)

        self.paritetLabel = QtGui.QLabel('Paritet :')
        self.paritet = QtGui.QComboBox()
        listaPariteta = sorted(['None', 'Odd', 'Even', 'Mark', 'Space'])
        self.paritet.addItems(listaPariteta)

        self.brojBitovaLabel = QtGui.QLabel('Broj bitova :')
        self.brojBitova = QtGui.QComboBox()
        listaBrojaBitova = ['5','6','7','8']
        self.brojBitova.addItems(listaBrojaBitova)

        self.stopBitoviLabel = QtGui.QLabel('Stop bitovi :')
        self.stopBitovi = QtGui.QComboBox()
        listaStopBitova = ['1', '2']
        self.stopBitovi.addItems(listaStopBitova)

        self.duplexLabel = QtGui.QLabel('Duplex :')
        self.duplex = QtGui.QComboBox()
        listaDuplex = ['Full', 'Half']
        self.duplex.addItems(listaDuplex)

        layout = QtGui.QGridLayout()
        layout.addWidget(self.ipAddressLabel, 0, 0, 1, 1)
        layout.addWidget(self.ipAddress, 0, 1, 1, 1)
        layout.addWidget(self.tipRS232vezeLabel, 1, 0, 1, 1)
        layout.addWidget(self.tipRS232veze, 1, 1, 1, 1)
        layout.addWidget(self.portLabel, 2 ,0 ,1, 1)
        layout.addWidget(self.port, 2 ,1 ,1, 1)
        layout.addWidget(self.brzinaLabel, 3 ,0 ,1, 1)
        layout.addWidget(self.brzina, 3 ,1 ,1, 1)
        layout.addWidget(self.paritetLabel, 4 ,0 ,1, 1)
        layout.addWidget(self.paritet, 4 ,1 ,1, 1)
        layout.addWidget(self.brojBitovaLabel, 5 ,0 ,1, 1)
        layout.addWidget(self.brojBitova, 5 ,1 ,1, 1)
        layout.addWidget(self.stopBitoviLabel, 6 ,0 ,1, 1)
        layout.addWidget(self.stopBitovi, 6 ,1 ,1, 1)
        layout.addWidget(self.duplexLabel, 7, 0, 1, 1)
        layout.addWidget(self.duplex, 7, 1, 1, 1)
        self.setLayout(layout)

        self.tipRS232veze.currentIndexChanged.connect(self.promjena_tipa_veze)

    def promjena_tipa_veze(self, x):
        tip = self.tipRS232veze.currentText()
        if tip == 'Hessen':
            self.brzina.setValue(1200)
            self.brojBitova.setCurrentIndex(self.brojBitova.findText('7'))
            self.stopBitovi.setCurrentIndex(self.stopBitovi.findText('2'))
            self.paritet.setCurrentIndex(self.paritet.findText('Even'))
            self.duplex.setCurrentIndex(self.duplex.findText('Half'))
        elif tip == 'Standard':
            self.brzina.setValue(19200)
            self.brojBitova.setCurrentIndex(self.brojBitova.findText('8'))
            self.stopBitovi.setCurrentIndex(self.stopBitovi.findText('1'))
            self.paritet.setCurrentIndex(self.paritet.findText('None'))
            self.duplex.setCurrentIndex(self.duplex.findText('Full'))
        else:
            pass


    def setupLayout(self, veza):
        if veza == 'TCP':
            self.ipAddressLabel.setVisible(True)
            self.ipAddress.setVisible(True)
            self.tipRS232vezeLabel.setVisible(False)
            self.tipRS232veze.setVisible(False)
            self.portLabel.setVisible(True)
            self.port.setVisible(True)
            self.brzinaLabel.setVisible(False)
            self.brzina.setVisible(False)
            self.paritetLabel.setVisible(False)
            self.paritet.setVisible(False)
            self.brojBitovaLabel.setVisible(False)
            self.brojBitova.setVisible(False)
            self.stopBitoviLabel.setVisible(False)
            self.stopBitovi.setVisible(False)
            self.duplexLabel.setVisible(False)
            self.duplex.setVisible(False)
        elif veza == 'RS-232':
            self.ipAddressLabel.setVisible(False)
            self.ipAddress.setVisible(False)
            self.tipRS232vezeLabel.setVisible(True)
            self.tipRS232veze.setVisible(True)
            self.portLabel.setVisible(True)
            self.port.setVisible(True)
            self.brzinaLabel.setVisible(True)
            self.brzina.setVisible(True)
            self.paritetLabel.setVisible(True)
            self.paritet.setVisible(True)
            self.brojBitovaLabel.setVisible(True)
            self.brojBitova.setVisible(True)
            self.stopBitoviLabel.setVisible(True)
            self.stopBitovi.setVisible(True)
            self.duplexLabel.setVisible(True)
            self.duplex.setVisible(True)
        else:
            pass

    def get_postavke(self):
        veza = self.wizard().izborVeze.izabranaVeza
        uredjaj = self.wizard().izborUredjaja.izabraniUredjaj

        self.postavkeProtokola['uredjaj'] = uredjaj
        self.postavkeProtokola['veza'] = veza
        if veza == 'TCP':
            self.postavkeProtokola['ip'] = self.ipAddress.text()
            self.postavkeProtokola['port'] = self.port.text()
        elif veza == 'RS-232':
            self.postavkeProtokola['port'] = self.port.text()
            self.postavkeProtokola['brzina'] = int(self.brzina.value())
            self.postavkeProtokola['paritet'] = self.paritet.currentText()
            self.postavkeProtokola['brojBitova'] = int(self.brojBitova.currentText())
            self.postavkeProtokola['stopBitovi'] = int(self.stopBitovi.currentText())
            self.postavkeProtokola['duplex'] = self.duplex.currentText()
        else:
            pass
        return self.postavkeProtokola

    def initializePage(self):
        veza = self.wizard().izborVeze.izabranaVeza
        self.setupLayout(veza)
        self.tipRS232veze.currentIndexChanged.emit(0)

    def cleanupPage(self):
        self.ipAddressLabel.setVisible(True)
        self.ipAddress.setVisible(True)
        self.tipRS232vezeLabel.setVisible(True)
        self.tipRS232veze.setVisible(True)
        self.portLabel.setVisible(True)
        self.port.setVisible(True)
        self.brzinaLabel.setVisible(True)
        self.brzina.setVisible(True)
        self.paritetLabel.setVisible(True)
        self.paritet.setVisible(True)
        self.brojBitovaLabel.setVisible(True)
        self.brojBitova.setVisible(True)
        self.stopBitoviLabel.setVisible(True)
        self.stopBitovi.setVisible(True)
        self.duplexLabel.setVisible(True)
        self.duplex.setVisible(True)

    def validatePage(self):
        veza = self.wizard().izborVeze.izabranaVeza
        if veza == 'TCP':
            try:
                value = self.ipAddress.text()
                #fail u slucaju neispravne ip adrese (IPv4 i IPv6)
                ipaddress.ip_address(str(value))
            except ValueError as err:
                logging.error(str(err), exc_info=True)
                QtGui.QMessageBox.information(self, 'Pogreska', 'Neispravna ip adresa')
                return False
        #TODO! test ispravnosti porta...
        return True
