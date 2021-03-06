

def to_bits(seq):
    return [_to_bit(c) for c in seq]


def _to_bit(symbol):
    return "01".index(symbol)


def to_seq(bits):
    return "".join("01"[bit] for bit in bits)

