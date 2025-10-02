from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy
from utils.element_helper import ElementHelper
from loguru import logger
import time
import pyperclip


class WeChatPage:
    """微信页面操作类"""
    
    def __init__(self, driver):
        self.driver = driver
        self.helper = ElementHelper(driver)
        
        # 页面元素定位器
        self.search_button = (AppiumBy.ID, "com.tencent.mm:id/action_option_search")
        self.search_input = (AppiumBy.ID, "com.tencent.mm:id/search_input")
        self.contact_item = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, '{}')]")
        self.message_input = (AppiumBy.XPATH, "//android.widget.EditText[@text='请输入消息内容']")
        self.send_button = (AppiumBy.XPATH, "//android.widget.Button[@text='发送']")
        self.paste_option = (AppiumBy.XPATH, "//android.widget.TextView[@text='粘贴']")
    
    def open_wechat(self):
        """打开微信"""
        try:
            logger.info("正在打开微信...")
            time.sleep(3)
            return True
        except Exception as e:
            logger.error(f"打开微信失败: {e}")
            return False
    
    def search_contact(self, contact_name):
        """搜索联系人"""
        try:
            logger.info(f"搜索联系人: {contact_name}")
            
            # 确保在主页
            # (可以根据需要添加返回主页的逻辑)

            # 点击顶部的搜索图标
            if not self.helper.click_element_safe(self.search_button):
                logger.error("未找到顶部的搜索图标")
                return False
            
            time.sleep(1)
            
            # 输入联系人名称
            if not self.helper.input_text_safe(self.search_input, contact_name):
                logger.error("输入联系人名称失败")
                return False
            
            time.sleep(2)
            
            # 点击搜索结果中的联系人
            contact_locator = (AppiumBy.XPATH, f"//android.widget.TextView[contains(@text, '{contact_name}')]")
            if self.helper.click_element_safe(contact_locator):
                logger.info(f"成功找到并点击联系人: {contact_name}")
                time.sleep(2)
                return True
            else:
                logger.error(f"未找到联系人: {contact_name}")
                return False
                
        except Exception as e:
            logger.error(f"搜索联系人失败: {e}")
            return False
    
    def send_message(self, message):
        """发送消息，优先使用剪贴板内容"""
        try:
            logger.info("发送消息...")
            
            message_input = self.helper.find_element_safe(self.message_input)
            if not message_input:
                logger.error("未找到消息输入框")
                return False
            
            # 直接将剪贴板内容设置为元素的值
            clipboard_content = pyperclip.paste()
            if clipboard_content:
                message_input.set_value(clipboard_content)
                logger.info("已将剪贴板内容粘贴到输入框。")
            elif message:
                message_input.set_value(message)
                logger.info(f"已输入消息: {message}")
            else:
                logger.warning("剪贴板和消息参数均为空，无可发送内容。")
                return False

            time.sleep(1)

            if self.helper.click_element_safe(self.send_button):
                logger.info("消息发送成功")
                return True
            else:
                logger.error("未找到或未能点击发送按钮")
                return False
                
        except Exception as e:
            logger.error(f"发送消息时发生异常: {e}")
            return False
    
    def go_back_to_chat_list(self):
        """返回聊天列表"""
        try:
            self.driver.back()
            time.sleep(1)
            self.driver.back()
            time.sleep(1)
            return True
        except Exception as e:
            logger.error(f"返回聊天列表失败: {e}")
            return False
