# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 09:10:18 2016

@author: DHMZ-Milic
"""
import pickle
import logging
from PyQt4 import QtGui, QtCore, uic
from app.model.dilucijska_jedinica import DilucijskaJedinica
from app.model.qt_models import ListModelDilucija

BASE_DIJALOG_DILUCIJA, FORM_DIJALOG_DILUCIJA = uic.loadUiType('./app/view/uiFiles/dijalog_dilucija.ui')
class DijalogDilucija(BASE_DIJALOG_DILUCIJA, FORM_DIJALOG_DILUCIJA):
    """
    Gui element glavnog prozora
    """
    def __init__(self, dokument=None, parent=None):
        super(BASE_DIJALOG_DILUCIJA, self).__init__(parent)
        self.setupUi(self)
        #instanca dokumenta
        tegla = pickle.loads(dokument)
        self.doc = tegla
        self.aktivnaDilucija = None #string kljuca
        self.pushButtonIzbrisi.setEnabled(False)
        self.enable_edit_widgets(check=False)
        #popunjavanje dijaloga za dodavanje dilucijskih jedinica
        self.model = ListModelDilucija(dokument=tegla)
        self.listViewDilucija.setModel(self.model)
        ### Setup signala i slotova ###
        self.setup_signal_connections()

    def get_dokument(self):
        tegla = pickle.dumps(self.doc)
        return tegla

    def setup_signal_connections(self):
        """Definiranje interakcije widgeta (spajanje signala i slotova."""
        self.listViewDilucija.clicked.connect(self.select_aktivnu_diluciju)
        self.lineEditModel.textChanged.connect(self.edit_model_dilucije)
        self.lineEditProizvodjac.textChanged.connect(self.edit_proizvodjac_dilucije)
        self.doubleSpinBoxSljedivost.valueChanged.connect(self.edit_sljedivost_dilucije)
        self.doubleSpinBoxNul.valueChanged.connect(self.edit_uNul_dilucije)
        self.doubleSpinBoxKal.valueChanged.connect(self.edit_uKal_dilucije)
        self.doubleSpinBoxOzon.valueChanged.connect(self.edit_uO3_dilucije)
        self.pushButtonDodaj.clicked.connect(self.add_diluciju)
        self.pushButtonIzbrisi.clicked.connect(self.remove_diluciju)

    def add_diluciju(self):
        """Metoda dodaje novu dilucijsku jedinicu u dokument."""
        naziv, ok = QtGui.QInputDialog.getText(self,
                                               'Izbor naziva kalibracijske jedinice',
                                               'Naziv : ')
        if ok:
            naziv = str(naziv)
            if len(naziv) == 0:
                msg = 'Naziv kalibracijske jedinice nije zadan.'
                QtGui.QMessageBox.information(self, 'Problem', msg)
            elif naziv in self.doc.get_listu_dilucijskih_jedinica():
                msg = 'Kalibracijska jedinica istog naziva vec postoji.'
                QtGui.QMessageBox.information(self, 'Problem', msg)
            else:
                jedinica = DilucijskaJedinica(model=naziv)
                self.doc.set_diluciju(naziv, jedinica)
                self.listViewDilucija.clearSelection()
                self.aktivnaDilucija = None
                self.pushButtonIzbrisi.setEnabled(False)
                self.enable_edit_widgets(check=False)
                self.model.refresh_model()

    def remove_diluciju(self):
        """Metoda brise selektiranu dilucijsku jedinicu iz dokumenta."""
        if self.aktivnaDilucija != None:
            self.doc.remove_diluciju(self.aktivnaDilucija)
            self.listViewDilucija.clearSelection()
            self.aktivnaDilucija = None
            self.pushButtonIzbrisi.setEnabled(False)
            self.enable_edit_widgets(check=False)
            self.model.refresh_model()

    def edit_sljedivost_dilucije(self, value):
        """Callback za promjenu sljedivosti dilucijske jedinice."""
        try:
            value = float(value)
            dilucija = self.doc.get_diluciju(self.aktivnaDilucija)
            dilucija.set_sljedivost(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def edit_model_dilucije(self, value):
        """Callback za promjenu naziva modela dilucijske jedinice."""
        try:
            value = str(value)
            dilucija = self.doc.get_diluciju(self.aktivnaDilucija)
            dilucija.set_model(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def edit_proizvodjac_dilucije(self, value):
        """Callback za promjenu proizvodjaca dilucijske jedinice."""
        try:
            value = str(value)
            dilucija = self.doc.get_diluciju(self.aktivnaDilucija)
            dilucija.set_proizvodjac(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def edit_uNul_dilucije(self, value):
        """Callback za promjenu U Nul plina dilucijske jedinice."""
        try:
            value = float(value)
            dilucija = self.doc.get_diluciju(self.aktivnaDilucija)
            dilucija.set_uNul(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def edit_uKal_dilucije(self, value):
        """Callback za promjenu U Kal plina dilucijske jedinice."""
        try:
            value = float(value)
            dilucija = self.doc.get_diluciju(self.aktivnaDilucija)
            dilucija.set_uKal(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def edit_uO3_dilucije(self, value):
        """Callback za promjenu U ozona dilucijske jedinice."""
        try:
            value = float(value)
            dilucija = self.doc.get_diluciju(self.aktivnaDilucija)
            dilucija.set_uO3(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def select_aktivnu_diluciju(self, x):
        """
        Callback za izbor dilucijske jedinice sa liste
        """
        value = self.model.data(x, QtCore.Qt.DisplayRole)
        self.aktivnaDilucija = value
        self.pushButtonIzbrisi.setEnabled(True)
        self.enable_edit_widgets(check=True)
        self.set_podatke_dilucije()
        self.model.layoutChanged.emit()

    def set_podatke_dilucije(self):
        """
        Setter stanja dilucijske jedinice u gui za izabranu dilucijsku jedinicu.
        """
        #block signale za editiranje postavki
        self.block_edit_signals(check=True)
        try:
            dilucija = self.doc.get_diluciju(self.aktivnaDilucija)
            self.lineEditModel.setText(dilucija.get_model())
            self.lineEditProizvodjac.setText(dilucija.get_proizvodjac())
            self.doubleSpinBoxNul.setValue(dilucija.get_uNul())
            self.doubleSpinBoxKal.setValue(dilucija.get_uKal())
            self.doubleSpinBoxOzon.setValue(dilucija.get_uO3())
            self.doubleSpinBoxSljedivost.setValue(dilucija.get_sljedivost())
        except Exception as err:
            logging.error(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))
            self.lineEditModel.setText('n/a')
            self.lineEditProizvodjac.setText('n/a')
            self.doubleSpinBoxNul.setValue(0.0)
            self.doubleSpinBoxKal.setValue(0.0)
            self.doubleSpinBoxOzon.setValue(0.0)
            self.doubleSpinBoxSljedivost.setValue(0.0)
        #unblock signale za editiranje postavki
        self.block_edit_signals(check=False)

    def enable_edit_widgets(self, check=True):
        """
        Metoda sluzi za enable ili disable edit widgeta za postavke jedinice
        """
        x = bool(check)
        self.lineEditModel.setEnabled(x)
        self.lineEditProizvodjac.setEnabled(x)
        self.doubleSpinBoxNul.setEnabled(x)
        self.doubleSpinBoxKal.setEnabled(x)
        self.doubleSpinBoxOzon.setEnabled(x)
        self.doubleSpinBoxSljedivost.setEnabled(x)

    def block_edit_signals(self, check=True):
        """
        Metoda sluzi za block ili unblock edit signala za postavke jedinice.
        """
        x = bool(check)
        self.lineEditModel.blockSignals(x)
        self.lineEditProizvodjac.blockSignals(x)
        self.doubleSpinBoxNul.blockSignals(x)
        self.doubleSpinBoxKal.blockSignals(x)
        self.doubleSpinBoxOzon.blockSignals(x)
        self.doubleSpinBoxSljedivost.blockSignals(x)
