from kivy.app import App, async_runTouchApp
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
import time

Window.size = (400, 600)


def long_calculation(m):
    time.sleep(5)
    result = {
        'x2': m * 2,
        'x3': m * 3,
        'x10': m * 10,
    }
    return result


class Container(GridLayout):

    def calculate(self):
        try:
            m = float(self.input_number.text)
        except ValueError as e:
            m = 0
        print('Long Calculation Requested')

        # result = long_calculation(m)
        # self.x2.text = '{:.2f}'.format(result['x2'])
        # self.x3.text = '{:.2f}'.format(result['x3'])
        # self.x10.text = '{:.2f}'.format(result['x10'])


class MyApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dt = 1.0

    def build(self):
        Clock.schedule_interval(self.process_tasks, self.dt)
        return Container()

    def process_tasks(self, *args):
        print('wow', args)

if __name__ == '__main__':
    # async_runTouchApp_func = partial(async_runTouchApp, async_lib='trio')
    # trio.run(async_runTouchApp_func, MyApp())
    MyApp().run()
