import logging
import re
from pathlib import Path

from playwright.async_api import Page

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def download_one_per_one(
    page: Page,
    target: Path = Path.joinpath(Path(__file__).parent.parent, "output"),
) -> None:
    """Baixa arquivos da página um por um. Utilizado quando o total de arquivos da página atual ultrapassa o limite de download em batch (700 MB)

    Args:
        page (Page): Página Playwright
        target (Path): Pasta de destino do download. Padrão: Pasta `output` na raiz do pasta do script.
    """

    Path.mkdir(target, exist_ok=True)
    success = 0
    error = 0

    docs = await page.locator(".appTblRow", has_text=".pdf").all()
    for count, doc in enumerate(docs, start=1):
        doc_name = await doc.locator(".appDocumentLink", has_text=".pdf").text_content()
        doc_date = await doc.locator(".appAttrDateTime").locator(".appAttrValue").locator("span").first.text_content()
        doc_final_name = re.sub(r"[^a-zA-Z0-9]", "_", f"{doc_date} ") + doc_name

        async with page.expect_download() as download_info:
            await doc.click(timeout=120000)

        download = await download_info.value
        file_output = target / doc_final_name

        failure = await download.failure()
        if not failure:
            await download.save_as(file_output)
            success += 1

        else:
            error += 1

        logger.info(f"Baixando: {count}/{len(docs)}, sucesso: {success}, erros: {error}")  # noqa: G004
