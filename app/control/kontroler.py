# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 12:51:48 2016

@author: DHMZ-Milic
"""
import os
import copy
import pickle
import logging
import configparser
from PyQt4 import QtCore, QtGui
from app.model import dokument
from app.model.konfig_objekt import MainKonfig
from app.view import display
from app.view import dijalog_dilucija
from app.view import dijalog_cistiZrak
from app.view import dijalog_uredjaj
from app.view import dijalog_komponenta
from app.view import dijalog_metoda


class Kontroler(QtGui.QWidget):
    """
    Kontroler aplikacije.
    -Prilikom inicijalizacije podize instancu konfiga, dokumenta i gui-a.
    -Sadrzi glavni 'workflow' programa
    -'most' izmedju dokumenta i displaya.
    """
    def __init__(self, parent=None):
        """
        Ulazni argumenti:
        -parent : parent objekta
        """
        QtGui.QWidget.__init__(self, parent=parent)
        #inicijalni setup iz konfiga
        config = configparser.ConfigParser()
        try:
            config.read('umjeravanje_konfig.cfg', encoding='utf-8')
            self.setup_logging(konfig=config)
            self.konfig = MainKonfig(cfg = config)
        except OSError:
            logging.error('Pogreska prilikom ucitavanja konfiguracije.', exc_info=True)
            raise SystemExit('Kriticna pogreska, izlaz iz aplikacije.')

        self.dokument = dokument.Dokument(cfg=self.konfig)
        self.workingFolder = os.path.dirname(__file__)
        self.gui = display.GlavniProzor()
        self.otvoreniProzori = {} #podrska prozorima za prikupljanje podataka preko RS232 veze
        self.idCounter = 1 #podrska prozorima za prikupljanje podataka preko RS232 veze
        self.gui.show() #prikaz guia na ekranu.
        self.setup_connections()


    def set_workingFolder(self, x):
        """Metoda postavlja member working folder"""
        self.workingFolder = x

    def get_workingFolder(self, y):
        """Metoda vraca workinf folder aplikacije"""
        return self.workingFolder

    def setup_connections(self):
        """
        Definiranje komunikacije sa display-om
        """
        #signalizacija nakon sto se gui ugasi.
        self.connect(self.gui,
                     QtCore.SIGNAL('gui_terminated'),
                     self.close)
        #gui akcije
        self.gui.action_edit_kalibracijska_jedinica.triggered.connect(self.edit_kalibracijske_jedinice)
        self.gui.action_edit_generator_cistog_zraka.triggered.connect(self.edit_generatore_zraka)
        self.gui.action_dodaj_novu_komponentu.triggered.connect(self.dodaj_novu_komponentu)
        self.gui.action_dodaj_novu_analiticku_metodu.triggered.connect(self.edit_analiticku_metodu)
        self.gui.action_edit_uredjaj.triggered.connect(self.edit_uredjaje)
        self.gui.action_new.triggered.connect(self.new_umjeravanje)
        self.gui.action_load.triggered.connect(self.load_umjeravanja)

    def test_za_previse_umjeravanja(self):
        """Metoda vraca True ako ima vise od 10 trenutno otvorenih umjeravanja,
        False inace"""
        aktivnaUmjeravanja = self.gui.mdiArea.subWindowList()
        if len(aktivnaUmjeravanja) >= 10:
            msg = 'Trenutno postoji 10 aktivnih umjeravanja u aplikaciji. Ako hocete otvoriti jos jedno umjeravanje morati cete ugasiti neko postojece.'
            QtGui.QMessageBox.information(self.gui, 'Previse aktivnih umjeravanja', msg)
            return True
        else:
            return False

    def load_umjeravanja(self):
        """load procedura za spremljeno umjeravanje"""
        try:
            if self.test_za_previse_umjeravanja():
                return None
            selectedFilters = "All files (*.*);;Umjeravanja (*.kal)"
            path = QtGui.QFileDialog.getOpenFileName(self, 'Otvori umjeravanje', self.workingFolder, selectedFilters)
            if path:
                with open(path, 'rb') as the_file:
                    txt = the_file.read() #read all
                    data = pickle.loads(txt) #unserialize datastore
                    self.gui.load_umjeravanje(path=path, data=data)
        except Exception as err:
            QtGui.QMessageBox.warning(self, 'Problem', 'Umjeravanje nije uspjesno ucitano.\n{0}'.format(str(err)))
            logging.error(str(err), exc_info=True)

    def new_umjeravanje(self):
        """Metoda otvara dijalog za izbor uredjaja, kalibracijske jedinice i generatora
        cistog zraka. Metoda poziva metodu gui-a zaduzenu sa stvaranje novog prozora umjeravanja."""
        if self.test_za_previse_umjeravanja():
            return None

        popis = self.dokument.get_listu_uredjaja()
        ure, ok = QtGui.QInputDialog.getItem(self.gui,
                                             'Izbor uredjaja',
                                             'Uredjaj :',
                                             popis,
                                             editable=False)
        if ok:
            try:
                ure = self.dokument.get_kopiju_uredjaja(ure)
            except Exception as err:
                logging.warning(str(err), exc_info=True)
                QtGui.QMessageBox.information(self.gui, 'Problem', 'Izabrani uredjaj ne postoji u dokumentu.')
                return None
            dilucije = copy.deepcopy(self.dokument.dilucijskeJedinice)
            generatori = copy.deepcopy(self.dokument.generatoriCistogZraka)
            lokacije = self.dokument.get_listu_postaja()
            konfigfile = 'umjeravanje_konfig.cfg'
            #nardedi stvaranje objekta.
            self.gui.new_umjeravanje(uredjaj=ure,
                                     generatori=generatori,
                                     dilucije=dilucije,
                                     postaje=lokacije,
                                     cfg=konfigfile,
                                     folder=self.workingFolder)

    def dodaj_novu_komponentu(self):
        """poziv dijaloga za dodavanje nove komponente u dokument"""
        tegla = pickle.dumps(self.dokument)
        dijalog = dijalog_komponenta.DijalogKomponenta(dokument=tegla)
        self.gui.statusBar().showMessage("Otvoren dijalog za edit komponentama.", 2000)
        ok = dijalog.exec_()
        if ok:
            tegla = dijalog.get_dokument()
            self.dokument = pickle.loads(tegla)

    def edit_kalibracijske_jedinice(self):
        """poziv dijaloga za editiranje kalibracijskih jedinica u dokumentu"""
        tegla = pickle.dumps(self.dokument)
        dijalog = dijalog_dilucija.DijalogDilucija(dokument=tegla)
        self.gui.statusBar().showMessage("Otvoren dijalog za edit kalibracijskih jedinica.", 2000)
        ok = dijalog.exec_()
        if ok:
            tegla = dijalog.get_dokument()
            self.dokument = pickle.loads(tegla)

    def edit_generatore_zraka(self):
        """poziv dijaloga za editiranje generatora cistog zraka u dokumentu"""
        tegla = pickle.dumps(self.dokument)
        dijalog = dijalog_cistiZrak.DijalogCistiZrak(dokument=tegla)
        self.gui.statusBar().showMessage("Otvoren dijalog za edit generatora cistog zraka.", 2000)
        ok = dijalog.exec_()
        if ok:
            tegla = dijalog.get_dokument()
            self.dokument = pickle.loads(tegla)

    def edit_uredjaje(self):
        """poziv dijaloga za editiranje uredjaja u dokumentu"""
        tegla = pickle.dumps(self.dokument)
        dijalog = dijalog_uredjaj.DijalogUredjaj(dokument=tegla)
        self.gui.statusBar().showMessage("Otvoren dijalog za edit uredjajima.", 2000)
        ok = dijalog.exec_()
        if ok:
            tegla = dijalog.get_dokument()
            self.dokument = pickle.loads(tegla)

    def edit_analiticku_metodu(self):
        """Poziv dijaloga za editiranje analiticke metode"""
        tegla = pickle.dumps(self.dokument)
        dijalog = dijalog_metoda.DijalogAnalitickaMetoda(dokument=tegla)
        self.gui.statusBar().showMessage("Otvoren dijalog za edit analitickih metoda.", 2000)
        ok = dijalog.exec_()
        if ok:
            tegla = dijalog.get_dokument()
            self.dokument = pickle.loads(tegla)

    def setup_logging(self, konfig=None):
        """Inicijalizacija loggera"""
        DOZVOLJENI = {'DEBUG': logging.DEBUG,
                      'INFO': logging.INFO,
                      'WARNING': logging.WARNING,
                      'ERROR': logging.ERROR,
                      'CRITICAL': logging.CRITICAL}
        try:
            filename = konfig.get('LOG_SETUP', 'file', fallback='applog.log')
            filemode = konfig.get('LOG_SETUP', 'mode', fallback='a')
            level = konfig.get('LOG_SETUP', 'lvl', fallback='INFO')

            if level in DOZVOLJENI:
                level = DOZVOLJENI[level]
            else:
                level = logging.ERROR
            if filemode not in ['a', 'w']:
                filemode = 'a'
            logging.basicConfig(level=level,
                                filename=filename,
                                filemode=filemode,
                                format='{levelname}:::{asctime}:::{module}:::{funcName}:::LOC:{lineno}:::{message}',
                                style='{')
        except Exception as err:
            print('Pogreska prilikom konfiguracije loggera.')
            print(err)
            raise SystemExit('Kriticna greska, izlaz iz aplikacije.')
