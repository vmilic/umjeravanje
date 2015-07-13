# -*- coding: utf-8 -*-
"""
Created on Wed May 13 13:50:05 2015

@author: DHMZ-Milic
"""
import os


def parse_name_for_serial(fajl):
    """
    File name parser za serial broj uredjaja.
    """
    name = os.path.split(fajl)[1]
    name = name.lower()
    step1 = [element.strip() for element in name.split(sep='-')]
    step2 = [element.lstrip('0') for element in step1]
    i = step2.index('conc1min')
    step3 = step2[1:i]
    if step3[-1] == 'e':
        serial = step3[-2]
    else:
        serial = step3[-1]
    moguci = []
    moguci.append(serial)
    moguci.append("".join([serial, 'e']))
    moguci.append("".join([serial, 'E']))
    moguci.append("-".join([serial, 'e']))
    moguci.append("-".join([serial, 'E']))
    return moguci
