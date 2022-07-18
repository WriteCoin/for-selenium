import asyncio
from typing import Optional
from playsound import playsound


async def play(path: Optional[str] = None):
    playsound("sound/notify.oga")


async def run():
    asyncio.create_task(play())
    print("End")


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
