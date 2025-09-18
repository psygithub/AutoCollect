from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy
from utils.element_helper import ElementHelper
from loguru import logger
import time
import pyperclip


class TikTokPage:
    """TikTok页面操作类"""
    
    def __init__(self, driver):
        self.driver = driver
        self.helper = ElementHelper(driver)
        
        # === 页面元素定位器 (已根据最终流程更新) ===

        shop_xpath='//android.widget.TextView[@resource-id="android:id/text1" and @text="商城"] | //android.widget.TextView[@resource-id="com.zhiliaoapp.musically:id/title" and (@text="商城" or @text="Shop")]'
        self.shop_tab = (AppiumBy.XPATH, shop_xpath)
        # 使用XPath定位搜索框和相机图标的组合，更加健壮
        self.search_button = (AppiumBy.XPATH, "//*[contains(@text, '搜索') or contains(@content-desc, '搜索')]/../*[contains(@class, 'ImageView')]")
        camera_xapth='//androidx.recyclerview.widget.RecyclerView[@resource-id="com.zhiliaoapp.musically:id/hz0"]/android.widget.FrameLayout/android.widget.FrameLayout/com.ss.android.ugc.aweme.ecommerce.ui.EcomFlattenUIImage[2]'
        self.camera_button = (AppiumBy.XPATH, camera_xapth)
        upload_photo_btn_xpath='//android.widget.ImageView[@content-desc="图片"]'
        self.upload_photo_button = (AppiumBy.XPATH, upload_photo_btn_xpath)
        take_photoe_xpath='(//android.widget.ImageView[@resource-id="com.zhiliaoapp.musically:id/f4n"])[1]'
        self.take_photo_button = (AppiumBy.XPATH, take_photoe_xpath)
        # self.confirm_photo_button = (AppiumBy.XPATH, "//android.widget.TextView[@text='确定' or @text='OK']")
        
        # 更通用的XPath，匹配所有产品项
        product_items_xpath='//android.widget.FrameLayout[@resource-id="com.zhiliaoapp.musically:id/g8d"]/android.widget.FrameLayout/android.widget.FrameLayout/com.lynx.tasm.behavior.ui.view.UIComponent'
        self.product_items = (AppiumBy.XPATH, product_items_xpath)
        share_btn_xpath='//android.view.ViewGroup[@resource-id="com.zhiliaoapp.musically:id/rg8"]'
        self.share_button = (AppiumBy.XPATH, share_btn_xpath)
        copy_link_btn_xpath='(//android.widget.ImageView[@resource-id="com.zhiliaoapp.musically:id/rfq"])[1] | //android.widget.TextView[@text="复制链接" or @text="Copy Link"]'
        self.copy_link_option = (AppiumBy.XPATH, copy_link_btn_xpath)

        best_sell_product_xpath='//com.lynx.tasm.behavior.ui.view.UIView[@content-desc="畅销商品"]'
        self.best_sell_product = (AppiumBy.XPATH, best_sell_product_xpath)

    def open_tiktok_shop(self):
        """打开TikTok商城"""
        try:
            logger.info("正在打开TikTok商城...")
            
            # 增加更长的等待时间以确保应用完全加载
            logger.info("等待10秒，让应用充分加载...")
            time.sleep(10)
            self.helper.handle_popups()
            
            # 点击商城标签
            if self.helper.click_element_safe(self.shop_tab, timeout=15):
                logger.info("成功进入TikTok商城")
                time.sleep(1)
                return True
            else:
                logger.error("未找到商城入口")
                return False
                
        except Exception as e:
            logger.error(f"打开TikTok商城失败: {e}")
            return False
    
    def start_image_search(self):
        """开始图像搜索 (根据简化流程重写)"""
        try:
            logger.info("开始图像搜索...")

            # 1. 直接点击商城主页的相机图标
            if not self.helper.click_element_safe(self.camera_button, timeout=15):
                logger.error("在商城主页未找到相机图标")
                return False
            
            logger.info("成功点击相机图标，进入相册")
            time.sleep(2) # 等待相册加载
            
            # 2. 选择相册中的第一张图片
            if not self.helper.click_element_safe(self.upload_photo_button):
                logger.error("在相册中未找到任何图片")
                return False
            

            # 2. 选择相册中的第一张图片
            if self.helper.click_element_safe(self.take_photo_button):
                logger.info("成功选择第一张图片进行搜索")
                time.sleep(5) # 等待搜索结果加载
                return True
            else:
                logger.error("在相册中未找到任何图片")
                return False
                
        except Exception as e:
            logger.error(f"图像搜索失败: {e}")
            return False
    
    def get_product_list(self):
        """获取商品列表"""
        try:
            logger.info("获取商品列表...")
            
            # 等待搜索结果加载
            time.sleep(2)
            logger.info("点击畅销产品...")
            self.helper.click_element_safe(self.best_sell_product, timeout=5)
            time.sleep(2)
                

            # 查找商品元素
            products = self.helper.find_elements_safe(self.product_items, timeout=10)
            
            if products:
                logger.info(f"找到 {len(products)} 个商品")
                return products
            else:
                logger.warning("未找到商品列表")
                return []
                
        except Exception as e:
            logger.error(f"获取商品列表失败: {e}")
            return []
    
    def enter_product_detail(self, product_element):
        """进入商品详情页"""
        try:
            logger.info("进入商品详情页...")
            product_element.click()
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"进入商品详情页失败: {e}")
            return False
    
    def share_product_link(self):
        """分享商品链接"""
        try:
            logger.info("开始分享商品链接...")
            
            # 使用更长的等待时间来查找分享按钮
            if not self.helper.click_element_safe(self.share_button, timeout=10):
                logger.error("未找到分享按钮")
                return False
            
            time.sleep(2) # 等待分享菜单弹出
            
            # 使用更长的等待时间来查找复制链接选项
            if self.helper.click_element_safe(self.copy_link_option, timeout=10):
                logger.info("商品链接已复制到剪贴板")
                time.sleep(1) # 等待剪贴板更新
                return True
            else:
                logger.error("未找到复制链接选项")
                return False
                
        except Exception as e:
            logger.error(f"分享商品链接失败: {e}")
            return False
    
    def go_back(self):
        """返回上一页"""
        try:
            self.driver.back()
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"返回上一页失败: {e}")
            return False

    def share_and_collect_links(self, max_links=20):
        """
        循环分享和收集商品链接，直到达到指定数量或列表结束。

        :param max_links: 需要收集的最大链接数
        :return: 收集到的链接列表
        """
        logger.info(f"开始收集商品链接，目标: {max_links}个")
        collected_links = []
        processed_elements = set()

        while len(collected_links) < max_links:
            products = self.helper.find_elements_safe(self.product_items)
            if not products:
                logger.warning("当前页面未找到任何商品。")
                break

            new_product_found = False
            for product in products:
                try:
                    # 使用元素的位置和大小作为唯一标识符
                    uid = (product.location['x'], product.location['y'], product.size['width'], product.size['height'])
                    if uid in processed_elements:
                        continue

                    processed_elements.add(uid)
                    new_product_found = True

                    logger.info(f"处理新商品... 当前已收集 {len(collected_links)}/{max_links}")
                    
                    # 1. 进入详情页
                    if self.enter_product_detail(product):
                        # 2. 分享并复制链接
                        if self.share_product_link():
                            pyperclip.copy('') # 清空剪贴板
                            # 增加重试逻辑来读取剪贴板
                            link = None
                            for _ in range(3): # 重试3次
                                time.sleep(0.5)
                                link = pyperclip.paste()
                                if link and link.startswith('http'):
                                    break
                            
                            if link and link.startswith('http'):
                                collected_links.append(link)
                                logger.success(f"成功收集链接: {link}")
                            else:
                                logger.warning(f"从剪贴板获取的链接无效: '{link}'")
                        
                        # 3. 返回列表页
                        self.go_back()

                        if len(collected_links) >= max_links:
                            break
                except Exception as e:
                    logger.error(f"处理单个商品时出错: {e}")
                    # 如果出错，尝试返回列表页继续
                    self.go_back()
            
            if len(collected_links) >= max_links:
                logger.info("已达到目标链接数。")
                break

            if not new_product_found:
                logger.info("滚动后未发现新商品，认为已到达列表底部。")
                break

            # 滑动页面以加载更多商品
            logger.info("滑动页面以加载更多...")
            self.helper.swipe_up()
            time.sleep(3) # 等待新商品加载

        if not collected_links:
            logger.warning("未能收集到任何商品链接。")
        else:
            logger.info(f"总共收集到 {len(collected_links)} 个链接。")
            
        return collected_links
