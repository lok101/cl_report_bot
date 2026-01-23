import asyncio

from dotenv import load_dotenv

from srс.app import app

load_dotenv()


async def main():
    await app()

if __name__ == "__main__":
    asyncio.run(main())
