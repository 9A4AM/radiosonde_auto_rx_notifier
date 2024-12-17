from async_radiosonde_auto_rx_listener import AsyncRadiosondeAutoRxListener

import asyncio


if __name__ == "__main__":
    listener = AsyncRadiosondeAutoRxListener()
    asyncio.run(listener.start())
