#!/usr/bin/env python3

"""
Converts sequence of images to compact PDF while removing speckles,
bleedthrough, etc.

Credits to github@mzucker
https://github.com/mzucker/noteshrink/
"""


from __future__ import print_function
import sys
import os
import numpy as np
from utilities.digicon_classes import image_location
from subprocess import call

# in some installation of PIL, Image can be imported directly
try:
    import Image, ImageFile
except ImportError:
    from PIL import Image, ImageFile

from scipy.cluster.vq import kmeans, vq

# ignores division warnings caused in numpy
np.seterr(divide='ignore', invalid='ignore')


def whiteboard(input_image):
    input_filename = os.path.join(input_image.images_path, input_image.image_name)
    # os.system("./white.sh " + input_filename + " " + os.path.join(input_image.temp_path, "white_" +
    # input_image.image_name))
    call([os.path.join(os.path.dirname(os.path.realpath(__file__)), "white.sh"), input_filename,
          os.path.join(input_image.temp_path, "white_" + input_image.image_name)])


def quantize(image, bits_per_channel=None):

    """
    Reduces the number of bits per channel in the given image.
    """

    if bits_per_channel is None:
        bits_per_channel = 6

    assert image.dtype == np.uint8

    shift = 8-bits_per_channel
    halfbin = (1 << shift) >> 1

    return ((image.astype(int) >> shift) << shift) + halfbin


def pack_rgb(rgb):

    """
    Packs a 24-bit RGB triples into a single integer,
    works on both arrays and tuples.
    """

    orig_shape = None

    if isinstance(rgb, np.ndarray):
        assert rgb.shape[-1] == 3
        orig_shape = rgb.shape[:-1]
    else:
        assert len(rgb) == 3
        rgb = np.array(rgb)

    rgb = rgb.astype(int).reshape((-1, 3))

    packed = (rgb[:, 0] << 16 |
              rgb[:, 1] << 8 |
              rgb[:, 2])

    if orig_shape is None:
        return packed
    else:
        return packed.reshape(orig_shape)


def unpack_rgb(packed):

    """
    Unpacks a single integer or array of integers into one or more
    24-bit RGB values.
    """

    orig_shape = None

    if isinstance(packed, np.ndarray):
        assert packed.dtype == int
        orig_shape = packed.shape
        packed = packed.reshape((-1, 1))

    rgb = ((packed >> 16) & 0xff,
           (packed >> 8) & 0xff,
           packed & 0xff)

    if orig_shape is None:
        return rgb
    else:
        return np.hstack(rgb).reshape(orig_shape + (3,))


def get_bg_color(image, bits_per_channel=None):

    """
    Obtains the background color from an image or array of RGB colors
    by grouping similar colors into bins and finding the most frequent
    one.
    """

    assert image.shape[-1] == 3

    quantized = quantize(image, bits_per_channel).astype(int)
    packed = pack_rgb(quantized)

    unique, counts = np.unique(packed, return_counts=True)

    packed_mode = unique[counts.argmax()]

    return unpack_rgb(packed_mode)


def rgb_to_sv(rgb):

    """Convert an RGB image or array of RGB colors to saturation and
    value, returning each one as a separate 32-bit floating point array or
    value.
    """

    if not isinstance(rgb, np.ndarray):
        rgb = np.array(rgb)

    axis = len(rgb.shape)-1
    cmax = rgb.max(axis=axis).astype(np.float32)
    cmin = rgb.min(axis=axis).astype(np.float32)
    delta = cmax - cmin

    saturation = delta.astype(np.float32) / cmax.astype(np.float32)
    saturation = np.where(cmax == 0, 0, saturation)

    value = cmax/255.0

    return saturation, value


def percent(string):
    """
    Convert a string (i.e. 85) to a fraction (i.e. .85).
    """
    return float(string)/100.0


def load(input_filename):

    """Load an image with Pillow and convert it to numpy array. Also
returns the image DPI in x and y as a tuple."""

    try:
        pil_img = Image.open(input_filename)
    except IOError:
        sys.stderr.write('warning: error opening {}\n'.format(
            input_filename))
        return None, None

    if pil_img.mode != 'RGB':
        pil_img = pil_img.convert('RGB')

    if 'dpi' in pil_img.info:
        dpi = pil_img.info['dpi']
    else:
        dpi = (300, 300)

    img = np.array(pil_img)

    return img, dpi


def sample_pixels(img):

    """
    Pick a fixed percentage of pixels in the image, returned in random
    order.
    """

    pixels = img.reshape((-1, 3))
    num_pixels = pixels.shape[0]
    num_samples = int(num_pixels*float(.05))

    idx = np.arange(num_pixels)
    np.random.shuffle(idx)

    return pixels[idx[:num_samples]]


def get_fg_mask(bg_color, samples):

    """
    Determine whether each pixel in a set of samples is foreground by
    comparing it to the background color. A pixel is classified as a
    foreground pixel if either its value or saturation differs from the
    background by a threshold.
    """

    s_bg, v_bg = rgb_to_sv(bg_color)
    s_samples, v_samples = rgb_to_sv(samples)

    s_diff = np.abs(s_bg - s_samples)
    v_diff = np.abs(v_bg - v_samples)

    return ((v_diff >= float(.25)) |
            (s_diff >= float(.20)))


def get_palette(samples, return_mask=False, kmeans_iter=40):

    """
    Extract the palette for the set of sampled RGB values. The first
    palette entry is always the background color; the rest are determined
    from foreground pixels by running K-means clustering. Returns the
    palette, as well as a mask corresponding to the foreground pixels.
    """

    bg_color = get_bg_color(samples, 6)

    fg_mask = get_fg_mask(bg_color, samples)

    centers, _ = kmeans(samples[fg_mask].astype(np.float32),
                        7,
                        iter=kmeans_iter)

    palette = np.vstack((bg_color, centers)).astype(np.uint8)

    if not return_mask:
        return palette
    else:
        return palette, fg_mask


def apply_palette(img, palette):

    """
    Apply the pallete to the given image. The first step is to set all
    background pixels to the background color; then, nearest-neighbor
    matching is used to map each foreground color to the closest one in
    the palette.
    """

    bg_color = palette[0]

    fg_mask = get_fg_mask(bg_color, img)

    orig_shape = img.shape

    pixels = img.reshape((-1, 3))
    fg_mask = fg_mask.flatten()

    num_pixels = pixels.shape[0]

    labels = np.zeros(num_pixels, dtype=np.uint8)

    labels[fg_mask], _ = vq(pixels[fg_mask], palette)

    return labels.reshape(orig_shape[:-1])


def save(output_filename, labels, palette, dpi):

    """
    Save the label/palette pair out as an indexed PNG image.  This
    optionally saturates the pallete by mapping the smallest color
    component to zero and the largest one to 255, and also optionally sets
    the background color to pure white.
    """

    palette = palette.astype(np.float32)
    pmin = palette.min()
    pmax = palette.max()
    palette = 255 * (palette - pmin)/(pmax-pmin)
    palette = palette.astype(np.uint8)

    output_img = Image.fromarray(labels, 'P')
    output_img.putpalette(palette.flatten())
    # convert to 8-bit black and white
    output_img = output_img.convert("L")
    output_img.save(output_filename, dpi=dpi)


def notescan_main(input_image):

    """
    main function that processes the input file
    :param input_image: path to the image file to be loaded
    :return: None
    """
    input_filename = os.path.join(input_image.images_path, input_image.image_name)
    img, dpi = load(input_filename)
    output_filename = os.path.join(input_image.images_path, input_image.image_name)

    samples = sample_pixels(img)
    palette = get_palette(samples)

    labels = apply_palette(img, palette)

    ImageFile.MAXBLOCK = max(ImageFile.MAXBLOCK, (4 * img.size [0] * img.size [1]) + 10)
    save(output_filename, labels, palette, dpi)


if __name__ == '__main__':

    # uncomment below lines for debugging
    # notescan_main("input.jpg")
    pass
