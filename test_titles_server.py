import asyncio
import websockets


async def send_test_annoucement(websocket):
    annoucement = '{"source":"BINANCE","title":"Binance Will List (BTC) and (ETH) something with Seed Tag Applied"}'
    await websocket.send(annoucement)
    print("Sent > {}".format(annoucement))
    while True:
        await asyncio.sleep(1)


async def main():
    async with websockets.serve(send_test_annoucement, "localhost", 8765):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
