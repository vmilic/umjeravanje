# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 12:15:30 2015

@author: DHMZ-Milic
"""
import os
import logging
import pandas as pd
from PyQt4 import QtGui
import app.model.pomocne_funkcije as helperi
import app.model.frejm_model as modeli

################################################################################
################################################################################
#TODO! wizard klasa
class CarobnjakZaCitanjeFilea(QtGui.QWizard):
    """
    Wizard dijalog klasa za ucitavanje fileova za umjeravanje
    """
    def __init__(self, parent=None, uredjaji=None, postaje=None):
        QtGui.QWizard.__init__(self, parent)
        logging.info('Inicijalizacija Wizada za citanje podataka')

        tmp = helperi.priprema_podataka_za_model_stanica_i_uredjaja(uredjaji)
        self.setPostaja, self.setUredjaj, self.setKomponenta, self.listaZaModel = tmp

        self.uredjaji = uredjaji
        self.postaje = postaje

        self.komponente = []
        self.izbor = []
        # opcije
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.setMinimumSize(600,600)
        self.setWindowTitle("Read config file wizard")
        self.setOption(QtGui.QWizard.IndependentPages, on=False)
        # stranice wizarda
        self.P1 = Page1Wizarda(parent=self)
        self.P2 = Page2Wizarda(parent=self)
        self.P3 = Page3Wizarda(parent=self)
        self.setPage(1, self.P1)
        self.setPage(2, self.P2)
        self.setPage(3, self.P3)
        self.setStartId(1)

    def set_izbor(self, lista):
        """
        postavljanje izbora postaje-uredjaja-komponente
        """
        self.izbor = lista
        uredjaj = self.izbor[1]
        komp = self.uredjaji[uredjaj]['komponente']
        self.set_komponente(komp)

    def set_komponente(self, lista):
        """
        Setter za dozvoljene komponente uredjaja. Ulazni parametar je lista
        stringova koji odgovaraju komponentama. Dodaje se 'None' ako ne postoji
        sa ciljem da se neki stupci u sirovim podacima mogu zanemariti.
        """
        self.komponente = lista
        if not 'None' in self.komponente:
            self.komponente.append('None')

    def get_frejm(self):
        """
        Getter metoda za dohvacanje 'uredjenog' pandas datafrejma podataka nakon
        uspjesnog izlaska iz wizarda.
        """
        outFrejm = pd.DataFrame()
        stupci = self.P3.model.cols
        for i in range(len(stupci)):
            if stupci[i] != 'None':
                outFrejm[stupci[i]] = self.P3.df.iloc[:,i]
        return outFrejm

    def get_path_do_filea(self):
        """
        Vrati path do filea koji je ucitan nakon uspjesnog izlaska
        iz wizarda"""
        path = str(self.P1.lineEditPath.text())
        if len(path) != 0:
            return path
        else:
            return 'None'

    def get_postaja(self):
        """
        Vrati izabranu postaju nakon uspjesnog izlaska iz wizarda.
        """
        postaja = str(self.izbor[0])
        if len(postaja) != 0:
            return postaja
        else:
            return 'None'

    def get_uredjaj(self):
        """
        Vrati izabrani uredjaj nakon uspjesnog izlaska iz wizarda.
        """
        uredjaj = str(self.izbor[1])
        if len(uredjaj) != 0:
            return uredjaj
        else:
            return 'None'
################################################################################
################################################################################
#TODO! stranica 1
class Page1Wizarda(QtGui.QWizardPage):
    """
    Prva stranica izbornika, prikazuje polje za unos lokacije filea i gumb
    koji otvara dijalog za izbor filea.
    """
    def __init__(self, parent = None):
        QtGui.QWizard.__init__(self, parent)
        self.setTitle('Izaberi file')
        self.setSubTitle('Browse ili direktno upisi path do filea')
        # widgets
        self.lineEditPath = QtGui.QLineEdit()
        self.buttonBrowse = QtGui.QPushButton('Browse')
        # layout
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.lineEditPath)
        layout.addWidget(self.buttonBrowse)
        self.setLayout(layout)
        # povezivanje elemenata
        self.buttonBrowse.clicked.connect(self.locate_file)
        """
        --> registriram sadrzaj widgeta self.lineEditPath kao 'filepath'
        --> dostupan je svim drugim stanicama wizarda
        --> * na kraju stringa oznacava mandatory field
        """
        self.registerField('filepath*', self.lineEditPath)

    def initializePage(self):
        """
        overloaded funkcija koja odradjuje inicijalizaciju prilikom prvog prikaza
        """
        self.lineEditPath.clear()

    def locate_file(self):
        """
        Funkcija je povezana sa gumbom browse, otvara file dijalog i sprema
        izabrani path do konfiguracijske datoteke u self.lineEditPath widget
        """
        self.lineEditPath.clear()
        path = QtGui.QFileDialog.getOpenFileName(parent=self,
                                         caption="Open file",
                                         directory="",
                                         filter="CSV files (*.csv)")
        self.lineEditPath.setText(str(path))

    def validatePage(self):
        """
        funkcija se pokrece prilikom prelaza na drugi wizard page.
        Funkcija mora vratiti boolean. True omogucava ucitavanje druge stranice
        wizarda, False blokira prijelaz.
        """
        path = str(self.lineEditPath.text())
        #provjeri da li je file path validan prije nastavka
        if not os.path.isfile(path):
            msg = 'Trazena datoteka ne postoji.'
            QtGui.QMessageBox.information(self, 'Problem.', msg)
            return False
        return True
################################################################################
################################################################################
#TODO! stranica 2
class Page2Wizarda(QtGui.QWizardPage):
    """
    Izbor postaje, uredjaja i komponente. Podaci su u modelu koji je "wrapan"
    u 3 proxy modela koji omogucavaju filtriranje za svaki od pojedinih stupaca.
    Filtriranje je uz pomoc comboboxeva. Izbor kombinacije je klikom na model.
    """
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.setTitle('Izbor uredjaja')
        msg = 'Izaberi kombinaciju postaje uredjaja i komponente'
        self.setSubTitle(msg)
        #memberi
        self.postaje = sorted(list(self.parent().setPostaja))
        self.uredjaji = sorted(list(self.parent().setUredjaj))
        self.komponente = sorted(list(self.parent().setKomponenta))
        self.modelList = self.parent().listaZaModel
        self.postaje.append('')  #opcija bez filtera
        self.uredjaji.append('')  #opcija bez filtera
        self.komponente.append('')  #opcija bez filtera

        #widgets
        self.comboKomponenta = QtGui.QComboBox()
        self.comboKomponenta.addItems(self.komponente)
        self.comboPostaja = QtGui.QComboBox()
        self.comboPostaja.addItems(self.postaje)
        self.comboUredjaj = QtGui.QComboBox()
        self.comboUredjaj.addItems(self.uredjaji)
        self.labelKomponenta = QtGui.QLabel('Filter komponente')
        self.labelPostaja = QtGui.QLabel('Filter postaja')
        self.labelUredjaj = QtGui.QLabel('Filter uredjaja')
        self.tableView = QtGui.QTableView()
        self.fileLabel = QtGui.QLabel('')
        self.fileLabel.setWordWrap(True)
        self.fileLabel.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                                     QtGui.QSizePolicy.Fixed)
        self.label1 = QtGui.QLabel('Datoteka :')

        #models
        self.model = modeli.PostajaUredjajKomponentaModel(lista=self.modelList, parent=self)

        self.proksiModelPostaja = QtGui.QSortFilterProxyModel()
        self.proksiModelPostaja.setDynamicSortFilter(True)
        self.proksiModelPostaja.setFilterKeyColumn(0)
        self.proksiModelPostaja.setSourceModel(self.model)

        self.proksiModelUredjaj = QtGui.QSortFilterProxyModel()
        self.proksiModelUredjaj.setDynamicSortFilter(True)
        self.proksiModelUredjaj.setFilterKeyColumn(1)
        self.proksiModelUredjaj.setSourceModel(self.proksiModelPostaja)

        self.proksiModelKomponenta = QtGui.QSortFilterProxyModel()
        self.proksiModelKomponenta.setDynamicSortFilter(True)
        self.proksiModelKomponenta.setFilterKeyColumn(2)
        self.proksiModelKomponenta.setSourceModel(self.proksiModelUredjaj)

        self.tableView.setModel(self.proksiModelKomponenta)
        self.tableView.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.tableView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tableView.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tableView.verticalHeader().setVisible(False)
        self.tableView.setSortingEnabled(True)

        #layout
        fileLayout = QtGui.QHBoxLayout()
        fileLayout.addWidget(self.label1)
        fileLayout.addWidget(self.fileLabel)
        postajaLayout = QtGui.QVBoxLayout()
        postajaLayout.addWidget(self.labelPostaja)
        postajaLayout.addWidget(self.comboPostaja)
        uredjajLayout = QtGui.QVBoxLayout()
        uredjajLayout.addWidget(self.labelUredjaj)
        uredjajLayout.addWidget(self.comboUredjaj)
        komponentaLayout = QtGui.QVBoxLayout()
        komponentaLayout.addWidget(self.labelKomponenta)
        komponentaLayout.addWidget(self.comboKomponenta)
        filterLayout = QtGui.QHBoxLayout()
        filterLayout.addLayout(postajaLayout)
        filterLayout.addLayout(uredjajLayout)
        filterLayout.addLayout(komponentaLayout)
        glavniLayout = QtGui.QVBoxLayout()
        glavniLayout.addLayout(fileLayout)
        glavniLayout.addLayout(filterLayout)
        glavniLayout.addWidget(self.tableView)
        self.setLayout(glavniLayout)

        #connections
        self.comboPostaja.currentIndexChanged.connect(self.filter_stanica)
        self.comboKomponenta.currentIndexChanged.connect(self.filter_komponenta)
        self.comboUredjaj.currentIndexChanged.connect(self.filter_uredjaj)
        self.tableView.clicked.connect(self.set_izabrani)


    def filter_stanica(self, x):
        s = str(self.comboPostaja.currentText())
        self.proksiModelPostaja.setFilterFixedString(s)
        self.tableView.update()

    def filter_komponenta(self, x):
        s = str(self.comboKomponenta.currentText())
        self.proksiModelKomponenta.setFilterFixedString(s)
        self.tableView.update()

    def filter_uredjaj(self, x):
        s = str(self.comboUredjaj.currentText())
        self.proksiModelUredjaj.setFilterFixedString(s)
        self.tableView.update()

    def set_izabrani(self, indeks):
        """
        lagana komplikacija... da bi dosao do indeksa moram transformirati indeks
        koji je trenutno izabran nazad kroz sve proxy modele
        """
        iuredjaj = self.proksiModelKomponenta.mapToSource(indeks)
        ipostaja = self.proksiModelUredjaj.mapToSource(iuredjaj)
        imodel = self.proksiModelPostaja.mapToSource(ipostaja)
        red = imodel.row()
        self.izbor = self.modelList[red]
        self.wizard().set_izbor(self.izbor)

    def initializePage(self):
        """
        Funkcija se poziva prilikom inicijalizacije stranice.
        Pokusaj automatskog pronalaska kombinacije stanice, uredjaja i komponente
        iz imena filea.
        """
        name = os.path.split(self.field('filepath'))[1]
        self.fileLabel.setText(name)
        name = name.lower()
        self.izbor = []
        #inicijalno bez filtera
        self.filter_stanica(self.postaje.index(''))
        self.filter_uredjaj(self.uredjaji.index(''))
        #pokusaj pronaci postaju u imenu filea
        for stanica in self.postaje:
            if stanica.lower() in name:
                ind = self.comboPostaja.findText(stanica)
                self.comboPostaja.setCurrentIndex(ind)
                break
        for uredjaj in self.uredjaji:
            if uredjaj.lower() in name:
                ind = self.comboUredjaj.findText(uredjaj)
                self.comboUredjaj.setCurrentIndex(ind)
                break
        ind = self.comboKomponenta.findText('')
        self.comboKomponenta.setCurrentIndex(ind)

    def validatePage(self):
        """
        provjeri da li je izabrana kombinacija postaja-uredjaj-komponenta
        """
        if self.comboUredjaj.count() == 1:
            msg = 'Nema uredjaja sa definiranim komponentama.'
            QtGui.QMessageBox.information(self, 'Problem.', msg)
            return False
        if not self.izbor:
            msg = 'Niste izabrali kombinaciju u tablici'
            QtGui.QMessageBox.information(self, 'Problem.', msg)
            return False
        return True
################################################################################
################################################################################
#TODO! stranica 3
class Page3Wizarda(QtGui.QWizardPage):
    def __init__(self, parent = None):
        """
        Stranica wizarda za izbor stupaca u ucitanom frejmu.
        """
        QtGui.QWizard.__init__(self, parent)
        self.setTitle('Stranica 3')
        self.setSubTitle('Izaberite komponente za pojedini stupac')

        self.tableView = QtGui.QTableView()
        self.tableView.setWordWrap(True)
        self.tableView.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)

        self.fileLabel = QtGui.QLabel('')
        self.fileLabel.setWordWrap(True)
        self.fileLabel.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                                     QtGui.QSizePolicy.Fixed)
        self.label1 = QtGui.QLabel('Datoteka :')


        fileLayout = QtGui.QHBoxLayout()
        fileLayout.addWidget(self.label1)
        fileLayout.addWidget(self.fileLabel)
        layout = QtGui.QVBoxLayout()
        layout.addLayout(fileLayout)
        layout.addWidget(self.tableView)
        self.setLayout(layout)

    def initializePage(self):
        """
        Funkcija se pokrece prilikom inicijalizacije stranice
        """
        name = os.path.split(self.field('filepath'))[1]
        self.fileLabel.setText(name)

        self.mjerenja = self.wizard().komponente
        self.path = self.field('filepath')
        izbor = self.wizard().izbor
        if len(izbor) == 3:
            uredjaj = izbor[1]
        else:
            uredjaj = ''

        txt = " ".join(['Izaberi komponente', uredjaj])
        self.setSubTitle(txt)
        try:
            self.df = self.read_csv_file(self.path)
            self.model = modeli.BaseFrejmModel(frejm=self.df)
            self.delegat = modeli.ComboBoxDelegate(stupci = self.mjerenja, parent=self.tableView)
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
        if len(izabraniStupci) == (len(self.mjerenja) - 1):
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
        self.setMogucih = set(self.mjerenja)
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

    def read_csv_file(self, path):
        """
        reader csv filea
        """
        frejm = pd.read_csv(path,
                            index_col=0,
                            parse_dates=[0],
                            dayfirst=True,
                            header=0,
                            sep=",",
                            encoding="iso-8859-1")
        return frejm
