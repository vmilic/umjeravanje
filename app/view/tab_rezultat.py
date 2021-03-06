# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 10:50:23 2015

@author: DHMZ-Milic
"""
import gc
import sip
import logging
import pandas as pd
from PyQt4 import QtGui, QtCore, uic
import app.view.canvas as canvas
from app.pomocni import pomocni
from app.model.qt_models import SiroviFrameModel


BASE_TAB_REZULTAT, FORM_TAB_REZULTAT = uic.loadUiType('./app/view/uiFiles/tab_rezultat.ui')
class TabRezultat(BASE_TAB_REZULTAT, FORM_TAB_REZULTAT):
    """
    Panel za prikaz rezultata umjeravanja.
    """
    def __init__(self, datastore=None, plin=None, parent=None):
        super(BASE_TAB_REZULTAT, self).__init__(parent)
        self.setupUi(self)
        self.datastore = datastore
        self.plin = plin
        #nazivi boxeva
        self.graf1GroupBox.setTitle(", ".join(['graf koncentracije', self.plin]))
        self.graf2GroupBox.setTitle(", ".join(['graf individualnih mjerenja', self.plin]))
        self.rezultatiGroupBox.setTitle(", ".join(['rezultati umjeravanja', self.plin]))
        self.slopeGroupBox.setTitle(", ".join(['funkcija prilagodbe', self.plin]))
        self.kriterijGroupBox.setTitle(", ".join(['kriterij prihvatljivosti', self.plin]))
        #postavi grafove
        self.inicijalizacija_grafova(self.plin)
        #postavi rezultate mjerenja
        self.tablicaRezultataUmjeravanja = QtGui.QWidget()
        self.rezultatLayout.addWidget(self.tablicaRezultataUmjeravanja)
        rezultat = self.generiraj_nan_frejm_rezultata_umjeravanja()
        self.postavi_tablicu_rezultata_umjeravanja(rezultat)
        #slope i offset data
        self.tablicaPrilagodba = pomocni.TablicaFunkcijePrilagodbe()
        self.slopeLayout.addWidget(self.tablicaPrilagodba)
        #kriterij
        self.tablicaParametri = pomocni.TablicaUmjeravanjeKriterij()
        self.kriterijLayout.addWidget(self.tablicaParametri)
        #model za tablicu
        self.model = SiroviFrameModel(tocke=self.datastore.get_tocke(self.plin),
                                      frejm=self.datastore.tabData[self.plin].get_frejm(),
                                      start=self.datastore.tabData[self.plin].get_startIndeks())

    def get_model(self):
        return self.model

    def set_model(self, model):
        self.model = model

    def generiraj_nan_frejm_rezultata_umjeravanja(self):
        """generiranje izlaznog frejma za prikaz"""
        tocke = self.datastore.get_tocke(self.plin)
        frejm = pd.DataFrame(
            columns=['cref', 'U', 'c', u'\u0394', 'sr', 'r'],
            index=list(range(len(tocke))))
        return frejm

    def inicijalizacija_grafova(self, plin):
        """inicijalizacija i postavljanje kanvasa za grafove u layout.
        ulazni parametar plin je naziv (string) izabranog plina"""
        meta1 = {'xlabel':'referentna koncentracija, cref',
                 'ylabel':'koncentracija, c',
                 'title':", ".join(['Cref / koncentracija graf', str(plin)])}
        meta2 = {'xlabel':'vrijeme',
                 'ylabel':'koncentracija, c',
                 'title':", ".join(['Individualna mjerenja', str(plin)])}
        self.crefCanvas = canvas.Kanvas(meta=meta1)
        self.mjerenjaCanvas = canvas.KanvasMjerenja(meta=meta2)
        self.graf1Layout.addWidget(self.crefCanvas)
        self.graf2Layout.addWidget(self.mjerenjaCanvas)

    def postavi_tablicu_rezultata_umjeravanja(self, rezultat):
        """
        metoda koja generira tablicu umjeravanja i postavlja je u specificno mjesto
        u layoutu.

        input je frejm rezultata
        """
        #korak 1, maknuti widget iz layouta
        self.rezultatLayout.removeWidget(self.tablicaRezultataUmjeravanja)
        #korak 2, moram zatvoriti widget (garbage collection...)
        sip.delete(self.tablicaRezultataUmjeravanja)
        self.tablicaRezultataUmjeravanja = None
        #self.tablicaRezultataUmjeravanja.destroy()
        gc.collect() #force garbage collection
        #korak 3, stvaram novi widget (tablicu) i dodjelujem je istom imenu
        frejm = rezultat.copy()
        try:
            self.tablicaRezultataUmjeravanja = pomocni.TablicaUmjeravanje(
                tocke=self.datastore.get_tocke(self.plin),
                data=frejm,
                jedinica=self.datastore.get_izabranaMjernaJedinica(),
                parent=None)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            self.tablicaRezultataUmjeravanja = pomocni.TablicaUmjeravanje(
                tocke=self.datastore.get_tocke(self.plin),
                data=self.generiraj_nan_frejm_rezultata_umjeravanja(),
                jedinica=self.datastore.get_izabranaMjernaJedinica(),
                parent=None)
        finally:
            #korak 4, insert novog widgeta na isto mjesto u layout
            self.rezultatLayout.addWidget(self.tablicaRezultataUmjeravanja)
            #korak 5, update layouta
            self.rezultatLayout.update()
            #korak 6, spajanje signala iz kontekstnog menija sa metodama za
            #dodavanje, editiranje i brisanje tocaka
            self.connect(self.tablicaRezultataUmjeravanja,
                         QtCore.SIGNAL('addrow'),
                         self.add_red_umjeravanje)
            self.connect(self.tablicaRezultataUmjeravanja,
                         QtCore.SIGNAL('removerow'),
                         self.remove_red_umjeravanje)
            self.connect(self.tablicaRezultataUmjeravanja,
                         QtCore.SIGNAL('editrow'),
                         self.edit_red_umjeravanje)

    def add_red_umjeravanje(self):
        """metoda (slot) za dodavanje tocaka u dokument"""
        self.emit(QtCore.SIGNAL('panel_dodaj_umjernu_tocku'))

    def remove_red_umjeravanje(self):
        """metoda za brisanje tocke za umjeravanje iz dokumenta"""
        red = self.tablicaRezultataUmjeravanja.get_redak()
        red = red - 1
        self.emit(QtCore.SIGNAL('panel_makni_umjernu_tocku(PyQt_PyObject)'),
                  red)

    def edit_red_umjeravanje(self):
        """metoda za editiranje umjerne tocke uz pomoc dijaloga"""
        red = self.tablicaRezultataUmjeravanja.get_redak()
        red = red - 1
        self.emit(QtCore.SIGNAL('panel_edit_umjernu_tocku(PyQt_PyObject)'),
                  red)

    def update_rezultat(self, mapa):
        """
        update gui elemenata panela ovisno o prosljedjenim parametrima u mapi
        """
        rezultat = mapa['umjeravanje']
        slopeData = mapa['prilagodba'] #dictionary (slope, offset, prilagodbaA, prilagodbaB)
        testovi = mapa['testovi'] #dictionary... koji ima kljuceve : srz, srs, rz, rmax...
        #grafovi
        self.prikazi_grafove(rezultat, slopeData)
        #rezultati
        self.postavi_tablicu_rezultata_umjeravanja(rezultat)
        #prilagodba
        prilagodba = [str(round(slopeData['prilagodbaA'], 3)), str(round(slopeData['prilagodbaB'], 1))]
        #invalid value encountered in rint
        self.tablicaPrilagodba.set_values(prilagodba)
        #hide ako je umjeravanje off
        if self.datastore.get_checkUmjeravanje():
            self.rezultatiGroupBox.show()
            self.slopeGroupBox.show()
        else:
            self.rezultatiGroupBox.hide()
            self.slopeGroupBox.hide()
        #testovi
        kriterij = []
        if self.datastore.get_checkPonovljivost():
            kriterij.append(testovi['srz'])
            kriterij.append(testovi['srs'])
        if self.datastore.get_checkLinearnost():
            kriterij.append(testovi['rz'])
            kriterij.append(testovi['rmax'])
        self.tablicaParametri.set_values(kriterij)
        if len(kriterij):
            self.kriterijGroupBox.show()
        else:
            self.kriterijGroupBox.hide()

    def prikazi_grafove(self, rezultat, slopeData):
        """
        Metoda za crtanje grafova, ulazni parametri su frejm rezultata umjeravanja
        i mapa sa podacima za 'slope', 'offset', 'prilagodbaA', 'prilagodbaB'
        """
        self.crefCanvas.clear_graf()
        self.mjerenjaCanvas.clear_graf()
        #dohvati rezultat umjeravanja:
        testLinearnosti = self.datastore.get_checkLinearnost()
        tocke = self.datastore.get_tocke(self.plin)
        frejm = self.datastore.tabData[self.plin].get_frejm()
        if self.plin in frejm.columns:
            x = list(rezultat.loc[:, 'cref'])
            y = list(rezultat.loc[:, 'c'])
            if testLinearnosti:
                slope = slopeData['slope']
                offset = slopeData['offset']
                self.crefCanvas.set_slope_offset(slope, offset)
            else:
                self.crefCanvas.set_slope_offset(None, None)
            self.crefCanvas.crtaj(x, y)

            frejm = frejm.copy()
            frejm = frejm.loc[:, self.plin]
            if testLinearnosti:
                self.mjerenjaCanvas.crtaj(frejm, tocke)
            else:
                z, s = pomocni.pronadji_zero_span_tocke(tocke)
                zs = [z, s]
                self.mjerenjaCanvas.crtaj(frejm, zs)


