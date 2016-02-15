# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 12:42:54 2016

@author: DHMZ-Milic
"""
import pickle
import logging
from PyQt4 import QtGui, uic
from app.model.qt_models import ListModelMetode
from app.model.analiticka_metoda import AnalitickaMetoda


BASE_DIJALOG_METODA, FORM_DIJALOG_METODA = uic.loadUiType('./app/view/uiFiles/dijalog_metoda.ui')
class DijalogAnalitickaMetoda(BASE_DIJALOG_METODA, FORM_DIJALOG_METODA):
    """
    Dijalog za edit i dodavanje analitickih metoda u dokument
    """
    def __init__(self, dokument=None, parent=None):
        super(BASE_DIJALOG_METODA, self).__init__(parent)
        self.setupUi(self)
        tegla = pickle.loads(dokument)
        self.doc = tegla
        self.aktivnaMetoda = None
        self.model = ListModelMetode(dokument=tegla)
        self.listViewMetode.setModel(self.model)

        self.setup_connections()

    def get_dokument(self):
        tegla = pickle.dumps(self.doc)
        return tegla

    def setup_connections(self):
        self.pushButtonDodaj.clicked.connect(self.dodaj_metodu_u_dokument)
        self.listViewMetode.clicked.connect(self.select_aktivnu_metodu)
        self.lineEditMjernaJedinica.textChanged.connect(self.edit_finished_jedinica)
        self.lineEditNaziv.textChanged.connect(self.edit_finished_naziv)
        self.lineEditNorma.textChanged.connect(self.edit_finished_norma)
        self.doubleSpinBoxSrs.valueChanged.connect(self.edit_finished_srz)
        self.doubleSpinBoxSrz.valueChanged.connect(self.edit_finished_srz)
        self.doubleSpinBoxOpseg.valueChanged.connect(self.edit_finished_o)
        self.doubleSpinBoxRmax.valueChanged.connect(self.edit_finished_rmax)
        self.doubleSpinBoxRz.valueChanged.connect(self.edit_finished_rz)
        self.doubleSpinBoxTr.valueChanged.connect(self.edit_finished_tr)
        self.doubleSpinBoxTf.valueChanged.connect(self.edit_finished_tf)
        self.doubleSpinBoxEcmin.valueChanged.connect(self.edit_finished_ecmin)
        self.doubleSpinBoxEcmax.valueChanged.connect(self.edit_finished_ecmax)

    def edit_finished_jedinica(self, x):
        """Callback za promjenu mjerne jedinice analiticke metode."""
        try:
            value = str(x)
            metoda = self.doc.get_analiticku_metodu(self.aktivnaMetoda)
            metoda.set_jedinica(value)
            #prebaci ostale jedinice
            value = "".join(['( ', metoda.get_jedinica(), ' )'])
            self.label_jedinica_1.setText(value)
            self.label_jedinica_2.setText(value)
            self.label_jedinica_3.setText(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))
            #prebaci ostale jedinice
            self.label_jedinica_1.setText('( n/a )')
            self.label_jedinica_2.setText('( n/a )')
            self.label_jedinica_3.setText('( n/a )')

    def edit_finished_naziv(self, x):
        """Callback za promjenu naziva analiticke metode."""
        try:
            value = str(x)
            metoda = self.doc.get_analiticku_metodu(self.aktivnaMetoda)
            metoda.set_naziv(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def edit_finished_norma(self, x):
        """Callback za promjenu norme analiticke metode."""
        try:
            value = str(x)
            metoda = self.doc.get_analiticku_metodu(self.aktivnaMetoda)
            metoda.set_norma(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def edit_finished_srs(self, x):
        """Callback za promjenu Srs analiticke metode."""
        try:
            value = str(x)
            metoda = self.doc.get_analiticku_metodu(self.aktivnaMetoda)
            metoda.set_Srs(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def edit_finished_srz(self, x):
        """Callback za promjenu Srz analiticke metode."""
        try:
            value = str(x)
            metoda = self.doc.get_analiticku_metodu(self.aktivnaMetoda)
            metoda.set_Srz(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def edit_finished_o(self, x):
        """Callback za promjenu opsega analiticke metode."""
        try:
            value = str(x)
            metoda = self.doc.get_analiticku_metodu(self.aktivnaMetoda)
            metoda.set_o(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def edit_finished_rmax(self, x):
        """Callback za promjenu rmax analiticke metode."""
        try:
            value = str(x)
            metoda = self.doc.get_analiticku_metodu(self.aktivnaMetoda)
            metoda.set_rmax(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def edit_finished_rz(self, x):
        """Callback za promjenu rz analiticke metode."""
        try:
            value = str(x)
            metoda = self.doc.get_analiticku_metodu(self.aktivnaMetoda)
            metoda.set_rz(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def edit_finished_tr(self, x):
        """Callback za promjenu tr analiticke metode."""
        try:
            value = str(x)
            metoda = self.doc.get_analiticku_metodu(self.aktivnaMetoda)
            metoda.set_tr(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def edit_finished_tf(self, x):
        """Callback za promjenu tf analiticke metode."""
        try:
            value = str(x)
            metoda = self.doc.get_analiticku_metodu(self.aktivnaMetoda)
            metoda.set_tf(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def edit_finished_ecmin(self, x):
        """Callback za promjenu Ec_min analiticke metode."""
        try:
            value = str(x)
            metoda = self.doc.get_analiticku_metodu(self.aktivnaMetoda)
            metoda.set_Ec_min(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def edit_finished_ecmax(self, x):
        """Callback za promjenu Ec_max analiticke metode."""
        try:
            value = str(x)
            metoda = self.doc.get_analiticku_metodu(self.aktivnaMetoda)
            metoda.set_Ec_max(value)
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))

    def set_podatke_metode(self):
        """
        Setter stanja dilucijske jedinice u gui za izabranu analiticku metodu.
        """
        #block signale za editiranje postavki
        self.block_edit_signals(check=True)
        try:
            metoda = self.doc.get_analiticku_metodu(self.aktivnaMetoda)
            self.labelID.setText(metoda.get_ID())
            self.lineEditMjernaJedinica.setText(metoda.get_jedinica())
            unit = "".join(['( ', metoda.get_jedinica(), ' )'])
            self.label_jedinica_1.setText(unit)
            self.label_jedinica_2.setText(unit)
            self.label_jedinica_3.setText(unit)
            self.lineEditNaziv.setText(metoda.get_naziv())
            self.lineEditNorma.setText(metoda.get_norma())
            self.doubleSpinBoxSrs.setValue(metoda.get_Srs())
            self.doubleSpinBoxSrz.setValue(metoda.get_Srz())
            self.doubleSpinBoxOpseg.setValue(metoda.get_o())
            self.doubleSpinBoxRmax.setValue(metoda.get_rmax())
            self.doubleSpinBoxRz.setValue(metoda.get_rz())
            self.doubleSpinBoxTr.setValue(metoda.get_tr())
            self.doubleSpinBoxTf.setValue(metoda.get_tf())
            self.doubleSpinBoxEcmin.setValue(metoda.get_Ec_min())
            self.doubleSpinBoxEcmax.setValue(metoda.get_Ec_max())
        except Exception as err:
            logging.error(str(err), exc_info=True)
            QtGui.QMessageBox.warning(self, 'Pogreska pri radu', str(err))
            self.labelID.setText('n/a')
            self.lineEditMjernaJedinica.setText('n/a')
            self.label_jedinica_1.setText('( n/a )')
            self.label_jedinica_2.setText('( n/a )')
            self.label_jedinica_3.setText('( n/a )')
            self.lineEditNaziv.setText('n/a')
            self.lineEditNorma.setText('n/a')
            self.doubleSpinBoxSrs.setValue(0.0)
            self.doubleSpinBoxSrz.setValue(0.0)
            self.doubleSpinBoxOpseg.setValue(0.0)
            self.doubleSpinBoxRmax.setValue(0.0)
            self.doubleSpinBoxRz.setValue(0.0)
            self.doubleSpinBoxTr.setValue(0.0)
            self.doubleSpinBoxTf.setValue(0.0)
            self.doubleSpinBoxEcmin.setValue(0.0)
            self.doubleSpinBoxEcmax.setValue(0.0)
        #unblock signale za editiranje postavki
        self.block_edit_signals(check=False)

    def select_aktivnu_metodu(self, x):
        """callback za izbor metode iz liste"""
        key = self.model.vrati_kljuc_indeksa(x)
        self.aktivnaMetoda = key
        self.enable_edit_widgets(check=True)
        self.set_podatke_metode()
        self.model.layoutChanged.emit()

    def dodaj_metodu_u_dokument(self, x):
        """dodavanje nove metode"""
        metode = self.doc.get_listu_analitickih_metoda()
        intmetode = [int(i) for i in metode]
        ID = str(max(intmetode) + 1)
        if ID in self.doc.get_listu_analitickih_metoda():
            QtGui.QMessageBox.warning(self, 'Upozorenje', 'Metoda sa istim ID vec postoji.')
            return None
        elif len(ID) == 0:
            QtGui.QMessageBox.warning(self, 'Upozorenje', 'ID nije zadan.')
        else:
            metoda = AnalitickaMetoda(ID=ID)
            self.doc.set_novu_analiticku_metodu(ID, metoda)
            self.model.layoutChanged.emit()

    def enable_edit_widgets(self, check=True):
        """
        Metoda sluzi za enable ili disable edit widgeta za postavke metode.
        """
        x = bool(check)
        self.lineEditMjernaJedinica.setEnabled(x)
        self.lineEditNaziv.setEnabled(x)
        self.lineEditNorma.setEnabled(x)
        self.doubleSpinBoxSrs.setEnabled(x)
        self.doubleSpinBoxSrz.setEnabled(x)
        self.doubleSpinBoxOpseg.setEnabled(x)
        self.doubleSpinBoxRmax.setEnabled(x)
        self.doubleSpinBoxRz.setEnabled(x)
        self.doubleSpinBoxTr.setEnabled(x)
        self.doubleSpinBoxTf.setEnabled(x)
        self.doubleSpinBoxEcmin.setEnabled(x)
        self.doubleSpinBoxEcmax.setEnabled(x)

    def block_edit_signals(self, check=True):
        """
        Metoda sluzi za block ili unblock edit signala za postavke metode.
        """
        x = bool(check)
        self.lineEditMjernaJedinica.blockSignals(x)
        self.lineEditNaziv.blockSignals(x)
        self.lineEditNorma.blockSignals(x)
        self.doubleSpinBoxSrs.blockSignals(x)
        self.doubleSpinBoxSrz.blockSignals(x)
        self.doubleSpinBoxOpseg.blockSignals(x)
        self.doubleSpinBoxRmax.blockSignals(x)
        self.doubleSpinBoxRz.blockSignals(x)
        self.doubleSpinBoxTr.blockSignals(x)
        self.doubleSpinBoxTf.blockSignals(x)
        self.doubleSpinBoxEcmin.blockSignals(x)
        self.doubleSpinBoxEcmax.blockSignals(x)

