# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 14:48:17 2015

@author: DHMZ-Milic
"""
import numpy as np
import logging
from PyQt4 import QtGui
import app.model.frejm_model as modeli


class IzborNazivaStupacaWizard(QtGui.QWizard):
    """
    Wizard za 'izbor' stupaca frejma podataka preuzetih preko veze
    frejm --> frejm podataka
    moguci --> lista komponenti za taj uredjaj
    """
    def __init__(self, parent=None, frejm=None, moguci=None):
        QtGui.QWizard.__init__(self, parent)
        self.frejm = frejm
        self.sekundniFrejm = self.frejm.copy()
        self.minutniFrejm = self.sekundniFrejm.resample('1min', how=np.average, closed='right', label='right')
        self.moguci = moguci
        self.izbor = True #TODO!

        # opcije
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.setMinimumSize(600, 600)
        self.setWindowTitle("Postavke veze uredjaja")
        self.setOption(QtGui.QWizard.IndependentPages, on=False)
        # stranice wizarda
        self.izborStupaca = PageIzborStupaca(parent=self)
        self.sekundniToCsv = PageSekundniToCsv(parent=self)
        self.minutniToCsv = PageMinutniToCsv(parent=self)
        self.prebaciData = PagePrebaciData(parent=self)
        self.setPage(1, self.izborStupaca)
        self.setPage(2, self.sekundniToCsv)
        self.setPage(3, self.minutniToCsv)
        self.setPage(4, self.prebaciData)
        self.setStartId(1)

    def rename_stupce_frejmova(self, stupci=None):
        """
        Promjena naziva stupaca frejma. Parametar stupci su lista novih naziva
        """
        oldlist = list(self.sekundniFrejm.columns)
        tempmapa = dict(zip(oldlist, stupci))
        self.sekundniFrejm.rename(columns=tempmapa, inplace=True)
        self.minutniFrejm.rename(columns=tempmapa, inplace=True)

    def get_listu_stupaca(self):
        return self.moguci

    def get_sekundni_frejm(self):
        return self.sekundniFrejm

    def get_minutni_frejm(self):
        return self.minutniFrejm

    def get_ckecked_tabove(self):
        """metoda odredjuje u koje tabove se spremaju preuzeti podaci"""
        output = {}
        for item in self.prebaciData.listaCheckboxeva: #lista checkboxeva
            naziv = item.text()
            value = item.isChecked()
            output[naziv] = value
        return output


class PageSekundniToCsv(QtGui.QWizardPage):
    """wizard page za spremanje sirovih podataka u csv file"""
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.setTitle('Spremi sekundne podatke u csv file')
        self.setSubTitle('Ako želite, pritisnte gumb za spremanje i zatim spremite podatke uz pomoc file dijaloga')

        self.gumbSpremi = QtGui.QPushButton('Spremi sekundne podatke')

        self.tableView = QtGui.QTableView()

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.tableView)
        layout.addWidget(self.gumbSpremi)
        self.setLayout(layout)

        self.gumbSpremi.clicked.connect(self.spremi_sekundne_u_csv)

    def initializePage(self):
        self.sekfrejm = self.wizard().sekundniFrejm
        self.model = modeli.BareFrameModel()
        self.model.set_frejm(self.sekfrejm)
        self.tableView.setModel(self.model)

    def spremi_sekundne_u_csv(self):
        filepath = QtGui.QFileDialog.getSaveFileName(parent=self,
                                                     caption='Spremi podatke u csv file',
                                                     filter='CSV file (*.csv);;all (*.*)')
        if filepath:
            try:
                self.sekfrejm.to_csv(filepath,
                                     sep=',',
                                     encoding='utf-8')
            except Exception as err:
                logging.error(str(err), exc_info=True)
                QtGui.QMessageBox.warning(self, 'Problem', 'File nije uspjesno spremljen')
                pass
            else:
                QtGui.QMessageBox.information(self, 'Informacija', 'File je uspjesno spremljen')


class PageMinutniToCsv(QtGui.QWizardPage):
    """wizard page za spremanje minutno usrednjenih podataka u csv file"""
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.setTitle('Spremi minutno usrednjene podatke u csv file')
        self.setSubTitle('Ako želite, pritisnte gumb za spremanje i zatim spremite podatke uz pomoc file dijaloga')

        self.gumbSpremi = QtGui.QPushButton('Spremi usrednjene podatke')

        self.tableView = QtGui.QTableView()

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.tableView)
        layout.addWidget(self.gumbSpremi)
        self.setLayout(layout)

        self.gumbSpremi.clicked.connect(self.spremi_minutne_u_csv)

    def initializePage(self):
        self.minfrejm = self.wizard().minutniFrejm
        self.model = modeli.BareFrameModel()
        self.model.set_frejm(self.minfrejm)
        self.tableView.setModel(self.model)

    def spremi_minutne_u_csv(self):
        filepath = QtGui.QFileDialog.getSaveFileName(parent=self,
                                                     caption='Spremi podatke u csv file',
                                                     filter='CSV file (*.csv);;all (*.*)')
        if filepath:
            try:
                self.minfrejm.to_csv(filepath,
                                     sep=',',
                                     encoding='utf-8')
            except Exception as err:
                logging.error(str(err), exc_info=True)
                QtGui.QMessageBox.warning(self, 'Problem', 'File nije uspjesno spremljen')
                pass
            else:
                QtGui.QMessageBox.information(self, 'Informacija', 'File je uspjesno spremljen')



class PageIzborStupaca(QtGui.QWizardPage):
    """Wizard page za 'rename' stupaca """
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.setTitle('Definiranje komponenti')
        self.setSubTitle('Odaberi koji stupac u sirovim podacima odgovara kojoj komponenti')

        self.tableView = QtGui.QTableView()
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.tableView)
        self.setLayout(layout)

    def initializePage(self):
        """
        Funkcija se pokrece prilikom inicijalizacije stranice
        """
        self.frejm = self.wizard().frejm
        self.moguci = self.wizard().moguci
        if 'None' not in self.moguci:
            self.moguci.append('None')

        try:
            self.model = modeli.BaseFrejmModel(frejm=self.frejm)
            self.delegat = modeli.ComboBoxDelegate(stupci = self.moguci, parent=self.tableView)
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

class PagePrebaciData(QtGui.QWizardPage):
    """Wizard page za prebacivanje podataka u 'aktivno stanje' za rad sa podacima"""
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.setTitle('Prebacivanje preuzetih podataka u radni dio aplikacije')
        tekst = ['Izaberite u koje tabove treba prebaciti podatke.',
                 'U tabove za mjerenje i provjeru konvertera spremaju se minutno usrednjeni podaci.',
                 'U tabove za provjeru odaziva spremaju se sekundni podaci.']
        t = ' '.join(tekst)
        self.setSubTitle(t)

        self.lay = QtGui.QVBoxLayout()
        self.setLayout(self.lay)

    def initializePage(self):
        """
        Funkcija se pokrece prilikom inicijalizacije stranice
        """
        stupci = self.wizard().get_listu_stupaca()
        if 'None' in stupci:
            stupci.remove('None')

        self.listaCheckboxeva = []

        for stupac in stupci:
            self.listaCheckboxeva.append(QtGui.QCheckBox(stupac))
            name = stupac+'-odaziv'
            self.listaCheckboxeva.append(QtGui.QCheckBox(name))
        self.listaCheckboxeva.append(QtGui.QCheckBox('konverter'))

        for item in self.listaCheckboxeva:
            self.lay.addWidget(item)
            item.setChecked(True)
