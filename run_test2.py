import pytest
import yaml
from loguru import logger
from utils.driver_manager import DriverManager
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
    
    @classmethod
    def teardown_class(cls):
        """测试类清理"""
        if cls.driver_manager:
            cls.driver_manager.quit_driver()
        logger.info("TikTok商城自动化测试结束")
    
    def test_tiktok_shop_image_search_and_share(self):
        """测试TikTok商城图搜和分享功能"""
        try:
            # 1. 启动TikTok应用
            logger.info("=== 步骤1: 启动TikTok应用 ===")
            logger.info("  - 正在切换到TikTok应用...")
            self.driver_manager.switch_to_app(
                self.config['tiktok']['app_package'],
                self.config['tiktok']['app_activity']
            )
            
            tiktok_page = TikTokPage(self.driver)
            
            # 2. 进入TikTok商城
            logger.info("=== 步骤2: 进入TikTok商城 ===")
            logger.info("  - 正在打开TikTok商城...")
            assert tiktok_page.open_tiktok_shop(), "进入TikTok商城失败"
            logger.info("  - 已进入TikTok商城")
            logger.info("  - 正在开始图像搜索...")
            
            # 3. 开始图像搜索
            logger.info("=== 步骤3: 开始图像搜索 ===")
            logger.info("  - 正在开始图像搜索...")
            assert tiktok_page.start_image_search(), "图像搜索失败"
            logger.info("  - 图像搜索已开始")
            
            # 4. 获取商品列表
            logger.info("=== 步骤4: 获取商品列表 ===")
            logger.info("  - 正在获取商品列表...")
            products = tiktok_page.get_product_list()
            logger.info("  - 已获取商品列表")
            assert len(products) > 0, "未找到商品列表"
            
            # 5. 处理每个商品
            max_products = min(len(products), self.config['test']['max_products_to_process'])
            logger.info(f"=== 步骤5: 处理前{max_products}个商品 ===")
            logger.info("  - 正在处理商品...")
            
            successful_shares = 0
            
            for i in range(max_products):
                try:
                    logger.info(f"处理第{i+1}个商品...")
                    logger.info(f"  - 正在进入第{i+1}个商品详情页...")
                    
                    # 进入商品详情页
                    if not tiktok_page.enter_product_detail(products[i]):
                        logger.warning(f"进入第{i+1}个商品详情页失败，跳过")
                        continue
                    logger.info(f"  - 已进入第{i+1}个商品详情页")
                    
                    # 分享商品链接
                    logger.info(f"  - 正在分享第{i+1}个商品链接...")
                    if tiktok_page.share_product_link():
                        logger.info(f"第{i+1}个商品链接复制成功")
                        logger.info(f"  - 链接复制成功")
                        
                        # 切换到微信发送链接
                        logger.info("  - 正在切换到微信发送链接...")
                        if self._send_link_to_wechat():
                            successful_shares += 1
                            logger.info(f"第{i+1}个商品链接发送到微信成功")
                        else:
                            logger.warning(f"第{i+1}个商品链接发送到微信失败")
                    else:
                        logger.warning(f"第{i+1}个商品链接复制失败")
                    
                    # 返回TikTok商品列表
                    logger.info("  - 正在返回TikTok商品列表...")
                    self.driver_manager.switch_to_app(self.config['tiktok']['app_package'])
                    time.sleep(2)
                    logger.info("  - 已返回TikTok商品列表")
                    
                    # 如果不是最后一个商品，需要重新获取商品列表
                    if i < max_products - 1:
                        products = tiktok_page.get_product_list()
                        if len(products) <= i + 1:
                            logger.warning("商品列表不足，结束处理")
                            break
                    
                except Exception as e:
                    logger.error(f"处理第{i+1}个商品时出错: {e}")
                    # 尝试返回到商品列表
                    self.driver_manager.switch_to_app(self.config['tiktok']['app_package'])
                    time.sleep(2)
                    continue
            
            logger.info(f"=== 测试完成: 成功处理{successful_shares}个商品 ===")
            assert successful_shares > 0, "没有成功分享任何商品链接"
            
        except Exception as e:
            logger.error(f"测试执行失败: {e}")
            # 截图保存错误状态
            self.driver_manager.take_screenshot("test_error.png")
            raise
    
    def _send_link_to_wechat(self):
        """发送链接到微信"""
        try:
            # 切换到微信
            self.driver_manager.switch_to_app(
                self.config['wechat']['app_package'],
                self.config['wechat']['app_activity']
            )
            logger.info("  - 已切换到微信")
            
            wechat_page = WeChatPage(self.driver)
            
            # 搜索联系人
            contact_name = self.config['test']['contact_name']
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
