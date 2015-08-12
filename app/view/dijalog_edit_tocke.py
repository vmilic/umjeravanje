# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 09:14:05 2015

@author: DHMZ-Milic
"""
import copy
from PyQt4 import QtGui, QtCore, uic
import app.model.frejm_model as modeli
import app.model.konfig_klase as konfig

BASE3, FORM3 = uic.loadUiType('./app/view/uiFiles/edit_tocku.ui')
class EditTockuDijalog(BASE3, FORM3):
    """
    Dijalog za edit pojedine tocke
    """
    def __init__(self, indeks=None, tocke=None, frejm=None, start=None, parent=None):
        """
        inicijalizacija sa:
        -indeksom tocke koju editiramo
        -listom tocaka
        -frejmom sirovih podataka
        -izabrani pocetni indeks
        """
        super(BASE3, self).__init__(parent)
        self.setupUi(self)

        #TODO! postavi pocetnu boju i indekse

        self.indeks = indeks
        self.tocke = tocke
        self.frejm = frejm
        self.startIndeks = start

        self.dataModel = modeli.SiroviFrameModel()
        self.dataModel.set_frejm(self.frejm)
        self.dataModel.set_tocke(self.tocke)
        self.dataModel.set_start(self.startIndeks)

        self.tableViewPodaci.setModel(self.dataModel)
        self.tableViewPodaci.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

        self.tocka = self.tocke[self.indeks]
        minIndeks = list(self.frejm.index)[min(self.tocka.indeksi)]
        maxIndeks = list(self.frejm.index)[max(self.tocka.indeksi)]
        cref = float(self.tocka.crefFaktor)

        self.crefDoubleSpinBox.setValue(cref)
        self.labelStart.setText(minIndeks)
        self.labelEnd.setText(maxIndeks)

        #TODO! connect elemente sa slotovima

    def set_start(self, ind):
        #TODO! provjera preklapanja sa drugim tockama
        red = ind.row()
        minIndeks = red
        maxIndeks = max(self.tocka.indeksi)
        if minIndeks == maxIndeks:
            return
        if minIndeks > maxIndeks:
            minIndeks, maxIndeks = maxIndeks, minIndeks
        self.tocka.indeksi = set(range(minIndeks, maxIndeks))
        self.labelStart.setText(maxIndeks)

    def set_end(self, ind):
        #TODO! provjera preklapanja sa drugim tockama
        red = ind.row()
        minIndeks = min(self.tocka.indeksi)
        maxIndeks = red
        if minIndeks == maxIndeks:
            return
        if minIndeks >= maxIndeks:
            minIndeks, maxIndeks = maxIndeks, minIndeks
        self.tocka.indeksi = set(range(minIndeks, maxIndeks))
        self.labelEnd.setText(maxIndeks)

    def set_cref(self, value):
        self.tocka.crefFaktor = value

    def promjena_boje(self, x):
        #TODO! prikaz boje.. pixmap, boja gumba?
        oldColor = self.tocka.boja.rgba()
        newColor, test = QtGui.QColorDialog.getRgba(oldColor)
        if test:
            color = QtGui.QColor().fromRgba(newColor)
            self.tocka.boja = color























BASE2, FORM2 = uic.loadUiType('./app/view/uiFiles/edit_tocke.ui')
class EditTockeDijalog(BASE2, FORM2):
    """
    Dijalog za edit i promjenu parametara tocaka za umjeravanje
    """
    def __init__(self, tocke=None, frejm=None, start=None, parent=None):
        """
        inicijalizacija sa
        - lista tocaka (kopija)
        - modelom sirovih podataka (trenutno ucitani)
        """
        super(BASE2, self).__init__(parent)
        self.setupUi(self)

        self.tocke = tocke
        self.frejm = frejm
        self.startIndeks = start

        self.dataModel = modeli.SiroviFrameModel()
        self.dataModel.set_frejm(self.frejm)
        self.dataModel.set_tocke(self.tocke)
        self.dataModel.set_start(self.startIndeks)

        self.izabranaTocka = None

        self.modelTocaka = modeli.TockeModel()
        self.modelTocaka.set_tocke(self.tocke)
        self.modelTocaka.set_frejm(self.frejm)

        self.colorDelegat = modeli.ColorDelegate(tocke=self.tocke)

        self.tockeView.setModel(self.modelTocaka)
        self.tockeView.horizontalHeader().setStretchLastSection(True)
        self.tockeView.setItemDelegateForColumn(6, self.colorDelegat)
        self.tockeView.update()

        self.dataView.setModel(self.dataModel)
        self.dataView.horizontalHeader().setStretchLastSection(True)
        self.dataView.update()

        self.setup_comboBox()

        #TODO! kontrolni connectioni
        self.dodajTockuGumb.clicked.connect(self.dodaj_tocku)
        self.izbrisiTockuGumb.clicked.connect(self.izbrisi_tocku)
        self.tockeView.clicked.connect(self.select_tocku)
        self.dataView.clicked.connect(self.odaberi_novi_interval_izabrane_tocke)

    def select_tocku(self, indeks):
        """
        izbor tocke klikom na tocku u tablici
        """
        red = indeks.row()
        self.selectTockuCombo.setCurrentIndex(red)

    def dodaj_tocku(self):
        """
        Dodavanje nove tocke na popis umjernih tocaka.
        """
        if len(self.tocke) == 0:
            #ne postoje tocke umjeravanja...napravi novu
            tocka = konfig.Tocka(ime='TOCKA1', start=15, end=45, cref=0.8)
            self.tocke.append(tocka)
        else:
            #pronadji max indeks izmedju svih tocaka
            maxIndeks = max([max(tocka.indeksi) for tocka in self.tocke])
            ime = "".join(['TOCKA',str(len(self.tocke)+1)])
            start = maxIndeks + 15
            end = maxIndeks + 30
            tocka = konfig.Tocka(ime=ime, start=start, end=end, cref=0.0)
            self.tocke.append(tocka)
        self.setup_comboBox()
        self.refresh_tablice()

    def refresh_tablice(self):
        self.dataModel.layoutChanged.emit()
        self.modelTocaka.layoutChanged.emit()
        self.tockeView.update()
        self.dataView.update()


    def izbrisi_tocku(self):
        """
        Brisanje izabrane tocke
        """
        if len(self.tocke) != 0:
            dots = [str(tocka) for tocka in self.tocke]
            tocka = self.selectTockuCombo.currentText()
            indeks = dots.index(tocka)
            self.tocke.pop(indeks)
            self.rename_tocke()
            self.setup_comboBox()
            self.refresh_tablice()

    def rename_tocke(self):
        n = 1
        for tocka in self.tocke:
            tocka.ime = "".join(['TOCKA', str(n)])
            n += 1

    def setup_comboBox(self):
        """
        Metoda populira combobox sa popisom tocaka prema nazivu.
        """
        if self.selectTockuCombo.count() != 0:
            self.izabranaTocka = self.selectTockuCombo.currentText()
        self.selectTockuCombo.blockSignals(True)
        self.selectTockuCombo.clear()
        dots = [str(tocka) for tocka in self.tocke]
        self.selectTockuCombo.addItems(dots)
        ind = self.selectTockuCombo.findText(self.izabranaTocka)
        if ind != -1:
            self.selectTockuCombo.setCurrentIndex(ind)
        self.selectTockuCombo.blockSignals(False)

    def odaberi_novi_interval_izabrane_tocke(self, x):
        """izbor novih granica tocke
        1. provjeri da li je izabrana neka tocka i dohvati njene podatke (lokaciju)
        2. selection changed...
        """
        if len(self.tocke) != 0:
            #indeks izabrane tocke
            dots = [str(dot) for dot in self.tocke]
            ind = dots.index(self.selectTockuCombo.currentText())
            #slektirani indeksi --> pretvori u redove
            indeksi = self.dataView.selectedIndexes()
            redovi = set(sorted([i.row() for i in indeksi]))
            #indeksi ostalih tocaka
            temp = copy.deepcopy(self.tocke)
            temp.pop(ind)
            testPreklapanja = [tocka.test_indeksi_tocke_se_preklapaju(redovi) for tocka in temp]
            if True in testPreklapanja:
                return None
            minimalni = min(redovi)
            if len(redovi) >= 15 and minimalni >= self.startIndeks:
                self.tocke[ind].indeksi = redovi
                #clear selection
                self.dataView.clearSelection()
                self.refresh_tablice()

    def vrati_nove_tocke(self):
        """
        getter za output dijaloga
        """
        return self.tocke
