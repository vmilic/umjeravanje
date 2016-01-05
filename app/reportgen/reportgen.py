# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 09:07:26 2015

@author: DHMZ-Milic

1. napravi objekt koji zna slagati report
2. tom objektu prosljedi (metodi generiraj_report):
    -ime buduceg filea kao string (.pdf)
    -referencu na dokument
    -dict za rezultatima i testovima
"""
import numpy as np
import pandas as pd
import app.model.pomocne_funkcije as helperi

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4 #(8.3 / 11.7 inca)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

class ReportGenerator(object):
    """
    klasa zaduzena za stvaranje pdf reporta
    """
    def __init__(self):
        """
        postavke za report, fontovi isl...
        """
        self.dokument = None
        PAGE_WIDTH, PAGE_HEIGHT = A4
        try:
            pdfmetrics.registerFont(TTFont('FreeSans', './app/reportgen/freefont-20120503/FreeSans.ttf'))
            pdfmetrics.registerFont(TTFont('FreeSansBold', './app/reportgen/freefont-20120503/FreeSansBold.ttf'))
            pdfmetrics.registerFont(TTFont('FreeSansBoldOblique', './app/reportgen/freefont-20120503/FreeSansBoldOblique.ttf'))
            pdfmetrics.registerFont(TTFont('FreeSansOblique', './app/reportgen/freefont-20120503/FreeSansOblique.ttf'))
            self.logo = './app/reportgen/logo.png'
        except Exception:
            pdfmetrics.registerFont(TTFont('FreeSans', './freefont-20120503/FreeSans.ttf'))
            pdfmetrics.registerFont(TTFont('FreeSansBold', './freefont-20120503/FreeSansBold.ttf'))
            pdfmetrics.registerFont(TTFont('FreeSansBoldOblique', './freefont-20120503/FreeSansBoldOblique.ttf'))
            pdfmetrics.registerFont(TTFont('FreeSansOblique', './freefont-20120503/FreeSansOblique.ttf'))
            self.logo = 'logo.png'


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

    def generiraj_header_tablicu(self, stranica=1, total=3):
        """
        generiranje header tablice sa logotipom
        """
        stil1 = self.generate_paragraph_style(align=TA_CENTER, size=11)
        stil2 = self.generate_paragraph_style(font='FreeSansBold', align=TA_CENTER, size=14)
        stil3 = self.generate_paragraph_style(align=TA_CENTER, size=10)
        stil4 = self.generate_paragraph_style(font='FreeSansBold', align=TA_CENTER, size=12)
        stil5 = self.generate_paragraph_style(font='FreeSansBold', align=TA_CENTER, size=10)
        #defaultne vrijednosti polja iz mape - isti kljuc je string unutar []
        stranica = str(stranica)
        total = str(total)
        norma = self.dokument.get_norma()
        broj_obrasca = self.dokument.get_brojObrasca()
        revizija = self.dokument.get_revizija()
        #logo
        logotip = Image(self.logo)
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
        sirina_stupaca = [0.75*inch, 1*inch, 3.6*inch, 0.5*inch, 1.4*inch]
        visina_stupaca = [0.4*inch, None, None]
        tablica = Table(layout_tablice,
                        colWidths=sirina_stupaca,
                        rowHeights=visina_stupaca,
                        hAlign='LEFT')
        tablica.setStyle(stil_tablice)
        return tablica

    def generiraj_tablicu_podataka_o_uredjaju(self):
        """
        tablica sa podacima o lokaciji, tipu uredjaja, broj izvjesca...
        """
        stil1 = self.generate_paragraph_style()
        stil2 = self.generate_paragraph_style(font='FreeSansBold')
        oznaka_izvjesca = self.dokument.get_oznakaIzvjesca()
        lokacija = self.dokument.get_izabranaPostaja()
        proizvodjac = self.dokument.get_proizvodjacUredjaja()
        model = self.dokument.get_oznakaModelaUredjaja()
        tvornicka_oznaka = self.dokument.get_izabraniUredjaj()
        datum_umjeravanja = self.dokument.get_datumUmjeravanja()
        mjerna_jedinica = self.dokument.get_mjernaJedinica()
        zadani_opseg = self.dokument.get_opseg()
        popis = ['Od 0',
                 mjerna_jedinica,
                 'do',
                 str(zadani_opseg),
                 mjerna_jedinica]
        mjerno_podrucje = " ".join(popis)
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
        sirina_stupaca = [1.8125*inch, 1.8125*inch, 1.8125*inch, 1.8125*inch]
        tablica = Table(layout_tablice,
                        colWidths=sirina_stupaca,
                        hAlign='LEFT')
        tablica.setStyle(stil_tablice)
        return tablica

    def generiraj_crm_tablicu(self):
        """
        tablica sa podacima o certificiranom referentnom materijalu
        """
        stil1 = self.generate_paragraph_style(font='FreeSansBold', align=TA_CENTER)
        stil2 = self.generate_paragraph_style(font='FreeSansBold')
        stil3 = self.generate_paragraph_style()
        mjerna_jedinica = self.dokument.get_mjernaJedinica()
        crm_vrsta = self.dokument.get_izvorCRM()
        crm_C = " ".join([str(round(self.dokument.get_koncentracijaCRM(), 1)), mjerna_jedinica])
        crm_U = " ".join([str(round(self.dokument.get_sljedivostCRM(), 1)), '%'])
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
        sirina_stupaca = [1.3125*inch, 2.3125*inch, 1.3125*inch, 2.3125*inch]
        tablica = Table(layout_tablice,
                        colWidths=sirina_stupaca,
                        hAlign='LEFT')
        tablica.setStyle(stil_tablice)
        return tablica

    def generiraj_tablicu_kalibracijske_jedinice(self):
        """
        tablica sa podacima o kalibracijskoj jedinici
        """
        stil1 = self.generate_paragraph_style(font='FreeSansBold', align=TA_CENTER)
        stil2 = self.generate_paragraph_style(font='FreeSansBold')
        stil3 = self.generate_paragraph_style()
        kalibracijska_jedinica_proizvodjac = self.dokument.get_proizvodjacDilucija()
        kalibracijska_jedinica_model = self.dokument.get_izabranaDilucija()
        kalibracijska_jedinica_sljedivost = self.dokument.get_sljedivostDilucija()
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
        sirina_stupaca = [1.3125*inch, 2.3125*inch, 1.3125*inch, 2.3125*inch]
        tablica = Table(layout_tablice,
                        colWidths=sirina_stupaca,
                        hAlign='LEFT')
        tablica.setStyle(stil_tablice)
        return tablica

    def generiraj_tablicu_izvora_cistog_zraka(self):
        """
        tablica sa podacima o generatoru cistog zraka
        """
        stil1 = self.generate_paragraph_style(font='FreeSansBold', align=TA_CENTER)
        stil2 = self.generate_paragraph_style(font='FreeSansBold')
        stil3 = self.generate_paragraph_style()
        cisti_zrak_proizvodjac = self.dokument.get_proizvodjacZrak()
        cisti_zrak_model = self.dokument.get_izabraniZrak()
        mjerna_jedinica = self.dokument.get_mjernaJedinica()
        cisti_zrak_U = " ".join([str(round(self.dokument.get_sljedivostZrak(), 1)), mjerna_jedinica])
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
        sirina_stupaca = [1.3125*inch, 2.3125*inch, 1.3125*inch, 2.3125*inch]
        tablica = Table(layout_tablice,
                        colWidths=sirina_stupaca,
                        hAlign='LEFT')
        tablica.setStyle(stil_tablice)
        return tablica

    def generiraj_tablicu_vremena_pocetka_i_kraja_umjeravanja(self):
        """
        generiranje tablice za vrijeme pocetka i kraja umjeravanja
        """
        stil1 = self.generate_paragraph_style(font='FreeSansBold')
        stil2 = self.generate_paragraph_style()
        #problem... za koje mjerenje...
        listaPocetaka = []
        listaKrajeva = []
        for plin in self.rezultati:
            start, kraj = self.dokument.get_pocetak_i_kraj_umjeravanja(mjerenje=plin)
            if len(self.rezultati) > 1:
                start = " ".join([str(start), '(', str(plin), ')'])
                kraj = " ".join([str(kraj), '(', str(plin), ')'])
            else:
                start = str(start)
                kraj = str(kraj)
            listaPocetaka.append(start)
            listaKrajeva.append(kraj)
        if self.dokument.get_provjeraKonvertera():
            start, kraj = self.dokument.get_pocetak_i_kraj_umjeravanja(mjerenje='konverter')
            start = " ".join([str(start), '( konverter )'])
            kraj = " ".join([str(kraj), '( konverter )'])
            listaPocetaka.append(start)
            listaKrajeva.append(kraj)

        vrijeme_pocetka_umjeravanja = ", ".join(listaPocetaka)
        vrijeme_kraja_umjeravanja = ", ".join(listaKrajeva)
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
        sirina_stupaca = [2.25*inch, 5*inch]
        tablica = Table(layout_tablice,
                        colWidths=sirina_stupaca,
                        hAlign='LEFT')
        tablica.setStyle(stil_tablice)
        return tablica

    def generiraj_tablicu_okolisnih_uvijeta_tjekom_provjere(self):
        """
        tablica okolisnih uvijeta tjekom provjere
        """
        stil1 = self.generate_paragraph_style(font='FreeSansBold', align=TA_CENTER)
        stil2 = self.generate_paragraph_style(font='FreeSansBold')
        stil3 = self.generate_paragraph_style()
        temperatura = str(round(self.dokument.get_temperatura(), 1))
        vlaga = str(round(self.dokument.get_vlaga(), 1))
        tlak_zraka = str(round(self.dokument.get_tlak(), 1))
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
        layout_tablice = [
            [a1, '', ''],
            [b1, b2, b3],
            [c1, c2, c3],
            [d1, d2, d3]]
        stil_tablice = TableStyle(
            [
            ('SPAN', (0, 0), (-1, 0)),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ])
        sirina_stupaca = [2.7*inch, 2.7*inch, 1.85*inch]
        visina_stupaca = [0.25*inch, 0.25*inch, 0.25*inch, 0.25*inch]
        tablica = Table(layout_tablice,
                        colWidths=sirina_stupaca,
                        rowHeights=visina_stupaca,
                        hAlign='LEFT')
        tablica.setStyle(stil_tablice)
        return tablica

    def generiraj_tablicu_napomene(self):
        """Generiranje tablice za napomenu"""
        stil1 = self.generate_paragraph_style(font='FreeSansBold', align=TA_CENTER)
        stil3 = self.generate_paragraph_style()
        napomena = self.dokument.get_napomena()
        if len(napomena):
            a1 = Paragraph('Napomena', stil1)
            b1 = Paragraph(napomena, stil3)
            layout_tablice = [
                [a1],
                [b1]]
            stil_tablice = TableStyle(
                [
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
                ])
            sirina_stupaca = [7.25*inch]
            tablica = Table(layout_tablice,
                            colWidths=sirina_stupaca,
                            hAlign='LEFT')
            tablica.setStyle(stil_tablice)
            return tablica
        else:
            return None

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
        sirina_stupaca = [2.41*inch, 2.42*inch, 2.42*inch]
        visina_stupaca = [0.25*inch, 0.5*inch]
        tablica = Table(layout_tablice,
                        colWidths=sirina_stupaca,
                        rowHeights=visina_stupaca,
                        hAlign='LEFT')
        tablica.setStyle(stil_tablice)
        return tablica

    def generiraj_tablicu_ocjene_umjeravanja(self, zadovoljava='NE', komponenta=''):
        """
        tablica ocjene umjeravanja
        """
        stil1 = self.generate_paragraph_style(font='FreeSansBold', align=TA_CENTER)
        stil2 = self.generate_paragraph_style(font='FreeSansBold')
        naslov = " ".join(['REZULTATI ISPITIVANJA:', komponenta])
        a1 = Paragraph(naslov, stil1)
        b1 = Paragraph('Ocjena:', stil2)
        if zadovoljava == 'DA':
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
        sirina_stupaca = [1.75*inch, 5.5*inch]
        tablica = Table(layout_tablice,
                        colWidths=sirina_stupaca,
                        hAlign='CENTRE')
        tablica.setStyle(stil_tablice)
        return tablica

    def generiraj_tablicu_rezultata_umjeravanja(self, frejm=None):
        """
        izrada tablice sa parametrima umjeravanja, cref, U, sr....
        """
        linearnost = True
        stil1 = self.generate_paragraph_style(align=TA_CENTER)
        jedinica = self.dokument.get_mjernaJedinica()
        if not isinstance(frejm, pd.core.frame.DataFrame):
            frejm = pd.DataFrame(index=list(range(5)), columns=['cref', 'U', 'c', u'\u0394', 'sr', 'r'])
        #korekcije zbog provjere linearnosti
        stupac = list(frejm.columns).index('c') #indeks stupca 'c'
        droplist = [i for i in range(len(frejm.index)) if np.isnan(frejm.iloc[i, stupac])]
        frejm.drop(frejm.index[droplist], inplace=True)
        isl = list(frejm.columns).index('r') #indeks stupca linearnosti
        if self.dokument.get_provjeraLinearnost():
            #drop stupca za provjeru linearnosti 'r'
            frejm.drop(frejm.columns[isl], inplace=True, axis=1) #drop column provjera linearnosti
            linearnost = False
        if linearnost:
            h0 = Paragraph('N:', stil1)
            h1 = Paragraph('cref ({0})'.format(str(jedinica)), stil1)
            h2 = Paragraph('U ({0})'.format(str(jedinica)), stil1)
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
            s = (1.13)*inch
            sirina_stupaca = [0.47*inch, s, s, s, s, s, s]
            tablica = Table(layout_tablice,
                            colWidths=sirina_stupaca,
                            hAlign='LEFT')
            tablica.setStyle(stil_tablice)
        else:
            h0 = Paragraph('N:', stil1)
            h1 = Paragraph('cref ({0})'.format(str(jedinica)), stil1)
            h2 = Paragraph('U ({0})'.format(str(jedinica)), stil1)
            h3 = Paragraph('c ({0})'.format(str(jedinica)), stil1)
            h4 = Paragraph('\u0394 ({0})'.format(str(jedinica)), stil1)
            h5 = Paragraph('sr ({0})'.format(str(jedinica)), stil1)
            headeri = [h0, h1, h2, h3, h4, h5]
            rows = [[str(a+1)] for a in range(len(frejm))] #nested lista
            for row in range(len(rows)):
                for col in range(5):
                    value = frejm.iloc[row, col]
                    value = round(value, 2)
                    if np.isnan(value):
                        value = ''
                    value = str(value)
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
            s = (1.36)*inch
            sirina_stupaca = [0.45*inch, s, s, s, s, s]
            tablica = Table(layout_tablice,
                            colWidths=sirina_stupaca,
                            hAlign='LEFT')
            tablica.setStyle(stil_tablice)
        return tablica

    def generiraj_tablicu_funkcije_prilagodbe_za_plin(self, plin=None):
        """generiranje tablice sa koeficijentima pravca prilagodbe"""
        if plin == None:
            return None

        stil1 = self.generate_paragraph_style(font='FreeSansBold', align=TA_CENTER)
        stil2 = self.generate_paragraph_style(align=TA_CENTER)
        stil3 = self.generate_paragraph_style(font='FreeSansBold')
        stil4 = self.generate_paragraph_style()

        a1 = Paragraph('FUNKCIJA PRILAGODBE', stil1)
        b1 = Paragraph('C = A * Cm + b', stil2)
        layout_tablice = [
            [a1, '', ''],
            [b1, '', '']]

        slopeData = self.rezultati[plin]['prilagodba']
        gas = Paragraph(str(plin), stil3)
        a = 'A = {0}'.format(str(round(slopeData['prilagodbaA'], 3)))
        a = Paragraph(a, stil4)
        b = 'B = {0}'.format(str(round(slopeData['prilagodbaB'], 1)))
        b = Paragraph(b, stil4)
        layout_tablice.append([gas, a, b])
        #special NO slucaj'
        if plin == 'NO':
            slopeDataNOx = self.rezultati['NOx']['prilagodba']
            c = 'A = {0}'.format(str(round(slopeDataNOx['prilagodbaA'], 3)))
            c = Paragraph(c, stil4)
            d = 'B = {0}'.format(str(round(slopeDataNOx['prilagodbaB'], 1)))
            d = Paragraph(d, stil4)
            layout_tablice.append(['NOx', a, b])

        stil_tablice = TableStyle(
            [
            ('SPAN', (0, 0), (-1, 0)),
            ('SPAN', (0, 1), (-1, 1)),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ])
        sirina_stupaca = [1.5 * inch, 1.5 * inch, 1.5 * inch]
        tablica = Table(layout_tablice,
                        colWidths=sirina_stupaca,
                        hAlign='LEFT')
        tablica.setStyle(stil_tablice)
        return tablica

    def generiraj_tablicu_kriterija(self, kriterij=None):
        """
        metoda generira tablicu sa kriterijima umjeravanja
        7stupaca (n + bitni stupci)
        ? redaka (header + testovi)
        """
        if kriterij == None:
            kriterij = []
        stil1 = self.generate_paragraph_style(align=TA_CENTER)
        stil2 = self.generate_paragraph_style()
        stil3 = self.generate_paragraph_style(align=TA_RIGHT)
        for parametar in kriterij:
            #round vrijednosti na 1 decimalu
            parametar[3] = str(round(parametar[3], 1))
        a2 = Paragraph('Naziv kriterija', stil1)
        a3 = Paragraph('Točka norme', stil1)
        a4 = Paragraph('Rezultati', stil1)
        a6 = Paragraph('Uvijeti prihvatljivosti', stil1)
        a7 = Paragraph('Ispunjeno', stil1)
        headeri = ['', a2, a3, a4, '', a6, a7]
        layout_tablice = []
        layout_tablice.append(headeri)
        for i in range(len(kriterij)):
            red = []
            red.append(Paragraph(str(i+1), stil1))
            for j in range(6): #elementi reda iz parametara (bez rednog broja)
                if j == 0:
                    red.append(Paragraph(str(kriterij[i][j]), stil2))
                elif j == 2:
                    red.append(Paragraph(str(kriterij[i][j]), stil3))
                elif j == 3:
                    red.append(Paragraph(str(kriterij[i][j]), stil2))
                else:
                    red.append(Paragraph(str(kriterij[i][j]), stil1))
            layout_tablice.append(red)
        stil_tablice = TableStyle(
            [
            ('SPAN', (3, 0), (4, 0)),
            ('INNERGRID', (0, 0), (1, -1), 0.25, colors.black),
            ('INNERGRID', (0, 0), (3, -1), 0.25, colors.black),
            ('INNERGRID', (4, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ])
        sirina_stupaca = [0.37*inch,
                          2.97*inch,
                          0.62*inch,
                          0.67*inch,
                          0.67*inch,
                          1.08*inch,
                          0.87*inch]
        visina_stupaca = [0.5*inch for i in range(len(kriterij)+1)]
        tablica = Table(layout_tablice,
                        colWidths=sirina_stupaca,
                        rowHeights=visina_stupaca,
                        hAlign='LEFT')
        tablica.setStyle(stil_tablice)
        return tablica

    def provjeri_ispravnost_testa(self, testovi=None, kljuc=None):
        """
        metoda provjerava da li je test ispravan...
        ulazni parametra je mapa testova (dict) i kljuc koji definira test.
        Pod svakim kljucem se nalazi lista.

        Ako je 5 element liste == 'DA' vrati True
        """
        if kljuc in testovi:
            if testovi[kljuc][5] == 'DA':
                return True
            else:
                return False
        else:
            return False


    def generiraj_stranice_reporta_za_zadani_plin(self, plin, parts, stranica, nStranica, razmak):
        """
        metoda sluzi za generiranje stranica plina

        plin = string naziv plina
        parts = lista vec postojecih elemenata za report na koju se dodaje
        stranica = broj trenutne stranice
        nStranica = ukupni broj stranica

        podaci se nazale u mapi self.rezultati[plin]

        metoda vraca tuple elemenata
        (parts, stranica)
        """
        trenutnaStranica = stranica
        if self.dokument.get_provjeraUmjeravanje():
            parts.append(PageBreak())
            trenutnaStranica += 1
            head2 = self.generiraj_header_tablicu(stranica=trenutnaStranica,
                                                  total=nStranica)
            parts.append(head2)
            parts.append(razmak)
            naziv = " ".join(['REZULTATI UMJERAVANJA:', plin])
            stilNaziva = self.generate_paragraph_style(font='FreeSansBold', align=TA_CENTER)
            naziv = Paragraph(naziv, stilNaziva)
            parts.append(naziv)
            parts.append(razmak)
            frejm_rezultata = self.rezultati[plin]['umjeravanje']
            tabla9 = self.generiraj_tablicu_rezultata_umjeravanja(frejm=frejm_rezultata)
            parts.append(tabla9)
            parts.append(razmak)
            tabla10 = self.generiraj_tablicu_funkcije_prilagodbe_za_plin(plin=plin)
            if tabla10 != None:
                parts.append(tabla10)

        dictTestova = self.rezultati[plin]['testovi']
        if len(dictTestova):
            parts.append(PageBreak()) #page break
            trenutnaStranica += 1 #pomakni broj stranice
            head3 = self.generiraj_header_tablicu(stranica=trenutnaStranica,
                                                  total=nStranica)
            parts.append(head3)
            parts.append(razmak)
            ocjena = True
            for specificTest in dictTestova:
                test = self.provjeri_ispravnost_testa(testovi=dictTestova, kljuc=specificTest)
                ocjena = ocjena and test

            if ocjena:
                tabla8 = self.generiraj_tablicu_ocjene_umjeravanja(zadovoljava='DA',
                                                                   komponenta=str(plin))
            else:
                tabla8 = self.generiraj_tablicu_ocjene_umjeravanja(zadovoljava='NE',
                                                                   komponenta=str(plin))
            parts.append(tabla8)
            parts.append(razmak)
            #slaganje testova tocnim redosljedom s time da nan vrijednosti ne stavljam u report
            kriterij = []
            if self.dokument.get_provjeraPonovljivost():
                if 'srs' in dictTestova:
                    if not np.isnan(dictTestova['srs'][3]):
                        kriterij.append(dictTestova['srs'])
                if 'srz' in dictTestova:
                    if not np.isnan(dictTestova['srz'][3]):
                        kriterij.append(dictTestova['srz'])
            if self.dokument.get_provjeraLinearnost():
                if 'rz' in dictTestova:
                    if not np.isnan(dictTestova['rz'][3]):
                        kriterij.append(dictTestova['rz'])
                if 'rmax' in dictTestova:
                    if not np.isnan(dictTestova['rmax'][3]):
                        kriterij.append(dictTestova['rmax'])
            if self.dokument.get_provjeraKonvertera():
                if 'ec' in dictTestova:
                    if not np.isnan(dictTestova['ec'][3]):
                        kriterij.append(dictTestova['ec'])
            if self.dokument.get_provjeraOdaziv():
                if 'rise' in dictTestova:
                    if not np.isnan(dictTestova['rise'][3]):
                        kriterij.append(dictTestova['rise'])
                if 'fall' in dictTestova:
                    if not np.isnan(dictTestova['fall'][3]):
                        kriterij.append(dictTestova['fall'])
                if 'diff' in dictTestova:
                    if not np.isnan(dictTestova['diff'][3]):
                        kriterij.append(dictTestova['diff'])
            tabla11 = self.generiraj_tablicu_kriterija(kriterij=kriterij)
            parts.append(tabla11)
        return (parts, trenutnaStranica)

    @helperi.activate_wait_spinner
    def generiraj_report(self, ime, dokument, rezultati):
        """
        metoda za generiranje izvjestaja:
        ime --> path + naziv pdf filea
        dokument --> instanca dokumenta
        rezultati --> nested mapa rezultata
        """
        self.ime = ime
        self.dokument = dokument
        self.rezultati = rezultati

        #ukupan broj stranica [umjeravanje, testovi, prilagodba]
        nStranica = 1
        if self.dokument.get_provjeraUmjeravanje():
            nStranica = nStranica + len(self.rezultati)
        for komponenta in self.rezultati:
            if self.rezultati[komponenta]['testovi']:
                nStranica = nStranica + 1

        #trenutna stranica
        trenutnaStranica = 1

        #pdf templata
        doc = SimpleDocTemplate(ime,
                                pagesize=A4,
                                topMargin=0.4*inch,
                                bottomMargin=0.4*inch,
                                leftMargin=0.5*inch,
                                rightMargin=0.5*inch,
                                allowSplitting=0)
        #lista flowable elemenata za report
        parts = []
        razmak = Spacer(1, 0.29*inch)
        #Generiranje prve stranice reporta (Uredjaj, CRM, vrijeme, okolisni uvijeti...)
        head1 = self.generiraj_header_tablicu(stranica=trenutnaStranica,
                                              total=nStranica)
        parts.append(head1)
        parts.append(razmak)
        tabla1 = self.generiraj_tablicu_podataka_o_uredjaju()
        parts.append(tabla1)
        parts.append(razmak)
        tabla2 = self.generiraj_crm_tablicu()
        parts.append(tabla2)
        parts.append(razmak)
        tabla3 = self.generiraj_tablicu_kalibracijske_jedinice()
        parts.append(tabla3)
        parts.append(razmak)
        tabla4 = self.generiraj_tablicu_izvora_cistog_zraka()
        parts.append(tabla4)
        parts.append(razmak)
        tabla5 = self.generiraj_tablicu_vremena_pocetka_i_kraja_umjeravanja()
        parts.append(tabla5)
        parts.append(razmak)
        tabla6 = self.generiraj_tablicu_okolisnih_uvijeta_tjekom_provjere()
        parts.append(tabla6)
        parts.append(razmak)
        tabla7 = self.generiraj_tablicu_datum_mjeritelj_voditelj()
        parts.append(tabla7)
        #kraj prve stranice
        for plin in self.rezultati:
            parts, trenutnaStranica = self.generiraj_stranice_reporta_za_zadani_plin(plin,
                                                                                     parts,
                                                                                     trenutnaStranica,
                                                                                     nStranica,
                                                                                     razmak)
        parts.append(razmak)
        #generiraj tablicu sa napomenom ako napomena postoji
        tablicaNapomene = self.generiraj_tablicu_napomene()
        if tablicaNapomene != None:
            parts.append(tablicaNapomene)
            parts.append(razmak)
        #generiraj kraj ispitnog izvjesca
        annotation2_stil = self.generate_paragraph_style()
        annotation2 = Paragraph('Kraj ispitnog izvješća.', annotation2_stil)
        parts.append(annotation2)
        #zavrsna naredba za konstrukciju dokumenta
        doc.build(parts)
