import unittest
import numpy as np
import distarray as da
from distutils.version import StrictVersion
from numpy.testing import assert_array_equal
from distarray.testing import comm_null_passes, MpiTestCase


VALID_DIST_TYPES = {'n', 'b', 'c', 'u'}


class DapTestMixin(object):

    """Base test class for DAP test cases.

    You must overload `more_setUp` and add a `self.larr` LocalArray to
    test.
    """

    @comm_null_passes
    def test_has_export(self):
        self.assertTrue(hasattr(self.larr, '__distarray__'))

    @comm_null_passes
    def test_export_keys(self):
        required_keys = set(("__version__", "buffer", "dim_data"))
        export_data = self.larr.__distarray__()
        exported_keys = set(export_data.keys())
        self.assertEqual(required_keys, exported_keys)

    @comm_null_passes
    def test_export_buffer(self):
        """See if we actually export a buffer."""
        export_data = self.larr.__distarray__()
        memoryview(export_data['buffer'])

    @comm_null_passes
    def test_export_version(self):
        """Check type of version."""
        export_data = self.larr.__distarray__()
        StrictVersion(export_data['__version__'])

    @comm_null_passes
    def test_export_dim_data_len(self):
        """Test if there is a `dimdict` for every dimension."""
        export_data = self.larr.__distarray__()
        dim_data = export_data['dim_data']
        self.assertEqual(len(dim_data), self.larr.ndim)

    @comm_null_passes
    def test_export_dim_data_keys(self):
        export_data = self.larr.__distarray__()
        dim_data = export_data['dim_data']
        required_keys = {"dist_type", "size"}
        for dimdict in dim_data:
            self.assertTrue(required_keys <= set(dimdict.keys()))

    @comm_null_passes
    def test_export_dim_data_values(self):
        export_data = self.larr.__distarray__()
        dim_data = export_data['dim_data']
        for dd in dim_data:
            self.assertIn(dd['dist_type'], VALID_DIST_TYPES)
            self.assertIsInstance(dd['size'], int)

            for key in ('proc_grid_rank', 'proc_grid_size',  'block_size', 'padding'):
                try:
                    self.assertIsInstance(dd[key], int)
                except KeyError:
                    pass
            try:
                self.assertIsInstance(dd['periodic'], bool)
            except KeyError:
                pass

    @comm_null_passes
    def test_round_trip_equality(self):
        larr = da.LocalArray.from_distarray(self.larr, comm=self.comm)
        self.assertEqual(larr.shape, self.larr.shape)
        self.assertEqual(larr.dist, self.larr.dist)
        self.assertEqual(larr.grid_shape, self.larr.grid_shape)
        self.assertEqual(larr.comm_size, self.larr.comm_size)
        self.assertEqual(larr.ndistdim, self.larr.ndistdim)
        self.assertEqual(larr.distdims, self.larr.distdims)
        self.assertEqual(larr.comm.Get_topo(), self.larr.comm.Get_topo())
        self.assertEqual(len(larr.maps), len(self.larr.maps))
        self.assertEqual(larr.local_shape, self.larr.local_shape)
        self.assertEqual(larr.local_array.shape, self.larr.local_array.shape)
        self.assertEqual(larr.local_array.dtype, self.larr.local_array.dtype)
        assert_array_equal(larr.local_array, self.larr.local_array)

    @comm_null_passes
    def test_round_trip_identity(self):
        larr = da.LocalArray.from_distarray(self.larr, comm=self.comm)
        if self.comm.Get_rank() == 0:
            idx = (0,) * larr.local_array.ndim
            larr.local_array[idx] = 99
        assert_array_equal(larr.local_array, self.larr.local_array)
        #self.assertIs(larr.local_array.data, self.larr.local_array.data)


class TestDapBasic(DapTestMixin, MpiTestCase):

    @comm_null_passes
    def more_setUp(self):
        self.larr = da.LocalArray((16, 16), grid_shape=(4,), comm=self.comm)


class TestDapUint(DapTestMixin, MpiTestCase):

    @comm_null_passes
    def more_setUp(self):
        self.larr = da.LocalArray((16, 16), dtype='uint8', grid_shape=(4,),
                                  comm=self.comm, buf=None)


class TestDapComplex(DapTestMixin, MpiTestCase):

    @comm_null_passes
    def more_setUp(self):
        self.larr = da.LocalArray((16, 16), dtype='complex128',
                                  grid_shape=(4,), comm=self.comm, buf=None)


class TestDapExplicitNoDist0(DapTestMixin, MpiTestCase):

    @comm_null_passes
    def more_setUp(self):
        self.larr = da.LocalArray((16, 16), dist={0: 'b', 1: 'n'},
                                  grid_shape=(4,), comm=self.comm)


class TestDapExplicitNoDist1(DapTestMixin, MpiTestCase):

    @comm_null_passes
    def more_setUp(self):
        self.larr = da.LocalArray((30, 60), dist={0: 'n', 1: 'b'},
                                  grid_shape=(4,), comm=self.comm)


class TestDapTwoDistDims(DapTestMixin, MpiTestCase):

    @comm_null_passes
    def more_setUp(self):
        self.larr = da.LocalArray((53, 77), dist={0: 'b', 1: 'b'},
                                  grid_shape=(2, 2), comm=self.comm)


class TestDapThreeBlockDims(DapTestMixin, MpiTestCase):

    def get_comm_size(self):
        return 12

    @comm_null_passes
    def more_setUp(self):
        self.larr = da.LocalArray((53, 77, 99),
                                  dist={0: 'b', 1: 'b', 2: 'b'},
                                  grid_shape=(2, 2, 3),
                                  comm=self.comm)


class TestDapCyclicDim(DapTestMixin, MpiTestCase):

    @comm_null_passes
    def more_setUp(self):
        self.larr = da.LocalArray((53, 77),
                                  dist={0: 'c'},
                                  grid_shape=(4,),
                                  comm=self.comm)


class TestDapCyclicBlock(DapTestMixin, MpiTestCase):

    @comm_null_passes
    def more_setUp(self):
        self.larr = da.LocalArray((53, 77),
                                  dist={0: 'c', 1: 'b'},
                                  grid_shape=(2, 2),
                                  comm=self.comm)


class TestDapThreeMixedDims(DapTestMixin, MpiTestCase):

    @comm_null_passes
    def more_setUp(self):
        self.larr = da.LocalArray((53, 77, 99), dtype='float64',
                                  dist={0: 'b', 1: 'n', 2: 'c'},
                                  grid_shape=(2, 2),
                                  comm=self.comm)


class TestDapLopsided(DapTestMixin, MpiTestCase):

    def get_comm_size(self):
        return 2

    @comm_null_passes
    def more_setUp(self):
        if self.comm.Get_rank() == 0:
            arr = np.arange(20)
        elif self.comm.Get_rank() == 1:
            arr = np.arange(30)

        self.larr = da.LocalArray((50,), dtype='float64',
                             dist={0: 'b', 1: 'n'},
                             grid_shape=(2,), comm=self.comm, buf=arr)

    @comm_null_passes
    def test_values(self):
        if self.comm.Get_rank() == 0:
            assert_array_equal(np.arange(20), self.larr.local_array)
        elif self.comm.Get_rank() == 1:
            assert_array_equal(np.arange(30), self.larr.local_array)

        larr = da.LocalArray.from_distarray(self.larr, comm=self.comm)
        if self.comm.Get_rank() == 0:
            assert_array_equal(np.arange(20), larr.local_array)
        elif self.comm.Get_rank() == 1:
            assert_array_equal(np.arange(30), larr.local_array)


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit:
        pass
