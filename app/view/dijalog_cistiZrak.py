# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 14:41:14 2016

@author: DHMZ-Milic
"""
import pickle
import logging
from PyQt4 import QtGui, QtCore, uic
from app.model.generator_cistog_zraka import GeneratorCistogZraka
from app.model.qt_models import ListModelCistiZrak

BASE_DIJALOG_CISTIZRAK, FORM_DIJALOG_CISTIZRAK = uic.loadUiType('./app/view/uiFiles/dijalog_cistiZrak.ui')
class DijalogCistiZrak(BASE_DIJALOG_CISTIZRAK, FORM_DIJALOG_CISTIZRAK):
    """
    Gui element glavnog prozora
    """
    def __init__(self, dokument=None, parent=None):
        super(BASE_DIJALOG_CISTIZRAK, self).__init__(parent)
        self.setupUi(self)
        #instanca dokumenta
        tegla = pickle.loads(dokument)
        self.doc = tegla #TODO!
        self.aktivniZrak = None #string kljuca
        self.pushButtonIzbrisi.setEnabled(False)
        self.enable_edit_widgets(check=False)
        #popunjavanje dijaloga za dodavanje dilucijskih jedinica
        self.model = ListModelCistiZrak(dokument=tegla)
        self.listViewCistiZrak.setModel(self.model)

        ### Setup signala i slotova ###
        self.setup_signal_connections()

    def get_dokument(self):
        tegla = pickle.dumps(self.doc)
        return tegla

    def setup_signal_connections(self):
        self.listViewCistiZrak.clicked.connect(self.select_aktivni_zrak)
        self.pushButtonDodaj.clicked.connect(self.add_zrak)
        self.pushButtonIzbrisi.clicked.connect(self.remove_zrak)
        self.lineEditModel.textChanged.connect(self.edit_model_zrak)
        self.lineEditProizvodjac.textChanged.connect(self.edit_proizvodjac_zrak)
        self.doubleSpinBoxSO2.valueChanged.connect(self.edit_SO2_zrak)
        self.doubleSpinBoxNOx.valueChanged.connect(self.edit_NOx_zrak)
        self.doubleSpinBoxCO.valueChanged.connect(self.edit_CO_zrak)
        self.doubleSpinBoxO3.valueChanged.connect(self.edit_O3_zrak)
        self.doubleSpinBoxBTX.valueChanged.connect(self.edit_BTX_zrak)

    def add_zrak(self):
        """Metoda dodaje novi generator cistog zraka u dokument."""
        naziv, ok = QtGui.QInputDialog.getText(self,
                                               'Izbor naziva generatora cistog zraka',
                                               'Naziv : ')
        if ok:
            naziv = str(naziv)
            if len(naziv) == 0:
                msg = 'Naziv generatora cistog zraka nije zadan.'
                QtGui.QMessageBox.information(self, 'Problem', msg)
            elif naziv in self.doc.get_listu_dilucijskih_jedinica():
                msg = 'Generator cistog zraka istog naziva vec postoji.'
                QtGui.QMessageBox.information(self, 'Problem', msg)
            else:
                zrak = GeneratorCistogZraka(model=naziv)
                self.doc.set_cistiZrak(naziv, zrak)
                self.listViewCistiZrak.clearSelection()
                self.aktivniZrak = None
                self.pushButtonIzbrisi.setEnabled(False)
                self.enable_edit_widgets(check=False)
                self.model.refresh_model()

    def remove_zrak(self):
        """Metoda brise selektirani generator cistog zraka iz dokumenta."""
        if self.aktivniZrak != None:
            self.doc.remove_cistiZrak(self.aktivniZrak)
            self.listViewCistiZrak.clearSelection()
            self.aktivniZrak = None
            self.pushButtonIzbrisi.setEnabled(False)
            self.enable_edit_widgets(check=False)
            self.model.refresh_model()

    def edit_model_zrak(self, x):
        """Callback za promjenu naziva modela generatora cistog zraka."""
        try:
            value = str(x)
            zrak = self.doc.get_cistiZrak(self.aktivniZrak)
            zrak.set_model(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def edit_proizvodjac_zrak(self, x):
        """Callback za promjenu naziva proizvodjaca generatora cistog zraka."""
        try:
            value = str(x)
            zrak = self.doc.get_cistiZrak(self.aktivniZrak)
            zrak.set_proizvodjac(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def edit_SO2_zrak(self, x):
        """Callback za promjenu naziva maxSO2 generatora cistog zraka."""
        try:
            value = float(x)
            zrak = self.doc.get_cistiZrak(self.aktivniZrak)
            zrak.set_maxSO2(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def edit_NOx_zrak(self, x):
        """Callback za promjenu naziva maxNOx generatora cistog zraka."""
        try:
            value = float(x)
            zrak = self.doc.get_cistiZrak(self.aktivniZrak)
            zrak.set_maxNOx(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def edit_CO_zrak(self, x):
        """Callback za promjenu naziva maxCO generatora cistog zraka."""
        try:
            value = float(x)
            zrak = self.doc.get_cistiZrak(self.aktivniZrak)
            zrak.set_maxCO(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def edit_O3_zrak(self, x):
        """Callback za promjenu naziva maxO3 generatora cistog zraka."""
        try:
            value = float(x)
            zrak = self.doc.get_cistiZrak(self.aktivniZrak)
            zrak.set_maxO3(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def edit_BTX_zrak(self, x):
        """Callback za promjenu naziva maxBTX generatora cistog zraka."""
        try:
            value = float(x)
            zrak = self.doc.get_cistiZrak(self.aktivniZrak)
            zrak.set_maxBTX(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))


    def select_aktivni_zrak(self, x):
        """
        Callback za izbor generatora cistog zraka sa liste
        """
        value = self.model.data(x, QtCore.Qt.DisplayRole)
        self.aktivniZrak = value
        self.pushButtonIzbrisi.setEnabled(True)
        self.enable_edit_widgets(check=True)
        self.set_podatke_zraka()

    def set_podatke_zraka(self):
        """
        setter stanja izabranog generatora cistog zraka.
        """
        #block signale za editiranje postavki
        self.block_edit_signals(check=True)
        try:
            zrak = self.doc.get_cistiZrak(self.aktivniZrak)
            self.lineEditModel.setText(zrak.get_model())
            self.lineEditProizvodjac.setText(zrak.get_proizvodjac())
            self.doubleSpinBoxSO2.setValue(zrak.get_maxSO2())
            self.doubleSpinBoxNOx.setValue(zrak.get_maxNOx())
            self.doubleSpinBoxCO.setValue(zrak.get_maxCO())
            self.doubleSpinBoxO3.setValue(zrak.get_maxO3())
            self.doubleSpinBoxBTX.setValue(zrak.get_maxBTX())
        except Exception as err:
            logging.error(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))
            self.lineEditModel.setText('n/a')
            self.lineEditProizvodjac.setText('n/a')
            self.doubleSpinBoxSO2.setValue(0.0)
            self.doubleSpinBoxNOx.setValue(0.0)
            self.doubleSpinBoxCO.setValue(0.0)
            self.doubleSpinBoxO3.setValue(0.0)
            self.doubleSpinBoxBTX.setValue(0.0)
        #unblock signale za editiranje postavki
        self.block_edit_signals(check=False)

    def enable_edit_widgets(self, check=True):
        """
        Metoda sluzi za enable ili disable edit widgeta za postavke generatora cistog zraka.
        """
        x = bool(check)
        self.lineEditModel.setEnabled(x)
        self.lineEditProizvodjac.setEnabled(x)
        self.doubleSpinBoxSO2.setEnabled(x)
        self.doubleSpinBoxNOx.setEnabled(x)
        self.doubleSpinBoxCO.setEnabled(x)
        self.doubleSpinBoxO3.setEnabled(x)
        self.doubleSpinBoxBTX.setEnabled(x)

    def block_edit_signals(self, check=True):
        """
        Metoda sluzi za block ili unblock edit signala za postavke generatora cistog zraka.
        """
        x = bool(check)
        self.lineEditModel.blockSignals(x)
        self.lineEditProizvodjac.blockSignals(x)
        self.doubleSpinBoxSO2.blockSignals(x)
        self.doubleSpinBoxNOx.blockSignals(x)
        self.doubleSpinBoxCO.blockSignals(x)
        self.doubleSpinBoxO3.blockSignals(x)
        self.doubleSpinBoxBTX.blockSignals(x)
