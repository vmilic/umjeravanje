# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 09:41:20 2015

@author: DHMZ-Milic
"""
import logging
import copy
import gc #garbage collector
import sip
import numpy as np
import pandas as pd
from PyQt4 import QtGui, QtCore, uic
import app.view.canvas as canvas
import app.view.pomocni as view_helpers
import app.view.read_file_wizard as datareader
import app.view.dijalog_edit_tocke as dotedit
import app.reportgen.reportgen as pdfreport
import app.model.konfig_klase as konfig
import app.model.kalkulator as calc
import app.model.frejm_model as modeli
import app.model.model as doc
import app.view.rezultat_panel as panel



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

        ### setup view elemente ###
        self.tablicaRezultataUmjeravanja = QtGui.QWidget() #placeholder za tablicu
        self.layoutRezultati.addWidget(self.tablicaRezultataUmjeravanja)
        self.tablicaPrilagodba = view_helpers.TablicaFunkcijePrilagodbe()
        self.tablicaParametri = view_helpers.TablicaUmjeravanjeKriterij()
        self.konverterRezultatView = view_helpers.TablicaKonverterRezultati()
        self.tablicaKonverter = view_helpers.TablicaKonverterParametri()

        ### setup objekte za racunanje ###
        self.kalkulator = calc.RacunUmjeravanja(doc=self.dokument)
        self.konverterKalkulator = calc.ProvjeraKonvertera(doc=self.dokument)

        self.generiraj_tablicu_rezultata_umjeravanja()

        self.siroviPodaciModel = modeli.SiroviFrameModel()
        self.siroviPodaciView.setModel(self.siroviPodaciModel)
        self.siroviPodaciView.horizontalHeader().setStretchLastSection(True)

        self.konverterRezultatView.set_mjerna_jedinica(self.dokument.get_mjernaJedinica())
        self.konverterRezultatView.set_tocke(self.dokument.get_tockeKonverter())
        self.konverterRezultatView.set_data(self.dokument.get_konverterRezultat())

        self.konverterPodaciModel = modeli.SiroviFrameModel(tocke=self.dokument.get_tockeKonverter())
        self.konverterPodaciView.setModel(self.konverterPodaciModel)
        self.konverterPodaciView.horizontalHeader().setStretchLastSection(True)

        ### setup i postavljanje layouta za view elemente ###
        #grafovi
        self.inicijalizacija_grafova()
        #umjeravanje prilagodba
        self.layoutPrilagodba = QtGui.QVBoxLayout()
        self.layoutPrilagodba.addWidget(self.tablicaPrilagodba)
        self.layoutPrilagodba.addStretch(-1)
        self.layoutRezultati.addLayout(self.layoutPrilagodba)
        self.layoutRezultati.addStretch(-1)
        #umjeravanje kriterij prihvatljivosti
        self.layoutParametri.addWidget(self.tablicaParametri)
        self.layoutParametri.addStretch(-1)
        #vertikalni spacer za scroll area layout
        self.layoutUmjeravanje.addStretch(-1)
        #konverter rezultati
        self.layoutKonverterRezultati.addWidget(self.konverterRezultatView)
        self.layoutKonverterRezultati.addStretch(-1)
        #konverter kriterij prihvatljivosti
        self.layoutKonverterParametri.addWidget(self.tablicaKonverter)
        self.layoutKonverterParametri.addStretch(-1)
        #vertikalni spacer za scroll area layout
        self.konverterRezultatiLayout.addStretch(-1)

        ### setup signale i slotove ###
        self.setup_signal_connections()

        ### inicijalni setup kontrolnih elemenata gui-a ###
        self.dokument.init_listaDilucija()
        self.dokument.init_listaZrak()
        self.checkLinearnost.setChecked(self.dokument.get_provjeraLinearnosti())
        self.cnox50SpinBox.setValue(self.dokument.get_cNOx50())
        self.cnox95SpinBox.setValue(self.dokument.get_cNOx95())


    def setup_signal_connections(self):
        """
        connect actione i widgete za callbackovima
        """
        self.action_Exit.triggered.connect(self.close)
        self.action_ucitaj_podatke.triggered.connect(self.read_data)
        self.action_spremi.triggered.connect(self.save_umjeravanje_to_file)
        self.action_ucitaj.triggered.connect(self.load_umjeravanje_from_file)
        self.action_Napravi_pdf_report.triggered.connect(self.napravi_pdf_report)

        #izbor pocetka umjeravanja
        self.siroviPodaciView.clicked.connect(self.odaberi_start_umjeravanja)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_siroviPodaciStart(PyQt_PyObject)'),
                     self.set_start_umjeravanja)
        #izbor pocetka kontrole konvertera
        self.konverterPodaciView.clicked.connect(self.odaberi_start_provjere_konvertera)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_konverterPodaciStart(PyQt_PyObject)'),
                     self.set_start_provjere_konvertera)
        #provjera linearnosti
        self.checkLinearnost.toggled.connect(self.promjena_checkLinearnost)
        self.multiCheckLinearnost.toggled.connect(self.promjena_checkLinearnost)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_provjeraLinearnosti(PyQt_PyObject)'),
                     self.set_checkLinearnost)
        #provjera konvertera
        self.checkKonverter.toggled.connect(self.promjena_checkKonverter)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_provjeraKonvertera(PyQt_PyObject)'),
                     self.set_checkKonverter)
        #promjena opsega
        self.doubleSpinBoxOpseg.valueChanged.connect(self.promjena_doubleSpinBoxOpseg)
        self.konverterOpseg.valueChanged.connect(self.promjena_konverterOpseg)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_opseg(PyQt_PyObject)'),
                     self.set_doubleSpinBoxOpseg)
        #promjena izabranog mjerenja
        self.comboMjerenje.currentIndexChanged.connect(self.promjena_comboMjerenje)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_izabranoMjerenje(PyQt_PyObject)'),
                     self.set_comboMjerenje)
        #promjena izvora CRM
        self.izvorPlainTextEdit.textChanged.connect(self.promjena_izvorPlainTextEdit)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_izvorCRM(PyQt_PyObject)'),
                     self.set_izvorPlainTextEdit)
        #promjena koncentracije CRM
        self.doubleSpinBoxKoncentracijaCRM.valueChanged.connect(self.promjena_doubleSpinBoxKoncentracijaCRM)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_koncentracijaCRM(PyQt_PyObject)'),
                     self.set_doubleSpinBoxKoncentracijaCRM)
        #promjena sljedivosti CRM
        self.doubleSpinBoxSljedivostCRM.valueChanged.connect(self.promjena_doubleSpinBoxSljedivostCRM)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_sljedivostCRM(PyQt_PyObject)'),
                     self.set_doubleSpinBoxSljedivostCRM)
        #promjena izbora dilucijske jedinice
        self.comboDilucija.currentIndexChanged.connect(self.promjena_comboDilucija)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_izabranaDilucija(PyQt_PyObject)'),
                     self.set_comboDilucija)
        #promjena proizvodjaca dilucijske jedinice
        self.dilucijaProizvodjacLineEdit.textChanged.connect(self.promjena_dilucijaProizvodjacLineEdit)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_proizvodjacDilucija(PyQt_PyObject)'),
                     self.set_dilucijaProizvodjacLineEdit)
        #promjena sljedivosti dilucijske jedinice
        self.dilucijaSljedivostLineEdit.textChanged.connect(self.promjena_dilucijaSljedivostLineEdit)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_sljedivostDilucija(PyQt_PyObject)'),
                     self.set_dilucijaSljedivostLineEdit)
        #promjena izbora generatora cistog zraka
        self.comboZrak.currentIndexChanged.connect(self.promjena_comboZrak)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_izabraniZrak(PyQt_PyObject)'),
                     self.set_comboZrak)
        #promjena proizvodjaca generatora cistog zraka
        self.zrakProizvodjacLineEdit.textChanged.connect(self.promjena_zrakProizvodjacLineEdit)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_proizvodjacCistiZrak(PyQt_PyObject)'),
                     self.set_zrakProizvodjacLineEdit)
        #promjena sljedivosti generatora cistog zraka
        self.doubleSpinBoxSljedivostCistiZrak.valueChanged.connect(self.promjena_doubleSpinBoxSljedivostCistiZrak)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_sljedivostCistiZrak(PyQt_PyObject)'),
                     self.set_doubleSpinBoxSljedivostCistiZrak)
        #promjena teksta norme
        self.normaPlainTextEdit.textChanged.connect(self.promjena_normaPlainTextEdit)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_norma(PyQt_PyObject)'),
                     self.set_normaPlainTextEdit)
        #promjena oznake izvjesca
        self.oznakaIzvjescaLineEdit.textChanged.connect(self.promjena_oznakaIzvjescaLineEdit)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_oznakaIzvjesca(PyQt_PyObject)'),
                     self.set_oznakaIzvjescaLineEdit)
        #promjena broja obrasca
        self.brojObrascaLineEdit.textChanged.connect(self.promjena_brojObrascaLineEdit)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_brojObrasca(PyQt_PyObject)'),
                     self.set_brojObrascaLineEdit)
        #promjena broja revizije
        self.revizijaLineEdit.textChanged.connect(self.promjena_revizijaLineEdit)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_revizija(PyQt_PyObject)'),
                     self.set_revizijaLineEdit)
        #promjena datuma umjeravanja
        self.datumUmjeravanjaLineEdit.textChanged.connect(self.promjena_datumUmjeravanjaLineEdit)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_datumUmjeravanja(PyQt_PyObject)'),
                     self.set_datumUmjeravanjaLineEdit)
        #promjena temperature (okolisni uvijeti)
        self.temperaturaDoubleSpinBox.valueChanged.connect(self.promjena_temperaturaDoubleSpinBox)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_temperatura(PyQt_PyObject)'),
                     self.set_temperaturaDoubleSpinBox)
        #promjena relativne vlage (okolisni uvijeti)
        self.vlagaDoubleSpinBox.valueChanged.connect(self.promjena_vlagaDoubleSpinBox)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_vlaga(PyQt_PyObject)'),
                     self.set_vlagaDoubleSpinBox)
        #promjena tlaka zraka (okolisni uvijeti)
        self.tlakDoubleSpinBox.valueChanged.connect(self.promjena_tlakDoubleSpinBox)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_tlak(PyQt_PyObject)'),
                     self.set_tlakDoubleSpinBox)
        #promjena teksta napomene
        self.napomenaPlainTextEdit.textChanged.connect(self.promjena_napomenaPlainTextEdit)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_napomena(PyQt_PyObject)'),
                     self.set_napomenaPlainTextEdit)
        #promjena cnox50 parametra
        self.cnox50SpinBox.valueChanged.connect(self.promjena_cnox50SpinBox)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_cNOx50(PyQt_PyObject)'),
                     self.set_cnox50SpinBox)
        #promjena cnox95 parametra
        self.cnox95SpinBox.valueChanged.connect(self.promjena_cnox95SpinBox)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_cNOx95(PyQt_PyObject)'),
                     self.set_cnox95SpinBox)
        #popunjavanje comboMjerenje iz dokumenta
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_listaMjerenja(PyQt_PyObject)'),
                     self.napuni_comboMjerenje)
        #popunjavanje comboDilucija iz dokumenta
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_listaDilucija(PyQt_PyObject)'),
                     self.napuni_comboDilucija)
        #popunjavanje comboZrak iz dokumenta
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_listaZrak(PyQt_PyObject)'),
                     self.napuni_comboZrak)
        #promjena izabrani uredjaj
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_izabraniUredjaj(PyQt_PyObject)'),
                     self.set_labelUredjaj)
        #promjena izabrana postaja
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_izabranaPostaja(PyQt_PyObject)'),
                     self.set_labelPostaja)
        #promjena izabrani csv file
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_izabraniPathCSV(PyQt_PyObject)'),
                     self.set_labelDatoteka)
        #promjena umjernih tocaka (broj, postavke tocke...)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_tockeUmjeravanja'),
                     self.recalculate)
        #naredna iz dokumenta za ponovnim crtanjem tablice rezultata umjeravanja
        self.connect(self.dokument,
                     QtCore.SIGNAL('redraw_rezultateUmjeravanja'),
                     self.generiraj_tablicu_rezultata_umjeravanja)
        #promjena mjerne jedinice
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_mjernaJedinica(PyQt_PyObject)'),
                     self.set_mjernaJedinica)
        #promjena rezultata umjeravanja
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_rezultatUmjeravanja'),
                     self.generiraj_tablicu_rezultata_umjeravanja)
        #promjena slope data [slope, offset, prilagodbaA, prilagodbaB]
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_slopeData(PyQt_PyObject)'),
                     self.set_slopeData)
        #promjena parametara rezultata (kriterij prihvatljivosti)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_parametriRezultata(PyQt_PyObject)'),
                     self.set_kriterijPrihvatljivosti)
        #promjena rezultata konvertera
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_konverterRezultat(PyQt_PyObject)'),
                     self.set_konverterRezultat)
        #promjena efikasnosti konvertera
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_listaEfikasnostiKonvertera(PyQt_PyObject)'),
                     self.set_efikasnostiKonvertera)
        #setter za frejm sirovih podataka preuzetih iz dokumenta
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_siroviPodaci(PyQt_PyObject)'),
                     self.set_ucitane_sirove_podatke)
        #setter za frejm sirovih podataka za konverter preuzetih iz dokumenta
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_konverterPodaci(PyQt_PyObject)'),
                     self.set_ucitane_konverter_podatke)
        #setup usporednih mjerenja
        self.connect(self.dokument,
                     QtCore.SIGNAL('postavi_usporedna_mjerenja'),
                     self.postavi_usporedna_umjeravanja)



    def inicijalizacija_grafova(self):
        """inicijalizacija i postavljanje kanvasa za grafove u layout."""
        meta1 = {'xlabel':'referentna koncentracija, cref',
                 'ylabel':'koncentracija, c',
                 'title':'Cref / koncentracija graf'}
        meta2 = {'xlabel':'vrijeme',
                 'ylabel':'koncentracija, c',
                 'title':'Individualna mjerenja'}
        self.crefCanvas = canvas.Kanvas(meta=meta1)
        self.mjerenjaCanvas = canvas.KanvasMjerenja(meta=meta2)
        self.layoutGrafovi.addWidget(self.crefCanvas)
        self.layoutGrafovi.addWidget(self.mjerenjaCanvas)

    def generiraj_tablicu_rezultata_umjeravanja(self):
        """
        metoda koja generira tablicu umjeravanja i postavlja je u specificno mjesto
        u layoutu.
        Dolazi do lagane komplikacije u nacinu rada metode zbog parent-child
        odnosa izmedju widgeta i layouta u njemu.
        """
        #korak 1, maknuti widget iz layouta
        self.layoutRezultati.removeWidget(self.tablicaRezultataUmjeravanja)
        #korak 2, moram zatvoriti widget (garbage collection...)
        sip.delete(self.tablicaRezultataUmjeravanja)
        self.tablicaRezultataUmjeravanja = None
        #self.tablicaRezultataUmjeravanja.destroy()
        gc.collect() #force garbage collection
        #korak 3, stvaram novi widget (tablicu) i dodjelujem je istom imenu
        try:
            self.tablicaRezultataUmjeravanja = view_helpers.TablicaUmjeravanje(
                tocke=self.dokument.get_tockeUmjeravanja(),
                data=self.dokument.get_rezultatUmjeravanja(),
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
            self.layoutRezultati.insertWidget(0, self.tablicaRezultataUmjeravanja)
            #korak 5, update layouta
            self.layoutRezultati.update()
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
        self.dokument.dodaj_umjernu_tocku()

    def remove_red_umjeravanje(self):
        """metoda za brisanje tocke za umjeravanje iz dokumenta"""
        red = self.tablicaRezultataUmjeravanja.get_redak()
        self.dokument.makni_umjernu_tocku(red-1) #korekcija za zero based indexing

    def edit_red_umjeravanje(self):
        """metoda za editiranje umjerne tocke uz pomoc dijaloga"""
        red = self.tablicaRezultataUmjeravanja.get_redak()
        self.edit_tocku_dijalog(red-1) #korekcija za zero based indexing

    def add_red_umjeravanje_panel(self):
        """metoda (slot) za dodavanje tocaka u dokument"""
        self.dokument.dodaj_umjernu_tocku()

    def remove_red_umjeravanje_panel(self, x):
        """metoda za brisanje tocke za umjeravanje iz dokumenta, x je broj redka"""
        red = int(x)
        self.dokument.makni_umjernu_tocku(red)

    def edit_red_umjeravanje_panel(self, x):
        """metoda za editiranje umjerne tocke uz pomoc dijaloga"""
        red = int(x)
        self.edit_tocku_dijalog(red)


    def edit_tocku_dijalog(self, indeks):
        """
        Poziv dijaloga za edit vrijednosti parametara izabrane tocke.
        ulazni parametar indeks je indeks pod kojim se ta tocka nalazi
        u listi self.konfiguracija.umjerneTocke
        """
        tocke = copy.deepcopy(self.dokument.get_tockeUmjeravanja())
        podaci = self.dokument.get_siroviPodaci().copy()
        start = self.dokument.get_siroviPodaciStart()
        self.dijalog = dotedit.EditTockuDijalog(indeks=indeks,
                                                tocke=tocke,
                                                frejm=podaci,
                                                start=start,
                                                parent=None)
        if self.dijalog.exec_():
            dots = self.dijalog.get_tocke()
            tocka = dots[indeks]
            self.dokument.zamjeni_umjernu_tocku(indeks, tocka)
            self.recalculate()

    def read_data(self):
        """
        ucitavanje sirovih podataka preko wizarda
        """
        self.fileWizard = datareader.CarobnjakZaCitanjeFilea(uredjaji=self.dokument.get_uredjaji(),
                                                             postaje=self.dokument.get_postaje())
        prihvacen = self.fileWizard.exec_()
        if prihvacen:
            frejm = self.fileWizard.get_frejm()
            lokacija = self.fileWizard.get_postaja()
            uredjaj = self.fileWizard.get_uredjaj()
            path = str(self.fileWizard.get_path_do_filea())
            # postavi info o ucitanom fileu
            self.dokument.set_izabraniUredjaj(uredjaj)
            self.dokument.set_izabranaPostaja(lokacija)
            self.dokument.set_izabraniPathCSV(path)
            #postavi frejm sa sirovim podacima
            self.postavi_sirove_podatke(frejm)
            #update combobox za izbor mjerenja
            komponente = set(self.dokument.uredjaji[uredjaj]['komponente'])
            komponente.remove('None')
            komponente = list(komponente)
            self.dokument.set_listaMjerenja(komponente)
            self.recalculate()
            self.postavi_usporedna_umjeravanja()

    def set_ucitane_sirove_podatke(self, x):
        """setter sirovih podataka ucitanih iz spremljenog filea umjeravanja.
        Ulazni parametar x je dict:
        {'frejm': pandas frejm podataka, 'start': pocetni indeks}"""
        frejm = x['frejm']
        start = x['start']
        udots = self.dokument.get_tockeUmjeravanja()
        self.siroviPodaciModel.set_frejm(frejm)
        self.siroviPodaciModel.set_tocke(udots)
        self.siroviPodaciModel.set_start_prilikom_loada(start)
        self.siroviPodaciView.update()

    def set_ucitane_konverter_podatke(self, x):
        """setter sirovih podataka za efikasnost konvertera ucitanih iz spremljenog
        filea umjeravanja.
        Ulazni parametar x je dict:
        {'frejm': pandas frejm podataka, 'start': pocetni indeks}"""
        frejm = x['frejm']
        start = x['start']
        kdots = self.dokument.get_tockeKonverter()
        self.konverterPodaciModel.set_frejm(frejm)
        self.konverterPodaciModel.set_tocke(kdots)
        self.konverterPodaciModel.set_start_prilikom_loada(start)
        self.konverterPodaciView.update()

    def postavi_sirove_podatke(self, frejm):
        """
        Metoda postavlja pandas datafrejm (ulazni parametar) u member,
        predaje ga modelu i updatea view sa ucitanim podacima.
        """
        siroviPodaci = frejm.copy()
        konverterPodaci = frejm.copy()
        udots = self.dokument.get_tockeUmjeravanja()
        kdots = self.dokument.get_tockeKonverter()
        self.dokument.set_siroviPodaci(siroviPodaci)
        self.siroviPodaciModel.set_frejm(siroviPodaci)
        self.siroviPodaciModel.set_tocke(udots)
        self.siroviPodaciView.update()
        #postavljanje podataka za provjeru konvertera samo ako je NOX
        testSet = set(['NOx', 'NO', 'NO2'])
        dataSet = set(frejm.columns)
        if testSet.issubset(dataSet):
            self.dokument.set_konverterPodaci(konverterPodaci)
            self.konverterPodaciModel.set_frejm(konverterPodaci)
            self.konverterPodaciModel.set_tocke(kdots)
            self.konverterPodaciView.setModel(self.konverterPodaciModel)
            self.konverterPodaciView.update()
        else:
            self.dokument.set_konverterPodaci(pd.DataFrame())
            self.konverterPodaciModel.set_frejm(pd.DataFrame())
            self.konverterPodaciModel.set_tocke(kdots)
            self.konverterPodaciView.setModel(self.konverterPodaciModel)
            self.konverterPodaciView.update()

    def set_labelUredjaj(self, tekst):
        """Setter serijskog broja uredjaja (tekst) u label"""
        self.labelUredjaj.setText(tekst)
        self.recalculate()

    def set_labelPostaja(self, tekst):
        """Setter naziva postaje na kojoj je smjesten uredjaj u label"""
        self.labelPostaja.setText(tekst)

    def set_labelDatoteka(self, tekst):
        """Setter punog patha i naziva fajla sa sirovim csv podacima"""
        self.labelDatoteka.setText(tekst)

    def set_mjernaJedinica(self, jedinica):
        """Setter mjerne jedinice u labele i druge elemente gui-a"""
        self.labelJedinicaOpseg.setText(jedinica)
        self.labelJedinicaCCRM.setText(jedinica)
        self.labelKonverterOpseg.setText(jedinica)
        self.labelKonverter50.setText(jedinica)
        self.labelKonverter95.setText(jedinica)
        self.labelJedinicaZrak.setText(jedinica)
        self.konverterRezultatView.set_mjerna_jedinica(jedinica)

    def promjena_comboMjerenje(self, x):
        """slot koji dokumentu javlja promjenu izabranog mjerenja"""
        value = self.comboMjerenje.currentText()
        self.dokument.set_izabranoMjerenje(value)

    def set_comboMjerenje(self, x):
        """Metoda postavlja izabrano mjerenje preuzeto iz dokumenta u gui
        widgete"""
        ind = self.comboMjerenje.findText(x)
        self.comboMjerenje.setCurrentIndex(ind)
        self.recalculate()

    def promjena_doubleSpinBoxOpseg(self, x):
        """slot koji dokumentu javlja promjenu opsega mjerenja"""
        value = self.doubleSpinBoxOpseg.value()
        self.dokument.set_opseg(value)

    def set_doubleSpinBoxOpseg(self, x):
        """Metoda postavlja izabrani opseg preuzet iz dokumenta u gui widgete
        x je lista [vrijednost, neki boolean], boolean je odlucijuci faktor
        za recalculate"""
        #TODO!
        self.doubleSpinBoxOpseg.setValue(x[0])
        self.konverterOpseg.setValue(x[0])
        if x[1] == True:
            print('recaclulating opseg change')
            self.recalculate()
        else:
            print('not recaclulating opseg change')

    def promjena_izvorPlainTextEdit(self):
        """slot koji dokumentu javlja promjenu izvora CRM-a"""
        value = self.izvorPlainTextEdit.toPlainText()
        self.dokument.set_izvorCRM(value)

    def set_izvorPlainTextEdit(self, x):
        """Metoda postavlja izvorCRM u gui widget"""
        self.izvorPlainTextEdit.setPlainText(x)
        self.izvorPlainTextEdit.moveCursor(QtGui.QTextCursor.End)

    def promjena_doubleSpinBoxKoncentracijaCRM(self, x):
        """slot koji dokumentu javlja promjenu koncentracije CRM-a"""
        value = self.doubleSpinBoxKoncentracijaCRM.value()
        self.dokument.set_koncentracijaCRM(value)

    def set_doubleSpinBoxKoncentracijaCRM(self, x):
        """Metoda postavlja koncentraciju CRM-a u gui widget"""
        self.doubleSpinBoxKoncentracijaCRM.setValue(x)
        self.recalculate()

    def promjena_doubleSpinBoxSljedivostCRM(self, x):
        """slot koji dokumentu javlja promjenu sljedivosti CRM-a"""
        value = self.doubleSpinBoxSljedivostCRM.value()
        self.dokument.set_sljedivostCRM(value)

    def set_doubleSpinBoxSljedivostCRM(self, x):
        """Metoda postavlja sljedivost CRM u gui widget"""
        self.doubleSpinBoxSljedivostCRM.setValue(x)
        self.recalculate()

    def promjena_comboDilucija(self, x):
        """slot koji dokumentu javlja promjenu izabrane dilucijske jedinice"""
        value = self.comboDilucija.currentText()
        self.dokument.set_izabranaDilucija(value)

    def set_comboDilucija(self, x):
        """Metoda postavlja izabranu dilucijsku jedinicu preuzetu iz dokumenta
        u gui widget"""
        ind = self.comboDilucija.findText(x)
        self.comboDilucija.setCurrentIndex(ind)
        self.recalculate()

    def promjena_dilucijaProizvodjacLineEdit(self, x):
        """slot koji javlja dokumentu promjenu proizvodjaca dilucijske jedinice"""
        value = self.dilucijaProizvodjacLineEdit.text()
        self.dokument.set_proizvodjacDilucija(value)

    def set_dilucijaProizvodjacLineEdit(self, x):
        """Metoda postavlja proizvodjaca dilucijske jedinice preuzetu iz dokumenta
        u gui widget"""
        self.dilucijaProizvodjacLineEdit.setText(x)

    def promjena_dilucijaSljedivostLineEdit(self, x):
        """slot koji javlja dokumentu promjenu sljedivosti dilucijske jedinice"""
        value = self.dilucijaSljedivostLineEdit.text()
        self.dokument.set_sljedivostDilucija(value)

    def set_dilucijaSljedivostLineEdit(self, x):
        """Metoda postavlja sljedivost dilucijske jedinice preuzetu iz dokumenta
        u gui widget"""
        self.dilucijaSljedivostLineEdit.setText(x)

    def promjena_comboZrak(self, x):
        """slot koji javlja dokumentu da je doslo do promjene izabranog generatora
        cistog zraka"""
        value = self.comboZrak.currentText()
        self.dokument.set_izabraniZrak(value)

    def set_comboZrak(self, x):
        """Metoda postavlja izabrani generator cistog zraka iz dokumenta u gui
        widget"""
        ind = self.comboZrak.findText(x)
        self.comboZrak.setCurrentIndex(ind)
        self.recalculate()

    def promjena_zrakProizvodjacLineEdit(self, x):
        """slot koji postavlja proizvodjaca generatora cistog zraka u dokument"""
        value = self.zrakProizvodjacLineEdit.text()
        self.dokument.set_proizvodjacCistiZrak(value)

    def set_zrakProizvodjacLineEdit(self, x):
        """Metoda postavlja proizvodjaca generatora cistog zraka iz dokumenta
        u gui widget"""
        self.zrakProizvodjacLineEdit.setText(x)

    def promjena_doubleSpinBoxSljedivostCistiZrak(self, x):
        """slot koji postavlja sljedivost generatora cistog zraka u dokument"""
        value = self.doubleSpinBoxSljedivostCistiZrak.value()
        self.dokument.set_sljedivostCistiZrak(value)

    def set_doubleSpinBoxSljedivostCistiZrak(self, x):
        """Metoda postavlja slejdivost generatora cistog zraka iz dokumenta u gui
        widget"""
        self.doubleSpinBoxSljedivostCistiZrak.setValue(x)
        self.recalculate()

    def promjena_normaPlainTextEdit(self):
        """slot koji postavlja tekst norme u dokument"""
        value = self.normaPlainTextEdit.toPlainText()
        self.dokument.set_norma(value)

    def set_normaPlainTextEdit(self, x):
        """Metoda koja postavlja tekst norme iz dokumenta u gui widget"""
        self.normaPlainTextEdit.setPlainText(x)
        self.normaPlainTextEdit.moveCursor(QtGui.QTextCursor.End)

    def promjena_oznakaIzvjescaLineEdit(self, x):
        """slot koji postavlja oznaku izvjesca u dokument"""
        value = self.oznakaIzvjescaLineEdit.text()
        self.dokument.set_oznakaIzvjesca(value)

    def set_oznakaIzvjescaLineEdit(self, x):
        """Metoda koja postavlja oznaku izvjesca iz dokumenta u gui widget"""
        self.oznakaIzvjescaLineEdit.setText(x)

    def promjena_brojObrascaLineEdit(self, x):
        """slot koji postavlja broj obrasca u dokument"""
        value = self.brojObrascaLineEdit.text()
        self.dokument.set_brojObrasca(value)

    def set_brojObrascaLineEdit(self, x):
        """Metoda koja postavlja broj obrasca iz dokumenta u gui widget"""
        self.brojObrascaLineEdit.setText(x)

    def promjena_revizijaLineEdit(self, x):
        """slot koji postavlja broj revizije u dokument"""
        value = self.revizijaLineEdit.text()
        self.dokument.set_revizija(value)

    def set_revizijaLineEdit(self, x):
        """Metoda koja postavlja broj revizije iz dokumenta u gui widget"""
        self.revizijaLineEdit.setText(x)

    def promjena_datumUmjeravanjaLineEdit(self, x):
        """slot koji postavlja datum umjeravanja u dokument"""
        value = self.datumUmjeravanjaLineEdit.text()
        self.dokument.set_datumUmjeravanja(value)

    def set_datumUmjeravanjaLineEdit(self, x):
        """metoda postavlja datum umjeravanja iz dokumenta u gui widget"""
        self.datumUmjeravanjaLineEdit.setText(x)

    def promjena_temperaturaDoubleSpinBox(self, x):
        """slot koji postavlja temperaturu (okolisni uvijeti) u dokument"""
        value = self.temperaturaDoubleSpinBox.value()
        self.dokument.set_temperatura(value)

    def set_temperaturaDoubleSpinBox(self, x):
        """metoda postavlja temperaturu (okolisni uvijeti) iz dokumenta u gui
        widget"""
        self.temperaturaDoubleSpinBox.setValue(x)

    def promjena_vlagaDoubleSpinBox(self, x):
        """slot koji postavlja relativnu vlagu (okolisni uvijeti) u dokumnet"""
        value = self.vlagaDoubleSpinBox.value()
        self.dokument.set_vlaga(value)

    def set_vlagaDoubleSpinBox(self, x):
        """Metoda postavlja relativnu vlagu (okolisni uvijeti) iz dokumenta u
        gui widget"""
        self.vlagaDoubleSpinBox.setValue(x)

    def promjena_tlakDoubleSpinBox(self, x):
        """slot koji postavlja tlak (okolisni uvijeti) u dokument"""
        value = self.tlakDoubleSpinBox.value()
        self.dokument.set_tlak(value)

    def set_tlakDoubleSpinBox(self, x):
        """metoda postavlja tlak (okolisni uvijeti) iz dokumenta u gui widget"""
        self.tlakDoubleSpinBox.setValue(x)

    def promjena_napomenaPlainTextEdit(self):
        """slot koji postavlja tekst napomena u dokument"""
        value = self.napomenaPlainTextEdit.toPlainText()
        self.dokument.set_napomena(value)

    def set_napomenaPlainTextEdit(self, x):
        """metoda postavlja tekst napomene iz dokumenta u gui widget"""
        self.napomenaPlainTextEdit.setPlainText(x)
        self.napomenaPlainTextEdit.moveCursor(QtGui.QTextCursor.End)

    def promjena_checkLinearnost(self, x):
        """slot koji zapisuje promjenu linearnosti (checkbox) u dokument"""
        value = self.checkLinearnost.isChecked()
        self.dokument.set_provjeraLinearnosti(value)

    def set_checkLinearnost(self, x):
        """metoda postavlja check linearnosti iz dokumenta u gui widget"""
        self.checkLinearnost.setChecked(x)
        self.multiCheckLinearnost.setChecked(x)
        self.recalculate()

    def promjena_checkKonverter(self, x):
        """slot koji zapisuje promjenu provjere konvertera u dokument (checkbox)"""
        value = self.checkKonverter.isChecked()
        self.dokument.set_provjeraKonvertera(value)

    def set_checkKonverter(self, x):
        """metoda postavlja ckeck provjere konvertera iz dokumenta u gui widget"""
        self.checkKonverter.setChecked(x)
        self.recalculate()

    def promjena_cnox50SpinBox(self, x):
        """slot koji zapisuje parametar cnox50 u dokument"""
        value = self.cnox50SpinBox.value()
        self.dokument.set_cNOx50(value)

    def set_cnox50SpinBox(self, x):
        """metoda postavlja parametar cNOx50 iz dokumenta u gui widget"""
        self.cnox50SpinBox.setValue(x)

    def promjena_cnox95SpinBox(self, x):
        """slot koji zapisuje parametar cnox95 u dokument"""
        value = self.cnox95SpinBox.value()
        self.dokument.set_cNOx95(value)

    def set_cnox95SpinBox(self, x):
        """metoda postavlja parametar cNOx95 iz dokumenta u gui widget"""
        self.cnox95SpinBox.setValue(x)

    def promjena_konverterOpseg(self, x):
        """slot koji zapisuje opseg konvertera u dokument (povezan sa opsegom
        umjeravanja)"""
        value = self.konverterOpseg.value()
        self.dokument.set_opseg(value)

    def napuni_comboMjerenje(self, x):
        """metoda postavlja listu x (lista stringova mjerenja) iz dokumenta
        u comboMjerenje widget"""
        self.comboMjerenje.clear()
        self.comboMjerenje.addItems(x)

    def napuni_comboDilucija(self, x):
        """metoda postavlja listu x (lista stringova dilucijskih jedinica) iz
        dokumenta u comboDilucija widget"""
        self.comboDilucija.clear()
        self.comboDilucija.addItems(x)

    def napuni_comboZrak(self, x):
        """metoda postavlja listu x (lista stringova generatora cistog zraka) iz
        dokumenta u comboZrak widget"""
        self.comboZrak.clear()
        self.comboZrak.addItems(x)

    def recalculate(self):
        """metoda je zaduzena za poziv kalkulatora na racunanje umjeravanja"""
        print('recalculating ...')
        self.kalkulator.racunaj()
        self.konverterKalkulator.racunaj()

        rezultat1 = self.kalkulator.rezultat.copy()
        self.dokument.set_rezultatUmjeravanja(rezultat1)

        slopeData = copy.deepcopy(self.kalkulator.get_slope_and_offset_list())
        self.dokument.set_slopeData(slopeData)
        #TODO!
        parametriUmjeravanje =  copy.deepcopy(self.kalkulator.get_provjeru_parametara())
        parametriUmjeravanje = [i for i in parametriUmjeravanje if not np.isnan(i[3])]
        ecKonverter = copy.deepcopy(self.konverterKalkulator.get_ec_parametar())
        if ecKonverter != None:
            if not np.isnan(ecKonverter[3]):
                parametriUmjeravanje.append(ecKonverter)
        self.dokument.set_parametriRezultata(parametriUmjeravanje)

        self.prikazi_grafove()

        rezultatKonverter = self.konverterKalkulator.rezultat
        self.dokument.set_konverterRezultat(rezultatKonverter)

        listaEfikasnosti = self.konverterKalkulator.get_listu_efikasnosti()
        self.dokument.set_listaEfikasnostiKonvertera(listaEfikasnosti)

        #update usporedni prikaz
        self.update_multiple_prikaz_rezultata()

    def odaberi_start_umjeravanja(self, x):
        """
        Metoda sluzi za odabir pocetnog indeksa (ljevi klik na tablicu sa sirovim
        podacima). Vrijednost se postavlja u dokument
        """
        self.dokument.set_siroviPodaciStart(x)

    def set_start_umjeravanja(self, x):
        """
        Metoda postavlja pocetni indeks umjeravanja u model (update gui)
        """
        self.siroviPodaciView.clearSelection()
        self.siroviPodaciModel.set_start(x)
        self.recalculate()

    def odaberi_start_provjere_konvertera(self, x):
        """Metoda sluzi za odabir pocetnog indeksa (ljevi klik na tablicu sa
        sitovim podacima konvertera). Vrijednost se postavlja u dokument."""
        self.dokument.set_konverterPodaciStart(x)

    def set_start_provjere_konvertera(self, x):
        """metoda postavlja pocetni indeks frejma u model (update gui)"""
        self.konverterPodaciView.clearSelection()
        self.konverterPodaciModel.set_start(x) #BUG!
        self.recalculate()

    def save_umjeravanje_to_file(self):
        """spremanje dokumenta u file"""
        filepath = QtGui.QFileDialog.getSaveFileName(parent=self,
                                                     caption='Spremi file',
                                                     filter='Umjeravanje save files (*.usf);;all (*.*)')
        if filepath:
            self.dokument.save_dokument(filepath)

    def load_umjeravanje_from_file(self):
        """ucitavanje dokumenta iz spremljenog filea"""
        filepath = QtGui.QFileDialog.getOpenFileName(parent=self,
                                                     caption='Ucitaj file',
                                                     filter='Umjeravanje save files (*.usf);;all (*.*)')
        if filepath:
            self.dokument.load_dokument(filename=filepath)

    def napravi_pdf_report(self):
        """metoda je zaduzena za generiranje pdf reporta umjeravanja.
        - podaci se preuzimaju u obliku dicta od dokumenta (mapa)
        - ime filea se dobiva uz pomoc dijaloga
        """
        ime = QtGui.QFileDialog.getSaveFileName(parent=self,
                                                caption='Spremi pdf report',
                                                filter = 'pdf file (*.pdf)')
        if ime:
            mapa = self.dokument.dokument_to_dict()
            mapa = copy.deepcopy(mapa)
            report = pdfreport.ReportGenerator()
            report.generiraj_report(ime, mapa)

    def set_slopeData(self, x):
        """Setter za slope podatke umjeravanja
        x = [slope, offset, prilagodbaA, prilagodbaB]"""
        #zaokruzi vrijednosti
        prilagodba = [str(round(x[2], 3)), str(round(x[3], 1))]
        #postavi elemente u tablicu
        self.tablicaPrilagodba.set_values(prilagodba)
        self.tablicaPrilagodba.update()

    def set_kriterijPrihvatljivosti(self, x):
        """Setter za kriterij prihvatljivosti (parametri umjeravanja).
        x je nested lista kriterija koji su izracunati.
        x = [srz, srs, rz, rmax, ec]

        svaki kriterij je lista sa elementima:
        [naziv,tocka norme,kratka oznaka,vrijednost,uvijet prihvatljivosti,ispunjeno]
        """
        parametri = copy.deepcopy(x)
        self.tablicaParametri.set_values(parametri)
        self.tablicaParametri.update()

    def set_konverterRezultat(self, x):
        """Setter za rezultat frejm provjere konvertera iz dokumenta u gui."""
        jedinica = self.dokument.get_mjernaJedinica()
        tocke = self.dokument.get_tockeKonverter()
        self.konverterRezultatView.set_mjerna_jedinica(jedinica)
        self.konverterRezultatView.set_tocke(tocke)
        self.konverterRezultatView.set_data(x)

    def set_efikasnostiKonvertera(self, x):
        """Setter za listu efikasnosti konvertera iz dokumenta u gui"""
        lista = [str(round(i, 1)) for i in x]
        self.tablicaKonverter.set_values(lista)

    def prikazi_grafove(self):
        """
        Metoda za crtanje grafova
        """
        self.crefCanvas.clear_graf()
        self.mjerenjaCanvas.clear_graf()

        #dohvati rezultat umjeravanja:
        rezultat = self.dokument.get_rezultatUmjeravanja()
        slopeData = self.dokument.get_slopeData()
        testLinearnosti = self.dokument.get_provjeraLinearnosti()
        tocke = self.dokument.get_tockeUmjeravanja()
        stupac = self.dokument.get_izabranoMjerenje()
        frejm = self.dokument.get_siroviPodaci()

        if stupac in frejm.columns:
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
            frejm = frejm.loc[:, stupac]
            if testLinearnosti:
                self.mjerenjaCanvas.crtaj(frejm, tocke)
            else:
                zs = self.dokument.get_zero_span_tocke()
                self.mjerenjaCanvas.crtaj(frejm, zs)

    def postavi_usporedna_umjeravanja(self):
        """
        inicijalno postavljanje panela za usporedno umjeravanje.

        svaki plin, koji postoji kao stupac u frejmu sirovih podataka, se racuna
        i prikazuje u zasebnom objektu panel. Ti objekti se onda slazu u horizontalni
        layout u posebnom tabu glavnog gui prozora.
        """
        #potrebne postavke
        plin = self.dokument.get_izabranoMjerenje()
        frejm = self.dokument.get_siroviPodaci()
        stupci = sorted(list(frejm.columns))

        #prije postavljanja novih panela potrebno je maknuti stare
        for i in reversed(range(self.multipleRezultatLayout.count())):
            item = self.multipleRezultatLayout.itemAt(i).widget()
            if item != None:
                self.multipleRezultatLayout.removeWidget(item)
                sip.delete(item)
                item = None

        #inicijalizacija i postavljanje panela
        self.dokument.block_all_signals()
        for gas in stupci:
            izabraniPanel = panel.RezultatPanel(dokument=self.dokument, plin=gas)
            # direktno manipuliranje dokumentom
            self.dokument.izabranoMjerenje = gas
            #racunanje potrebnih vrijednosti
            self.kalkulator.racunaj()
            rez = self.kalkulator.rezultat
            slopedata = self.kalkulator.get_slope_and_offset_list()
            kriterij = self.kalkulator.get_provjeru_parametara()
            mapa = {'rezultat':rez,
                    'slopeData':slopedata,
                    'kriterij':kriterij}
            #postavljanje panela u layout
            self.multipleRezultatLayout.addWidget(izabraniPanel)
            #update rezultata za layout
            izabraniPanel.update_rezultat(mapa)
            #spoji signale iz panela
            self.connect(izabraniPanel,
                         QtCore.SIGNAL('panel_dodaj_umjernu_tocku'),
                         self.add_red_umjeravanje)
            self.connect(izabraniPanel,
                         QtCore.SIGNAL('panel_makni_umjernu_tocku(PyQt_PyObject)'),
                         self.remove_red_umjeravanje)
            self.connect(izabraniPanel,
                         QtCore.SIGNAL('panel_makni_umjernu_tocku(PyQt_PyObject)'),
                         self.edit_red_umjeravanje)

        #restore dokument i kalkulator u pocetno stanje
        self.dokument.izabranoMjerenje = plin
        self.kalkulator.racunaj()
        self.dokument.unblock_all_signals()

    def update_multiple_prikaz_rezultata(self):
        """
        refresh vrijednosti nakon racunanja za usporedni prikaz rezultata
        """
        print('multiple_prikaz_rezultata')
        plin = self.dokument.get_izabranoMjerenje()
        self.dokument.block_all_signals()
        #panel po panel... dohvati plin tog panela, izracunaj rezultat i postavi u gui
        for i in range(self.multipleRezultatLayout.count()):
            item = self.multipleRezultatLayout.itemAt(i).widget()
            gas = item.plin
            self.dokument.izabranoMjerenje = gas
            self.kalkulator.racunaj()
            rez = self.kalkulator.rezultat
            slopedata = self.kalkulator.get_slope_and_offset_list()
            kriterij = self.kalkulator.get_provjeru_parametara()
            mapa = {'rezultat':rez,
                    'slopeData':slopedata,
                    'kriterij':kriterij}
            item.update_rezultat(mapa)
        self.dokument.izabranoMjerenje = plin
        self.kalkulator.racunaj()
        self.dokument.unblock_all_signals()


