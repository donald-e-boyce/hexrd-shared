import numpy as np

from hexrd.xrd.transforms_CAPI import \
     anglesToGVec, \
     gvecToDetectorXY

class generate_tth_eta(object):
    """
    """
    def __init__(self, plane_data, instrument,
                 eta_min=0., eta_max=360.,
                 pixel_size=(0.05, 0.25)):
        # tth stuff
        tth_ranges = plane_data.getTThRanges()
        self._tth_min = np.min(tth_ranges)
        self._tth_max = np.max(tth_ranges)

        # etas
        self._eta_min = np.radians(eta_min)
        self._eta_max = np.radians(eta_max)

        self._tth_pixel_size = pixel_size[0]
        self._eta_pixel_size = pixel_size[1]

        self.detectors = instrument.detectors

    @property
    def tth_min(self):
        return self._tth_min
    @tth_min.setter
    def tth_min(self, x):
        assert x < self.tth_max,\
          'tth_min must be < tth_max (%f)' % (self._tth_max)
        self._tth_min = x

    @property
    def tth_max(self):
        return self._tth_max
    @tth_max.setter
    def tth_max(self, x):
        assert x > self.tth_min,\
          'tth_max must be < tth_min (%f)' % (self._tth_min)
        self._tth_max = x

    @property
    def tth_range(self):
        return self.tth_max - self.tth_min

    @property
    def tth_pixel_size(self):
        return self._tth_pixel_size
    @tth_pixel_size.setter
    def tth_pixel_size(self, x):
        self._tth_pixel_size = float(x)

    @property
    def eta_min(self):
        return self._eta_min
    @eta_min.setter
    def eta_min(self, x):
        assert x < self.eta_max,\
          'eta_min must be < eta_max (%f)' % (self.eta_max)
        self._eta_min = x

    @property
    def eta_max(self):
        return self._eta_max
    @eta_max.setter
    def eta_max(self, x):
        assert x > self.eta_min,\
          'eta_max must be < eta_min (%f)' % (self.eta_min)
        self._eta_max = x

    @property
    def eta_range(self):
        return self.eta_max - self.eta_min

    @property
    def eta_pixel_size(self):
        return self._eta_pixel_size
    @eta_pixel_size.setter
    def eta_pixel_size(self, x):
        self._eta_pixel_size = float(x)

    @property
    def ntth(self):
        return int(np.ceil(np.degrees(self.tth_range)/self.tth_pixel_size))
    @property
    def neta(self):
        return int(np.ceil(np.degrees(self.eta_range)/self.eta_pixel_size))
    @property
    def shape(self):
        return (self.neta, self.ntth)

    @property
    def angular_grid(self):
        tth_vec = np.radians(self.tth_pixel_size*(np.arange(self.ntth)))\
            + self.tth_min
        eta_vec = np.radians(self.eta_pixel_size*(np.arange(self.neta)))\
            + self.eta_min
        return np.meshgrid(eta_vec, tth_vec, indexing='ij')


    """ ####### METHODS ####### """
    def warp_image(self, image_dict):
        """
        """
        angpts = self.angular_grid
        dummy_ome = np.zeros((self.ntth*self.neta))

        lcount = 0
        wimg = np.zeros(self.shape)
        for detector_id in self.detectors:
            #lcount +=1
            #if lcount > 4: break
            print "detector: ", detector_id, image_dict[detector_id].shape
            panel = self.detectors[detector_id]

            gpts = anglesToGVec(
                np.vstack([
                    angpts[1].flatten(),
                    angpts[0].flatten(),
                    dummy_ome,
                    ]).T, bHat_l=panel.bvec)
            xypts = gvecToDetectorXY(
                gpts,
                panel.rmat, np.eye(3), np.eye(3),
                panel.tvec, np.zeros(3), np.zeros(3),
                beamVec=panel.bvec)
            if panel.distortion is not None:
                dfunc = panel.distortion[0]
                dparams = panel.distortion[1]
                xypts = dfunc(xypts, dparams)

            wimg += panel.interpolate_bilinear(
                xypts, image_dict[detector_id],
                pad_with_nans=False).reshape(self.neta, self.ntth)
        return wimg

    def tth_to_pixel(self, tth):
        """convert two-theta value to pixel value (float) along two-theta axis"""
        return np.degrees(tth - self.tth_min)/self.tth_pixel_size
