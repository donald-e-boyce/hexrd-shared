"""Parse APS .par files"""
from collections import namedtuple
import os

import numpy as np

from hexrd import imageseries
from hexrd.imageseries.process import ProcessedImageSeries as Pims

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


flip_dflt = "h"
darkframes_dflt = 100

def process_raw(yml_ims, threshold=10):
    raw = imageseries.open(yml_ims, 'imagefiles')
    pims = Pims(raw, [('dark', make_dark(ims)), ('flip', 'h')])


def make_dark(ims):
    """build dark"""
    return imageseries.stats.median(ims, nframes=darkframes_dflt)


class ParParser(object):

    def __init__(self, parfile, image_dir="."):
        self.parfile = parfile
        self.image_dir = image_dir

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


    def write_raw(self, sample, scans, panels):
        for p in panels:
            self._imageseries(sample, scans, p)

    def _imageseries(self, sample, scans, panel):
        """generate yaml for imagefiles type imageseries"""
        # use first scan number for name in yaml
        scan_fname = "%s-0%s.%s"
        # scan_fname = "%s_0%s.%s" % (sample, scans[0], panel)
        files = " ".join([scan_fname % (sample, s, panel) for s in scans])
        # find omega info

        d = dict(
            dir=os.path.join(self.image_dir, panel),
            files=files,
            empty=1,
            panel="ge1",
            meta=self._make_meta(sample, scans, panel)
        )
        print(_imagefiles_tmpl % d)

    def _make_meta(self, sample, scans, panel):
        """build metadata"""
        meta = self.scan_info(sample)[scans[0]]
        meta['panel'] = panel
        return _meta_tmpl % meta

def _rounde4(x):
    return int(np.round(1e4*float(x)))

# ==================== Image series yaml template

_imagefiles_tmpl = r"""
image-files:
  directory: %(dir)s
  files: %(files)s

options:
  empty-frames: %(empty)s
  max-frames: 0
%(meta)s
"""

_meta_tmpl = r"""
meta:
  panel: %(panel)s
  ostart: %(ostart)s
  ostop: %(ostop)s
"""
