import os
from ctypes import POINTER
from ctypes import pointer
from ctypes import Structure
from ctypes import c_float
from ctypes import c_int
from ctypes import c_void_p
import numpy as np

leargist_folder = os.path.abspath(__file__).rsplit(os.path.sep, 1)[0]
leargist_name = "_gist"
libleargist = np.ctypeslib.load_library(leargist_name, leargist_folder)

class GistColorImage(Structure):
    _fields_ = [
        ("width", c_int), # stride = width
        ("height", c_int),
        ("c1", POINTER(c_float)), # R
        ("c2", POINTER(c_float)), # G
        ("c3", POINTER(c_float)), # B
    ]

libleargist.color_gist_scaletab.argtypes = (
    POINTER(GistColorImage), c_int, c_int, POINTER(c_int))
libleargist.color_gist_scaletab.restype = c_void_p

def color_gist(im, nblocks=4, orientations=(8, 8, 4)):
    """Compute the GIST descriptor of an RGB image"""
    scales = len(orientations)
    orientations = np.array(orientations, dtype=np.int32)

    # check minimum image size
    if im.size[0] < 8 or im.size[1] < 8:
        raise ValueError(
            "image size should at least be (8, 8), got %r" % (im.size,))

    # ensure the image is encoded in RGB
    im = im.convert(mode='RGB')

    # build the lear_gist color image C datastructure
    arr = np.fromstring(im.tostring(), np.uint8)
    arr.shape = list(im.size) + [3]
    arr = arr.transpose(2, 0, 1)
    arr = np.ascontiguousarray(arr, dtype=np.float32)

    gci = GistColorImage(
        im.size[0],
        im.size[1],
        arr[0].ctypes.data_as(POINTER(c_float)),
        arr[1].ctypes.data_as(POINTER(c_float)),
        arr[2].ctypes.data_as(POINTER(c_float)))

    descriptors = c_float * (nblocks * nblocks * orientations.sum() * 3)
    addr= libleargist.color_gist_scaletab(
        pointer(gci), nblocks, scales,
        orientations.ctypes.data_as(POINTER(c_int)))
    return np.ctypeslib.as_array(descriptors.from_address(addr))

