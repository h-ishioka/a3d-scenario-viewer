import io
from PIL import Image

from a3d_lzss import *
from a3d_struct import *


class ScenarioPage():
    MAKERNOTE_TAG_ID = 0x927C
    IMAGE_HEADER_HEIGHT = 64
    HEADER_SIZE = 0x35
    FOOTER_SIZE = 0x41

    def __init__(self, header, body, footer):
        self.header = header
        self.body = body
        self.footer = footer

    @classmethod
    def open(cls, filename):
        im = Image.open(filename)

        # get makernote data from image
        makernote_data = cls.get_makernote_data_from_image(im)
        header = makernote_data[:cls.HEADER_SIZE]
        makernote_body = makernote_data[cls.HEADER_SIZE:-cls.FOOTER_SIZE]
        footer = makernote_data[-cls.FOOTER_SIZE:]

        # get grayscale data from image
        grayscale_body = cls.get_grayscale_data_from_image(im)

        body = makernote_body + grayscale_body

        return ScenarioPage(header, body, footer)

    @classmethod
    def get_makernote_data_from_image(cls, im):
        makernote = im._getexif()[cls.MAKERNOTE_TAG_ID]
        return makernote

    @classmethod
    def get_grayscale_data_from_image(cls, im):
        crop_rect = (0, cls.IMAGE_HEADER_HEIGHT, im.width, im.height)
        im = im.crop(crop_rect)
        im = im.convert('L')
        im = cls.downscale(im)
        bit2array = im.tobytes()
        bit8array = cls.bit2array_to_bit8array(bit2array)
        return bit8array

    @classmethod
    def downscale(cls, image):
        new_size = (image.width // 2, image.height // 2)
        new_image = Image.new(image.mode, new_size)
        pix = image.load()
        newpix = new_image.load()
        for j in range(new_image.height):
            for i in range(new_image.width):
                newpix[i, j] = (pix[i*2, j*2] + pix[i*2+1, j*2] +
                                pix[i*2, j*2+1] + pix[i*2+1, j*2+1]) // 4
        return new_image

    @classmethod
    def bit2array_to_bit8array(cls, bit2array):
        bit8array = bytearray(len(bit2array) // 4)
        for i in range(len(bit2array)):
            p = i >> 2
            bit8array[p] = (bit8array[p] << 2) | (bit2array[i] >> 6)
        return bit8array


class Scenario(object):
    def __init__(self, header, body, footer):
        self.header = header
        self.body = body
        self.footer = footer

    @classmethod
    def frompages(cls, *pages):
        raw = b''
        for page in pages:
            raw += page.body
        st = io.BytesIO(raw)

        header = ScenarioHeader()
        header_bytes = st.read(ctypes.sizeof(header))
        ctypes.memmove(
            ctypes.addressof(header),
            header_bytes,
            ctypes.sizeof(header))

        body = ScenarioBody()
        body_bytes = Lzss.decode(st, ctypes.sizeof(body))
        ctypes.memmove(
            ctypes.addressof(body),
            body_bytes,
            ctypes.sizeof(body))

        footer = st.read()

        scenario = Scenario(header, body, footer)
        scenario.raw = raw
        return scenario
