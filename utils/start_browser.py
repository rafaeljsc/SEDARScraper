from playwright.async_api import BrowserContext, Page, Playwright, async_playwright
from pathlib import Path


async def start_browser(headless: bool = False) -> tuple[Page, BrowserContext, Playwright]:
    """Inicia um browser Playwright com perfil persistente"""

    manager = await async_playwright().start()


    # Perfil persistente para reduzir a solução de captcha
    profile_dir = Path("./profile").absolute()

    # launch_persistent_context já inicia o browser e o context juntos
    context = await manager.chromium.launch_persistent_context(
        user_data_dir=str(profile_dir),
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        headless=headless,
        device_scale_factor=1,
        accept_downloads=True,
        viewport={"width": 1366, "height": 768},
        args=[
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--disable-extensions",
        ],
    )

    # O contexto persistente já vem com uma página aberta por padrão
    if context.pages:
        page = context.pages[0]
    else:
        page = context.new_page()

    return page, context, manager
