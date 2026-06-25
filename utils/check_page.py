import logging

from playwright.async_api import Page

logger = logging.getLogger(__name__)


async def check_page(page: Page) -> tuple[int, int]:
    """Retorna a página atual e o total de páginas

    Args:
        page (Page): Página Playwright
    """

    logger.info("Verificando páginas")
    
    pages = await page.locator(".appPager").first.is_visible()
    total_pages = int(
        1
        if not pages
        else await page.locator(".appPager").first.locator(".appPage.pagination-item").last.text_content(),
    )
    
    current_page = (
        total_pages
        if total_pages == 1
        else int(await page.locator(".active").first.text_content())
    )
    
    return current_page, total_pages
