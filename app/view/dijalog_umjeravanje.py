# -*- coding: utf-8 -*-
"""
Created on Tue Feb  2 13:32:50 2016

@author: DHMZ-Milic
"""

from PyQt4 import uic

BASE_DIJALOG_UMJERAVANJE, FORM_DIJALOG_UMJERAVANJE = uic.loadUiType('./app/view/uiFiles/dijalog_umjeravanje.ui')
class DijalogUmjeravanje(BASE_DIJALOG_UMJERAVANJE, FORM_DIJALOG_UMJERAVANJE):
    """
    Dijalog za izbor postavki umjeravanja
    """
    def __init__(self, dokument=None, parent=None):
        super(BASE_DIJALOG_UMJERAVANJE, self).__init__(parent)
        self.setupUi(self)
        self.doc = dokument

        self.setup_connections()

        uredjaji = self.doc.get_listu_uredjaja()
        cistiZrak = self.doc.get_listu_generatora_cistog_zraka()
        dilucije = self.doc.get_listu_dilucijskih_jedinica()

        self.comboBoxUredjaj.addItems(uredjaji)
        self.comboBoxZrak.addItems(cistiZrak)
        self.comboBoxDilucija.addItems(dilucije)

        self.izabraniUredjaj = self.comboBoxUredjaj.currentText()
        self.izabraniZrak = self.comboBoxZrak.currentText()
        self.izabranaDilucija = self.comboBoxDilucija.currentText()

    def setup_connections(self):
        self.comboBoxUredjaj.currentIndexChanged.connect(self.set_izabraniUredjaj)
        self.comboBoxZrak.currentIndexChanged.connect(self.set_izabraniZrak)
        self.comboBoxDilucija.currentIndexChanged.connect(self.set_izabranuDiluciju)

    def set_izabraniUredjaj(self, x):
        self.izabraniUredjaj = self.comboBoxUredjaj.currentText()

    def get_izabraniUredjaj(self):
        return self.izabraniUredjaj

    def set_izabraniZrak(self, x):
        self.izabraniZrak = self.comboBoxZrak.currentText()

    def get_izabraniZrak(self):
        return self.izabraniZrak

    def set_izabranuDiluciju(self, x):
        self.izabranaDilucija = self.comboBoxDilucija.currentText()

    def get_izabranuDiluciju(self):
        return self.izabranaDilucija
