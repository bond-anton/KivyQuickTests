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
        # self.line, = self.ax.plot(points_x, points_y, 'r-')
        self.line, = self.ax.plot(points_x, points_y, 'r-', animated=True)

        self.bg = None
        # self.fig.draw_artist(self.line)

    def on_kv_post(self, base_widget):
        # print('BBOX:', self.fig.bbox)
        pass
        # plt.pause(1)

        # self.ax.draw_artist(self.line)

    def update_line(self, points_x, points_y):
        if self.bg is None:
            print('ZZZZZZZZZZZZZ')
            self.fig.canvas.draw()
            self.bg = self.fig.canvas.copy_from_bbox(self.fig.bbox)
            self.ax.draw_artist(self.line)
            self.fig.canvas.draw()
        print('BBOX:', self.fig.bbox)
        self.fig.canvas.restore_region(self.bg)
        # update the artist, neither the canvas state nor the screen have changed
        self.line.set_data(points_x, points_y)
        # re-render the artist, updating the canvas state, but not the screen
        self.ax.draw_artist(self.line)
        # copy the image to the GUI state, but screen might not be changed yet
        self.fig.canvas.blit(self.fig.bbox)
        # flush any pending GUI events, re-painting the screen if needed
        # self.fig.canvas.draw()
        self.fig.canvas.flush_events()
