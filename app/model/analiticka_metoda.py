# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 09:06:35 2016

@author: DHMZ-Milic
"""
class AnalitickaMetoda(object):
    """
    Objekt analiticke metode.

    memebri stanja sa getterima i setterima:
    -ID        : id metode preuzet sa REST-a -- string
    -jedinica  : mjerna jedinica -- string( npr. 'mg/m3')
    -naziv     : naziv metode -- string( npr. 'UV Fotometrija')
    -norma     : naziv norme -- string( npr. 'HRN EN 14625:2005')
    -Srs       : ponovljivost pri spanu -- float (%)
    -Srz       : ponovljivost u nuli -- float (abs)
    -o         : opseg -- float (abs)
    -rmax      : maksimalno odstupanje od linearnosti -- float (%)
    -rz        : odstupanje od linearnosti u nuli -- float (abs)
    -tr        : vrijeme uspona -- float (s)
    -tf        : vrijeme pada -- float (s)
    -Ec_min    : minimalna efikasnost konvertera -- float (%)
    -Ec_max    : maksimalna efikasnost konvertera -- float (%)
    """
    Srs_opis = 'Ponovljivost pri spanu'
    Srz_opis = 'Ponovljivost u nuli'
    o_opis = 'Opseg'
    rmax_opis = 'Maksimalno odstupanje od linearnosti'
    rz_opis = 'Odstupanje od linearnosti u nuli'
    tr_opis = 'Vrijeme uspona'
    tf_opis = 'Vrijeme pada'
    Ec_opis = 'Efikasnost konvertera'

    def __init__(self, ID='n/a', jedinica='n/a', naziv='n/a', norma='n/a', Srs=0.0,
                 Srz=0.0, o=0.0, rmax=0.0, rz=0.0, Ec_min=0.0,
                 Ec_max=0.0, tr=0.0, tf=0.0):

        self.set_member = {'ID':self.set_ID,
                           'jedinica':self.set_jedinica,
                           'naziv':self.set_naziv,
                           'norma':self.set_norma,
                           'Srs':self.set_Srs,
                           'Srz':self.set_Srz,
                           'o':self.set_o,
                           'rmax':self.set_rmax,
                           'rz':self.set_rz,
                           'tr':self.set_tr,
                           'tf':self.set_tf,
                           'Ec_min':self.set_Ec_min,
                           'Ec_max':self.set_Ec_max}

        self.get_member = {'ID':self.get_ID,
                           'jedinica':self.get_jedinica,
                           'naziv':self.get_naziv,
                           'norma':self.get_norma,
                           'Srs':self.get_Srs,
                           'Srz':self.get_Srz,
                           'o':self.get_o,
                           'rmax':self.get_rmax,
                           'rz':self.get_rz,
                           'tr':self.get_tr,
                           'tf':self.get_tf,
                           'Ec_min':self.get_Ec_min,
                           'Ec_max':self.get_Ec_max,
                           'Ec':self.get_Ec}

        self.ID = ID
        self.jedinica = jedinica
        self.naziv = naziv
        self.norma = norma
        self.Srs = Srs
        self.Srz = Srz
        self.o = o
        self.rmax = rmax
        self.rz = rz
        self.tr = tr
        self.tf = tf
        self.Ec_min = Ec_min
        self.Ec_max = Ec_max
        self.Ec = [Ec_min, Ec_max]

    def set_ID(self, x):
        """Setter ID metode. Input je string."""
        x = str(x)
        if self.ID != x:
            self.ID = x

    def get_ID(self):
        """Getter ID metode. Output je string."""
        return self.ID

    def set_jedinica(self, x):
        """Setter mjerne jedinice metode. Input je string."""
        x = str(x)
        if self.jedinica != x:
            self.jedinica = x

    def get_jedinica(self):
        """Getter mjerne jedinice metode. Output je string."""
        return self.jedinica

    def set_naziv(self, x):
        """Setter naziva metode. Input je string."""
        x = str(x)
        if self.naziv != x:
            self.naziv = x

    def get_naziv(self):
        """Getter naziva metode. Output je string."""
        return self.naziv

    def set_norma(self, x):
        """Setter norme metode. Input je string."""
        x = str(x)
        if self.norma != x:
            self.norma = x

    def get_norma(self):
        """Getter norme metode. Output je string."""
        return self.norma

    def set_Srs(self, x):
        """Setter ponovljivosti pri spanu. Input je float."""
        x = float(x)
        if self.Srs != x:
            self.Srs = x

    def get_Srs(self):
        """Getter ponovljivosti pri spanu. Output je float."""
        return self.Srs

    def set_Srz(self, x):
        """Setter ponovljivosti u nuli. Input je float."""
        x = float(x)
        if self.Srz != x:
            self.Srz = x

    def get_Srz(self):
        """Getter ponovljivosti u nuli. Output je float"""
        return self.Srz

    def set_o(self, x):
        """Setter opsega metode. Input je float."""
        x = float(x)
        if self.o != x:
            self.o = x

    def get_o(self):
        """Getter opsega metode. Output je float."""
        return self.o

    def set_rmax(self, x):
        """Setter maksimalnog odstupanja od linearnosti. Input je float."""
        x = float(x)
        if self.rmax != x:
            self.rmax = x

    def get_rmax(self):
        """Getter maksimalnog odstupanja od linearnosti. Output je float."""
        return self.rmax

    def set_rz(self, x):
        """Setter maksimalnog odstupanja od linearnosti u nuli. Input je float."""
        x = float(x)
        if self.rz != x:
            self.rz = x

    def get_rz(self):
        """Getter maksimalnog odstupanja od linearnosti u nuli. Output je float."""
        return self.rz

    def set_tr(self, x):
        """Setter vremena uspona. Input je float."""
        x = float(x)
        if self.tr != x:
            self.tr = x

    def get_tr(self):
        """Getter vremena uspona. Output je float"""
        return self.tr

    def set_tf(self, x):
        """Setter vremena pada. Input je float."""
        x = float(x)
        if self.tf != x:
            self.tf = x

    def get_tf(self):
        """Getter vremena pada. Output je float"""
        return self.tf

    def set_Ec_min(self, x):
        """Setter minimalne efikasnosti konvertera. Input je float."""
        x = float(x)
        if self.Ec_min != x:
            self.Ec_min = x
            self.Ec[0] = x

    def get_Ec_min(self):
        """Getter minimalne efikasnosti konvertera. Output je float."""
        return self.Ec_min

    def set_Ec_max(self, x):
        """Setter maksimalne efikasnosti konvertera. Input je float."""
        x = float(x)
        if self.Ec_max != x:
            self.Ec_max = x
            self.Ec[1] = x

    def get_Ec_max(self):
        """Getter maksimalne efikasnosti konvertera. Output je float."""
        return self.Ec_max

    def get_Ec(self):
        """Getter liste efikasnosti konvertera. Output je lista 2 floata."""
        return self.Ec
