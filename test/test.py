from PIL import Image
import leargist

from numpy.linalg import norm
from numpy.testing import assert_equal
from scipy.misc import imread


im = Image.open('lear_gist/ar.ppm')
image = imread(im.filename)
gist = leargist.color_gist(im),
gist_numpy = leargist.color_gist_numpy(image)
assert_equal(
    leargist.color_gist(im),
    leargist.color_gist_numpy(image)
)
