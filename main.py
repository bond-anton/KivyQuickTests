import trio
import numpy as np


async def main():
    # send_channel, receive_channel = trio.open_memory_channel(0)
    async with trio.open_nursery() as nursery:
        # nursery.start_soon(producer, send_channel, 'P1')
        # nursery.start_soon(consumer, receive_channel, 'C1')
        # nursery.start_soon(producer, send_channel2, 'P2')
        # nursery.start_soon(consumer, receive_channel2, 'C2')
        for i in range(10):
            print('I am here')
            send_channel2, receive_channel2 = trio.open_memory_channel(0)
            nursery.start_soon(consumer, receive_channel2, 'C2')
            nursery.start_soon(single_task_action, long_operation, send_channel2, 'TASK1', None, 0.5, 10)
            await trio.sleep(2)
        nursery.cancel_scope.cancel()


async def producer(send_channel, name):
    async with send_channel:
        try:
            print(f'Producer {name} has started')
            i = 0
            while True:
                with trio.move_on_after(5) as time_out_scope:
                    await trio.sleep(np.random.random()*10)
                    await send_channel.send(f'FROM: {name}, MSG: message {i}')
                if time_out_scope.cancelled_caught:
                    print('X' * 10)
                    print(f'Producer {name} timeout: {time_out_scope.cancelled_caught}')
                    print('X' * 10)
                i += 1
        except trio.Cancelled:
            print(f'Producer {name} execution canceled')
        finally:
            print(f'Producer {name} done')
    print(f'Producer {name} leaving the game')


async def consumer(receive_channel, name):
    print(f'Consumer {name} has started')
    async with receive_channel:
        async for value in receive_channel:
            print(f'<== {name}: got value {value!r}')
    print(f'Consumer {name} done')


async def long_operation(m):
    result = np.random.random()
    await trio.sleep(result)
    return result * m


async def single_task_action(coro, sender_channel, name, default=None, timeout=0.5, *args, **kwargs):
    async with sender_channel:
        try:
            with trio.move_on_after(timeout) as time_out_scope:
                print(f'Task: {name} started')
                result = await coro(*args, **kwargs)
            if time_out_scope.cancelled_caught:
                result = default
            await sender_channel.send(f'FROM: {name}, MSG: {result}')
        except trio.Cancelled:
            print(f'Task {name} execution canceled')
        finally:
            print(f'Task {name} done')


if __name__ == '__main__':
    trio.run(main)
