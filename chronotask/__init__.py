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
        self._is_running = False
        self._thread = Thread(target=self._process_executions, daemon=True)
        self._exec_tracker: t.Dict[str, t.List] = defaultdict(list)

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

    def start(self) -> None:
        self._is_running = True
        self._thread.start()

    def stop(self) -> None:
        self._is_running = False
        self._thread.join()

    def _process_executions(self) -> None:
        while self._is_running:
            threads = []
            now = datetime.now().strftime("%Y-%m-%dT%H:%M")

            for func in self._scheduled_funcs.keys():
                if func in self._exec_tracker[now]:
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

                self._exec_tracker[now].append(func)

            time.sleep(1)

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
