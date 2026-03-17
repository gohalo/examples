import asyncio

async def task1():
    print("Task 1 started")
    await asyncio.sleep(0.1)
    print("Task 1 finished")

async def task2():
    print("Task 2 started")
    await asyncio.sleep(0.2)
    print("Task 2 finished")

async def long_task():
    await asyncio.sleep(1)
    print("Long task finished")

async def main():
    try:
        await asyncio.wait_for(long_task(), timeout=0.5)
    except asyncio.TimeoutError:
        print("Task timed out")

    await asyncio.gather(task1(), task2())

asyncio.run(main())
