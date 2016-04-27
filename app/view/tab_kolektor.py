# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 09:00:51 2015

@author: DHMZ-Milic

Sve potrebno za tab 'Prikupljanje podataka'
"""
import logging
import datetime
import pandas as pd
from PyQt4 import QtCore, QtGui, uic
from app.view.canvas import GrafPreuzetihPodataka
from app.model.qt_models import BareFrameModel
import app.model.veza as veza
import app.model.protokol as prot
import app.model.komunikacija as kom
import app.view.izbor_naziva_stupaca_wizard as izbor_stupaca
import app.view.postavke_veze_wizard as postavke_veze



BASE_TAB_KOLEKTOR, FORM_TAB_KOLEKTOR = uic.loadUiType('./app/view/uiFiles/tab_kolektor.ui')
class Kolektor(BASE_TAB_KOLEKTOR, FORM_TAB_KOLEKTOR):
    """
    Panel za prikupljanje podataka od instrumenta
    """
    def __init__(self, uredjaj=None, konfig=None, parent=None, datastore=None):
        super(BASE_TAB_KOLEKTOR, self).__init__(parent)
        self.setupUi(self)

        self.headeri = [] #TODO!
        self.tempFileName = "_".join(['kolektor_data', datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')])

        self.datastore = datastore
        self.plin = 'kolektor'
        self.konfig = konfig
        self.uredjaj = uredjaj
        ### setup komunikacijskog objekta u odvojenom threadu ###
        self.komThread = QtCore.QThread()
        self.veza = veza.RS232Veza()
        self.koristeniSerialPort = None
        self.protokol = prot.HessenBCC()
        self.komObjekt = kom.KomunikacijskiObjekt(veza=self.veza,
                                                  protokol=self.protokol,
                                                  parent=None)
        self.komObjekt.moveToThread(self.komThread)
        ### setup grafa za prikaz podataka ###
        self.meta = {'xlabel':'vrijeme',
                     'ylabel':'koncentracija',
                     'title':'Prikupljeni podaci'}
        self.graf = GrafPreuzetihPodataka(meta=self.meta)
        self.layoutZaGraf.addWidget(self.graf)
        ### setup tablice i ostalih membera ###
        self.frejm = pd.DataFrame()
        self.raspon_grafa = int(self.rasponCombo.currentText())
        self.bareFrejmModel = BareFrameModel(frejm=self.frejm)
        self.stopButton.setEnabled(False)
        sr = str(self.komObjekt.get_sample_rate())
        self.sampleCombo.setCurrentIndex(self.sampleCombo.findText(sr))
        self.setup_connections()
        #postavi max vrijednost ovisno o opsegu...
        self.doubleSpinBoxMaxY.setValue(self.datastore.get_izabraniOpseg())


    def get_model(self):
        """Metoda vraca frejm model preuzetih podataka"""
        return self.bareFrejmModel

    def update_table_view(self):
        """signal gui view update"""
        self.emit(QtCore.SIGNAL('update_table_view'))

    def setup_connections(self):
        self.startButton.clicked.connect(self.start_handle)
        self.stopButton.clicked.connect(self.stop_handle)
        self.sampleCombo.currentIndexChanged.connect(self.promjeni_period_uzorkovanja)
        self.clearButton.clicked.connect(self.reset_frejm)
        self.spremiButton.clicked.connect(self.spremi_frejm)
        self.postavkeButton.clicked.connect(self.prikazi_wizard_postavki)
        self.rasponCombo.currentIndexChanged.connect(self.promjeni_vremenski_raspon_grafa)

        self.doubleSpinBoxMinY.valueChanged.connect(self.pomakni_ymin)
        self.doubleSpinBoxMaxY.valueChanged.connect(self.pomakni_ymax)

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

    def pomakni_ymin(self, x):
        """pomak min y raspona grafa"""
        self.graf.set_ymin(x)
        if len(self.frejm):
            self.graf.crtaj(frejm=self.frejm, raspon=self.raspon_grafa)

    def pomakni_ymax(self, x):
        """pomak max y raspona grafa"""
        self.graf.set_ymax(x)
        if len(self.frejm):
            self.graf.crtaj(frejm=self.frejm, raspon=self.raspon_grafa)

    def get_used_serial(self):
        """
        Metoda vraca koristeni serial port ili None...
        """
        return self.koristeniSerialPort

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

    def upisi_podatke_u_temp_file(self, plinovi, indeks, value):
        """
        upisivanje preuzetih podataka u csv file...

        plinovi = lista plinova
        indeks = datetime objekt vremena zaprimanja podataka
        value = mapa vrijednosti
        """
        with open(self.tempFileName, mode='a') as teh_fajl:
            if len(self.frejm) == 0:
                self.headeri = ['vrijeme']
                for i in plinovi:
                    self.headeri.append(i)
                headerLine = ','.join(self.headeri)
                headerLine = ''.join([headerLine, '\n'])
                teh_fajl.write(headerLine)
                vrijednosti = []
                for i in self.headeri:
                    if i == 'vrijeme':
                        vrijednosti.append(indeks.strftime('%Y-%m-%d %H:%M:%S'))
                    else:
                        vrijednosti.append(str(value[i][2]))
                vrijednostiLine = ','.join(vrijednosti)
                vrijednostiLine = ''.join([vrijednostiLine, '\n'])
                teh_fajl.write(vrijednostiLine)
            else:
                headerLine = ','.join(self.headeri)
                vrijednosti = []
                for i in self.headeri:
                    if i == 'vrijeme':
                        vrijednosti.append(indeks.strftime('%Y-%m-%d %H:%M:%S'))
                    else:
                        vrijednosti.append(str(value[i][2]))
                vrijednostiLine = ','.join(vrijednosti)
                vrijednostiLine = ''.join([vrijednostiLine, '\n'])
                teh_fajl.write(vrijednostiLine)


    def dodaj_vrijednost_frejmu(self, value):
        """
        metoda dodaje preuzetu vrijednost komunikacijskog objekta u frejm
        """
        try:
            plinovi = list(value.keys())
            indeks = value[plinovi[0]][0] #podatak o vremenu

            #temp file za kolektor podatke.
            self.upisi_podatke_u_temp_file(plinovi, indeks, value)

            row = {}
            for plin in plinovi:
                row[plin] = float(value[plin][2])
            tmp = pd.DataFrame(row, index=[indeks])
            self.frejm = self.frejm.append(tmp)
            self.graf.crtaj(frejm=self.frejm, raspon=self.raspon_grafa)
            self.bareFrejmModel.set_frejm(self.frejm)
            self.update_table_view()

        except Exception as err:
            logging.error(str(err), exc_info=True)
            pass

    def promjeni_period_uzorkovanja(self, x):
        value = int(self.sampleCombo.currentText())
        self.komObjekt.set_sample_rate(value)

    def promjeni_vremenski_raspon_grafa(self, x):
        value = int(self.rasponCombo.currentText())
        self.raspon_grafa = value
        if len(self.frejm):
            self.graf.crtaj(frejm=self.frejm, raspon=self.raspon_grafa)

    def reset_frejm(self):
        """clear trenutnih podataka u frejmu...nema backupa"""
        self.frejm = pd.DataFrame()
        self.bareFrejmModel.set_frejm(self.frejm)
        self.update_table_view()
        self.graf.reset_graf()

    def spremi_frejm(self):
        """
        Spremanje prezuetih podataka.

        Emitira se signal sa 4 podatka:
        1. minutno usrednjeni podaci (za umjeravanje i provjeru konvertera)
        2. sirovi podaci (sekundna rezolucija, za provjeru odaziva)
        3. serijski broj uredjaja sa kojeg stizu podaci
        4. mapa sa podacima u koje se tabove trebaju prebaciti podaci
        """
        tempFrejm = self.frejm.copy()
        moguceKomponente = self.uredjaj.get_listu_komponenti()
        izborStupaca = izbor_stupaca.IzborNazivaStupacaWizard(frejm=tempFrejm,
                                                              moguci=moguceKomponente,
                                                              uredjaj=self.uredjaj)
        prihvacen = izborStupaca.exec_()
        if prihvacen:
            minutniFrejm = izborStupaca.get_minutni_frejm()
            sekundniFrejm = izborStupaca.get_sekundni_frejm()
            #pakiranje i emit podataka aplikaciji
            output = {'podaci':sekundniFrejm,
                      'minutniPodaci':minutniFrejm,
                      'uredjaj':self.uredjaj.get_serial()}
            self.emit(QtCore.SIGNAL('spremi_preuzete_podatke(PyQt_PyObject)'),
                      output)

    def prikazi_wizard_postavki(self):
        """
        Promjena postavki veze. Ovisno o rezultatima wizarda treba inicijalizirati
        nove objekte Protokol() i Veza() te ih postaviti u komunikacijski objekt
        """
        usedPorts = self.parent().parent().parent().get_koristene_serial_portove()
        wiz = postavke_veze.PostavkeVezeWizard(uredjaj=self.uredjaj, konfig=self.konfig, used=usedPorts)
        prihvacen = wiz.exec_()
        if prihvacen:
            postavke = wiz.get_postavke_veze()
            #set veze
            if postavke['veza'] == 'RS-232':
                tekst = 'Uredjaj {0}, veza: {1}, protokol: {2}, port: {3}'.format(postavke['uredjaj'], postavke['veza'], postavke['protokol'], postavke['port'])
                self.opisLabel.setText(tekst)
                self.veza = veza.RS232Veza()
                self.koristeniSerialPort = postavke['port']
                self.veza.setup_veze(port=postavke['port'],
                                     baudrate=postavke['brzina'],
                                     bytesize=postavke['brojBitova'],
                                     parity=postavke['paritet'],
                                     stopbits=postavke['stopBitovi'],
                                     xonxoff=postavke['xon/xoff'],
                                     rtscts=postavke['rts/cts'])
            self.komObjekt.set_veza(self.veza)
            #set protokola komunikacije
            temp = postavke['protokol']
            if temp == 'Hessen, BCC':
                self.protokol = prot.HessenBCC()
            elif temp == 'Hessen, text':
                self.protokol = prot.HessenText()
            self.komObjekt.set_protokol(self.protokol)
            #enable gumbe za prikupljanje
            self.startButton.setEnabled(True)
            self.stopButton.setEnabled(False)
            self.sampleCombo.setEnabled(True)
            self.clearButton.setEnabled(True)
            self.spremiButton.setEnabled(True)
            self.rasponCombo.setEnabled(True)
            return True
        else:
            return False
