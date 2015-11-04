# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 14:48:17 2015

@author: DHMZ-Milic
"""
import logging
from PyQt4 import QtGui
import app.model.frejm_model as modeli

#TODO! nije provjereno do kraja
class IzborNazivaStupacaWizard(QtGui.QWizard):
    """
    Wizard za 'izbor' stupaca frejma podataka preuzetih preko veze
    frejm --> frejm podataka
    moguci --> lista komponenti za taj uredjaj
    """
    def __init__(self, parent=None, frejm=None, moguci=None):
        QtGui.QWizard.__init__(self, parent)
        self.frejm = frejm
        self.moguci = moguci
        # opcije
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.setMinimumSize(600, 600)
        self.setWindowTitle("Postavke veze uredjaja")
        self.setOption(QtGui.QWizard.IndependentPages, on=False)
        # stranice wizarda
        self.izborStupaca = PageIzborStupaca(parent=self)
        self.setPage(1, self.izborStupaca)
        self.setStartId(1)

    def get_listu_stupaca(self):
        return self.moguci

class PageIzborStupaca(QtGui.QWizardPage):
    """Wizard za 'rename' stupaca """
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.setTitle('Definiranje komponenti')
        self.setSubTitle('Odaberi koji stupac u sirovim podacima odgovara kojoj komponenti')

        self.tableView = QtGui.QTableView()
        self.tableView.setWordWrap(True)
        self.tableView.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.tableView)
        self.setLayout(layout)

    def initializePage(self):
        """
        Funkcija se pokrece prilikom inicijalizacije stranice
        """
        self.frejm = self.wizard().frejm
        self.moguci = self.wizard().moguci
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
        #TODO! treba srediti validaciju podataka !!!
        izabraniStupci = [i for i in self.model.cols if i != 'None']
        izabraniStupci = [i for i in izabraniStupci if i != '']
        setIzabranih = set(izabraniStupci)
        print(setIzabranih)
        print(self.moguci)
        return True
#        if len(izabraniStupci) == (len(self.moguci) - 1):
#            if len(setIzabranih) == len(izabraniStupci):
#                return True
#            else:
#                msg = 'Isti naziv je koristen na vise stupaca. Naziv se smije koristiti samo jednom.'
#                QtGui.QMessageBox.information(self, 'Problem.', msg)
#                return False
#        else:
#            msg = 'Sve dozvoljene komponente moraju biti izabrane.'
#            QtGui.QMessageBox.information(self, 'Problem.', msg)
#            return False

    def dinamicki_update_opcija_comboa(self, ind):
        """
        Pomocna metoda za promjenu popisa itema unutar comboboxa. Na ovu metodu su
        spojeni svi comboboxevi i pozivaju ju prilikom promjene trenutno aktivnog
        indeksa.
        """
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
