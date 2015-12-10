# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 11:47:06 2015

@author: DHMZ-Milic
"""
import numpy as np
import pandas as pd
from PyQt4 import QtCore, uic
import app.view.pomocni as view_helpers


BASE3, FORM3 = uic.loadUiType('./app/view/uiFiles/tab_konverter.ui')
class KonverterPanel(BASE3, FORM3):
    def __init__(self, dokument=None, parent=None):
        super(BASE3, self).__init__(parent)
        self.setupUi(self)
        self.dokument = dokument
        self.plin = 'konverter'
        self.model = self.dokument.get_model(mjerenje='konverter')
        self.checkBoxReport.setChecked(self.dokument.get_generateReportCheck(mjerenje=self.plin))

        ### postavljanje inicijalnih vrijednosti kontrolnih elemenata ###
        self.konverterOpseg.setValue(self.dokument.get_opseg())
        self.cnox50SpinBox.setValue(self.dokument.get_cNOx50())
        self.cnox95SpinBox.setValue(self.dokument.get_cNOx95())
        self.labelKonverterOpseg.setText(self.dokument.get_mjernaJedinica())
        self.labelKonverter50.setText(self.dokument.get_mjernaJedinica())
        self.labelKonverter95.setText(self.dokument.get_mjernaJedinica())

        ### postavljanje tablica ###
        self.konverterRezultatView = view_helpers.TablicaKonverterRezultati()
        self.konverterRezultatView.set_mjerna_jedinica(self.dokument.get_mjernaJedinica())
        self.konverterRezultatView.set_tocke(self.model.get_tocke())
        self.konverterRezultatView.set_data(self.generiraj_nan_frejm_rezultata_konvertera())
        self.layoutKonverterRezultati.addWidget(self.konverterRezultatView)
        self.layoutKonverterRezultati.addStretch(-1)

        self.tablicaKonverter = view_helpers.TablicaKonverterParametri()
        self.tablicaKonverter.set_values([np.NaN, np.NaN, np.NaN, np.NaN])

        self.layoutKonverterParametri.addWidget(self.tablicaKonverter)
        self.layoutKonverterParametri.addStretch(-1)

        self.tablicaKriterija = view_helpers.TablicaKonverterKriterij()
        self.layoutKonverterKriterij.addWidget(self.tablicaKriterija)
        self.layoutKonverterKriterij.addStretch(-1)

        self.setup_connections()

    def generiraj_nan_frejm_rezultata_konvertera(self):
        """
        metoda generira datafrejm sa 4 stupca i 6 redaka radi inicijalnog prikaza
        tablice rezultata umjeravanja. Sve vrijednosti tog datafrejma su np.NaN
        """
        tocke = self.model.get_tocke()
        indeks = [str(tocka) for tocka in tocke]
        frejm = pd.DataFrame(
            columns=['c, R, NOx', 'c, R, NO2', 'c, NO', 'c, NOx'],
            index=indeks)
        return frejm

    def setup_connections(self):
        #promjena opsega
        self.checkBoxReport.stateChanged.connect(self.set_report_check)
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

    def set_report_check(self, x):
        """promjeni check za generiranje reporta za zadano mjerenje"""
        x = bool(x)
        self.dokument.set_generateReportCheck(x, mjerenje=self.plin)

    def get_report_check(self):
        """getter checka za generiranje reporta"""
        return self.checkBoxReport.isChecked()

    def konverter_request_recalculate(self):
        """emit zahtjeva za ponovnim racunanjem rezultata"""
        self.emit(QtCore.SIGNAL('konverter_request_recalculate'))

    def promjena_konverterOpseg(self, x):
        """slot koji zapisuje opseg konvertera u dokument (povezan sa opsegom
        umjeravanja)"""
        value = float(self.konverterOpseg.value())
        self.dokument.set_opseg(value)

    def set_konverterOpseg(self, x):
        """setter opsega provjere konvertera. x je mapa sa kljucevima
        'value', 'recalculate'.
        """
        value = x['value']
        recalculate = x['recalculate']
        self.konverterOpseg.setValue(value)
        if recalculate:
            self.konverter_request_recalculate()

    def promjena_cnox50SpinBox(self, x):
        """slot koji zapisuje parametar cnox50 u dokument"""
        value = float(self.cnox50SpinBox.value())
        self.dokument.set_cNOx50(value)

    def set_cnox50SpinBox(self, x):
        """metoda postavlja parametar cNOx50 iz dokumenta u gui widget.
        x je lista [value, boolean]"""
        value = x['value']
        recalculate = x['recalculate']
        self.cnox50SpinBox.setValue(value)
        if recalculate:
            self.konverter_request_recalculate()

    def promjena_cnox95SpinBox(self, x):
        """slot koji zapisuje parametar cnox95 u dokument"""
        value = float(self.cnox95SpinBox.value())
        self.dokument.set_cNOx95(value)

    def set_cnox95SpinBox(self, x):
        """metoda postavlja parametar cNOx95 iz dokumenta u gui widget.
        x je mapa sa kljucevima 'value', 'recalculate' """
        value = x['value']
        recalculate = x['recalculate']
        self.cnox95SpinBox.setValue(value)
        if recalculate:
            self.konverter_request_recalculate()

    def update_rezultat(self, x):
        """update gui elemenata za prikaz rezultata sa novim podacima
        x je mapa:
        {'rezultat':frejm sa podacima,
         'efikasnost':lista efikasnosti konvertera,
         'ec_kriterij':nested lista podataka za prikaz kriterija prihvatljivosti}"""
        jedinica = self.dokument.get_mjernaJedinica()
        tocke = self.model.get_tocke()
        frejm = x['rezultat']
        eff = x['efikasnost']
        krit = x['ec_kriterij']
        krit[3] = str(round(krit[3], 1)) #round i adapt rezultat u string
        efikasnost = [str(round(i, 1)) for i in eff]
        self.konverterRezultatView.set_mjerna_jedinica(jedinica)
        self.konverterRezultatView.set_tocke(tocke)
        self.konverterRezultatView.set_data(frejm)
        self.tablicaKonverter.set_values(efikasnost)
        self.tablicaKriterija.set_values(krit)
