from __future__ import print_function

import numpy as np
import unittest

from hexrd_shared.hardware import dexela_ims
from hexrd import imageseries


class TestDexelaIMS(unittest.TestCase):

    def setUp(self):
        self._nfxy = (3, 6, 6)
        a = np.zeros(self._nfxy)
        ind = np.array([0,1,2])
        a[ind, 1,2] = 1 + ind
        self.is_a = imageseries.open(None, 'array', data=a)

    def test_dtype(self):
        dims = dexela_ims.ProcessedDexelaIMS(self.is_a, [])
        img = dims[0]
        self.assertEqual(dims.dtype, img.dtype)

    def test_shape_rows(self):
        dims = dexela_ims.ProcessedDexelaIMS(self.is_a, [('add-row', 1)])
        self.assertEqual(dims.shape[0], self._nfxy[1] + 1)

    def test_shape_cols(self):
        dims = dexela_ims.ProcessedDexelaIMS(self.is_a, [('add-column', 1)])
        self.assertEqual(dims.shape[1], self._nfxy[2] + 1)

    def test_addrow_avg(self):
        op = ('add-row', 1)
        a = np.linspace(0, 3, 4, dtype=np.uint).reshape((1,2,2))
        ims_a = imageseries.open(None, 'array', data=a)
        dims = dexela_ims.ProcessedDexelaIMS(ims_a, [op])
        self.assertEqual(dims[0][1,0], 1)
        self.assertEqual(dims[0][1,1], 2)

    def test_addcol_avg(self):
        op = ('add-column', 1)
        a = np.linspace(0, 3, 4, dtype=np.uint).reshape((1,2,2))
        ims_a = imageseries.open(None, 'array', data=a)
        dims = dexela_ims.ProcessedDexelaIMS(ims_a, [op])
        self.assertEqual(dims[0][0,1], 0)
        self.assertEqual(dims[0][1,1], 2)

    def test_commute(self):
        opr = ('add-row', 1)
        opc = ('add-column', 1)
        a = np.linspace(0, 3, 4, dtype=np.uint).reshape((1,2,2))
        ims_a = imageseries.open(None, 'array', data=a)
        dims_rc = dexela_ims.ProcessedDexelaIMS(ims_a, [opr, opc])
        dims_cr = dexela_ims.ProcessedDexelaIMS(ims_a, [opc, opr])
        self.assertEqual(dims_rc[0][1,1], dims_cr[0][1,1])

    def test_pixfix(self):
        # under development
        _nfxy = (3, 4, 4)
        a = np.ones(_nfxy)
        self.is_a = imageseries.open(None, 'array', data=a)
        print("\noriginal:\n", self.is_a[0])

        dims = dexela_ims.ProcessedDexelaIMS(self.is_a, [('pixfix', None)])
        print("pixfix'd:\n", dims[0])
