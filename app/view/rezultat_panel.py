# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 10:50:23 2015

@author: DHMZ-Milic
"""
import sip
import gc
import logging
from PyQt4 import QtGui, QtCore, uic
import app.view.canvas as canvas
import app.view.pomocni as view_helpers


BASE5, FORM5 = uic.loadUiType('./app/view/uiFiles/rezultat_panel.ui')
class RezultatPanel(BASE5, FORM5):
    """
    Panel za prikaz rezultata umjeravanja.

    layouts:
        self.graf1Layout --> graf c/cref
        self.graf2Layout --> graf vrijeme/tocke
        self.rezultatiLayout --> tablica frejma rezultata (cref, c, U, delta...)
        self.slopeLayout --> tablica sa parametrime prilagodbe
        self.kriterijLayout --> tablica kriterija prihvatljivosti
    """
    def __init__(self, dokument=None, plin=None, parent=None):
        super(BASE5, self).__init__(parent)
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
        rezultat = self.dokument.generiraj_nan_frejm_rezultata_umjeravanja()
        self.postavi_tablicu_rezultata_umjeravanja(rezultat)
        #slope i offset data
        self.tablicaPrilagodba = view_helpers.TablicaFunkcijePrilagodbe()
        self.slopeLayout.addWidget(self.tablicaPrilagodba)
        #kriterij
        self.tablicaParametri = view_helpers.TablicaUmjeravanjeKriterij()
        self.kriterijLayout.addWidget(self.tablicaParametri)

    def get_pdf_elements(self):
        """metoda vraca elemente za pdf report u obliku dicta"""
        #TODO!
        pass
        #kriterij
        #tablica rezultata
        #prilagodba


    def update_rezultat(self, mapa):
        """
        update gui elemenata panela ovisno o prosljedjenim parametrima u mapi
        """
        rezultat = mapa['rezultat']
        slopeData = mapa['slopeData'] #lista(slope, offset, prilagodbaA, prilagodbaB)
        kriterij = mapa['kriterij'] #nested lista(srz, srs, rz, rmax), svaki ima podatke o kriteriju
        #grafovi
        self.prikazi_grafove(rezultat, slopeData)
        #rezultati
        self.postavi_tablicu_rezultata_umjeravanja(rezultat)
        #prilagodba
        prilagodba = [str(round(slopeData[2], 3)), str(round(slopeData[3], 1))]
        self.tablicaPrilagodba.set_values(prilagodba)
        #kriterij
        self.tablicaParametri.set_values(kriterij)

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
                tocke=self.dokument.get_tockeUmjeravanja(),
                data=frejm,
                jedinica=self.dokument.get_mjernaJedinica(),
                parent=None)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            self.tablicaRezultataUmjeravanja = view_helpers.TablicaUmjeravanje(
                tocke=self.dokument.get_tockeUmjeravanja(),
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
        self.emit(QtCore.SIGNAL('panel_makni_umjernu_tocku(PyQt_PyObject)'),
                  red)

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

    def prikazi_grafove(self, rezultat, slopeData):
        """
        Metoda za crtanje grafova, ulazni parametri su frejm rezultata umjeravanja
        i podaci (lista) slope, offset i prilagodba
        """
        self.crefCanvas.clear_graf()
        self.mjerenjaCanvas.clear_graf()

        #dohvati rezultat umjeravanja:
        testLinearnosti = self.dokument.get_provjeraLinearnosti()
        tocke = self.dokument.get_tockeUmjeravanja()
        frejm = self.dokument.get_siroviPodaci()

        if self.plin in frejm.columns:
            x = list(rezultat.loc[:, 'cref'])
            y = list(rezultat.loc[:, 'c'])
            if testLinearnosti:
                slope = slopeData[0]
                offset = slopeData[1]
                self.crefCanvas.set_slope_offset(slope, offset)
            else:
                self.crefCanvas.set_slope_offset(None, None)
            self.crefCanvas.crtaj(x, y)

            frejm = frejm.copy()
            frejm = frejm.loc[:, self.plin]
            if testLinearnosti:
                self.mjerenjaCanvas.crtaj(frejm, tocke)
            else:
                zs = self.dokument.get_zero_span_tocke()
                self.mjerenjaCanvas.crtaj(frejm, zs)

