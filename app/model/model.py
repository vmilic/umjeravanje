# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 12:04:06 2015

@author: DHMZ-Milic
"""
import logging
import pickle
import datetime
from PyQt4 import QtGui, QtCore
import app.model.pomocne_funkcije as helperi
import copy
import pandas as pd
from app.model.konfig_klase import Tocka
import app.model.frejm_model as qtmodeli
import app.model.kalkulator as calc
import app.view.tab_rezultat as rezultat
import app.view.tab_konverter as konverter
import app.view.tab_odaziv as odaziv

class DokumentModel(QtCore.QObject):
    def __init__(self, cfg=None, parent=None):
        QtCore.QObject.__init__(self, parent=parent)
        self.cfg = cfg  # MainKonfig objekt
        self.postaje = {} #mapa sa podacima o postajama (postaja: [lista uredjaja na njoj])
        self.uredjaji = {} #mapa sa podacima o uredjaju (komponente, metode...)
        self.komponente = {} #mapa komponente:lista uredjaja
        self.mjerenja = {} #mapa sa podacima za pojedini tab rezultata
        self.frejmovi = {} #mapa sa ucitanim ili preuzetim frejmovima
        self.izabraniFrejm = {} #mapa sa aktivnim frejmom za podatke

        self.postavke = {'izabranaKomponenta':'',
                         'izabraniUredjaj':'',
                         'izabranaPostaja':'',
                         'oznakaModelaUredjaja':'',
                         'proizvodjacUredjaja':'',
                         'opseg':1.0,
                         'listaDilucija':[],
                         'izabranaDilucija':'',
                         'proizvodjacDilucija':'',
                         'sljedivostDilucija':'',
                         'listaZrak':[],
                         'izabraniZrak':'',
                         'proizvodjacZrak':'',
                         'sljedivostZrak':1.0,
                         'mjernaJedinica':'n/a',
                         'izvorCRM':'',
                         'koncentracijaCRM':1.0,
                         'sljedivostCRM':2.0,
                         'norma':'',
                         'oznakaIzvjesca':'',
                         'brojObrasca':'',
                         'revizija':'',
                         'datumUmjeravanja':'',
                         'temperatura':0.0,
                         'vlaga':0.0,
                         'tlak':0.0,
                         'napomena':'',
                         'cNOx50':200.0,
                         'cNOx95':180.0,
                         'provjeraKonvertera':False,
                         'provjeraOdaziv':False,
                         'provjeraUmjeravanje':False,
                         'provjeraPonovljivost':False,
                         'provjeraLinearnost':False}

        self.init_uredjaje_i_postaje_sa_REST() #postavlja postaje, uredjaje i komponente
        self.init_frejmove() #multi dokument stup za ucitane frejmove...
        self.init_mjerenja() #konstrukcija elemenata za tabove...

################################################################################
    ### inicijalizacija membera
    def init_tockeUmjeravanja(self):
        """
        Inicijalizacija umjernih tocaka uz pomoc konfiga. Output je lista
        tocaka
        """
        return self.cfg.get_tockeUmjeravanja()

    def init_tockeKonverter(self):
        """
        Inicijalizacija tocaka za provjeru konvertera uz pomoc konfiga. Output
        je lista tocaka.
        """
        return self.cfg.get_tockeKonverter()

    def init_frejmove(self):
        """
        metoda priprema model za podatke za svaki uredjaj i sprema ih u mapu self.frejmovi
        """
        for uredjaj in self.uredjaji:
            self.frejmovi[uredjaj] = qtmodeli.IzborFrejmovaModel(uredjaj=uredjaj)
            self.izabraniFrejm[uredjaj] = None

    def init_comboboxeve(self):
        """
        Inicijalno popunjavanje dijelova mape self.postavke (liste za comboboxeve).

        Metoda nije dio __init__ jer se poziva naknadno. Dijelovi gui-a koji se
        trebaju updateati jos ne postoje kao objekti u trenutku kada __init__ dokumenta zavrsi.
        """
        self.init_listaDilucija()
        self.init_listaZrak()
        self.init_postaja()
        self.init_listaKomponente()

    def init_listaKomponente(self):
        """inicijalni setup liste komponenti za combobox"""
        value = list(self.komponente.keys())
        output = {'value':value}
        self.emit(QtCore.SIGNAL('promjena_komponente(PyQt_PyObject)'),
                  output)

    def init_listaDilucija(self):
        """inicijalni setup liste dilucijskih jedinica iz konfiga"""
        lista = self.cfg.get_listu_dilucija()
        self.set_listaDilucija(lista)

    def init_listaZrak(self):
        """inicijalna postavka izbora generatora cistog zraka"""
        lista = self.cfg.get_listu_cistiZrak()
        self.set_listaZrak(lista)

    def init_postaja(self):
        """inicijalna postavka izbora postaja"""
        stanice = sorted(list(self.postaje.keys()))
        output = {'value':stanice}
        self.emit(QtCore.SIGNAL('promjena_listaPostaja(PyQt_PyObject)'),
                  output)

    def init_uredjaje_i_postaje_sa_REST(self):
        """
        Inicijalno popunjavanje podataka o uredjajima i postajama sa podacima
        preuzetim od REST servisa.

        U slucaju da dodje do pogreske prilikom spajanja sa RESTOM otvara se dijalog
        za izbor cache filea iz kojeg ce se pokusati ucitati potrebni podaci

        U slucaju da se podaci uredno pokupe sa REST-a, napraviti ce se novi cache
        file sa azurnim podacima za potrebe buduceg loada.
        """
        try:
            urlUredjaji = self.cfg.get_konfig_element('REST', 'uredjaj')
            urlPostaje = self.cfg.get_konfig_element('REST', 'postaje')
            pos, ure = helperi.pripremi_mape_postaja_i_uredjaja(urlUredjaji,
                                                                urlPostaje)
            #prvo se postavljaju uredjaji i postaje
            self.set_uredjaji(ure)
            self.set_postaje(pos)
            #racunanje 'inverzne' mape za komponente
            komp = self.get_map_komponente_to_uredjaj()
            #postavljanje mape komponenti
            self.set_komponente(komp)
            #napravi lokal cache
            self.save_RESTdata_to_cache()
        except Exception as err:
            logging.error(str(err), exc_info=True)
            #probaj loadati REST data iz lokalnog cachea
            self.load_RESTdata_from_cache()

    def init_mjerenja(self):
        """
        Metoda priprema mapu mjerenja za sve komponente. U mapi se nalaze modeli,
        tocke umjeravanja i sve sto je potrebno za funkcioniranje pojedinih tabova.
        """
        setKomponenti=set()
        for uredjaj in self.uredjaji:
            komp = set(self.uredjaji[uredjaj]['komponente'])
            setKomponenti = setKomponenti.union(komp)

        #imam viskove... npr.tocke su u modelima, high i low limit za odaziv takodjer...
        for key in setKomponenti:
            ###umjeravanja###
            self.mjerenja[key] = {}
            #tocke
            tocke = self.init_tockeUmjeravanja()
#            self.mjerenja[key]['tocke'] = tocke
            #model za prikaz
            model = qtmodeli.SiroviFrameModel(frejm=None,
                                              tocke=tocke,
                                              start=0)
            self.mjerenja[key]['model'] = model
            #kalkulator koji racuna model
            self.mjerenja[key]['kalkulator'] = calc.Kalkulator(doc=self,mjerenje=key)
            ###odazivi###
            #naziv taba
            naziv = "".join([str(key),'-odaziv'])
            self.mjerenja[naziv] = {}
            #granice uspona i pada
#            self.mjerenja[naziv]['highLimit'] = 90
#            self.mjerenja[naziv]['lowLimit'] = 10
            #model
            model = qtmodeli.RiseFallModel(slajs=None,
                                           naziv=key)
#            model.set_high_limit(self.mjerenja[naziv]['highLimit'])
#            model.set_low_limit(self.mjerenja[naziv]['lowLimit'])
            model.set_high_limit(90.0)
            model.set_low_limit(10.0)
            self.mjerenja[naziv]['model'] = model
            #frejm sa rezultatima
            #embed u model...
#            cols = ['Naziv', 'Pocetak', 'Kraj', 'Delta']
#            rez = pd.DataFrame(columns=cols)
#            self.mjerenja[naziv]['rezultatStupci'] = cols
#            self.mjerenja[naziv]['rezultatFrejm'] = rez
        ###konverter###
        self.mjerenja['konverter'] = {}
        #tocke
        tocke = self.init_tockeKonverter()
        #model
        model = qtmodeli.SiroviFrameModel(frejm=None,
                                          tocke=tocke,
                                          start=0)
        self.mjerenja['konverter']['model'] = model
        self.mjerenja['konverter']['kalkulator'] = calc.KonverterKalkulator(doc=self)
################################################################################
    ### setteri i getteri za ostale membere dokumenta
    def set_uredjaji(self, x):
        """
        Setter mape uredjaja u dokument.
        -kljucevi mape su serijski brojevi uredjaja.
        -mapa je duboko nested sa drugim mapama i sadrzi podatke o:
            -analitickim metodama
            -komponentama
            -mjerna jedinica
            -podaci o uredjaju (oznaka modela, lokacija...)
        """
        self.uredjaji = x
        if x != self.uredjaji:
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_uredjaji(PyQt_PyObject)'),
                      output)

    def get_uredjaji(self):
        """Getter svih mape svih uredjaja"""
        return self.uredjaji

    def set_postaje(self, x):
        """
        Setter mape postaja.
        -kljucevi mape su nazivi postaja, a vrijednosti su liste serijskih brojeva
        uredjaja
        """
        if x != self.postaje:
            self.postaje = x
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_postaje(PyQt_PyObject)'),
                      output)

    def get_postaje(self):
        """Getter postaja"""
        return self.postaje

    def set_komponente(self, x):
        """
        Setter komponenti mjerenja. Ulazna vrijednost je mapa koja povezuje listu
        komponenti sa serijskim brojevima uredjaja
        """
        if x != self.komponente:
            self.komponente = x
            value = list(x.keys())
            output = {'value':value}
            self.emit(QtCore.SIGNAL('promjena_komponente(PyQt_PyObject)'),
                      output)

    def get_komponente(self):
        """Getter mape {komponenta:lista serijskih brojeva uredjaja}"""
        return self.komponente

    def set_mjerenja(self, x):
        """Setter mape mjerenja, podaci za tabove"""
        if x != self.mjerenja:
            self.mjerenja = x
            self.emit(QtCore.SIGNAL('promjena_mjerenja'))

    def get_mjerenja(self):
        """geter mape mjerenja, (kljucevi su tabovi, vrijednost je mapa podataka
        potrebnih za taj tab"""
        return self.mjerenja

    def pripremi_mjerenja_za_pickle(self):
        """
        Metoda uzima nested mapu mjerenja iz dokumenta i priprema ju za
        serijalizaciju sa modulom pickle. Promblem nastaje jer unutar nested mape
        se nalaze Qt objekti koji se ne mogu direktno picklati. Iz tih objekata
        moram izvuci sve potrebno da se rekonstruiraju i te podatke pospremiti u
        mapu.
        """
        output = {}
        for mjerenje in self.mjerenja:
            output[mjerenje] = {}
            if mjerenje.endswith('-odaziv'):
                output[mjerenje]['model'] = {}
                #unutar frejma su u prva dva stupca Qt checked flagovi....
                frejm = self.mjerenja[mjerenje]['model'].get_frejm()
                frejm.iloc[:,0].replace(QtCore.Qt.Checked, 1, inplace=True)
                frejm.iloc[:,0].replace(QtCore.Qt.Unchecked, 0, inplace=True)
                frejm.iloc[:,1].replace(QtCore.Qt.Checked, 1, inplace=True)
                frejm.iloc[:,1].replace(QtCore.Qt.Unchecked, 0, inplace=True)
                output[mjerenje]['model']['frejm'] = frejm
                output[mjerenje]['model']['highLimit'] = self.mjerenja[mjerenje]['model'].get_high_limit()
                output[mjerenje]['model']['lowLimit'] = self.mjerenja[mjerenje]['model'].get_low_limit()
            else:
                output[mjerenje]['model'] = {}
                output[mjerenje]['model']['frejm'] = self.mjerenja[mjerenje]['model'].get_frejm()
                output[mjerenje]['model']['tocke'] = self.mjerenja[mjerenje]['model'].get_tocke()
                output[mjerenje]['model']['start'] = self.mjerenja[mjerenje]['model'].get_start()
        return output

    def pripremi_mjerenja_za_unpickle(self, mapa):
        """
        Metoda prima mapu sa podacima za rekonstrukciju self.mjerenja prilikom
        loada iz filea. Za svako mjerenje rekonstruira model i kalkulator.
        """
        outMjerenja = {}
        for mjerenje in mapa:
            if mjerenje.endswith('-odaziv'):
                frejm = mapa[mjerenje]['model']['frejm']
                frejm.iloc[:,0].replace(1, QtCore.Qt.Checked, inplace=True)
                frejm.iloc[:,0].replace(0, QtCore.Qt.Unchecked, inplace=True)
                frejm.iloc[:,1].replace(1, QtCore.Qt.Checked, inplace=True)
                frejm.iloc[:,1].replace(0, QtCore.Qt.Unchecked, inplace=True)
                high = mapa[mjerenje]['model']['highLimit']
                low = mapa[mjerenje]['model']['lowLimit']
                model = qtmodeli.RiseFallModel(slajs=None,
                                               naziv=mjerenje)
                model.set_high_limit(high)
                model.set_low_limit(low)
                model.set_frejm(frejm)
                #nest in another dict
                outMjerenja[mjerenje] = {}
                outMjerenja[mjerenje]['model'] = model
            elif mjerenje == 'konverter':
                frejm = mapa[mjerenje]['model']['frejm']
                tocke = mapa[mjerenje]['model']['tocke']
                start = mapa[mjerenje]['model']['start']
                model = qtmodeli.SiroviFrameModel(frejm=frejm,
                                                  tocke=tocke,
                                                  start=start)
                kalkulator = calc.KonverterKalkulator(doc=self)
                #nest in another dict
                outMjerenja[mjerenje] = {}
                outMjerenja[mjerenje]['model'] = model
                outMjerenja[mjerenje]['kalkulator'] = kalkulator
            else:
                frejm = mapa[mjerenje]['model']['frejm']
                tocke = mapa[mjerenje]['model']['tocke']
                start = mapa[mjerenje]['model']['start']
                model = qtmodeli.SiroviFrameModel(frejm=frejm,
                                                  tocke=tocke,
                                                  start=start)
                kalkulator = calc.Kalkulator(doc=self,
                                             mjerenje=mjerenje)
                #nest in another dict
                outMjerenja[mjerenje] = {}
                outMjerenja[mjerenje]['model'] = model
                outMjerenja[mjerenje]['kalkulator'] = kalkulator
        return outMjerenja

    def set_frejmovi(self, x):
        """setter mape frejmova, ucitani podaci za pojedini uredjaj"""
        if x != self.frejmovi:
            self.frejmovi = x
            self.emit(QtCore.SIGNAL('promjena_frejmovi'))

    def get_frejmovi(self):
        """getter mape frejmova, mapa modela frejmova ucitanih podataka"""
        return self.frejmovi

    def pripremi_frejmove_za_pickle(self):
        """metoda priprema member self.frejmovi za pickle"""
        outMapa = {}
        for uredjaj in self.frejmovi:
            model = self.frejmovi[uredjaj]
            podaci = model.get_podatke()
            outMapa[uredjaj] = podaci
        return outMapa

    def unpickle_frejmove_iz_mape(self, mapa):
        """metoda sastavlja mapu self frejmovi. Sluzi prilikom loada podataka"""
        outMapa = {}
        for uredjaj in mapa:
            model = qtmodeli.IzborFrejmovaModel(uredjaj=uredjaj)
            model.set_frejmovi(mapa[uredjaj])
            outMapa[uredjaj] = model
        return outMapa

    def set_izabraniFrejm(self, x):
        """setter mape izabranih frejmova"""
        if x != self.izabraniFrejm:
            self.izabraniFrejm = x
            self.emit(QtCore.SIGNAL('promjena_izabraniFrejm'))

    def get_izabraniFrejm(self):
        """getter mape izabranih frejmova, kljuc je serial uredjaja, vrijednost je
        broj indeksa modela pod kojim se nalazi frejm (mapa self.frejmovi)"""
        return self.izabraniFrejm
################################################################################
    ### self.postavke getteri i setteri ###
    def set_postavke(self, mapa):
        """Setter mape postavki, redosljed postavljanja elemenata je bitan"""
        try:
            self.set_izabranaKomponenta(mapa['izabranaKomponenta'])
            self.set_izabraniUredjaj(mapa['izabraniUredjaj'], recalculate=False)
            self.set_izabranaPostaja(mapa['izabranaPostaja'])
            self.set_oznakaModelaUredjaja(mapa['oznakaModelaUredjaja'])
            self.set_proizvodjacUredjaja(mapa['proizvodjacUredjaja'])
            self.set_opseg(mapa['opseg'], recalculate=False)
            self.set_mjernaJedinica(mapa['mjernaJedinica'])
            self.set_izvorCRM(mapa['izvorCRM'])
            self.set_norma(mapa['norma'])
            self.set_revizija(mapa['revizija'])
            self.set_oznakaIzvjesca(mapa['oznakaIzvjesca'])
            self.set_listaDilucija(mapa['listaDilucija'], recalculate=False)
            self.set_izabranaDilucija(mapa['izabranaDilucija'], recalculate=False)
            self.set_proizvodjacDilucija(mapa['proizvodjacDilucija'])
            self.set_sljedivostDilucija(mapa['sljedivostDilucija'])
            self.set_listaZrak(mapa['listaZrak'], recalculate=False)
            self.set_izabraniZrak(mapa['izabraniZrak'], recalculate=False)
            self.set_proizvodjacZrak(mapa['proizvodjacZrak'])
            self.set_sljedivostZrak(mapa['sljedivostZrak'], recalculate=False)
            self.set_koncentracijaCRM(mapa['koncentracijaCRM'], recalculate=False)
            self.set_sljedivostCRM(mapa['sljedivostCRM'], recalculate=False)
            self.set_brojObrasca(mapa['brojObrasca'])
            self.set_datumUmjeravanja(mapa['datumUmjeravanja'])
            self.set_temperatura(mapa['temperatura'])
            self.set_vlaga(mapa['vlaga'])
            self.set_tlak(mapa['tlak'])
            self.set_napomena(mapa['napomena'])
            self.set_cNOx50(mapa['cNOx50'], recalculate=False)
            self.set_cNOx95(mapa['cNOx95'], recalculate=False)
            self.set_provjeraKonvertera(mapa['provjeraKonvertera'])
            self.set_provjeraOdaziv(mapa['provjeraOdaziv'])
            self.set_provjeraUmjeravanje(mapa['provjeraUmjeravanje'])
            self.set_provjeraPonovljivost(mapa['provjeraPonovljivost'])
            self.set_provjeraLinearnost(mapa['provjeraLinearnost'])
        except Exception as err:
            logging.error(str(err), exc_info=True)
            #default fallback
            self.set_izabranaKomponenta('')
            self.set_izabraniUredjaj('', recalculate=False)
            self.set_izabranaPostaja('')
            self.set_oznakaModelaUredjaja('')
            self.set_proizvodjacUredjaja('')
            self.set_opseg(1.0, recalculate=False)
            self.set_mjernaJedinica('n/a')
            self.set_izvorCRM('')
            self.set_norma('')
            self.set_revizija('')
            self.set_oznakaIzvjesca('')
            self.set_listaDilucija([], recalculate=False)
            self.set_izabranaDilucija('', recalculate=False)
            self.set_proizvodjacDilucija('')
            self.set_sljedivostDilucija('')
            self.set_listaZrak([], recalculate=False)
            self.set_izabraniZrak('', recalculate=False)
            self.set_proizvodjacZrak('')
            self.set_sljedivostZrak(1.0, recalculate=False)
            self.set_koncentracijaCRM(1.0, recalculate=False)
            self.set_sljedivostCRM(2.0, recalculate=False)
            self.set_brojObrasca('')
            self.set_datumUmjeravanja('')
            self.set_temperatura(0.0)
            self.set_vlaga(0.0)
            self.set_tlak(0.0)
            self.set_napomena('')
            self.set_cNOx50(200.0, recalculate=False)
            self.set_cNOx95(180.0, recalculate=False)
            self.set_provjeraKonvertera(False)
            self.set_provjeraOdaziv(False)
            self.set_provjeraUmjeravanje(False)
            self.set_provjeraPonovljivost(False)
            self.set_provjeraLinearnost(False)
        finally:
            self.recalculate()

    def get_postavke(self):
        """getter mape postavki"""
        return self.postavke

    def set_izabranaKomponenta(self, x):
        """
        Setter trenutno aktivne komponente. Ulazni parametar x je string.

        Izabrana komponenta definira moguce plinove i uredjaje
        """
        x = str(x)
        if x != self.postavke['izabranaKomponenta']:
            self.postavke['izabranaKomponenta'] = x
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_izabranaKomponenta(PyQt_PyObject)'),
                      output)
            uredjaji = self.komponente[x]
            output = {'value':uredjaji}
            self.emit(QtCore.SIGNAL('promjena_uredjaja(PyQt_PyObject)'),
                      output)
            komp = x.split(sep=',')
            komp = [i.strip()[1:-1] for i in komp]
            plin = komp[0]
            #pokusaj postavljanja izvora crm
            try:
                izvorCRM = self.cfg.get_konfig_element(plin, 'izvor')
                self.set_izvorCRM(izvorCRM)
            except Exception as err:
                logging.error(str(err), exc_info=True)
                self.set_izvorCRM('')
            #pokusaj postavljanja naziva norme
            try:
                s1 = self.cfg.get_konfig_element(plin, 'norma')
                s2 = self.cfg.get_konfig_element(plin, 'naziv')
                norma = ' '.join([s1, s2])
                self.set_norma(norma)
            except Exception as err:
                logging.error(str(err), exc_info=True)
                self.set_norma('')
            #pokisaj postavljanja revizije
            try:
                revizija = self.cfg.get_konfig_element(plin, 'revizija')
                self.set_revizija(revizija)
            except Exception as err:
                logging.error(str(err), exc_info=True)
                self.set_revizija('')
            #pokisaj postavljanja oznake izvjesca
            try:
                oznaka = self.cfg.get_konfig_element(plin, 'oznaka')
                self.set_oznakaIzvjesca(oznaka)
            except Exception as err:
                logging.error(str(err), exc_info=True)
                self.set_oznakaIzvjesca('')

    def get_izabranaKomponenta(self):
        """
        Getter trenutno aktivne komponente.
        """
        return self.postavke['izabranaKomponenta']

    def set_izabraniUredjaj(self, x, recalculate=True):
        """
        Setter trenutno aktivnog uredjaja
        """
        x = str(x)
        if x != self.postavke['izabraniUredjaj']:
            self.postavke['izabraniUredjaj'] = x
            #postavi izabranu postaju
            try:
                lok = self.uredjaji[x]['lokacija']
                self.set_izabranaPostaja(lok)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            #postavi oznaku modela uredjaja
            try:
                value = str(self.uredjaji[x]['oznakaModela'])
                self.set_oznakaModelaUredjaja(value)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            #postavi proizvodjaca uredjaja
            try:
                value = str(self.uredjaji[x]['proizvodjac'])
                self.set_proizvodjacUredjaja(value)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            #postavi opseg
            try:
                opseg = self.uredjaji[x]['analitickaMetoda']['o']['max']
                self.set_opseg(opseg, recalculate=False)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            #postavi mjernu jedinicu:
            try:
                komp = self.uredjaji[x]['komponente'][0] #izaberi prvu komponentu as popisa
                jedinica = self.uredjaji[x]['komponenta'][komp]['mjernaJedinica']
            except Exception as err:
                jedinica = 'n/a'
            finally:
                self.set_mjernaJedinica(jedinica)
            if recalculate:
                self.recalculate()
            #emit change
            output = {'value':x,
                      'recalculate':recalculate}
            self.emit(QtCore.SIGNAL('promjena_izabraniUredjaj(PyQt_PyObject)'),
                      output)

    def get_izabraniUredjaj(self):
        """Getter trenutno aktivnog uredjaja"""
        return self.postavke['izabraniUredjaj']

    def set_izabranaPostaja(self, x):
        """Setter trenutno aktivne postaje"""
        x = str(x)
        if x != self.postavke['izabranaPostaja']:
            self.postavke['izabranaPostaja'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_izabranaPostaja(PyQt_PyObject)'),
                      output)

    def get_izabranaPostaja(self):
        """Getter trenutno aktivne postaje"""
        return self.postavke['izabranaPostaja']


    def set_oznakaModelaUredjaja(self, x):
        """Setter oznake modela izabranog uredjaja"""
        x = str(x)
        if x != self.postavke['oznakaModelaUredjaja']:
            self.postavke['oznakaModelaUredjaja'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_oznakaModelaUredjaja(PyQt_PyObject)'),
                      output)

    def get_oznakaModelaUredjaja(self):
        """getter oznake modela uredjaja"""
        return self.postavke['oznakaModelaUredjaja']

    def set_proizvodjacUredjaja(self, x):
        """setter proizvodjaca izabranog uredjaja"""
        x = str(x)
        if x != self.postavke['proizvodjacUredjaja']:
            self.postavke['proizvodjacUredjaja'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_proizvodjacUredjaja(PyQt_PyObject)'),
                      output)

    def get_proizvodjacUredjaja(self):
        """Getter proizvodjaca izabranog uredjaja"""
        return self.postavke['proizvodjacUredjaja']

    def set_opseg(self, x, recalculate=True):
        """Setter opsega umjeravanja"""
        x = float(x)
        if x != self.postavke['opseg']:
            self.postavke['opseg'] = x
            if recalculate:
                self.recalculate()
        output = {'value':x,
                  'recalculate':recalculate}
        self.emit(QtCore.SIGNAL('promjena_opseg(PyQt_PyObject)'),
                  output)

    def get_opseg(self):
        """getter opsega umjeravanja"""
        return self.postavke['opseg']

    def set_listaDilucija(self, x, recalculate=True):
        """
        Setter liste dilucijskih (kalibracijskih) jedinica. Ulazna vrijednost
        je lista stringova.
        """
        if x != self.postavke['listaDilucija']:
            self.postavke['listaDilucija'] = x
            #emit change
            output = {'value':x,
                      'recalculate':recalculate}
            self.emit(QtCore.SIGNAL('promjena_listaDilucija(PyQt_PyObject)'),
                      output)
            #ako lista nije prazna izaberi prvi element
            if x:
                self.set_izabranaDilucija(x[0], recalculate=recalculate)
            else:
                self.set_izabranaDilucija('', recalculate=recalculate)

    def get_listaDilucija(self):
        """Gettet liste dilucijskih jedinica"""
        return self.postavke['listaDilucija']

    def set_izabranaDilucija(self, x, recalculate=True):
        """Setter izabrane dilucijske jedinice. Ulazna vrijednost je string."""
        x = str(x)
        dilucije = self.get_listaDilucija()
        if not x in dilucije:
            msg = '{0} se ne nalazi na popisu mogucih dilucijskih jedinica {1}'.format(x, str(dilucije))
            raise ValueError(msg)
        if x != self.postavke['izabranaDilucija']:
            self.postavke['izabranaDilucija'] = x
            #promjena povezanih polja
            try:
                # dilucija proizvodjac
                value = self.cfg.get_konfig_element(x, 'proizvodjac')
                self.set_proizvodjacDilucija(value)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            try:
                # dilucija sljedivost
                part1 = self.cfg.get_konfig_element(x, 'MFC_NUL_Plin_sljedivost')
                part2 = self.cfg.get_konfig_element(x, 'MFC_KAL_PLIN_sljedivost')
                part3 = self.cfg.get_konfig_element(x, 'GENERATOR_OZONA_sljedivost')
                value = ", ".join([part1, part2, part3])
                self.set_sljedivostDilucija(value)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            if recalculate:
                self.recalculate()
                #emit change
            output = {'value':x,
                      'recalculate':recalculate}
            self.emit(QtCore.SIGNAL('promjena_izabranaDilucija(PyQt_PyObject)'),
                      output)

    def get_izabranaDilucija(self):
        """Getter izabrane dilucijske jedinice"""
        return self.postavke['izabranaDilucija']

    def set_proizvodjacDilucija(self, x):
        """Setter proizvodjaca dilucijske (kalibracijske) jedinice. Ulazna vrijednost
        je tipa string"""
        x = str(x)
        if x != self.postavke['proizvodjacDilucija']:
            self.postavke['proizvodjacDilucija'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_proizvodjacDilucija(PyQt_PyObject)'),
                      output)

    def get_proizvodjacDilucija(self):
        """Getter proizvodjaca dilucijske (kalibracijske) jedinice."""
        return self.postavke['proizvodjacDilucija']

    def set_sljedivostDilucija(self, x):
        """Setter sljedivosti dilucijske (kalibracijske) jedinice. Ulazna vrijednost
        je tipa string"""
        x = str(x)
        if x != self.postavke['sljedivostDilucija']:
            self.postavke['sljedivostDilucija'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_sljedivostDilucija(PyQt_PyObject)'),
                      output)

    def get_sljedivostDilucija(self):
        """Getter sljedivosti dilucijske (kalibracijske) jedinice"""
        return self.postavke['sljedivostDilucija']

    def set_listaZrak(self, x, recalculate=True):
        """Setter liste generatora cistog zraka. Ulazna vrijednost je lista stringova"""
        if x != self.postavke['listaZrak']:
            self.postavke['listaZrak'] = x
            #emit change
            output = {'value':x,
                      'recalculate':recalculate}
            self.emit(QtCore.SIGNAL('promjena_listaZrak(PyQt_PyObject)'),
                      output)
            if x:
                #ako lista nije prazna izaberi prvi element
                self.set_izabraniZrak(x[0], recalculate=recalculate)
            else:
                self.set_izabraniZrak('', recalculate=recalculate)

    def get_listaZrak(self):
        """Getter liste generatora cistog zraka"""
        return self.postavke['listaZrak']

    def set_izabraniZrak(self, x, recalculate=True):
        """Setter izabranog generatora cistog zraka. Ulazna vrijednost je string"""
        x = str(x)
        listaMogucih = self.get_listaZrak()
        if x not in listaMogucih:
            msg = '{0} se ne nalazi na popisu mogucih generatora cistog zraka {1}'.format(x, str(listaMogucih))
            raise ValueError(msg)
        if x != self.postavke['izabraniZrak']:
            self.postavke['izabraniZrak'] = x
            # promjena proizvodjaca generatora cistog zraka
            try:
                value = self.cfg.get_konfig_element(x, 'proizvodjac')
                self.set_proizvodjacZrak(value)
            except Exception as err:
                logging.error(str(err), exc_info=True)
            try:
                # sljedivost generatora cistog zraka
                plinovi = self.get_izabranaKomponenta()
                plinovi = plinovi.split(sep=',')
                plinovi = [i.strip()[1:-1] for i in plinovi]
                plin = plinovi[0]
                value = self.cfg.get_konfig_element(x, plin)
                value = 2*float(value) #get_konfig_element vraca string..za U(k=2)
                self.set_sljedivostZrak(value, recalculate=recalculate)
            except Exception as err:
                logging.error(str(err), exc_info=True)
                self.set_sljedivostZrak(1.0, recalculate=recalculate)
            if recalculate:
                self.recalculate()
            #emit change
            output = {'value':x,
                      'recalculate':recalculate}
            self.emit(QtCore.SIGNAL('promjena_izabraniZrak(PyQt_PyObject)'),
                      output)

    def get_izabraniZrak(self):
        """Getter izabranog generatora cistog zraka"""
        return self.postavke['izabraniZrak']

    def set_proizvodjacZrak(self, x):
        """Setter proizvodjaca generatora cistog zraka. Ulazna vrijednost je tipa
        string"""
        x = str(x)
        if x != self.postavke['proizvodjacZrak']:
            self.postavke['proizvodjacZrak'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_proizvodjacZrak(PyQt_PyObject)'),
                      output)

    def get_proizvodjacZrak(self):
        """Getter proizvodjaca generatora cistog zraka"""
        return self.postavke['proizvodjacZrak']

    def set_sljedivostZrak(self, x, recalculate=True):
        """Setter sljedivosti generatora cistog zraka. Ulazna vrijednost je tipa
        float"""
        x = float(x)
        if x != self.postavke['sljedivostZrak']:
            self.postavke['sljedivostZrak'] = x
            #recalculate all tabs
            if recalculate:
                self.recalculate()
            #emit change
            output = {'value':x,
                      'recalculate':recalculate}
            self.emit(QtCore.SIGNAL('promjena_sljedivostZrak(PyQt_PyObject)'),
                      output)

    def get_sljedivostZrak(self):
        """Getter sljedivosti generatora cistog zraka"""
        return self.postavke['sljedivostZrak']

    def set_mjernaJedinica(self, x):
        """Setter mjerne jedinice. Ulazna vrijednost je tipa string."""
        x = str(x)
        if x != self.postavke['mjernaJedinica']:
            self.postavke['mjernaJedinica'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_mjernaJedinica(PyQt_PyObject)'),
                      output)

    def get_mjernaJedinica(self):
        """Getter mjerne jedinice, Izlazna vrijednost je tipa string."""
        return self.postavke['mjernaJedinica']

    def set_izvorCRM(self, x):
        """Setter izvora certificiranog referentnog materijala. Ulazna vrijednost
        je string"""
        x = str(x)
        if x != self.postavke['izvorCRM']:
            self.postavke['izvorCRM'] = x
            self.emit(QtCore.SIGNAL('promjena_izvorCRM(PyQt_PyObject)'),
                      x)

    def get_izvorCRM(self):
        """Getter izvora certificiranog referentnog materijala."""
        return self.postavke['izvorCRM']

    def set_koncentracijaCRM(self, x, recalculate=True):
        """Setter koncentracije certificiranog referentnog materijala. Ulazna
        vrijednost je tipa float"""
        x = float(x)
        if x != self.postavke['koncentracijaCRM']:
            self.postavke['koncentracijaCRM'] = x
            #recalculate all tabs
            if recalculate:
                self.recalculate()
            #emit change
            output = {'value':x,
                      'recalculate':recalculate}
            self.emit(QtCore.SIGNAL('promjena_koncentracijaCRM(PyQt_PyObject)'),
                      output)

    def get_koncentracijaCRM(self):
        """Getter koncentracije certificiranog referentnog materijala"""
        return self.postavke['koncentracijaCRM']

    def set_sljedivostCRM(self, x, recalculate=True):
        """Setter sljedivosti certificiranog referentnog materijala. Ulazna vrijednost
        je tipa float"""
        x = float(x)
        if x != self.postavke['sljedivostCRM']:
            self.postavke['sljedivostCRM'] = x
            #recalculate all tabs
            if recalculate:
                self.recalculate()
            #emit change
            output = {'value':x,
                      'recalculate':recalculate}
            self.emit(QtCore.SIGNAL('promjena_sljedivostCRM(PyQt_PyObject)'),
                      output)

    def get_sljedivostCRM(self):
        """Getter sljedivosti certificiranog referentnog materijala"""
        return self.postavke['sljedivostCRM']

    def set_norma(self, x):
        """Setter norme mjerenja (norma + naziv). Ulazna vrijednost je tipa string."""
        x = str(x)
        if x != self.postavke['norma']:
            self.postavke['norma'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_norma(PyQt_PyObject)'),
                      output)

    def get_norma(self):
        """Getter norme mjerenja"""
        return self.postavke['norma']

    def set_oznakaIzvjesca(self, x):
        """Setter oznake izvjesca. Ulazna vrijednost je tipa."""
        x = str(x)
        if x != self.postavke['oznakaIzvjesca']:
            self.postavke['oznakaIzvjesca'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_oznakaIzvjesca(PyQt_PyObject)'),
                      output)

    def get_oznakaIzvjesca(self):
        """Getter oznake izvjesca"""
        return self.postavke['oznakaIzvjesca']

    def set_brojObrasca(self, x):
        """Setter broja obrasca. Ulazni parametar je tipa string"""
        x = str(x)
        if x != self.postavke['brojObrasca']:
            self.postavke['brojObrasca'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_brojObrasca(PyQt_PyObject)'),
                      output)

    def get_brojObrasca(self):
        """Getter broj obrasca"""
        return self.postavke['brojObrasca']

    def set_revizija(self, x):
        """Setter broja revizije. Ulazni parametar je tipa string"""
        x = str(x)
        if x != self.postavke['revizija']:
            self.postavke['revizija'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_revizija(PyQt_PyObject)'),
                      output)

    def get_revizija(self):
        """Getter broja revizije"""
        return self.postavke['revizija']

    def set_datumUmjeravanja(self, x):
        """Setter datuma umjeravanja. Ulazna vrijednost je string"""
        x = str(x)
        if x != self.postavke['datumUmjeravanja']:
            self.postavke['datumUmjeravanja'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_datumUmjeravanja(PyQt_PyObject)'),
                      output)

    def get_datumUmjeravanja(self):
        """Getter datuma umjeravanja"""
        return self.postavke['datumUmjeravanja']

    def set_temperatura(self, x):
        """Setter okolisnih uvijeta, temperatura. Ulazna vrijednost je float"""
        x = float(x)
        if x != self.postavke['temperatura']:
            self.postavke['temperatura'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_temperatura(PyQt_PyObject)'),
                      output)

    def get_temperatura(self):
        """Gettter okolisnih uvijeta, temperatura"""
        return self.postavke['temperatura']

    def set_tlak(self, x):
        """Setter okolisnih uvijeta, tlak. Ulazna vrijednost je float"""
        x = float(x)
        if x != self.postavke['tlak']:
            self.postavke['tlak'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_tlak(PyQt_PyObject)'),
                      output)

    def get_tlak(self):
        """Getter okolisnih uvijeta, tlak"""
        return self.postavke['tlak']

    def set_vlaga(self, x):
        """Setter okolisnih uvijeta, vlaga. Ulazna vrijednost je float"""
        x = float(x)
        if x != self.postavke['vlaga']:
            self.postavke['vlaga'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_vlaga(PyQt_PyObject)'),
                      output)

    def get_vlaga(self):
        """Getter okolisnih uvijeta, vlaga."""
        return self.postavke['vlaga']

    def set_napomena(self, x):
        """Setter napomene umjeravanja. Ulazna vrijednost je string"""
        x = str(x)
        if x != self.postavke['napomena']:
            self.postavke['napomena'] = x
            #emit change
            output = {'value':x}
            self.emit(QtCore.SIGNAL('promjena_napomena(PyQt_PyObject)'),
                      output)

    def get_napomena(self):
        """Getter napomena umjeravanja"""
        return self.postavke['napomena']

    def set_cNOx50(self, x, recalculate=True):
        """Setter za parametar cNOx50. Ulazna vrijednost je float"""
        x = float(x)
        if x != self.postavke['cNOx50']:
            self.postavke['cNOx50'] = x
            if recalculate:
                self.recalculate()
            output = {'value':x,
                      'recalculate':recalculate}
            self.emit(QtCore.SIGNAL('promjena_cNOx50(PyQt_PyObject)'),
                      output)

    def get_cNOx50(self):
        """Getter za vijednost cNOx50 parametra"""
        return self.postavke['cNOx50']

    def set_cNOx95(self, x, recalculate=True):
        """Setter za parametar cNOx95. Ulazna vrijednost je float"""
        x = float(x)
        if x != self.postavke['cNOx95']:
            self.postavke['cNOx95'] = x
            if recalculate:
                self.recalculate()
            output = {'value':x,
                      'recalculate':recalculate}
            self.emit(QtCore.SIGNAL('promjena_cNOx95(PyQt_PyObject)'),
                      output)

    def get_cNOx95(self):
        """Getter za vijednost cNOx95 parametra"""
        return self.postavke['cNOx95']

    def set_provjeraKonvertera(self, x):
        """
        Setter za "globalnu" provjeru konvertera (check za prikaz taba).
        Ulazni parametar je boolean.
        """
        if x != self.postavke['provjeraKonvertera']:
            self.postavke['provjeraKonvertera'] = x
            self.emit(QtCore.SIGNAL('promjena_provjeraKonvertera(PyQt_PyObject)'),
                      x)
            self.recalculate()

    def get_provjeraKonvertera(self):
        """
        Getter za boolean provjere konvertera.
        """
        return self.postavke['provjeraKonvertera']

    def set_provjeraOdaziv(self, x):
        """
        Setter za "globalnu" provjeru odaziva (check za prikaz tabova odaziva).
        Ulazni parametar je boolean.
        """
        if x != self.postavke['provjeraOdaziv']:
            self.postavke['provjeraOdaziv'] = x
            self.emit(QtCore.SIGNAL('display_odaziv(PyQt_PyObject)'),
                      x)
            self.recalculate()

    def get_provjeraOdaziv(self):
        """
        Getter za "globalnu" provjeru odaziva (check za prikaz tabova odaziva).
        """
        return self.postavke['provjeraOdaziv']

    def set_provjeraUmjeravanje(self, x):
        """
        Setter za provjeru umjeravanja. Ulazni parametar je boolean.
        """
        if x != self.postavke['provjeraUmjeravanje']:
            self.postavke['provjeraUmjeravanje'] = x
            self.emit(QtCore.SIGNAL('display_umjeravanje(PyQt_PyObject)'),
                      x)
            self.recalculate()

    def get_provjeraUmjeravanje(self):
        """Getter za provjeru umjeravanja"""
        return self.postavke['provjeraUmjeravanje']

    def set_provjeraPonovljivost(self, x):
        """
        Setter za provjeru ponovljivosti. Ulazni parametar je boolean.
        """
        if x != self.postavke['provjeraPonovljivost']:
            self.postavke['provjeraPonovljivost'] = x
            self.emit(QtCore.SIGNAL('display_ponovljivost(PyQt_PyObject)'),
                      x)
            self.recalculate()

    def get_provjeraPonovljivost(self):
        """Getter za provjeru ponovljivosti"""
        return self.postavke['provjeraPonovljivost']

    def set_provjeraLinearnost(self, x):
        """
        Setter za provjeru linearnosti. Ulazni parametar je boolean.
        """
        if x != self.postavke['provjeraLinearnost']:
            self.postavke['provjeraLinearnost'] = x
            self.emit(QtCore.SIGNAL('display_linearnost(PyQt_PyObject)'),
                      x)
            self.recalculate()

    def get_provjeraLinearnost(self):
        """
        Getter za provjeru linearnosti.
        """
        return self.postavke['provjeraLinearnost']
################################################################################
    ### pomocni setteri i getteri za objekte unutar raznih mapa...
    def set_start(self, indeks, mjerenje=None, recalculate=True):
        """setter pocetnog indeksa od kojeg se krece sa umjeravanjem"""
        if self.mjerenje_isValid(mjerenje):
            if indeks != self.get_start(mjerenje=mjerenje):
                self.mjerenja[mjerenje]['model'].set_start(indeks)
                #recalculate
                if recalculate:
                    self.recalculate_tab_umjeravanja(mjerenje=mjerenje)
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)

    def get_start(self, mjerenje=None):
        """getter pocetnog indeksa od kojeg se krece sa umjeravanjem"""
        if self.mjerenje_isValid(mjerenje):
            return self.mjerenja[mjerenje]['model'].get_start()
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)
            return None

    def set_tocke(self, tocke, mjerenje=None, recalculate=True):
        """setter tocaka umjeravanja za mjerenje (tab)"""
        if self.mjerenje_isValid(mjerenje):
            if tocke != self.get_tocke(mjerenje=mjerenje):
                # modificiranje modela za novi prikaz
                self.mjerenja[mjerenje]['model'].set_tocke(tocke)
                #recalculate
                if recalculate:
                    self.recalculate_tab_umjeravanja(mjerenje=mjerenje)
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)

    def get_tocke(self, mjerenje=None):
        if self.mjerenje_isValid(mjerenje):
            return self.mjerenja[mjerenje]['model'].get_tocke()
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)
            return None

    def zamjeni_umjernu_tocku(self, indeks, tocka, mjerenje=None, recalculate=True):
        """
        Metoda mjenja postojecu tocku sa zadanom tockom. Lokacija je zadana
        sa indeksom u listi. Zamjena je samo u tockama za odredjeni tab.
        """
        if self.mjerenje_isValid(mjerenje):
            tocke = copy.deepcopy(self.get_tocke(mjerenje=mjerenje))
            tocke[indeks] = tocka
            self.set_tocke(tocke, mjerenje=mjerenje, recalculate=True)
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)

    def dodaj_umjernu_tocku(self, mjerenje=None, recalculate=True):
        """
        Metoda dodaje tocku na popis tocaka za mjerenje(tab). Dodaje je iza vec
        definiranih tocaka, ukupno 30 indeksa, prvih 15 zanemarenih, random boja.
        """
        if self.mjerenje_isValid(mjerenje):
            tocke = copy.deepcopy(self.get_tocke(mjerenje=mjerenje))
            ime = 'TOCKA' + str(len(tocke)+1)
            indeks = max([max(tocka.indeksi) for tocka in tocke])
            start = indeks+15
            end = start+15
            cref = 0.0
            novaTocka = Tocka(ime=ime, start=start, end=end, cref=cref)
            tocke.append(novaTocka)
            self.set_tocke(tocke, mjerenje=mjerenje, recalculate=True)
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)

    def makni_umjernu_tocku(self, indeks, mjerenje=None, recalculate=True):
        """
        Metoda brise tocku zadanu indeksom sa popisa tocaka za mjerenje(tab)
        Metoda mjenja nazive ostalih tocaka radi konzistencije.
        """
        if self.mjerenje_isValid(mjerenje):
            tocke = copy.deepcopy(self.get_tocke(mjerenje=mjerenje))
            tocke.pop(indeks)
            for i in range(len(tocke)):
                tocke[i].ime = 'TOCKA' + str(i+1)
            self.set_tocke(tocke, mjerenje=mjerenje, recalculate=True)
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)


    def get_frejmovi_model(self, uredjaj):
        """ getter modela frejmova ucitanih podataka za zadani serijski broj uredjaja"""
        return self.frejmovi[uredjaj]

    def set_aktivni_frejm(self, indeks, dictTabova, aktivniTab):
        """
        Setter aktivnog frejma za podatke u model. indeks je broj redka u tablici.

        Extra... frejm se treba prebaciti u sve modele pojedinih tabova za prikaz
        niza podataka.
        """
        uredjaj = self.get_izabraniUredjaj()
        self.izabraniFrejm[uredjaj] = indeks
        frejm = self.frejmovi[uredjaj].vrati_selektirani_frejm(indeks)
        for key in dictTabova:
            tab = dictTabova[key]
            if isinstance(tab, rezultat.RezultatPanel):
                model = self.get_model(mjerenje=tab.plin)
                if model:
                    model.set_frejm(frejm)
            elif isinstance(tab, konverter.KonverterPanel):
                model = self.get_model(mjerenje=tab.plin)
                if model:
                    model.set_frejm(frejm)
            elif isinstance(tab, odaziv.RiseFallWidget):
                naziv = tab.naziv #samo naziv komponente bez '-odaziv'
                slajs = frejm.loc[:,naziv]
                model = self.get_model(mjerenje=tab.plin)
                if model:
                    model.set_slajs(slajs, naziv)
            else:
                #defaultni prazni model
                tocke = self.init_tockeUmjeravanja()
                model = qtmodeli.SiroviFrameModel(frejm=None, tocke=tocke, start=0)
            #update gui da prikaze ispravni model za tab
            model = self.get_model(mjerenje=aktivniTab.plin)
            self.emit(QtCore.SIGNAL('update_tablicu_podataka(PyQt_PyObject)'),
                      model)

    def get_aktivni_frejm(self, uredjaj):
        """getter aktivnog frejma (njegovog indeksa) za uredjaj"""
        return self.izabraniFrejm[uredjaj]

    def get_model(self, mjerenje=None):
        """ getter instance modela za mjerenje """
        if self.mjerenje_isValid(mjerenje):
            return self.mjerenja[mjerenje]['model']
        else:
            msg = 'kljuc {0} ne postoji u mapi. Vraca se prazni model.'.format(str(mjerenje))
            logging.warning(msg)
            tocke = self.init_tockeUmjeravanja()
            return qtmodeli.SiroviFrameModel(frejm=None, tocke=tocke, start=0)
################################################################################
    ###ostale metode... save/load ...
    def mjerenje_isValid(self, mjerenje):
        """helper metoda za provjeru da li je zadano mjerenje validno"""
        if mjerenje != None and mjerenje in self.mjerenja:
            return True
        else:
            return False

    def get_map_komponente_to_uredjaj(self):
        """
        Metoda vraca mapu {komponente:lista uredjaja}.
        Zanemaruju se svi uredjaji koji nemaju zadane komponente"""
        mapa = {}
        for uredjaj in self.uredjaji:
            komponente = self.uredjaji[uredjaj]['komponente']
            if len(komponente):
                value = str(komponente)
                value = value[1:-1] #treba maknuti [] od liste
                if value in mapa:
                    mapa[value].append(uredjaj)
                else:
                    mapa[value] = [uredjaj]
        return mapa

    def save_RESTdata_to_cache(self):
        """
        Spremanje podataka o uredjajima i postajama u binary formatu u file naziva
        "RESTcache-YYYY-MM-DD.dat" gdje je YYYY-MM-DD datum kada je file napravljen.
        Za serijalizaciju koristimo modul pickle
        """
        datum = str(datetime.datetime.now().date())
        filename = ''.join(['./RESTcache-', datum, '.dat'])
        #napravi cache direktorij sa svim podacima koji su potrebni
        cacheData = {'postaje':self.postaje,
                     'uredjaji':self.uredjaji}
        with open(filename, mode='wb') as fajl:
            try:
                pickle.dump(cacheData, fajl)
            except Exception as err:
                logging.error(str(err), exc_info=True)
                mes = '\n'.join(['Spremanje REST cache filea nije uspjelo.',str(err)])
                QtGui.QMessageBox.warning(QtGui.QApplication, 'Problem', mes)

    def load_RESTdata_from_cache(self):
        """
        Ucitavanje podataka o uredjajima i postajama iz binarnog formata (file
        naziva "RESTcache-YYYY-MM-DD.dat"). Izbor filea je uz pomoc dijaloga.
        Za deserijalizaciju se koristi modul pickle.
        """
        filepath = QtGui.QFileDialog.getOpenFileName(caption='Izaberi RESTcache file',
                                                     filter='dat files (*.dat);;all (*.*)')

        if filepath:
            with open(filepath, mode='rb') as fajl:
                try:
                    mapa = pickle.load(fajl)
                    #prvo postavljamo postaje i uredjaje
                    self.set_postaje(mapa['postaje'])
                    self.set_uredjaji(mapa['uredjaji'])
                    #racunamo mapu komponenti od uredjaja
                    komp = self.get_map_komponente_to_uredjaj()
                    #postavljanje komponenti
                    self.set_komponente(komp)
                except Exception as err:
                    logging.error(str(err), exc_info=True)
                    mes = '\n'.join(['Ucitavanje REST cache nije uspjelo.',
                                     'Uredjaji i postaje nisu definirani.',
                                     str(err)])
                    QtGui.QMessageBox.warning(QtGui.QApplication, 'Problem', mes)
                    #defaulti
                    self.set_postaje({})
                    self.set_uredjaji({})
                    self.set_komponente({})

    def add_frejm_ucitanih_za_uredjaj(self, frejm, tip, uredjaj):
        """
        Dodavanje ucitanih frejmova u dokument (mapa self.frejmovi) pod kljucem
        uredjaja.
        ulazni podaci:
        frejm - dataframe podataka
        tip - 'minutni' ili 'sekundni' (da li su podaci minutno usrednjeni?)
        uredjaj - string serijskog broja uredjaja
        """
        #trebam inicijalizirati modele za svaki uredjaj...
        #dokument takodjer treba pratiti koji je izabrani model za pojedini uredjaj...
        #dodadj ako nije medju kljucevima frejmova
        if uredjaj not in self.frejmovi.keys():
            self.frejmovi[uredjaj] = qtmodeli.IzborFrejmovaModel(uredjaj=uredjaj)
        #dodaj frejm na kraj reda
        self.frejmovi[uredjaj].add_frejm(frejm, tip)

    def recalculate(self):
        """
        Ako je zdan uredjaj, trigger recalculate za svaki pojedini tab
        """
        uredjaj = self.get_izabraniUredjaj()
        if uredjaj:
            komp = self.uredjaji[uredjaj]['komponente']
            if 'NO' in komp:
                popis = ['konverter', 'NO', 'NO-odaziv', 'NOx']
            else:
                popis = []
                for i in komp:
                    popis.append(i)
                    odaziv = "".join([i, '-odaziv'])
                    popis.append(odaziv)
            #recalculate za svaki pojedini tab
            for mjerenje in popis:
                self.recalculate_tab_umjeravanja(mjerenje=mjerenje)

    @helperi.activate_wait_spinner
    def recalculate_tab_umjeravanja(self, mjerenje=None):
        """metoda koja racuna parametre za tab s mjerenjem, za zadano mjerenje"""
        if self.mjerenje_isValid(mjerenje):
            print('recalculating --> {0}'.format(mjerenje))
            if mjerenje == 'konverter':
                kal = self.mjerenja['konverter']['kalkulator']
                kal.racunaj()
                tablica1 = kal.get_rezultate_konvertera()
                lista1 = kal.get_listu_efikasnosti()
                kriterij = kal.get_ec_parametar()
                output = {'rezultat':tablica1,
                          'kriterij':kriterij,
                          'lista_efikasnosti':lista1,
                          'tab':'konverter'}
                self.emit(QtCore.SIGNAL('update_tab_konverter(PyQt_PyObject)'),
                          output)
            elif mjerenje.endswith('-odaziv'):
                output = {'tab':mjerenje}
                self.emit(QtCore.SIGNAL('update_tab_odaziv(PyQt_PyObject)'),
                          output)
            else:
                kal = self.mjerenja[mjerenje]['kalkulator']
                kal.racunaj()
                tablica1 = kal.get_tablicu_rezultata()
                tablica2 = kal.get_provjeru_parametara()
                tablica3 = kal.get_slope_and_offset_map()
                output = {'umjeravanje':tablica1,
                          'testovi':tablica2,
                          'prilagodba':tablica3,
                          'tab':mjerenje}
                self.emit(QtCore.SIGNAL('update_tab_results(PyQt_PyObject)'),
                          output)
        else:
            msg = 'ne postoji mapa {0}'.format(str(mjerenje))
            logging.warning(msg)

    def dokument_to_dict(self):
        """
        Metoda je zaduzena za generiranje mape sa podacima iz dokumenta zbog
        serijalizacije (pickle).
        """
        output = {}
        output['konfig'] = self.cfg
        output['postaje'] = self.get_postaje()
        output['uredjaji'] = self.get_uredjaji()
        output['komponente'] = self.get_komponente()
        output['mjerenja'] = self.pripremi_mjerenja_za_pickle()
        frejmovi = self.pripremi_frejmove_za_pickle()
        output['frejmovi'] = frejmovi
        output['izabraniFrejm'] = self.get_izabraniFrejm()
        output['postavke'] = self.get_postavke()
        return output

    def dict_to_dokument(self, mapa):
        """
        Metoda je zaduzena da iz mape sa podacima updatea dokument. Koristi se
        za load prethodno spremljenog dokumenta.

        Metodi treba dosta vremena da se loada ... 6-7 sekundi
        """
        self.cfg = mapa['konfig']
        self.set_postaje(mapa['postaje'])
        self.set_uredjaji(mapa['uredjaji'])
        self.set_komponente(mapa['komponente'])
        mjerenja = self.pripremi_mjerenja_za_unpickle(mapa['mjerenja'])
        self.set_mjerenja(mjerenja)
        frejmovi = self.unpickle_frejmove_iz_mape(mapa['frejmovi'])
        self.set_frejmovi(frejmovi)
        self.set_izabraniFrejm(mapa['izabraniFrejm'])
        self.set_postavke(mapa['postavke'])

    def get_pocetak_i_kraj_umjeravanja(self, mjerenje=None):
        """
        Metoda dohvaca timestampove pocetka i kraja umjeravanja za trazeno mjerenje
        """
        if mjerenje in self.mjerenja:
            model = self.get_model(mjerenje=mjerenje)
            start = model.get_startUmjeravanja()
            kraj = model.get_krajUmjeravanja()
            return start, kraj
        else:
            return pd.NaT, pd.NaT
