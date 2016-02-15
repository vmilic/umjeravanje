# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 09:14:05 2015

@author: DHMZ-Milic
"""
from PyQt4 import QtGui, uic
from app.model.qt_models import SiroviFrameModel


BASE_EDIT_TOCKU, FORM_EDIT_TOCKU = uic.loadUiType('./app/view/uiFiles/dijalog_edit_tocku.ui')
class EditTockuDijalog(BASE_EDIT_TOCKU, FORM_EDIT_TOCKU):
    """
    Dijalog za edit pojedine tocke
    """
    def __init__(self, parent=None, frejm=None, tocke=None, start=None, indeks=None):
        """
        -frejm : pandas dataframe podataka
        -tocke : lista objekata "Tocka", sve tocke umjeravanja
        -start : int, pocetni indeks umjeravanja
        -indeks : int, indeks pod kojim se nalazi tocka u listi tocke
        """
        super(BASE_EDIT_TOCKU, self).__init__(parent)
        self.setupUi(self)

        self.frejm = frejm
        self.tocke = tocke
        self.indeks = indeks
        self.start = start

        self.tocka = self.tocke[self.indeks]
        self.model = SiroviFrameModel(frejm=frejm, tocke=tocke, start=start)
        self.tableViewPodaci.setModel(self.model)
        self.tableViewPodaci.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        try:
            minIndeks = list(frejm.index)[min(self.tocka.get_indeksi())]
            maxIndeks = list(frejm.index)[max(self.tocka.get_indeksi())]
        except Exception:
            minIndeks = None
            maxIndeks = None
        cref = float(self.tocka.get_crefFaktor())

        self.crefDoubleSpinBox.setValue(cref)
        self.labelStart.setText(str(minIndeks))
        self.labelEnd.setText(str(maxIndeks))
        self.labelBrojPodataka.setText(str(len(self.tocka.get_indeksi())))
        stil = self.color_to_style_string(self.tocka.get_color())
        self.gumbBoja.setStyleSheet(stil)

        #connect elemente sa slotovima
        self.crefDoubleSpinBox.valueChanged.connect(self.set_cref)
        self.gumbBoja.clicked.connect(self.promjena_boje)
        self.gumbStart.clicked.connect(self.set_start)
        self.gumbEnd.clicked.connect(self.set_end)
        self.tableViewPodaci.clicked.connect(self.set_selektirani_indeks)

    def get_promjenjena_tocka(self):
        """
        output modificirane tocake
        """
        return self.tocka

    def set_selektirani_indeks(self, modelIndeks):
        """
        pamti zadnje selektirani indeks u tablici
        """
        if modelIndeks.isValid():
            red = modelIndeks.row()
            self.selektiraniIndeks = red
        else:
            self.selektiraniIndeks = None

    def set_start(self):
        """
        promjena pocetnog pocetnog indeksa tocke
        """
        red = self.selektiraniIndeks
        if red is not None:
            minIndeks = red
            maxIndeks = max(self.tocka.get_indeksi())
            if minIndeks == maxIndeks:
                return
            if minIndeks > maxIndeks:
                minIndeks, maxIndeks = maxIndeks, minIndeks
            raspon = set(range(minIndeks, maxIndeks))
            if len(raspon) < 15:
                QtGui.QMessageBox.information(self, 'Pogreska', 'Tocka mora imati barem 15 minutnih vrijednosti.')
                return
            testPreklapanja = [tocka for tocka in self.tocke if tocka != self.tocka]
            testPreklapanja = [tocka.test_indeksi_tocke_se_preklapaju(raspon) for tocka in testPreklapanja]
            if True in testPreklapanja:
                QtGui.QMessageBox.information(self, 'Pogreska', 'Tocke se ne smiju preklapati.')
                return
            self.tocka.set_indeksi(raspon)
            noviStart = list(self.frejm.index)[minIndeks]
            self.labelStart.setText(str(noviStart))
            self.labelBrojPodataka.setText(str(len(self.tocka.get_indeksi())))
            self.model.layoutChanged.emit()
            self.tableViewPodaci.update()

    def set_end(self):
        """
        prmojena zavrsnog indeksa tocke
        """
        red = self.selektiraniIndeks
        if red is not None:
            minIndeks = min(self.tocka.get_indeksi())
            maxIndeks = red
            if minIndeks == maxIndeks:
                return
            if minIndeks >= maxIndeks:
                minIndeks, maxIndeks = maxIndeks, minIndeks
            raspon = set(range(minIndeks, maxIndeks))
            if len(raspon) < 15:
                QtGui.QMessageBox.information(self, 'Pogreska', 'Tocka mora imati barem 15 minutnih vrijednosti')
                return
            testPreklapanja = [tocka for tocka in self.tocke if tocka != self.tocka]
            testPreklapanja = [tocka.test_indeksi_tocke_se_preklapaju(raspon) for tocka in testPreklapanja]
            if True in testPreklapanja:
                QtGui.QMessageBox.information(self, 'Pogreska', 'Tocke se ne smiju preklapati.')
                return
            self.tocka.set_indeksi(raspon)
            noviKraj = list(self.frejm.index)[maxIndeks]
            self.labelEnd.setText(str(noviKraj))
            self.labelBrojPodataka.setText(str(len(self.tocka.get_indeksi())))
            self.model.layoutChanged.emit()
            self.tableViewPodaci.update()

    def set_cref(self, value):
        """
        postavljanje nove cref vrijednosti
        """
        self.tocka.set_crefFaktor(value)

    def promjena_boje(self, x):
        """
        promjena boje tocke uz pomoc dijaloga. Update boje gumba u istu boju
        """
        oldColor = self.tocka.get_color()
        newColor = QtGui.QColorDialog.getColor(oldColor, self, 'Promjena boje tocke', QtGui.QColorDialog.ShowAlphaChannel)
        if newColor.isValid():
            self.tocka.set_red(newColor.red())
            self.tocka.set_green(newColor.green())
            self.tocka.set_blue(newColor.blue())
            self.tocka.set_alpha(newColor.alpha())
            stil = self.color_to_style_string(newColor)
            self.gumbBoja.setStyleSheet(stil)
            #signaliziraj promjenu model i view
            self.tableViewPodaci.update()

    def color_to_style_string(self, color):
        """
        input:
            color -> QtGui.QColor (QColor objekt, sadrzi informaciju o boji)
        output:
            string - styleSheet 'css' stil ciljanog elementa
        """
        r = color.red()
        g = color.green()
        b = color.blue()
        a = int(100*color.alpha()/255)
        stil = "QPushButton#gumbBoja {background-color: rgba(" +"{0},{1},{2},{3}%)".format(r, g, b, a)+"}"
        return stil
