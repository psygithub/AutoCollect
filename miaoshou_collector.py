import asyncio
from playwright.async_api import async_playwright
from loguru import logger
import time

# --- 配置信息 ---
PROXY_SERVER = "http://127.0.0.1:10908"
MIAOSHOU_URL = "https://erp.91miaoshou.com/?redirect=%2Fwelcome"
MIAOSHOU_USERNAME = "18575215654"
MIAOSHOU_PASSWORD = "599kioKIO!@#"
# 注意：请将插件路径中的反斜杠 `\` 替换为正斜杠 `/`
EXTENSION_PATH = "C:/Users/Kan/AppData/Local/Google/Chrome/User Data/Default/UnpackedExtensions/kuajing-erp-plugin-v3_109952_241147546"

async def collect_links_with_miaoshou(links_to_collect):
    """
    使用Playwright加载妙手插件，并对给定的链接列表进行采集。
    """
    logger.info("开始使用Playwright进行妙手采集...")
    
    async with async_playwright() as p:
        # 代理服务器配置
        proxy_settings = {
            "server": PROXY_SERVER
        }
        logger.info(f"正在使用代理服务器: {proxy_settings['server']}")

        # 启动一个带有插件和代理的浏览器上下文
        # headless=False 可以在开发时看到浏览器界面，方便调试
        context = await p.chromium.launch_persistent_context(
            "",  # 用户数据目录，留空则为临时目录
            headless=False,
            args=[
                f"--disable-extensions-except={EXTENSION_PATH}",
                f"--load-extension={EXTENSION_PATH}",
            ],
            proxy=proxy_settings,
        )
        
        page = await context.new_page()
        
        # --- 步骤1: 处理插件初始化和登录妙手 ---
        try:
            # 插件可能会打开一个自己的设置页面，需要先处理掉
            # 等待片刻，让所有初始页面都加载出来
            await page.wait_for_timeout(5000) 
            all_pages = context.pages
            logger.info(f"浏览器启动后有 {len(all_pages)} 个页面。")
            
            # 遍历所有页面，寻找插件的设置页面并处理
            for p in all_pages:
                if p != page: # 排除主页面
                    try:
                        logger.info(f"正在检查页面: {p.url}")
                        # 尝试在非主页面上执行录制到的关闭弹窗操作
                        await p.locator("label span").nth(1).click(timeout=5000)
                        await p.get_by_role("button", name="确认开启").click(timeout=5000)
                        logger.success("成功处理插件的初始设置页面。")
                        await p.close()
                        break # 处理完就退出循环
                    except Exception:
                        logger.warning(f"页面 {p.url} 不是插件设置页，或无法执行操作。将忽略。")

            # --- 开始登录 ---
            logger.info(f"正在导航到妙手登录页面: {MIAOSHOU_URL}")
            await page.goto(MIAOSHOU_URL, timeout=60000)
            
            logger.info("输入账号和密码 (使用录制的新选择器)...")
            await page.get_by_role("textbox", name="手机号/子账号/邮箱").click()
            await page.get_by_role("textbox", name="手机号/子账号/邮箱").fill(MIAOSHOU_USERNAME)
            await page.get_by_role("textbox", name="密码").click()
            await page.get_by_role("textbox", name="密码").fill(MIAOSHOU_PASSWORD)
            
            logger.info("勾选记住密码并点击登录...")
            await page.locator(".remember-check-box").click()
            await page.get_by_role("button", name="立即登录").click()

            # 等待URL跳转到包含 'welcome' 的页面
            logger.info("正在等待登录跳转...")
            await page.wait_for_url("**/welcome**", timeout=60000)
            logger.success("妙手网站登录成功！")
            
        except Exception as e:
            logger.error(f"登录或处理插件初始化失败: {e}")
            await context.close()
            return

        # --- 步骤2: 遍历并采集链接 ---
        logger.info(f"准备采集 {len(links_to_collect)} 个链接...")
        for index, link in enumerate(links_to_collect):
            try:
                logger.info(f"[{index + 1}/{len(links_to_collect)}] 正在打开链接: {link}")
                await page.goto(link, timeout=60000)
                
                # 等待页面加载完成
                await page.wait_for_load_state("domcontentloaded", timeout=30000)
                
                # 根据录制的操作，尝试关闭商品页上可能出现的弹窗
                try:
                    # await page.get_by_role("button", name="取消").click(timeout=5000)
                    logger.info("成功关闭商品页上的'取消'弹窗。")
                except Exception:
                    logger.info("商品页上未找到'取消'弹窗，或弹窗已关闭。")

                time.sleep(3) # 等待插件UI加载

                # --- 与插件交互 ---
                # 这是最不确定的部分，因为插件可能会以多种方式将按钮注入页面
                # 可能是iframe，也可能是直接的div。您需要在这里进行调试。
                
                # TODO: 【请您补充】请在这里填写采集按钮的准确选择器
                # 您可以使用浏览器的开发者工具(F12)来查找这个按钮的CSS选择器或XPath
                # 例如: collection_button_selector = "#miaoshou-collect-button"
                # 根据您的反馈，插件的按钮文本是“采集此商品”
                # 使用用户提供的 XPath 定位采集按钮
                collection_button_xpath = "/html/body/rtwcqko-ykzqpmj-mkuzjvsipv//html/body/div/div/div[1]/button/span"
                logger.info(f"正在使用 XPath 查找采集按钮: {collection_button_xpath}")
                collect_button = page.locator(f"xpath={collection_button_xpath}")
                
                if await collect_button.is_visible(timeout=10000):
                    await collect_button.click()
                    logger.success(f"成功点击采集按钮: {link}")
                    # 等待采集完成
                    time.sleep(5) 
                else:
                    logger.warning(f"在页面上未找到指定的 XPath 采集按钮: {link}")

            except Exception as e:
                logger.error(f"处理链接 {link} 时出错: {e}")
                continue # 继续处理下一个链接

        logger.info("所有链接处理完毕。")
        await context.close()

# --- 用于直接运行测试的入口 ---
if __name__ == '__main__':
    # 提供一些示例链接进行测试
    sample_links = [
        "https://vt.tiktok.com/ZSHnb1eg86vA5-uTrrO/",
        "https://vt.tiktok.com/ZSHnb18VnLuk7-I2bDl/"
        # ... 您可以添加更多测试链接
    ]
    
    # 运行异步函数
    asyncio.run(collect_links_with_miaoshou(sample_links))
