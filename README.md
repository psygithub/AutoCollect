# TikTok商城自动化测试项目

基于Appium框架的TikTok商城图像搜索和微信分享自动化测试项目。

## 功能特性

- 🔍 **图像搜索**: 自动进入TikTok商城，使用相机拍照进行商品搜索
- 📱 **商品浏览**: 自动遍历搜索结果中的商品列表
- 🔗 **链接复制**: 自动进入商品详情页并复制分享链接
- 💬 **微信分享**: 自动切换到微信应用，向指定联系人发送商品链接
- 📊 **测试报告**: 生成详细的测试报告和日志
- 📸 **截图记录**: 自动截图记录测试过程

## 项目结构

```
AutoCollectItem/
├── config.yaml                    # 配置文件
├── requirements.txt               # Python依赖
├── run_test.py                   # 主运行脚本
├── README.md                     # 项目说明文档
├── utils/                        # 工具类
│   ├── __init__.py
│   ├── driver_manager.py         # Appium驱动管理器
│   └── element_helper.py         # 元素操作辅助类
├── pages/                        # 页面对象模型
│   ├── __init__.py
│   ├── tiktok_page.py           # TikTok页面操作类
│   └── wechat_page.py           # 微信页面操作类
├── tests/                        # 测试用例
│   ├── __init__.py
│   └── test_tiktok_shop_automation.py  # 主测试用例
├── logs/                         # 日志文件目录
├── screenshots/                  # 截图文件目录
└── reports/                      # 测试报告目录
```

## 环境要求

### 系统要求
- Windows 10/11 或 macOS 或 Linux
- Python 3.8+
- Node.js 14+
- Android SDK
- 已连接的Android设备或模拟器

### 应用要求
- 设备上已安装TikTok应用
- 设备上已安装微信应用
- 设备已登录相关账号

## 安装步骤

### 1. 安装Node.js和Appium
```bash
# 安装Node.js (如果未安装)
# 下载地址: https://nodejs.org/

# 安装Appium
npm install -g appium

# 安装UiAutomator2驱动
appium driver install uiautomator2
```

### 2. 安装Android SDK
```bash
# 下载Android Studio或单独的SDK工具
# 设置ANDROID_HOME环境变量
# 将platform-tools添加到PATH
```

### 3. 克隆项目并安装Python依赖
```bash
git clone <项目地址>
cd AutoCollectItem
pip install -r requirements.txt
```

### 4. 配置设备
```bash
# 连接Android设备并启用USB调试
# 或启动Android模拟器

# 检查设备连接
adb devices
```

## 配置说明

编辑 `config.yaml` 文件，根据实际情况修改配置：

```yaml
# 设备配置
device:
  platform_name: "Android"
  platform_version: "11.0"  # 修改为实际设备版本
  device_name: "Android Device"
  automation_name: "UiAutomator2"

# 测试配置
test:
  max_products_to_process: 5  # 最多处理的商品数量
  contact_name: "测试联系人"  # 修改为实际的微信联系人名称
```

## 使用方法

### 方法1: 使用运行脚本（推荐）
```bash
python run_test.py
```

### 方法2: 直接运行pytest
```bash
# 启动Appium服务器
appium server

# 在另一个终端运行测试
pytest tests/test_tiktok_shop_automation.py -v -s
```

### 方法3: 运行单个测试方法
```bash
pytest tests/test_tiktok_shop_automation.py::TestTikTokShopAutomation::test_tiktok_shop_image_search_and_share -v -s
```

## 测试流程

1. **启动TikTok应用**: 自动启动并切换到TikTok应用
2. **进入商城**: 点击商城标签进入TikTok商城
3. **图像搜索**: 点击搜索 → 相机 → 拍照 → 确认，启动图像搜索
4. **获取商品列表**: 等待搜索结果加载，获取商品列表
5. **遍历商品**: 依次进入每个商品详情页
6. **复制链接**: 点击分享按钮，选择复制链接
7. **发送到微信**: 切换到微信，搜索联系人，发送链接
8. **重复处理**: 返回TikTok继续处理下一个商品

## 元素定位策略

项目使用多种定位策略确保稳定性：

### TikTok元素定位
- 商城入口: `//android.widget.TextView[@text='商城' or @text='Shop']`
- 搜索按钮: `com.ss.android.ugc.trill:id/search_entrance`
- 相机按钮: `//android.widget.ImageView[contains(@content-desc, '相机')]`
- 商品列表: `//android.widget.RecyclerView//android.widget.FrameLayout`

### 微信元素定位
- 搜索按钮: `//android.widget.TextView[@text='搜索']`
- 消息输入框: `//android.widget.EditText[@text='请输入消息内容']`
- 发送按钮: `//android.widget.Button[@text='发送']`

## 日志和报告

### 日志文件
- 位置: `logs/test_YYYY-MM-DD.log`
- 包含详细的执行步骤和错误信息
- 自动按日期轮转，保留7天

### 截图文件
- 位置: `screenshots/`
- 自动截图记录关键步骤
- 错误时自动截图保存现场

### 测试报告
- 位置: `reports/allure-results/`
- 使用Allure生成详细的HTML报告
- 查看报告: `allure serve reports/allure-results`

## 故障排除

### 常见问题

1. **Appium服务器连接失败**
   ```bash
   # 检查Appium是否启动
   appium server
   
   # 检查端口是否被占用
   netstat -an | grep 4723
   ```

2. **设备连接问题**
   ```bash
   # 检查设备连接
   adb devices
   
   # 重启adb服务
   adb kill-server
   adb start-server
   ```

3. **元素定位失败**
   - 检查应用版本是否匹配
   - 使用Appium Inspector查看元素属性
   - 调整等待时间和定位策略

4. **应用切换失败**
   - 确保应用已安装并可正常启动
   - 检查应用包名和Activity名称
   - 确保设备有足够内存

### 调试技巧

1. **启用详细日志**
   ```python
   # 在config.yaml中设置
   test:
     implicit_wait: 15  # 增加等待时间
   ```

2. **单步调试**
   ```python
   # 在测试代码中添加断点
   import pdb; pdb.set_trace()
   ```

3. **手动截图**
   ```python
   # 在关键步骤添加截图
   self.driver_manager.take_screenshot("debug_step.png")
   ```

## 扩展功能

### 添加新的页面操作
1. 在 `pages/` 目录下创建新的页面类
2. 继承基础的元素操作方法
3. 在测试用例中引用新页面类

### 添加新的测试用例
1. 在 `tests/` 目录下创建新的测试文件
2. 使用pytest的测试类和方法结构
3. 利用现有的页面对象和工具类

### 自定义配置
1. 在 `config.yaml` 中添加新的配置项
2. 在相应的类中读取和使用配置
3. 支持环境变量覆盖配置

## 注意事项

1. **设备要求**: 确保设备性能足够，避免应用响应缓慢
2. **网络环境**: 确保网络连接稳定，避免加载超时
3. **应用版本**: 定期更新元素定位器以适配新版本应用
4. **权限设置**: 确保应用有相机、存储等必要权限
5. **电量管理**: 关闭设备的省电模式和应用后台限制

## 许可证

本项目仅供学习和测试使用，请遵守相关应用的使用条款。

## 贡献

欢迎提交Issue和Pull Request来改进项目。

## 联系方式

如有问题请通过Issue或邮件联系。
