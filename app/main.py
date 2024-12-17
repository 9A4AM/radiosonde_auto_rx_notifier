import asyncio

from radiosonde_auto_rx_listener import AsyncRadiosondeAutoRxListener

from logger import configure_logger
from pathlib import Path


if __name__ == "__main__":
    base_path = Path(__file__).parent
    configure_logger(base_path)

    listener = AsyncRadiosondeAutoRxListener()
    asyncio.run(listener.start())
