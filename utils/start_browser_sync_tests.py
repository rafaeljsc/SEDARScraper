from playwright.sync_api import sync_playwright
from pathlib import Path

manager = sync_playwright().start()

# Perfil persistente para reduzir a solução de captcha
profile_dir = Path("./profile").absolute()

# launch_persistent_context já inicia o browser e o context juntos
context = manager.chromium.launch_persistent_context(
    user_data_dir=str(profile_dir),
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    headless=False,
    device_scale_factor=1,
    accept_downloads=True,
    args=[
        "--start-maximized",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-software-rasterizer",
        "--disable-extensions",
    ],
)

# O contexto persistente já vem com uma página aberta por padrão
page = context.pages[0] if context.pages else context.new_page()


#################

page.evaluate(
    'document.querySelector(\'div[style*="top: -10000px"]\').style.top = "100px"'
)
page.evaluate(
    'document.querySelector(\'div[style*="opacity: 0"]\').style.opacity = "1"'
)
page.evaluate(
    'document.querySelector(\'div[style*="hidden"]\').style.visibility = "visible"'
)


from math import ceil
from utils.dinamic_sleep import dinamic_sleep

page_docs_size_mb = 0
download_limit_mb = 700

while download_limit_mb > page_docs_size_mb:
    
    docs = page.locator(".appTblRow", has_text=".pdf").all()
    page_docs_size = 0
    
    for doc in docs:
        size = int(doc.locator(".appAttrValue", has_text="KB").text_content().split()[0])
        page_docs_size += size

    page_docs_size_mb = ceil(page_docs_size / 1024)
    
    
    current_page = page.locator("//a[@class='active']").first.text_content()
    print(f"page: {current_page}, size: {page_docs_size_mb} MB")
    
    page.locator(".appNext.pagination-item").first.click()
    dinamic_sleep(page)


selection_size = 0
for doc in docs:
    size = int(doc.locator(".appAttrValue", has_text="KB").text_content().split()[0])
    size_mb = ceil(size/1024)
    if selection_size + size_mb >= download_limit_mb:
        break
    
    selection_size += size_mb
    print(selection_size)
    doc.locator("//input[@type='checkbox']").click()
    dinamic_sleep(page)
    
    
    
    
    
    
    
    
    










from uuid import uuid4
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_one_per_one(page: Page, target: Path):

output = Path("output")
Path.mkdir(output, exist_ok=True)
from playwright.sync_api import Download

docs = page.locator(".appTblRow", has_text=".pdf").all()
for count, doc in enumerate(docs, start=1):
    
    print(f"Baixando {count}/{len(docs)}")
    with page.expect_download() as download_info:
        doc.click()

    download = download_info.value
    file_output = Path.joinpath(output, f"{str(uuid4())}.pdf")
    failure = download.failure()
    if failure:
        print(f"Download falhou: {failure}")
    else:
        download.save_as(file_output)

