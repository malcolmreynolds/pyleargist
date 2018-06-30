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

class GistBwImage(Structure):
    '''Matches image_t declared in standalone_image.h'''
    _fields_ = [
        ("width", c_int),
        ("height", c_int),
        ("stride", c_int),  # stride needs to be computed separately
        ("data", POINTER(c_float))
    ]


class GistColorImage(Structure):
    '''Matches color_image_t declared in standalone_image.h'''
    _fields_ = [
        ("width", c_int),  # stride = width
        ("height", c_int),
        ("c1", POINTER(c_float)),  # R
        ("c2", POINTER(c_float)),  # G
        ("c3", POINTER(c_float)),  # B
    ]

# Setup argument & return types for color gist
libleargist.color_gist_scaletab.argtypes = (
    POINTER(GistColorImage), c_int, c_int, POINTER(c_int))
libleargist.color_gist_scaletab.restype = c_void_p

# Setup argument & return types
libleargist.bw_gist_scaletab.argtypes = (
    POINTER(GistBwImage), c_int, c_int, POINTER(c_int))
libleargist.bw_gist_scaletab.restype = c_void_p


def bw_gist(im, nblocks=4, orientations=(8, 8, 4)):

    scales = len(orientations)
    orientations = np.array(orientations, dtype=np.int32)

    if im.shape[0] < 8 or im.shape[1] < 8:
        raise ValueError(
            "image size must at least be (8, 8), got %s" % im.size)

    im = np.ascontiguousarray(im, dtype=np.float32)

    gbwi = GistBwImage(
        im.shape[1],  # Width is the SECOND element of the shape tuple
        im.shape[0],
        im.shape[1],
        im.ctypes.data_as(POINTER(c_float)))

    # We don't need a *3 because it's black & white. Note the useless
    # looking brackets here are HIGHLY NECESSARY!! difference between
    # ending up with c_float * 320 (which we want) and c_float * 4 * 4 * 20
    descriptors = c_float * (nblocks * nblocks * orientations.sum())
    addr = libleargist.bw_gist_scaletab(
        pointer(gbwi), nblocks, scales,
        orientations.ctypes.data_as(POINTER(c_int)))

    if addr == None:
        # This can happen when the block we give it contains NaN, Inf, etc.
        raise ValueError("Descriptor invalid")

    return np.ctypeslib.as_array(descriptors.from_address(addr))


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
    arr = np.fromstring(im.tobytes(), np.uint8)
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
    addr = libleargist.color_gist_scaletab(
        pointer(gci), nblocks, scales,
        orientations.ctypes.data_as(POINTER(c_int)))

    if addr == None:
        # This can happen when the block we give it contains NaN, Inf, etc.
        raise ValueError("Descriptor invalid")

    return np.ctypeslib.as_array(descriptors.from_address(addr))
