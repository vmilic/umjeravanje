# -*- coding: utf-8 -*-
"""
Created on Mon Feb 16 10:13:58 2015

@author: User
"""
from PyQt4 import uic
BASE2, FORM2 = uic.loadUiType('./app/view/uiFiles/auth_login.ui')


class DijalogLoginAuth(BASE2, FORM2):
    """Dijalog za unos user name i password"""
    def __init__(self, parent=None):
        super(BASE2, self).__init__(parent)
        self.setupUi(self)
        self.user = None
        self.password = None
        self.LEUser.textEdited.connect(self.set_user)
        self.LEPass.textEdited.connect(self.set_pswd)

    def set_user(self, user):
        """setter za user name"""
        self.user = str(user)

    def set_pswd(self, pswd):
        """seter za password"""
        self.password = str(pswd)

    def vrati_postavke(self):
        """metoda zaduzena za vracanje podataka"""
        return self.user, self.password
