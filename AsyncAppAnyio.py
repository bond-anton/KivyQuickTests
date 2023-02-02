from kivy.app import App
import anyio
import importlib


trio_spec = importlib.util.find_spec('trio')
trio_found = trio_spec is not None
if trio_found:
    async_lib = 'trio'
else:
    async_lib = 'asyncio'


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
                with anyio.move_on_after(task_timeout) as time_out_scope:
                    print(f'Task: {name} started')
                    result = await coro(*args, **kwargs)
                if time_out_scope.cancel_called:
                    result = default_result
                await sender_channel.send(result)
                print('sensor value sent, sleep for', interval)
                await anyio.sleep(interval)
                if repeats > 0:
                    repeats -= 1
        except anyio.get_cancelled_exc_class():
            print(f'Task {name} execution canceled')
        finally:
            print(f'Task {name} stopped')


class AsyncApp(App):

    __task_group = None

    async def app_func(self):
        async with anyio.create_task_group() as task_group:
            self.__task_group = task_group

            async def run_wrapper():
                await self.async_run(async_lib=async_lib)
                print('App done')
                await task_group.cancel_scope.cancel()

            task_group.start_soon(run_wrapper)

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
        sender, receiver = anyio.create_memory_object_stream(0)
        self.__task_group.start_soon(task_consumer, processor_coro, receiver,
                                     processor_name, *processor_args, **processor_kwargs)
        self.__task_group.start_soon(repetitive_task, task_coro, sender,
                                     task_name, task_default_result, interval, repeats,
                                     task_timeout, *task_args, **task_kwargs)
