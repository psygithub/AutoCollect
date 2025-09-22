from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy
from loguru import logger
import time


class ElementHelper:
    """元素操作辅助类"""
    
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)
    
    def find_element_safe(self, locator, timeout=10):
        """安全查找元素"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return element
        except Exception as e:
            logger.warning(f"未找到元素 {locator}: {e}")
            return None
    
    def find_elements_safe(self, locator, timeout=10):
        """安全查找多个元素"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return self.driver.find_elements(*locator)
        except Exception as e:
            logger.warning(f"未找到元素列表 {locator}: {e}")
            return []
    
    def click_element_safe(self, locator, timeout=3):
        """安全点击元素"""
        try:
            # 使用传入的timeout，而不是self.wait的默认值
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            element.click()
            logger.info(f"成功点击元素: {locator}")
            return True
        except Exception as e:
            logger.error(f"点击元素失败 {locator}: {e}")
            return False
    
    def input_text_safe(self, locator, text, timeout=10):
        """安全输入文本"""
        try:
            element = self.find_element_safe(locator, timeout)
            if element:
                element.clear()
                element.send_keys(text)
                logger.info(f"成功输入文本: {text}")
                return True
        except Exception as e:
            logger.error(f"输入文本失败: {e}")
        return False
    
    def wait_for_element_disappear(self, locator, timeout=10):
        """等待元素消失"""
        try:
            WebDriverWait(self.driver, timeout).until_not(
                EC.presence_of_element_located(locator)
            )
            return True
        except Exception:
            return False
    
    def scroll_to_element(self, element):
        """滚动到指定元素"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
            time.sleep(1)
        except Exception as e:
            logger.warning(f"滚动到元素失败: {e}")
    
    def swipe_up(self, duration=1000):
        """向上滑动"""
        size = self.driver.get_window_size()
        start_x = size['width'] // 2
        start_y = size['height'] * 0.8
        end_y = size['height'] * 0.2
        
        self.driver.swipe(start_x, start_y, start_x, end_y, duration)
        time.sleep(1)
    
    def handle_popups(self):
        """快速检查并处理一次弹窗"""
        logger.info("快速检查并处理弹窗...")
        try:
            keywords = [
                '关闭', '跳过', '我知道了', '同意', '允许', '以后再说',
                'close', 'Close', 'skip', 'Skip', 'Agree', 'Allow'
            ]
            conditions = " or ".join([f"contains(@text, '{k}')" for k in keywords] + [f"contains(@content-desc, '{k}')" for k in keywords])
            popup_xpath = f"//*[{conditions}]"
            
            # 使用非常短的超时时间，因为弹窗通常会立即出现
            popup_button = self.find_element_safe((AppiumBy.XPATH, popup_xpath), timeout=3)
            
            if popup_button:
                logger.info(f"发现弹窗并尝试点击: {popup_button.text}")
                popup_button.click()
                time.sleep(2)  # 等待动画
            else:
                logger.info("未发现弹窗。")
        except Exception as e:
            logger.warning(f"处理弹窗时未发生任何操作: {e}")
        return True
    
    def swipe_down(self, duration=1000):
        """向下滑动"""
        size = self.driver.get_window_size()
        start_x = size['width'] // 2
        start_y = size['height'] * 0.2
        end_y = size['height'] * 0.8
        
        self.driver.swipe(start_x, start_y, start_x, end_y, duration)
        time.sleep(1)
