# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 09:41:20 2015

@author: DHMZ-Milic

"""
import gc
import sip
import logging
import copy
import pickle
import pandas as pd
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

        ### inicijalni setup dokumenta ###
        self.dokument.init_listaDilucija()
        self.dokument.init_listaZrak()

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
    def create_tabove(self, popis):
        """
        Metoda je zaduzena za stvaranje svih potrebnih tabova. Ulazni parametar je
        mapa tabova (kljucevi su nazivi tabova)
        """
        for name in popis:
            if name == 'konverter':
                self.dictTabova[name] = konverter.KonverterPanel(dokument=self.dokument)
            elif name.endswith('-odaziv'):
                tab = odaziv.RiseFallWidget(dokument=self.dokument,
                                            naziv=name)
                self.dictTabova[name] = tab
            else:
                tab = rezultat.RezultatPanel(dokument=self.dokument,
                                             plin=name)
                self.dictTabova[name] = tab
                self.connect(tab,
                             QtCore.SIGNAL('panel_dodaj_umjernu_tocku'),
                             self.add_red_umjeravanje)
                self.connect(tab,
                             QtCore.SIGNAL('panel_makni_umjernu_tocku(PyQt_PyObject)'),
                             self.remove_red_umjeravanje)
                self.connect(tab,
                             QtCore.SIGNAL('panel_edit_umjernu_tocku(PyQt_PyObject)'),
                             self.edit_red_umjeravanje)

        #dinamicki display tabova ovisno o chekovima
        self.toggle_umjeravanja(self.dokument.get_provjeraUmjeravanje())
        self.toggle_tabove_odaziva(self.dokument.get_provjeraOdaziv())
        self.toggle_tab_konverter(self.dokument.get_provjeraKonvertera())

    def interakcija_sa_tablicom(self, x):
        """slot za clicked signal tablice sa podacima...razlicito ponasanje ovisno o
        aktivnom tabu"""
        widg = self.glavniTabWidget.currentWidget()
        try:
            mjerenje = widg.plin
            if mjerenje.endswith('-odaziv'):
                #delegiraj klik widgetu
                widg.check_pocetak(x)
            else:
                #dohvati aktivni model
                model = self.dokument.get_model(mjerenje=mjerenje)
                #postavi novi start podataka u model
                model.set_start(x)
                #zahtjev za ponovnim racunanjem s novim podacima
                self.dokument.recalculate_tab_umjeravanja(mjerenje=mjerenje)
        except Exception as err:
            logging.error(str(err), exc_info=True)


    def promjena_aktivnog_taba(self, x):
        """metoda zaduzena za promjenu konteksta prilikom promjene taba. Definira
        koji je model aktivan u ljevoj tablici sa podacima."""
        widg = self.glavniTabWidget.currentWidget()
        try:
            mjerenje = widg.plin
            model = self.dokument.get_model(mjerenje=mjerenje)
            self.siroviPodaciView.setModel(model)
            if '-odaziv' in mjerenje:
                self.siroviPodaciView.resizeColumnToContents(0)
                self.siroviPodaciView.resizeColumnToContents(1)
                self.siroviPodaciView.horizontalHeader().setStretchLastSection(True)
            elif mjerenje == 'konverter':
                self.siroviPodaciView.resizeColumnsToContents()
            else:
                self.siroviPodaciView.horizontalHeader().setStretchLastSection(True)
            self.siroviPodaciView.update()
        except Exception as err:
            logging.error(str(err), exc_info=True)

    def postavi_podatke_u_dokument(self, mapa):
        """
        Spremanje ucitanih podataka u model

        ulazna mapa ima sljedece kljuceve:
        'podaci' - frejm sekundnih podataka
        'minutniPodaci' - frejm minutnih podataka
        'tabMap' - popis tabova u koje treba spremiti podatke
        'uredjaj' - serijski broj uredjaja (string)
        'lokacija' - string naziva lokacije
        """
        uredjaj = mapa['uredjaj']
        lokacija = mapa['lokacija']
        frejm = mapa['minutniPodaci']
        frejmSek = mapa['podaci']
        tabMap = mapa['tabMap']

        cleared = False
        if not self.dokument.usporedi_mjerenja(tabMap):
            self.clear_tabove()
            cleared = True

        # postavi info o ucitanom fileu
        self.dokument.set_izabraniUredjaj(uredjaj)
        self.dokument.set_izabranaPostaja(lokacija)

        #treba napraviti tabMap mangle...
        m1 = copy.deepcopy(tabMap)
        m2 = copy.deepcopy(tabMap)
        #prebaci sve odazive na False
        for key in m1:
            if '-odaziv' in key:
                m1[key] = False
        #prebaci sve osim odaziva na False
        for key in m2:
            if '-odaziv' not in key:
               m2[key] = False
        #set minutne podatke
        self.dokument.set_ucitane_podatke(frejm, m1)
        #set sekundne podatke
        self.dokument.set_ucitane_podatke(frejmSek, m2)
        if cleared:
            self.create_tabove(tabMap)

        #izbor mjerenja?
        komponente = set(self.dokument.uredjaji[uredjaj]['komponente'])
        if 'None' in komponente:
            komponente.remove('None')
        komponente = list(komponente)
        self.dokument.set_listaMjerenja(komponente)

        # naredi racunanje svih tabova (to ce updateati gui)
        mjerenja = self.dokument.get_mjerenja()
        for mjerenje in mjerenja:
            self.dokument.recalculate_tab_umjeravanja(mjerenje=mjerenje)

    def read_data_from_csv(self):
        """
        Ucitavanje sirovih podataka iz csv filea putem wizarda.

        redosljed ucitavanja je bitan:
        1. clear tabove (ako su razliciti od postojecih tabova)
        2. update dokument sa novim podacima
        3. create tabove (ako su prethodno izbrisani)
        """
        self.fileWizard = datareader.CarobnjakZaCitanjeFilea(uredjaji=self.dokument.get_uredjaji(),
                                                             postaje=self.dokument.get_postaje())
        prihvacen = self.fileWizard.exec_()

        stariUredjaj = self.dokument.get_izabraniUredjaj()

        if prihvacen:
            stariUredjaj = self.dokument.get_izabraniUredjaj()
            lokacija = self.fileWizard.get_postaja()
            noviUredjaj = self.fileWizard.get_uredjaj()
            #mapa tabova u koje se trebaju spremiti podaci
            tabMap = self.fileWizard.get_ckecked_tabove()
            frejmovi = self.fileWizard.get_frejmovi()

            mapa = {'podaci':frejmovi['sekundni'].copy(),
                    'minutniPodaci':frejmovi['minutni'].copy(),
                    'tabMap':tabMap,
                    'uredjaj':noviUredjaj,
                    'lokacija':lokacija}

            if noviUredjaj != stariUredjaj and stariUredjaj != '':
                naslov = 'Potvrdi prebacivanje podataka'
                opis = 'Trenutno se umjerava uredjaj {0}, a pokušavate prebaciti podatke iz uredjaja {1}. Ako nastavite trenutno aktivno umjeravanje će biti izbrisano. Da li želite nastaviti?.'.format(stariUredjaj, noviUredjaj)
                reply = QtGui.QMessageBox.question(self,
                                                   naslov,
                                                   opis,
                                                   QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                if reply == QtGui.QMessageBox.Yes:
                    self.postavi_podatke_u_dokument(mapa)
                else:
                    pass
            else:
                self.postavi_podatke_u_dokument(mapa)



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
        try:
            mjerenje = widg.plin
            self.dijalog = dotedit.EditTockuDijalog(indeks=indeks,
                                                    dokument=self.dokument,
                                                    mjerenje=mjerenje,
                                                    parent=None)
            if self.dijalog.exec_():
                tocka = self.dijalog.get_promjenjena_tocka()
                self.dokument.zamjeni_umjernu_tocku(indeks, tocka, mjerenje=mjerenje)
        except Exception as err:
            logging.error(str(err), exc_info=True)

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


    def toggle_tabove_odaziva(self, x):
        """Metoda sakriva ili prikazuje sve tabove sa odazivom ovisno o ulaznom
        parametru x (boolean)"""
        odazivi = []
        for tab in self.dictTabova:
            if '-odaziv' in tab:
                widget = self.dictTabova[tab]
                odazivi.append(widget)
        #prebaci check u dokumentu
        self.dokument.set_provjeraOdaziv(x)
        if x:
            for widget in odazivi:
                self.glavniTabWidget.addTab(widget, widget.plin)
        else:
            for widget in odazivi:
                self.glavniTabWidget.removeTab(self.glavniTabWidget.indexOf(widget))

    def toggle_tab_konverter(self, x):
        """Metoda skriva ili prikazuje tab sa provjerom konvertera ovisno o
        ulaznom parametru x (boolean)"""
        widget = None
        for tab in self.dictTabova:
            if tab == 'konverter':
                widget = self.dictTabova[tab]
                break
        #prebaci check u dokumentu
        self.dokument.set_provjeraKonvertera(x)
        if x:
            if widget != None:
                self.glavniTabWidget.addTab(widget, 'konverter')
        else:
            if widget != None:
                self.glavniTabWidget.removeTab(self.glavniTabWidget.indexOf(widget))

    def toggle_umjeravanja(self, x):
        """
        Metoda je zaduzena za skrivanje ili prikazivanje tabova sa rezultatima.

        Metoda ce overrideati postavke pojedinog taba sa rezultatima za test
        umjeravanja.
        """
        popis = []
        for tab in self.dictTabova:
            if not (tab == 'konverter' or tab.endswith('-odaziv')):
                popis.append(tab)
                self.dictTabova[tab].checkBoxUmjeravanje.setChecked(x)
        # prebaci check u dokumentu
        self.dokument.set_provjeraUmjeravanje(x)
        #hide tabove samo ako su umjeravanje, ponovljivost i linearnost iskljuceni
        ponovljivost = self.dokument.get_provjeraPonovljivost()
        linearnost = self.dokument.get_provjeraLinearnost()
        if x or ponovljivost or linearnost:
            for tab in popis:
                widget = self.dictTabova[tab]
                self.glavniTabWidget.addTab(widget, tab)
        else:
            for tab in popis:
                widget = self.dictTabova[tab]
                self.glavniTabWidget.removeTab(self.glavniTabWidget.indexOf(widget))

    def toggle_ponovljivost(self, x):
        """
        Metoda je zaduzena za skrivanje ili prikazivanje tabova sa rezultatima.

        Metoda ce overrideati postavke pojedinog taba sa rezultatima za test
        ponovljivosti.
        """
        popis = []
        for tab in self.dictTabova:
            if not (tab == 'konverter' or tab.endswith('-odaziv')):
                popis.append(tab)
                self.dictTabova[tab].checkBoxPonovljivost.setChecked(x)
        # prebaci check u dokumentu
        self.dokument.set_provjeraPonovljivost(x)
        #hide tabove samo ako su umjeravanje, ponovljivost i linearnost iskljuceni
        umjeravanje = self.dokument.get_provjeraUmjeravanje()
        linearnost = self.dokument.get_provjeraLinearnost()
        if x or umjeravanje or linearnost:
            for tab in popis:
                widget = self.dictTabova[tab]
                self.glavniTabWidget.addTab(widget, tab)
        else:
            for tab in popis:
                widget = self.dictTabova[tab]
                self.glavniTabWidget.removeTab(self.glavniTabWidget.indexOf(widget))

    def toggle_linearnost(self, x):
        """
        Metoda je zaduzena za skrivanje ili prikazivanje tabova sa rezultatima.

        Metoda ce overrideati postavke pojedinog taba sa rezultatima za test
        ponovljivosti.
        """
        popis = []
        for tab in self.dictTabova:
            if not (tab == 'konverter' or tab.endswith('-odaziv')):
                popis.append(tab)
                self.dictTabova[tab].checkBoxLinearnost.setChecked(x)
        # prebaci check u dokumentu
        self.dokument.set_provjeraLinearnost(x)
        #hide tabove samo ako su umjeravanje, ponovljivost i linearnost iskljuceni
        umjeravanje = self.dokument.get_provjeraUmjeravanje()
        ponovljivost = self.dokument.get_provjeraPonovljivost()
        if x or umjeravanje or ponovljivost:
            for tab in popis:
                widget = self.dictTabova[tab]
                self.glavniTabWidget.addTab(widget, tab)
        else:
            for tab in popis:
                widget = self.dictTabova[tab]
                self.glavniTabWidget.removeTab(self.glavniTabWidget.indexOf(widget))

    def closeEvent(self, event):
        """Close glavne aplikacije. Potrebno je ugasiti sve prozore za prikupljanje podataka prije
        izlaza"""
        for prozor in self.otvoreniProzori:
            x = self.otvoreniProzori[prozor]
            if x != None:
                x.closeEvent(event)
        event.accept()

    def aktiviraj_ucitane_podatke(self, mapa):
        """
        Metoda preuzima mapu sa ucitanim podacima i postavlja je u dokument.
        dict mapa sadrzi :
        {'podaci':frejm sa podacima (sekundni),
         'minutniPodaci':frejm sa minutno usrednjenim podacima,
         'tabMap':mapa sa definicijom u koje tabove se trebaju staviti podaci
         'uredjaj':string, naziv uredjaja}
        """
        x = copy.deepcopy(mapa)
        noviUredjaj = mapa['uredjaj']
        stariUredjaj = self.dokument.get_izabraniUredjaj()
        try:
            x['lokacija'] = self.dokument.uredjaji[noviUredjaj]['lokacija']
        except Exception as err:
            logging.error(str(err), exc_info=True)
            x['lokacija'] = 'n/a'
        if noviUredjaj != stariUredjaj and stariUredjaj != '':
            naslov = 'Potvrdi prebacivanje podataka'
            opis = 'Trenutno se umjerava uredjaj {0}, a pokušavate prebaciti podatke iz uredjaja {1}. Ako nastavite trenutno aktivno umjeravanje će biti izbrisano. Da li želite nastaviti?.'.format(stariUredjaj, noviUredjaj)
            reply = QtGui.QMessageBox.question(self,
                                               naslov,
                                               opis,
                                               QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                self.postavi_podatke_u_dokument(mapa)
            else:
                pass
        else:
            self.postavi_podatke_u_dokument(mapa)

    def otvori_prozor(self):
        """otvori prozor, spoji sa necim"""
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

    def makni_referencu_na_prozor(self, idProzora):
        """makni referencu na objekt prilikom gasenja prozora za prikupljanje"""
        self.otvoreniProzori[idProzora] = None

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
                    #konstruiraj mapu tabova iz mape mjerenja
                    keys = list(mapa['mjerenja'].keys())
                    values = [False for i in keys]
                    tabMap = dict(zip(keys, values))
                    #napravi prazan frejm sa dobrim stupcima
                    cols = [i for i in keys if i != 'konverter']
                    cols = [i for i in cols if not i.endswith('-odaziv')]
                    mockFrejm = pd.DataFrame(columns=cols)
                    #podatak o lokaciji i uredjaju
                    ure = mapa['postavke']['izabraniUredjaj']
                    lok = mapa['postavke']['izabranaPostaja']
                    fakeData = {'podaci':mockFrejm,
                                'minutniPodaci':mockFrejm,
                                'tabMap':tabMap,
                                'uredjaj':ure,
                                'lokacija':lok}
                    #koristim fake data da pravilno cleara i postavi potrebne tabove
                    self.postavi_podatke_u_dokument(fakeData)
                    #update dokument sa stvarim podacima
                    self.dokument.dict_to_dokument(mapa)
                    # naredi racunanje svih tabova (to ce updateati gui)
                    mjerenja = self.dokument.get_mjerenja()
                    for mjerenje in mjerenja:
                        self.dokument.recalculate_tab_umjeravanja(mjerenje=mjerenje)
                except Exception as err:
                    logging.error(str(err), exc_info=True)
                    raise err
                    QtGui.QMessageBox.information(self, 'Problem', 'Ucitavanje datoteke nije uspjelo.')

    def toggle_report_check_za_tab(self, mapa):
        """
        toggle report checka za pojedini tab
        """
        value = mapa['value']
        mjerenje = mapa['mjerenje']
        try:
            self.dictTabova[mjerenje].checkBoxReport.setChecked(value)
        except Exception as err:
            logging.error(str(err), exc_info=True)

    def toggle_promjena_testUmjeravanje(self, mapa):
        """toggle provjere umjeravanja za pojedini tab"""
        value = mapa['value']
        mjerenje = mapa['mjerenje']
        try:
            self.dictTabova[mjerenje].checkBoxUmjeravanje.setChecked(value)
        except Exception as err:
            logging.error(str(err), exc_info=True)

    def toggle_promjena_testPonovljivost(self, mapa):
        """toggle provjere ponovljivosti za pojedini tab"""
        value = mapa['value']
        mjerenje = mapa['mjerenje']
        try:
            self.dictTabova[mjerenje].checkBoxPonovljivost.setChecked(value)
        except Exception as err:
            logging.error(str(err), exc_info=True)

    def toggle_promjena_testLinearnost(self, mapa):
        """toggle provjere linearnosti za pojedini tab"""
        value = mapa['value']
        mjerenje = mapa['mjerenje']
        try:
            self.dictTabova[mjerenje].checkBoxLinearnost.setChecked(value)
        except Exception as err:
            logging.error(str(err), exc_info=True)

    def reinit_tab_odaziv(self, mapa):
        """reinit taba za odaziv sa novim podacima"""
        mjerenje = mapa['mjerenje']
        print('----> reinitializing tab : ', mjerenje)
        #TODO! ovo je metoda iskljucivo kod loada i nespretno je
#        treba definirati metodu koja ce postaviti novi frejm i podatke ili bolje
#        definirati rezultat mjerenja / update istog...jer ovo bas ne radi dobro
        try:
            self.dictTabova[mjerenje].__init__(dokument=self.dokument, naziv=mjerenje)
        except Exception as err:
            logging.error(str(err), exc_info=True)

    def prebaci_checkKonverter_u_tabu_postavke(self, x):
        """Prebacivanje glavnog chekboxa za prikaz konvertera. x je boolean"""
        self.tabPostavke.checkBoxKonverterTab.setChecked(x)

    def prebaci_checkOdaziv_u_tabu_postavke(self, x):
        """Prebacivanje glavnog chekboxa za prikaz odaziva. x je boolean"""
        self.tabPostavke.checkBoxRiseFall.setChecked(x)

    def prebaci_checkUmjeravanje_u_tabu_postavke(self, x):
        """Prebacivanje glavnog chekboxa za umjeravanje. x je boolean"""
        self.tabPostavke.checkUmjeravanje.setChecked(x)

    def prebaci_checkPonovljivost_u_tabu_postavke(self, x):
        """Prebacivanje glavnog chekboxa za ponovljivost. x je boolean"""
        self.tabPostavke.checkPonovljivost.setChecked(x)

    def prebaci_checkLinearnost_u_tabu_postavke(self, x):
        """Prebacivanje glavnog chekboxa za linearnost. x je boolean"""
        self.tabPostavke.checkLinearnost.setChecked(x)

    def update_label_postaja(self, x):
        """Setter naziva postaje na kojoj je smjesten uredjaj u label"""
        value = x['value']
        self.labelPostaja.setText(value)

    def update_label_uredjaj(self, x):
        """Setter serijskog broja uredjaja (tekst) u label"""
        value = x['value']
        self.labelUredjaj.setText(value)

    def napravi_pdf_report(self):
        """
        Generiranje pdf reporta trenutno aktivnog umjeravanja
        """
        #TODO!
        print('NOT FULLY IMPLEMENTED YET')
        ime = QtGui.QFileDialog.getSaveFileName(parent=self,
                                                caption='Spremi pdf report',
                                                filter = 'pdf file (*.pdf)')
        if ime:
            report = pdfreport.ReportGenerator()
            try:
                report.generiraj_report(ime, self.dokument)
            except Exception as err:
                logging.error(str(err), exc_info=True)
                msg = "\n".join(['Izvještaj nije uspješno generiran.', str(err)])
                QtGui.QMessageBox.information(self, 'Problem', msg)

    def setup_signal_connections(self):
        """definiranje komunikacije izmedju objekata"""
        ### actions ###
        self.action_ucitaj_podatke.triggered.connect(self.read_data_from_csv)
        self.action_Exit.triggered.connect(self.close)
        self.action_otvori_kolektor.triggered.connect(self.otvori_prozor)
        self.action_spremi.triggered.connect(self.save_umjeravanje_to_file)
        self.action_ucitaj.triggered.connect(self.load_umjeravanje_from_file)
        self.action_Napravi_pdf_report.triggered.connect(self.napravi_pdf_report)
        self.glavniTabWidget.currentChanged.connect(self.promjena_aktivnog_taba)
        self.siroviPodaciView.clicked.connect(self.interakcija_sa_tablicom)

        self.connect(self.dokument,
                     QtCore.SIGNAL('update_tab_results(PyQt_PyObject)'),
                     self.update_tab_results)

        self.connect(self.dokument,
                     QtCore.SIGNAL('update_tab_odaziv(PyQt_PyObject)'),
                     self.update_tab_odaziv)

        self.connect(self.dokument,
                     QtCore.SIGNAL('update_tab_konverter(PyQt_PyObject)'),
                     self.update_tab_konverter)

        self.connect(self.tabPostavke,
                     QtCore.SIGNAL('toggle_tab_odaziv(PyQt_PyObject)'),
                     self.toggle_tabove_odaziva)

        self.connect(self.tabPostavke,
                     QtCore.SIGNAL('toggle_tab_konverter(PyQt_PyObject)'),
                     self.toggle_tab_konverter)

        self.connect(self.tabPostavke,
                     QtCore.SIGNAL('toggle_umjeravanja(PyQt_PyObject)'),
                     self.toggle_umjeravanja)

        self.connect(self.tabPostavke,
                     QtCore.SIGNAL('toggle_ponovljivost(PyQt_PyObject)'),
                     self.toggle_ponovljivost)

        self.connect(self.tabPostavke,
                     QtCore.SIGNAL('toggle_linearnost(PyQt_PyObject)'),
                     self.toggle_linearnost)

        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_generateReportCheck(PyQt_PyObject)'),
                     self.toggle_report_check_za_tab)

        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_testUmjeravanje(PyQt_PyObject)'),
                     self.toggle_promjena_testUmjeravanje)

        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_testPonovljivost(PyQt_PyObject)'),
                     self.toggle_promjena_testPonovljivost)

        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_testLinearnost(PyQt_PyObject)'),
                     self.toggle_promjena_testLinearnost)

        self.connect(self.dokument,
                     QtCore.SIGNAL('reinitialize_tab_odaziv(PyQt_PyObject)'),
                     self.reinit_tab_odaziv)

        self.connect(self.dokument,
                     QtCore.SIGNAL('display_konverter(PyQt_PyObject)'),
                     self.prebaci_checkKonverter_u_tabu_postavke)

        self.connect(self.dokument,
                     QtCore.SIGNAL('display_odaziv(PyQt_PyObject)'),
                     self.prebaci_checkOdaziv_u_tabu_postavke)

        self.connect(self.dokument,
                     QtCore.SIGNAL('display_umjeravanje(PyQt_PyObject)'),
                     self.prebaci_checkUmjeravanje_u_tabu_postavke)

        self.connect(self.dokument,
                     QtCore.SIGNAL('display_ponovljivost(PyQt_PyObject)'),
                     self.prebaci_checkPonovljivost_u_tabu_postavke)

        self.connect(self.dokument,
                     QtCore.SIGNAL('display_linearnost(PyQt_PyObject)'),
                     self.prebaci_checkLinearnost_u_tabu_postavke)

        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_izabranaPostaja(PyQt_PyObject)'),
                     self.update_label_postaja)

        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_izabraniUredjaj(PyQt_PyObject)'),
                     self.update_label_uredjaj)

