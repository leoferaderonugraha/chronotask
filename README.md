# PySched

Python function call scheduler with crontab formatted time supports.


example of usage:

```python
from pysched import PySched
import time

scheduler = PySched()

# as a decorator
@scheduler.schedule()
def hello():
    ...


# or by call
scheduler.register(hello)


# start the scheduler
scheduler.start()
time.sleep(10)
scheduler.stop()
```
