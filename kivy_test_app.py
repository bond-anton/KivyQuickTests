import datetime
import numpy as np
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
import trio

Window.size = (1024, 600)


async def read_sensor_value():
    result = np.random.random()
    await trio.sleep(result)
    return result


async def task_consumer(processing_coro, receive_channel, name, *args, **kwargs):
    print(f'Consumer {name} has started')
    async with receive_channel:
        async for value in receive_channel:
            await processing_coro(value, *args, **kwargs)
    print(f'Consumer {name} done')


async def repetitive_task(coro, sender_channel, name, default_result=None, interval=1, repeats=-1,
                          task_timeout=0.5, *args, **kwargs):
    async with sender_channel:
        try:
            while repeats != 0:
                print(f'Task {name} loop')
                with trio.move_on_after(task_timeout) as time_out_scope:
                    print(f'Task: {name} started')
                    result = await coro(*args, **kwargs)
                if time_out_scope.cancelled_caught:
                    result = default_result
                await sender_channel.send(result)
                print('sensor value sent, sleep for', interval)
                await trio.sleep(interval)
                if repeats > 0:
                    repeats -= 1
        except trio.Cancelled:
            print(f'Task {name} execution canceled')
        finally:
            print(f'Task {name} stopped')


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


class MyApp(App):

    dt = 1.0
    nursery = None

    def build(self):
        return Container()

    async def app_func(self):

        async with trio.open_nursery() as nursery:
            self.nursery = nursery

            async def run_wrapper():
                await self.async_run(async_lib='trio')
                print('App done')
                nursery.cancel_scope.cancel()

            nursery.start_soon(run_wrapper)
            self.spawn_task(get_datetime, self.process_datetime, interval=1, repeats=-1,
                            task_name='My clock', task_default_result='No signal from clock', task_timeout=0.5,
                            processor_name='Clock processor')

    def spawn_task(self, task_coro, processor_coro, interval=1, repeats=-1,
                   task_name=None, task_default_result=None, task_timeout=1.0, task_args=None, task_kwargs=None,
                   processor_name=None, processor_args=None, processor_kwargs=None):
        if task_name is None:
            task_name = 'Task'
        if processor_name is None:
            processor_name = 'Processor'
        if task_args is None:
            task_args = ()
        if processor_args is None:
            processor_args = ()
        if task_kwargs is None:
            task_kwargs = {}
        if processor_kwargs is None:
            processor_kwargs = {}
        sender, receiver = trio.open_memory_channel(0)
        self.nursery.start_soon(task_consumer, processor_coro, receiver,
                                processor_name, *processor_args, **processor_kwargs)
        self.nursery.start_soon(repetitive_task, task_coro, sender,
                                task_name, task_default_result, interval, repeats,
                                task_timeout, *task_args, **task_kwargs)

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
