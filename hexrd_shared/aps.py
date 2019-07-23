"""Parse APS .par files"""
import numpy as np


class ParFields(object):
    # 32, 33, 34, 36, 37 (1-based)
    ostart = 31
    ostop = 32
    nframes = 33
    name = 35
    scan = 36


class ParParser(object):

    def __init__(self, parfile):
        self.parfile = parfile
        with open(parfile, 'r') as p:
            self.parlines = p.readlines()
        self.split_lines = []
        for l in self.parlines:
            self.split_lines.append(l.split())

    def matchlines(self, name):
        """return lines matching string"""
        result = []
        for l in self.parlines:
            if name in l:
                result.append(l)
        return result

    @property
    def samples(self):
        """names of samples"""
        names = [sl[ParFields.name] for sl in self.split_lines]
        return np.unique(names)

    def imageseries(self, name, flips, panels=['ge1', 'ge2']):
        """generate imageseries from par file"""
        Pf = ParFields
        lines = self.matchlines(name)
        files = ''
        for l in lines:
            flds = l.split()
            files += '\n' + _scanfile_tmpl.format(
                name=name, num=flds[Pf.scan_num], suf=panels[0])
        print(files)

    def scan_info(self, name):
        """return scan info matching name"""
        Pf = ParFields
        lines = self.matchlines(name)
        for l in lines:
            flds = l.split()
            print(flds[Pf.name], flds[Pf.scan_num], flds[Pf.ostart],\
              flds[Pf.ostop], flds[Pf.nframes])
        pass


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
