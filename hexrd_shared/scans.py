"""Module for reading Hexrd grains.out files
"""
import numpy as np


# Functions for converting grains.out files to npz format
def read_txt_grains(fname):
    """Read hexrd grains output file"""

    # Note: (21) fields named below with an underscore are not yet used
    #
    # Fields from grains.out header:
    """grain ID         completeness         chi2
       xi[0]            xi[1]                xi[2]
       tVec_c[0]        tVec_c[1]            tVec_c[2]
       vInv_s[0]        vInv_s[1]            vInv_s[2]    vInv_s[4]*sqrt(2)    vInv_s[5]*sqrt(2)    vInv_s[6]*sqrt(2)
       ln(V[0,0])       ln(V[1,1])           ln(V[2,2])   ln(V[1,2])           ln(V[0,2])           ln(V[0,1])"""

    # Use shortened names in construction of numpy data type.

    d = {'names': ('id', 'completeness', 'chisq',
                   'ori_0', 'ori_1', 'ori_2',
                   'cen_0', 'cen_1', 'cen_2',
                   'vi0', 'vi1', 'vi2', 'vi3', 'vi4', 'vi5',
                   'lnV00', 'lnV11', 'lnV22', 'lnV12', 'lnV02', 'lnV01'),
         'formats': ('i4',) + 20*('f4',)}

    return np.loadtxt(fname, dtype=d)


def read_txt_dataset(tmpl, keys, savenpz=False):
    """Read sequence of grains.out files

    tmpl is a template for the filename
    keys is a sequence of keys to apply to the template


    RETURNS
    d - a dictionary of grain data arrays by keys
"""
    d = dict()
    for k in keys:
        fname = tmpl % k
        d[k] = read_txt_grains(fname)

    if savenpz:
        np.savez_compressed(savenpz, **d)

    return d


class ScanSet(object):
    """Class for processing grains.out files"""
    def __init__(self, scand):
        """Instantiate with a dictionary of scans"""
        self._scand = scand

    def __getitem__(self, key):
        return Scan(self._scand[key])

    @property
    def keys(self):
        """Available keys for the scan dictionary"""
        return list(self._scand.keys())

    def scan(self, key):
        """Return grain data for given scan

        key - the identifier for the scan, usually a 0-padded numeric string

        RETURNS

        glist - grain list for the scan
"""
        return Scan(self.scand[key])

    def get_data(self, attr, scankeys):
        """Return numpy array of data for an attribtute over multiple scans"""
        arrays = (getattr(self[s], attr) for s in scankeys)
        return np.stack(arrays, axis=1)


class Scan(object):
    """Grain data for a single scan"""

    def __init__(self, scan_dt):
        """Build object from scan data"""
        self.scan = scan_dt

    @property
    def completeness(self):
        return self.scan['completeness']

    @property
    def chi_squared(self):
        return self.scan['chisq']

    @property
    def orientations(self):
        return np.vstack((self.scan['ori_0'], self.scan['ori_1'], self.scan['ori_2'])).T

    @property
    def centroids(self):
        return np.vstack((self.scan['cen_0'], self.scan['cen_1'], self.scan['cen_2'])).T

    @property
    def strains(self):
        """logarithmic strains"""
        return np.vstack((
            self.scan['lnV00'], self.scan['lnV11'], self.scan['lnV22'],
            self.scan['lnV12'], self.scan['lnV02'], self.scan['lnV01']
        )).T
