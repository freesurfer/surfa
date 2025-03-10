import surfa as sf
from surfa.image.framed import FramedImage

class TimeSeries(FramedImage):

    def __init__(self, data):
        """
        Time-Series class defining an array with data frames.

        Parameters
        ----------
        data : array_like
            Image data array.
        """

        basedim = data.ndim - 1
        super().__init__(basedim=basedim, data=data)


    def save(self, filename, fmt=None):
        super().save(filename, fmt=fmt, intent=sf.core.framed.FramedArrayIntents.timeseries)

