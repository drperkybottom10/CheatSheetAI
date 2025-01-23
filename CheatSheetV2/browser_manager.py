import logging
from browser_use import Browser, BrowserConfig
from browser_use.browser.context import BrowserContextConfig

logger = logging.getLogger(__name__)

class BrowserManager:
    def __init__(self, config):
        self.config = config
        self.browser = Browser(config=self.create_browser_config())

    def create_browser_config(self):
        browser_config = BrowserConfig(
            headless=False,
            disable_security=True,
            extra_chromium_args=['--start-maximized']
        )
        context_config = BrowserContextConfig(
            wait_for_network_idle_page_load_time=0.1,
            browser_window_size={'width': 1280, 'height': 1100},
            minimum_wait_page_load_time=0.1,
            maximum_wait_page_load_time=2.0
        )
        browser_config.new_context_config = context_config
        return browser_config

    async def close(self):
        await self.browser.close()
        logger.info("Browser closed")

    async def new_page(self):
        return await self.browser.new_page()
