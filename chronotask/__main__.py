import time
import asyncio
from datetime import datetime
from . import ChronoTask


def test_sync_fn():
    print('sync: ', datetime.now())


async def test_async_fn():
    print('async: ', datetime.now())
    await asyncio.sleep(.1)


if __name__ == '__main__':
    task = ChronoTask()
    task.register(test_sync_fn, fmt='44 * * * *')
    task.register(lambda: print('lambda...'), fmt='* * * * *')
    # also supports async function
    task.register(test_async_fn, fmt='* * * * *')

    task.start()

    while True:
        try:
            time.sleep(.1)
        except KeyboardInterrupt:
            print('stopping...')
            break

    task.stop()
