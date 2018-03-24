"""Example of imageseries subclass for Dexela images"""

from hexrd.imageseries.process import ProcessedImageSeries

class ProcessedDexelaIMS(ProcessedImageSeries):

    PIXFIX = 'pixfix'

    def __init__(self, imser, oplist, **kwargs):
        super(ProcessedImageSeries, self).__init__(imser, oplist, **kwargs)
        self.addop(self.PIXFIX, self._pixfix)

        # You could automatically apply the pixfix if you want
        self.oplist = [(self.PIXFIX, None)] + self.oplist

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
