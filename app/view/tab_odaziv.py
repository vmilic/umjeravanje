# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 09:08:43 2015

@author: DHMZ-Milic
"""
import numpy as np
import pandas as pd
from PyQt4 import QtCore, uic
from app.model.qt_models import OdazivModel, RiseFallResultModel
import app.view.canvas as canvas
from app.pomocni import pomocni

BASE_TAB_ODAZIV, FORM_TAB_ODAZIV = uic.loadUiType('./app/view/uiFiles/tab_odaziv.ui')
class TabOdaziv(BASE_TAB_ODAZIV, FORM_TAB_ODAZIV):
    """
    prozor provjeru vremena uspona i pada za pojedini plin
    """
    def __init__(self, parent=None, datastore=None, plin=None):
        """
        inicijalizacija prozora uz instancu dokumenta i slajs frejma sa podacima
        """
        super(BASE_TAB_ODAZIV, self).__init__(parent)
        self.setupUi(self)
        #zadani memberi
        self.datastore = datastore
        self.plin = plin #'komponenta-odaziv'
        self.naziv = plin[:-7] #'komponenta'
        #inicijalni kriterij za vrijeme uspona i pada
        self.tr = self.datastore.get_uredjaj().get_analitickaMetoda().get_tr() #time rise
        self.tf = self.datastore.get_uredjaj().get_analitickaMetoda().get_tf() #time fall
        #granice
        self.highLimit = self.datastore.tabData[self.plin].get_maxlimit()
        self.lowLimit = self.datastore.tabData[self.plin].get_minlimit()
        #metapodaci za graf
        self.meta = {'xlabel':'vrijeme',
                     'ylabel':'koncentracija',
                     'title':'Vrijeme uspona i pada'}
        #kriteriji prihvatljivosti
        kriterijRise = ['Vrijeme odaziva (uspon)',
                        '',
                        't<sub>r</sub> = ',
                        np.NaN,
                        '<{0} s'.format(self.tr),
                        'NE']
        kriterijFall = ['Vrijeme odaziva (pad)',
                        '',
                        't<sub>f</sub> = ',
                        np.NaN,
                        '<{0} s'.format(self.tf),
                        'NE']
        self.reportKriterijValue = {'rise':kriterijRise,
                                    'fall':kriterijFall}
        #rezultati
        self.rezultatStupci = ['Naziv', 'Pocetak', 'Kraj', 'Delta']
        self.rezultat = pd.DataFrame(columns=self.rezultatStupci)

        self.model = OdazivModel(slajs=None, naziv=self.naziv)
        frejm = self.datastore.tabData[self.plin].get_frejm()
        if isinstance(frejm, pd.core.frame.DataFrame):
            self.model.set_frejm(frejm)
        self.model.set_high_limit(self.highLimit)
        self.model.set_low_limit(self.lowLimit)
        self.doubleSpinBoxHigh.setValue(self.highLimit)
        self.doubleSpinBoxLow.setValue(self.lowLimit)

        self.modelRezultata = RiseFallResultModel()
        self.modelRezultata.set_frejm(self.rezultat)

        #postavljanje elemenata u layout:
        self.tableViewRezultati.setModel(self.modelRezultata)
        self.tableViewRezultati.setColumnWidth(0,45)
        self.tableViewRezultati.setColumnWidth(1,135)
        self.tableViewRezultati.setColumnWidth(2,135)
        self.tableViewRezultati.setColumnWidth(3,45)
        self.graf = canvas.RiseFallKanvas(meta=self.meta)
        self.tablicaKriterija = pomocni.ReportTablicaKriterijaRiseFall()
        self.kriterijLayout.addWidget(self.tablicaKriterija)
        self.grafLayout.addWidget(self.graf)

        self.setup_connections()
        self.update_rezultate()

    def set_model(self, x):
        self.model = x

    def get_model(self):
        return self.model

    def setup_connections(self):
        self.doubleSpinBoxHigh.valueChanged.connect(self.modify_high_limit)
        self.doubleSpinBoxLow.valueChanged.connect(self.modify_low_limit)
        self.connect(self.graf,
                     QtCore.SIGNAL('izabrano_vrijeme(PyQt_PyObject)'),
                     self.selektiraj_najblizi_indeks)

    def selektiraj_najblizi_indeks(self, x):
        """Ulaz je pandas timestamp. Metoda sluzi za scroll tablice podataka na
        najblizi indeks"""
        #find index...
        frejm = self.model.get_frejm()
        if len(frejm):
            rez = frejm[frejm.index >= x]
            if len(rez):
                prviVeciIndex = rez.index[0]
                lista1 = list(frejm.index)
                red = lista1.index(prviVeciIndex)
            else:
                red = frejm.index[-1]
            indeks = self.model.index(red, 2)
            self.emit(QtCore.SIGNAL('scroll_to_index(PyQt_PyObject)'), indeks)

    def modify_high_limit(self, x):
        value = float(x)
        self.highLimit = value
        self.model.set_high_limit(value)
        self.datastore.tabData[self.plin].set_maxlimit(value)
        self.update_rezultate()

    def modify_low_limit(self, x):
        value = float(x)
        self.lowLimit = value
        self.model.set_low_limit(value)
        self.datastore.tabData[self.plin].set_minlimit(value)
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
        #set novi frejm u datastore...
        self.datastore.tabData[self.plin].set_frejm(self.model.get_frejm())
        #nacrtaj rezultat
        slajs = self.model.get_slajs()
        self.graf.crtaj(podaci=slajs,
                        rezultati=self.rezultat,
                        high=self.highLimit,
                        low=self.lowLimit)
        #provjeri kriterij
        self.set_reportValue()
        mapa = {}
        mapa['kriterij'] = self.reportKriterijValue
        s = self.rezultat.loc[:,'Pocetak']
        if len(s):
            mapa['start'] = min(s)
        else:
            mapa['start'] = 'n/a'
        k = self.rezultat.loc[:,'Kraj']
        if len(k):
            mapa['kraj'] = max(k)
        else:
            mapa['kraj'] = 'n/a'
        self.datastore.tabData[self.plin].set_rezultat(mapa)

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
        frejmRise = frejm[frejm.loc[:,'Naziv'] == 'RISE']
        frejmFall = frejm[frejm.loc[:,'Naziv'] == 'FALL']
        #time rise
        if len(frejmRise) >= 4:
            deltaRise = np.average(frejmRise.loc[:,'Delta'])
            if deltaRise <= self.tr:
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
            if deltaFall <= self.tf:
                self.reportKriterijValue['fall'][5] = 'DA'
            else:
                self.reportKriterijValue['fall'][5] = 'NE'
        else:
            deltaFall = np.NaN
            self.reportKriterijValue['fall'][5] = 'NE'
        self.reportKriterijValue['fall'][3] = deltaFall
        self.tablicaKriterija.set_values(self.reportKriterijValue)
