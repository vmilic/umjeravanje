# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 09:55:59 2016

@author: DHMZ-Milic
"""
import logging


class GeneratorCistogZraka(object):
    """
    Reprezentacija generatora cistog zraka.
    Objekt sadrzi membere:
    -model, (string) naziv modela
    -proizvodjac, (string) naziov proizvodjaca
    -maxSO2, (float) maksimalni udio SO2
    -maxNOx, (float) maksimalni udio NOx
    -maxCO, (float) maksimalni udio  CO
    -maxO3, (float) maksimalni udio O3
    -maxBTX, (float) maksimalni udio BTX
    """
    def __init__(self, model='n/a', proizvodjac='n/a', maxSO2=0.0,
                 maxNOx=0.0, maxCO=0.0, maxO3=0.0, maxBTX=0.0):
        self.model = model
        self.proizvodjac = proizvodjac
        self.maxSO2 = maxSO2
        self.maxNOx = maxNOx
        self.maxCO = maxCO
        self.maxO3 = maxO3
        self.maxBTX = maxBTX

    def set_model(self, model):
        """Setter za naziv modela. Ulazni parametat je string."""
        model = str(model)
        if model != self.model:
            self.model = model

    def get_model(self):
        """Getter za naziv modela. Output je string."""
        return self.model

    def set_proizvodjac(self, proizvodjac):
        """Setter za naziv proizvodjaca uredjaja. Input je string."""
        proizvodjac = str(proizvodjac)
        if proizvodjac != self.proizvodjac:
            self.proizvodjac = proizvodjac

    def get_proizvodjac(self):
        """Getter za naziv proizvodjaca uredjaja. Output je string."""
        return self.proizvodjac

    def set_maxSO2(self, maxSO2):
        """Setter maksimalne koncentracije SO2. Input je float."""
        try:
            maxSO2 = float(maxSO2)
            if maxSO2 != self.maxSO2:
                self.maxSO2 = maxSO2
        except Exception as err:
            logging.warning(str(err), exc_info=True)

    def get_maxSO2(self):
        """Getter maksimalne koncentracije SO2. Output je float."""
        return self.maxSO2

    def set_maxNOx(self, maxNOx):
        """Setter maksimalne koncentracije NOx. Input je float."""
        try:
            maxNOx = float(maxNOx)
            if maxNOx != self.maxNOx:
                self.maxNOx = maxNOx
        except Exception as err:
            logging.warning(str(err), exc_info=True)

    def get_maxNOx(self):
        """Getter maksimalne koncentracije NOx. Output je float."""
        return self.maxNOx

    def set_maxCO(self, maxCO):
        """Setter maksimalne koncentracije CO. Input je float."""
        try:
            maxCO = float(maxCO)
            if maxCO != self.maxCO:
                self.maxCO = maxCO
        except Exception as err:
            logging.warning(str(err), exc_info=True)

    def get_maxCO(self):
        """Getter maksimalne koncentracije CO. Output je float."""
        return self.maxCO

    def set_maxO3(self, maxO3):
        """Setter maksimalne koncentracije O3. Input je float."""
        try:
            maxO3 = float(maxO3)
            if maxO3 != self.maxO3:
                self.maxO3 = maxO3
        except Exception as err:
            logging.warning(str(err), exc_info=True)

    def get_maxO3(self):
        """Getter maksimalne koncentracije O3. Output je float."""
        return self.maxO3

    def set_maxBTX(self, maxBTX):
        """Setter maksimalne koncentracije BTX. Input je float."""
        try:
            maxBTX = float(maxBTX)
            if maxBTX != self.maxBTX:
                self.maxBTX = maxBTX
        except Exception as err:
            logging.warning(str(err), exc_info=True)

    def get_maxBTX(self):
        """Getter maksimalne koncentracije BTX. Output je float."""
        return self.maxBTX
