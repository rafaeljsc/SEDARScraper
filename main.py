import logging
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
import shutil

from utils.check_captcha import check_captcha
from utils.send_to_spo import send_to_spo
from utils.start_browser import start_browser
from utils.dinamic_sleep import dinamic_sleep
from utils.download_files import download_files
from utils.check_page import check_page
from utils.unziper import unziper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)  # noqa: DTZ005
end_date = now.strftime("%d/%m/%Y")
start_date = (now - timedelta(days=1)).strftime("%d/%m/%Y")

async def run_scrapping(start_date: str = start_date, end_date: str = end_date) -> None:
    """Navega num site específico e baixa pdfs"""

    cwd = Path(__file__).parent
    files_output = Path.joinpath(cwd, "output")
    ss_output = Path.joinpath(cwd, "screenshots")
    Path.mkdir(ss_output, exist_ok=True)
    Path.mkdir(files_output, exist_ok=True)

    logger.info("Iniciando navegador")
    page, context, manager = await start_browser(headless=True)

    try:
        if Path("output").exists():
            shutil.rmtree("output")

        logger.info("Navegando para a página principal")
        await page.goto("https://www.sedarplus.ca")
        await check_captcha(page=page)

        logger.info("Acessando a área de busca")
        await page.locator(".title", has_text="Search SEDAR+").click()
        await page.locator(".title", has_text="Documents").click()
        await check_captcha(page=page)

        logger.info("Preenchendo filtros")
        await page.locator("//select[@id='FilingType']").select_option(
            value="TECHNICAL_REPORTS_NI_43101",
        )

        await dinamic_sleep(page)

        await page.locator("//select[@id='DocumentType']").select_option(
            value="TECHNICAL_REPORT_NI_43101",
        )

        await dinamic_sleep(page)

        await page.locator("#SubmissionDate").fill(start_date)
        await page.locator("#SubmissionDate2").fill(end_date)

        logger.info(f"Buscando arquivos de {start_date} a {end_date}")  # noqa: G004
        await page.locator("button", has_text="Search").click()
        await dinamic_sleep(page)

        logger.info("Baixando arquivos")
        current_page, total_page = await check_page(page)

        while current_page <= total_page:
            logger.info(f"Baixando arquivos da página {current_page}/{total_page}")  # noqa: G004

            await download_files(page, current_page)

            logger.info("Descompactando arquivos")
            files = unziper()

            logger.info("Enviando arquivos para o Sharepoint")
            await send_to_spo(
                items=files,
                site="gamabotvalebase",
                lib="Documentos",
                path="Persona de Benchmark",
            )

            if files_output.exists():
                shutil.rmtree(files_output)

            next_page = page.locator(".appNext.pagination-item").first
            if await next_page.is_visible():
                await page.locator(".appNext.pagination-item").first.click()
                await dinamic_sleep(page)
                current_page, total_page = await check_page(page)
                

    except Exception:
        logger.error("Não foi possível prosseguir com o scrapping", exc_info=True)  # noqa: G201
        ss = ss_output / "screen_before_closing.png"
        await page.screenshot(path=ss, full_page=True)

    finally:
        await page.close()
        await context.close()
        await manager.stop()
        if files_output.exists():
            shutil.rmtree(files_output)


if __name__ == "__main__":
    asyncio.run(run_scrapping())