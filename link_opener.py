import asyncio
from playwright.async_api import async_playwright
from loguru import logger
import os

async def open_links_from_file(filename):
    """
    Reads a file from the 'shared_links' directory and opens each link in a new browser tab.
    """
    links_dir = 'shared_links'
    file_path = os.path.join(links_dir, filename)

    if not os.path.exists(file_path):
        logger.error(f"文件不存在: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        links = [line.strip() for line in f if line.strip()]

    if not links:
        logger.warning(f"文件中没有找到任何链接: {file_path}")
        return

    logger.info(f"准备从文件 '{file_path}' 打开 {len(links)} 个链接...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        # Keep track of pages to ensure they are all created
        pages = []
        
        for index, link in enumerate(links):
            try:
                logger.info(f"[{index + 1}/{len(links)}] 正在打开链接: {link}")
                page = await context.new_page()
                await page.goto(link, timeout=60000, wait_until='domcontentloaded')
                pages.append(page)
            except Exception as e:
                logger.error(f"打开链接失败 {link}: {e}")
        
        logger.info(f"所有链接都已尝试打开。浏览器将保持开启状态，您可以手动检查。")
        logger.info("您可以随时手动关闭浏览器。")
        
        # This will keep the browser open until manually closed.
        # To close automatically, you would use: await browser.close()
        # For this use case, we want it to stay open.
        await context.on("close", lambda: logger.info("浏览器上下文已关闭。"))
        # A simple way to keep the script alive while the browser is open
        while len(context.pages) > 0:
            await asyncio.sleep(1)

if __name__ == '__main__':
    # 默认使用 'collected_links.txt' 文件进行测试
    default_filename = 'collected_links.txt'
    asyncio.run(open_links_from_file(default_filename))
