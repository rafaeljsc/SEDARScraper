from math import ceil
from playwright.async_api import Page
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def download_too_large_to_batch(page: Page, download_limit_mb: int = 700) -> bool:
    page_docs_size_mb = 0
    docs = await page.locator(".appTblRow", has_text=".pdf").all()

    page_docs_size = 0
    for doc in docs:
        size = int(
            (await doc.locator(".appAttrValue", has_text="KB").text_content()).split()[
                0
            ],
        )
        page_docs_size += size

    current_page = (
        1
        if not await page.locator(".active").is_visible()
        else await page.locator(".active").first.text_content()
    )
    page_docs_size_mb = ceil(page_docs_size / 1024)

    cant_download_batch = page_docs_size_mb > download_limit_mb

    if cant_download_batch:
        logger.info(
            f"Página {current_page}: {page_docs_size_mb} MB > {download_limit_mb} MB. Baixando um por um."
        )  # noqa: G004
        return True

    logger.info(
        f"Página {current_page}: {page_docs_size_mb} MB < {download_limit_mb} MB. Baixando em batch.",  # noqa: G004
    )

    return False
        