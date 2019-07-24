"""Parse APS .par files"""
from collections import namedtuple

import numpy as np

KeyIndex = namedtuple('KeyIndex', ['key', 'index'])
_mtsY =  KeyIndex('mtsY', 24)
_mtsX =  KeyIndex('mtsX', 25)
_ostart = KeyIndex('ostart', 31)
_ostop = KeyIndex('ostop', 32)
_nframes = KeyIndex('nframes', 33)
_exposure = KeyIndex('exposure', 34)
_sample = KeyIndex('sample', 35)
_scan = KeyIndex('scan', 36)

_daterange = range(5) # first five fields are date

class ParParser(object):

    def __init__(self, parfile):
        self.parfile = parfile
        with open(parfile, 'r') as p:
            self.parlines = p.readlines()
        self.split_lines = []
        for l in self.parlines:
            self.split_lines.append(l.split())

    def _matchlines(self, sample):
        """return line numbers matching sample"""
        result = []
        for lnum, sl in enumerate(self.split_lines):
            if sl[_sample.index] == sample:
                result.append(lnum)

        return result

    @property
    def samples(self):
        """names of samples"""
        names = [sl[_sample.index] for sl in self.split_lines]
        return np.unique(names)

    def scans(self, sample=None):
        """names of scans matching sample if given, else all scans"""

        slines = self.split_lines
        if sample is not None:
            slines = []
            for sl in self.split_lines:
                if sample in sl:
                    slines.append(sl)

        scans = [sl[_scan.index] for sl in slines]
        return np.unique(scans)

    def scan_info(self, sample):
        """return scan info matching name

        return data as a dictionary of dictionaries indexed by scan string
"""
        # mtsX = int(np.round(1e4*float(pars[25])))
        # mtsY = int(np.round(1e4*float(pars[24])))

        scand = dict()
        lnums = self._matchlines(sample)
        for l in lnums:
            flds = self.split_lines[l]
            scand[flds[_scan.index]] = {
                _ostart.key: flds[_ostart.index],
                _ostop.key: flds[_ostop.index],
                _nframes.key: flds[_nframes.index],
                _mtsX.key: _rounde4(flds[_mtsX.index]),
                _mtsY.key: _rounde4(flds[_mtsY.index]),
                _exposure.key: float(flds[_exposure.index]),
                'date': ' '.join([flds[i] for i in _daterange])
                }

        return scand

    def imageseries(self, name, flips, panels=['ge1', 'ge2']):
        """generate imageseries from par file"""
        Pf = ParFields
        lines = self.matchlines(name)
        files = ''
        for l in lines:
            flds = l.split()
            files += '\n' + _scanfile_tmpl.format(
                name=name, num=flds[Pf.scan], suf=panels[0])
        print(files)


def _rounde4(x):
    return int(np.round(1e4*float(x)))

_scanfile_tmpl = "{name}_0{num}.{suf}"
_imagefiles_tmpl = """
image-files:
  directory: {image_dir}
  files: "{image_files}"

options:
  empty-frames: 0
  max-frames: 0
meta:
  panel: {panel}
  omega: "! load-numpy-array {omega_file}"
"""
