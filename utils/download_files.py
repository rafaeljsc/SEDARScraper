import logging

from playwright.async_api import Page

from utils.download_batch import download_batch
from utils.download_one_per_one import download_one_per_one
from utils.download_too_large_to_batch import download_too_large_to_batch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def download_files(page: Page) -> None:
    """Baixa arquivos da página

    Args:
        page (Page): Página Playwright
    """

    if await download_too_large_to_batch(page):
        await download_one_per_one(page)
    else:
        await download_batch(page)
