#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 10:55:19 2015

@author: DHMZ-Milic

ideja:
1. napravi objekt koji zna slagati report
2. tom objektu prosljedi (metodi generiraj_report):
    -ime buduceg filea kao string (.pdf)
    -dictionary sa podacima koji se trebaju upisati u report

u testu koristim mock mapu i objekte koji su slicni ili identicni objektima u aplikaciji

ako se program pokrene samostalno... generirati ce pdf file u istom folderu.

#TODO!
-fontove i slike prebaciti u neki drugi folder?
-napraviti dijalog za pokretanje report generatora
"""

import logging
import numpy as np
import pandas as pd

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER

class ReportGenerator(object):
    """
    klasa zaduzena za stvaranje pdf reporta
    """
    def __init__(self):
        """
        postavke za report, fontovi isl...
        """
        PAGE_WIDTH, PAGE_HEIGHT = A4

        pdfmetrics.registerFont(TTFont('FreeSans', './freefont-20120503/FreeSans.ttf'))
        pdfmetrics.registerFont(TTFont('FreeSansBold', './freefont-20120503/FreeSansBold.ttf'))
        pdfmetrics.registerFont(TTFont('FreeSansBoldOblique', './freefont-20120503/FreeSansBoldOblique.ttf'))
        pdfmetrics.registerFont(TTFont('FreeSansOblique', './freefont-20120503/FreeSansOblique.ttf'))

    def generate_paragraph_style(self, font='FreeSans', align=TA_LEFT, size=10):
        """
        Metoda generira stil paragrafa. Default je: arial, left aligned, size 10
        """
        style = getSampleStyleSheet()
        stil = style['BodyText']
        stil.alignment = align
        stil.fontName = font
        stil.fontSize = size
        return stil

    def generiraj_header_tablicu(self, argmap=None, stranica=1, total=2):
        """
        generiranje tablice sa logotipom
        """
        if argmap == None:
            argmap = {}

        stil1 = self.generate_paragraph_style(align=TA_CENTER, size=11)
        stil2 = self.generate_paragraph_style(font='FreeSansBold', align=TA_CENTER, size=14)
        stil3 = self.generate_paragraph_style(align=TA_CENTER, size=10)
        stil4 = self.generate_paragraph_style(font='FreeSansBold', align=TA_CENTER, size=12)
        stil5 = self.generate_paragraph_style(font='FreeSansBold', align=TA_CENTER, size=10)

        #defaultne vrijednosti polja iz mape - isti kljuc je string unutar []
        stranica = str(stranica)
        total = str(total)
        norma = '[norma]'
        broj_obrasca = '[broj_obrasca]'
        revizija = '[revizija]'

        try:
            norma = argmap['norma']
            broj_obrasca = argmap['broj_obrasca']
            revizija = argmap['revizija']
        except LookupError as err:
            logging.error(str(err), exc_info=True)
            pass

        logotip = Image('logo.png')
        logotip.drawHeight = 0.75*inch*1.25
        logotip.drawWidth = 0.75*inch

        a2 = Paragraph('Laboratorij za istraživanje kvalitete zraka', stil1)
        a3 = Paragraph('OBRAZAC', stil2)
        a4 = Paragraph('Ozn', stil1)
        a5 = Paragraph(broj_obrasca, stil3)
        b3 = Paragraph('Terensko ispitivanje mjernog uređaja prema:', stil4)
        b4 = Paragraph('Rev', stil1)
        b5 = Paragraph(revizija, stil3)
        c3 = Paragraph(norma, stil5)
        c4 = Paragraph('Str', stil1)
        c5 = Paragraph("".join([stranica, '/', total]), stil3)

        layout_tablice = [
            [logotip, a2, a3, a4, a5],
            ['', '', b3, b4, b5],
            ['', '', c3, c4, c5]]

        stil_tablice = TableStyle(
            [
            ('SPAN', (0, 0), (0, -1)),
            ('SPAN', (1, 0), (1, -1)),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ])

        sirina_stupaca = [0.75*inch, 1.25*inch, 3*inch, 0.75*inch, 1*inch]

        tablica = Table(layout_tablice,
                        colWidths=sirina_stupaca)

        tablica.setStyle(stil_tablice)

        return tablica

    def generiraj_tablicu_podataka_o_uredjaju(self, argmap=None):
        """
        tablica sa podacima o lokaciji, tipu uredjaja, broj izvjesca...
        """
        if argmap == None:
            argmap = {}

        stil1 = self.generate_paragraph_style()
        stil2 = self.generate_paragraph_style(font='FreeSansBold')

        #defaultne vrijednosti polja iz mape - isti kljuc je string unutar []
        oznaka_izvjesca = '[oznaka_izvjesca]'
        lokacija = '[lokacija]'
        proizvodjac = '[proizvodjac]'
        model = '[model]'
        tvornicka_oznaka = '[tvornicka_oznaka]'
        datum_umjeravanja = '[datum_umjeravanja]'
        mjerno_podrucje = '[mjerno_podrucje]'

        try:
            oznaka_izvjesca = argmap['oznaka_izvjesca']
            lokacija = argmap['lokacija']
            proizvodjac = argmap['proizvodjac']
            model = argmap['model']
            tvornicka_oznaka = argmap['tvornicka_oznaka']
            datum_umjeravanja = argmap['datum_umjeravanja']
            mjerno_podrucje = argmap['mjerno_podrucje']
        except LookupError as err:
            logging.error(str(err), exc_info=True)
            pass

        a1 = Paragraph('OZNAKA IZVJEŠĆA:', stil2)
        a2 = Paragraph(oznaka_izvjesca, stil1)
        b1 = Paragraph('Lokacija:', stil2)
        b2 = Paragraph(lokacija, stil1)
        c1 = Paragraph('Proizvođač:', stil2)
        c2 = Paragraph(proizvodjac, stil1)
        c3 = Paragraph('Model:', stil2)
        c4 = Paragraph(model, stil1)
        d1 = Paragraph('Tvornička oznaka:', stil2)
        d2 = Paragraph(tvornicka_oznaka, stil1)
        e1 = Paragraph('Datum umjeravanja:', stil2)
        e2 = Paragraph(datum_umjeravanja, stil1)
        f1 = Paragraph('Mjerno područje:', stil2)
        f2 = Paragraph(mjerno_podrucje, stil1)

        layout_tablice = [
            [a1, a2, '', ''],
            ['', '', '', ''],
            [b1, b2, '', ''],
            [c1, c2, c3, c4],
            [d1, d2, '', ''],
            [e1, e2, '', ''],
            [f1, f2, '', '']]

        stil_tablice = TableStyle(
            [
            ('SPAN', (1, 0), (-1, 0)),
            ('SPAN', (0, 1), (-1, 1)),
            ('SPAN', (1, 2), (-1, 2)),
            ('SPAN', (1, 4), (-1, 4)),
            ('SPAN', (1, 5), (-1, 5)),
            ('SPAN', (1, 6), (-1, 6)),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ])

        sirina_stupaca = [1.6875*inch, 1.6875*inch, 1.6875*inch, 1.6875*inch]

        tablica = Table(layout_tablice,
                        colWidths=sirina_stupaca)

        tablica.setStyle(stil_tablice)

        return tablica

    def generiraj_crm_tablicu(self, argmap=None):
        """
        tablica sa podacima o certificiranom referentnom materijalu
        """
        if argmap == None:
            argmap = {}

        stil1 = self.generate_paragraph_style(font='FreeSansBold', align=TA_CENTER)
        stil2 = self.generate_paragraph_style(font='FreeSansBold')
        stil3 = self.generate_paragraph_style()

        #defaultne vrijednosti polja iz mape - isti kljuc je string unutar []
        crm_vrsta = '[crm_vrsta]'
        crm_C = '[crm_C]'
        crm_U = '[crm_U]'

        try:
            crm_vrsta = argmap['crm_vrsta']
            crm_C = argmap['crm_C']
            crm_U = argmap['crm_U']
        except LookupError as err:
            logging.error(str(err), exc_info=True)
            pass

        a1 = Paragraph('Certificirani referentni materijal', stil1)
        b1 = Paragraph('Vrsta:', stil2)
        b2 = Paragraph(crm_vrsta, stil3)
        b3 = Paragraph('Sljedivost:', stil2)
        c1 = Paragraph('C()=', stil2)
        c2 = Paragraph(crm_C, stil3)
        c3 = Paragraph('U(k=2)=', stil2)
        c4 = Paragraph(crm_U, stil3)

        layout_tablice = [
            [a1, '', '', ''],
            [b1, b2, b3, ''],
            [c1, c2, c3, c4]]

        stil_tablice = TableStyle(
            [
            ('SPAN', (0, 0), (-1, 0)),
            ('SPAN', (2, 1), (-1, 1)),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ])

        sirina_stupaca = [1.1875*inch, 2.1875*inch, 1.1875*inch, 2.1875*inch]

        tablica = Table(layout_tablice,
                        colWidths=sirina_stupaca)

        tablica.setStyle(stil_tablice)

        return tablica

    def generiraj_tablicu_kalibracijske_jedinice(self, argmap=None):
        """
        tablica sa podacima o certificiranom referentnom materijalu
        """
        if argmap == None:
            argmap = {}

        stil1 = self.generate_paragraph_style(font='FreeSansBold', align=TA_CENTER)
        stil2 = self.generate_paragraph_style(font='FreeSansBold')
        stil3 = self.generate_paragraph_style()

        #defaultne vrijednosti polja iz mape - isti kljuc je string unutar []
        kalibracijska_jedinica_proizvodjac = '[kalibracijska_jedinica_proizvodjac]'
        kalibracijska_jedinica_model = '[kalibracijska_jedinica_model]'
        kalibracijska_jedinica_sljedivost = '[kalibracijska_jedinica_sljedivost]'

        try:
            kalibracijska_jedinica_proizvodjac = argmap['kalibracijska_jedinica_proizvodjac']
            kalibracijska_jedinica_model = argmap['kalibracijska_jedinica_model']
            kalibracijska_jedinica_sljedivost = argmap['kalibracijska_jedinica_sljedivost']
        except LookupError as err:
            logging.error(str(err), exc_info=True)
            pass

        a1 = Paragraph('Kalibracijska jedinica', stil1)
        b1 = Paragraph('Proizvođač:', stil2)
        b2 = Paragraph(kalibracijska_jedinica_proizvodjac, stil3)
        b3 = Paragraph('Model:', stil2)
        b4 = Paragraph(kalibracijska_jedinica_model, stil3)
        c1 = Paragraph('Sljedivost:', stil2)
        c2 = Paragraph(kalibracijska_jedinica_sljedivost, stil3)

        layout_tablice = [
            [a1, '', '', ''],
            [b1, b2, b3, b4],
            [c1, c2, '', '']]

        stil_tablice = TableStyle(
            [
            ('SPAN', (0, 0), (-1, 0)),
            ('SPAN', (1, 2), (-1, 2)),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ])

        sirina_stupaca = [1.1875*inch, 2.1875*inch, 1.1875*inch, 2.1875*inch]

        tablica = Table(layout_tablice,
                        colWidths=sirina_stupaca)

        tablica.setStyle(stil_tablice)

        return tablica

    def generiraj_tablicu_izvora_cistog_zraka(self, argmap=None):
        """
        tablica sa podacima o certificiranom referentnom materijalu
        """
        if argmap == None:
            argmap = {}

        stil1 = self.generate_paragraph_style(font='FreeSansBold', align=TA_CENTER)
        stil2 = self.generate_paragraph_style(font='FreeSansBold')
        stil3 = self.generate_paragraph_style()

        #defaultne vrijednosti polja iz mape - isti kljuc je string unutar []
        cisti_zrak_proizvodjac = '[cisti_zrak_proizvodjac]'
        cisti_zrak_model = '[cisti_zrak_model]'
        cisti_zrak_U = '[cisti_zrak_U]'

        try:
            cisti_zrak_proizvodjac = argmap['cisti_zrak_proizvodjac']
            cisti_zrak_model = argmap['cisti_zrak_model']
            cisti_zrak_U = argmap['cisti_zrak_U']
        except LookupError as err:
            logging.error(str(err), exc_info=True)
            pass

        a1 = Paragraph('Izvor čistog zraka', stil1)
        b1 = Paragraph('Proizvođač:', stil2)
        b2 = Paragraph(cisti_zrak_proizvodjac, stil3)
        b3 = Paragraph('Model:', stil2)
        b4 = Paragraph(cisti_zrak_model, stil3)
        c1 = Paragraph('U(k=2)=', stil2)
        c2 = Paragraph(cisti_zrak_U, stil3)

        layout_tablice = [
            [a1, '', '', ''],
            [b1, b2, b3, b4],
            [c1, c2, '', '']]

        stil_tablice = TableStyle(
            [
            ('SPAN', (0, 0), (-1, 0)),
            ('SPAN', (1, 2), (-1, 2)),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ])

        sirina_stupaca = [1.1875*inch, 2.1875*inch, 1.1875*inch, 2.1875*inch]

        tablica = Table(layout_tablice,
                        colWidths=sirina_stupaca)

        tablica.setStyle(stil_tablice)

        return tablica

    def generiraj_tablicu_vremena_pocetka_i_kraja_umjeravanja(self, argmap=None):
        """
        generiranje tablice za vrijeme umjeravanja
        """
        if argmap == None:
            argmap = {}

        stil1 = self.generate_paragraph_style(font='FreeSansBold')
        stil2 = self.generate_paragraph_style()

        #defaultne vrijednosti polja iz mape - isti kljuc je string unutar []
        vrijeme_pocetka_umjeravanja = '[vrijeme_pocetka_umjeravanja]'
        vrijeme_kraja_umjeravanja = '[vrijeme_kraja_umjeravanja]'

        try:
            vrijeme_pocetka_umjeravanja = argmap['vrijeme_pocetka_umjeravanja']
            vrijeme_kraja_umjeravanja = argmap['vrijeme_kraja_umjeravanja']
        except LookupError as err:
            logging.error(str(err), exc_info=True)
            pass

        a1 = Paragraph('Vrijeme početka umjeravanja:', stil1)
        a2 = Paragraph(vrijeme_pocetka_umjeravanja, stil2)
        b1 = Paragraph('Vrijeme kraja umjeravanja:', stil1)
        b2 = Paragraph(vrijeme_kraja_umjeravanja, stil2)

        layout_tablice = [
            [a1, a2],
            [b1, b2]]

        stil_tablice = TableStyle(
            [
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ])

        sirina_stupaca = [2.25*inch, 4.5*inch]

        tablica = Table(layout_tablice,
                        colWidths=sirina_stupaca)

        tablica.setStyle(stil_tablice)

        return tablica

    def generiraj_tablicu_okolisnih_uvijeta_tjekom_provjere(self, argmap=None):
        """
        tablica okolisnih uvijeta tjekom provjere
        """
        if argmap == None:
            argmap = {}

        stil1 = self.generate_paragraph_style(font='FreeSansBold', align=TA_CENTER)
        stil2 = self.generate_paragraph_style(font='FreeSansBold')
        stil3 = self.generate_paragraph_style()

        #defaultne vrijednosti polja iz mape - isti kljuc je string unutar []
        temperatura = '[temperatura]'
        vlaga = '[vlaga]'
        tlak_zraka = '[tlak_zraka]'
        napomena = '[napomena]'

        try:
            temperatura = argmap['temperatura']
            vlaga = argmap['vlaga']
            tlak_zraka = argmap['tlak_zraka']
            napomena = argmap['napomena']
        except LookupError as err:
            logging.error(str(err), exc_info=True)
            pass

        a1 = Paragraph('Okolišni uvijeti tjekom provjere', stil1)
        b1 = Paragraph('Temperatura:', stil2)
        b2 = Paragraph(temperatura, stil3)
        b3 = Paragraph('°C', stil3)
        c1 = Paragraph('Relativna vlaga:', stil2)
        c2 = Paragraph(vlaga, stil3)
        c3 = Paragraph('%', stil3)
        d1 = Paragraph('Tlak zraka:', stil2)
        d2 = Paragraph(tlak_zraka, stil3)
        d3 = Paragraph('hPa', stil3)
        e1 = Paragraph('Napomena:', stil2)
        f1 = Paragraph(napomena, stil3)

        layout_tablice = [
            [a1, '', ''],
            [b1, b2, b3],
            [c1, c2, c3],
            [d1, d2, d3],
            [e1, '', ''],
            [f1, '', '']]

        stil_tablice = TableStyle(
            [
            ('SPAN', (0, 0), (-1, 0)),
            ('SPAN', (0, 4), (-1, 4)),
            ('SPAN', (0, 5), (-1, 5)),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ])

        sirina_stupaca = [2.5*inch, 2.5*inch, 1.75*inch]
        visina_stupaca = [0.25*inch, 0.25*inch, 0.25*inch, 0.25*inch, 0.25*inch, 0.75*inch]

        tablica = Table(layout_tablice,
                        colWidths=sirina_stupaca,
                        rowHeights=visina_stupaca)

        tablica.setStyle(stil_tablice)

        return tablica

    def generiraj_tablicu_datum_mjeritelj_voditelj(self):
        """
        tablica za upisivanje mjeritelja, voditelja i datuma
        """
        stil = self.generate_paragraph_style(align=TA_CENTER)

        a1 = Paragraph('Datum', stil)
        a2 = Paragraph('Mjeritelj', stil)
        a3 = Paragraph('Voditelj', stil)
        b1 = Paragraph('', stil)

        layout_tablice = [
            [a1, a2, a3],
            [b1, b1, b1]]

        stil_tablice = TableStyle(
            [
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ])

        sirina_stupaca = [2.25*inch, 2.25*inch, 2.25*inch]
        visina_stupaca = [0.25*inch, 0.5*inch]

        tablica = Table(layout_tablice,
                        colWidths=sirina_stupaca,
                        rowHeights=visina_stupaca)

        tablica.setStyle(stil_tablice)

        return tablica

    def generiraj_tablicu_ocjene_umjeravanja(self, argmap=None):
        """
        tablica ocjene umjeravanja
        """
        if argmap == None:
            argmap = {}

        stil1 = self.generate_paragraph_style(font='FreeSansBold', align=TA_CENTER)
        stil2 = self.generate_paragraph_style(font='FreeSansBold')

        ocjena_umjeravanja = False

        try:
            ocjena_umjeravanja = argmap['ocjena_umjeravanja']
        except LookupError as err:
            logging.error(str(err), exc_info=True)
            pass

        a1 = Paragraph('REZULTATI ISPITIVANJA:', stil1)
        b1 = Paragraph('Ocjena:', stil2)
        if ocjena_umjeravanja:
            b2 = Paragraph('Mjerni uređaj ZADOVOLJAVA uvjete norme', stil2)
        else:
            b2 = Paragraph('Mjerni uređaj NE ZADOVOLJAVA uvjete norme', stil2)

        layout_tablice = [
            [a1, ''],
            [b1, b2]]

        stil_tablice = TableStyle(
            [
            ('SPAN', (0, 0), (-1, 0)),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ])

        sirina_stupaca = [1.75*inch, 5*inch]

        tablica = Table(layout_tablice,
                        colWidths=sirina_stupaca)

        tablica.setStyle(stil_tablice)

        return tablica

    def generiraj_tablicu_rezultata_umjeravanja(self, argmap=None):
        """
        izrada tablice sa parametrima umjeravanja, cref, U, sr....
        """
        if argmap == None:
            argmap = {}

        stil1 = self.generate_paragraph_style(align=TA_CENTER)

        jedinica = '[mjerna_jedinica]'
        frejm = pd.DataFrame(index=list(range(5)), columns=list(range(6)))

        try:
            frejm = argmap['rezultati_umjeravanja']
            jedinica = argmap['mjerna_jedinica']
        except LookupError as err:
            logging.error(str(err), exc_info=True)
            pass

        h0 = Paragraph('N:', stil1)
        h1 = Paragraph('cref ({0})'.format(str(jedinica)), stil1)
        h2 = Paragraph('U* ({0})'.format(str(jedinica)), stil1)
        h3 = Paragraph('c ({0})'.format(str(jedinica)), stil1)
        h4 = Paragraph('\u0394 ({0})'.format(str(jedinica)), stil1)
        h5 = Paragraph('sr ({0})'.format(str(jedinica)), stil1)
        h6 = Paragraph('Odstupanje od linearnosti', stil1)

        headeri = [h0, h1, h2, h3, h4, h5, h6]

        rows = [[str(a+1)] for a in range(len(frejm))] #nested lista
        for row in range(len(rows)):
            for col in range(6):
                value = frejm.iloc[row, col]
                value = round(value, 2)
                if np.isnan(value):
                    value = ''
                value = str(value)
                if col == 5:
                    if frejm.iloc[row, 0] == 0:
                        value = value + ' ({0})'.format(jedinica)
                    elif value != '':
                        value = value + ' (%)'
                value = Paragraph(value, stil1)
                rows[row].append(value)

        layout_tablice = []
        layout_tablice.append(headeri)
        for row in rows:
            layout_tablice.append(row)

        stil_tablice = TableStyle(
            [
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ])

        s = (1.05)*inch
        sirina_stupaca = [0.45*inch, s, s, s, s, s, s]

        tablica = Table(layout_tablice,
                        colWidths=sirina_stupaca)

        tablica.setStyle(stil_tablice)

        return tablica

    def generiraj_tablicu_kriterija(self, argmap=None):
        """
        metoda generira tablicu sa kriterijima umjeravanja
        7stupaca (n + bitni stupci)
        ? redaka (header + 2 do 7 redaka)
        """
        if argmap == None:
            argmap = {}

        stil1 = self.generate_paragraph_style(align=TA_CENTER)
        stil2 = self.generate_paragraph_style()

        parametri = []
        try:
            parametri = argmap['parametri_umjeravanja']
        except LookupError as err:
            logging.error(str(err), exc_info=True)
            pass

        a2 = Paragraph('Naziv kriterija', stil1)
        a3 = Paragraph('Točka norme', stil1)
        a4 = Paragraph('Rezultati', stil1)
        a6 = Paragraph('Uvijeti prihvatljivosti', stil1)
        a7 = Paragraph('Ispunjeno', stil1)

        headeri = ['', a2, a3, a4, '', a6, a7]

        layout_tablice = []
        layout_tablice.append(headeri)

        for i in range(len(parametri)):
            red = []
            red.append(Paragraph(str(i+1), stil1))
            for j in range(6): #elementi reda iz parametara (bez rednog broja)
                if j == 0:
                    red.append(Paragraph(parametri[i][j], stil2))
                else:
                    red.append(Paragraph(parametri[i][j], stil1))
            layout_tablice.append(red)

        stil_tablice = TableStyle(
            [
            ('SPAN', (3, 0), (4, 0)),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ])

        sirina_stupaca = [0.3*inch,
                          2.125*inch,
                          0.7*inch,
                          0.55*inch,
                          0.55*inch,
                          1.725*inch,
                          0.8*inch]

        visina_stupaca = [0.5*inch for i in range(len(parametri)+1)]

        tablica = Table(layout_tablice,
                        colWidths=sirina_stupaca,
                        rowHeights=visina_stupaca)

        tablica.setStyle(stil_tablice)

        return tablica

    def generiraj_tablicu_funkcije_prilagodbe(self, argmap=None):
        """
        generiranje tablice sa koefiicjentima pravca prilagodbe
        """
        if argmap == None:
            argmap = {}

        stil1 = self.generate_paragraph_style(font='FreeSansBold', align=TA_CENTER)
        stil2 = self.generate_paragraph_style(align=TA_CENTER)
        stil3 = self.generate_paragraph_style(font='FreeSansBold')
        stil4 = self.generate_paragraph_style()

        prilagodbaA = ''
        prilagodbaB = ''

        try:
            prilagodbaA = argmap['prilagodbaA']
            prilagodbaB = argmap['prilagodbaB']
        except LookupError as err:
            logging.error(str(err), exc_info=True)
            pass

        a1 = Paragraph('FUNKCIJA PRILAGODBE', stil1)
        b1 = Paragraph('C = A * Cm + b', stil2)
        c1 = Paragraph('A=', stil3)
        c2 = Paragraph(prilagodbaA, stil4)
        c3 = Paragraph('B=', stil3)
        c4 = Paragraph(prilagodbaB, stil4)

        layout_tablice = [
            [a1, '', '', ''],
            [b1, '', '', ''],
            [c1, c2, c3, c4]]

        stil_tablice = TableStyle(
            [
            ('SPAN', (0, 0), (-1, 0)),
            ('SPAN', (0, 1), (-1, 1)),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ])

        sirina_stupaca = [0.5*inch, 0.5*inch, 0.5*inch, 0.5*inch]

        tablica = Table(layout_tablice,
                        colWidths=sirina_stupaca,
                        hAlign='LEFT')

        tablica.setStyle(stil_tablice)

        return tablica

    def generiraj_report(self, ime, argmap):
        """
        metoda za generiranje izvjestaja.

        ime je naziv (path) buduceg pdf filea  (string)
        argmap je dict podataka koji ispunjavaju report (podaci...)
        """
        #TODO! vidi mapu na kraju za potrebna polja
        #pdf templata
        doc = SimpleDocTemplate(ime,
                                pagesize=A4,
                                topMargin=0.4*inch,
                                bottomMargin=0.4*inch,
                                allowSplitting=0)

        #lista flowable elemenata za report
        parts = []

        razmak = Spacer(1, 0.15*inch)

        head1 = self.generiraj_header_tablicu(argmap=argmap, stranica=1)
        parts.append(head1)

        parts.append(razmak)

        tabla1 = self.generiraj_tablicu_podataka_o_uredjaju(argmap=argmap)
        parts.append(tabla1)

        parts.append(razmak)

        tabla2 = self.generiraj_crm_tablicu(argmap=argmap)
        parts.append(tabla2)

        parts.append(razmak)

        tabla3 = self.generiraj_tablicu_kalibracijske_jedinice(argmap=argmap)
        parts.append(tabla3)

        parts.append(razmak)

        tabla4 = self.generiraj_tablicu_izvora_cistog_zraka(argmap=argmap)
        parts.append(tabla4)

        parts.append(razmak)

        tabla5 = self.generiraj_tablicu_vremena_pocetka_i_kraja_umjeravanja(argmap=argmap)
        parts.append(tabla5)

        parts.append(razmak)

        tabla6 = self.generiraj_tablicu_okolisnih_uvijeta_tjekom_provjere(argmap=argmap)
        parts.append(tabla6)

        parts.append(razmak)

        tabla7 = self.generiraj_tablicu_datum_mjeritelj_voditelj()
        parts.append(tabla7)

        #kraj prve stranice... page break
        parts.append(PageBreak())

        head2 = self.generiraj_header_tablicu(argmap=argmap, stranica=2)
        parts.append(head2)

        parts.append(razmak)
        parts.append(razmak)

        tabla8 = self.generiraj_tablicu_ocjene_umjeravanja(argmap=argmap)
        parts.append(tabla8)

        parts.append(razmak)
        parts.append(razmak)

        tabla9 = self.generiraj_tablicu_rezultata_umjeravanja(argmap=argmap)
        parts.append(tabla9)

        annotation1_stil = self.generate_paragraph_style(font='FreeSansOblique', size=8)
        annotation1 = Paragraph('* Proširena mjerna nesigurnost uz k=2 izračunata prema RU-5.5.1.11', annotation1_stil)
        parts.append(annotation1)

        parts.append(razmak)

        tabla10 = self.generiraj_tablicu_kriterija(argmap=argmap)
        parts.append(tabla10)

        parts.append(razmak)

        tabla11 = self.generiraj_tablicu_funkcije_prilagodbe(argmap=argmap)
        parts.append(tabla11)

        parts.append(razmak)

        annotation2_stil = self.generate_paragraph_style()
        annotation2 = Paragraph('Kraj ispitnog izvješća', annotation2_stil)
        parts.append(annotation2)

        #zavrsna naredba za konstrukciju dokumenta
        doc.build(parts)

if __name__ == '__main__':
    ime = 'example_report.pdf'
    import random
    c1 = pd.Series([random.randint(1,10) for i in range(8)])
    c2 = pd.Series([random.randint(11,20) for i in range(8)])
    c3 = pd.Series([random.randint(21,30) for i in range(8)])
    c4 = pd.Series([random.randint(31,40) for i in range(8)])
    c5 = pd.Series([random.randint(41,50) for i in range(8)])
    c6 = pd.Series([random.randint(51,60) for i in range(8)])
    mockfrejm = pd.DataFrame({'c1':c1, 'c2':c2, 'c3':c3, 'c4':c4, 'c5':c5, 'c6':c6})

    p1 = ['Ponovljivost standardne devijacije u nuli', '9.5.1', 'S<sub>r,z</sub> =', '0.2', '< 1.0 nmol/mol', 'Da']
    p2 = ['Ponovljivost standardne devijacije pri koncentraciji ct', '9.5.1', 'S<sub>r,ct</sub> =', '1.7', '< 1.5 nmol/mol', 'Ne']
    p3 = ['Odstupanje od linearnosti u nuli', '9.6.2', 'r<sub>z</sub> =', '1.4', '≤ 5.0 nmol/mol', 'Da']
    p4 = ['Maksimalno relativno odstupanje od linearnosti', '9.6.2', 'r<sub>z,rel</sub> =', '2.1', '≤ 4.0 %', 'Da']
    p5 = ['Efikasnost konvertera dušikovih oksida', '9.6.2', 'E<sub>c</sub> =', '50', '95 % ≤ E<sub>c</sub> ≤ 105 %', 'Ne']
    p6 = ['Nešto bezveze radi testiranja', '1.1.1', 'N<sup>o</sup> =', '32.1', '≤ 12.0 %', 'Ne']


    mockparametri = [p1, p2, p3, p4, p5, p6]

    mapa = {
        'norma':'HRN EN 14212:2012 Vanjski zrak – Standardna metoda za mjerenje koncentracije sumporova dioksida u zraku ultraljubičastom fluorescencijom',
        'broj_obrasca':'OB 5.10.0.0-1',
        'revizija':'1',
        'oznaka_izvjesca':'neka oznaka izvješća',
        'lokacija':'nearby...',
        'proizvodjac':'neki proizvođač',
        'model':'neki model',
        'tvornicka_oznaka':'neka oznaka',
        'datum_umjeravanja':'danas',
        'mjerno_podrucje':'od x do y',
        'crm_vrsta':'Boca pod tlakom NO u N2 ili nesto slicno',
        'crm_C':'10000 nekih jedinica',
        'crm_U':'23%',
        'kalibracijska_jedinica_proizvodjac':'proizvođač kalibracijske jedinice',
        'kalibracijska_jedinica_model':'model kalibracijske jedinice',
        'kalibracijska_jedinica_sljedivost':'sss, wewe, ssss',
        'cisti_zrak_proizvodjac':'proizvođač cisti zrak',
        'cisti_zrak_model':'model cisti zrak',
        'cisti_zrak_U':'12 neke mjerne jedinice',
        'vrijeme_pocetka_umjeravanja': 'start umjeravanja',
        'vrijeme_kraja_umjeravanja':'kraj umjeravanja',
        'temperatura':'temperatura',
        'vlaga':'vlaga',
        'tlak_zraka':'tlak zraka',
        'napomena':'napomena',
        'ocjena_umjeravanja':False,
        'rezultati_umjeravanja':mockfrejm,
        'mjerna_jedinica':'nmol/mol',
        'parametri_umjeravanja':mockparametri,
        'prilagodbaA':'1.05',
        'prilagodbaB':'0.12'
        }

    report = ReportGenerator()
    report.generiraj_report(ime, mapa)
