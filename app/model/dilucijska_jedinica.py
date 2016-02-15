# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 09:53:40 2016

@author: DHMZ-Milic
"""
import logging


class DilucijskaJedinica(object):
    """
    Reprezentacija dilucijske jedinice.
    Objekt sadrzi membere:
    -model (string)
    -naziv proizvidjaca (string)
    -nul plin U (float)
    -nul plin sljedivost (string)
    -kal plin U (float)
    -kal plin sljedivost (string)
    -ozon U (float)
    -ozon sljedivost (string)
    """
    def __init__(self, model='n/a', proizvodjac='n/a', uNul=0.0, uKal=0.0, uO3=0.0, sljedivost=0.0):
        self.model = model
        self.proizvodjac = proizvodjac
        self.uNul = uNul
        self.uKal = uKal
        self.uO3 = uO3
        self.sljedivost = sljedivost

    def set_model(self, model):
        """Setter naziva dilucijske jedinice (oznaka modela). Input je string."""
        model = str(model)
        if model != self.model:
            self.model = model

    def get_model(self):
        """Getter naziva dilucijske jedinice. Output je string."""
        return self.model

    def set_proizvodjac(self, proizvodjac):
        """Setter proizvodjaca dilucjiske jedinice. Input je string."""
        proizvodjac = str(proizvodjac)
        if proizvodjac != self.proizvodjac:
            self.proizvodjac = proizvodjac

    def get_proizvodjac(self):
        """Getter proizvodjaca dilucijske jedinice. Output je string."""
        return self.proizvodjac

    def set_sljedivost(self, sljedivost):
        """Setter sljedivosti dilucijske jedinice."""
        try:
            sljedivost = float(sljedivost)
            if sljedivost != self.sljedivost:
                self.sljedivost = sljedivost
        except Exception as err:
            logging.warning(str(err), exc_info=True)

    def get_sljedivost(self):
        """Getter sljedivosti dilucijske jedinice."""
        return self.sljedivost

    def set_uNul(self, uNul):
        """Setter U nul plina (MFC_NUL_PLIN U). Input je float."""
        try:
            uNul = float(uNul)
            if uNul != self.uNul:
                self.uNul = uNul
        except Exception as err:
            logging.warning(str(err), exc_info=True)

    def get_uNul(self):
        """Getter U nul plina (MFC_NUL_PLIN U). Output je float."""
        return self.uNul

    def set_uKal(self, uKal):
        """Setter U kalibracijskog plina (MFC_KAL_PLIN U). Input je
        float."""
        try:
            uKal = float(uKal)
            if uKal != self.uKal:
                self.uKal = uKal
        except Exception as err:
            logging.warning(str(err), exc_info=True)

    def get_uKal(self):
        """Geter U kalibracijskog plina (MFC_KAL_PLIN U). Output je float."""
        return self.uKal

    def set_uO3(self, uO3):
        """Setter U ozona (GENERATOR OZONA U). Input je float."""
        try:
            uO3 = float(uO3)
            if uO3 != self.uO3:
                self.uO3 = uO3
        except Exception as err:
            logging.warning(str(err), exc_info=True)

    def get_uO3(self):
        """Getter U ozona (GENERATOR OZONA U). Output je float."""
        return self.uO3
