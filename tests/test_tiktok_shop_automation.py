import pytest
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from pages.tiktok_page import TikTokPage
from utils.driver_manager import DriverManager
from utils.share_service import ShareService
from loguru import logger
import os
import yaml
import time
from appium.webdriver.common.appiumby import AppiumBy

@pytest.fixture(scope="class")
def driver_setup(request):
    driver_manager = DriverManager()
    driver = driver_manager.create_driver()
    
    if driver is None:
        pytest.fail("Failed to initialize driver")
    
    with open('config.yaml', 'r', encoding='utf-8') as file:
        request.cls.config = yaml.safe_load(file)
        
    request.cls.driver = driver
    request.cls.driver_manager = driver_manager
    
    logger.info("强制关闭并重启TikTok以确保干净的测试环境...")
    tiktok_package = request.cls.config['tiktok']['app_package']
    driver_manager.terminate_app(tiktok_package)
    driver_manager.press_home()
    driver_manager.switch_to_app(tiktok_package)
    time.sleep(8)
    
    yield
    
    driver_manager.quit_driver()

@pytest.mark.usefixtures("driver_setup")
class TestTikTokShopAutomation:
    def test_full_process(self):
        try:
            tiktok_page = TikTokPage(self.driver_manager)
            share_service = ShareService(self.driver_manager, self.config)
            
            logger.info("=== 步骤1: 进入TikTok商城 ===")
            if not tiktok_page.open_tiktok_shop():
                pytest.fail("进入TikTok商城失败")
            
            logger.info("=== 步骤2: 开始图像搜索 ===")
            if not tiktok_page.start_image_search():
                pytest.fail("图像搜索失败")
            
            logger.info("=== 步骤3: 收集并分享商品链接 ===")
            shared_links = tiktok_page.collect_and_share_links(share_service,self.config)
            
            logger.info("=== 步骤4: 验证结果 ===")
            if not shared_links:
                logger.warning("未能成功分享任何链接。")
            else:
                logger.success(f"成功分享了 {len(shared_links)} 个链接。")
            
            assert len(shared_links) > 0, "断言失败：未能成功分享任何产品链接。"

        except Exception as e:
            logger.error(f"测试执行期间发生意外错误: {e}")
            self.driver_manager.take_screenshot("test_error.png")
            pytest.fail(f"测试因异常而失败: {e}")
