import asyncio
import time


class ConcurrentBuilder:
    def __init__(self):
        self.tasks = {}

    def add_task(self, name, func):
        self.tasks[name] = func
        return self

    async def run(self):
        start_times = {}

        async def run_task(name, func):
            print(f"🚀 START: {name}")
            start_times[name] = time.time()

            result = await func()

            duration = round(time.time() - start_times[name], 2)
            print(f"✅ END: {name} ({duration}s)")
            return name, result

        coroutines = [
            run_task(name, func)
            for name, func in self.tasks.items()
        ]

        results = await asyncio.gather(*coroutines)

        return {name: result for name, result in results}