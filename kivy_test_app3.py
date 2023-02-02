import datetime
import numpy as np

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window

from AsyncAppTrio import AsyncApp

import trio


Window.size = (1024, 600)


async def read_sensor_value():
    result = np.random.random()
    await trio.sleep(result)
    return result


async def long_calculation(m):
    await trio.sleep(5)
    result = {
        'x2': m * 2,
        'x3': m * 3,
        'x10': m * 10,
    }
    return result


async def get_datetime():
    await trio.sleep(0.1)
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Container(GridLayout):

    def calculate(self):
        self.calculate_button.disabled = True
        app = App.get_running_app()
        try:
            m = float(self.input_number.text)
        except ValueError:
            m = 0
        print('Long Calculation Requested')
        default = {'x2': 'x2', 'x3': 'x3', 'x10': 'x10'}
        app.spawn_task(long_calculation, app.process_calculation_results,
                       task_name='Long calculation', task_default_result=default, interval=0, repeats=1,
                       task_timeout=10, task_args=(m,), task_kwargs=None,
                       processor_name='Calculation processor', processor_args=None, processor_kwargs=None)


class MyApp(AsyncApp):

    dt = 0

    def build(self):
        return Container()

    def on_start(self):
        self.spawn_task(get_datetime, self.process_datetime, interval=1, repeats=-1,
                        task_name='My clock', task_default_result='No signal from clock', task_timeout=0.5,
                        processor_name='Clock processor')
        self.spawn_task(self.sin_scope, self.process_scope, interval=0.1, repeats=-1,
                        task_name='My scope', task_default_result={'x': np.zeros(100), 'y': np.zeros(100)},
                        task_timeout=0.5,
                        processor_name='Scope processor')

    async def process_calculation_results(self, value):
        print(value)
        self.root.ids.x2.text = '{:.2f}'.format(value['x2'])
        self.root.ids.x3.text = '{:.2f}'.format(value['x3'])
        self.root.ids.x10.text = '{:.2f}'.format(value['x10'])
        self.root.ids.calculate_button.disabled = False

    async def process_datetime(self, value):
        self.root.ids.datetime.text = value

    async def sin_scope(self):
        x = np.linspace(0, 2 * np.pi, num=100, endpoint=True)
        y = np.sin(x + 2 * np.pi / 200 * self.dt)
        self.dt += 1
        if self.dt == 200:
            self.dt = 0
        return {'x': x, 'y': y}

    async def process_scope(self, value):
        # print(value)
        self.root.ids.plotter.update_line(value['x'], value['y'])


if __name__ == '__main__':
    trio.run(MyApp().app_func)
