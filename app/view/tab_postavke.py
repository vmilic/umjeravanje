# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 08:45:50 2015

@author: DHMZ-Milic
"""

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
        self.plin = 'postavke' #problem kod prebacivanja tabova

        self.set_connections()

    def postavke_request_recalculate(self):
        """emit zahtjeva za ponovnim racunajnem"""
        self.emit(QtCore.SIGNAL('postavke_request_recalculate'))

    def set_connections(self):
        """povezivanje kontrolnih elemenata"""
        # checkbox za testove
        self.checkBoxRiseFall.toggled.connect(self.toggle_tab_odaziv)
        self.checkBoxKonverterTab.toggled.connect(self.toggle_tab_konverter)
        self.checkUmjeravanje.toggled.connect(self.toggle_umjeravanja)
        self.checkPonovljivost.toggled.connect(self.toggle_ponovljivost)
        self.checkLinearnost.toggled.connect(self.toggle_linearnost)

        self.comboMjerenje.currentIndexChanged.connect(self.promjena_comboMjerenje)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_izabranoMjerenje(PyQt_PyObject)'),
                     self.set_comboMjerenje)

        #promjena opsega
        self.doubleSpinBoxOpseg.valueChanged.connect(self.promjena_doubleSpinBoxOpseg)
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_opseg(PyQt_PyObject)'),
                     self.set_doubleSpinBoxOpseg)

        #promjena mjerne jedinice
        self.connect(self.dokument,
                     QtCore.SIGNAL('promjena_mjernaJedinica(PyQt_PyObject)'),
                     self.set_mjernaJedinica)

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

    def promjena_comboMjerenje(self, x):
        """slot koji dokumentu javlja promjenu izabranog mjerenja"""
        value = self.comboMjerenje.currentText()
        self.dokument.set_izabranoMjerenje(value)

    def set_comboMjerenje(self, x):
        """Metoda postavlja izabrano mjerenje preuzeto iz dokumenta u gui
        widgete, x je mapa sa kljucevima 'value' i 'recalculate'"""
        value = x['value']
        ind = self.comboMjerenje.findText(value)
        self.comboMjerenje.setCurrentIndex(ind)

    def toggle_tab_odaziv(self, x):
        """
        Emitiranje zahtjeva za prikazom ili skrivanjem taba za provjeru odaziva
        (rise i fall)
        """
        self.emit(QtCore.SIGNAL('toggle_tab_odaziv(PyQt_PyObject)'),
                  x)

    def toggle_tab_konverter(self, x):
        """
        Emitiranje zahtjeva za prikazom ili skrivanjem taba za provjeru konvertera
        """
        self.emit(QtCore.SIGNAL('toggle_tab_konverter(PyQt_PyObject)'),
                  x)

    def toggle_umjeravanja(self, x):
        """
        Emitiranje zahtjeva za ukljucivanje umjeravanja za sve tabove sa rezultatima
        """
        self.emit(QtCore.SIGNAL('toggle_umjeravanja(PyQt_PyObject)'),
                  x)

    def toggle_ponovljivost(self, x):
        """
        Emitiranje zahtjeva za ukljucivanjem provjere ponovljivosti za sve
        tabove sa rezultatima
        """
        self.emit(QtCore.SIGNAL('toggle_ponovljivost(PyQt_PyObject)'),
                 x)

    def toggle_linearnost(self, x):
        """
        Emitiranje zahtjeva za uljucivanjem provjere linearnosti za sve tabove
        sa rezultatima
        """
        self.emit(QtCore.SIGNAL('toggle_linearnost(PyQt_PyObject)'),
                  x)

    def promjena_doubleSpinBoxOpseg(self, x):
        """slot koji dokumentu javlja promjenu opsega mjerenja"""
        value = self.doubleSpinBoxOpseg.value()
        self.dokument.set_opseg(value)

    def set_doubleSpinBoxOpseg(self, x):
        """Metoda postavlja izabrani opseg preuzet iz dokumenta u gui widgete
        x je mapa sa kljucevima 'value', 'recalculate'"""
        value = x['value']
        self.doubleSpinBoxOpseg.setValue(value)

    def set_mjernaJedinica(self, mapa):
        """Setter mjerne jedinice u labele gui-a"""
        jedinica = mapa['value']
        self.labelJedinicaOpseg.setText(jedinica)
        self.labelJedinicaCCRM.setText(jedinica)
        self.labelJedinicaZrak.setText(jedinica)

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

    def promjena_comboDilucija(self, x):
        """slot koji dokumentu javlja promjenu izabrane dilucijske jedinice"""
        value = self.comboDilucija.currentText()
        self.dokument.set_izabranaDilucija(value)

    def set_comboDilucija(self, x):
        """Metoda postavlja izabranu dilucijsku jedinicu preuzetu iz dokumenta
        u gui widget"""
        value = x['value']
        ind = self.comboDilucija.findText(value)
        self.comboDilucija.setCurrentIndex(ind)

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

    def promjena_comboZrak(self, x):
        """slot koji javlja dokumentu da je doslo do promjene izabranog generatora
        cistog zraka"""
        value = self.comboZrak.currentText()
        self.dokument.set_izabraniZrak(value)

    def set_comboZrak(self, x):
        """Metoda postavlja izabrani generator cistog zraka iz dokumenta u gui
        widget"""
        value = x['value']
        ind = self.comboZrak.findText(value)
        self.comboZrak.setCurrentIndex(ind)

    def promjena_zrakProizvodjacLineEdit(self, x):
        """slot koji postavlja proizvodjaca generatora cistog zraka u dokument"""
        value = self.zrakProizvodjacLineEdit.text()
        self.dokument.set_proizvodjacCistiZrak(value)

    def set_zrakProizvodjacLineEdit(self, x):
        """Metoda postavlja proizvodjaca generatora cistog zraka iz dokumenta
        u gui widget"""
        value = x['value']
        self.zrakProizvodjacLineEdit.setText(value)

    def promjena_doubleSpinBoxSljedivostCistiZrak(self, x):
        """slot koji postavlja sljedivost generatora cistog zraka u dokument"""
        value = self.doubleSpinBoxSljedivostCistiZrak.value()
        self.dokument.set_sljedivostCistiZrak(value)

    def set_doubleSpinBoxSljedivostCistiZrak(self, x):
        """Metoda postavlja slejdivost generatora cistog zraka iz dokumenta u gui
        widget"""
        value = x['value']
        self.doubleSpinBoxSljedivostCistiZrak.setValue(value)

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

    def promjena_napomenaPlainTextEdit(self):
        """slot koji postavlja tekst napomena u dokument"""
        value = self.napomenaPlainTextEdit.toPlainText()
        self.dokument.set_napomena(value)

    def set_napomenaPlainTextEdit(self, x):
        """metoda postavlja tekst napomene iz dokumenta u gui widget"""
        value = x['value']
        self.napomenaPlainTextEdit.setPlainText(value)
        self.napomenaPlainTextEdit.moveCursor(QtGui.QTextCursor.End)

    def napuni_comboMjerenje(self, x):
        """
        Metoda postavlja listu (lista stringova mjerenja) iz dokumenta
        u comboMjerenje widget. Lista se nalazi pod kljucem 'value' u mapi x.
        """
        value = x['value']
        self.comboMjerenje.blockSignals(True)
        self.comboMjerenje.clear()
        self.comboMjerenje.addItems(value)
        self.comboMjerenje.blockSignals(False)

    def napuni_comboDilucija(self, x):
        """
        Metoda postavlja listu (lista stringova dilucijskih jedinica) iz
        dokumenta u comboDilucija widget. Lista se nalazi pod kljucem 'value'
        u mapi x
        """
        value = x['value']
        self.comboDilucija.blockSignals(True)
        self.comboDilucija.clear()
        self.comboDilucija.addItems(value)
        self.comboDilucija.blockSignals(False)

    def napuni_comboZrak(self, x):
        """
        Metoda postavlja listu (lista stringova generatora cistog zraka) iz
        dokumenta u comboZrak widget. Lista se nalazi pod kljucem 'value'
        u mapi x
        """
        value = x['value']
        self.comboZrak.blockSignals(True)
        self.comboZrak.clear()
        self.comboZrak.addItems(value)
        self.comboZrak.blockSignals(False)

    def disable_sve_testove(self):
        self.disable_test('umjeravanje')
        self.disable_test('ponovljivost')
        self.disable_test('linearnost')
        self.disable_test('konverter')
        self.disable_test('odaziv')

    def enable_sve_testove(self):
        self.enable_test('umjeravanje')
        self.enable_test('ponovljivost')
        self.enable_test('linearnost')
        self.enable_test('konverter')
        self.enable_test('odaziv')

    def disable_test(self, x):
        if x == 'umjeravanje':
            self.checkUmjeravanje.setEnabled(False)
        elif x == 'ponovljivost':
            self.checkPonovljivost.setEnabled(False)
        elif x == 'linearnost':
            self.checkLinearnost.setEnabled(False)
        elif x == 'konverter':
            self.checkBoxKonverterTab.setEnabled(False)
        elif x == 'odaziv':
            self.checkBoxRiseFall.setEnabled(False)

    def enable_test(self, x):
        if x == 'umjeravanje':
            self.checkUmjeravanje.setEnabled(True)
        elif x == 'ponovljivost':
            self.checkPonovljivost.setEnabled(True)
        elif x == 'linearnost':
            self.checkLinearnost.setEnabled(True)
        elif x == 'konverter':
            self.checkBoxKonverterTab.setEnabled(True)
        elif x == 'odaziv':
            self.checkBoxRiseFall.setEnabled(True)
