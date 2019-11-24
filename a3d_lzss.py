class Lzss():
    N = 1 << 12
    THRESHOLD = 3

    @classmethod
    def read_byte(cls, f):
        c = f.read(1)
        if c:
            return c[0]

    @classmethod
    def read_data(cls, f):
        data_bytes = f.read(2)
        if len(data_bytes) == 2:
            data_int = int.from_bytes(data_bytes, byteorder='big')
            length = (data_int >> 12) + cls.THRESHOLD
            offset = (data_int & 0x0FFF) + 1
            return (length, offset)

    @classmethod
    def decode(cls, source, size):
        result = bytearray(size)
        buffer = bytearray(cls.N)
        p = 0
        r = 0
        flags = 0

        while p < size:
            flags <<= 1
            if not(flags & 0xFF):
                c = cls.read_byte(source)
                if c is None:
                    break
                flags = (c << 8) | 0xFF
            if not(flags & 0x8000):
                c = cls.read_byte(source)
                if c is None:
                    break
                result[p] = c
                p += 1
                buffer[r] = c
                r = (r+1) & (cls.N-1)
            else:
                data = cls.read_data(source)
                if data is None:
                    break
                (length, offset) = data
                for _ in range(0, min(length, size - p)):
                    c = buffer[r - offset]
                    result[p] = c
                    p += 1
                    buffer[r] = c
                    r = (r+1) & (cls.N-1)

        return bytes(result)
