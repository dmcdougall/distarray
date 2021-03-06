"""
Tests for distarray ufuncs.

Many of these tests require a 4-engine cluster to be running locally.
"""

import unittest
import warnings
import numpy as np
from IPython.parallel import Client
from distarray.client import Context
from numpy.testing import assert_array_equal


# For these tests we use a global context
c = Client()
context = Context(c[:])


def add_checkers(cls, ops, checker_name):
    """Helper function to dynamically add a list of tests.

    Add tests to cls for each op in ops. Where checker_name is
    the name of the test you want to call on each op. So we add:

        TestCls.test_op_name(): return op_checker(op_name)

    for each op.
    """
    op_checker = getattr(cls, checker_name)

    def check(op_name):
        return lambda self: op_checker(self, op_name)

    for op_name in ops:
        op_test_name = 'test_' + op_name
        setattr(cls, op_test_name, check(op_name))


class TestDistArrayUfuncs(unittest.TestCase):
    """Test ufuncs operating on distarrays"""

    @classmethod
    def setUpClass(cls):
        # Standard data
        cls.a = np.arange(1, 99)
        cls.b = np.ones_like(cls.a)*2
        # distributed array data
        cls.da = context.fromndarray(cls.a)
        cls.db = context.fromndarray(cls.b)

    def check_binary_op(self, op_name):
        """Check binary operation for success.

        Check the two- and three-arg ufunc versions as well as the
        method version attached to a LocalArray.
        """
        op = getattr(context, op_name)
        ufunc = getattr(np, op_name)
        with warnings.catch_warnings():
            # ignore inf, NaN warnings etc.
            warnings.simplefilter("ignore", category=RuntimeWarning)
            expected = ufunc(self.a, self.b)
            result = op(self.da, self.db)
        assert_array_equal(result.toarray(), expected)

    def check_unary_op(self, op_name):
        """Check unary operation for success.

        Check the two- and three-arg ufunc versions as well as the
        method version attached to a LocalArray.
        """
        op = getattr(context, op_name)
        ufunc = getattr(np, op_name)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            expected = ufunc(self.a)
            result = op(self.da)
        assert_array_equal(result.toarray(), expected)


class TestSpecialMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Standard data
        cls.a = np.arange(1, 99)
        cls.b = np.ones_like(cls.a)*2
        # distributed array data
        cls.da = context.fromndarray(cls.a)
        cls.db = context.fromndarray(cls.b)

    def check_op(self, op_name):
        distop = getattr(self.da, op_name)
        numpyop = getattr(self.a, op_name)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            result = distop(self.db)
            expected = numpyop(self.b)
        assert_array_equal(result.toarray(), expected)


unary_ops = ('absolute', 'arccos', 'arccosh', 'arcsin', 'arcsinh',
             'arctan', 'arctanh', 'conjugate', 'cos', 'cosh', 'exp',
             'expm1', 'invert', 'log', 'log10', 'log1p', 'negative',
             'reciprocal', 'rint', 'sign', 'sin', 'sinh', 'sqrt',
             'square', 'tan', 'tanh',)

binary_ops = ('add', 'arctan2', 'bitwise_and', 'bitwise_or',
              'bitwise_xor', 'divide', 'floor_divide', 'fmod', 'hypot',
              'left_shift', 'multiply', 'power', 'remainder',
              'right_shift', 'subtract', 'true_divide', 'less',
              'less_equal', 'equal', 'not_equal', 'greater',
              'greater_equal', 'mod',)

binary_special_methods = ('__lt__', '__le__', '__eq__', '__ne__', '__gt__',
                          '__ge__', '__add__', '__sub__', '__mul__',
                          '__floordiv__', '__mod__', '__pow__', '__lshift__',
                          '__rshift__', '__and__', '__xor__', '__or__',
                          '__radd__', '__rsub__', '__rmul__', '__rfloordiv__',
                          '__rmod__', '__rpow__', '__rlshift__', '__rrshift__',
                          '__rand__', '__rxor__', '__ror__',)

# There is no divmod function in numpy. And there is no __div__
# attribute on ndarrays.
problematic_special_methods = ('__divmod__', '__rdivmod__', '__div__')

add_checkers(TestDistArrayUfuncs, binary_ops, 'check_binary_op')
add_checkers(TestDistArrayUfuncs, unary_ops, 'check_unary_op')
add_checkers(TestSpecialMethods, binary_special_methods, 'check_op')

if __name__ == '__main__':
    unittest.main(verbosity=2)
