import numpy as np
import unittest

from hexrd_shared.hardware import dexela_ims
from hexrd import imageseries


class TestDexelaIMS(unittest.TestCase):

    def setUp(self):
        self._nfxy = (3, 4, 4)
        a = np.zeros(self._nfxy)
        ind = np.array([0,1,2])
        a[ind, 1,2] = 1 + ind
        self.is_a = imageseries.open(None, 'array', data=a)

    def test_oplist(self):
        dims = dexela_ims.ProcessedDexelaIMS(self.is_a, [])
        self.assertEqual(len(dims.oplist), 1)

    def test_shape(self):
        dims = dexela_ims.ProcessedDexelaIMS(self.is_a, [])
        self.assertEqual(dims.shape[0], self._nfxy[1] + 1)
        self.assertEqual(dims.shape[1], self._nfxy[2] + 1)

    def test_dtype(self):
        dims = dexela_ims.ProcessedDexelaIMS(self.is_a, [])
        img = dims[0]
        self.assertEqual(dims.dtype, img.dtype)
