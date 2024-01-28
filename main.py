import asyncio
import websockets
from os import getenv
import orjson
import logging
import aiohttp

WEBSOCKET_URI = "ws://localhost:8765"
TITLES_LIST = [
    "Binance Will List",
    "마켓 디지털 자산 추가",  # upbit
    "Binance Futures Will Launch",
    "Coinbase Roadmap",  # coinbase
    "New Listing",  # bybit
    "[마켓 추가]",  # bithumb
]

logger = logging.getLogger("[DUFF-ALERTS]")
logger.setLevel(logging.INFO)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


async def websocket_listen():
    while True:
        try:
            async with websockets.connect(WEBSOCKET_URI) as websocket:
                await websocket.send(f'login {getenv("tree_of_alpha_key")}')

                while True:
                    news_event = await websocket.recv()

                    news_event_json = orjson.loads(news_event)

                    title = process_title(news_event_json)

                    logger.info(f"Title: {title}")
                    logger.info(f"News Event: {news_event_json}")

                    if title:
                        await send_to_pushover(title)
                    else:
                        logger.info(
                            f"Title doesn't match a listing: {news_event_json['title']}"
                        )

                    await websocket.ping()

        except (
            websockets.exceptions.ConnectionClosedError,
            websockets.exceptions.ConnectionClosedOK,
            websockets.exceptions.ConnectionClosed,
        ) as e:
            logger.error(f"Connection closed: {e}")


def process_title(response):
    try:
        if "title" in response:
            title = response["title"]

            for listing in TITLES_LIST:
                if listing in title:
                    return title
    except KeyError:
        logger.error(f"Title not in tree: {response}")

    return None


async def send_to_pushover(title):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": getenv("pushover_token"),
                "user": getenv("pushover_user"),
                "message": title,
            },
        ) as response:
            logger.info(f"Pushover response: {response.status}")


if __name__ == "__main__":
    logger.info("Starting Bot...")
    if (
        not getenv("tree_of_alpha_key")
        and not getenv("pushover_token")
        and not getenv("pushover_user")
    ):
        raise Exception("tree_of_alpha_key,pushover_token, pushover_user not set")
    asyncio.run(websocket_listen())
