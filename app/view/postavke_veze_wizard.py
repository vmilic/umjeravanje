# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:28:41 2015

@author: DHMZ-Milic
"""
import sys
import glob
import serial
import logging
import ipaddress
from PyQt4 import QtGui


def list_serial_ports():
    """ Lists serial port names
        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


class PostavkeVezeWizard(QtGui.QWizard):
    """
    Wizard klasa postavke veze sa uredjajem kojeg umjeravamo
    """
    def __init__(self, parent=None, uredjaji=None):
        QtGui.QWizard.__init__(self, parent)
        if uredjaji == None:
            self.uredjaji = []
        else:
            self.uredjaji = uredjaji
        # opcije
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.setMinimumSize(600, 600)
        self.setWindowTitle("Postavke veze uredjaja")
        self.setOption(QtGui.QWizard.IndependentPages, on=False)
        # stranice wizarda
        self.izborUredjaja = PageIzborUredjaja(parent=self)
        self.izborVeze = PageIzborVeze(parent=self)
        self.izborProtokola = PageIzborProtokola(parent=self)
        self.setPage(1, self.izborUredjaja)
        self.setPage(2, self.izborVeze)
        self.setPage(3, self.izborProtokola)
        self.setStartId(1)

    def get_postavke_veze(self):
        mapa = self.izborProtokola.get_postavke()
        return mapa


class PageIzborUredjaja(QtGui.QWizardPage):
    """
    Stranice za izbor uredjaja s kojim se pokusavamo spojiti. (stranica1)
    """
    def __init__(self, parent = None):
        QtGui.QWizard.__init__(self, parent)
        self.setTitle('Izabor uredjaja')
        self.setSubTitle('Izaberi uredjaj s kojim se pokusavas spojiti')
        self.izabraniUredjaj = None
        # widgets
        self.labelOpis = QtGui.QLabel('Uredjaji :')
        self.comboBoxUredjaji = QtGui.QComboBox()
        # layout
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.labelOpis)
        layout.addWidget(self.comboBoxUredjaji)
        layout.addStretch(-1)
        self.setLayout(layout)

        self.comboBoxUredjaji.currentIndexChanged.connect(self.promjena_uredjaja)

    def promjena_uredjaja(self, x):
        tekst = self.comboBoxUredjaji.currentText()
        self.izabraniUredjaj = tekst

    def initializePage(self):
        self.comboBoxUredjaji.clear()
        uredjaji = self.wizard().uredjaji
        self.comboBoxUredjaji.addItems(uredjaji)
        self.izabraniUredjaj = self.comboBoxUredjaji.currentText()

    def validatePage(self):
        return True


class PageIzborVeze(QtGui.QWizardPage):
    """Stranica wizarda za izbor tipa veze (stranica2)"""
    def __init__(self, parent=None):
        QtGui.QWizardPage.__init__(self, parent)
        self.setTitle('Izbor veze')
        self.setSubTitle('Izaberi nacin spajanja sa uredjajem')
        self.labelVeza = QtGui.QLabel('Tip veze :')
        self.comboBoxVeza = QtGui.QComboBox()
        self.izabranaVeza = None

        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.labelVeza)
        layout.addWidget(self.comboBoxVeza)
        layout.addStretch(-1)
        self.setLayout(layout)

        self.comboBoxVeza.currentIndexChanged.connect(self.promjena_veze)

    def promjena_veze(self, x):
        tekst = self.comboBoxVeza.currentText()
        self.izabranaVeza = tekst

    def initializePage(self):
        self.comboBoxVeza.clear()
        veze = ['RS-232']
        self.comboBoxVeza.addItems(veze)
        self.izabranaVeza = self.comboBoxVeza.currentText()

    def validatePage(self):
        return True


class PageIzborProtokola(QtGui.QWizardPage):
    """Stranica za izbor protokola veze (stranica3)"""
    def __init__(self, parent=None):
        QtGui.QWizardPage.__init__(self, parent)
        self.setTitle('Izbor protokola')
        self.setSubTitle('Izaberi postavke komunikacijskog protokola')
        self.postavkeProtokola = {}

        self.ipAddressLabel = QtGui.QLabel('IP adresa :')
        self.ipAddress = QtGui.QLineEdit()

        self.tipRS232vezeLabel = QtGui.QLabel('Tip RS-232 veze :')
        self.tipRS232veze = QtGui.QComboBox()
        tipoviRS232veze = ['Hessen', 'Standard']
        self.tipRS232veze.addItems(tipoviRS232veze)

        self.portLabel = QtGui.QLabel('Port :')
        listaPortova = list_serial_ports()
        self.port = QtGui.QComboBox()
        self.port.addItems(listaPortova)

        self.brzinaLabel = QtGui.QLabel('Brzina (Baud Rate):')
        self.brzina = QtGui.QComboBox()
        listaBaudRate = ['50', '75', '110', '134', '150', '200', '300', '600',
                         '1200', '1800', '2400', '4800', '9600', '19200',
                         '38400', '57600', '115200']
        self.brzina.addItems(listaBaudRate)

        self.paritetLabel = QtGui.QLabel('Paritet :')
        self.paritet = QtGui.QComboBox()
        listaPariteta = sorted(['none', 'odd', 'even', 'mark', 'space'])
        self.paritet.addItems(listaPariteta)

        self.brojBitovaLabel = QtGui.QLabel('Broj bitova :')
        self.brojBitova = QtGui.QComboBox()
        listaBrojaBitova = ['5','6','7','8']
        self.brojBitova.addItems(listaBrojaBitova)

        self.stopBitoviLabel = QtGui.QLabel('Stop bitovi :')
        self.stopBitovi = QtGui.QComboBox()
        listaStopBitova = ['1', '2']
        self.stopBitovi.addItems(listaStopBitova)

        layout = QtGui.QGridLayout()
        layout.addWidget(self.ipAddressLabel, 0, 0, 1, 1)
        layout.addWidget(self.ipAddress, 0, 1, 1, 1)
        layout.addWidget(self.tipRS232vezeLabel, 1, 0, 1, 1)
        layout.addWidget(self.tipRS232veze, 1, 1, 1, 1)
        layout.addWidget(self.portLabel, 2 ,0 ,1, 1)
        layout.addWidget(self.port, 2 ,1 ,1, 1)
        layout.addWidget(self.brzinaLabel, 3 ,0 ,1, 1)
        layout.addWidget(self.brzina, 3 ,1 ,1, 1)
        layout.addWidget(self.paritetLabel, 4 ,0 ,1, 1)
        layout.addWidget(self.paritet, 4 ,1 ,1, 1)
        layout.addWidget(self.brojBitovaLabel, 5 ,0 ,1, 1)
        layout.addWidget(self.brojBitova, 5 ,1 ,1, 1)
        layout.addWidget(self.stopBitoviLabel, 6 ,0 ,1, 1)
        layout.addWidget(self.stopBitovi, 6 ,1 ,1, 1)
        self.setLayout(layout)

        self.tipRS232veze.currentIndexChanged.connect(self.promjena_tipa_veze)

    def promjena_tipa_veze(self, x):
        tip = self.tipRS232veze.currentText()
        if tip == 'Hessen':
            self.brzina.setCurrentIndex(self.brzina.findText('1200'))
            self.brojBitova.setCurrentIndex(self.brojBitova.findText('7'))
            self.stopBitovi.setCurrentIndex(self.stopBitovi.findText('2'))
            self.paritet.setCurrentIndex(self.paritet.findText('even'))
        elif tip == 'Standard':
            self.brzina.setCurrentIndex(self.brzina.findText('19200'))
            self.brojBitova.setCurrentIndex(self.brojBitova.findText('8'))
            self.stopBitovi.setCurrentIndex(self.stopBitovi.findText('1'))
            self.paritet.setCurrentIndex(self.paritet.findText('none'))
        else:
            pass


    def setupLayout(self, veza):
        if veza == 'TCP':
            self.ipAddressLabel.setVisible(True)
            self.ipAddress.setVisible(True)
            self.tipRS232vezeLabel.setVisible(False)
            self.tipRS232veze.setVisible(False)
            self.portLabel.setVisible(True)
            self.port.setVisible(True)
            self.brzinaLabel.setVisible(False)
            self.brzina.setVisible(False)
            self.paritetLabel.setVisible(False)
            self.paritet.setVisible(False)
            self.brojBitovaLabel.setVisible(False)
            self.brojBitova.setVisible(False)
            self.stopBitoviLabel.setVisible(False)
            self.stopBitovi.setVisible(False)
        elif veza == 'RS-232':
            self.ipAddressLabel.setVisible(False)
            self.ipAddress.setVisible(False)
            self.tipRS232vezeLabel.setVisible(True)
            self.tipRS232veze.setVisible(True)
            self.portLabel.setVisible(True)
            self.port.setVisible(True)
            self.brzinaLabel.setVisible(True)
            self.brzina.setVisible(True)
            self.paritetLabel.setVisible(True)
            self.paritet.setVisible(True)
            self.brojBitovaLabel.setVisible(True)
            self.brojBitova.setVisible(True)
            self.stopBitoviLabel.setVisible(True)
            self.stopBitovi.setVisible(True)
        else:
            pass

    def get_postavke(self):
        veza = self.wizard().izborVeze.izabranaVeza
        uredjaj = self.wizard().izborUredjaja.izabraniUredjaj

        self.postavkeProtokola['uredjaj'] = uredjaj
        self.postavkeProtokola['veza'] = veza
        if veza == 'TCP':
            self.postavkeProtokola['ip'] = self.ipAddress.text()
            self.postavkeProtokola['port'] = self.port.currentText()
        elif veza == 'RS-232':
            self.postavkeProtokola['port'] = self.port.currentText()
            self.postavkeProtokola['brzina'] = int(self.brzina.currentText())
            self.postavkeProtokola['paritet'] = self.paritet.currentText()
            self.postavkeProtokola['brojBitova'] = int(self.brojBitova.currentText())
            self.postavkeProtokola['stopBitovi'] = int(self.stopBitovi.currentText())
        else:
            pass
        return self.postavkeProtokola

    def initializePage(self):
        veza = self.wizard().izborVeze.izabranaVeza
        self.setupLayout(veza)
        self.tipRS232veze.currentIndexChanged.emit(0)

    def cleanupPage(self):
        self.ipAddressLabel.setVisible(True)
        self.ipAddress.setVisible(True)
        self.tipRS232vezeLabel.setVisible(True)
        self.tipRS232veze.setVisible(True)
        self.portLabel.setVisible(True)
        self.port.setVisible(True)
        self.brzinaLabel.setVisible(True)
        self.brzina.setVisible(True)
        self.paritetLabel.setVisible(True)
        self.paritet.setVisible(True)
        self.brojBitovaLabel.setVisible(True)
        self.brojBitova.setVisible(True)
        self.stopBitoviLabel.setVisible(True)
        self.stopBitovi.setVisible(True)

    def validatePage(self):
        veza = self.wizard().izborVeze.izabranaVeza
        if veza == 'TCP':
            try:
                value = self.ipAddress.text()
                #fail u slucaju neispravne ip adrese (IPv4 i IPv6)
                ipaddress.ip_address(str(value))
            except ValueError as err:
                logging.error(str(err), exc_info=True)
                QtGui.QMessageBox.information(self, 'Pogreska', 'Neispravna ip adresa')
                return False
        if veza == 'RS-232':
            try:
                PARITET = {'none':serial.PARITY_NONE,
                           'odd':serial.PARITY_ODD,
                           'even':serial.PARITY_EVEN,
                           'mark':serial.PARITY_MARK,
                           'space':serial.PARITY_SPACE}
                #pokusaj otvaranja veze
                ser = serial.Serial(port=self.port.currentText(),
                                    baudrate=int(self.brzina.currentText()),
                                    parity=PARITET[self.paritet.currentText()],
                                    bytesize=int(self.brojBitova.currentText()),
                                    stopbits=int(self.stopBitovi.currentText()))
                ser.close()
            except Exception as err:
                logging.error(str(err), exc_info=True)
                QtGui.QMessageBox.information(self, 'Pogreska', 'Spajanje preko RS-232 porta nije usjelo. Provjerite postavke.')
                return False
        return True
