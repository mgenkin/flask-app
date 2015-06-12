import scikits.audiolab
import numpy as np
from scikits.audiolab import Sndfile
from skimage.viewer import ImageViewer
from scikits.audiolab import Format
from scikits.audiolab import Sndfile


def sh(im):
    v = ImageViewer(im)
    v.show()


def sn(snd):
    s = Sndfile("test.wav", mode="w", Format(format="wav", encoding="float64", endianness="file"), channels=1, samplerate=44100)
    s.write_frames(snd)

