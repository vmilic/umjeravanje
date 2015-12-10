# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 12:15:30 2015

@author: DHMZ-Milic
"""
import os
import logging
import numpy as np
import pandas as pd
from PyQt4 import QtGui
import app.model.pomocne_funkcije as helperi
import app.model.frejm_model as modeli


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
        self.P4 = Page4Wizarda(parent=self)
        self.setPage(1, self.P1)
        self.setPage(2, self.P2)
        self.setPage(3, self.P3)
        self.setPage(4, self.P4)
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

    def get_frejmovi(self):
        """
        Metoda vraca mapu sa frejmovima podataka nakon uspjesnog izlaska iz wizarda.
        kljucevi su minutniPodaci, sekundniPodaci.
        """
        mapa = {}
        frejm = self.get_frejm()
        if self.P3.isMinutniPodaci():
            mapa['minutni'] = frejm
            mapa['sekundni'] = frejm
        else:
            minutni = frejm.resample('1min', how=np.average, closed='right', label='right')
            mapa['sekundni'] = frejm
            mapa['minutni'] = minutni
            print('stuff')
        return mapa

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

    def get_ckecked_tabove(self):
        """metoda odredjuje u koje tabove se spremaju preuzeti podaci"""
        output = {}
        for item in self.P4.listaCheckboxeva: #lista checkboxeva
            naziv = item.text()
            value = item.isChecked()
            output[naziv] = value
        return output


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

    @helperi.activate_wait_spinner
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


class Page2Wizarda(QtGui.QWizardPage):
    """
    Izbor postaje, uredjaja i komponente. Podaci su u modelu koji je "wrapan"
    u 3 proxy modela koji omogucavaju filtriranje za svaki od pojedinih stupaca.
    Filtriranje je uz pomoc comboboxeva. Izbor kombinacije je klikom na model.
    """
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.setTitle('Izbor uredjaja')
        msg = 'Izaberi kombinaciju, postaje uredjaja i komponente'
        self.setSubTitle(msg)
        #memberi
        pos = list(self.parent().setPostaja)
        ure = list(self.parent().setUredjaj)
        kom = list(self.parent().setKomponenta)
        pos.append('---')  #nedostatak izbora
        ure.append('---')
        kom.append('---')
        self.postaje = sorted(pos)
        self.uredjaji = sorted(ure)
        self.komponente = sorted(kom)
        self.modelList = self.parent().listaZaModel
        self.undoStack = []
        #widgets
        self.comboKomponenta = QtGui.QComboBox()
        self.comboPostaja = QtGui.QComboBox()
        self.comboUredjaj = QtGui.QComboBox()
        self.labelKomponenta = QtGui.QLabel('Komponenta')
        self.labelPostaja = QtGui.QLabel('Postaja')
        self.labelUredjaj = QtGui.QLabel('Uredjaj')
        self.tableView = QtGui.QTableView()
        self.fileLabel = QtGui.QLabel('')
        self.fileLabel.setWordWrap(True)
        self.fileLabel.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                                     QtGui.QSizePolicy.Fixed)
        self.label1 = QtGui.QLabel('Datoteka :')
        self.undoGumb = QtGui.QPushButton('Undo')
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
        comboLayout = QtGui.QHBoxLayout()
        comboLayout.addLayout(postajaLayout)
        comboLayout.addLayout(uredjajLayout)
        comboLayout.addLayout(komponentaLayout)
        undoLayout = QtGui.QHBoxLayout()
        undoLayout.addStretch()
        undoLayout.addWidget(self.undoGumb)
        glavniLayout = QtGui.QVBoxLayout()
        glavniLayout.addLayout(fileLayout)
        glavniLayout.addLayout(comboLayout)
        glavniLayout.addLayout(undoLayout)
        self.setLayout(glavniLayout)
        #connections
        self.comboUredjaj.currentIndexChanged.connect(self.promjena_uredjaja)
        self.comboPostaja.currentIndexChanged.connect(self.promjena_postaje)
        self.comboKomponenta.currentIndexChanged.connect(self.promjena_komponente)
        self.undoGumb.clicked.connect(self.undo_implementacija)

    @helperi.activate_wait_spinner
    def initializePage(self):
        """
        Funkcija se poziva prilikom inicijalizacije stranice.
        Pokusaj automatskog pronalaska kombinacije stanice, uredjaja i komponente
        iz imena filea.
        """
        self.undoStack.append(['---', '---', '---'])
        self.reset_combos()
        name = os.path.split(self.field('filepath'))[1]
        self.fileLabel.setText(name)
        predlozeniUredjaji = helperi.parse_name_for_serial(self.field('filepath'))
        predlozeni = '---'
        for uredjaj in self.uredjaji:
            if uredjaj in predlozeniUredjaji:
                predlozeni = uredjaj
                break
        self.comboUredjaj.setCurrentIndex(self.comboUredjaj.findText(predlozeni))

    def validatePage(self):
        """
        provjeri da li je izabrana kombinacija postaja-uredjaj-komponenta
        """
        postaja = self.comboPostaja.currentText()
        komponenta = self.comboKomponenta.currentText()
        uredjaj = self.comboUredjaj.currentText()
        self.izbor = [postaja, uredjaj, komponenta]
        if self.comboUredjaj.count() == 1:
            msg = 'Nema uredjaja sa definiranim komponentama.'
            QtGui.QMessageBox.information(self, 'Problem.', msg)
            return False
        if uredjaj == '---':
            msg = 'Niste izabrali uredjaj'
            QtGui.QMessageBox.information(self, 'Problem.', msg)
            return False
        if postaja == '---':
            msg = 'Niste izabrali postaju'
            QtGui.QMessageBox.information(self, 'Problem.', msg)
            return False
        if komponenta == '---':
            msg = 'Niste izabrali komponentu'
            QtGui.QMessageBox.information(self, 'Problem.', msg)
            return False
        self.wizard().set_izbor(self.izbor)
        return True

    def block_combo_signals(self):
        """
        Blokiranje signala svih comboboxeva
        """
        self.comboUredjaj.blockSignals(True)
        self.comboPostaja.blockSignals(True)
        self.comboKomponenta.blockSignals(True)

    def unblock_combo_signals(self):
        """
        Odblokiranje signala svih comboboxeva
        """
        self.comboUredjaj.blockSignals(False)
        self.comboPostaja.blockSignals(False)
        self.comboKomponenta.blockSignals(False)

    def reset_combos(self):
        """
        reset comboboxeva na inicijalno stanje (sve moguce vrijednosti)
        """
        self.block_combo_signals()
        self.comboKomponenta.clear()
        self.comboPostaja.clear()
        self.comboUredjaj.clear()
        self.comboKomponenta.addItems(self.komponente)
        self.comboPostaja.addItems(self.postaje)
        self.comboUredjaj.addItems(self.uredjaji)
        self.comboUredjaj.setCurrentIndex(self.comboUredjaj.findText('---'))
        self.comboPostaja.setCurrentIndex(self.comboPostaja.findText('---'))
        self.comboKomponenta.setCurrentIndex(self.comboKomponenta.findText('---'))
        self.unblock_combo_signals()

    def undo_implementacija(self):
        """
        implementacija undo na prethodni value
        """
        if len(self.undoStack) > 1:
            postaja, uredjaj, komponenta = self.undoStack.pop()
            self.reset_combos()
            self.block_combo_signals()
            self.comboPostaja.setCurrentIndex(self.comboPostaja.findText(postaja))
            self.comboUredjaj.setCurrentIndex(self.comboUredjaj.findText(uredjaj))
            self.comboKomponenta.setCurrentIndex(self.comboKomponenta.findText(komponenta))
            self.unblock_combo_signals()

    def promjena_postaje(self, x):
        """
        promjena postaje u comboboxu
        """
        #trenutno stanje
        postaja = self.comboPostaja.currentText()
        komponenta = self.comboKomponenta.currentText()
        uredjaj = self.comboUredjaj.currentText()
        if postaja == '---':
            self.reset_combos()
            self.undoStack.append(['---', '---', '---'])
        else:
            moguci = [k for k in self.modelList if postaja in k]
            if uredjaj != '---':
                moguci = [k for k in moguci if uredjaj in k]
            if komponenta != '---':
                moguci = [k for k in moguci if komponenta in k]
            if len(moguci) == 1:
                ure = moguci[0][1]
                kom = moguci[0][2]
                self.block_combo_signals()
                self.comboUredjaj.clear()
                self.comboKomponenta.clear()
                self.comboUredjaj.addItems(['---', ure])
                self.comboKomponenta.addItems(['---', kom])
                self.comboUredjaj.setCurrentIndex(self.comboUredjaj.findText(ure))
                self.comboKomponenta.setCurrentIndex(self.comboKomponenta.findText(kom))
                self.unblock_combo_signals()
            else:
                moguciUredjaji = [k[1] for k in moguci]
                moguceKomponente = [k[2] for k in moguci]
                moguciUredjaji.append('---')
                moguceKomponente.append('---')
                moguciUredjaji = sorted(list(set(moguciUredjaji)))
                moguceKomponente = sorted(list(set(moguceKomponente)))
                self.block_combo_signals()
                self.comboUredjaj.clear()
                self.comboKomponenta.clear()
                self.comboUredjaj.addItems(moguciUredjaji)
                self.comboKomponenta.addItems(moguceKomponente)
                if uredjaj in moguciUredjaji:
                    self.comboUredjaj.setCurrentIndex(self.comboUredjaj.findText(uredjaj))
                else:
                    self.comboUredjaj.setCurrentIndex(self.comboUredjaj.findText('---'))
                if komponenta in moguceKomponente:
                    self.comboKomponenta.setCurrentIndex(self.comboKomponenta.findText(komponenta))
                else:
                    self.comboKomponenta.setCurrentIndex(self.comboKomponenta.findText('---'))
                self.unblock_combo_signals()
            postaja = self.comboPostaja.currentText()
            uredjaj = self.comboUredjaj.currentText()
            komponenta = self.comboKomponenta.currentText()
            self.undoStack.append([postaja, uredjaj, komponenta])


    def promjena_uredjaja(self, x):
        """
        promjena uredjaja u comboboxu
        """
        #trenutno stanje
        postaja = self.comboPostaja.currentText()
        komponenta = self.comboKomponenta.currentText()
        uredjaj = self.comboUredjaj.currentText()
        if uredjaj == '---':
            self.reset_combos()
            self.undoStack.append(['---', '---', '---'])
        else:
            moguci = [k for k in self.modelList if uredjaj in k]
            postaja = moguci[0][0] #uredjaj ima samo jednu postaju
            if len(moguci) == 1:
                kom = moguci[0][2]
                self.block_combo_signals()
                self.comboPostaja.clear()
                self.comboKomponenta.clear()
                self.comboPostaja.addItems(['---', postaja])
                self.comboKomponenta.addItems(['---', kom])
                self.comboPostaja.setCurrentIndex(self.comboPostaja.findText(postaja))
                self.comboKomponenta.setCurrentIndex(self.comboKomponenta.findText(kom))
                self.unblock_combo_signals()
            else:
                mogucePostaje = ['---', postaja]
                moguceKomponente = [k[2] for k in moguci]
                moguceKomponente.append('---')
                moguceKomponente = sorted(list(set(moguceKomponente)))
                self.block_combo_signals()
                self.comboPostaja.clear()
                self.comboKomponenta.clear()
                self.comboPostaja.addItems(mogucePostaje)
                self.comboKomponenta.addItems(moguceKomponente)
                self.comboPostaja.setCurrentIndex(self.comboPostaja.findText(postaja))
                if komponenta in moguceKomponente:
                    self.comboKomponenta.setCurrentIndex(self.comboKomponenta.findText(komponenta))
                else:
                    self.comboKomponenta.setCurrentIndex(self.comboKomponenta.findText('---'))
                self.unblock_combo_signals()
            postaja = self.comboPostaja.currentText()
            uredjaj = self.comboUredjaj.currentText()
            komponenta = self.comboKomponenta.currentText()
            self.undoStack.append([postaja, uredjaj, komponenta])

    def promjena_komponente(self, x):
        """
        promjena komponente u comboboxu
        """
        #trenutno stanje
        postaja = self.comboPostaja.currentText()
        komponenta = self.comboKomponenta.currentText()
        uredjaj = self.comboUredjaj.currentText()
        if komponenta == '---':
            self.reset_combos()
            self.undoStack.append(['---', '---', '---'])
        else:
            moguci = [k for k in self.modelList if komponenta in k]
            if uredjaj != '---':
                moguci = [k for k in moguci if uredjaj in k]
            if postaja != '---':
                moguci = [k for k in moguci if postaja in k]
            if len(moguci) == 1:
                pos = moguci[0][0]
                ure = moguci[0][1]
                self.block_combo_signals()
                self.comboUredjaj.clear()
                self.comboPostaja.clear()
                self.comboUredjaj.addItems(['---', ure])
                self.comboPostaja.addItems(['---', pos])
                self.comboUredjaj.setCurrentIndex(self.comboUredjaj.findText(ure))
                self.comboPostaja.setCurrentIndex(self.comboPostaja.findText(pos))
                self.unblock_combo_signals()
            else:
                moguciUredjaji = [k[1] for k in moguci]
                mogucePostaje = [k[0] for k in moguci]
                moguciUredjaji.append('---')
                mogucePostaje.append('---')
                moguciUredjaji = sorted(list(set(moguciUredjaji)))
                mogucePostaje = sorted(list(set(mogucePostaje)))
                self.block_combo_signals()
                self.comboUredjaj.clear()
                self.comboPostaja.clear()
                self.comboUredjaj.addItems(moguciUredjaji)
                self.comboPostaja.addItems(mogucePostaje)
                if uredjaj in moguciUredjaji:
                    self.comboUredjaj.setCurrentIndex(self.comboUredjaj.findText(uredjaj))
                else:
                    self.comboUredjaj.setCurrentIndex(self.comboUredjaj.findText('---'))
                if postaja in mogucePostaje:
                    self.comboPostaja.setCurrentIndex(self.comboPostaja.findText(postaja))
                else:
                    self.comboPostaja.setCurrentIndex(self.comboPostaja.findText('---'))
                self.unblock_combo_signals()
            postaja = self.comboPostaja.currentText()
            uredjaj = self.comboUredjaj.currentText()
            komponenta = self.comboKomponenta.currentText()
            self.undoStack.append([postaja, uredjaj, komponenta])


class Page3Wizarda(QtGui.QWizardPage):
    def __init__(self, parent = None):
        """
        Stranica wizarda za izbor stupaca u ucitanom frejmu.
        """
        QtGui.QWizard.__init__(self, parent)
        self.setTitle('Stranica 3')
        self.setSubTitle('Izaberite komponente za pojedini stupac. Odaberite da li su podaci prethodno minutno usrednjeni.')

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
        self.minutniRadio.toggle()

        boxlayout = QtGui.QHBoxLayout()
        boxlayout.addWidget(self.minutniRadio)
        boxlayout.addWidget(self.sekundniRadio)
        self.box.setLayout(boxlayout)

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

    @helperi.activate_wait_spinner
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

class Page4Wizarda(QtGui.QWizardPage):
    def __init__(self, parent=None):
        """
        Stranica wizarda za izbor stupaca u ucitanom frejmu.
        """
        QtGui.QWizard.__init__(self, parent)
        self.setTitle('Stranica 4')
        self.setSubTitle('Izaberite gdje ce se koristiti preuzeti podaci.')

        self.lay = QtGui.QVBoxLayout()
        self.setLayout(self.lay)

    @helperi.activate_wait_spinner
    def initializePage(self):
        """
        Funkcija se pokrece prilikom inicijalizacije stranice
        """
        frejm = self.wizard().get_frejm()
        stupci = list(frejm.columns)

        self.listaCheckboxeva = []

        for stupac in stupci:
            self.listaCheckboxeva.append(QtGui.QCheckBox(stupac))
            name = stupac+'-odaziv'
            self.listaCheckboxeva.append(QtGui.QCheckBox(name))
        self.listaCheckboxeva.append(QtGui.QCheckBox('konverter'))

        for item in self.listaCheckboxeva:
            self.lay.addWidget(item)
            item.setChecked(True)


