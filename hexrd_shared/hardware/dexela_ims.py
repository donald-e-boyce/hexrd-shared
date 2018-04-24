"""Example of imageseries subclass for Dexela images"""

import numpy as np

from hexrd.imageseries.process import ProcessedImageSeries

class ProcessedDexelaIMS(ProcessedImageSeries):

    ADDROW = 'add-row'
    ADDCOL = 'add-column'

    def __init__(self, imser, oplist, **kwargs):
        super(ProcessedDexelaIMS, self).__init__(imser, oplist, **kwargs)
        self.addop(self.ADDROW, self._addrow)
        self.addop(self.ADDCOL, self._addcol)

    def _addrow(self, img, k):
        """insert row into position k"""
        shp = img.shape
        pimg = np.insert(img, k, 0, axis=0)
        if k==0:
            pimg[0] = pimg[1]
        elif k==shp[0]:
            pimg[k] = pimg[k-1]
        else: # in middle
            pimg[k] = (pimg[k-1] + pimg[k+1])/2

        return pimg

    def _addcol(self, img, k):
        """insert row into position k"""
        shp = img.shape
        pimg = np.insert(img, k, 0, axis=1)
        if k==0:
            pimg[:,0] = pimg[:,1]
        elif k==shp[0]:
            pimg[:,k] = pimg[:,k-1]
        else: # in middle
            pimg[:,k] = (pimg[:,k-1] + pimg[:,k+1])/2

        return pimg
