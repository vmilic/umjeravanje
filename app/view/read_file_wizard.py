# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 12:15:30 2015

@author: DHMZ-Milic
"""
import os
import logging
import pandas as pd
from PyQt4 import QtGui, QtCore
import app.model.pomocne_funkcije as helperi

class CarobnjakZaCitanjeFilea(QtGui.QWizard):
    """
    Wizard dijalog klasa za ucitavanje fileova za umjeravanje
    """
    def __init__(self, parent=None, uredjaji=None, postaje=None):
        QtGui.QWizard.__init__(self, parent)
        logging.info('Inicijalizacija Wizada za citanje podataka')
        self.uredjaji = uredjaji
        self.postaje = postaje
        self.komponente = []
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
        postaja = str(self.P2.izabranaPostaja.text())
        if len(postaja) != 0:
            return postaja
        else:
            return 'None'

    def get_uredjaj(self):
        """
        Vrati izabrani uredjaj nakon uspjesnog izlaska iz wizarda.
        """
        uredjaj = str(self.P2.izabraniUredjaj.text())
        if len(uredjaj) != 0:
            return uredjaj
        else:
            return 'None'


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


class Page2Wizarda(QtGui.QWizardPage):
    """
    Stranica wizarda za izbor uredjaja. Prikazuje se padajuci izbornik
    sa svim serijskim brojevima uredjaja koji su zadani u configu.
    """
    def __init__(self, parent = None):
        QtGui.QWizard.__init__(self, parent)
        self.setTitle('Izbor uredjaja')
        self.setSubTitle('Provjeri izbor uredjaja prije nastavka.')
        # memberi
        self.uredjajInfo = self.parent().uredjaji
        self.postajaInfo = self.parent().postaje
        svePostaje = sorted(list(self.postajaInfo.keys()))
        # widgeti
        self.comboPostaje = QtGui.QComboBox()
        self.comboPostaje.addItems(svePostaje)
        self.labelPostaje = QtGui.QLabel('Postaja : ')
        self.izabranaPostaja = QtGui.QLineEdit()
        self.izabranaPostaja.setVisible(False)
        self.izabranaPostaja.setText(str(self.comboPostaje.currentText()))
        tmplist = self.postajaInfo[str(self.comboPostaje.currentText())]
        tmplist = [":::".join([item, str(self.uredjajInfo[item]['komponente'])])for item in tmplist]
        self.comboUredjaji = QtGui.QComboBox()
        self.comboUredjaji.addItems(tmplist)
        self.labelUredjaji = QtGui.QLabel('Uredjaj: ')
        self.izabraniUredjaj = QtGui.QLineEdit()
        self.izabraniUredjaj.setVisible(False)
        # layout
        layoutUredjaji = QtGui.QHBoxLayout()
        layoutPostaje = QtGui.QHBoxLayout()
        layout = QtGui.QVBoxLayout()
        layoutUredjaji.addWidget(self.labelUredjaji)
        layoutUredjaji.addWidget(self.comboUredjaji)
        layoutUredjaji.addWidget(self.izabraniUredjaj)
        layoutPostaje.addWidget(self.labelPostaje)
        layoutPostaje.addWidget(self.comboPostaje)
        layoutPostaje.addWidget(self.izabranaPostaja)
        layout.addLayout(layoutPostaje)
        layout.addLayout(layoutUredjaji)
        self.setLayout(layout)
        # povezivanje elemenata
        self.comboPostaje.currentIndexChanged.connect(self.promjeni_postaju)
        self.comboUredjaji.currentIndexChanged.connect(self.promjeni_uredjaj)
        self.registerField('uredjaj', self.izabraniUredjaj)
        self.registerField('postaja', self.izabranaPostaja)

    def initializePage(self):
        """
        Funkcija se poziva prilikom inicijalizacije stranice. Treba populirati
        comboboxeve i postaviti izbor
        """
        # parse name za serial... nadji postaju i uredjaj if possible
        serial = None
        lokacija = None
        msg = 'Pokusaj pronalaska uredjaja iz imena filea, ime={0}'.format(self.field('filepath'))
        logging.debug(msg)
        predlozeniUredjaji = helperi.parse_name_for_serial(self.field('filepath'))
        msg = 'Predlozene serijske oznake oredjaja iz imena datoteke, oznake={0}'.format(predlozeniUredjaji)
        logging.debug(msg)
        if len(predlozeniUredjaji) != 0:
            for i in predlozeniUredjaji:
                if i in self.uredjajInfo:
                    msg = 'Serijska oznaka pronadjena, oznaka={0}'.format(i)
                    logging.debug(msg)
                    serial = i
                    lokacija = self.uredjajInfo[i]['lokacija']
                    break
        else:
            logging.debug('Serijska oznaka nije pronadjena')
        # update combobox sa ponudjenim izborom
        if lokacija is not None and serial is not None:
            #self.init_izbornike(lokacija, serial)
            self.init_izbornike(lokacija,
                                ":::".join([serial, str(self.uredjajInfo[serial]['komponente'])]))

    def validatePage(self):
        """
        provjeri da li je izabran uredjaj
        """
        if self.comboUredjaji.count() == 0:
            msg = 'Na postoji nema uredjaja, izaberite drugu postaju.'
            QtGui.QMessageBox.information(self, 'Problem.', msg)
            return False
        serial = str(self.comboUredjaji.currentText())
        ind = serial.find(':::')
        serial = serial[:ind]
        if serial not in self.uredjajInfo:
            msg = 'Podaci o uredjaju ne postoje na REST-servisu.'
            QtGui.QMessageBox.information(self, 'Problem.', msg)
            return False
        else:
            if len(self.uredjajInfo[serial]['komponente']) == 0:
                msg = 'Uredjaj nema komponente mjerenja.'
                QtGui.QMessageBox.information(self, 'Problem.', msg)
                return False
        return True

    def init_izbornike(self, lokacija, serial):
        """
        Metoda je zaduzena za postavljanje inicijalnog izbora ako je iz filea
        uspjesno prepoznat neki uredjaj. Postavlja postaju i uredjaj.
        """
        ind = self.comboPostaje.findText(lokacija)
        self.comboPostaje.blockSignals(True)
        self.comboPostaje.setCurrentIndex(ind)
        self.comboPostaje.blockSignals(False)
        self.comboUredjaji.blockSignals(True)
        self.comboUredjaji.clear()
        tmplist = self.postajaInfo[lokacija]
        tmp = [":::".join([item, str(self.uredjajInfo[item]['komponente'])])for item in tmplist]
        self.comboUredjaji.addItems(tmp)
        ind = self.comboUredjaji.findText(serial)
        self.comboUredjaji.setCurrentIndex(ind)
        ind = serial.find(':::')
        serial = serial[:ind]
        listaKomponenti = self.uredjajInfo[serial]['komponente']
        self.wizard().set_komponente(listaKomponenti)
        self.comboUredjaji.blockSignals(False)
        self.izabranaPostaja.setText(str(lokacija))
        self.izabraniUredjaj.setText(str(serial))
        msg = 'Default izbor postavljen, postaja={0} , uredjaj={1}'.format(lokacija, serial)
        logging.debug(msg)

    def promjeni_postaju(self, x):
        """
        Promjena indeksa comboboxa sa postajama
        """
        lokacija = self.comboPostaje.currentText()
        self.comboUredjaji.blockSignals(True)
        self.comboUredjaji.clear()
        tmplist = self.postajaInfo[lokacija]
        tmp = [":::".join([item, str(self.uredjajInfo[item]['komponente'])])for item in tmplist]
        self.comboUredjaji.addItems(tmp)
        self.comboUredjaji.blockSignals(False)
        self.izabranaPostaja.setText(str(lokacija))
        msg = 'Promjena postaje, postaja={0}'.format(lokacija)
        logging.debug(msg)

    def promjeni_uredjaj(self, x):
        """
        Promjena indeksa comboboxa sa uredjajima
        """
        serial = self.comboUredjaji.currentText()
        ind = serial.find(':::')
        serial = serial[:ind]
        self.izabraniUredjaj.setText(str(serial))
        listaKomponenti = self.uredjajInfo[serial]['komponente']
        self.wizard().set_komponente(listaKomponenti)
        msg = 'Promjena uredjaja, uredjaj={0}'.format(serial)
        logging.debug(msg)


class Page3Wizarda(QtGui.QWizardPage):
    def __init__(self, parent = None):
        """
        Stranica wizarda za izbor stupaca u ucitanom frejmu.
        """
        QtGui.QWizard.__init__(self, parent)
        self.setTitle('Stranica 3')
        self.setSubTitle('Izaberite komponente')

        self.tableView = QtGui.QTableView()
        self.tableView.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.tableView.setWordWrap(True)
        #self.tableView.horizontalHeader().setVisible(False)
        self.tableView.setMouseTracking(True)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.tableView)
        self.setLayout(layout)

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

    def initializePage(self):
        """
        Funkcija se pokrece prilikom inicijalizacije stranice
        """
        self.mjerenja = self.wizard().komponente

        self.path = self.field('filepath')
        self.uredjaj = self.field('uredjaj')

        txt = " ".join(['Izaberi komponente', self.uredjaj])
        self.setSubTitle(txt)
        try:
            self.df = self.read_csv_file(self.path)
            self.model = BaseFrejmModel(frejm=self.df)
            self.delegat = ComboBoxDelegate(stupci = self.mjerenja, parent=self.tableView)
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


class ComboBoxDelegate(QtGui.QItemDelegate):
    def __init__(self, stupci=['None'], parent=None):
        QtGui.QItemDelegate.__init__(self, parent=parent)
        self.stupci = stupci

    def createEditor(self, parent, option, index):
        """
        return editor widget

        parent
        --> argument sluzi da stvoreni editor ne bude "garbage collected" (parent drzi referencu na njega)
        option
        --> Qt style opcije... nebitno (ali mora biti kao positional argument)
        index
        --> indeks elementa iz tablice (veza sa modelom)
        """
        editor = QtGui.QComboBox(parent=parent)
        editor.clear()
        editor.addItems(sorted(self.stupci))
        ind = editor.findText('None')
        editor.setCurrentIndex(ind)
        editor.setFocusPolicy(QtCore.Qt.StrongFocus)
        return editor

    def setEditorData(self, editor, index):
        """
        Inicijalizacija editora sa podacima, setup izgleda editora
        """
        pass

    def setModelData(self, editor, model, index):
        """
        Nakon kraja editiranja, metoda postavlja novo unesenu vrijednost u model
        """
        data = str(editor.currentText())
        model.setData(index, data)


class BaseFrejmModel(QtCore.QAbstractTableModel):
    """
    Definiranje qt modela za qt table view klase.
    Osnova modela ce biti pandas dataframe.
    Must reimplement:
        rowCount()
        columnCount()
        data()
        headerData()
    Implemented by default:
        parent()
        index()
    """
    def __init__(self, frejm=pd.DataFrame(), parent=None):
        """
        Initialize with pandas dataframe with data
        """
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.dataFrejm = frejm
        self.cols = ['None' for i in range(len(frejm.columns))]

    def rowCount(self, parent=QtCore.QModelIndex()):
        """
        MUST BE IMPLEMENTED.
        Return number of rows of pandas dataframe
        """
        return len(self.dataFrejm)+1
        #return min(15, len(self.dataFrejm))+1 #prikaz max 15 vrijednosti u tablici

    def columnCount(self, parent=QtCore.QModelIndex()):
        """
        MUST BE IMPLEMENTED
        Return number of columns of pandas dataframe. (add one for time index)
        """
        return len(self.dataFrejm.columns)

    def flags(self, index):
        """
        Flags each item in table as enabled and selectable
        """
        if index.isValid():
            if index.row() == 0:
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
            else:
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """
        must be enabled for editable models
        """
        if not index.isValid():
            return False

        row = index.row()
        col = index.column()
        if role == QtCore.Qt.EditRole and row == 0:
            self.cols[col] = str(value)
            """emit sigala da je doslo do promjene u modelu. View se nece
            updateati sve dokle god je fokus na comboboxu (smatra da editing
            nije gotov)."""
            self.dataChanged.emit(index, index)
            return True
        else:
            return False

    def data(self, index, role):
        """
        MUST BE IMPLEMENTED.
        Return value for each index and role
        """
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()
        if row == 0:
            if role == QtCore.Qt.DisplayRole:
                return self.cols[col]
        else:
            if role == QtCore.Qt.DisplayRole:
                return round(float(self.dataFrejm.iloc[row-1, col]),2)

    def headerData(self, section, orientation, role):
        """
        Sets the headers of the table...
        """
        if orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                if section == 0:
                    return 'Vrijeme'
                else:
                    return str(self.dataFrejm.index[section-1])
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return str(self.dataFrejm.columns[section])
