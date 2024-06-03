# CronTask

A Python function call scheduler that supports crontab-formatted time (also supports async functions).

example of usage:

```python
from crontask import CronTask
import time

cron = CronTask()

# as a decorator
@cron.schedule()
def hello():
    ...


# or by call
cron.register(hello)


# start the cron
cron.start()
time.sleep(10)
cron.stop()
```
