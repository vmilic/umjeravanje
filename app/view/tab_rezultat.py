# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 10:50:23 2015

@author: DHMZ-Milic
"""
import sip
import gc
import logging
import pandas as pd
from PyQt4 import QtGui, QtCore, uic
import app.view.canvas as canvas
import app.view.pomocni as view_helpers

BASE4, FORM4 = uic.loadUiType('./app/view/uiFiles/tab_rezultat.ui')
class RezultatPanel(BASE4, FORM4):
    """
    Panel za prikaz rezultata umjeravanja.

    novi memberi za set/get i ponasanje taba (tablica sa testovima za mjerenje)

    self.checkBoxReport
    self.checkBoxUmjeravanje
    self.checkBoxPonovljivost
    self.checkBoxLinearnost
    """
    def __init__(self, dokument=None, plin=None, parent=None):
        super(BASE4, self).__init__(parent)
        self.setupUi(self)
        self.dokument = dokument
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
        self.tablicaPrilagodba = view_helpers.TablicaFunkcijePrilagodbe()
        self.slopeLayout.addWidget(self.tablicaPrilagodba)
        #kriterij
        self.tablicaParametri = view_helpers.TablicaUmjeravanjeKriterij()
        self.kriterijLayout.addWidget(self.tablicaParametri)

    def generiraj_nan_frejm_rezultata_umjeravanja(self):
        """generiranje izlaznog frejma za prikaz"""
        tocke = self.dokument.get_tocke(mjerenje=self.plin)
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
            self.tablicaRezultataUmjeravanja = view_helpers.TablicaUmjeravanje(
                tocke=self.dokument.get_tocke(mjerenje=self.plin),
                data=frejm,
                jedinica=self.dokument.get_mjernaJedinica(),
                parent=None)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            self.tablicaRezultataUmjeravanja = view_helpers.TablicaUmjeravanje(
                tocke=self.dokument.get_tocke(mjerenje=self.plin),
                data=self.dokument.generiraj_nan_frejm_rezultata_umjeravanja(),
                jedinica=self.dokument.get_mjernaJedinica(),
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
        slopeData = mapa['prilagodba'] #lista(slope, offset, prilagodbaA, prilagodbaB)
        testovi = mapa['testovi'] #dictionary... koji ima kljuceve : srz, srs, rz, rmax...
        #grafovi
        self.prikazi_grafove(rezultat, slopeData)
        #rezultati
        self.postavi_tablicu_rezultata_umjeravanja(rezultat)
        #prilagodba
        prilagodba = [str(round(slopeData['prilagodbaA'], 3)), str(round(slopeData['prilagodbaB'], 1))]
        self.tablicaPrilagodba.set_values(prilagodba)
        #hide ako je umjeravanje off
        if self.dokument.get_provjeraUmjeravanje():
            self.rezultatiGroupBox.show()
            self.slopeGroupBox.show()
        else:
            self.rezultatiGroupBox.hide()
            self.slopeGroupBox.hide()
        #testovi
        kriterij = []
        if self.dokument.get_provjeraPonovljivost():
            kriterij.append(testovi['srz'])
            kriterij.append(testovi['srs'])
        if self.dokument.get_provjeraLinearnost():
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
        testLinearnosti = self.dokument.get_provjeraLinearnost()
        tocke = self.dokument.get_tocke(mjerenje=self.plin)
        mjerenja = self.dokument.get_mjerenja()
        mjerenje = mjerenja[self.plin]
        model = mjerenje['model']
        frejm = model.get_frejm()
        calc = mjerenje['kalkulator']

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
                z, s = calc.pronadji_zero_span_tocke()
                zs = [z, s]
                self.mjerenjaCanvas.crtaj(frejm, zs)
