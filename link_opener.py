import asyncio
from playwright.async_api import async_playwright
from loguru import logger
import os

async def open_links_from_file(filename, config=None):
    """
    Reads a file from the 'shared_links' directory and opens each link in a new browser tab.
    """
    if config is None:
        config = {}

    # --- 配置信息 ---
    PROXY_SERVER = config.get("proxy_server", "http://127.0.0.1:10908")
    MIAOSHOU_URL = config.get("miaoshou_url", "https://erp.91miaoshou.com/?redirect=%2Fwelcome")
    MIAOSHOU_USERNAME = config.get("miaoshou_username", "18575215654")
    MIAOSHOU_PASSWORD = config.get("miaoshou_password", "599kioKIO!@#")
    EXTENSION_PATH = config.get("extension_path", "C:/Users/Kan/AppData/Local/Google/Chrome/User Data/Default/UnpackedExtensions/kuajing-erp-plugin-v3_109952_241147546")

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
        proxy_settings = { "server": PROXY_SERVER } if PROXY_SERVER else None
        
        launch_args = [
            f"--disable-extensions-except={EXTENSION_PATH}",
            f"--load-extension={EXTENSION_PATH}",
        ]

        if proxy_settings:
            logger.info(f"正在使用代理服务器: {proxy_settings['server']}")
        else:
            logger.info("未使用代理服务器。")

        context = await p.chromium.launch_persistent_context(
            "",
            headless=False,
            args=launch_args,
            proxy=proxy_settings,
        )

        page = await context.new_page()
        # --- 步骤1: 处理插件初始化和登录 ---
        try:
            await page.wait_for_timeout(5000) 
            all_pages = context.pages
            logger.info(f"浏览器启动后有 {len(all_pages)} 个页面。")
            
            for p_item in all_pages:
                if p_item != page:
                    try:
                        logger.info(f"正在检查页面: {p_item.url}")
                        await p_item.locator("label span").nth(1).click(timeout=5000)
                        await p_item.get_by_role("button", name="确认开启").click(timeout=5000)
                        logger.success("成功处理插件的初始设置页面。")
                        await p_item.close()
                        break
                    except Exception:
                        logger.warning(f"页面 {p_item.url} 不是插件设置页，或无法执行操作。将忽略。")

            logger.info(f"正在导航到妙手登录页面: {MIAOSHOU_URL}")
            await page.goto(MIAOSHOU_URL, timeout=60000)
            
            await page.get_by_role("textbox", name="手机号/子账号/邮箱").fill(MIAOSHOU_USERNAME)
            await page.get_by_role("textbox", name="密码").fill(MIAOSHOU_PASSWORD)
            await page.locator(".remember-check-box").click()
            await page.get_by_role("button", name="立即登录").click()

            await page.wait_for_url("**/welcome**", timeout=60000)
            logger.success("妙手网站登录成功！")
            
        except Exception as e:
            logger.error(f"登录或处理插件初始化失败: {e}")
            await context.close()
            return



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
        await page.pause()

        # This will keep the browser open until manually closed.
        # To close automatically, you would use: await context.close()
        # For this use case, we want it to stay open.
        
        # Wait for the user to close the browser context.
        closed_future = asyncio.get_running_loop().create_future()
        context.on("close", lambda: closed_future.set_result(None))
        await closed_future
        
        logger.info("浏览器上下文已关闭。")
if __name__ == '__main__':
    # 默认使用 'collected_links.txt' 文件进行测试
    default_filename = 'collected_links.txt'
    # 为直接运行提供默认配置
    default_config = {
        "proxy_server": "http://127.0.0.1:10908",
        "miaoshou_url": "https://erp.91miaoshou.com/?redirect=%2Fwelcome",
        "miaoshou_username": "18575215654",
        "miaoshou_password": "599kioKIO!@#",
        "extension_path": "C:/Users/Kan/AppData/Local/Google/Chrome/User Data/Default/UnpackedExtensions/kuajing-erp-plugin-v3_109952_241147546"
    }
    asyncio.run(open_links_from_file(default_filename, default_config))
