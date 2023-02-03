import numpy as np
from matplotlib import pyplot as plt
from kivy.uix.boxlayout import BoxLayout
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg as FigureCanvas


class Plotter(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'

        self.fig, self.ax = plt.subplots()

        self.ax.set_xlim(0, 2*np.pi)
        self.ax.set_ylim(-1.1, 1.1)

        self.graph_widget = FigureCanvas(self.fig)
        self.add_widget(self.graph_widget)
        self.graph_widget.disabled = True

        points_x = np.linspace(0, 2 * np.pi, num=100, endpoint=True)
        points_y = np.sin(points_x)
        self.line, = self.ax.plot(points_x, points_y, 'r-')

    def update_line(self, points_x, points_y):
        self.line.set_data(points_x, points_y)
        self.fig.canvas.draw()
        # self.fig.canvas.flush_events()
