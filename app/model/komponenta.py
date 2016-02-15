# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 09:20:26 2016

@author: DHMZ-Milic
"""


class Komponenta(object):
    """
    Reprezentacija komponente umjeravanja.
    Memberi stanja (sa pripadnim setterima i getterima) su:
    -naziv : string, naziv komponente
    -jedinica : string, mjerne jedinice
    -formula : string, formule
    """
    def __init__(self,
                 naziv='n/a',
                 jedinica='n/a',
                 formula='n/a',
                 kv=1.0):
        self.naziv = str(naziv)
        self.jedinica = str(jedinica)
        self.formula = str(formula)
        self.kv = kv

    def set_naziv(self, naziv):
        """Setter punog naziva komponente. Input je string."""
        naziv = str(naziv)
        if naziv != self.naziv:
            self.naziv = naziv

    def get_naziv(self):
        """Getter punog naziva komponente. Output je string."""
        return self.naziv

    def set_jedinica(self, jedinica):
        """Setter mjerne jedinice komponente. Input je string."""
        jedinica = str(jedinica)
        if jedinica != self.jedinica:
            self.jedinica = jedinica

    def get_jedinica(self):
        """Getter mjerne jedinice komponente. Output je string."""
        return self.jedinica

    def set_formula(self, formula):
        """Setter formule komponente. Input je string."""
        formula = str(formula)
        if formula != self.formula:
            self.formula = formula

    def get_formula(self):
        """Getter formule komopnente. Output je string."""
        return self.formula

    def set_kv(self, kv):
        """Setter konverzijskog volumena za komponentu. Input je float."""
        kv = float(kv)
        if kv != self.kv:
            self.kv = kv

    def get_kv(self):
        """Getter konverzijskog volumena za komponentu. Output je float."""
        return self.kv

