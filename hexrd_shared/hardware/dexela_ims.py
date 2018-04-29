"""Example of imageseries subclass for Dexela images"""

import numpy as np

from hexrd.imageseries.process import ProcessedImageSeries

class ProcessedDexelaIMS(ProcessedImageSeries):

    ADDROW = 'add-row'
    ADDCOL = 'add-column'
    PIXFIX = 'pixfix'

    def __init__(self, imser, oplist, **kwargs):
        super(ProcessedDexelaIMS, self).__init__(imser, oplist, **kwargs)
        self.addop(self.ADDROW, self._addrow)
        self.addop(self.ADDCOL, self._addcol)
        self.addop(self.PIXFIX, self._pixfix)

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

    def _pixfix(self, img, ddummy):
        pimg=img

        rows=pimg.shape[0]
        cols=pimg.shape[1]

        pimg=np.insert(pimg,rows/2,0,axis=0)
        pimg=np.insert(pimg,cols/2,0,axis=1)


        pimg[rows/2,1:-1]=(pimg[rows/2-1,0:-2]+pimg[rows/2+1,0:-2]\
                           +pimg[rows/2-1,2:]+pimg[rows/2+1,2:])/8\
                           +(pimg[rows/2-1,1:-1]+pimg[rows/2+1,1:-1])/4
        pimg[1:-1,cols/2]=(pimg[0:-2,cols/2-1]+pimg[0:-2,cols/2+1]\
                           +pimg[2:,cols/2-1]+pimg[2:,cols/2+1])/8\
                           +(pimg[1:-1,cols/2-1]+pimg[1:-1,cols/2+1])/4

        #special cases
        pimg[rows/2,cols/2]=(pimg[rows/2-1,cols/2-1]\
                             +pimg[rows/2-1,cols/2+1]\
                             +pimg[rows/2+1,cols/2-1]\
                             +pimg[rows/2+1,cols/2+1])/4#center
        pimg[0,cols/2]=(pimg[0,cols/2-1]+pimg[0,cols/2+1])/2#top
        pimg[rows/2,0]=(pimg[rows/2-1,0]+pimg[rows/2+1,0])/2#left
        pimg[rows/2,-1]=(pimg[rows/2-1,-1]+pimg[rows/2+1,-1])/2#right
        pimg[-1,cols/2]=(pimg[-1,cols/2-1]+pimg[0,cols/2+1])/2#bottom

        return pimg
