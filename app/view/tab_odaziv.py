# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 09:08:43 2015

@author: DHMZ-Milic
"""
import numpy as np
import pandas as pd
from PyQt4 import QtGui, QtCore, uic
import app.model.frejm_model as modeli
import app.view.canvas as canvas
import app.view.pomocni as view_helpers


BASE14, FORM14 = uic.loadUiType('./app/view/uiFiles/tab_odaziv.ui')
class RiseFallWidget(BASE14, FORM14):
    """
    prozor provjeru vremena uspona i pada za pojedini plin
    """
    def __init__(self, parent=None, dokument=None, naziv=None):
        """
        inicijalizacija prozora uz instancu dokumenta i slajs frejma sa podacima
        """
        super(BASE14, self).__init__(parent)
        self.setupUi(self)
        #zadani memberi
        self.doc = dokument
        self.plin = naziv
        self.naziv = naziv[:-7]
        #metapodaci za graf
        self.meta = {'xlabel':'vrijeme',
                     'ylabel':'koncentracija',
                     'title':'Vrijeme uspona i pada'}
        #kriteriji prihvatljivosti
        kriterijRise = ['Vrijeme odaziva (uspon)',
                        '???',
                        't<sub>r</sub',
                        np.NaN,
                        '???',
                        'NE']
        kriterijFall = ['Vrijeme odaziva (pad)',
                        '???',
                        't<sub>f</sub',
                        np.NaN,
                        '???',
                        'NE']
        kriterijDiff = ['Razlika odaziva uspona i pada',
                        '???',
                        't<sub>d</sub',
                        np.NaN,
                        '???',
                        'NE']
        self.reportKriterijValue = {'rise':kriterijRise,
                                    'fall':kriterijFall,
                                    'diff':kriterijDiff}
        #rezultati
        self.rezultatStupci = ['Naziv', 'Pocetak', 'Kraj', 'Delta']
        self.rezultat = pd.DataFrame(columns=self.rezultatStupci)
        self.model = self.doc.get_model(mjerenje=self.plin)
        self.modelRezultata = modeli.RiseFallResultModel()
        self.modelRezultata.set_frejm(self.rezultat)
        self.highLimit = self.model.get_high_limit()
        self.lowLimit = self.model.get_low_limit()
        self.doubleSpinBoxHigh.setValue(self.highLimit)
        self.doubleSpinBoxLow.setValue(self.lowLimit)

        #postavljanje elemenata u layout:
        self.tableViewRezultati.setModel(self.modelRezultata)
        self.graf = canvas.RiseFallKanvas(meta=self.meta)
        self.tablicaKriterija = view_helpers.ReportTablicaKriterijaRiseFall()
        self.kriterijLayout.addWidget(self.tablicaKriterija)
        self.grafLayout.addWidget(self.graf)

        self.setup_connections()
        self.update_rezultate()

    def setup_connections(self):
        self.doubleSpinBoxHigh.valueChanged.connect(self.modify_high_limit)
        self.doubleSpinBoxLow.valueChanged.connect(self.modify_low_limit)

    def modify_high_limit(self, x):
        value = float(x)
        self.highLimit = value
        self.model.set_high_limit(value)
        self.update_rezultate()

    def modify_low_limit(self, x):
        value = float(x)
        self.lowLimit = value
        self.model.set_low_limit(value)
        self.update_rezultate()

    def nadji_kraj_uspona(self, frejm, ts):
        frejm = frejm.iloc[:,2]
        frejm = frejm[frejm.index >= ts]
        frejm = frejm[frejm >= self.highLimit]
        if len(frejm):
            return frejm.index[0]
        else:
            return pd.NaT

    def nadji_kraj_pada(self, frejm, ts):
        frejm = frejm.iloc[:,2]
        frejm = frejm[frejm.index >= ts]
        frejm = frejm[frejm <= self.lowLimit]
        if len(frejm):
            return frejm.index[0]
        else:
            return pd.NaT

    def get_reportKriterijValue(self):
        return self.reportKriterijValue

    def update_rezultate(self):
        self.make_rezultat_from_model_data()
        self.modelRezultata.set_frejm(self.rezultat)
        slajs = self.model.get_slajs()
        self.graf.crtaj(podaci=slajs,
                        rezultati=self.rezultat,
                        high=self.highLimit,
                        low=self.lowLimit)
        self.set_reportValue()

    def make_rezultat_from_model_data(self):
        """Metoda generira frejm rezultata iz modela"""
        self.rezultat = pd.DataFrame(columns=self.rezultatStupci)
        frejm = self.model.get_frejm()
        #usponi
        r = frejm[frejm.iloc[:,0] == QtCore.Qt.Checked]
        for i in r.index:
            start = i
            kraj = self.nadji_kraj_uspona(frejm, i)
            if not isinstance(kraj, pd.tslib.NaTType):
                delta = (kraj - start).total_seconds()
            else:
                delta = np.NaN
            self.dodaj_red_u_rezultat_frejm('RISE', start, kraj, delta)
        #padovi
        f = frejm[frejm.iloc[:,1] == QtCore.Qt.Checked]
        for i in f.index:
            start = i
            kraj = self.nadji_kraj_pada(frejm, i)
            if not isinstance(kraj, pd.tslib.NaTType):
                delta = (kraj - start).total_seconds()
            else:
                delta = np.NaN
            self.dodaj_red_u_rezultat_frejm('FALL', start, kraj, delta)

    def dodaj_red_u_rezultat_frejm(self, nazivStupca, start, kraj, delta):
        indeks = len(self.rezultat)
        #provjeri da li postoji vec isto vrijeme prije dodavanja
        startovi = list(self.rezultat['Pocetak'])
        if start not in startovi:
            df = pd.DataFrame({'Naziv':nazivStupca,
                               'Pocetak':start,
                               'Kraj':kraj,
                               'Delta':delta},
                               index=[indeks],
                               columns=self.rezultatStupci)
            self.rezultat = self.rezultat.append(df)

    def set_reportValue(self):
        frejm = self.rezultat.copy()
        risenaziv = '{0}-RISE'.format(self.naziv)
        fallnaziv = '{0}-FALL'.format(self.naziv)
        frejmRise = frejm[frejm.loc[:,'Naziv'] == risenaziv]
        frejmFall = frejm[frejm.loc[:,'Naziv'] == fallnaziv]
        #time rise
        if len(frejmRise) >= 4:
            deltaRise = np.average(frejmRise.loc[:,'Delta'])
            #TODO! nedostaje jasan kriterij, hardcoded 180
            kriterij = 180
            if deltaRise <= kriterij:
                self.reportKriterijValue['rise'][5] = 'DA'
            else:
                self.reportKriterijValue['rise'][5] = 'NE'
        else:
            deltaRise = np.NaN
            self.reportKriterijValue['rise'][5] = 'NE'
        self.reportKriterijValue['rise'][3] = deltaRise
        #time fall
        if len(frejmFall):
            deltaFall = np.average(frejmFall.loc[:,'Delta'])
            #TODO! nedostaje jasan kriterij, hardcoded 180
            kriterij = 180
            if deltaFall <= kriterij:
                self.reportKriterijValue['fall'][5] = 'DA'
            else:
                self.reportKriterijValue['fall'][5] = 'NE'
        else:
            deltaFall = np.NaN
            self.reportKriterijValue['fall'][5] = 'NE'
        self.reportKriterijValue['fall'][3] = deltaFall
        # time rise - time fall
        if (not np.isnan(deltaRise)) and (not np.isnan(deltaFall)):
            t = abs(deltaRise - deltaFall)
            #TODO! nedostaje jasan kriterij, hardcoded 60
            kriterij = 60
            if t <= kriterij:
                self.reportKriterijValue['diff'][5] = 'DA'
            else:
                self.reportKriterijValue['diff'][5] = 'NE'
        else:
            t = np.NaN
            self.reportKriterijValue['diff'][5] = 'NE'
        self.reportKriterijValue['diff'][3] = t

        self.tablicaKriterija.set_values(self.reportKriterijValue)
