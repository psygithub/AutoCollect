# 自动化信息采集平台

本项目是一个集成了移动端（App）自动化和桌面端（Web）自动化的多功能信息采集平台。它提供了一个Web界面来管理和运行各项自动化任务，并支持通过Docker进行容器化部署。

## 核心功能

- 🌐 **Web管理界面**: 基于Flask和Waitress，提供友好的用户界面，用于配置、启动和监控自动化任务。
- 📱 **App自动化 (TikTok)**:
    - **图像搜索**: 自动进入TikTok商城，可使用PC端指定图片或手机摄像头拍照进行商品搜索。
    - **链接采集**: 自动遍历搜索结果，进入商品详情页并提取分享链接。
    - **结果保存**: 将采集到的链接保存到带时间戳的本地文本文件中。
- 🖥️ **Web自动化 (秒手)**:
    - **链接处理**: 自动读取采集到的链接文件。
    - **浏览器操作**: 在Chrome浏览器中打开链接，并可配置代理、加载扩展程序、自动登录秒手平台等。
- 🐳 **Docker支持**: 提供`Dockerfile`，支持一键构建和部署，实现环境隔离和快速迁移。
- ⚙️ **灵活配置**: 所有关键参数均通过`config.yaml`进行配置，易于修改和维护。

## 项目结构

```
AutoCollect/
├── app.py                         # Flask Web应用主程序
├── automation_task.py             # App自动化核心逻辑
├── link_opener.py                 # Web自动化核心逻辑
├── config.yaml                    # 全局配置文件
├── Dockerfile                     # Docker配置文件
├── requirements.txt               # Python依赖
├── README.md                      # 项目说明文档
├── pages/                         # Appium页面对象模型
├── utils/                         # 工具类
├── templates/                     # Flask前端模板
├── shared_links/                  # 存放采集结果的目录
└── uploads/                       # 存放用于图像搜索的图片
```

## 环境要求

### 系统要求
- **部署环境**: Windows, macOS, Linux 或任何支持Docker的系统。
- **Python版本**: 3.11+
- **Node.js**: (如果需要手动运行Appium)

### App自动化依赖
- **Appium Server**: 用于驱动移动端App。
- **Android SDK**: `adb`等工具。
- 已连接的Android设备或模拟器，并开启USB调试。
- 设备上已安装TikTok应用。

## 架构与运行模式

本项目包含三个核心组件，可以根据需求选择不同的运行方式：

1.  **Web管理界面 (`app.py`)**: 提供配置和任务触发的可视化界面。
2.  **App自动化 (`automation_task.py`)**: 执行基于Appium的移动端任务。**此组件强依赖于外部Appium服务和物理设备连接，不适合在Docker容器内运行。**
3.  **Web自动化 (`link_opener.py`)**: 执行基于Playwright的浏览器任务。此组件可以被容器化。

因此，我们提供两种部署策略：**本地运行**和**Docker部署**。

## 部署方式一：本地直接运行 (推荐用于开发)

此方法在你的开发机上直接运行所有组件，功能最完整，尤其适合需要同时进行App和Web自动化的场景。

1.  **克隆项目**:
    ```bash
    git clone <项目地址>
    cd AutoCollect
    ```

2.  **安装Python依赖**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **安装Playwright浏览器依赖**:
    *这是Web自动化所必需的。*
    ```bash
    playwright install
    ```

4.  **配置Appium**:
    *这是App自动化所必需的。*
    确保Appium服务器正在运行，并且Android设备已正确连接。
    ```bash
    # (可选) 启动Appium服务器
    appium server
    ```

5.  **修改配置**:
    根据你的实际环境，编辑 `config.yaml` 文件，特别是设备ID、App包名、秒手账号、插件路径等。

6.  **启动Web服务**:
    ```bash
    python app.py
    ```

7.  **访问Web界面**:
    打开浏览器，访问 `http://localhost:8080`。

## 部署方式二：使用Docker

Docker部署提供了标准化的环境，主要用于隔离运行 **Web管理界面** 和 **Web自动化** 任务。我们提供两个独立的Dockerfile。

### 选项A: 部署纯Web界面 (`Dockerfile`)

此镜像仅包含Flask Web应用，体积较小。它本身无法执行自动化任务，但可以作为一个远程触发器（需要进行代码修改以支持远程执行）。

1.  **构建镜像**:
    ```bash
    docker build -t autocollect-ui -f Dockerfile .
    ```
2.  **运行容器**:
    ```bash
    docker run --rm -p 8080:8080 \
      -v "$(pwd)/shared_links:/app/shared_links" \
      -v "$(pwd)/uploads:/app/uploads" \
      -v "$(pwd)/config.yaml:/app/config.yaml" \
      autocollect-ui
    ```

### 选项B: 部署Web自动化服务 (`Dockerfile.playwright`)

此镜像包含Web界面、Playwright和Chromium浏览器，能够完整地在容器内执行Web自动化任务。

1.  **准备Chrome插件**:
    - 在项目根目录创建一个名为 `extensions` 的文件夹。
    - 将你解压后的Chrome插件完整地放入 `extensions` 文件夹中。
    - **这是构建镜像前的必需步骤。**

2.  **修改配置**:
    - 打开 `config.yaml`，找到 `web_automation` 部分。
    - 将 `extension_path` 修改为容器内的路径：`/app/extensions/`。

3.  **构建镜像**:
    ```bash
    docker build -t autocollect-playwright -f Dockerfile.playwright .
    ```

4.  **运行容器**:
    ```bash
    # --shm-size=1g: 推荐为Chromium设置，防止因内存不足而崩溃
    docker run --rm -it -p 8080:8080 \
      -v "$(pwd)/shared_links:/app/shared_links" \
      -v "$(pwd)/config.yaml:/app/config.yaml" \
      --shm-size=1g \
      autocollect-playwright
    ```
    *注意: 在Windows PowerShell中，请使用`${pwd}`代替`$(pwd)`。*

5.  **访问和使用**:
    - 打开浏览器访问 `http://localhost:8080`。
    - 在此容器中，只有 **Web自动化** (打开链接) 功能可以成功执行。App自动化任务会因缺少Appium环境而失败。


## 使用流程

1.  **访问主页**: 打开 `http://localhost:8080`。
2.  **上传图片**: (仅App自动化需要) 如果需要使用特定图片进行搜索，请将图片文件放入项目根目录下的 `uploads` 文件夹中。
3.  **配置参数**: 在Web界面上，根据需求填写或修改各项配置：
    - **APP自动化配置**: 设置设备版本、名称、TikTok包名等。
    - **APP自动化任务**: 设置本次任务要处理的商品数量和用于搜索的图片。
    - **Web自动化配置**: 设置代理服务器、秒手URL、用户名、密码和浏览器扩展路径。
4.  **启动App自动化任务**:
    - 在主页的“APP自动化任务”板块，选择一张图片。
    - 点击“开始任务”按钮，后台将开始执行TikTok图像搜索和链接采集。
    - 任务状态会实时显示在界面上，完成后可以点击“查看结果”或刷新主页查看采集到的链接文件。
5.  **启动Web自动化任务**:
    - 在主页的“已采集链接文件”列表中，会显示所有已生成的链接文件。
    - 点击任意文件旁的“在浏览器中打开”按钮。
    - 后台将启动一个Chrome浏览器，根据配置自动处理该文件中的所有链接。

## 配置项说明 (`config.yaml`)

```yaml
# Appium服务器地址
appium:
  server_url: http://127.0.0.1:4723

# 移动设备配置
device:
  platform_name: "Android"
  platform_version: "13"      # 你的安卓版本
  device_name: "Your_Device_ID" # adb devices获取到的设备ID
  automation_name: UiAutomator2
  no_reset: true

# App自动化任务配置
task:
  max_products_to_process: 5  # 每次任务最多采集的商品链接数
  pc_image_path: "uploads/your_image.jpg" # 用于图像搜索的图片路径（在Web界面选择会覆盖此项）
  share_target: file          # 结果处理方式，'file'表示保存到文件

# TikTok应用配置
tiktok:
  app_package: com.zhiliaoapp.musically
  app_activity: com.ss.android.ugc.aweme.splash.SplashActivity

# (可选) Web自动化配置
web_automation:
  proxy_server: "http://user:pass@host:port" # 代理服务器地址
  miaoshou_url: "https://www.miaoshou.com/login" # 秒手登录URL
  miaoshou_username: "your_username"
  miaoshou_password: "your_password"
  extension_path: "path/to/your/chrome_extension" # Chrome扩展程序路径
```

## 注意事项

- **路径问题**: 在配置文件和Web界面中填写路径时，请使用正斜杠 `/` 或双反斜杠 `\\`。
- **Appium会话**: 确保没有其他程序正在占用Appium服务。Web界面启动的任务是独占的，请等待一个任务完成后再启动下一个。
- **浏览器驱动**: Web自动化功能依赖于`webdriver-manager`自动下载匹配的ChromeDriver。如果自动下载失败，请手动安装与你的Chrome浏览器版本对应的ChromeDriver。
