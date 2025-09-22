from loguru import logger
import pyperclip
import os
from pages.wechat_page import WeChatPage
import time
from appium.webdriver.common.appiumby import AppiumBy

from datetime import datetime

class ShareService:
    """
    处理分享操作的服务类。
    """
    def __init__(self, driver_manager, config, output_filename=None):
        self.driver_manager = driver_manager
        self.config = config
        self.driver = driver_manager.driver
        self.output_filename = output_filename

    def share_link(self, link):
        """
        根据配置的分享目标，执行相应的分享操作。
        """
        target = self.config['task'].get('share_target', 'file') # 默认为保存到文件
        logger.info(f"分享目标: {target}")

        if target == 'wechat':
            return self._share_to_wechat(link)
        elif target == 'file':
            return self._save_to_file(link)
        else:
            logger.error(f"不支持的分享目标: {target}")
            return False

    def _share_to_wechat(self, link):
        """
        私有方法：分享链接到微信。
        """
        try:
            pyperclip.copy(link) # 确保剪贴板内容是当前链接
            wechat_page = WeChatPage(self.driver)
            contact_name = self.config['task']['contact_name']

            # 检查是否已在聊天页面
            if wechat_page.helper.find_element_safe((AppiumBy.XPATH, f"//android.widget.TextView[@text='{contact_name}']"), timeout=3):
                return wechat_page.send_message("")

            # 如果不在，执行完整流程
            self.driver_manager.terminate_app(self.config['wechat']['app_package'])
            self.driver_manager.press_home()
            self.driver_manager.switch_to_app(self.config['wechat']['app_package'])
            time.sleep(5)
            
            if wechat_page.search_contact(contact_name) and wechat_page.send_message(""):
                return True
        except Exception as e:
            logger.error(f"分享到微信失败: {e}")
        
        return False

    def _save_to_file(self, link):
        """
        私有方法：将链接保存到本地文件。
        每次调用都会生成一个带时间戳的新文件。
        """
        try:
            links_dir = 'shared_links'
            os.makedirs(links_dir, exist_ok=True)

            # 生成带时间戳的文件名
            timestamp = datetime.now().strftime("%m%d%H%M%S")
            filename = f"links-{timestamp}.txt"
            file_path = os.path.join(links_dir, filename)

            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(f"{link}\n")
            
            logger.success(f"链接已保存到: {file_path}")
            return True
        except Exception as e:
            logger.error(f"保存链接到文件失败: {e}")
            return False
