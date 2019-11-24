import ctypes
from PIL import Image


class PageMakernoteHeader(ctypes.Structure):
    pass


PageMakernoteHeader_fieldtable = [
    # (offset, name, size)
    (0x1E, 'id', 12 * ctypes.c_char),  # ?
    (0x2A, 'index', ctypes.c_ubyte),  # page index
    (None, 'count', ctypes.c_ubyte),  # number of pages
    (0x35,)  # END OF TABLE
]


class PageMakernoteFooter(ctypes.Structure):
    pass


PageMakernoteFooter_fieldtable = [
    # (offset, name, size)
    (0x41,)  # END OF TABLE
]


class PageMakernote(ctypes.Structure):
    pass


PageMakernote_fieldtable = [
    # (offset, name, size)
    (None, 'header', PageMakernoteHeader),
    (None, 'body', 0xDC00 * ctypes.c_ubyte),
    (None, 'footer', PageMakernoteFooter),
    (None,)
]


class ScenarioName(ctypes.Structure):
    _fields_ = [
        ('len', ctypes.c_uint),
        ('data', 31 * ctypes.c_char)
    ]

    def __str__(self):
        return self.data[:self.len].decode('utf-8')


class ScenarioDescription(ctypes.Structure):
    _fields_ = [
        ('data', 282 * ctypes.c_char)
    ]

    def __str__(self):
        return self.data.decode('utf-8')


class ScenarioHeader(ctypes.Structure):
    pass


ScenarioHeader_fieldtable = [
    # (offset, name, size)
    (0x0014, 'title', ScenarioName),
    (0x010E, 'description', ScenarioDescription),
    (0x04FC,)  # END OF TABLE
]


class Point(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.c_ubyte),
        ('y', ctypes.c_ubyte)
    ]


class AreaName(ctypes.Structure):
    _fields_ = [
        ('len', ctypes.c_uint),
        ('data', 12 * ctypes.c_char)
    ]

    def __str__(self):
        return self.data[:self.len].decode('utf-8')


class Area(ctypes.Structure):
    pass


Area_fieldtable = [
    # (offset, name, size)
    (0, 'name', AreaName),
    (0x28,)  # END OF TABLE
]


class HeightMap(ctypes.Structure):
    _fields_ = [
        ('data', 225 * (225 * ctypes.c_ubyte))
    ]

    def to_image(self):
        im = Image.new('L', (225, 225))
        pix = im.load()
        for x in range(225):
            for y in range(225):
                pix[x, y] = self.data[x][y]
        return im


class BuildingMap(ctypes.Structure):
    _fields_ = [
        ('data', 224 * (224 * ctypes.c_uint))
    ]

    def to_image(self):
        im = Image.new('RGBA', (224, 224))
        pix = im.load()
        for x in range(224):
            for y in range(224):
                c = self.data[x][y]
                pix[x, y] = tuple(c.to_bytes(4, byteorder='little'))
        return im


class Layer(ctypes.Structure):
    _fields_ = [
        ('data', 224 * (224 * ctypes.c_ushort))
    ]

    def to_image(self):
        im = Image.new('RGB', (224, 224))
        pix = im.load()
        for x in range(224):
            for y in range(224):
                c = self.data[x][y]
                pix[x, y] = tuple(c.to_bytes(3, byteorder='little'))
        return im


class Author(ctypes.Structure):
    _fields_ = [
        ('len', ctypes.c_uint),
        ('data', 50 * ctypes.c_char)
    ]

    def __str__(self):
        return self.data[:self.len].decode('utf-8')


class Message(ctypes.Structure):
    _fields_ = [
        ('data', 182 * ctypes.c_char)
    ]

    def __str__(self):
        return self.data.decode('utf-8')


class ScenarioBody(ctypes.Structure):
    pass


ScenarioBody_fieldtable = [
    # (offset, name, size)
    (0x0000B2, 'height_map', HeightMap),
    (None, 'building_map', BuildingMap),
    (None, 'layers', 10 * Layer),
    (None, 'areas', '16 * Area'),
    (None, 'points', '5 * (5 * Point)'),
    (None, 'wakaranai', 2 * ctypes.c_ubyte),
    (None, 'cities', '4 * Area'),
    (0x173017, 'messages', 40 * (50 * Message)),
    (0x279CF3, 'author', Author),
    (0x27B07C,)  # END OF TABLE
]


def prepare_fields():
    list = [
        (PageMakernoteHeader, PageMakernoteHeader_fieldtable),
        (PageMakernoteFooter, PageMakernoteFooter_fieldtable),
        (PageMakernote, PageMakernote_fieldtable),
        (ScenarioHeader, ScenarioHeader_fieldtable),
        (Area, Area_fieldtable),
        (ScenarioBody, ScenarioBody_fieldtable),
    ]

    for pair in list:
        classname, fieldtable = pair
        fields = []
        address = 0
        unknown_index = 0
        for row in fieldtable:
            offset, *field = row
            if offset and (address != offset):
                fields.append(('unknown%04d' % unknown_index,
                               ctypes.c_ubyte * (offset - address)))
                unknown_index += 1
                address = offset
            if not(field):
                break
            [name, ctype] = field
            if isinstance(ctype, str):
                ctype = eval(ctype)
            fields.append(tuple([name, ctype]))
            address += ctypes.sizeof(ctype)
        classname._pack_ = 1
        classname._fields_ = fields


prepare_fields()
