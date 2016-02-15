# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 11:47:06 2015

@author: DHMZ-Milic
"""
import copy
import numpy as np
import pandas as pd
from PyQt4 import QtCore, uic
from app.pomocni import pomocni
from app.model.qt_models import SiroviFrameModel

BASE_TAB_KONVERTER, FORM_TAB_KONVERTER = uic.loadUiType('./app/view/uiFiles/tab_konverter.ui')
class TabKonverter(BASE_TAB_KONVERTER, FORM_TAB_KONVERTER):
    def __init__(self, datastore=None, plin='konverter', parent=None):
        super(BASE_TAB_KONVERTER, self).__init__(parent)
        self.setupUi(self)
        self.datastore = datastore
        self.plin = plin
        self.model = SiroviFrameModel(tocke=self.datastore.get_tocke(self.plin),
                                      frejm=self.datastore.tabData[self.plin].get_frejm(),
                                      start=self.datastore.tabData[self.plin].get_startIndeks())
        ### postavljanje tablica ###
        self.konverterRezultatView = pomocni.TablicaKonverterRezultati()
        self.konverterRezultatView.set_mjerna_jedinica(self.datastore.get_izabranaMjernaJedinica())
        self.konverterRezultatView.set_tocke(self.datastore.tabData['konverter'].get_tocke())
        self.konverterRezultatView.set_data(self.generiraj_nan_frejm_rezultata_konvertera())
        self.layoutKonverterRezultati.addWidget(self.konverterRezultatView)
        self.layoutKonverterRezultati.addStretch(-1)
        self.tablicaKonverter = pomocni.TablicaKonverterParametri()
        self.tablicaKonverter.set_values([np.NaN, np.NaN, np.NaN, np.NaN])
        self.layoutKonverterParametri.addWidget(self.tablicaKonverter)
        self.layoutKonverterParametri.addStretch(-1)
        self.tablicaKriterija = pomocni.TablicaKonverterKriterij()
        self.layoutKonverterKriterij.addWidget(self.tablicaKriterija)
        self.layoutKonverterKriterij.addStretch(-1)

    def get_model(self):
        return self.model

    def set_model(self, x):
        self.model = x

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

    def konverter_request_recalculate(self):
        """emit zahtjeva za ponovnim racunanjem rezultata"""
        self.emit(QtCore.SIGNAL('konverter_request_recalculate'))

    def update_rezultat(self, ulaz):
        """update gui elemenata za prikaz rezultata sa novim podacima
        x je mapa:
        {'rezultat':frejm sa podacima,
         'efikasnost':lista efikasnosti konvertera,
         'ec_kriterij':nested lista podataka za prikaz kriterija prihvatljivosti}"""
        jedinica = self.datastore.get_izabranaMjernaJedinica()
        tocke = self.model.get_tocke()
        x = copy.deepcopy(ulaz)
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
