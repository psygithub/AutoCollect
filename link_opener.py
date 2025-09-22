import asyncio
from playwright.async_api import async_playwright
from loguru import logger
import os

# --- 配置信息 ---
PROXY_SERVER = "http://127.0.0.1:10908"
MIAOSHOU_URL = "https://erp.91miaoshou.com/?redirect=%2Fwelcome"
MIAOSHOU_USERNAME = "18575215654"
MIAOSHOU_PASSWORD = "599kioKIO!@#"
# 注意：请将插件路径中的反斜杠 `\` 替换为正斜杠 `/`
EXTENSION_PATH = "C:/Users/Kan/AppData/Local/Google/Chrome/User Data/Default/UnpackedExtensions/kuajing-erp-plugin-v3_109952_241147546"



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
        proxy_settings = { "server": PROXY_SERVER }
        logger.info(f"正在使用代理服务器: {proxy_settings['server']}")

        context = await p.chromium.launch_persistent_context(
            "",
            headless=False,
            args=[
                f"--disable-extensions-except={EXTENSION_PATH}",
                f"--load-extension={EXTENSION_PATH}",
            ],
            proxy=proxy_settings,
        )
        
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
        
        await page.wait_for_timeout(60000 * 10)  # 等待10分钟以便手动检查
        await context.close()
if __name__ == '__main__':
    # 默认使用 'collected_links.txt' 文件进行测试
    default_filename = 'collected_links.txt'
    asyncio.run(open_links_from_file(default_filename))
