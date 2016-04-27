# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 12:15:30 2015

@author: DHMZ-Milic
"""
import os
import numpy as np
import pandas as pd
from PyQt4 import QtGui
from app.pomocni import pomocni
from app.model.qt_models import BaseFrejmModel, ComboBoxDelegate


class CarobnjakZaCitanjeFilea(QtGui.QWizard):
    """
    Wizard dijalog klasa za ucitavanje fileova za umjeravanje
    """
    def __init__(self, parent=None, datastore=None):
        QtGui.QWizard.__init__(self, parent)
        self.datastore = datastore
        """
        page 1 izbor filea i komponenti
        page 2 izbor stupaca i opcije da li su podaci vec minutno usrednjeni.
        """
        # opcije
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.setMinimumSize(600,600)
        self.setWindowTitle("Read config file wizard")
        self.setOption(QtGui.QWizard.IndependentPages, on=False)
        # stranice wizarda
        self.filePage = PageIzborFile(parent=self, datastore=self.datastore)
        self.komponentePage = PageIzborKomponentiFrejma(parent=self, datastore=self.datastore)
        self.setPage(1, self.filePage)
        self.setPage(2, self.komponentePage)
        self.setStartId(1)

    def get_frejm(self):
        """
        Getter metoda za dohvacanje 'uredjenog' pandas datafrejma podataka nakon
        uspjesnog izlaska iz wizarda.
        """
        outFrejm = pd.DataFrame()
        stupci = self.komponentePage.model.cols
        for i in range(len(stupci)):
            if stupci[i] != 'None':
                outFrejm[stupci[i]] = self.komponentePage.df.iloc[:,i]
        return outFrejm

    def get_frejmovi(self):
        """
        Metoda vraca mapu sa frejmovima podataka nakon uspjesnog izlaska iz wizarda.
        kljucevi su minutniPodaci, sekundniPodaci.
        """
        mapa = {}
        frejm = self.get_frejm()
        if self.komponentePage.isMinutniPodaci():
            mapa['minutni'] = frejm
            mapa['sekundni'] = frejm
        else:
            minutni = frejm.resample('1min', how=np.average, closed='right', label='right')
            mapa['sekundni'] = frejm
            mapa['minutni'] = minutni
        return mapa


class PageIzborFile(QtGui.QWizardPage):
    """
    Stranica wizarda za izbor filea i uredjaja
    """
    def __init__(self, parent=None, datastore=None):
        QtGui.QWizard.__init__(self, parent)
        self.datastore = datastore

        #naslov
        self.setTitle('Izbor datoteke')
        serial = str(self.datastore.get_uredjaj().get_serial())
        subTitle = 'Izaberite csv datoteku sa podacima za uredjaj {0}.'.format(serial)
        self.setSubTitle(subTitle)

        #TODO! separator i enkoding
        self.le_separator = QtGui.QLineEdit()
        self.le_enkoding = QtGui.QLineEdit()

        #widgets
        self.pathLabel = QtGui.QLabel('Datoteka :')
        self.lineEditPath = QtGui.QLineEdit()
        self.lineEditPath.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Preferred)
        self.buttonBrowse = QtGui.QPushButton('Browse')

        #TODO! separator
        self.separatorLabel = QtGui.QLabel('Separator :')
        self.comboSeparator = QtGui.QComboBox()
        self.comboSeparator.addItems(['zarez', 'tocka-zarez', 'tab'])
        separatorLayout = QtGui.QHBoxLayout()
        separatorLayout.addWidget(self.separatorLabel)
        separatorLayout.addWidget(self.comboSeparator)
        separatorLayout.addStretch(-1)
        #TODO! encoding
        self.encodingLabel = QtGui.QLabel('Encoding :')
        self.comboEncoding = QtGui.QComboBox()
        self.comboEncoding.addItems(['utf-8', 'iso-8859-1'])
        encodingLayout = QtGui.QHBoxLayout()
        encodingLayout.addWidget(self.encodingLabel)
        encodingLayout.addWidget(self.comboEncoding)
        encodingLayout.addStretch(-1)
        #TODO! layout za opcije
        optionsLayout = QtGui.QVBoxLayout()
        optionsLayout.addLayout(separatorLayout)
        optionsLayout.addLayout(encodingLayout)

        #layout
        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(self.pathLabel)
        mainLayout.addWidget(self.lineEditPath)
        mainLayout.addWidget(self.buttonBrowse)

        #layout za opcije encoding....
        topLayout = QtGui.QVBoxLayout()
        topLayout.addLayout(optionsLayout)
        topLayout.addLayout(mainLayout)
        topLayout.addStretch(-1)

        self.setLayout(topLayout)
        #self.setLayout(mainLayout)
        #connections
        self.buttonBrowse.clicked.connect(self.locate_file)
        #connections
        self.comboSeparator.currentIndexChanged.connect(self.set_separator_text)
        self.comboEncoding.currentIndexChanged.connect(self.set_enkoding_text)
#        """
#        --> registriram sadrzaj widgeta self.lineEditPath kao 'filepath'
#        --> dostupan je svim drugim stanicama wizarda
#        --> * na kraju stringa oznacava mandatory field
#        """
        self.registerField('filepath*', self.lineEditPath)
        #TODO! field register sep i encoding
        self.registerField('separator*', self.le_separator)
        self.registerField('enkoding*', self.le_enkoding)

    def set_enkoding_text(self, x):
        """setter separatora csv filea"""
        tekst = self.comboEncoding.currentText()
        self.le_enkoding.setText(tekst)

    def set_separator_text(self, x):
        """setter tipa encodinga filea"""
        tekst = self.comboSeparator.currentText()
        if tekst == 'tab':
            separator = '\t'
        elif tekst == 'tocka-zarez':
            separator = ';'
        else:
            separator = ","
        self.le_separator.setText(separator)

    def initializePage(self):
        """
        Inicijalizacija izbornika
        """
        print('initializePage')
        self.set_separator_text(True)
        self.set_enkoding_text(True)

    def validatePage(self):
        """
        Validacija stranice. Provjera da li postoji file koji pokusavamo ucitati.
        """
        path = str(self.lineEditPath.text())
        #provjeri da li je file path validan prije nastavka
        if not os.path.isfile(path):
            msg = 'Trazena datoteka ne postoji.'
            QtGui.QMessageBox.information(self, 'Problem.', msg)
            return False
        return True

    def locate_file(self):
        """
        Funkcija je povezana sa gumbom browse, otvara file dijalog i sprema
        izabrani path do datoteke u self.lineEditPath widget
        """
        self.lineEditPath.clear()
        path = QtGui.QFileDialog.getOpenFileName(parent=self,
                                         caption="Open file",
                                         directory="",
                                         filter="CSV files (*.csv)")
        self.lineEditPath.setText(str(path))


class PageIzborKomponentiFrejma(QtGui.QWizardPage):
    def __init__(self, parent=None, datastore=None):
        """
        Stranica wizarda za izbor stupaca u ucitanom frejmu.
        """
        QtGui.QWizard.__init__(self, parent)
        self.setTitle('Izbor komponenti')
        self.setSubTitle('Izaberite sve komponente za pojedini stupac. Odaberite da li su podaci prethodno minutno usrednjeni.')
        self.datastore = datastore

        self.tableView = QtGui.QTableView()
        self.tableView.setWordWrap(True)
        self.tableView.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)

        self.fileLabel = QtGui.QLabel('')
        self.fileLabel.setWordWrap(True)
        self.fileLabel.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                                     QtGui.QSizePolicy.Fixed)
        self.label1 = QtGui.QLabel('Datoteka :')

        self.box = QtGui.QGroupBox('Tip podataka')
        self.minutniRadio = QtGui.QRadioButton('Minutni podaci')
        self.sekundniRadio = QtGui.QRadioButton('Sekundni podaci')
        boxlayout = QtGui.QHBoxLayout()
        boxlayout.addWidget(self.minutniRadio)
        boxlayout.addWidget(self.sekundniRadio)
        self.box.setLayout(boxlayout)
        self.minutniRadio.toggle()

        fileLayout = QtGui.QHBoxLayout()
        fileLayout.addWidget(self.label1)
        fileLayout.addWidget(self.fileLabel)
        layout = QtGui.QVBoxLayout()
        layout.addLayout(fileLayout)
        layout.addWidget(self.box)
        layout.addWidget(self.tableView)
        self.setLayout(layout)

    def isMinutniPodaci(self):
        """
        Metoda sluzi za provjeru tipa podataka (minutni ili sekundni).
        Metoda vraca True ako je radio button self.minutniRadio aktivan.
        """
        return self.minutniRadio.isChecked()

    def return_frejm(self):
        """
        Metoda vraca za vracanje ucitanog frejma
        """
        return self.df

    @pomocni.activate_wait_spinner
    def initializePage(self):
        """
        Funkcija se pokrece prilikom inicijalizacije stranice
        """
        self.path = self.field('filepath')
        self.uredjaj = self.datastore.get_uredjaj()
        name = os.path.split(self.path)[1]
        self.fileLabel.setText(name)
        txt = " ".join(['Izaberi komponente za uredjaj', self.uredjaj.get_serial()])
        self.setSubTitle(txt)
        self.komponente = list(self.uredjaj.get_komponente().keys())
        if 'None' not in self.komponente:
            self.komponente.append('None')
        try:
            #TODO! separator i enkoding ulaznog filea...
            separator, enkoding = self.field('separator'), self.field('enkoding')
            self.df = self.read_csv_file(self.path, sep=separator, enc=enkoding)
            self.model = BaseFrejmModel(frejm=self.df)
            self.delegat = ComboBoxDelegate(stupci=self.komponente, parent=self.tableView)
            self.tableView.setModel(self.model)
            self.tableView.setItemDelegateForRow(0, self.delegat)
            for col in range(len(self.df.columns)):
                self.tableView.openPersistentEditor(self.model.index(0, col))
                self.tableView.indexWidget(self.model.index(0, col)).currentIndexChanged.connect(self.dinamicki_update_opcija_comboa)
        except OSError as err:
            msg = 'error kod citanja filea: {0}\n'.format(str(err))
            QtGui.QMessageBox.information(self, 'Problem.', msg)
            self.wizard().done(0)

    def validatePage(self):
        """
        Validator za stranicu. return True ako je sve u redu, inace vrati False.

        -svi nazivi stupaca moraju biti unikatni (osim 'None')
        -mora biti barem jedan stupac
        """
        izabraniStupci = [i for i in self.model.cols if i != 'None']
        izabraniStupci = [i for i in izabraniStupci if i != '']
        setIzabranih = set(izabraniStupci)
        if len(izabraniStupci) == (len(self.komponente) - 1):
            if len(setIzabranih) == len(izabraniStupci):
                return True
            else:
                msg = 'Isti naziv je koristen na vise stupaca. Naziv se smije koristiti samo jednom.'
                QtGui.QMessageBox.information(self, 'Problem.', msg)
                return False
        else:
            msg = 'Sve dozvoljene komponente moraju biti izabrane.'
            QtGui.QMessageBox.information(self, 'Problem.', msg)
            return False

    def dinamicki_update_opcija_comboa(self, ind):
        """
        Pomocna metoda za promjenu popisa itema unutar comboboxa. Na ovu metodu su
        spojeni svi comboboxevi i pozivaju ju prilikom promjene trenutno aktivnog
        indeksa.
        """
        self.setMogucih = set(self.komponente)
        kutije = []
        for i in range(self.model.columnCount()):
            kutije.append(self.tableView.indexWidget(self.model.index(0, i)))
        for combo in kutije:
            #pronadji listu ostalih comboboxeva
            x = [kutije[i] for i in range(len(kutije)) if kutije[i] != combo]
            #pozovi na update popisa
            self.update_sadrzaj_comboboxa(combo, x, self.setMogucih)

    def update_sadrzaj_comboboxa(self, combo, ostali, moguci):
        """
        pomocna metoda za promjenu popisa itema unutar comboboxa
        """
        combo.blockSignals(True)
        #zapamti trenutni Izbor
        trenutni = combo.currentText()
        #pronadji koristene u drugim comboima
        used = set()
        for item in ostali:
            used.add(item.currentText())
        if 'None' in used:
            used.remove('None')
        dozvoljeni = moguci.difference(used)
        #clear starog comboa
        combo.clear()
        #dodavanje novog popisa
        combo.addItems(sorted(list(dozvoljeni)))
        #reset na pocetnu vrijednosti
        ind = combo.findText(trenutni)
        combo.setCurrentIndex(ind)
        combo.blockSignals(False)

    def read_csv_file(self, path, sep=',', enc='utf-8'):
        """
        reader csv filea
        """
        frejm = pd.read_csv(path,
                            index_col=0,
                            parse_dates=[0],
                            dayfirst=True,
                            header=0,
                            sep=sep,
                            encoding=enc)
        return frejm
