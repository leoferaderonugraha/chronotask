import asyncio
import typing as t
import time
from threading import Thread
from datetime import datetime
from collections import defaultdict


class ChronoTask:
    def __init__(self, max_threads: int = 1) -> None:
        self.max_threads = max_threads
        self._scheduled_funcs: t.Dict[t.Callable, str] = {}
        self._scheduled_funcs_ms: t.Dict[t.Callable, int] = {}
        self._is_running = False
        self._thread = Thread(target=self._process_executions, daemon=True)
        self._exec_tracker: t.Dict[str, t.List] = defaultdict(list)
        self._exec_tracker_ms: t.Dict[t.Callable, int] = {}

    def schedule(self, fmt: str = '* * * * *') -> t.Callable:
        """Schedule a function call with crontab formatted execution time"""

        if not self._validate_format(fmt):
            raise ValueError

        # doesn't make sense to add args and kwargs
        def decorator(func: t.Callable) -> t.Callable:
            self._scheduled_funcs[func] = fmt
            return func

        return decorator

    def register(self, func: t.Callable, fmt: str = '* * * * *') -> None:
        if not self._validate_format(fmt):
            raise ValueError

        self._scheduled_funcs[func] = fmt

    def register_ms(self, func: t.Callable, ms: int) -> None:
        if ms < 100:
            raise ValueError('Minimum value for ms is 100')

        self._scheduled_funcs_ms[func] = ms

    def start(self) -> None:
        self._is_running = True
        self._thread.start()

    def stop(self) -> None:
        self._is_running = False
        self._thread.join()

    def _process_scheduled_cron(self, exec_time: str) -> None:
        threads = []
        for func in self._scheduled_funcs.keys():
            if func in self._exec_tracker[exec_time]:
                continue

            if not self._match_crontab(self._scheduled_funcs[func]):
                continue

            # purposedly not in daemon mode since it may requires
            # another resource from the main program
            if asyncio.iscoroutinefunction(func):
                th = Thread(target=asyncio.run,
                            args=[func()])
            else:
                th = Thread(target=func)

            th.start()
            threads.append(th)

            if len(threads) >= self.max_threads:
                for thread in threads:
                    thread.join()

            self._exec_tracker[exec_time].append(func)

    def _process_scheduled_ms(self) -> None:
        threads = []

        for func, ms in self._scheduled_funcs_ms.items():
            last_exec = self._exec_tracker_ms.get(func, 0)
            current_time = time.time_ns() // 1_000_000

            if current_time - last_exec >= ms:
                th = self._make_thread(func)
                th.start()
                threads.append(th)

                if len(threads) >= self.max_threads:
                    for thread in threads:
                        thread.join()

                self._exec_tracker_ms[func] = current_time

    def _process_executions(self) -> None:
        while self._is_running:
            now = datetime.now().strftime("%Y-%m-%dT%H:%M")
            self._process_scheduled_cron(now)
            self._process_scheduled_ms()

            time.sleep(.1)

    def _validate_format(self, fmt: str) -> bool:
        fmt_parts = fmt.split(' ')

        if len(fmt_parts) != 5:
            return False

        for ch in fmt_parts:
            if ch != '*' and not ch.isdigit():
                return False

        return True

    def _parse_crontab(self, crontab_str):
        minute, hour, dom, month, dow = crontab_str.split()
        return {
            "minute": minute,
            "hour": hour,
            "day_of_month": dom,
            "month": month,
            "day_of_week": dow,
        }

    def _match_crontab(self, crontab):
        now = datetime.now()
        crontab_parts = self._parse_crontab(crontab)

        def match_part(cron_part, dt_value):
            if cron_part == '*':
                return True
            if cron_part.isdigit():
                return int(cron_part) == dt_value
            return False

        minute_match = match_part(crontab_parts["minute"], now.minute)
        hour_match = match_part(crontab_parts["hour"], now.hour)
        dom_match = match_part(crontab_parts["day_of_month"], now.day)
        month_match = match_part(crontab_parts["month"], now.month)
        dow_match = match_part(crontab_parts["day_of_week"], now.weekday())

        return (minute_match and
                hour_match and
                dom_match and
                month_match and
                dow_match)

    def _make_thread(self, func: t.Callable) -> Thread:
        # purposedly not in daemon mode since it may requires
        # another resource from the main program
        if asyncio.iscoroutinefunction(func):
            return Thread(target=asyncio.run, args=[func()])

        return Thread(target=func)
