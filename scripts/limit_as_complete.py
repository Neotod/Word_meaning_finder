import asyncio

def limit_as_complete(coros, limit: int):
    tasks = list()
    for _ in range(limit):
        coro = next(coros)
        task = asyncio.create_task(coro)
        tasks.append(task)
    # tasks = [asyncio.create_task(coro) for coro in coros[0:limit]]
    
    async def update():
        while True:
            await asyncio.sleep(0)
            for t in tasks:
                if t.done():
                    tasks.remove(t)
                    try:
                        new_coro = next(coros)
                        new_task = asyncio.create_task(new_coro)
                        tasks.append(new_task)
                    except StopIteration:
                        pass
                    
                    result = t.result()
                    t.cancel()
                    return result
                        
    while len(tasks) > 0:
        yield update()