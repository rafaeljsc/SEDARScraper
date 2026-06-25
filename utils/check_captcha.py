import logging
from random import randint

from playwright.sync_api import FrameLocator, Page

from .captcha_replier import AzureLLM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_captcha(page: Page) -> bool:
    """Verifica e resolve captcha

    Args:
        page (Page): Página Playwright
    """

    await page.wait_for_timeout(5000)
    if "http://validate.perfdrive.com/" not in page.url:
        return False

    logger.info("Resolvendo Captcha...")
    
    await page.evaluate('document.querySelector(\'div[style*="top: -10000px"]\').style.top = "100px"')
    await page.evaluate('document.querySelector(\'div[style*="opacity: 0"]\').style.opacity = "1"')

    await page.locator("//div[@class='h-captcha']").click()  # Clica no captcha
    captcha_frame: FrameLocator = page.frame_locator("iframe[src*='captcha']").last  # Seleciona janela do captcha
    await captcha_frame.locator("#menu-info").click()  # Clica nas opções
    await captcha_frame.locator("//*[text()='Desafio de acessibilidade']").click()  # Seleciona acessibilidade
    await captcha_frame.locator("#prompt-text").focus(timeout=5000)

    # Enquanto o captcha fizer perguntas
    while True:
        try:
            txt = await captcha_frame.locator("#prompt-text").text_content()  # Captura pergunta
            await captcha_frame.locator(".input-field").focus(timeout=5000)
            captcha_response = AzureLLM().captcha_replier(txt)  # Responde com IA
            logger.info(f"Captcha: {txt} | Resposta: {captcha_response}")  # noqa: G004

            await captcha_frame.locator(".input-field").fill(captcha_response)  # Preenche campo de resposta
            await page.wait_for_timeout(randint(5, 30) * 1000)  # noqa: S311

            await captcha_frame.locator(".button-submit.button").click()  # Envia resposta
            await page.wait_for_timeout(randint(1, 10) * 1000)  # noqa: S311
            if (
                not await captcha_frame.locator("#prompt-text").is_visible()
                or txt == await captcha_frame.locator("#prompt-text").text_content()
            ):
                break
        except:  # noqa: E722
            break
    
    logger.info("Questões finalizadas. Aguardando resultado.")
    await page.locator("//input[@type='submit']").click()  # Finaliza desafio captcha
    await page.locator("a", has_text="Login").all() # Finaliza desafio captcha
    logger.info("Captcha resolvido!")

    return True
