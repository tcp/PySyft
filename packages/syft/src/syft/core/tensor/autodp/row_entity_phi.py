from ..passthrough import PassthroughTensor
from ..passthrough import is_acceptable_simple_type
from ..passthrough import implements

import numpy as np


class RowEntityPhiTensor(PassthroughTensor):

    def __init__(self, rows, check_shape=True):
        super().__init__(rows)

        if check_shape:
            shape = rows[0].shape
            for row in rows[1:]:
                if (shape != row.shape):
                    raise Exception(f"All rows in RowEntityPhiTensor must match: {shape} != {row.shape}")

    @property
    def shape(self):
        return [len(self.child)] + list(self.child[0].shape[1:])

    def __add__(self, other):

        if is_acceptable_simple_type(other) or len(self.child) == len(other.child):
            new_list = list()
            for i in range(len(self.child)):
                if is_acceptable_simple_type(other):
                    new_list.append(self.child[i] + other)
                else:
                    new_list.append(self.child[i] + other.child[i])
            return RowEntityPhiTensor(rows=new_list, check_shape=False)
        else:
            raise Exception(f"Tensor dims do not match for __add__: {len(self.child)} != {len(other.child)}")

    def __sub__(self, other):

        if is_acceptable_simple_type(other) or len(self.child) == len(other.child):
            new_list = list()
            for i in range(len(self.child)):
                if is_acceptable_simple_type(other):
                    new_list.append(self.child[i] - other)
                else:
                    new_list.append(self.child[i] - other.child[i])
            return RowEntityPhiTensor(rows=new_list, check_shape=False)
        else:
            raise Exception(f"Tensor dims do not match for __sub__: {len(self.child)} != {len(other.child)}")

    def __mul__(self, other):

        if is_acceptable_simple_type(other) or len(self.child) == len(other.child):
            new_list = list()
            for i in range(len(self.child)):
                if is_acceptable_simple_type(other):
                    new_list.append(self.child[i] * other)
                else:
                    new_list.append(self.child[i] * other.child[i])
            return RowEntityPhiTensor(rows=new_list, check_shape=False)
        else:
            raise Exception(f"Tensor dims do not match for __mul__: {len(self.child)} != {len(other.child)}")

    def __truediv__(self, other):

        if is_acceptable_simple_type(other) or len(self.child) == len(other.child):
            new_list = list()
            for i in range(len(self.child)):
                if is_acceptable_simple_type(other):
                    new_list.append(self.child[i] / other)
                else:
                    new_list.append(self.child[i] / other.child[i])
            return RowEntityPhiTensor(rows=new_list, check_shape=False)
        else:
            raise Exception(f"Tensor dims do not match for __truediv__: {len(self.child)} != {len(other.child)}")

    def repeat(self, repeats, axis=None):

        if axis == None:
            raise Exception("Conservatively, RowEntityPhiTensor doesn't yet support repeat(axis=None)")

        if axis == 0 or axis == -len(self.shape):
            new_list = list()
            for r in range(repeats):
                for row in self.child:
                    new_list.append(row)
            return RowEntityPhiTensor(rows=new_list, check_shape=False)

        elif axis > 0:
            new_list = list()
            for row in self.child:
                new_list.append(row.repeat(repeats, axis=axis - 1))
            return RowEntityPhiTensor(rows=new_list, check_shape=False)

        # axis is negative
        elif abs(axis) < len(self.shape):
            new_list = list()
            for row in self.child:
                new_list.append(row.repeat(repeats, axis=axis))
            return RowEntityPhiTensor(rows=new_list, check_shape=False)

        else:
            raise Exception("'axis' arg is negative and strangely large... not sure what to do.")

    def reshape(self, *shape):

        if shape[0] != self.shape[0]:
            raise Exception(
                "For now, you can't reshape the first dimension because that would probably require creating a gamma tensor.")

        new_list = list()
        for row in self.child:
            new_list.append(row.reshape(shape[1:]))

        return RowEntityPhiTensor(rows=new_list, check_shape=False)

    def sum(self, *args, axis=None, **kwargs):

        if axis is None or axis == 0:
            raise Exception(
                "For now, you can't sum the entire vector into a scalar or sum across dim 0 without needing a GammaTensor.")

        new_list = list()
        for row in self.child:
            new_list.append(row.sum(*args, axis=axis, **kwargs))

        return RowEntityPhiTensor(rows=new_list, check_shape=False)

    def transpose(self, *dims):

        if dims[0] != 0:
            raise Exception("Can't move dim 0 in RowEntityPhiTensor at this time")

        new_dims = list(np.array(dims[1:]) )

        new_list = list()
        for row in self.child:
            new_list.append(row.transpose(*new_dims))

        return RowEntityPhiTensor(rows=new_list, check_shape=False)


@implements(RowEntityPhiTensor, np.expand_dims)
def expand_dims(a, axis):

    if axis == 0:
        raise Exception("Currently, we don't have functionality for axis=0 but we could with a bit more work.")

    new_rows = list()
    for row in a.child:
        new_rows.append(np.expand_dims(a, axis))

    return RowEntityPhiTensor(rows=new_rows, check_shape=False)