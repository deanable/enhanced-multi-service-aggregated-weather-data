from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MatplotlibCanvas(QWidget):
    """
    A custom widget to embed a Matplotlib figure in a PyQt6 application.
    """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """
        Initializes the canvas.
        """
        super().__init__(parent)

        # Create a Matplotlib figure
        self.figure = Figure(figsize=(width, height), dpi=dpi)

        # Create a canvas widget from the figure
        self.canvas = FigureCanvas(self.figure)

        # The main axes for plotting. Can be treated like a subplot.
        self.axes = self.figure.add_subplot(111)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def clear(self):
        """
        Clears the plot on the canvas.
        """
        self.axes.clear()

    def draw(self):
        """
        Redraws the canvas.
        """
        self.canvas.draw()
