from playwright.async_api import Page

async def dinamic_sleep(page: Page) -> None:
    """Aguarda o carregamento da página de forma dinâmica
    
    Args:
        page (Page): Página Playwright
    """
    
    try:
        await page.wait_for_selector("#catProcessing")
        while await page.locator("#catProcessing").is_visible():
            await page.wait_for_timeout(1000)

        await page.wait_for_timeout(1000)
    except:  # noqa: E722
        pass