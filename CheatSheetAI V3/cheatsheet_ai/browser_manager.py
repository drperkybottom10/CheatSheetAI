import logging
from browser_use import Browser, BrowserConfig, BrowserContextConfig

logger = logging.getLogger(__name__)

class BrowserManager:
    def __init__(self, config):
        self.config = config
        self.browser = None
        self.context = None

    async def initialize(self):
        browser_config = BrowserConfig(
            headless=self.config.HEADLESS,
            disable_security=True,
            extra_chromium_args=[
                '--disable-blink-features=AutomationControlled',
                '--start-maximized',
                '--no-first-run',
                '--no-default-browser-check',
                '--no-sandbox',
                '--disable-gpu',
                '--disable-extensions',
                '--enable-features=NetworkService,NetworkServiceInProcess'
            ]
        )

        context_config = BrowserContextConfig(
            wait_for_network_idle_page_load_time=0.1,
            browser_window_size={'width': 1280, 'height': 1100},
            minimum_wait_page_load_time=0.1,
            maximum_wait_page_load_time=2.0
        )

        browser_config.new_context_config = context_config

        self.browser = Browser(browser_config)
        self.context = await self.browser.new_context()
        logger.info("Browser initialized")

    async def new_page(self):
        if not self.context:
            await self.initialize()
        return await self.context.new_page()

    async def close(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        logger.info("Browser closed")
