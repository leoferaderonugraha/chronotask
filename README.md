# ChronoTask

A Python function call scheduler that supports crontab-formatted time (also supports async functions).

example of usage:

```python
from chronotask import ChronoTask
import time

task = ChronoTask()

# as a decorator
@task.schedule()
def hello():
    ...


# or by call
task.register(hello)


# start the scheduler
task.start()
time.sleep(10)
task.stop()
```
