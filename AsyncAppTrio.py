from kivy.app import App
import trio


async_lib = 'trio'


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


class AsyncApp(App):

    __nursery = None

    async def app_func(self):

        async with trio.open_nursery() as nursery:
            self.__nursery = nursery

            async def run_wrapper():
                await self.async_run(async_lib='trio')
                print('App done')
                nursery.cancel_scope.cancel()

            nursery.start_soon(run_wrapper)

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
        self.__nursery.start_soon(task_consumer, processor_coro, receiver,
                                  processor_name, *processor_args, **processor_kwargs)
        self.__nursery.start_soon(repetitive_task, task_coro, sender,
                                  task_name, task_default_result, interval, repeats,
                                  task_timeout, *task_args, **task_kwargs)
