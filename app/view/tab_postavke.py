# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 08:45:50 2015

@author: DHMZ-Milic
"""
import logging
from PyQt4 import QtGui, QtCore, uic


BASE1, FORM1 = uic.loadUiType('./app/view/uiFiles/tab_postavke.ui')
class PostavkeTab(BASE1, FORM1):
    """
    Panel za prikaz postavki umjeravanja
    """
    def __init__(self, dokument=None, parent=None):
        super(BASE1, self).__init__(parent)
        self.setupUi(self)
        self.dokument = dokument
        self.plin = 'postavke' #naziv taba
        self.set_connections()

    def is_nox_active(self):
        """Metoda provjerava da li trenutno aktivna komponenta ima 'NOx'"""
        komp = self.comboKomponenta.currentText()
        if 'NOx' in komp:
            return True
        else:
            return False

    def enable_konverter_check(self):
        """disable ili enable konverter ovisno da li je NOx komponenta"""
        if self.is_nox_active():
            self.checkKonverter.setEnabled(True)
        else:
            self.checkKonverter.setChecked(False)
            self.checkKonverter.setEnabled(False)


    def set_mjernaJedinica(self, mapa):
        """Setter mjerne jedinice u labele gui-a"""
        jedinica = mapa['value']
        self.labelJedinicaCCRM.setText(jedinica)
        self.labelJedinicaZrak.setText(jedinica)
################################################################################
    #mjerenje groupbox
    def set_listu_comboKomponenta(self, x):
        """
        Setter liste stringova u comboKomponenta
        """
        self.comboKomponenta.clear()
        lista = sorted(x['value'])
        self.comboKomponenta.addItems(lista)
        #pokusaj postaviti izabranu komponentu iz dokumenta
        try:
            izbor = self.dokument.get_izabranaKomponenta()
            ind = self.comboKomponenta.findText(izbor)
            self.comboKomponenta.setCurrentIndex(ind)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            #update dokument koja je opcija trenutno izabrana
            self.dokument.set_izabranaKomponenta(self.comboKomponenta.currentText())
        #test za enable i disable konvertera ovisno o NOX
        self.enable_konverter_check()

    def set_izabranu_komponentu(self, x):
        """setter izabrane komponente u comboboxu comboKomponenta"""
        value = x['value']
        ind = self.comboKomponenta.findText(value)
        self.comboKomponenta.setCurrentIndex(ind)
        #test za enable i disable konvertera ovisno o NOX
        self.enable_konverter_check()

    def promjena_izbora_komponente(self, x):
        """metoda reagira na promjenu trenunog izbora u comboboxu comboKomponenta"""
        value = self.comboKomponenta.currentText()
        if value != '':
            self.dokument.set_izabranaKomponenta(value)
            #test za enable i disable konvertera ovisno o NOX
            self.enable_konverter_check()

    def set_listu_comboUredjaji(self, x):
        """Setter liste stringova u comboUredjaji"""
        self.comboUredjaj.clear()
        lista = sorted(x['value'])
        self.comboUredjaj.addItems(lista)
        #pokusaj postaviti izabrani uredjaj iz dokumenta
        try:
            izbor = self.dokument.get_izabraniUredjaj()
            ind = self.comboUredjaj.findText(izbor)
            self.comboUredjaj.setCurrentIndex(ind)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            #update dokument koji uredjaj je izabran
            self.dokument.set_izabraniUredjaj(self.comboUredjaj.currentText())

    def set_izabrani_uredjaj(self, x):
        """setter izabranog uredjaja u comboboxu"""
        value = x['value']
        ind = self.comboUredjaj.findText(value)
        self.comboUredjaj.setCurrentIndex(ind)

    def promjena_izbora_uredjaja(self, x):
        """metoda reagira na promjenu trenunog izbora u comboboxu comboUredjaji"""
        value = self.comboUredjaj.currentText()
        self.dokument.set_izabraniUredjaj(value)

    def set_listu_comboPostaja(self, x):
        """
        Setter liste postaja u comboPostaje
        """
        self.comboPostaja.clear()
        lista = sorted(x['value'])
        self.comboPostaja.addItems(lista)
        #pokusaj postaviti izabranu postaju iz dokumenta
        try:
            izbor = self.dokument.get_izabranaPostaja()
            ind = self.comboPostaja.findText(izbor)
            self.comboUredjaj.setCurrentIndex(ind)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            #update dokument koja je postaja izabrana
            self.dokument.set_izabranaPostaja(self.comboPostaja.currentText())

    def set_izabranu_postaju(self, x):
        """setter izabrane postaje u comboboxu"""
        value = x['value']
        ind = self.comboPostaja.findText(value)
        self.comboPostaja.setCurrentIndex(ind)

    def promjena_izbora_postaje(self, x):
        """metoda reagira na promjenu trenunog izbora u comboboxu comboPostaja"""
        value = self.comboPostaja.currentText()
        self.dokument.set_izabranaPostaja(value)

    def set_opseg(self, x):
        """setter opsega mjerenja"""
        value = x['value']
        self.doubleSpinBoxOpseg.setValue(value)

    def get_opseg(self):
        """getter opsega mjerenja"""
        return self.doubleSpingBoxOpseg.value()

    def promjena_opseg(self, x):
        """ signal koji updatea dokument sa promjenom opsega"""
        value = self.doubleSpinBoxOpseg.value()
        self.dokument.set_opseg(value)
################################################################################
    #dilucijska jedinica groupbox
    def set_listu_comboDilucija(self, x):
        """setter liste dilucijskih jedinica u combobox"""
        self.comboDilucija.clear()
        lista = sorted(x['value'])
        self.comboDilucija.addItems(lista)
        #pokusaj postaviti izabranu diluciju iz dokumenta
        try:
            izbor = self.dokument.get_izabranaDilucija()
            ind = self.comboDilucija.findText(izbor)
            self.comboDilucija.setCurrentIndex(ind)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            #update dokument sa trenutnim izborom dilucijske jedinice
            self.dokument.set_izabranaDilucija(self.comboDilucija.currentText())

    def set_izabranu_diluciju(self, x):
        """setter izabrane dilucijske jedinice u combou"""
        value = x['value']
        ind = self.comboDilucija.findText(value)
        self.comboDilucija.setCurrentIndex(ind)

    def promjena_izbora_dilucije(self, x):
        """metoda reagira na promjenu trenunog izbora u comboboxu comboDilucija"""
        value = self.comboDilucija.currentText()
        self.dokument.set_izabranaDilucija(value)

    def promjena_dilucijaProizvodjacLineEdit(self, x):
        """slot koji javlja dokumentu promjenu proizvodjaca dilucijske jedinice"""
        value = self.dilucijaProizvodjacLineEdit.text()
        self.dokument.set_proizvodjacDilucija(value)

    def set_dilucijaProizvodjacLineEdit(self, x):
        """Metoda postavlja proizvodjaca dilucijske jedinice preuzetu iz dokumenta
        u gui widget"""
        value = x['value']
        self.dilucijaProizvodjacLineEdit.setText(value)

    def promjena_dilucijaSljedivostLineEdit(self, x):
        """slot koji javlja dokumentu promjenu sljedivosti dilucijske jedinice"""
        value = self.dilucijaSljedivostLineEdit.text()
        self.dokument.set_sljedivostDilucija(value)

    def set_dilucijaSljedivostLineEdit(self, x):
        """Metoda postavlja sljedivost dilucijske jedinice preuzetu iz dokumenta
        u gui widget"""
        value = x['value']
        self.dilucijaSljedivostLineEdit.setText(value)
################################################################################
    #generator cistog zraka groupbox
    def set_listu_comboZrak(self, x):
        """setter liste generatora cistog zraka u combobox"""
        self.comboZrak.clear()
        lista = sorted(x['value'])
        self.comboZrak.addItems(lista)
        #pokusaj postaviti izabrani zrak iz dokumenta
        try:
            izbor = self.dokument.get_izabraniZrak()
            ind = self.comboZrak.findText(izbor)
            self.comboZrak.setCurrentIndex(ind)
        except Exception as err:
            logging(str(err), exc_info=True)
            #update dokument sa trenutnim izborom generatora cistog zraka
            self.dokument.set_izabraniZrak(self.comboZrak.currentText())

    def set_izabrani_zrak(self, x):
        """setter izabranog generatora cistog zraka u combou"""
        value = x['value']
        ind = self.comboZrak.findText(value)
        self.comboZrak.setCurrentIndex(ind)

    def promjena_izbora_zraka(self, x):
        """metoda reagira na promjenu trenunog izbora u comboboxu comboZrak"""
        value = self.comboZrak.currentText()
        self.dokument.set_izabraniZrak(value)

    def promjena_zrakProizvodjacLineEdit(self, x):
        """slot koji postavlja proizvodjaca generatora cistog zraka u dokument"""
        value = self.zrakProizvodjacLineEdit.text()
        self.dokument.set_proizvodjacZrak(value)

    def set_zrakProizvodjacLineEdit(self, x):
        """Metoda postavlja proizvodjaca generatora cistog zraka iz dokumenta
        u gui widget"""
        value = x['value']
        self.zrakProizvodjacLineEdit.setText(value)

    def promjena_doubleSpinBoxSljedivostCistiZrak(self, x):
        """slot koji postavlja sljedivost generatora cistog zraka u dokument"""
        value = self.doubleSpinBoxSljedivostCistiZrak.value()
        self.dokument.set_sljedivostZrak(value)

    def set_doubleSpinBoxSljedivostCistiZrak(self, x):
        """Metoda postavlja sljedivost generatora cistog zraka iz dokumenta u gui
        widget"""
        value = x['value']
        self.doubleSpinBoxSljedivostCistiZrak.setValue(value)
################################################################################
    #testovi groupbox
    def toggle_konverter(self, x):
        """
        toggle checka za provjeru konvertera
        """
        self.dokument.set_provjeraKonvertera(x)

    def set_checkKonverter(self, x):
        """setter za checkbox konvertera"""
        x = bool(x)
        self.checkKonverter.setChecked(x)

    def toggle_odaziv(self, x):
        """
        toggle checka za provjeru odaziva
        """
        self.dokument.set_provjeraOdaziv(x)

    def set_checkOdaziv(self, x):
        """setter za checkbox odaziva"""
        x = bool(x)
        self.checkOdaziv.setChecked(x)

    def toggle_umjeravanje(self, x):
        """
        toggle checka za kontrolu umjeravanja
        """
        self.dokument.set_provjeraUmjeravanje(x)

    def set_checkUmjeravanje(self, x):
        """setter za checkbox umjeravanja"""
        x = bool(x)
        self.checkUmjeravanje.setChecked(x)

    def toggle_ponovljivost(self, x):
        """
        toggle checka za provjeru ponovljivosti
        """
        self.dokument.set_provjeraPonovljivost(x)

    def set_checkPonovljivost(self, x):
        """setter za checkbox ponovljivosti"""
        x = bool(x)
        self.checkPonovljivost.setChecked(x)

    def toggle_linearnost(self, x):
        """
        toggle checka za provjeru linearnosti
        """
        self.dokument.set_provjeraLinearnost(x)

    def set_checkLinearnost(self, x):
        """setter za checkbox linearnosti"""
        x = bool(x)
        self.checkLinearnost.setChecked(x)
################################################################################
    #crm groupbox
    def set_izvorPlainTextEdit(self, x):
        """Metoda postavlja izvorCRM u gui widget"""
        self.izvorPlainTextEdit.setPlainText(x)
        self.izvorPlainTextEdit.moveCursor(QtGui.QTextCursor.End)

    def promjena_izvorPlainTextEdit(self):
        """slot koji dokumentu javlja promjenu izvora CRM-a"""
        value = self.izvorPlainTextEdit.toPlainText()
        self.dokument.set_izvorCRM(value)

    def promjena_doubleSpinBoxKoncentracijaCRM(self, x):
        """slot koji dokumentu javlja promjenu koncentracije CRM-a"""
        value = self.doubleSpinBoxKoncentracijaCRM.value()
        self.dokument.set_koncentracijaCRM(value)

    def set_doubleSpinBoxKoncentracijaCRM(self, x):
        """Metoda postavlja koncentraciju CRM-a u gui widget"""
        value = x['value']
        self.doubleSpinBoxKoncentracijaCRM.setValue(value)

    def promjena_doubleSpinBoxSljedivostCRM(self, x):
        """slot koji dokumentu javlja promjenu sljedivosti CRM-a"""
        value = self.doubleSpinBoxSljedivostCRM.value()
        self.dokument.set_sljedivostCRM(value)

    def set_doubleSpinBoxSljedivostCRM(self, x):
        """Metoda postavlja sljedivost CRM u gui widget"""
        value = x['value']
        self.doubleSpinBoxSljedivostCRM.setValue(value)
################################################################################
    #postavke izvjesca groupbox
    def promjena_normaPlainTextEdit(self):
        """slot koji postavlja tekst norme u dokument"""
        value = self.normaPlainTextEdit.toPlainText()
        self.dokument.set_norma(value)

    def set_normaPlainTextEdit(self, x):
        """Metoda koja postavlja tekst norme iz dokumenta u gui widget"""
        value = x['value']
        self.normaPlainTextEdit.setPlainText(value)
        self.normaPlainTextEdit.moveCursor(QtGui.QTextCursor.End)

    def promjena_oznakaIzvjescaLineEdit(self, x):
        """slot koji postavlja oznaku izvjesca u dokument"""
        value = self.oznakaIzvjescaLineEdit.text()
        self.dokument.set_oznakaIzvjesca(value)

    def set_oznakaIzvjescaLineEdit(self, x):
        """Metoda koja postavlja oznaku izvjesca iz dokumenta u gui widget"""
        value = x['value']
        self.oznakaIzvjescaLineEdit.setText(value)

    def promjena_brojObrascaLineEdit(self, x):
        """slot koji postavlja broj obrasca u dokument"""
        value = self.brojObrascaLineEdit.text()
        self.dokument.set_brojObrasca(value)

    def set_brojObrascaLineEdit(self, x):
        """Metoda koja postavlja broj obrasca iz dokumenta u gui widget"""
        value = x['value']
        self.brojObrascaLineEdit.setText(value)

    def promjena_revizijaLineEdit(self, x):
        """slot koji postavlja broj revizije u dokument"""
        value = self.revizijaLineEdit.text()
        self.dokument.set_revizija(value)

    def set_revizijaLineEdit(self, x):
        """Metoda koja postavlja broj revizije iz dokumenta u gui widget"""
        value = x['value']
        self.revizijaLineEdit.setText(value)

    def promjena_datumUmjeravanjaLineEdit(self, x):
        """slot koji postavlja datum umjeravanja u dokument"""
        value = self.datumUmjeravanjaLineEdit.text()
        self.dokument.set_datumUmjeravanja(value)

    def set_datumUmjeravanjaLineEdit(self, x):
        """metoda postavlja datum umjeravanja iz dokumenta u gui widget"""
        value = x['value']
        self.datumUmjeravanjaLineEdit.setText(value)
################################################################################
    #okolisni uvijeti tjekom provjere groupbox
    def promjena_temperaturaDoubleSpinBox(self, x):
        """slot koji postavlja temperaturu (okolisni uvijeti) u dokument"""
        value = self.temperaturaDoubleSpinBox.value()
        self.dokument.set_temperatura(value)

    def set_temperaturaDoubleSpinBox(self, x):
        """metoda postavlja temperaturu (okolisni uvijeti) iz dokumenta u gui
        widget"""
        value = x['value']
        self.temperaturaDoubleSpinBox.setValue(value)

    def promjena_vlagaDoubleSpinBox(self, x):
        """slot koji postavlja relativnu vlagu (okolisni uvijeti) u dokumnet"""
        value = self.vlagaDoubleSpinBox.value()
        self.dokument.set_vlaga(value)

    def set_vlagaDoubleSpinBox(self, x):
        """Metoda postavlja relativnu vlagu (okolisni uvijeti) iz dokumenta u
        gui widget"""
        value = x['value']
        self.vlagaDoubleSpinBox.setValue(value)

    def promjena_tlakDoubleSpinBox(self, x):
        """slot koji postavlja tlak (okolisni uvijeti) u dokument"""
        value = self.tlakDoubleSpinBox.value()
        self.dokument.set_tlak(value)

    def set_tlakDoubleSpinBox(self, x):
        """metoda postavlja tlak (okolisni uvijeti) iz dokumenta u gui widget"""
        value = x['value']
        self.tlakDoubleSpinBox.setValue(value)
################################################################################
    #napomena groupbox
    def promjena_napomenaPlainTextEdit(self):
        """slot koji postavlja tekst napomena u dokument"""
        value = self.napomenaPlainTextEdit.toPlainText()
        self.dokument.set_napomena(value)

    def set_napomenaPlainTextEdit(self, x):
        """metoda postavlja tekst napomene iz dokumenta u gui widget"""
        value = x['value']
        self.napomenaPlainTextEdit.setPlainText(value)
        self.napomenaPlainTextEdit.moveCursor(QtGui.QTextCursor.End)
################################################################################
    def set_connections(self):
        """povezivanje kontrolnih elemenata"""
        self.comboKomponenta.currentIndexChanged.connect(self.promjena_izbora_komponente)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_komponente(PyQt_PyObject)'),
                     self.set_listu_comboKomponenta)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_izabranaKomponenta(PyQt_PyObject)'),
                     self.set_izabranu_komponentu)
        self.comboUredjaj.currentIndexChanged.connect(self.promjena_izbora_uredjaja)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_uredjaja(PyQt_PyObject)'),
                     self.set_listu_comboUredjaji)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_izabraniUredjaj(PyQt_PyObject)'),
                     self.set_izabrani_uredjaj)
        self.comboPostaja.currentIndexChanged.connect(self.promjena_izbora_postaje)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_listaPostaja(PyQt_PyObject)'),
                     self.set_listu_comboPostaja)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_izabranaPostaja(PyQt_PyObject)'),
                     self.set_izabranu_postaju)
        self.comboDilucija.currentIndexChanged.connect(self.promjena_izbora_dilucije)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_listaDilucija(PyQt_PyObject)'),
                     self.set_listu_comboDilucija)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_izabranaDilucija(PyQt_PyObject)'),
                     self.set_izabranu_diluciju)
        self.comboZrak.currentIndexChanged.connect(self.promjena_izbora_zraka)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_listaZrak(PyQt_PyObject)'),
                     self.set_listu_comboZrak)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_izabraniZrak(PyQt_PyObject)'),
                     self.set_izabrani_zrak)
        self.checkKonverter.toggled.connect(self.toggle_konverter)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_provjeraKonvertera(PyQt_PyObject)'),
                     self.set_checkKonverter)
        self.checkOdaziv.toggled.connect(self.toggle_odaziv)
        self.connect(self.dokument,
                     QtCore.SIGNAL('display_odaziv(PyQt_PyObject)'),
                     self.set_checkOdaziv)
        self.checkUmjeravanje.toggled.connect(self.toggle_umjeravanje)
        self.connect(self.dokument,
                     QtCore.SIGNAL('display_umjeravanje(PyQt_PyObject)'),
                     self.set_checkUmjeravanje)
        self.checkPonovljivost.toggled.connect(self.toggle_ponovljivost)
        self.connect(self.dokument,
                     QtCore.SIGNAL('display_ponovljivost(PyQt_PyObject)'),
                     self.set_checkPonovljivost)
        self.checkLinearnost.toggled.connect(self.toggle_linearnost)
        self.connect(self.dokument,
                     QtCore.SIGNAL('display_linearnost(PyQt_PyObject)'),
                     self.set_checkLinearnost)
        self.izvorPlainTextEdit.textChanged.connect(self.promjena_izvorPlainTextEdit)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_izvorCRM(PyQt_PyObject)'),
                     self.set_izvorPlainTextEdit)
        self.doubleSpinBoxKoncentracijaCRM.valueChanged.connect(self.promjena_doubleSpinBoxKoncentracijaCRM)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_koncentracijaCRM(PyQt_PyObject)'),
                     self.set_doubleSpinBoxKoncentracijaCRM)
        self.doubleSpinBoxSljedivostCRM.valueChanged.connect(self.promjena_doubleSpinBoxSljedivostCRM)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_sljedivostCRM(PyQt_PyObject)'),
                     self.set_doubleSpinBoxSljedivostCRM)
        self.dilucijaProizvodjacLineEdit.textChanged.connect(self.promjena_dilucijaProizvodjacLineEdit)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_proizvodjacDilucija(PyQt_PyObject)'),
                     self.set_dilucijaProizvodjacLineEdit)
        self.dilucijaSljedivostLineEdit.textChanged.connect(self.promjena_dilucijaSljedivostLineEdit)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_sljedivostDilucija(PyQt_PyObject)'),
                     self.set_dilucijaSljedivostLineEdit)
        self.zrakProizvodjacLineEdit.textChanged.connect(self.promjena_zrakProizvodjacLineEdit)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_proizvodjacZrak(PyQt_PyObject)'),
                     self.set_zrakProizvodjacLineEdit)
        self.doubleSpinBoxSljedivostCistiZrak.valueChanged.connect(self.promjena_doubleSpinBoxSljedivostCistiZrak)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_sljedivostZrak(PyQt_PyObject)'),
                     self.set_doubleSpinBoxSljedivostCistiZrak)
        self.normaPlainTextEdit.textChanged.connect(self.promjena_normaPlainTextEdit)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_norma(PyQt_PyObject)'),
                     self.set_normaPlainTextEdit)
        self.oznakaIzvjescaLineEdit.textChanged.connect(self.promjena_oznakaIzvjescaLineEdit)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_oznakaIzvjesca(PyQt_PyObject)'),
                     self.set_oznakaIzvjescaLineEdit)
        self.brojObrascaLineEdit.textChanged.connect(self.promjena_brojObrascaLineEdit)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_brojObrasca(PyQt_PyObject)'),
                     self.set_brojObrascaLineEdit)
        self.revizijaLineEdit.textChanged.connect(self.promjena_revizijaLineEdit)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_revizija(PyQt_PyObject)'),
                     self.set_revizijaLineEdit)
        self.datumUmjeravanjaLineEdit.textChanged.connect(self.promjena_datumUmjeravanjaLineEdit)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_datumUmjeravanja(PyQt_PyObject)'),
                     self.set_datumUmjeravanjaLineEdit)
        self.temperaturaDoubleSpinBox.valueChanged.connect(self.promjena_temperaturaDoubleSpinBox)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_temperatura(PyQt_PyObject)'),
                     self.set_temperaturaDoubleSpinBox)
        self.vlagaDoubleSpinBox.valueChanged.connect(self.promjena_vlagaDoubleSpinBox)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_vlaga(PyQt_PyObject)'),
                     self.set_vlagaDoubleSpinBox)
        self.tlakDoubleSpinBox.valueChanged.connect(self.promjena_tlakDoubleSpinBox)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_tlak(PyQt_PyObject)'),
                     self.set_tlakDoubleSpinBox)
        #promjena teksta napomene
        self.napomenaPlainTextEdit.textChanged.connect(self.promjena_napomenaPlainTextEdit)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_napomena(PyQt_PyObject)'),
                     self.set_napomenaPlainTextEdit)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_mjernaJedinica(PyQt_PyObject)'),
                     self.set_mjernaJedinica)
        self.doubleSpinBoxOpseg.valueChanged.connect(self.promjena_opseg)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_opseg(PyQt_PyObject)'),
                     self.set_opseg)
