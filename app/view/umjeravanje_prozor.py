# -*- coding: utf-8 -*-
"""
Created on Tue Feb  2 12:38:19 2016

@author: DHMZ-Milic
"""
import os
import copy
import logging
import datetime
import pandas as pd
from PyQt4 import QtGui, QtCore, uic
from app.model.datastore import DataStore
from app.model.qt_models import SiroviFrameModel
from app.model.tocke import Tocka
from app.view import tab_postavke
from app.view import tab_rezultat
from app.view import tab_odaziv
from app.view import tab_konverter
from app.view import read_file_wizard
from app.view import dijalog_edit_tocke
from app.view.tab_kolektor import Kolektor
from app.pomocni import pomocni, kalkulator
from app.reportgen.reportgen import ReportGenerator


BASE_UMJERAVANJE, FORM_UMJERAVANJE = uic.loadUiType('./app/view/uiFiles/umjeravanje.ui')
class Umjeravanje(BASE_UMJERAVANJE, FORM_UMJERAVANJE):
    """
    Klasa za 'child' prozor umjeravanja.
    """
    redniBroj = 1

    def __init__(self, uredjaj=None, generatori=None, dilucije=None, parent=None, postaje=None, cfg=None, datastore=None):
        super(BASE_UMJERAVANJE, self).__init__(parent)
        self.setupUi(self)
        #MDI members ...
        self.bezNaslova = True
        self.isModified = True
        self.workingFolder = os.path.dirname(__file__)
        self.kolektor = QtGui.QWidget() #placeholder widget za kolektor preko veze
        #podaci za umjeravanje
        if datastore==None:
            self.datastore = DataStore(uredjaj=uredjaj,
                                       generatori=generatori,
                                       dilucije=dilucije,
                                       postaje=postaje,
                                       cfg=cfg)
        else:
            self.datastore = datastore

        #postavke prozora...
        self.labelUredjaj.setText(self.datastore.get_uredjaj().get_serial())
        self.labelPostaja.setText(self.datastore.get_izabranaPostaja())

        self.init_tabove()

        self.setup_connections()

    def setup_connections(self):
        #update teksta postaje
        self.connect(self.tabPostavke,
                     QtCore.SIGNAL('promjena_postaje(PyQt_PyObject)'),
                     self.labelPostaja.setText)
        ### UCITAVANJE PODATAKA ###
        self.pushButtonUcitajPodatke.clicked.connect(self.read_data_from_csv)
        self.pushButtonPrikupljanjePodataka.clicked.connect(self.display_tab_kolektor)
        ### REPORT GENERATOR ###
        self.pushButtonReport.clicked.connect(self.napravi_report)
        ### RECALCULATE TRIGGERI ###
        self.connect(self.tabPostavke,
                     QtCore.SIGNAL('recalculate_all_tabs'),
                     self.recalculate_all_tabs)
        self.connect(self.tabPostavke,
                     QtCore.SIGNAL('recalculate_konverter'),
                     self.recalculate_tab_konverter)
        self.connect(self.tabPostavke,
                     QtCore.SIGNAL('recalculate_umjeravanja'),
                     self.recalculate_all_umjeravanja)
        self.connect(self.tabPostavke,
                     QtCore.SIGNAL('promjena_checkOdaziv'),
                     self.prikazi_tabove_odaziva)
        self.connect(self.tabPostavke,
                     QtCore.SIGNAL('promjena_checkKonverter'),
                     self.prikazi_tab_konverter)
        self.tableViewFrejm.clicked.connect(self.interakcija_sa_tablicom_pojedinih_mjerenja)
        ### PROMJENA AKTIVNOG TABA ###
        self.glavniTabWidget.currentChanged.connect(self.promjena_aktivnog_taba)
        ### triggeri za save check ###
        self.tabPostavke.lineEditCRMSljedivost.textChanged.connect(self.trigger_is_modified)
        self.tabPostavke.comboBoxLokacija.currentIndexChanged.connect(self.trigger_is_modified)
        self.tabPostavke.comboBoxLokacija.editTextChanged.connect(self.trigger_is_modified)
        self.tabPostavke.lineEditVrstaCRM.textChanged.connect(self.trigger_is_modified)
        self.tabPostavke.lineEditOznakaIzvjesca.textChanged.connect(self.trigger_is_modified)
        self.tabPostavke.lineEditRevizija.textChanged.connect(self.trigger_is_modified)
        self.tabPostavke.lineEditBrojObrasca.textChanged.connect(self.trigger_is_modified)
        self.tabPostavke.lineEditNorma.textChanged.connect(self.trigger_is_modified)
        self.tabPostavke.plainTextEditPuniNazivMetode.textChanged.connect(self.trigger_is_modified)
        self.tabPostavke.plainTextEditNapomena.textChanged.connect(self.trigger_is_modified)
        self.tabPostavke.lineEditDatumUmjeravanja.textChanged.connect(self.trigger_is_modified)
        self.tabPostavke.doubleSpinBoxTemperatura.valueChanged.connect(self.trigger_is_modified)
        self.tabPostavke.doubleSpinBoxVlaga.valueChanged.connect(self.trigger_is_modified)
        self.tabPostavke.doubleSpinBoxTlak.valueChanged.connect(self.trigger_is_modified)

    def scroll_na_indeks(self, indeks):
        """callback za scroll na zadani qmodel indeks"""
        try:
            self.tableViewFrejm.scrollTo(indeks)
            red = indeks.row()
            self.tableViewFrejm.selectRow(red)
        except Exception as err:
            print(str(err))
            logging.error(str(err), exc_info=True)

    def trigger_is_modified(self, x):
        """callback za promjenu stanja dokumenta"""
        self.set_modified(True)

    def napravi_report(self):
        """
        Izrada PDF reporta umjeravanja.
        """
        komponente = self.datastore.get_uredjaj().get_listu_komponenti()
        if self.datastore.isNOx:
            plin = 'NO'
        elif len(komponente) > 1:
            plin, ok = QtGui.QInputDialog.getItem(self,
                                                  'Izbor komponente za report',
                                                  'Komponenta :',
                                                  komponente,
                                                  editable=False)
            if not ok:
                return None
        else:
            plin = komponente[0]
        ime = QtGui.QFileDialog.getSaveFileName(parent=self,
                                                caption='Spremi pdf report',
                                                filter = 'pdf file (*.pdf)')
        if ime:
            report = ReportGenerator()
            try:
                report.generiraj_report(ime, plin, self)
            except Exception as err:
                logging.error(str(err), exc_info=True)
                msg = "\n".join(['Izvještaj nije uspješno generiran.', str(err)])
                QtGui.QMessageBox.information(self, 'Problem', msg)

    def get_koristene_serial_portove(self):
        """
        Metoda vraca listu koristenih serial portova u aplikaciji. Metoda zanemaruje
        trenutno koristeni port u umjeravanju.
        """
        setPortova = self.parent().parent().parent().parent().parent().get_aktivne_serial_portove()
        setPortova.discard(None)
        #moram omoguciti izbor istog seriala koji je koristen u umjeravanju
        trenutni = self.get_serial_kolektora()
        setPortova.discard(trenutni)
        return list(setPortova)

    def get_serial_kolektora(self):
        """
        Metoda dohvaca koristeni serial port u kolektoru.
        """
        try:
            return self.kolektor.get_used_serial()
        except Exception as err:
            logging.error(str(err), exc_info=True)
            return None

    def display_tab_kolektor(self, x):
        """
        Callback gumba za prikaz atba kolektor. Ulazni parametar je boolean (stanje gumba).
        Ako je x True:
        -stvori objekt kolektor
        -dodaj ga u tab widget i spoji signale
        Ako je x False:
        -zatvori objekt kolektor
        -izbrisi objekt kolektor
        """
        if x:
            uredjaj = self.datastore.get_uredjaj()
            konfig = self.datastore.get_konfig()
            #koristeni serial portovi?
            self.kolektor = Kolektor(uredjaj=uredjaj, konfig=konfig, parent=self, datastore=self.datastore)
            #connect signal i slot
            self.connect(self.kolektor,
                         QtCore.SIGNAL('spremi_preuzete_podatke(PyQt_PyObject)'),
                         self.aktiviraj_ucitane_podatke)
            self.connect(self.kolektor,
                         QtCore.SIGNAL('update_table_view'),
                         self.tableViewFrejm.update)
            self.glavniTabWidget.addTab(self.kolektor, 'Kolektor')
        else:
            msg = 'Ako ugasite tab za skupljanje podataka, izgubiti cete sve podatke koji nisu spremljeni. Da li zelite ugasiti kolektor?'
            title = 'Potvrdi gasenje kolektora'
            chk = QtGui.QMessageBox.question(self, title, msg, QtGui.QMessageBox.Ok | QtGui.QMessageBox.No)
            if chk == QtGui.QMessageBox.Ok:
                ind = self.glavniTabWidget.indexOf(self.kolektor)
                self.glavniTabWidget.removeTab(ind)
                self.kolektor.close()
                self.kolektor = QtGui.QWidget()
            else:
                self.pushButtonPrikupljanjePodataka.blockSignals(True)
                self.pushButtonPrikupljanjePodataka.toggle()
                self.pushButtonPrikupljanjePodataka.blockSignals(False)

    def tab_isValid(self, tabname):
        """helper metoda za provjeru da li je zadano mjerenje validno"""
        if tabname != None and tabname in self.dictTabova:
            return True
        else:
            return False

    def prikazi_tab_konverter(self):
        check = self.datastore.get_checkKonverter()
        if 'konverter' in self.dictTabova:
            if check:
                self.glavniTabWidget.addTab(self.dictTabova['konverter'], 'konverter')
            else:
                ind = self.glavniTabWidget.indexOf(self.dictTabova['konverter'])
                self.glavniTabWidget.removeTab(ind)

    def prikazi_tabove_odaziva(self):
        """toggle tabova odaziv..."""
        check = self.datastore.get_checkOdaziv()
        if check:
            for tab in self.dictTabova:
                if tab.endswith('-odaziv'):
                    self.glavniTabWidget.addTab(self.dictTabova[tab], tab)
        else:
            for tab in self.dictTabova:
                if tab.endswith('-odaziv'):
                    ind = self.glavniTabWidget.indexOf(self.dictTabova[tab])
                    self.glavniTabWidget.removeTab(ind)

    def recalculate_all_umjeravanja(self):
        """recalculate sve tabove umjeravanja"""
        print('RECALCULATE ALL UMJERAVANJA')
        for tab in self.dictTabova:
            if not tab.endswith('-odaziv') and tab != 'konverter':
                self.recalculate_tab(tabname=tab)

    def recalculate_all_tabs(self):
        """recalculate sve tabove"""
        print('RECALCULATE ALL')
        for tab in self.dictTabova:
            self.recalculate_tab(tabname=tab)

    def recalculate_tab_konverter(self):
        print('RECALCULATE KONVERTER')
        self.recalculate_tab(tabname='konverter')

    @pomocni.activate_wait_spinner
    def recalculate_tab(self, tabname=None):
        """recalculate pojedinacni tab"""
        self.set_modified(True)
        try:
            if self.tab_isValid(tabname):
                print('recalculating --> {0}'.format(tabname))
                if tabname == 'konverter':
                    tocke = self.datastore.tabData[tabname].get_tocke()
                    opseg = self.datastore.get_izabraniOpseg()
                    cnox50 = self.datastore.get_cNOx50()
                    cnox95 = self.datastore.get_cNOx95()
                    ecmin = self.datastore.get_uredjaj().get_analitickaMetoda().get_Ec_min()
                    ecmax = self.datastore.get_uredjaj().get_analitickaMetoda().get_Ec_max()
                    frejm = self.datastore.tabData[tabname].get_frejm()
                    if not isinstance(frejm, pd.core.frame.DataFrame):
                        #nije zadan dataframe
                        return None
                    mapa = kalkulator.racunaj_vrijednosti_provjere_konvertera(tocke=tocke,
                                                                              opseg=opseg,
                                                                              frejm=frejm,
                                                                              cnox50=cnox50,
                                                                              cnox95=cnox95,
                                                                              ecmin=ecmin,
                                                                              ecmax=ecmax)
                    self.dictTabova[tabname].update_rezultat(mapa)
                    self.datastore.tabData[tabname].set_rezultat(mapa)
                elif tabname.endswith('-odaziv'):
                    self.dictTabova[tabname].update_rezultate()
                else:
                    tocke = self.datastore.tabData[tabname].get_tocke()
                    linearnost = self.datastore.get_checkLinearnost()
                    ponovljivost = self.datastore.get_checkPonovljivost()
                    opseg = self.datastore.get_izabraniOpseg()
                    cCRM = self.datastore.get_koncentracijaCRM()
                    sCRM = self.datastore.get_UCRM()
                    #dilucija
                    key = self.datastore.get_izabranaDilucija()
                    dilucija = self.datastore.get_objekt_izabrane_dilucije(key)
                    uNul = dilucija.get_uNul()
                    uKal = dilucija.get_uKal()
                    #data
                    frejm = self.datastore.tabData[tabname].get_frejm()
                    if isinstance(frejm, pd.core.frame.DataFrame):
                        data = list(frejm[tabname])
                    else:
                        #nije zadan dataframe
                        return None
                    #generator cistog zraka
                    key = self.datastore.get_izabraniGenerator()
                    generator = self.datastore.get_objekt_izabranog_generatora(key)
                    if tabname == 'SO2':
                        plinMaxC = generator.get_maxSO2()
                    elif tabname in ['NOx', 'NO', 'NO2']:
                        plinMaxC = generator.get_maxNOx()
                    elif tabname == 'CO':
                        plinMaxC = generator.get_maxCO()
                    elif tabname == 'O3':
                        plinMaxC = generator.get_maxO3()
                    else:
                        plinMaxC = generator.get_maxBTX()
                    #metoda
                    metoda = self.datastore.get_uredjaj().get_analitickaMetoda()
                    jedinica = metoda.get_jedinica()
                    srzlimit = metoda.get_Srz()
                    srslimit = metoda.get_Srs()
                    rzlimit = metoda.get_rz()
                    rmaxlimit = metoda.get_rmax()
                    mapa = kalkulator.racun_umjeravanja(tocke=tocke,
                                                        data=data,
                                                        linearnost=linearnost,
                                                        opseg=opseg,
                                                        cCRM=cCRM,
                                                        sCRM=sCRM,
                                                        uNul=uNul,
                                                        uKal=uKal,
                                                        plinMaxC=plinMaxC,
                                                        ponovljivost=ponovljivost,
                                                        jedinica=jedinica,
                                                        srzlimit=srzlimit,
                                                        srslimit=srslimit,
                                                        rzlimit=rzlimit,
                                                        rmaxlimit=rmaxlimit)
                    self.dictTabova[tabname].update_rezultat(mapa)
                    self.datastore.tabData[tabname].set_rezultat(mapa)
            else:
                msg = 'recalculate nepostojeceg taba {0}'.format(str(tabname))
                logging.warning(msg)
        except Exception as err:
            logging.error(str(err), exc_info=True)

    def aktiviraj_ucitane_podatke(self, mapa):
        """
        Spremanje podataka iz prozora u neku instancu otvorenog umjeravanja ili otvaranje novog umjeravanja..
        kljucevi mape su:
        'podaci':sekundniFrejm
        'minutniPodaci':minutniFrejm
        'uredjaj':serijski broj uredjaja
        """
        minutni = mapa['minutniPodaci']
        sekundni = mapa['podaci']
        for tab in self.dictTabova:
            if tab.endswith('-odaziv'):
                #prebaci sekundni frejm sa rise i fall podacima za tab u datastore
                model = self.dictTabova[tab].get_model()
                komponenta = self.dictTabova[tab].naziv
                model.set_slajs(sekundni[komponenta], komponenta)
                self.datastore.tabData[tab].set_frejm(model.get_frejm())
                self.recalculate_tab(tabname=tab)
            else:
                #prebaci minutni frejm u datastore
                self.datastore.tabData[tab].set_frejm(minutni)
                #updejtaj qt model u tab widgetu
                model = self.dictTabova[tab].get_model()
                model.set_frejm(minutni)
                self.recalculate_tab(tabname=tab)

    def read_data_from_csv(self):
        """
        Ucitavanje sirovih podataka iz csv filea putem wizarda.

        redosljed ucitavanja je bitan:
        1. clear tabove (ako su razliciti od postojecih tabova)
        2. update dokument sa novim podacima
        3. create tabove (ako su prethodno izbrisani)
        """
        fileWizard = read_file_wizard.CarobnjakZaCitanjeFilea(datastore=self.datastore)
        ok = fileWizard.exec_()
        if ok:
            frejmovi = fileWizard.get_frejmovi()
            minutni = frejmovi['minutni'] #za tab umjeravanja i konverter
            sekundni = frejmovi['sekundni'] #za tab odaziva
            for tab in self.dictTabova:
                if tab.endswith('-odaziv'):
                    #prebaci sekundni frejm sa rise i fall podacima za tab u datastore
                    model = self.dictTabova[tab].get_model()
                    komponenta = self.dictTabova[tab].naziv
                    model.set_slajs(sekundni[komponenta], komponenta)
                    self.datastore.tabData[tab].set_frejm(model.get_frejm())
                    self.recalculate_tab(tabname=tab)
                else:
                    #prebaci minutni frejm u datastore
                    self.datastore.tabData[tab].set_frejm(minutni)
                    #updejtaj qt model u tab widgetu
                    model = self.dictTabova[tab].get_model()
                    model.set_frejm(minutni)
                    self.recalculate_tab(tabname=tab)

    def interakcija_sa_tablicom_pojedinih_mjerenja(self, indeks):
        """interakcija sa tablicom sa podacima"""
        try:
            widg = self.glavniTabWidget.currentWidget()
            mjerenje = widg.plin
            x = indeks.row()
            if mjerenje == 'postavke':
                pass
            elif mjerenje.endswith('-odaziv'):
                #delegiraj klik widgetu
                widg.update_rezultate()
            elif mjerenje == 'konverter':
                model = self.dictTabova[mjerenje].get_model()
                model.set_start(x)
                self.datastore.tabData[mjerenje].set_startIndeks(x)
                self.recalculate_tab(tabname=mjerenje)
            else:
                if self.datastore.isNOx:
                    model = self.dictTabova['NO'].get_model()
                    model.set_start(x)
                    self.datastore.tabData['NO'].set_startIndeks(x)
                    self.recalculate_tab(tabname='NO')
                    model = self.dictTabova['NOx'].get_model()
                    model.set_start(x)
                    self.datastore.tabData['NOx'].set_startIndeks(x)
                    self.recalculate_tab(tabname='NOx')
                else:
                    model = self.dictTabova[mjerenje].get_model()
                    model.set_start(x)
                    self.datastore.tabData[mjerenje].set_startIndeks(x)
                    self.recalculate_tab(tabname=mjerenje)
        except Exception as err:
            logging.error(str(err), exc_info=True)

    def promjena_aktivnog_taba(self, x):
        """metoda zaduzena za promjenu konteksta prilikom promjene taba. Definira
        koji je model aktivan u ljevoj tablici sa podacima."""
        try:
            nazivTaba = self.glavniTabWidget.currentWidget().plin
            if nazivTaba == 'Postavke':
                emptyModel = SiroviFrameModel(frejm=pd.DataFrame(),
                                              tocke=self.datastore.init_tockeUmjeravanja(),
                                              start=0)
                self.tableViewFrejm.setModel(emptyModel)
                self.tableViewFrejm.update()
                #exit from method
                return None
            elif nazivTaba == 'kolektor':
                model = self.kolektor.get_model()
                self.tableViewFrejm.setModel(model)
                self.tableViewFrejm.update()
            else:
                model = self.dictTabova[nazivTaba].get_model()
                self.tableViewFrejm.setModel(model)
                self.tableViewFrejm.update()

            #display stupaca u modelu
            if nazivTaba.endswith('-odaziv'):
                self.glavniTabWidget.currentWidget().update_rezultate()
                self.tableViewFrejm.resizeColumnToContents(0)
                self.tableViewFrejm.resizeColumnToContents(1)
                self.tableViewFrejm.horizontalHeader().setStretchLastSection(True)
            else:
                self.tableViewFrejm.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
            self.tableViewFrejm.update()
        except Exception as err:
            logging.error(str(err), exc_info=True)
################################################################################
    #metode za rad i prikaz umjeravanja
    def init_tabove(self):
        """
        stvaranje tabova i povezivanje istih...
        """
        self.dictTabova = {}
        #tab postavke
        self.tabPostavke = tab_postavke.TabPostavke(datastore=self.datastore)
        self.glavniTabWidget.addTab(self.tabPostavke, 'Postavke')
        #ostali tabovi:
        for tab in self.datastore.tabData.keys():
            if tab.endswith('-odaziv'):
                self.dictTabova[tab] = tab_odaziv.TabOdaziv(datastore=self.datastore, plin=tab)
                ### scroll podataka tab odaziv...###
                self.connect(self.dictTabova[tab],
                             QtCore.SIGNAL('scroll_to_index(PyQt_PyObject)'),
                             self.scroll_na_indeks)
                if self.datastore.get_checkOdaziv():
                    self.glavniTabWidget.addTab(self.dictTabova[tab], tab)
            elif tab == 'konverter':
                self.dictTabova[tab] = tab_konverter.TabKonverter(datastore=self.datastore, plin=tab)
                if self.datastore.get_checkKonverter():
                    self.glavniTabWidget.addTab(self.dictTabova[tab], tab)
            else:
                self.dictTabova[tab] = tab_rezultat.TabRezultat(datastore=self.datastore, plin=tab)
                self.glavniTabWidget.addTab(self.dictTabova[tab], tab)
                #connectioni za dodavanje, brisanje i editiranje tocaka pojedinog taba
                self.connect(self.dictTabova[tab],
                             QtCore.SIGNAL('panel_dodaj_umjernu_tocku'),
                             self.dodaj_umjernu_tocku)
                self.connect(self.dictTabova[tab],
                             QtCore.SIGNAL('panel_makni_umjernu_tocku(PyQt_PyObject)'),
                             self.makni_umjernu_tocku)
                self.connect(self.dictTabova[tab],
                             QtCore.SIGNAL('panel_edit_umjernu_tocku(PyQt_PyObject)'),
                             self.edit_umjernu_tocku)

    def dodaj_umjernu_tocku(self):
        """
        Metoda dodaje tocku na popis tocaka za mjerenje(tab). Dodaje je iza vec
        definiranih tocaka, ukupno 30 indeksa, prvih 15 zanemarenih, random boja.
        """
        try:
            tabname = self.glavniTabWidget.currentWidget().plin
            frejm = self.datastore.tabData[tabname].get_frejm()
            if isinstance(frejm, pd.core.frame.DataFrame):
                tocke = copy.deepcopy(self.datastore.tabData[tabname].get_tocke())
                ime = "".join(['TOCKA',str(len(tocke)+1)])
                indeks =  max([max(tocka.indeksi) for tocka in tocke])
                start = indeks+15
                end = start+15
                cref = 0.0
                novaTocka = Tocka(ime=ime, start=start, end=end, cref=cref)
                tocke.append(novaTocka)
                self.datastore.tabData[tabname].set_tocke(tocke)
                self.recalculate_tab(tabname=tabname)
        except Exception as err:
            logging.error(str(err), exc_info=True)

    def makni_umjernu_tocku(self, red):
        """
        Metoda brise tocku zadanu indeksom (red) sa popisa tocaka za mjerenje.
        Metoda mjenja nazive ostalih tocaka radi konzistencije.
        """
        try:
            tabname = self.glavniTabWidget.currentWidget().plin
            frejm = self.datastore.tabData[tabname].get_frejm()
            if isinstance(frejm, pd.core.frame.DataFrame):
                tocke = copy.deepcopy(self.datastore.tabData[tabname].get_tocke())
                tocke.pop(red)
                #rename ostale tocke
                for i in range(len(tocke)):
                    tocke[i].ime = "".join(['TOCKA',str(i+1)])
                self.datastore.tabData[tabname].set_tocke(tocke)
                self.recalculate_tab(tabname=tabname)
        except Exception as err:
            logging.error(str(err), exc_info=True)

    def edit_umjernu_tocku(self, red):
        """
        Edit umjerne tocke. Poziva se dijalog za edit parametara.
        Ulazni parametar (red) je indeks pod kojim se ta tocka nalazi
        u listi tocaka.
        """
        try:
            tabname = self.glavniTabWidget.currentWidget().plin
            tocke = copy.deepcopy(self.datastore.tabData[tabname].get_tocke())
            start = self.datastore.tabData[tabname].get_startIndeks()
            frejm = self.datastore.tabData[tabname].get_frejm()
            if isinstance(frejm, pd.core.frame.DataFrame):
                staraTocka = tocke[red]
                if staraTocka.crefFaktor == 0.0:
                    staraTockaIsZero = True
                else:
                    staraTockaIsZero = False
                brojZeroTocaka = len([i for i in tocke if i.crefFaktor == 0.0])
                #poziv dijaloga za edit
                dijalog = dijalog_edit_tocke.EditTockuDijalog(frejm=frejm,
                                                              tocke=tocke,
                                                              start=start,
                                                              indeks=red,
                                                              parent=self)
                if dijalog.exec_():
                    novaTocka = dijalog.get_promjenjena_tocka()
                    if staraTockaIsZero and brojZeroTocaka == 1:
                        if novaTocka.crefFaktor == 0.0:
                            tocke[red] = novaTocka
                            self.datastore.tabData[tabname].set_tocke(tocke)
                            self.recalculate_tab(tabname=tabname)
                        else:
                            QtGui.QMessageBox.information(self, 'Oprez','Mora postojati barem jedna zero tocka. Cref faktor tocke nije promjenjen.')
                            novaTocka.crefFaktor = 0.0
                            tocke[red] = novaTocka
                            self.datastore.tabData[tabname].set_tocke(tocke)
                            self.recalculate_tab(tabname=tabname)
                    else:
                        tocke[red] = novaTocka
                        self.datastore.tabData[tabname].set_tocke(tocke)
                        self.recalculate_tab(tabname=tabname)
        except Exception as err:
            logging.error(str(err), exc_info=True)
################################################################################
    #metode za MDI interface
    def novi_file(self, folder=None):
        """inicijalizacija novog filea umjeravanja"""
        self.bezNaslova = True
        if folder:
            if os.path.isdir(folder):
                self.workingFolder = folder
        selectedFilter = "Umjeravanja (*.kal)"
        path = QtGui.QFileDialog.getSaveFileName(self, 'Save as', self.workingFolder, selectedFilter)
        if path:
            fullpath = os.path.normpath(path)
        else:
            #path nije zadan, koristi default
            vrijeme = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            naziv = 'dokument{0}_{1}.kal'.format(str(Umjeravanje.redniBroj), vrijeme)
            Umjeravanje.redniBroj += 1
            fullpath = os.path.join(self.workingFolder, naziv)
            fullpath = os.path.normpath(fullpath) #normalizacija
        self.set_trenutnoImeFilea(fullpath)
        self.set_modified(True)

    def set_modified(self, x):
        """setter cheka za stanje promjene dokumenta"""
        self.isModified = x
        if x:
            title = " ".join([self.trenutnoImeFilea, '(*)'])
        else:
            title = self.trenutnoImeFilea
        self.setWindowTitle(title)

    def get_modified(self):
        """getter cheka za stanje promjene dokumenta"""
        return self.isModified

    def set_trenutnoImeFilea(self, path):
        """setter patha do filea"""
        self.trenutnoImeFilea = path
        self.bezNaslova = False

    def get_trenutnoImeFilea(self):
        """getter patha do filea"""
        return self.trenutnoImeFilea

    def load_file(self, path=None):
        """load podataka iz spremljenog filea u objekt"""
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            if path==None:
                return False
            self.set_full_path_filea(path)
            self.recalculate_all_tabs()
            QtGui.QApplication.restoreOverrideCursor()
            logging.info('Umjeravanje {0} loaded'.format(path))
            return True
        except Exception as err:
            logging.error(str(err), exc_info=True)
            QtGui.QApplication.restoreOverrideCursor()
            return False

    def save(self):
        """save podatke u file"""
        if self.bezNaslova:
            return self.save_file_as()
        else:
            return self.save_file(self.trenutnoImeFilea)

    def save_file_as(self):
        """save file bez naslova... otvori dijalog za izbor naziva"""
        selectedFilter = "Umjeravanja (*.kal)"
        path = QtGui.QFileDialog.getSaveFileName(self, 'Save as', self.trenutnoImeFilea, selectedFilter)
        if not path:
            return False
        if not path.endswith('.kal'):
            path = "".join([path, '.kal'])
        return self.save_file(path)

    def save_file(self, path):
        """funkcija za spremanje stanja umjeravanja u file"""
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            with open(path, 'wb') as the_file:
                #pickle datastore
                data = self.datastore.serialize()
                the_file.write(data)
            self.set_full_path_filea(path)
            QtGui.QApplication.restoreOverrideCursor()
            logging.info('Umjeravanje {0} saved'.format(path))
            return True
        except Exception as err:
            logging.error(str(err), exc_info=True)
            QtGui.QApplication.restoreOverrideCursor()
            QtGui.QMessageBox.warning(self, 'Problem', 'Umjeravanje nije uspjesno spremljeno.\n{0}'.format(str(err)))
            return False

    def get_filename_from_path(self):
        """funkcija vraca samo naziv trenunog imena filea (bez foldera)"""
        x = os.path.split(self.trenutnoImeFilea)
        return x[1]

    def closeEvent(self, event):
        if self.provjeri_status_prije_izlaza():
            #propisno ugasi kolektor
            self.kolektor.close()
            self.kolektor = QtGui.QWidget()
            event.accept()
        else:
            event.ignore()

    def provjeri_status_prije_izlaza(self):
        """metoda provjerava da li su promjene spremljene prije gasenja prozora"""
        if self.get_modified():
            msg = 'Promjene na trenutnom umjeravanju nisu spremljene. Da li zelite spremiti promjene?'
            response = QtGui.QMessageBox.warning(self,
                                                 'Upozorenje',
                                                 msg,
                                                 QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard | QtGui.QMessageBox.Cancel)
            if response == QtGui.QMessageBox.Save:
                return self.save()
            elif response == QtGui.QMessageBox.Cancel:
                return False
        return True

    def set_full_path_filea(self, path):
        """metoda postavlja path do filea u objekt. Te mjenja naziv prozora i
        status 'spremljenosti' (koristi se prilikom spremanja i loada filea)"""
        self.set_trenutnoImeFilea(path)
        self.set_modified(False)
################################################################################

