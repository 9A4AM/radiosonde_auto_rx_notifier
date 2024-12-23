import asyncio
from pathlib import Path

from logger import configure_logger
from radiosonde_auto_rx_listener import AsyncRadiosondeAutoRxListener

if __name__ == "__main__":
    base_path = Path(__file__).parent
    configure_logger(base_path)

    listener = AsyncRadiosondeAutoRxListener()
    asyncio.run(listener.start())
