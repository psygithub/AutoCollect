import asyncio
import sys
from playwright.async_api import async_playwright

# --- 从 miaoshou_collector.py 导入配置 ---
try:
    from miaoshou_collector import MIAOSHOU_URL, EXTENSION_PATH
except ImportError:
    print("错误：无法从 'miaoshou_collector.py' 导入配置。")
    print("请确保 'miaoshou_collector.py' 文件存在于同一目录下，并且包含 MIAOSHOU_URL 和 EXTENSION_PATH 变量。")
    sys.exit(1)

class MiaoshouRecorder:
    """
    一个用于启动带有妙手插件的Playwright录制功能的测试类。
    此版本使用 page.pause() 来启动带录制功能的 Inspector。
    """
    def __init__(self):
        """
        初始化录制器，检查配置是否有效。
        """
        if not all([MIAOSHOU_URL, EXTENSION_PATH]):
            raise ValueError("MIAOSHOU_URL 和 EXTENSION_PATH 不能为空。请检查 miaoshou_collector.py 中的配置。")
        
        print("--- Playwright 录制器配置 ---")
        print(f"起始 URL: {MIAOSHOU_URL}")
        print(f"插件路径: {EXTENSION_PATH}")
        print("---------------------------------")

    async def start_recording_async(self):
        """
        启动 Playwright Inspector (带有录制功能)。
        这将打开一个加载了插件的浏览器窗口，您可以在其中进行操作，
        Playwright Inspector 会显示并记录您的操作。
        """
        print("\n正在启动带有插件的浏览器...")
        print("浏览器和 Playwright Inspector 窗口即将打开。")
        print("\n--- 操作指南 ---")
        print("1. 在新打开的浏览器窗口中执行您想要录制的操作（例如登录、点击按钮等）。")
        print("2. Playwright Inspector 窗口会实时显示生成的代码。")
        print("3. 操作完成后，您可以从 Inspector 窗口中点击 'Record' 按钮停止录制，然后点击 'Copy' 按钮复制生成的代码。")
        print("4. 关闭浏览器窗口即可结束整个会话。")
        print("------------------\n")

        proxy_settings = {
            "server": "http://127.0.0.1:10908"
        }
        print(f"正在使用代理服务器: {proxy_settings['server']}")

        async with async_playwright() as p:
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
            await page.goto(MIAOSHOU_URL)
            
            # page.pause() 会打开 Inspector 并暂停脚本执行，允许用户交互和录制
            print("浏览器已打开，Inspector 已激活。现在您可以开始操作了...")
            await page.pause()
            
            await context.close()
            print("录制会话已结束。")

    def start(self):
        """
        同步方法，用于运行异步的录制启动器。
        """
        try:
            asyncio.run(self.start_recording_async())
        except KeyboardInterrupt:
            print("\n录制被用户中断。")

# --- 用于直接运行录制器的入口 ---
if __name__ == '__main__':
    recorder = MiaoshouRecorder()
    recorder.start()
