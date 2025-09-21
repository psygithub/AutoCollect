import yaml
from appium import webdriver
from appium.options.android import UiAutomator2Options
from loguru import logger
import os
import time


class DriverManager:
    """Appium驱动管理器"""
    
    def __init__(self, config_path="config.yaml"):
        self.config = self._load_config(config_path)
        self.driver = None
        
    def _load_config(self, config_path):
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    
    def create_driver(self):
        """创建Appium驱动"""
        try:
            logger.info(f"使用配置创建驱动: {self.config['device']}")
            options = UiAutomator2Options()
            options.platform_name = self.config['device']['platform_name']
            # Force platformVersion to be a string, which is a common Appium requirement
            options.platform_version = str(self.config['device']['platform_version'])
            options.device_name = self.config['device']['device_name']
            options.automation_name = self.config['device']['automation_name']
            options.no_reset = self.config['device']['no_reset']
            options.full_reset = self.config['device']['full_reset']
            
            # 同时提供app_package和app_activity，确保启动正确的应用界面
            options.app_package = self.config['tiktok']['app_package']
            options.app_activity = self.config['tiktok']['app_activity']
            
            # 设置隐式等待
            options.implicit_wait = self.config['task']['implicit_wait']
            
            self.driver = webdriver.Remote(
                self.config['appium']['server_url'],
                options=options
            )
            
            logger.info("Appium驱动创建成功")
            return self.driver
            
        except Exception as e:
            logger.error(f"创建Appium驱动失败: {e}")
            logger.error("--- Appium连接失败排查指引 ---")
            logger.error("1. 请确认您的Appium Server是否已经启动。")
            logger.error("2. 请检查您的安卓设备是否已通过USB连接，并已开启'开发者模式'和'USB调试'。")
            logger.error("3. 请确认Web界面上配置的'设备名称 (UDID)'与您通过`adb devices`命令查看到的设备ID完全一致。")
            logger.error("4. 请确认Web界面上配置的'安卓版本'与您设备的系统版本一致。")
            logger.error(f"5. 请检查Appium Server的地址配置是否正确: {self.config['appium']['server_url']}")
            self.driver = None # Ensure driver is None on failure
            return None
    
    def quit_driver(self):
        """退出驱动"""
        if self.driver:
            self.driver.quit()
            logger.info("Appium驱动已退出")

    def press_home(self):
        """返回手机主屏幕"""
        try:
            self.driver.press_keycode(3) # 3 is the keycode for HOME
            logger.info("已返回主屏幕")
            time.sleep(1)
        except Exception as e:
            logger.error(f"返回主屏幕失败: {e}")

    def terminate_app(self, app_package):
        """关闭指定应用"""
        try:
            self.driver.terminate_app(app_package)
            logger.info(f"已关闭应用: {app_package}")
            time.sleep(1)
        except Exception as e:
            logger.error(f"关闭应用失败: {e}")
    
    def switch_to_app(self, app_package, app_activity=None):
        """切换到指定应用"""
        try:
            # 使用 activate_app，不依赖于具体的activity，更加稳定
            self.driver.activate_app(app_package)
            logger.info(f"已切换到应用: {app_package}")
        except Exception as e:
            logger.error(f"切换应用失败: {e}")
            raise
    
    def take_screenshot(self, filename=None):
        """截图"""
        if not filename:
            import time
            filename = f"screenshot_{int(time.time())}.png"
        
        screenshot_dir = self.config['task']['screenshot_path']
        os.makedirs(screenshot_dir, exist_ok=True)
        
        filepath = os.path.join(screenshot_dir, filename)
        self.driver.save_screenshot(filepath)
        logger.info(f"截图已保存: {filepath}")
        return filepath
