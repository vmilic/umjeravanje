# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 15:17:36 2016

@author: DHMZ-Milic
"""
import pickle
import logging
from PyQt4 import QtGui, uic
from app.model.komponenta import Komponenta
from app.model.qt_models import ListModelKomponente

BASE_DIJALOG_KOMPONENTE, FORM_DIJALOG_KOMPONENTE = uic.loadUiType('./app/view/uiFiles/dijalog_komponenta.ui')
class DijalogKomponenta(BASE_DIJALOG_KOMPONENTE, FORM_DIJALOG_KOMPONENTE):
    """
    Dijalog za pregled i dodavanje novih komponenti
    """
    def __init__(self, dokument=None, parent=None):
        super(BASE_DIJALOG_KOMPONENTE, self).__init__(parent)
        self.setupUi(self)
        tegla = pickle.loads(dokument)
        self.doc = tegla

        self.aktivnaKomponenta = None

        self.model = ListModelKomponente(dokument=tegla)
        self.listViewKomponente.setModel(self.model)

        ### Setup signala i slotova ###
        self.setup_signal_connections()

    def get_dokument(self):
        tegla = pickle.dumps(self.doc)
        return tegla

    def setup_signal_connections(self):
        """Definiranje interakcije widgeta (spajanje signala i slotova."""
        self.listViewKomponente.clicked.connect(self.select_aktivnu_komponentu)
        self.pushButtonDodaj.clicked.connect(self.dodaj_komponentu_u_dokument)
        self.lineEditNaziv.textChanged.connect(self.edit_naziv)
        self.lineEditJedinica.textChanged.connect(self.edit_jedinica)
        self.doubleSpinBoxKv.valueChanged.connect(self.edit_kv)

    def edit_kv(self, x):
        """Callback za promjenu konverzijskog volumena komponente"""
        try:
            value = float(x)
            komponenta = self.doc.get_komponentu(self.aktivnaKomponenta)
            komponenta.set_kv(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def edit_naziv(self, x):
        """Callback za promjenu naziva komponente."""
        try:
            value = str(x)
            komponenta = self.doc.get_komponentu(self.aktivnaKomponenta)
            komponenta.set_naziv(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def edit_jedinica(self, x):
        """Callback za promjenu mjerne_jedinice komponente."""
        try:
            value = str(x)
            komponenta = self.doc.get_komponentu(self.aktivnaKomponenta)
            komponenta.set_jedinica(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def set_podatke_komponente(self):
        """
        Setter stanja dilucijske jedinice u gui za izabranu analiticku metodu.
        """
        #block signale za editiranje postavki
        self.block_edit_signals(check=True)
        try:
            komponenta = self.doc.get_komponentu(self.aktivnaKomponenta)
            self.labelFormula.setText(komponenta.get_formula())
            self.lineEditNaziv.setText(komponenta.get_naziv())
            self.lineEditJedinica.setText(komponenta.get_jedinica())
            self.doubleSpinBoxKv.setValue(komponenta.get_kv())
        except Exception as err:
            logging.error(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))
            self.lineEditNaziv.setText('n/a')
            self.lineEditFormula.setText('n/a')
            self.lineEditJedinica.setText('n/a')
            self.doubleSpinBoxKv.setValue(1.0)
        #unblock signale za editiranje postavki
        self.block_edit_signals(check=False)

    def select_aktivnu_komponentu(self, x):
        """callback za izbor metode iz liste"""
        key = self.model.vrati_kljuc_indeksa(x)
        self.aktivnaKomponenta = key
        self.enable_edit_widgets(check=True)
        self.set_podatke_komponente()
        self.model.layoutChanged.emit()

    def dodaj_komponentu_u_dokument(self):
        """dodavanje nove komponente"""
        formula, ok = QtGui.QInputDialog.getText(self,
                                                 'Izbor formule komponente',
                                                 'Formula : ')
        if ok:
            formula = str(formula)
            if formula in self.doc.get_listu_komponenti():
                QtGui.QMessageBox.warning(self, 'Upozorenje', 'Komponenta sa istom formulom vec postoji.')
                return None
            elif len(formula) == 0:
                QtGui.QMessageBox.warning(self, 'Upozorenje', 'Formula nije zadana.')
            else:
                komp = Komponenta(formula=formula)
                self.doc.set_novu_komponentu(formula, komp)
                self.model.layoutChanged.emit()

    def enable_edit_widgets(self, check=True):
        """
        Metoda sluzi za enable ili disable edit widgeta za postavke metode.
        """
        x = bool(check)
        self.lineEditNaziv.setEnabled(x)
        self.lineEditJedinica.setEnabled(x)
        self.doubleSpinBoxKv.setEnabled(x)

    def block_edit_signals(self, check=True):
        """
        Metoda sluzi za block ili unblock edit signala za postavke metode.
        """
        x = bool(check)
        self.lineEditNaziv.blockSignals(x)
        self.lineEditJedinica.blockSignals(x)
        self.doubleSpinBoxKv.blockSignals(x)
