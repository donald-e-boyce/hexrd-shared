"""Parse CHESS spec files to find scan information

QUESTIONS/COMMENTS:
* This only processes "slew_omega" type scans. Do we need "tseries" too?
"""
from collections import namedtuple
import os
import re

import numpy as np

from hexrd import imageseries
from hexrd.imageseries.process import ProcessedImageSeries as Pims

fs_root = '/nfs/chess/raw'
re_scan = re.compile('^#S ')
re_eff = re.compile('effectively slew_ome')

flip_dflt = "h"
darkframes_dflt = 120
save_fmt = "frame-cache"

class ScanTypes:
    omega = 'slew_ome'
    tseries = 'tseries'

RunInfo = namedtuple('RunInfo', ['cycle', 'station', 'user', 'name'])

_fields = ['id', 'type', 'ome0', 'ome1', 'steps', 'exposure']
ScanRequest = namedtuple('ScanRequest', _fields)
del _fields

# Image Options: panels = list of strings, number from spec.log
ImageOpts = namedtuple('ImageOpts', ['panels', 'number'])


def _get_raw_dir(info):
    raw_tmpl = fs_root + '/%(cycle)s/%(station)s/%(user)s/%(name)s'
    return raw_tmpl % info._asdict()


def _make_dark(ims):
    """build dark"""
    return imageseries.stats.median(ims, nframes=darkframes_dflt)


class Parser(object):

    def __init__(self, runinfo):
        self.runinfo = runinfo
        self.requests = []
        self.effective = []
        self._get_requests()
        self.scans = []
        self._get_scans()

    def _get_scans(self):
        """Break log file into text for each scan"""
        speclog = os.path.join(self.rawdir, 'spec.log')

        with open(speclog, "r") as f:
            scantext = []
            for l in f:
                if re_scan.match(l):
                    # start new scan
                    self.scans.append(scantext)
                    scantext = []
                scantext.append(l)
            self.scans.append(scantext)


    def _get_requests(self):
        """List of available scan numbers"""
        speclog = os.path.join(self.rawdir, 'spec.log')
        with open(speclog, "r") as f:
            needs_eff = False
            for l in f:
                if re_scan.match(l):
                    if needs_eff:
                        # No matching effective request, scan probably terminated
                        self.effective.append(None)
                    needs_eff = True

                    # New scan, waiting for response
                    flds = l.split()
                    scanid = int(flds[1])
                    scantype = flds[2]
                    if scantype == ScanTypes.omega:
                        ome0 = float(flds[3]),
                        ome1 = float(flds[4]),
                        steps = int(flds[5]),
                        exposure = float(flds[6])
                    else:
                        ome0 = None
                        ome1 = None
                        steps = None
                        exposure = None

                    req = ScanRequest(
                        id=scanid,
                        type=scantype,
                        ome0=ome0,
                        ome1=ome1,
                        steps=steps,
                        exposure=exposure
                    )
                    self.requests.append(req)

                if re_eff.search(l):
                    # Got Response: assumes exposure not changed
                    flds = l.split()
                    effreq = ScanRequest(
                        id=scanid,
                        type=flds[8],
                        ome0=float(flds[9]),
                        ome1=float(flds[10]),
                        steps=int(flds[11]),
                        exposure=req.exposure
                    )
                    self.effective.append(effreq)
                    needs_eff = False
        if needs_eff:
            self.effective.append(None)

        nr, ne = len(self.requests), len(self.effective)
        amsg = "Request and response lists do not have same length: %d, %d" % (nr, ne)
        assert nr == ne, amsg

    def imagefiles(self, scanid, opts):
        imfiles = []
        imtmpl = '%(raw)s/%(scan)s/%(panel)s/%(panel)s_%(num)0.6d.h5'
        raw = self.rawdir
        num = opts.number
        for p in opts.panels:
            d = dict(raw=raw, scan=scanid, panel=p, num=num)
            imfiles.append(imtmpl % d)

        return imfiles

    @property
    def rawdir(self):
        return _get_raw_dir(self.runinfo)
