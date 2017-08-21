import sys

import cPickle
import yaml
import numpy as np

from hexrd import imageseries
from hexrd import instrument
from view_multipanel import InstrumentViewer as IView

# plane data
def load_pdata(cpkl):
    with file(cpkl, "r") as matf:
        matlist = cPickle.load(matf)
    return matlist[0].planeData

# images
def load_images(yml):
    return imageseries.open(yml, "image-files")

# instrument
def load_instrument(yml):
    with file(yml, 'r') as f:
        icfg = yaml.load(f)
    return instrument.HEDMInstrument(instrument_config=icfg)

# options
def load_options(yml):
    with file(yml, 'r') as f:
        icfg = yaml.load(f)
    return icfg

if __name__ == '__main__':
    #
    #  Run viewer
    #
    if len(sys.argv) < 5:
        print "*** needs four args, got ", len(sys.argv) - 1
        print "usage: run <instrument [yml]> <images [yml]> <material [cpl]> <options [yml]>"
        sys.exit()
    instr = load_instrument(sys.argv[1])
    ims = load_images(sys.argv[2])
    pdata = load_pdata(sys.argv[3])
    options = load_options(sys.argv[4])
    print options

    iv = IView(instr, ims, pdata, options)
