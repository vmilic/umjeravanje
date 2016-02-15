# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 09:05:18 2016

@author: DHMZ-Milic
"""
import pickle
import logging
from PyQt4 import QtGui, QtCore, uic
from app.model.dokument import Uredjaj
from app.model.qt_models import ListModelUredjaj, TableModelKomponente


BASE_DIJALOG_UREDJAJ, FORM_DIJALOG_UREDJAJ = uic.loadUiType('./app/view/uiFiles/dijalog_uredjaj.ui')
class DijalogUredjaj(BASE_DIJALOG_UREDJAJ, FORM_DIJALOG_UREDJAJ):
    """
    Dijalog za editiranje uredjaja...
    """
    def __init__(self, dokument=None, parent=None):
        super(BASE_DIJALOG_UREDJAJ, self).__init__(parent)
        self.setupUi(self)
        tegla = pickle.loads(dokument)
        self.doc = tegla

        self.listaMetoda = self.doc.get_listu_analitickih_metoda()
        self.comboBoxMetoda.addItems(self.listaMetoda)

        self.aktivniUredjaj = None
        self.pushButtonIzbrisiUredjaj.setEnabled(False)
        self.enable_edit_widgets(check=False)

        self.model = ListModelUredjaj(dokument=tegla)
        self.listViewUredjaj.setModel(self.model)

        self.modelKomponenti = TableModelKomponente(dokument=tegla, uredjaj=self.aktivniUredjaj)
        self.tableViewKomponente.setModel(self.modelKomponenti)

        ### Setup signala i slotova ###
        self.setup_signal_connections()

    def get_dokument(self):
        tegla = pickle.dumps(self.doc)
        return tegla

    def setup_signal_connections(self):
        """Definiranje interakcije widgeta (spajanje signala i slotova."""
        self.listViewUredjaj.clicked.connect(self.select_aktivni_uredjaj)
        self.pushButtonDodajUredjaj.clicked.connect(self.add_uredjaj)
        self.pushButtonIzbrisiUredjaj.clicked.connect(self.remove_uredjaj)
        self.lineEditProizvodjac.textChanged.connect(self.edit_proizvodjac_uredjaj)
        self.lineEditOznakaModela.textChanged.connect(self.edit_oznakaModela_uredjaj)
        self.lineEditLokacija.textChanged.connect(self.edit_lokacija_uredjaj)
        self.comboBoxMetoda.currentIndexChanged.connect(self.promjena_metode)
        self.pushButtonDodajKomponentu.clicked.connect(self.dodaj_komponentu_uredjaju)
        self.pushButtonIzbrisiKomponentu.clicked.connect(self.remove_komponentu_uredjaju)

    def dodaj_komponentu_uredjaju(self):
        """Dodavanje komponente uredjaju."""
        lista = self.doc.get_listu_komponenti()
        formula, ok = QtGui.QInputDialog.getItem(self,
                                                 'Izbor komponente',
                                                 'Formula :',
                                                 lista,
                                                 editable=False)
        if ok:
            komponenta = self.doc.get_komponentu(formula)
            self.doc.get_uredjaj(self.aktivniUredjaj).dodaj_komponentu(komponenta)
            self.modelKomponenti.set_uredjaj(self.aktivniUredjaj)

    def remove_komponentu_uredjaju(self):
        """Brisanje komponente iz uredjaja."""
        selected = self.tableViewKomponente.selectedIndexes()
        if selected:
            red = selected[0].row()
            formula = self.modelKomponenti.get_formula(red)
            self.doc.get_uredjaj(self.aktivniUredjaj).izbrisi_komponentu(formula)
            self.modelKomponenti.set_uredjaj(self.aktivniUredjaj)

    def update_info_metode(self, idmetode):
        """Funkcija updatea prikaz vrijednosti parametara (Srz...) za izabranu
        metodu. Ulazni parametar je 'id' analiticke metode."""
        metoda = self.doc.get_analiticku_metodu(idmetode)
        self.labelID.setText(metoda.get_ID())
        self.labelMjernaJedinica.setText(metoda.get_jedinica())
        self.labelNaziv.setText(metoda.get_naziv())
        self.labelNorma.setText(metoda.get_norma())
        self.labelSrs.setText(str(metoda.get_Srs()))
        self.labelSrz.setText(str(metoda.get_Srz()))
        self.labelO.setText(str(metoda.get_o()))
        self.labelRmax.setText(str(metoda.get_rmax()))
        self.labelRz.setText(str(metoda.get_rz()))
        self.labelTr.setText(str(metoda.get_tr()))
        self.labelTf.setText(str(metoda.get_tf()))
        self.labelEcmin.setText(str(metoda.get_Ec_min()))
        self.labelEcmax.setText(str(metoda.get_Ec_max()))

    def promjena_metode(self, i):
        """Callback za promjenu vrijednosti comboboxa za izbor metode"""
        idmetode = self.comboBoxMetoda.currentText()
        self.update_info_metode(idmetode)
        #update uredjaj sa novom metodom
        ure = self.doc.get_uredjaj(self.aktivniUredjaj)
        met = self.doc.get_analiticku_metodu(idmetode)
        ure.set_analitickaMetoda(met)

    def edit_proizvodjac_uredjaj(self, value):
        """callback za edit proizvodjaca uredjaja"""
        try:
            value = str(value)
            ure = self.doc.get_uredjaj(self.aktivniUredjaj)
            ure.set_proizvodjac(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def edit_oznakaModela_uredjaj(self, value):
        """callback za edit oznake modela uredjaja"""
        try:
            value = str(value)
            ure = self.doc.get_uredjaj(self.aktivniUredjaj)
            ure.set_oznakaModela(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def edit_lokacija_uredjaj(self, value):
        """callback za edit lokacije uredjaja"""
        try:
            value = str(value)
            ure = self.doc.get_uredjaj(self.aktivniUredjaj)
            ure.set_lokacija(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def add_uredjaj(self):
        """Metoda dodaje novi uredjaj u dokument."""
        naziv, ok = QtGui.QInputDialog.getText(self,
                                               'Izbor naziva uredjaja',
                                               'Naziv : ')
        if ok:
            naziv = str(naziv)
            if len(naziv) == 0:
                msg = 'Naziv uredjaja nije zadan.'
                QtGui.QMessageBox.information(self, 'Problem', msg)
            elif naziv in self.doc.get_listu_dilucijskih_jedinica():
                msg = 'Uredjaj istog naziva vec postoji.'
                QtGui.QMessageBox.information(self, 'Problem', msg)
            else:
                ure = Uredjaj(serial=naziv)
                try:
                    popis = self.doc.get_listu_analitickih_metoda()
                    met = self.doc.get_analiticku_metodu(popis[0])
                    ure.set_analitickaMetoda(met)
                except Exception as err:
                    logging.warning(str(err), exc_info=True)
                self.doc.dodaj_uredjaj(naziv, ure)
                self.listViewUredjaj.clearSelection()
                self.aktivniUredjaj = None
                self.pushButtonIzbrisiUredjaj.setEnabled(False)
                self.enable_edit_widgets(check=False)
                self.model.refresh_model()

    def remove_uredjaj(self):
        """Metoda brise selektirani uredjaj iz dokumenta."""
        if self.aktivniUredjaj != None:
            self.doc.remove_uredjaj(self.aktivniUredjaj)
            self.listViewUredjaj.clearSelection()
            self.aktivniUredjaj = None
            self.pushButtonIzbrisiUredjaj.setEnabled(False)
            self.enable_edit_widgets(check=False)
            self.model.refresh_model()

    def select_aktivni_uredjaj(self, x):
        """
        Callback za izbor uredjaja sa liste
        """

        value = self.model.data(x, QtCore.Qt.DisplayRole)
        self.aktivniUredjaj = value
        self.pushButtonIzbrisiUredjaj.setEnabled(True)
        self.enable_edit_widgets(check=True)
        try:
            #komponente
            self.tableViewKomponente.clearSelection()
            self.modelKomponenti.set_uredjaj(self.aktivniUredjaj)
            self.tableViewKomponente.update()
            #postavke
            ure = self.doc.get_uredjaj(self.aktivniUredjaj)
            self.block_edit_signals(check=True)
            self.labelSerijskiBroj.setText(ure.get_serial())
            self.lineEditProizvodjac.setText(ure.get_proizvodjac())
            self.lineEditOznakaModela.setText(ure.get_oznakaModela())
            self.lineEditLokacija.setText(ure.get_lokacija())
            self.block_edit_signals(check=False)
            #metoda
            metoda = ure.get_analitickaMetoda()
            idmetode = metoda.get_ID()
            self.comboBoxMetoda.setCurrentIndex(self.comboBoxMetoda.findText(idmetode))
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def enable_edit_widgets(self, check=True):
        """
        Metoda sluzi za enable ili disable edit widgeta za postavke uredjaja
        """
        x = bool(check)
        self.lineEditProizvodjac.setEnabled(x)
        self.lineEditOznakaModela.setEnabled(x)
        self.lineEditLokacija.setEnabled(x)
        self.pushButtonDodajKomponentu.setEnabled(x)
        self.pushButtonIzbrisiKomponentu.setEnabled(x)
        self.tableViewKomponente.setEnabled(x)
        self.comboBoxMetoda.setEnabled(x)

    def block_edit_signals(self, check=True):
        """
        Metoda sluzi za block ili unblock edit signala za postavke uredjaja.
        """
        x = bool(check)
        self.lineEditProizvodjac.blockSignals(x)
        self.lineEditOznakaModela.blockSignals(x)
        self.lineEditLokacija.blockSignals(x)
        self.pushButtonDodajKomponentu.blockSignals(x)
        self.pushButtonIzbrisiKomponentu.blockSignals(x)
