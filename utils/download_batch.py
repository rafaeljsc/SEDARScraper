import logging
import re
from pathlib import Path

from playwright.async_api import Page

from utils.dinamic_sleep import dinamic_sleep

logger = logging.getLogger(__name__)


async def download_batch(
    page: Page,
    current_page: int,
    target: Path = Path.joinpath(Path(__file__).parent.parent, "output"),
) -> None:
    """Baixa os arquivos resultantes da busca

    Args:
        page (Page): Página Playwright
        current_page (int): Página atual
        target (Path): Destino dos arquivos baixados. Padrão, pasta `output` criada na raiz do projeto
    """

    first_doc_date = (
        await page.locator(".appTblRow", has_text=".pdf")
        .first.locator(".appAttrDateTime")
        .locator(".appAttrValue")
        .locator("span")
        .first.text_content()
    )
    last_doc_date = (
        await page.locator(".appTblRow", has_text=".pdf")
        .last.locator(".appAttrDateTime")
        .locator(".appAttrValue")
        .locator("span")
        .first.text_content()
    )

    doc_date_prefix = re.sub(r"[^a-zA-Z0-9]", "_", f"{first_doc_date} {last_doc_date}")
    download_docs = page.locator("//label[contains(@for, 'DownloadAllDocumentsYn')]")
    if not await download_docs.is_visible():
        logger.info("A busca não retonou arquivos para download")
        return

    await download_docs.click()
    await dinamic_sleep(page)

    await page.locator("//button[contains(@class, 'downloadDocumentsButton')]").click()
    await dinamic_sleep(page)

    dialog = page.locator("//div[@role='dialog']")
    await dialog.focus()

    async with page.expect_download(timeout=180000) as download_info:
        await dialog.locator("button", has_text="Download").click(timeout=180000)

    await dinamic_sleep(page)

    Path.mkdir(target, exist_ok=True)
    download = await download_info.value
    output = Path.joinpath(target, f"{doc_date_prefix}-PG_{current_page}.zip")
    failure = await download.failure()
    if failure:
        logger.error(f"Falha no download batch: {failure}")  # noqa: G004
    else:
        await download.save_as(output)
