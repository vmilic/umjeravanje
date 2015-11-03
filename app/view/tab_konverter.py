# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 11:47:06 2015

@author: DHMZ-Milic
"""
import numpy as np
from PyQt4 import QtCore, uic
import app.view.pomocni as view_helpers

BASE3, FORM3 = uic.loadUiType('./app/view/uiFiles/tab_konverter.ui')
class KonverterPanel(BASE3, FORM3):
    def __init__(self, dokument=None, parent=None):
        super(BASE3, self).__init__(parent)
        self.setupUi(self)
        self.dokument = dokument

        ### postavljanje inicijalnih vrijednosti kontrolnih elemenata ###
        self.checkKonverter.setChecked(self.dokument.get_provjeraKonvertera())
        self.konverterOpseg.setValue(self.dokument.get_opseg())
        self.cnox50SpinBox.setValue(self.dokument.get_cNOx50())
        self.cnox95SpinBox.setValue(self.dokument.get_cNOx95())
        self.labelKonverterOpseg.setText(self.dokument.get_mjernaJedinica())
        self.labelKonverter50.setText(self.dokument.get_mjernaJedinica())
        self.labelKonverter95.setText(self.dokument.get_mjernaJedinica())

        ### postavljanje tablica ###
        self.konverterRezultatView = view_helpers.TablicaKonverterRezultati()
        self.konverterRezultatView.set_mjerna_jedinica(self.dokument.get_mjernaJedinica())
        self.konverterRezultatView.set_tocke(self.dokument.get_tockeKonverter())
        self.konverterRezultatView.set_data(self.dokument.generiraj_nan_frejm_rezultata_konvertera())
        self.layoutKonverterRezultati.addWidget(self.konverterRezultatView)
        self.layoutKonverterRezultati.addStretch(-1)

        self.tablicaKonverter = view_helpers.TablicaKonverterParametri()
        self.tablicaKonverter.set_values([np.NaN, np.NaN, np.NaN, np.NaN])
        self.layoutKonverterParametri.addWidget(self.tablicaKonverter)
        self.layoutKonverterParametri.addStretch(-1)

        self.setup_connections()

    def setup_connections(self):
        #promjena opsega
        self.konverterOpseg.valueChanged.connect(self.promjena_konverterOpseg)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_opseg(PyQt_PyObject)'),
                     self.set_konverterOpseg)
        #promjena cnox50 parametra
        self.cnox50SpinBox.valueChanged.connect(self.promjena_cnox50SpinBox)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_cNOx50(PyQt_PyObject)'),
                     self.set_cnox50SpinBox)
        #promjena cnox95 parametra
        self.cnox95SpinBox.valueChanged.connect(self.promjena_cnox95SpinBox)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_cNOx95(PyQt_PyObject)'),
                     self.set_cnox95SpinBox)
        #provjera konvertera
        self.checkKonverter.toggled.connect(self.promjena_checkKonverter)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_provjeraKonvertera(PyQt_PyObject)'),
                     self.set_checkKonverter)

    def konverter_request_recalculate(self):
        """emit zahtjeva za ponovnim racunanjem rezultata"""
        self.emit(QtCore.SIGNAL('konverter_request_recalculate'))

    def promjena_checkKonverter(self, x):
        """slot koji zapisuje promjenu provjere konvertera u dokument (checkbox)"""
        value = self.checkKonverter.isChecked()
        self.dokument.set_provjeraKonvertera(value)

    def set_checkKonverter(self, x):
        """metoda postavlja ckeck provjere konvertera iz dokumenta u gui widget.
        x je lista [value, boolean]"""
        self.checkKonverter.setChecked(x[0])
        if x[1]:
            self.konverter_request_recalculate()

    def promjena_konverterOpseg(self, x):
        """slot koji zapisuje opseg konvertera u dokument (povezan sa opsegom
        umjeravanja)"""
        value = float(self.konverterOpseg.value())
        self.dokument.set_opseg(value)

    def set_konverterOpseg(self, x):
        """setter opsega provjere konvertera. x je lista [value, boolean].
        boolean je bitan za recalculate"""
        self.konverterOpseg.setValue(x[0])

    def promjena_cnox50SpinBox(self, x):
        """slot koji zapisuje parametar cnox50 u dokument"""
        value = float(self.cnox50SpinBox.value())
        self.dokument.set_cNOx50(value)

    def set_cnox50SpinBox(self, x):
        """metoda postavlja parametar cNOx50 iz dokumenta u gui widget.
        x je lista [value, boolean]"""
        self.cnox50SpinBox.setValue(x[0])
        if x[1]:
            self.konverter_request_recalculate()

    def promjena_cnox95SpinBox(self, x):
        """slot koji zapisuje parametar cnox95 u dokument"""
        value = float(self.cnox95SpinBox.value())
        self.dokument.set_cNOx95(value)

    def set_cnox95SpinBox(self, x):
        """metoda postavlja parametar cNOx95 iz dokumenta u gui widget.
        x je lista [value, boolean]"""
        self.cnox95SpinBox.setValue(x[0])
        if x[1]:
            self.konverter_request_recalculate()

    def update_rezultat(self, x):
        """update gui elemenata za prikaz rezultata sa novim podacima
        x je mapa:
        {'rezultat':frejm sa podacima,
         'efikasnost':lista efikasnosti konvertera}"""
        jedinica = self.dokument.get_mjernaJedinica()
        tocke = self.dokument.get_tockeKonverter()
        frejm = x['rezultat']
        eff = x['efikasnost']
        efikasnost = [str(round(i, 1)) for i in eff]
        self.konverterRezultatView.set_mjerna_jedinica(jedinica)
        self.konverterRezultatView.set_tocke(tocke)
        self.konverterRezultatView.set_data(frejm)
        self.tablicaKonverter.set_values(efikasnost)
