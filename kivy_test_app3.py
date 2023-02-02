import datetime
import numpy as np

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window

from AsyncAppTrio import AsyncApp

import trio


Window.size = (400, 600)


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

    def build(self):
        return Container()

    def on_start(self):
        self.spawn_task(get_datetime, self.process_datetime, interval=1, repeats=-1,
                        task_name='My clock', task_default_result='No signal from clock', task_timeout=0.5,
                        processor_name='Clock processor')

    async def process_calculation_results(self, value):
        print(value)
        self.root.ids.x2.text = '{:.2f}'.format(value['x2'])
        self.root.ids.x3.text = '{:.2f}'.format(value['x3'])
        self.root.ids.x10.text = '{:.2f}'.format(value['x10'])
        self.root.ids.calculate_button.disabled = False

    async def process_datetime(self, value):
        self.root.ids.datetime.text = value


if __name__ == '__main__':
    trio.run(MyApp().app_func)
