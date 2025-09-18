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
            tiktok_page = TikTokPage(self.driver)
            share_service = ShareService(self.driver_manager, self.config)
            
            logger.info("=== 步骤1: 进入TikTok商城 ===")
            if not tiktok_page.open_tiktok_shop():
                pytest.fail("进入TikTok商城失败")
            
            logger.info("=== 步骤2: 开始图像搜索 ===")
            if not tiktok_page.start_image_search():
                pytest.fail("图像搜索失败")
            
            logger.info("=== 步骤3: 收集并分享商品链接 ===")
            shared_links = self._collect_and_share_links(tiktok_page, share_service)
            
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

    def _collect_and_share_links(self, tiktok_page, share_service):
        max_links = self.config['test']['max_products_to_process']
        shared_links = []
        processed_element_uids = set()
        
        base_xpath = '//android.widget.FrameLayout[@resource-id="com.zhiliaoapp.musically:id/g8d"]/android.widget.FrameLayout/android.widget.FrameLayout/com.lynx.tasm.behavior.ui.view.UIComponent'
        
        while len(shared_links) < max_links:
            new_links_on_this_scroll = 0
            for i in range(3, 7):
                if len(shared_links) >= max_links:
                    break
                
                product_xpath = f"{base_xpath}[{i}]"
                product = tiktok_page.helper.find_element_safe((AppiumBy.XPATH, product_xpath), timeout=5)
                
                if not product:
                    continue

                try:
                    uid = (product.location['x'], product.location['y'], product.size['width'], product.size['height'])
                    if uid in processed_element_uids:
                        continue
                    
                    processed_element_uids.add(uid)
                    
                    if tiktok_page.enter_product_detail(product):
                        if tiktok_page.share_product_link():
                            # 从设备获取剪贴板内容，而不是主机
                            link = self.driver.get_clipboard_text()
                            if link and link.startswith('http'):
                                logger.info(f"成功获取到链接: {link}")
                                if share_service.share_link(link):
                                    shared_links.append(link)
                                    new_links_on_this_scroll += 1
                                else:
                                    logger.warning(f"分享链接失败: {link}")
                            else:
                                logger.warning(f"从剪贴板获取的链接无效: {link}")
                        
                        self.driver_manager.switch_to_app(self.config['tiktok']['app_package'])
                        tiktok_page.go_back()

                except Exception as e:
                    logger.error(f"处理索引 {i} 的产品时出错: {e}")
                    self.driver_manager.switch_to_app(self.config['tiktok']['app_package'])
                    tiktok_page.go_back()

            if len(shared_links) >= max_links:
                break

            if new_links_on_this_scroll == 0:
                logger.info("在当前页面未发现任何新产品，认为已到达列表底部。")
                break
            
            tiktok_page.helper.swipe_up()
            time.sleep(3)
            
        return shared_links
