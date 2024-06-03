import time
import asyncio
from datetime import datetime
from . import CronTask


cron = CronTask()


def test_sync_fn():
    print('sync: ', datetime.now())


async def test_async_fn():
    print('async: ', datetime.now())
    await asyncio.sleep(.1)


if __name__ == '__main__':
    cron = CronTask()
    cron.register(test_sync_fn, fmt='44 * * * *')
    cron.register(lambda: print('lambda...'), fmt='* * * * *')
    # also supports async function
    cron.register(test_async_fn, fmt='* * * * *')

    cron.start()

    while True:
        try:
            time.sleep(.1)
        except KeyboardInterrupt:
            print('stopping...')
            break

    cron.stop()
