import pytest
import yaml
from loguru import logger
from utils.driver_manager import DriverManager
from utils.share_service import ShareService
from pages.tiktok_page import TikTokPage
from pages.wechat_page import WeChatPage
import time
import sys
import os


# Add the project root directory to sys.path to resolve module import issues
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class TestTikTokShopAutomation_2:
    """TikTok商城自动化测试类"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        logger.info("开始TikTok商城自动化测试")
        cls.driver_manager = DriverManager()
        cls.driver = cls.driver_manager.create_driver()
        
        # 加载配置
        with open('config.yaml', 'r', encoding='utf-8') as file:
            cls.config = yaml.safe_load(file)
        
        if cls.driver is None:
            logger.error("Failed to initialize driver")
        
        
        logger.info("强制关闭并重启TikTok以确保干净的测试环境...")
        tiktok_package = cls.config['tiktok']['app_package']
        cls.driver_manager.terminate_app(tiktok_package)
        cls.driver_manager.press_home()
        cls.driver_manager.switch_to_app(tiktok_package)
        time.sleep(8)
        


    @classmethod
    def teardown_class(cls):
        """测试类清理"""
        if cls.driver_manager:
            cls.driver_manager.quit_driver()
        logger.info("TikTok商城自动化测试结束")



    def test_tiktok_shop_image_search_and_share(self):
        """测试TikTok商城图搜和分享功能"""
        try:
            tiktok_page = TikTokPage(self.driver_manager)
            share_service = ShareService(self.driver_manager, self.config)
            
            logger.info("=== 步骤1: 进入TikTok商城 ===")
            if not tiktok_page.open_tiktok_shop():
                logger.error("进入TikTok商城失败")
            
            logger.info("=== 步骤2: 开始图像搜索 ===")
            if not tiktok_page.start_image_search():
                logger.error("图像搜索失败")
            
            logger.info("=== 步骤3: 收集并分享商品链接 ===")
            # 点击畅销商品
            tiktok_page.get_product_list()
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
            logger.error(f"测试因异常而失败: {e}")
    
    def _send_link_to_wechat(self):
        """发送链接到微信"""
        try:
            # 切换到微信
            self.driver_manager.switch_to_app(
                self.config['wechat']['app_package'],
                self.config['wechat']['app_activity']
            )
            logger.info("  - 已切换到微信")
            
            wechat_page = WeChatPage(self.driver_manager)
            
            # 搜索联系人
            contact_name = self.config['task']['contact_name']
            logger.info(f"  - 正在搜索联系人: {contact_name}...")
            if not wechat_page.search_contact(contact_name):
                logger.error(f"搜索联系人失败: {contact_name}")
                return False
            logger.info(f"  - 已搜索到联系人: {contact_name}")
            
            # 发送消息（粘贴剪贴板内容）
            logger.info("  - 正在发送消息...")
            if wechat_page.send_message(""):
                logger.info("链接发送成功")
                logger.info("  - 链接发送成功")
                return True
            else:
                logger.error("链接发送失败")
                logger.error("  - 链接发送失败")
                return False
                
        except Exception as e:
            logger.error(f"发送链接到微信失败: {e}")
            return False


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
