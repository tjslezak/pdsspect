import numpy as np

from .pdsspect_image_set import ginga_colors
from .roi_plot import ROIPlotModel, ROIPlotController, ROIPlotWidget, ROIPlot


class ROILinePlotModel(ROIPlotModel):
    """Model for ROI Line plot and widget"""

    @property
    def wavelengths(self):
        """:obj:`list` : Sorted list of wavelengths in the :attr:`image_set`"""
        wavelengths = []
        for image in self.image_set.images:
            if not np.isnan(image.wavelength):
                wavelengths.append(image.wavelength)
        return sorted(wavelengths)

    def data_with_color(self, color):
        """Get the data inside the ROI color if the image has a wavelength

        Parameters
        ----------
        color : :obj:`str`
            The color of the ROI

        Returns
        -------
        data : :obj:`list` or :class:`numpy.ndarray`
            Sorted list of arrays of data by wavelength
        """

        images = []
        rows, cols = self.image_set.get_coordinates_of_color(color)
        for image in self.image_set.images:
            if not np.isnan(image.wavelength):
                images.append(image)
        images = sorted(images, key=lambda image: image.wavelength)
        data = [image.data[rows, cols] for image in images]
        return data


class ROILinePlotController(ROIPlotController):
    """Controller for :class:`ROILinePlotWidget`"""

    pass


class ROILinePlotWidget(ROIPlotWidget):
    """Widget to hold line plot and check boxes

    Parameters
    ----------
    model : :class:`ROILinePlotModel`
        The model

    Attributes
    ----------
    model : :class:`ROILinePlotModel`
        The model
    controller : :class:`ROILinePlotController`
        The controller
    roi_line_plot : :class:`ROILinePlot`
        Line plot of ROI data
    """

    def __init__(self, model):
        self.model = model
        self.roi_line_plot = ROILinePlot(model)
        self.controller = ROILinePlotController(model, self)
        super(ROILinePlotWidget, self).__init__(model)
        self.setWindowTitle('ROI Line Plot')

    def _register_set_at_index(self, index):
        self.model.image_sets[index].register(self.roi_line_plot)
        self.model.image_sets[index].register(self)

    def _set_layout(self):
        self.main_layout.addLayout(self.view_boxes_layout, 0, 1, 1, 2)
        self.main_layout.addWidget(self.roi_line_plot, 1, 0, 2, 2)
        self.main_layout.addLayout(self.checkbox_layout, 1, 2)
        self.main_layout.setColumnStretch(1, 1)
        self.main_layout.setRowStretch(1, 1)
        self.setLayout(self.main_layout)


class ROILinePlot(ROIPlot):
    """Line plot of ROI data

    Parameters
    ----------
    model : :class:`ROILinePlotModel`
        The model

    Attributes
    ----------
    model : :class:`ROILinePlotModel`
        The model
    """

    def __init__(self, model):
        self.model = model
        model.register(self)
        self.controller = ROILinePlotController(model, self)
        super(ROILinePlot, self).__init__(model)

    def set_data(self):
        """Set the data of the selected colors on the line plot"""
        self._ax.cla()
        wavelengths = self.model.wavelengths
        for color in self.model.selected_colors:
            rgb = ginga_colors.lookup_color(color)
            data = self.model.data_with_color(color)
            means = [array.mean() for array in data]
            stdevs = [np.std(array) for array in data]
            self._ax.errorbar(
                x=wavelengths,
                y=means,
                yerr=stdevs,
                fmt='-s',
                color=rgb,
                capsize=5,
            )
        self._ax.set_xlabel(
            xlabel=r'Wavelength ($%s$)' % (self.model.unit),
            color='w',
            fontsize=9,
        )
        self._ax.set_ylabel(
            ylabel='Pixel Value',
            color='w',
            fontsize=9,
        )
        self.draw()
