# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 09:00:51 2015

@author: DHMZ-Milic

Sve potrebno za tab 'Prikupljanje podataka'
"""

import logging
import pandas as pd
from PyQt4 import QtCore, QtGui, uic
import app.model.komunikacija as kom
import app.model.protokol as prot
import app.model.veza as veza
import app.model.frejm_model as fmodel
import app.view.canvas as canvas
import app.view.postavke_veze_wizard as postavke_veze
import app.view.izbor_naziva_stupaca_wizard as izbor_stupaca


BASE2, FORM2 = uic.loadUiType('./app/view/uiFiles/tab_kolektor.ui')
class Kolektor(BASE2, FORM2):
    """
    Panel za prikupljanje podataka od instrumenta
    """
    def __init__(self, dokument=None, parent=None, uid=0):
        super(BASE2, self).__init__(parent)
        self.setupUi(self)

        ### setup komunikacijskog objekta u odvojenom threadu ###
        self.komThread = QtCore.QThread()

        self.veza = veza.RS232Veza()
        self.protokol = prot.HessenBCC()

        self.komObjekt = kom.KomunikacijskiObjekt(veza=self.veza,
                                                  protokol=self.protokol,
                                                  parent=None)

        self.komObjekt.moveToThread(self.komThread)

        ### setup grafa za prikaz podataka ###
        self.meta = {'xlabel':'vrijeme',
                     'ylabel':'koncentracija',
                     'title':'Prikupljeni podaci'}
        self.graf = canvas.GrafPreuzetihPodataka(meta=self.meta)
        self.layoutZaGraf.addWidget(self.graf)

        ### setup tablice i ostalih membera ###
        self.uid = uid #unique ID
        self.doc = dokument
        self.spojeni_uredjaj = None
        self.frejm = pd.DataFrame()
        self.raspon_grafa = int(self.rasponCombo.currentText())
        self.bareFrejmModel = fmodel.BareFrameModel(frejm=self.frejm)
        self.dataTableView.setModel(self.bareFrejmModel)
        self.stopButton.setEnabled(False)

        self.setup_connections()

    def setup_connections(self):
        self.startButton.clicked.connect(self.start_handle)
        self.stopButton.clicked.connect(self.stop_handle)
        self.sampleCombo.currentIndexChanged.connect(self.promjeni_period_uzorkovanja)
        self.clearButton.clicked.connect(self.reset_frejm)
        self.spremiButton.clicked.connect(self.spremi_frejm)
        self.postavkeButton.clicked.connect(self.prikazi_wizard_postavki)
        self.rasponCombo.currentIndexChanged.connect(self.promjeni_vremenski_raspon_grafa)

        self.connect(self,
                     QtCore.SIGNAL('start_prikupljanje_podataka'),
                     self.komObjekt.start_prikupljati_podatke)

        self.connect(self.komObjekt,
                     QtCore.SIGNAL('nova_vrijednost_od_veze(PyQt_PyObject)'),
                     self.dodaj_vrijednost_frejmu)
        #callback za error u radu komunikaicjskog objekta
        self.connect(self.komObjekt,
                     QtCore.SIGNAL('problem_sa_prikupljanjem_podataka(PyQt_PyObject)'),
                     self.prikazi_warning_popup)

    def closeEvent(self, event):
        """overloaded signal za close - cilj je zaustaviti prikupljanje podataka"""
        self.stop_handle()
        event.accept()

    def prikazi_warning_popup(self, poruka):
        """ popup warning dijalog as opisom problema i zaustavi prikupljanje"""
        self.stop_handle()
        QtGui.QMessageBox.warning(self, 'Problem', poruka)

    def start_handle(self):
        """
        metoda zapocinje prikupljanje podataka
        """
        #enable & disable some buttons
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.sampleCombo.setEnabled(False)
        self.clearButton.setEnabled(False)
        self.spremiButton.setEnabled(False)
        self.postavkeButton.setEnabled(False)
        self.komThread.start()
        self.emit(QtCore.SIGNAL('start_prikupljanje_podataka'))

    def stop_handle(self):
        """
        metoda prekida skupljanje podataka
        """
        self.komThread.exit()
        self.komObjekt.stop_prikupljati_podatke()
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.sampleCombo.setEnabled(True)
        self.clearButton.setEnabled(True)
        self.spremiButton.setEnabled(True)
        self.postavkeButton.setEnabled(True)

    def dodaj_vrijednost_frejmu(self, value):
        """
        metoda dodaje preuzetu vrijednost komunikacijskog objekta u frejm
        """
        try:
            plinovi = list(value.keys())
            indeks = value[plinovi[0]][0] #podatak o vremenu
            row = {}
            for plin in plinovi:
                row[plin] = float(value[plin][2])
            tmp = pd.DataFrame(row, index=[indeks])
            self.frejm = self.frejm.append(tmp)
            self.graf.crtaj(frejm=self.frejm, raspon=self.raspon_grafa)
            self.bareFrejmModel.set_frejm(self.frejm)
            self.dataTableView.update()
        except Exception as err:
            logging.error(str(err), exc_info=True)
            pass

    def promjeni_period_uzorkovanja(self, x):
        value = int(self.sampleCombo.currentText())
        self.komObjekt.set_sample_rate(value)

    def promjeni_vremenski_raspon_grafa(self, x):
        value = int(self.rasponCombo.currentText())
        self.raspon_grafa = value

    def reset_frejm(self):
        """clear trenutnih podataka u frejmu...nema backupa"""
        self.frejm = pd.DataFrame()
        self.bareFrejmModel.set_frejm(self.frejm)
        self.dataTableView.update()
        self.graf.reset_graf()


    def spremi_frejm(self):
        """spremanje frejma... po potrebi resample na minutni raspon, koristeci
        average
        """
        tempFrejm = self.frejm.copy()
        moguceKomponente = self.doc.uredjaji[self.spojeni_uredjaj]['komponente']
        izborStupaca = izbor_stupaca.IzborNazivaStupacaWizard(frejm=tempFrejm, moguci=moguceKomponente)
        prihvacen = izborStupaca.exec_()
        if prihvacen and izborStupaca.izbor: #ako je wizard prihvacen i ako je prebacivanje podataka True
            minutniFrejm = izborStupaca.get_minutni_frejm()
            #pakiranje i emit podataka aplikaciji
            output = {'podaci':minutniFrejm,
                      'uredjaj':self.spojeni_uredjaj}
            self.emit(QtCore.SIGNAL('spremi_preuzete_podatke(PyQt_PyObject)'),
                      output)

    def prikazi_wizard_postavki(self):
        """
        Promjena postavki veze. Ovisno o rezultatima wizarda treba inicijalizirati
        nove objekte Protokol() i Veza() te ih postaviti u komunikacijski objekt
        """
        wiz = postavke_veze.PostavkeVezeWizard(dokument=self.doc)
        prihvacen = wiz.exec_()
        if prihvacen:
            postavke = wiz.get_postavke_veze()
            #set veze
            if postavke['veza'] == 'RS-232':
                self.spojeni_uredjaj = postavke['uredjaj']
                tekst = 'Uredjaj {0}, veza: {1}, protokol: {2}, port: {3}'.format(postavke['uredjaj'], postavke['veza'], postavke['protokol'], postavke['port'])
                self.opisLabel.setText(tekst)
                self.veza = veza.RS232Veza()
                self.veza.setup_veze(port=postavke['port'],
                                     baudrate=postavke['brzina'],
                                     bytesize=postavke['brojBitova'],
                                     parity=postavke['paritet'],
                                     stopbits=postavke['stopBitovi'])
            self.komObjekt.set_veza(self.veza)
            #set protokola komunikacije
            temp = postavke['protokol']
            if temp == 'Hessen, BCC':
                self.protokol = prot.HessenBCC()
            elif temp == 'Hessen, text':
                self.protokol = prot.HessenText()
            self.komObjekt.set_protokol(self.protokol)
            return True
        else:
            #cancel slucaj
            return False
