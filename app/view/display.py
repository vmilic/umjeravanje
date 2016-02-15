# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 12:52:04 2016

@author: DHMZ-Milic
"""
from PyQt4 import QtGui, QtCore, uic
from app.view import umjeravanje_prozor

BASE, FORM = uic.loadUiType('./app/view/uiFiles/mdi_display.ui')
class GlavniProzor(BASE, FORM):
    """
    Gui element glavnog prozora
    """
    def __init__(self, parent=None):
        super(BASE, self).__init__(parent)
        self.setupUi(self)
        self.mdiArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        #dio sa windowMapperom je copy/pasted...
        self.windowMapper = QtCore.QSignalMapper(self)
        self.windowMapper.mapped[QtGui.QWidget].connect(self.mdiArea.setActiveSubWindow)
        ### Setup signala i slotova ###
        self.setup_signal_connections()
        #update izbornika
        self.update_menu()

    def setup_signal_connections(self):
        """PyQt4 conncections..."""
        self.action_exit.triggered.connect(self.close)
        self.action_save.triggered.connect(self.save_umjeravanje)
        self.action_save_as.triggered.connect(self.save_as_umjeravanje)
        self.action_close_aktivno_umjeravanje.triggered.connect(self.mdiArea.closeActiveSubWindow)
        self.action_close_all_umjeravanja.triggered.connect(self.mdiArea.closeAllSubWindows)
        self.mdiArea.subWindowActivated.connect(self.update_menu)
        self.menu_Umjeravanja.aboutToShow.connect(self.update_menu_umjeravanje)

    def get_aktivne_serial_portove(self):
        """Metoda vraca set aktivnih serial portova"""
        aktivniSerialPortovi = [i.widget().get_serial_kolektora() for i in self.mdiArea.subWindowList()]
        return set(aktivniSerialPortovi)

    def save_umjeravanje(self):
        """save umjeravanja u isti file"""
        prozor = self.get_aktivno_umjeravanje()
        if prozor:
            uspjeh = prozor.save()
            if uspjeh:
                self.statusBar().showMessage("Umjeravanje je uspjesno spremljeno u file.", 2000)
            else:
                self.statusBar().showMessage("Umjeravanje nije uspjesno spremljeno u file.", 2000)

    def save_as_umjeravanje(self):
        """save umjeravanja u isti file"""
        prozor = self.get_aktivno_umjeravanje()
        if prozor:
            uspjeh = prozor.save_file_as()
            if uspjeh:
                self.statusBar().showMessage("Umjeravanje je uspjesno spremljeno u file.", 2000)
            else:
                self.statusBar().showMessage("Umjeravanje nije uspjesno spremljeno u file.", 2000)

    def load_umjeravanje(self, path=None, data=None):
        """Load umjeravanja. Provjerava se da li je isti file trenutno otvoren.
        Ako nije, stvara se novi prozor umjeravanje te se pokusava loadati datastore.
        U slucaju neuspjeha, prozor se zatvara.
        -path : string path do filea
        -data : instanca Datastore objekta
        """
        #provjeri da li je prozor vec otvoren
        prethodnoOtvoreni = self.find_prozor_umjeravanja(path)
        if prethodnoOtvoreni:
            self.mdiArea.setActiveSubWindow(prethodnoOtvoreni)
            return None
        #dohvati postavke prozora umjeravanje iz data
        uredjaj = data.get_uredjaj()
        generatori = data.get_generatori()
        dilucije = data.get_dilucije()
        postaje = data.get_postaje()
        cfg = data.get_konfig()
        #stvori novi prozor
        child = self.stvori_prozor_umjeravanja(uredjaj=uredjaj,
                                               generatori=generatori,
                                               dilucije=dilucije,
                                               postaje=postaje,
                                               cfg=cfg,
                                               datastore=data)
        if child.load_file(path=path):
            #ako se uspjesno loada... prikazi
            self.statusBar().showMessage("Umjeravanje je uspjesno ucitano iz filea.", 2000)
            child.show()
        else:
            #ako ne uspije load... zatvori prozor
            child.close()

    def find_prozor_umjeravanja(self, path):
        """za zadani file path, pronadji otvoreni prozor umjeravanja."""
        for prozor in self.mdiArea.subWindowList():
            if prozor.widget().get_trenutnoImeFilea() == path:
                return prozor
        return None

    def stvori_prozor_umjeravanja(self, uredjaj=None, generatori=None, dilucije=None, postaje=None, cfg=None, datastore=None):
        """
        createMdiChild
        metoda stvara 'child' objekt umjeravanja (prozor) i dodaje ga u
        MDI area"""
        child = umjeravanje_prozor.Umjeravanje(uredjaj=uredjaj,
                                               generatori=generatori,
                                               dilucije=dilucije,
                                               postaje=postaje,
                                               cfg=cfg,
                                               datastore=datastore)
        self.mdiArea.addSubWindow(child)
        return child

    def new_umjeravanje(self, uredjaj=None, generatori=None, dilucije=None, folder=None, postaje=None, cfg=None, datastore=None):
        """callback za stvaranje novog umjeravanja."""
        child = self.stvori_prozor_umjeravanja(uredjaj=uredjaj,
                                               generatori=generatori,
                                               dilucije=dilucije,
                                               postaje=postaje,
                                               cfg=cfg,
                                               datastore=datastore)
        child.novi_file(folder=folder)
        child.show()
        child.save() #save file umjeravanja

    def get_aktivno_umjeravanje(self):
        """Metoda vraca aktivno umjeravanje ili None"""
        aktivnoUmjeravanje = self.mdiArea.activeSubWindow()
        if aktivnoUmjeravanje:
            return aktivnoUmjeravanje.widget()
        return None

    def update_menu(self):
        """enable i disable opcija menua ovisno o postojanju 'umjeravanja'"""
        aktivnoUmjeravanje = self.get_aktivno_umjeravanje()
        if aktivnoUmjeravanje:
            check = True
        else:
            check = False
        self.action_save.setEnabled(check)
        self.action_save_as.setEnabled(check)
        self.action_close_aktivno_umjeravanje.setEnabled(check)
        self.action_close_all_umjeravanja.setEnabled(check)

    def update_menu_umjeravanje(self):
        """
        Metoda koja dinamicki updatea menu umjeravanja prije prikaza. Upotpunjava popis
        sa trenutno aktivnim prozorima.

        P.S. ovo moze postati ekstremno blesavo ako se otvori velik broj dokumenata istovremeno
        """
        self.menu_Umjeravanja.clear()
        self.menu_Umjeravanja.addAction(self.action_close_aktivno_umjeravanje)
        self.menu_Umjeravanja.addAction(self.action_close_all_umjeravanja)
        self.menu_Umjeravanja.addSeparator()

        umjeravanja = self.mdiArea.subWindowList()
        for i, prozor in enumerate(umjeravanja):
            child = prozor.widget()
            text = "{0} {1}".format(str(i+1), str(child.get_trenutnoImeFilea()))
            action = self.menu_Umjeravanja.addAction(text)
            action.setCheckable(True)
            action.setChecked(child is self.get_aktivno_umjeravanje())
            #dio sa windowMapperom je copy/pasted...
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, prozor)

    def closeEvent(self, event):
        """
        close event gui-a, gui mora zatvoriti sve 'child' prozore i signalizirati
        kontroleru da je gotov.
        """
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            event.accept()
            self.emit(QtCore.SIGNAL('gui_terminated'))
