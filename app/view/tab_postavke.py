# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 13:04:52 2016

@author: DHMZ-Milic
"""
import logging
from PyQt4 import QtCore, uic
from app.model.qt_models import ProzorTableModelKomponente

BASE_TAB_POSTAVKE, FORM_TAB_POSTAVKE = uic.loadUiType('./app/view/uiFiles/tab_postavke.ui')
class TabPostavke(BASE_TAB_POSTAVKE, FORM_TAB_POSTAVKE):
    """
    Gui widget, tab posavki umjeravanja (uredjaj, postavke...)
    """
    def __init__(self, datastore=None, parent=None):
        super(BASE_TAB_POSTAVKE, self).__init__(parent)
        self.setupUi(self)
        #izvor podataka
        self.datastore = datastore
        self.plin = 'Postavke' # naziv taba

        self.setup_connections()
        self.popuni_postavke()

    def popuni_postavke(self):
        """popunjavanje widgeta sa podacima iz dokumenta"""
        ###UREDJAJ###
        #komponente
        komponente = self.datastore.get_uredjaj().get_komponente()
        self.modelKomponenti = ProzorTableModelKomponente(komponente=komponente)
        self.tableViewUredjajKomponente.setModel(self.modelKomponenti)
        #osnovni podaci o uredjaju
        self.labelUredjajSerijskiBroj.setText(self.datastore.get_uredjaj().get_serial())
        self.labelUredjajOznakaModela.setText(self.datastore.get_uredjaj().get_oznakaModela())
        self.labelUredjajProizvodjac.setText(self.datastore.get_uredjaj().get_proizvodjac())
        postaje = self.datastore.get_postaje()
        izabranaPostaja = self.datastore.get_izabranaPostaja()
        if izabranaPostaja not in postaje:
            postaje.append(izabranaPostaja)
        self.comboBoxLokacija.addItems(postaje)
        self.comboBoxLokacija.setCurrentIndex(self.comboBoxLokacija.findText(izabranaPostaja))
        #analiticka metoda
        metoda = self.datastore.get_uredjaj().get_analitickaMetoda()
        self.labelMetodaID.setText(metoda.get_ID())
        self.labelMetodaJedinica.setText(metoda.get_jedinica())
        self.label_jedinica_1.setText(metoda.get_jedinica())
        self.label_jedinica_2.setText(metoda.get_jedinica())
        self.label_jedinica_3.setText(metoda.get_jedinica())
        self.label_jedinica_4.setText(metoda.get_jedinica())
        self.label_jedinica_5.setText(metoda.get_jedinica())
        self.label_jedinica_6.setText(metoda.get_jedinica()) #jedinica za trenutno koristeni opseg
        self.labelCRMJedinica.setText(metoda.get_jedinica()) #jedinica za CRM koncentraciju
        self.labelMetodaNaziv.setText(metoda.get_naziv())
        self.labelMetodaNorma.setText(metoda.get_norma())
        self.labelMetodaSrs.setText(str(metoda.get_Srs()))
        self.labelMetodaSrs.setText(str(metoda.get_Srs()))
        self.labelMetodaSrz.setText(str(metoda.get_Srz()))
        self.labelMetodaOpseg.setText(str(metoda.get_o()))
        try:
            tmp = float(metoda.get_o())
            self.datastore.set_izabraniOpseg(tmp)
            self.doubleSpinBoxOpseg.setValue(tmp)
        except Exception as err:
            logging.warning(str(err))
            self.datastore.set_izabraniOpseg(1.0)
            self.doubleSpinBoxOpseg.setValue(1.0)
        self.labelMetodaRmax.setText(str(metoda.get_rmax()))
        self.labelMetodaRz.setText(str(metoda.get_rz()))
        self.labelMetodaTr.setText(str(metoda.get_tr()))
        self.labelMetodaTf.setText(str(metoda.get_tf()))
        self.labelMetodaEcmin.setText(str(metoda.get_Ec_min()))
        self.labelMetodaEcmax.setText(str(metoda.get_Ec_max()))
        ###KALIBRACIJSKA JEDINICA###
        dilucije = self.datastore.get_listu_dilucija()
        self.comboBoxDilucija.addItems(dilucije)
        kljuc = self.datastore.get_izabranaDilucija()
        if kljuc == 'n/a':
            kljuc = self.comboBoxDilucija.currentText()
        self.datastore.set_izabranaDilucija(kljuc)
        self.update_info_dilucija()
        ###GENERATOR CISTOG ZRAKA###
        generatori = self.datastore.get_listu_generatora()
        self.comboBoxGenerator.addItems(generatori)
        kljuc = self.datastore.get_izabraniGenerator()
        if kljuc == 'n/a':
            kljuc = self.comboBoxGenerator.currentText()
        self.datastore.set_izabraniGenerator(kljuc)
        self.update_info_generator()
        ###CRM###
        self.lineEditVrstaCRM.setText(self.datastore.get_izabranaVrstaCRM())
        self.lineEditCRMSljedivost.setText(self.datastore.get_sljedivostCRM())
        self.doubleSpinBoxCRMKoncentracija.setValue(self.datastore.get_koncentracijaCRM())
        self.doubleSpinBoxCRMU.setValue(self.datastore.get_UCRM())
        ###POSTAVKE IZVJESCA###
        self.lineEditOznakaIzvjesca.setText(self.datastore.get_izabranaOznakaIzvjesca())
        self.lineEditRevizija.setText(self.datastore.get_izabranaRevizijaIzvjesca())
        self.lineEditBrojObrasca.setText(self.datastore.get_izabraniBrojObrasca())
        self.lineEditNorma.setText(self.datastore.get_izabranaNormaObrasca())
        self.plainTextEditPuniNazivMetode.setPlainText(self.datastore.get_izabraniOpisMetode())
        self.plainTextEditNapomena.setPlainText(self.datastore.get_izabranaNapomena())
        self.lineEditDatumUmjeravanja.setText(self.datastore.get_izabraniDatum())
        self.doubleSpinBoxTemperatura.setValue(self.datastore.get_izabranaTemperatura())
        self.doubleSpinBoxVlaga.setValue(self.datastore.get_izabranaVlaga())
        self.doubleSpinBoxTlak.setValue(self.datastore.get_izabraniTlak())
        ###TESTOVI###
        self.checkBoxUmjeravanje.setChecked(self.datastore.get_checkUmjeravanje())
        self.checkBoxPonovljivost.setChecked(self.datastore.get_checkPonovljivost())
        self.checkBoxLinearnost.setChecked(self.datastore.get_checkLinearnost())
        self.checkBoxOdaziv.setChecked(self.datastore.get_checkOdaziv())
        if self.datastore.isNOx:
            self.checkBoxKonverter.setChecked(self.datastore.get_checkKonverter())
        else:
            self.checkBoxKonverter.setVisible(False)
            #hide cnox50
            self.label_60.setVisible(False)
            self.doubleSpinBoxCNOx50.setVisible(False)
            self.label_jedinica_5.setVisible(False)
            #hide cnox95
            self.label_61.setVisible(False)
            self.doubleSpinBoxCNOx95.setVisible(False)
            self.label_jedinica_6.setVisible(False)

        self.doubleSpinBoxCNOx50.setValue(self.datastore.get_cNOx50())
        self.doubleSpinBoxCNOx95.setValue(self.datastore.get_cNOx95())

    def setup_connections(self):
        """spajanje signala i slotova"""
        self.lineEditCRMSljedivost.textChanged.connect(self.datastore.set_sljedivostCRM)
        self.comboBoxLokacija.currentIndexChanged.connect(self.change_lokaciju)
        self.comboBoxLokacija.editTextChanged.connect(self.change_lokaciju)
        self.lineEditVrstaCRM.textChanged.connect(self.datastore.set_izabranaVrstaCRM)
        self.comboBoxDilucija.currentIndexChanged.connect(self.change_diluciju)
        self.comboBoxGenerator.currentIndexChanged.connect(self.change_generator)
        self.doubleSpinBoxCRMKoncentracija.valueChanged.connect(self.change_koncentracijaCRM)
        self.doubleSpinBoxCRMU.valueChanged.connect(self.change_UCRM)
        self.lineEditOznakaIzvjesca.textChanged.connect(self.datastore.set_izabranaOznakaIzvjesca)
        self.lineEditRevizija.textChanged.connect(self.datastore.set_izabranaRevizijaIzvjesca)
        self.lineEditBrojObrasca.textChanged.connect(self.datastore.set_izabraniBrojObrasca)
        self.lineEditNorma.textChanged.connect(self.datastore.set_izabranaNormaObrasca)
        self.plainTextEditPuniNazivMetode.textChanged.connect(self.change_OpisMetode)
        self.doubleSpinBoxOpseg.valueChanged.connect(self.change_izabraniOpseg)
        self.plainTextEditNapomena.textChanged.connect(self.change_napomenu)
        self.lineEditDatumUmjeravanja.textChanged.connect(self.datastore.set_izabraniDatum)
        self.checkBoxUmjeravanje.clicked.connect(self.change_checkUmjeravanje)
        self.checkBoxPonovljivost.clicked.connect(self.change_checkPonovljivost)
        self.checkBoxLinearnost.clicked.connect(self.change_checkLinearnost)
        self.checkBoxOdaziv.clicked.connect(self.change_checkOdaziv)
        self.doubleSpinBoxCNOx50.valueChanged.connect(self.change_cNOx50)
        self.doubleSpinBoxCNOx95.valueChanged.connect(self.change_cNOx95)
        self.doubleSpinBoxTemperatura.valueChanged.connect(self.datastore.set_izabranaTemperatura)
        self.doubleSpinBoxVlaga.valueChanged.connect(self.datastore.set_izabranaVlaga)
        self.doubleSpinBoxTlak.valueChanged.connect(self.datastore.set_izabraniTlak)
        if self.datastore.isNOx:
            self.checkBoxKonverter.clicked.connect(self.change_checkKonverter)

    def change_checkKonverter(self, x):
        """callback za promjenu checkboxa konvertera"""
        self.datastore.set_checkKonverter(x)
        self.emit(QtCore.SIGNAL('promjena_checkKonverter'))

    def change_checkOdaziv(self, x):
        """callback za promjenu checkobxa odaziv"""
        self.datastore.set_checkOdaziv(x)
        self.emit(QtCore.SIGNAL('promjena_checkOdaziv'))

    def change_checkLinearnost(self, x):
        """callback za promjenu checkboxa za linearnost"""
        self.datastore.set_checkLinearnost(x)
        self.emit(QtCore.SIGNAL('recalculate_umjeravanja'))

    def change_checkPonovljivost(self, x):
        """callback za promjenu chekboxa za ponovljivost"""
        self.datastore.set_checkPonovljivost(x)
        self.emit(QtCore.SIGNAL('recalculate_umjeravanja'))

    def change_checkUmjeravanje(self, x):
        """callback za promjenu checkboxa za umjeravanje"""
        self.datastore.set_checkUmjeravanje(x)
        self.emit(QtCore.SIGNAL('recalculate_umjeravanja'))

    def change_izabraniOpseg(self, x):
        """callback za promjenu opsega za racunanje"""
        self.datastore.set_izabraniOpseg(x)
        self.emit(QtCore.SIGNAL('recalculate_all_tabs'))

    def change_UCRM(self, x):
        """callback za promjenu U crm-a"""
        self.datastore.set_UCRM(x)
        self.emit(QtCore.SIGNAL('recalculate_umjeravanja'))

    def change_koncentracijaCRM(self, x):
        """callback za promjenu koncentracije crm-a"""
        self.datastore.set_koncentracijaCRM(x)
        self.emit(QtCore.SIGNAL('recalculate_umjeravanja'))

    def change_cNOx50(self, x):
        """callback za promjenu parametra cNOx50"""
        self.datastore.set_cNOx50(x)
        self.emit(QtCore.SIGNAL('recalculate_konverter'))

    def change_cNOx95(self, x):
        """callback za promjenu parametra cNOx95"""
        self.datastore.set_cNOx95(x)
        self.emit(QtCore.SIGNAL('recalculate_konverter'))

    def change_napomenu(self):
        """callback za promjenu napomene za report"""
        x = self.plainTextEditNapomena.toPlainText()
        self.datastore.set_izabranaNapomena(x)

    def change_OpisMetode(self):
        """callback za promjenu punog opisa metode za report"""
        x = self.plainTextEditPuniNazivMetode.toPlainText()
        self.datastore.set_izabraniOpisMetode(x)

    def change_lokaciju(self, ind):
        """callback za promjenu indeksa comboboxa lokacije"""
        kljuc = self.comboBoxLokacija.currentText()
        self.datastore.set_izabranaPostaja(kljuc)
        self.emit(QtCore.SIGNAL('promjena_postaje(PyQt_PyObject)'), kljuc)

    def update_info_generator(self):
        """metoda zaduzena za update widgeta ovisno o izabranom generatoru cistog zraka"""
        kljuc = self.datastore.get_izabraniGenerator()
        generator = self.datastore.get_objekt_izabranog_generatora(kljuc)
        self.labelGeneratorModel.setText(generator.get_model())
        self.labelGeneratorProizvodjac.setText(generator.get_proizvodjac())
        self.labelGeneratorMaxSO2.setText(str(generator.get_maxSO2()))
        self.labelGeneratorMaxCO.setText(str(generator.get_maxCO()))
        self.labelGeneratorMaxBTX.setText(str(generator.get_maxBTX()))
        self.labelGeneratorMaxNOx.setText(str(generator.get_maxNOx()))
        self.labelGeneratorMaxO3.setText(str(generator.get_maxO3()))

    def change_generator(self, ind):
        """callback za promjenu indeksa u comboboxu generatora"""
        izbor = self.comboBoxGenerator.currentText()
        self.datastore.set_izabraniGenerator(izbor)
        self.update_info_generator()
        self.emit(QtCore.SIGNAL('recalculate_umjeravanja'))

    def update_info_dilucija(self):
        """metoda zaduzena za update widgeta ovisno o izabranoj diluciji"""
        kljuc = self.datastore.get_izabranaDilucija()
        dilucija = self.datastore.get_objekt_izabrane_dilucije(kljuc)
        self.labelDilucijaModel.setText(dilucija.get_model())
        self.labelDilucijaProizvodjac.setText(dilucija.get_proizvodjac())
        self.labelDilucijaSljedivost.setText(str(dilucija.get_sljedivost()))
        self.labelDilucijaNulPlin.setText(str(dilucija.get_uNul()))
        self.labelDilucijaKalPlin.setText(str(dilucija.get_uKal()))
        self.labelDilucijaOzon.setText(str(dilucija.get_uO3()))

    def change_diluciju(self, ind):
        """callback za promjenu indeksa u comboboxu kalibracijskih jedinica"""
        izbor = self.comboBoxDilucija.currentText()
        self.datastore.set_izabranaDilucija(izbor)
        self.update_info_dilucija()
        self.emit(QtCore.SIGNAL('recalculate_umjeravanja'))

