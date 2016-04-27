# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 14:48:17 2015

@author: DHMZ-Milic
"""
import numpy as np
import logging
from PyQt4 import QtGui
import app.model.qt_models as modeli


class IzborNazivaStupacaWizard(QtGui.QWizard):
    """
    Wizard za 'izbor' stupaca frejma podataka preuzetih preko veze
    frejm --> frejm podataka
    moguci --> lista komponenti za taj uredjaj
    uredjaj --> serial uredjaja
    """
    def __init__(self, parent=None, frejm=None, moguci=None, uredjaj=None):
        QtGui.QWizard.__init__(self, parent)
        self.frejm = frejm
        self.uredjaj = uredjaj
        self.sekundniFrejm = self.frejm.copy()
        self.minutniFrejm = self.sekundniFrejm.resample('1min', how=np.average, closed='right', label='right')
        self.moguci = moguci
        # opcije
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.setMinimumSize(600, 600)
        self.setWindowTitle("Izbor naziva stupaca")
        self.setOption(QtGui.QWizard.IndependentPages, on=False)
        # stranice wizarda
        self.izborStupaca = PageIzborStupaca(parent=self)
        self.spremanjeFileova = PageSpremanjeFileova(parent=self)
        self.setPage(1, self.izborStupaca)
        self.setPage(2, self.spremanjeFileova)
        self.setStartId(1)

    def rename_stupce_frejmova(self, stupci=None):
        """
        Promjena naziva stupaca frejma. Parametar stupci su lista novih naziva
        """
        oldlist = list(self.sekundniFrejm.columns)
        tempmapa = dict(zip(oldlist, stupci))
        self.sekundniFrejm.rename(columns=tempmapa, inplace=True)
        self.minutniFrejm.rename(columns=tempmapa, inplace=True)

    def get_uredjaj(self):
        return self.uredjaj

    def get_sekundni_frejm(self):
        return self.sekundniFrejm

    def get_minutni_frejm(self):
        return self.minutniFrejm


class PageIzborStupaca(QtGui.QWizardPage):
    """Wizard page za 'rename' stupaca """
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent=parent)
        self.setTitle('Definiranje komponenti')
        self.setSubTitle('Odaberi koji stupac u sirovim podacima odgovara kojoj komponenti')
        self.tableView = QtGui.QTableView()
        self.deviceLabel = QtGui.QLabel()
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.deviceLabel)
        layout.addWidget(self.tableView)
        self.setLayout(layout)

    def initializePage(self):
        """
        Funkcija se pokrece prilikom inicijalizacije stranice
        """
        self.frejm = self.wizard().frejm
        self.moguci = self.wizard().moguci
        self.deviceLabel.setText('Izabrani uredjaj: {0}'.format(self.wizard().get_uredjaj().get_serial()))
        if 'None' not in self.moguci:
            self.moguci.append('None')
        try:
            self.model = modeli.BaseFrejmModel(frejm=self.frejm)
            self.delegat = modeli.ComboBoxDelegate(stupci=self.moguci, parent=self.tableView)
            self.tableView.setModel(self.model)
            self.tableView.setItemDelegateForRow(0, self.delegat)
            for col in range(len(self.frejm.columns)):
                self.tableView.openPersistentEditor(self.model.index(0, col))
                self.tableView.indexWidget(self.model.index(0, col)).currentIndexChanged.connect(self.dinamicki_update_opcija_comboa)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            msg = 'Error prilikom rada: {0}'.format(str(err))
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
        setMogucih = set(self.moguci)
        if len(izabraniStupci) == (len(setMogucih) - 1):
            if len(setIzabranih) == len(izabraniStupci):
                self.wizard().rename_stupce_frejmova(stupci=izabraniStupci)
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
        #potrebno je zapamitti promjenu
        self.setMogucih = set(self.moguci)
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


class PageSpremanjeFileova(QtGui.QWizardPage):
    """Wizard page za 'rename' stupaca """
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.setTitle('Spremanje podataka u csv file')
        self.setSubTitle('Ako želite, možete spremiti podatke u file. Moguće je prije spremanja usrednjiti podatke (minutni average).')

        self.sekundniTable = QtGui.QTableView()
        self.gumbSpremiSekundne = QtGui.QPushButton('Spremi...')
        self.minutniTable = QtGui.QTableView()
        self.gumbSpremiMinutne = QtGui.QPushButton('Spremi minutne...')

        #TODO! separator
        self.separatorLabel = QtGui.QLabel('Separator :')
        self.comboSeparator = QtGui.QComboBox()
        self.comboSeparator.addItems(['zarez', 'tocka-zarez', 'tab'])
        #TODO! encoding
        self.encodingLabel = QtGui.QLabel('Encoding :')
        self.comboEncoding = QtGui.QComboBox()
        self.comboEncoding.addItems(['utf-8', 'iso-8859-1'])
        #TODO! layout za opcije
        optionsLayout = QtGui.QHBoxLayout()
        optionsLayout.addWidget(self.separatorLabel)
        optionsLayout.addWidget(self.comboSeparator)
        optionsLayout.addWidget(self.encodingLabel)
        optionsLayout.addWidget(self.comboEncoding)
        optionsLayout.addStretch(-1)

        sekundniLayout = QtGui.QVBoxLayout()
        sekundniLayout.addWidget(self.gumbSpremiSekundne)
        sekundniLayout.addWidget(self.sekundniTable)

        minutniLayout = QtGui.QVBoxLayout()
        minutniLayout.addWidget(self.gumbSpremiMinutne)
        minutniLayout.addWidget(self.minutniTable)

        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addLayout(sekundniLayout)
        mainLayout.addLayout(minutniLayout)

        #top layout sa opcijama
        topLayout = QtGui.QVBoxLayout()
        topLayout.addLayout(optionsLayout)
        topLayout.addLayout(mainLayout)

        self.setLayout(topLayout)

        self.setup_connections()

    def get_enkoding_text(self):
        """getter separatora csv filea"""
        return self.comboEncoding.currentText()

    def get_separator_text(self):
        """getter tipa encodinga filea"""
        tekst = self.comboSeparator.currentText()
        if tekst == 'tab':
            separator = '\t'
        elif tekst == 'tocka-zarez':
            separator = ';'
        else:
            separator = ","
        return separator

    def initializePage(self):
        """
        Funkcija se pokrece prilikom inicijalizacije stranice
        """
        sekundniModel = modeli.BareFrameModel()
        sekundniModel.set_frejm(self.wizard().sekundniFrejm)
        self.sekundniTable.setModel(sekundniModel)
        minutniModel = modeli.BareFrameModel()
        minutniModel.set_frejm(self.wizard().minutniFrejm)
        self.minutniTable.setModel(minutniModel)

    def setup_connections(self):
        """widget communication"""
        self.gumbSpremiSekundne.clicked.connect(self.spremi_sekundne_u_csv)
        self.gumbSpremiMinutne.clicked.connect(self.spremi_minutne_u_csv)

    def spremi_sekundne_u_csv(self):
        filepath = QtGui.QFileDialog.getSaveFileName(parent=self,
                                                     caption='Spremi podatke u csv file',
                                                     filter='CSV file (*.csv);;all (*.*)')

        #TODO! sep and encoding choice
        separator = self.get_separator_text()
        enkoding = self.get_enkoding_text()

        if filepath:
            try:
                frejm = self.wizard().sekundniFrejm
                frejm.to_csv(filepath,
                             sep=separator,
                             float_format='%.4f',
                             date_format='%Y-%m-%d %H:%M:%S',
                             index_label='TIMESTAMP',
                             encoding=enkoding)
            except Exception as err:
                logging.error(str(err), exc_info=True)
                QtGui.QMessageBox.warning(self, 'Problem', 'File nije uspješno spremljen')
                pass
            else:
                QtGui.QMessageBox.information(self, 'Informacija', 'File je uspješno spremljen')

    def spremi_minutne_u_csv(self):
        filepath = QtGui.QFileDialog.getSaveFileName(parent=self,
                                                     caption='Spremi podatke u csv file',
                                                     filter='CSV file (*.csv);;all (*.*)')
        #TODO! sep and encoding choice
        separator = self.get_separator_text()
        enkoding = self.get_enkoding_text()

        if filepath:
            try:
                frejm = self.wizard().minutniFrejm
                frejm.to_csv(filepath,
                             sep=separator,
                             float_format='%.4f',
                             date_format='%Y-%m-%d %H:%M:%S',
                             index_label='TIMESTAMP',
                             encoding=enkoding)
            except Exception as err:
                logging.error(str(err), exc_info=True)
                QtGui.QMessageBox.warning(self, 'Problem', 'File nije uspješno spremljen')
                pass
            else:
                QtGui.QMessageBox.information(self, 'Informacija', 'File je uspješno spremljen')
