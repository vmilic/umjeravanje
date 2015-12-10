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

        self.doc = dokument
        self.plin = naziv
        self.naziv = naziv[:-7]
        self.rezultatStupci = self.doc.mjerenja[self.plin]['rezultatStupci']
        self.rezultat = self.doc.mjerenja[self.plin]['rezultatFrejm']
        self.meta = {'xlabel':'vrijeme',
                     'ylabel':'koncentracija',
                     'title':'Vrijeme uspona i pada'}
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

        self.model = self.doc.get_model(mjerenje=self.plin)
        self.modelRezultata = modeli.RiseFallResultModel()
        self.modelRezultata.set_frejm(self.rezultat)

        self.checkBoxReport.setChecked(self.doc.get_generateReportCheck(mjerenje=self.plin))
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
        self.checkBoxReport.toggled.connect(self.toggle_report)

    def toggle_report(self, x):
        x = bool(x)
        self.doc.set_generateReportCheck(x, mjerenje=self.plin)

    def get_report_check(self):
        return self.checkBoxReport.isChecked()

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

    def update_rezultate(self):
        #TODO!
        #update novi rezultat
        self.doc.set_rezulatFrejm_odaziva(self.rezultat, mjerenje=self.plin)
        self.modelRezultata.set_frejm(self.rezultat)
        slajs = self.model.get_slajs()
        self.graf.crtaj(podaci=slajs,
                        rezultati=self.rezultat,
                        high=self.highLimit,
                        low=self.lowLimit)
        self.set_reportValue()

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

    def check_pocetak(self, x):
        """slot za interakciju sa sirovim podacima"""
        red = x.row()
        stupac = x.column()
        check = self.model.dataFrejm.iloc[red, stupac]
        nazivStupca = self.model.dataFrejm.columns[stupac]
        start = self.model.dataFrejm.index[red]
        if check == QtCore.Qt.Checked:
            if 'RISE' in nazivStupca:
                col = stupac + 2
                kraj = self.nadji_kraj_uspona(red, col)
                if not isinstance(kraj, pd.tslib.NaTType):
                    delta = (kraj - start).total_seconds()
                else:
                    delta = np.NaN
                self.dodaj_red_u_rezultat_frejm(nazivStupca, start, kraj, delta)
            elif 'FALL' in nazivStupca:
                col = stupac + 1
                kraj = self.nadji_kraj_pada(red, col)
                if not isinstance(kraj, pd.tslib.NaTType):
                    delta = (kraj - start).total_seconds()
                else:
                    delta = np.NaN
                self.dodaj_red_u_rezultat_frejm(nazivStupca, start, kraj, delta)
            else:
                pass
        elif check == QtCore.Qt.Unchecked:
            self.makni_red_iz_rezultat_frejma(nazivStupca, start)
        else:
            pass

    def nadji_kraj_uspona(self, red, stupac):
        frejm = self.model.dataFrejm.copy()
        nazivStupca = frejm.columns[stupac]
        frejm = frejm[nazivStupca]
        frejm = frejm[frejm.index >= frejm.index[red]]
        frejm = frejm[frejm >= self.highLimit]
        if len(frejm):
            return frejm.index[0]
        else:
            return pd.NaT

    def nadji_kraj_pada(self, red, stupac):
        frejm = self.model.dataFrejm.copy()
        nazivStupca = frejm.columns[stupac]
        frejm = frejm[nazivStupca]
        frejm = frejm[frejm.index >= frejm.index[red]]
        frejm = frejm[frejm <= self.lowLimit]
        if len(frejm):
            return frejm.index[0]
        else:
            return pd.NaT

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
            self.update_rezultate()

    def makni_red_iz_rezultat_frejma(self, nazivStupca, start):
        if len(self.rezultat):
            frejm = self.rezultat.copy()
            frejm = frejm[frejm.iloc[:,0]==nazivStupca]
            frejm = frejm[frejm.iloc[:,1]==start]
            self.rezultat = self.rezultat.drop(self.rezultat.index[frejm.index])
            #reindex
            self.rezultat.index = list(range(len(self.rezultat)))
            self.update_rezultate()
