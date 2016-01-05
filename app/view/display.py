# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 09:41:20 2015

@author: DHMZ-Milic
"""
import gc
import sip
import logging
#import copy
import pickle
#import pandas as pd
from PyQt4 import QtGui, QtCore, uic
import app.reportgen.reportgen as pdfreport
import app.model.konfig_klase as konfig
import app.model.model as doc
import app.model.pomocne_funkcije as helperi
import app.view.read_file_wizard as datareader
import app.view.dijalog_edit_tocke as dotedit
import app.view.tab_rezultat as rezultat
import app.view.tab_postavke as postavke
import app.view.tab_kolektor as kolektor
import app.view.tab_konverter as konverter
import app.view.tab_odaziv as odaziv


BASE, FORM = uic.loadUiType('./app/view/uiFiles/display.ui')
class GlavniProzor(BASE, FORM):
    """
    Gui element glavnog prozora
    """
    def __init__(self, cfg=None, parent=None):
        super(BASE, self).__init__(parent)
        self.setupUi(self)
        ### setup konfig elemente ###
        try:
            self.konfiguracija = konfig.MainKonfig(cfg=cfg)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            raise SystemExit('Konfiguracijski file nije ispravan.')
        ### setup dokument ###
        self.dokument = doc.DokumentModel(cfg=self.konfiguracija)
        ### setup membere ###
        self.dictTabova = {}
        self.otvoreniProzori = {}
        self.idCounter = 1
        ### setup konstantne tabove ###
        self.tabPostavke = postavke.PostavkeTab(dokument=self.dokument)
        self.glavniTabWidget.addTab(self.tabPostavke, 'Postavke')
        self.siroviPodaciView.horizontalHeader().setStretchLastSection(True)
        ### Setup signala i slotova ###
        self.setup_signal_connections()
        ### popunjavanje izbornika u dokumentu ###
        self.dokument.init_comboboxeve()

    def setup_signal_connections(self):
        """definiranje komunikacije izmedju objekata"""
        self.action_ucitaj_podatke.triggered.connect(self.read_data_from_csv)
        self.frejmoviView.clicked.connect(self.interakcija_sa_tablicom_frejmova)
        self.siroviPodaciView.clicked.connect(self.interakcija_sa_tablicom_pojedinih_mjerenja)
        self.glavniTabWidget.currentChanged.connect(self.promjena_aktivnog_taba)
        self.action_Exit.triggered.connect(self.close)
        self.action_otvori_kolektor.triggered.connect(self.otvori_prozor)
        self.action_spremi.triggered.connect(self.save_umjeravanje_to_file)
        self.action_ucitaj.triggered.connect(self.load_umjeravanje_from_file)
        self.action_Napravi_pdf_report.triggered.connect(self.napravi_pdf_report)

        #feedback o izbranom uredjaju, promjena labela
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_izabraniUredjaj(PyQt_PyObject)'),
                     self.promjena_aktivni_uredjaj)
        #feedback o izabranoj postaji, promjena labela
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_izabranaPostaja(PyQt_PyObject)'),
                     self.promjena_label_postaja)
        # promjena modela za prikaz podataka u ljevoj tablici (izbor tocaka...)
        self.connect(self.dokument,
                     QtCore.SIGNAL('update_tablicu_podataka(PyQt_PyObject)'),
                     self.update_tablicu_pojedinih_mjerenja)
        # update taba sa rezultatima umjeravanja
        self.connect(self.dokument,
                     QtCore.SIGNAL('update_tab_results(PyQt_PyObject)'),
                     self.update_tab_results)
        # update taba sa odazivom
        self.connect(self.dokument,
                     QtCore.SIGNAL('update_tab_odaziv(PyQt_PyObject)'),
                     self.update_tab_odaziv)
        # update konverter taba
        self.connect(self.dokument,
                     QtCore.SIGNAL('update_tab_konverter(PyQt_PyObject)'),
                     self.update_tab_konverter)
        # display konvertera
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_provjeraKonvertera(PyQt_PyObject)'),
                     self.display_tab_konverter)
        # display odaziva
        self.connect(self.dokument,
                     QtCore.SIGNAL('display_odaziv(PyQt_PyObject)'),
                     self.display_tab_odaziv)
        # display umjeravanje
        self.connect(self.dokument,
                     QtCore.SIGNAL('display_umjeravanje(PyQt_PyObject)'),
                     self.display_tab_umjeravanje)
        self.connect(self.dokument,
                     QtCore.SIGNAL('display_ponovljivost(PyQt_PyObject)'),
                     self.display_tab_umjeravanje)
        self.connect(self.dokument,
                     QtCore.SIGNAL('display_linearnost(PyQt_PyObject)'),
                     self.display_tab_umjeravanje)

    def interakcija_sa_tablicom_frejmova(self, x):
        """izbor aktivnog dokumenta"""
        print('!!!!!!!!!!!izbor aktivnog frejma!!!!!!!!!!!!!!')
        red = x.row()
        aktivniTab = self.glavniTabWidget.currentWidget()
        self.dokument.set_aktivni_frejm(red, self.dictTabova, aktivniTab)

    def update_tablicu_pojedinih_mjerenja(self, x):
        """promjena modela za prikaz pojedinih mjerenja. ulazni parametar x je
        qt model"""
        self.siroviPodaciView.setModel(x)
        nazivTaba = self.glavniTabWidget.currentWidget().plin
        if '-odaziv' in nazivTaba:
            self.glavniTabWidget.currentWidget().update_rezultate()
            self.siroviPodaciView.resizeColumnToContents(0)
            self.siroviPodaciView.resizeColumnToContents(1)
            self.siroviPodaciView.horizontalHeader().setStretchLastSection(True)
        elif nazivTaba == 'konverter':
            self.siroviPodaciView.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        else:
            self.siroviPodaciView.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.siroviPodaciView.update()

    def promjena_aktivnog_taba(self, x):
        """metoda zaduzena za promjenu konteksta prilikom promjene taba. Definira
        koji je model aktivan u ljevoj tablici sa podacima."""
        print('!!!!!!!!!!!promjena_aktivnog_taba!!!!!!!!!!!!!!')
        try:
            nazivTaba = self.glavniTabWidget.currentWidget().plin
            model = self.dokument.get_model(mjerenje=nazivTaba)
            self.siroviPodaciView.setModel(model)
            if '-odaziv' in nazivTaba:
                self.glavniTabWidget.currentWidget().update_rezultate()
                self.siroviPodaciView.resizeColumnToContents(0)
                self.siroviPodaciView.resizeColumnToContents(1)
                self.siroviPodaciView.horizontalHeader().setStretchLastSection(True)
            elif nazivTaba == 'konverter':
                self.siroviPodaciView.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
            else:
                self.siroviPodaciView.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
            self.siroviPodaciView.update()
        except Exception as err:
            logging.error(str(err), exc_info=True)

    def interakcija_sa_tablicom_pojedinih_mjerenja(self, x):
        """izbor pocetka umjeravanja"""
        print('!!!!!!!!interakcija sa modelom pojedinih mjerenja!!!!!!!!!')
        widg = self.glavniTabWidget.currentWidget()
        try:
            mjerenje = widg.plin
            if mjerenje == 'postavke':
                pass
            elif mjerenje.endswith('-odaziv'):
                #delegiraj klik widgetu
                widg.update_rezultate()
            else:
                #dohvati aktivni model
                model = self.dokument.get_model(mjerenje=mjerenje)
                #postavi novi start podataka u model
                model.set_start(x)
                #zahtjev za ponovnim racunanjem s novim podacima
                self.dokument.recalculate_tab_umjeravanja(mjerenje=mjerenje)
        except Exception as err:
            logging.error(str(err), exc_info=True)

    def promjena_aktivni_uredjaj(self, mapa):
        """
        Promjena aktivnog uredjaja. Gui mora prebaciti label uredjaja i
        pravilno updateati i prikazati tablicu sa ucitanim mjerenjima.

        Serijski broj uredjaja je zapisan u mapi pod kljucem 'value'.
        """
        #promjena naziva
        ure = mapa['value']
        self.labelUredjaj.clear()
        if ure != '':
            self.labelUredjaj.setText(ure)
            self.clear_tabove()
            self.create_tabove(ure)
            pass
            model = self.dokument.get_frejmovi_model(ure)
            self.frejmoviView.setModel(model)
            self.frejmoviView.update()
            #pokusaj izabrati prethodno izabrani frejm... in case of None izaberi prvi moguci
            uredjaj = self.dokument.get_izabraniUredjaj()
            izabrani = self.dokument.get_aktivni_frejm(uredjaj)
            if izabrani != None:
                self.frejmoviView.selectRow(izabrani)
            else:
                self.frejmoviView.selectRow(0)
        else:
            self.labelUredjaj.setText('n/a')


    def promjena_label_postaja(self, mapa):
        """
        promjena teksta labela sa izabranom postajom.
        """
        postaja = mapa['value']
        self.labelPostaja.clear()
        self.labelPostaja.setText(postaja)

    def read_data_from_csv(self):
        """
        Ucitavanje sirovih podataka iz csv filea putem wizarda.

        redosljed ucitavanja je bitan:
        1. clear tabove (ako su razliciti od postojecih tabova)
        2. update dokument sa novim podacima
        3. create tabove (ako su prethodno izbrisani)
        """
        pass

        self.fileWizard = datareader.CarobnjakZaCitanjeFilea(dokument=self.dokument)
        prihvacen = self.fileWizard.exec_()
        if prihvacen:
            frejmovi = self.fileWizard.get_frejmovi()
            minutni = frejmovi['minutni']
            sekundni = frejmovi['sekundni']
            uredjaj = self.fileWizard.get_uredjaj()
            self.dokument.add_frejm_ucitanih_za_uredjaj(minutni, 'minutni', uredjaj)
            self.dokument.add_frejm_ucitanih_za_uredjaj(sekundni, 'sekundni', uredjaj)

    @helperi.activate_wait_spinner
    def clear_tabove(self):
        """
        Metoda je zaduzena za uklanjanje svih tabova u mapi self.dictTabova
        """
        # prebaci aktivni tab na 'Postavke' jer se on nikada ne brise
        self.glavniTabWidget.setCurrentWidget(self.tabPostavke)
        for tab in self.dictTabova:
            sip.delete(self.dictTabova[tab])
            self.dictTabova[tab] = None
        self.dictTabova.clear()
        gc.collect()

    @helperi.activate_wait_spinner
    def create_tabove(self, uredjaj):
        """
        Metoda je zaduzena za stvaranje svih potrebnih tabova za zadani uredjaj
        """
        komponente = self.dokument.uredjaji[uredjaj]['komponente']
        if 'None' in komponente:
            komponente.remove('None')
        #specijalni slucajevi:
        #1. NOX - NO, NOx, odaziv-NO, konverter
        if 'NO' in komponente:
            self.dictTabova['NO'] = rezultat.RezultatPanel(dokument=self.dokument, plin='NO')
            self.dictTabova['NOx'] = rezultat.RezultatPanel(dokument=self.dokument, plin='NOx')
            self.dictTabova['NO-odaziv'] = odaziv.RiseFallWidget(dokument=self.dokument, naziv='NO-odaziv')
            self.dictTabova['konverter'] = konverter.KonverterPanel(dokument=self.dokument)
            self.connect(self.dictTabova['NO'],
                         QtCore.SIGNAL('panel_dodaj_umjernu_tocku'),
                         self.add_red_umjeravanje)
            self.connect(self.dictTabova['NO'],
                         QtCore.SIGNAL('panel_makni_umjernu_tocku(PyQt_PyObject)'),
                         self.remove_red_umjeravanje)
            self.connect(self.dictTabova['NO'],
                         QtCore.SIGNAL('panel_edit_umjernu_tocku(PyQt_PyObject)'),
                         self.edit_red_umjeravanje)
            self.connect(self.dictTabova['NOx'],
                         QtCore.SIGNAL('panel_dodaj_umjernu_tocku'),
                         self.add_red_umjeravanje)
            self.connect(self.dictTabova['NOx'],
                         QtCore.SIGNAL('panel_makni_umjernu_tocku(PyQt_PyObject)'),
                         self.remove_red_umjeravanje)
            self.connect(self.dictTabova['NOx'],
                         QtCore.SIGNAL('panel_edit_umjernu_tocku(PyQt_PyObject)'),
                         self.edit_red_umjeravanje)
        else:
            for komponenta in komponente:
                #tab sa rezultatima
                tab = rezultat.RezultatPanel(dokument=self.dokument, plin=komponenta)
                self.dictTabova[komponenta] = tab
                self.connect(tab,
                             QtCore.SIGNAL('panel_dodaj_umjernu_tocku'),
                             self.add_red_umjeravanje)
                self.connect(tab,
                             QtCore.SIGNAL('panel_makni_umjernu_tocku(PyQt_PyObject)'),
                             self.remove_red_umjeravanje)
                self.connect(tab,
                             QtCore.SIGNAL('panel_edit_umjernu_tocku(PyQt_PyObject)'),
                             self.edit_red_umjeravanje)
                #tab odaziv
                naziv = "".join([komponenta, '-odaziv'])
                self.dictTabova[naziv] = odaziv.RiseFallWidget(dokument=self.dokument, naziv=naziv)
        #prikaz elemenata u  guiu
        self.display_tab_konverter(self.dokument.get_provjeraKonvertera())
        self.display_tab_odaziv(self.dokument.get_provjeraOdaziv())
        self.display_tab_umjeravanje(True) #True je placeholder zbog signala...vrijednost nije bitna

    def display_tab_konverter(self, x):
        """Metoda skriva ili prikazuje tab sa provjerom konvertera ovisno o
        ulaznom parametru x (boolean)"""
        popis = list(self.dictTabova)
        if 'konverter' in popis:
            widget = self.dictTabova['konverter']
            if x:
                self.glavniTabWidget.addTab(widget, 'konverter')
            else:
                self.glavniTabWidget.removeTab(self.glavniTabWidget.indexOf(widget))

    def display_tab_odaziv(self, x):
        """Metoda skriva ili prikazuje tabove sa provjerom odaziva ovisno o
        ulaznom parametru x (boolean)"""
        popis = list(self.dictTabova)
        odazivList = [i for i in popis if i.endswith('-odaziv')]
        for i in odazivList:
            widget = self.dictTabova[i]
            if x:
                self.glavniTabWidget.addTab(widget, i)
            else:
                self.glavniTabWidget.removeTab(self.glavniTabWidget.indexOf(widget))

    def display_tab_umjeravanje(self, x):
        """
        Metoda skriva ili prikazuje tabove sa umjeravanjem. Ulazni parametar x
        postoji samo zbog nacina pozivanja preko signala koji emitira boolean, ali
        se zanemaruje. Prikaz ovisi o 3 booleana u dokumentu:
        -provjera linearnosti
        -provjera ponovljivosti
        -provjera umjeravanja

        Ako su sva 3 cheka False, umjeravanje se ne prikazuje
        """
        test1 = self.dokument.get_provjeraUmjeravanje()
        test2 = self.dokument.get_provjeraPonovljivost()
        test3 = self.dokument.get_provjeraLinearnost()
        x = test1 or test2 or test3
        popis = list(self.dictTabova)
        umjList = [i for i in popis if not i.endswith('-odaziv')]
        if 'konverter' in umjList:
            umjList.remove('konverter')
        for i in umjList:
            widget = self.dictTabova[i]
            if x:
                self.glavniTabWidget.addTab(widget, i)
            else:
                self.glavniTabWidget.removeTab(self.glavniTabWidget.indexOf(widget))

    def update_tab_results(self, mapa):
        """update taba sa rezultatima"""
        tab = mapa['tab']
        try:
            for i in self.dictTabova:
                if i == tab:
                    self.dictTabova[i].update_rezultat(mapa)
                    break
        except Exception as err:
            logging.error(str(err), exc_info=True)

    def update_tab_odaziv(self, mapa):
        """update tab sa odazivom"""
        tab = mapa['tab']
        try:
            for i in self.dictTabova:
                if i == tab:
                    self.dictTabova[i].update_rezultate()
                    break
        except Exception as err:
            logging.error(str(err), exc_info=True)

    def update_tab_konverter(self, mapa):
        """update tab sa konverterom"""
        try:
            ulaz = {}
            ulaz['rezultat'] = mapa['rezultat']
            ulaz['efikasnost'] = mapa['lista_efikasnosti']
            ulaz['ec_kriterij'] = mapa['kriterij']
            self.dictTabova['konverter'].update_rezultat(ulaz)
        except Exception as err:
            logging.error(str(err), exc_info=True)

    def add_red_umjeravanje(self):
        """metoda (slot) za dodavanje tocaka u dokument"""
        widg = self.glavniTabWidget.currentWidget()
        try:
            mjerenje = widg.plin
            self.dokument.dodaj_umjernu_tocku(mjerenje=mjerenje)
        except Exception as err:
            logging.error(str(err), exc_info=True)

    def remove_red_umjeravanje(self, x):
        """metoda za brisanje tocke za umjeravanje iz dokumenta, x je broj redka"""
        red = int(x)
        widg = self.glavniTabWidget.currentWidget()
        try:
            mjerenje = widg.plin
            self.dokument.makni_umjernu_tocku(red, mjerenje=mjerenje)
        except Exception as err:
            logging.error(str(err), exc_info=True)

    def edit_red_umjeravanje(self, x):
        """metoda za editiranje umjerne tocke uz pomoc dijaloga"""
        red = int(x)
        self.edit_tocku_dijalog(red)

    def edit_tocku_dijalog(self, indeks):
        """
        Poziv dijaloga za edit vrijednosti parametara izabrane tocke.
        ulazni parametar indeks je indeks pod kojim se ta tocka nalazi
        u listi tocaka
        """
        widg = self.glavniTabWidget.currentWidget()
        mjerenje = widg.plin
        tocke = self.dokument.get_tocke(mjerenje=mjerenje)
        #tocka koju editiramo
        staraTocka = tocke[indeks]
        if staraTocka.crefFaktor == 0.0:
            staraTockaIsZero = True
        else:
            staraTockaIsZero = False
        #moramo se osigurati da postoji barem jedna zero tocka
        brojZeroTocaka = len([i for i in tocke if i.crefFaktor == 0.0])
        #poziv dijaloga
        try:
            self.dijalog = dotedit.EditTockuDijalog(indeks=indeks,
                                                    dokument=self.dokument,
                                                    mjerenje=mjerenje,
                                                    parent=None)
            if self.dijalog.exec_():
                novaTocka = self.dijalog.get_promjenjena_tocka()
                if staraTockaIsZero and brojZeroTocaka == 1:
                    if novaTocka.crefFaktor == 0.0:
                        self.dokument.zamjeni_umjernu_tocku(indeks, novaTocka, mjerenje=mjerenje)
                    else:
                        QtGui.QMessageBox.information(self, 'Oprez','Mora postojati barem jedna zero tocka. Cref faktor tocke nije promjenjen.')
                        novaTocka.crefFaktor = 0.0
                        self.dokument.zamjeni_umjernu_tocku(indeks, novaTocka, mjerenje=mjerenje)
                else:
                    self.dokument.zamjeni_umjernu_tocku(indeks, novaTocka, mjerenje=mjerenje)
        except Exception as err:
            logging.error(str(err), exc_info=True)

    def otvori_prozor(self):
        """otvori prozor, spoji sa metodama za upisivanje podataka i za gasenje prozora"""
        #create prozor i spremi ga u mapu sa unikatnim id
        prozor = kolektor.Kolektor(dokument=self.dokument, uid=self.idCounter)
        accepted = prozor.prikazi_wizard_postavki()
        if accepted:
            tekst = 'Prikupljanje podataka {0}'.format(str(self.idCounter))
            prozor.setWindowTitle(tekst)
            self.otvoreniProzori[self.idCounter] = prozor
            self.otvoreniProzori[self.idCounter].show()
            #connect signal i slot
            self.connect(self.otvoreniProzori[self.idCounter],
                         QtCore.SIGNAL('spremi_preuzete_podatke(PyQt_PyObject)'),
                         self.aktiviraj_ucitane_podatke)
            self.connect(self.otvoreniProzori[self.idCounter],
                         QtCore.SIGNAL('prozor_ugasen(PyQt_PyObject)'),
                         self.makni_referencu_na_prozor)
            self.idCounter = self.idCounter + 1

    def aktiviraj_ucitane_podatke(self, mapa):
        """prebacivanje frejmova iz kolektora u dokument"""
        minutni = mapa['minutniPodaci']
        sekundni = mapa['podaci']
        uredjaj = mapa['uredjaj']
        #prebaci u dokument
        self.dokument.add_frejm_ucitanih_za_uredjaj(minutni, 'minutni', uredjaj)
        self.dokument.add_frejm_ucitanih_za_uredjaj(sekundni, 'sekundni', uredjaj)


    def makni_referencu_na_prozor(self, idProzora):
        """makni referencu na objekt prilikom gasenja prozora za prikupljanje"""
        self.otvoreniProzori[idProzora] = None

    def closeEvent(self, event):
        """Close glavne aplikacije. Potrebno je ugasiti sve prozore za prikupljanje podataka prije
        izlaza"""
        for prozor in self.otvoreniProzori:
            x = self.otvoreniProzori[prozor]
            if x != None:
                x.closeEvent(event)
        event.accept()

    def save_umjeravanje_to_file(self):
        """
        spremanje dokumenta u file
        """
        filepath = QtGui.QFileDialog.getSaveFileName(parent=self,
                                                     caption='Spremi file',
                                                     filter='Umjeravanje save files (*.usf);;all (*.*)')
        if filepath:
            if not filepath.endswith('.usf'):
                filepath = filepath + '.usf'
            mapa = self.dokument.dokument_to_dict()
            with open(filepath, mode='wb') as fajl:
                try:
                    pickle.dump(mapa, fajl)
                except Exception as err:
                    logging.error(str(err), exc_info=True)
                    QtGui.QMessageBox.information(self, 'Problem', 'Spremanje datoteke nije uspjelo.')

    def load_umjeravanje_from_file(self):
        """ucitavanje dokumenta iz spremljenog filea"""
        filepath = QtGui.QFileDialog.getOpenFileName(parent=self,
                                                     caption='Ucitaj file',
                                                     filter='Umjeravanje save files (*.usf);;all (*.*)')
        if filepath:
            with open(filepath, mode='rb') as fajl:
                try:
                    mapa = pickle.load(fajl)
                    self.dokument.dict_to_dokument(mapa)
                except Exception as err:
                    print(str(err))
                    logging.error(str(err), exc_info=True)
                    QtGui.QMessageBox.information(self, 'Problem', 'Ucitavanje datoteke nije uspjelo.')

    def napravi_pdf_report(self):
        """
        Generiranje pdf reporta trenutno aktivnog umjeravanja
        """
        ime = QtGui.QFileDialog.getSaveFileName(parent=self,
                                                caption='Spremi pdf report',
                                                filter = 'pdf file (*.pdf)')
        if ime:
            report = pdfreport.ReportGenerator()
            try:
                mapa = self.generiraj_mapu_za_report()
                report.generiraj_report(ime, self.dokument, mapa)
            except Exception as err:
                logging.error(str(err), exc_info=True)
                msg = "\n".join(['Izvještaj nije uspješno generiran.', str(err)])
                QtGui.QMessageBox.information(self, 'Problem', msg)

    def generiraj_mapu_za_report(self):
        """
        Generiranje mape sa potrebnim podacima za report.

        -kljuc mape je naziv komponente (npr. 'NOx' ili 'SO2')
        -pod svakim kljucem je nested druga mapa sa podacima
            - 'umjeravanje' --> pandas frejm rezultata umjeravanja za tocke (ili None)
            - 'prilagodba' --> mapa sa podacima o slope, offset, prilagodbaA i prilagodbaB (ili None)
            - 'testovi' --> mapa sa podacima o pojedinim testovima (ili None)
                        --> moguca vrijednost je prazan dict
        """
        reportData = {}
        #checkovi linearnosti, umjeravanja, konvertera....
        konverter = self.dokument.get_provjeraKonvertera()
        odaziv = self.dokument.get_provjeraOdaziv()
        umjeravanje = self.dokument.get_provjeraUmjeravanje()
        ponovljivost = self.dokument.get_provjeraPonovljivost()
        linearnost = self.dokument.get_provjeraLinearnost()
        #uredjaj za report
        uredjaj = self.dokument.get_izabraniUredjaj()
        #komponente uredjaja
        komponente = self.dokument.uredjaji[uredjaj]['komponente']
        if 'None' in komponente:
            komponente.remove('None')
        #special case 'NOx'
        if 'NO' in komponente:
            #NO podaci
            reportData['NO'] = {}
            reportData['NO']['umjeravanje'] = None
            reportData['NO']['testovi'] = None
            reportData['NO']['prilagodba'] = None
            if umjeravanje:
                rez = self.dokument.mjerenja['NO']['kalkulator'].get_tablicu_rezultata()
                reportData['NO']['umjeravanje'] = rez
                slope = self.dokument.mjerenja['NO']['kalkulator'].get_slope_and_offset_map()
                reportData['NO']['prilagodba'] = slope
            #slaganje mape testova
            testovi = {}
            test1 = self.dokument.mjerenja['NO']['kalkulator'].get_provjeru_parametara()
            testovi.update(test1)
            test2 = self.dokument.mjerenja['konverter']['kalkulator'].get_ec_parametar()
            test2 = {'ec':test2} #need to convert to dict
            testovi.update(test2)
            test3 = self.dictTabova['NO-odaziv'].get_reportKriterijValue()
            testovi.update(test3)
            #removing not needed tests
            if not konverter:
                testovi.pop('ec', None)
            if not odaziv:
                testovi.pop('rise', None)
                testovi.pop('fall', None)
                testovi.pop('diff', None)
            if not ponovljivost:
                testovi.pop('srs', None)
                testovi.pop('srz', None)
            if not linearnost:
                testovi.pop('rz', None)
                testovi.pop('rmax', None)
            reportData['NO']['testovi'] = testovi

            #NOx podaci
            reportData['NOx'] = {}
            reportData['NOx']['umjeravanje'] = None
            reportData['NOx']['testovi'] = None
            reportData['NOx']['prilagodba'] = None
            if umjeravanje:
                rez = self.dokument.mjerenja['NOx']['kalkulator'].get_tablicu_rezultata()
                reportData['NOx']['umjeravanje'] = rez
                slope = self.dokument.mjerenja['NOx']['kalkulator'].get_slope_and_offset_map()
                reportData['NOx']['prilagodba'] = slope
            #slaganje mape testova
            testovi = {}
            test1 = self.dokument.mjerenja['NOx']['kalkulator'].get_provjeru_parametara()
            testovi.update(test1)
            test3 = self.dictTabova['NO-odaziv'].get_reportKriterijValue()
            testovi.update(test3)
            #removing not needed tests
            if not odaziv:
                testovi.pop('rise', None)
                testovi.pop('fall', None)
                testovi.pop('diff', None)
            if not ponovljivost:
                testovi.pop('srs', None)
                testovi.pop('srz', None)
            if not linearnost:
                testovi.pop('rz', None)
                testovi.pop('rmax', None)
            reportData['NOx']['testovi'] = testovi
        else:
            for komponenta in komponente:
                reportData[komponenta] = {}
                reportData[komponenta]['umjeravanje'] = None
                reportData[komponenta]['testovi'] = None
                reportData[komponenta]['prilagodba'] = None
                if umjeravanje:
                    rez = self.dokument.mjerenja[komponenta]['kalkulator'].get_tablicu_rezultata()
                    reportData[komponenta]['umjeravanje'] = rez
                    slope = self.dokument.mjerenja[komponenta]['kalkulator'].get_slope_and_offset_map()
                    reportData[komponenta]['prilagodba'] = slope
                #slaganje mape testova
                testovi = {}
                test1 = self.dokument.mjerenja[komponenta]['kalkulator'].get_provjeru_parametara()
                testovi.update(test1)
                imeTaba = ''.join([komponenta,'-odaziv'])
                test2 = self.dictTabova[imeTaba].get_reportKriterijValue()
                testovi.update(test2)
                #removing not needed tests
                if not odaziv:
                    testovi.pop('rise', None)
                    testovi.pop('fall', None)
                    testovi.pop('diff', None)
                if not ponovljivost:
                    testovi.pop('srs', None)
                    testovi.pop('srz', None)
                if not linearnost:
                    testovi.pop('rz', None)
                    testovi.pop('rmax', None)
                reportData[komponenta]['testovi'] = testovi
        return reportData
