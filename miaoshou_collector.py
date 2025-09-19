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
# --- 采集策略开关 ---
# True: 使用键盘模拟方案 (当前有效方案)
# False: 使用选择器直接定位方案 (在我们测试中失败，但保留作为备用)
USE_KEYBOARD_SIMULATION = False

async def collect_links_with_miaoshou(links_to_collect):
    """
    使用Playwright加载妙手插件，并对给定的链接列表进行采集。
    """
    logger.info("开始使用Playwright进行妙手采集...")
    
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

        # --- 步骤2: 遍历并采集链接 ---
        logger.info(f"准备采集 {len(links_to_collect)} 个链接...")
        for index, link in enumerate(links_to_collect):
            try:
                logger.info(f"[{index + 1}/{len(links_to_collect)}] 正在打开链接: {link}")
                await page.add_init_script("""
                (function() {
                const orig = Element.prototype.attachShadow;
                Element.prototype.attachShadow = function(init) {
                    init = Object.assign({}, init, {mode: 'open'});
                    return orig.call(this, init);
                };
                })();
                """)
                await page.goto(link, timeout=60000)
                
                # --- 验证码处理逻辑 ---
                captcha_present = False
                for i in range(3):
                    await page.wait_for_load_state("domcontentloaded", timeout=20000)
                    captcha_popup = page.get_by_text("Verify to continue:")
                    if await captcha_popup.is_visible(timeout=3000):
                        logger.warning(f"检测到 'Verify to continue' 验证码，正在刷新页面... (第 {i + 1}/3 次)")
                        if i < 2:
                            await page.reload()
                        else:
                            logger.error(f"刷新3次后验证码依然存在，放弃此链接: {link}")
                            captcha_present = True
                    else:
                        logger.info("未检测到验证码弹窗。")
                        captcha_present = False
                        break
                
                if captcha_present:
                    continue

                time.sleep(3)

                # --- 与插件交互 ---
                if USE_KEYBOARD_SIMULATION:
                    # --- 方案A：键盘模拟方案 (当前有效方案) ---
                    logger.info("尝试键盘模拟方案：聚焦宿主，按 Tab，再按 Enter...")
                    try:
                        shadow_host_selector = '[data-wxt-shadow-root]'
                        shadow_host = page.locator(shadow_host_selector).first
                        
                        await shadow_host.focus(timeout=5000)
                        logger.info("已成功聚焦到 Shadow DOM 宿主元素。")
                        
                        await page.keyboard.press("Tab")
                        logger.info("已按 Tab 键。")

                        await page.keyboard.press("Enter")
                        logger.success(f"已模拟回车键点击，期望采集已触发: {link}")

                        await page.wait_for_timeout(5000)
                        logger.info("采集操作已执行，等待5秒。")
                    except Exception as e:
                        logger.error(f"键盘模拟操作失败，放弃此链接: {e}")
                        continue
                else:
                    # --- 方案B：使用选择器直接定位（在我们测试中因插件限制而失败）---

                    button_selector = '[data-wxt-shadow-root] >> button:has-text("采集此商品")'
                    logger.info(f"尝试选择器定位方案: '{button_selector}'")
                    try:
                        collect_button = page.locator(button_selector)
                        await collect_button.wait_for(state="visible", timeout=5000)
                        await collect_button.click()
                        logger.success(f"成功点击采集按钮: {link}")
                        await page.wait_for_timeout(5000)
                        logger.info("采集操作已执行，等待5秒。")
                    except Exception as e:
                        logger.error(f"使用选择器 '{button_selector}' 点击采集按钮失败，放弃此链接: {e}")
                        continue

            except Exception as e:
                logger.error(f"处理链接 {link} 时出错: {e}")
                continue

        logger.info("所有链接处理完毕。")
        await context.close()

# --- 用于直接运行测试的入口 ---
if __name__ == '__main__':
    sample_links = [
        "https://vt.tiktok.com/ZSHnb1eg86vA5-uTrrO/",
        "https://vt.tiktok.com/ZSHnb18VnLuk7-I2bDl/"
    ]
    asyncio.run(collect_links_with_miaoshou(sample_links))
