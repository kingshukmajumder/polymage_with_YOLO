class Kpt(object):

    def __init__(octave, layer, row, column):
        self.octave = octave
        self.layer = layer
        self.row = (float)row
        self.column = (float)column

def make_Kpt(octave, layer, row, column):
    kpt = Kpt(octave, layer, row, column)
    return kpt