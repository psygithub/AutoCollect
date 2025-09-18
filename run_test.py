#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TikTok商城自动化测试运行脚本
"""

import os
import sys
import subprocess
from loguru import logger


def setup_logging():
    """设置日志"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    logger.add(
        "logs/test_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="1 day",
        retention="7 days"
    )


def check_appium_server():
    """检查Appium服务器是否运行"""
    try:
        import requests
        response = requests.get("http://localhost:4723/status", timeout=5)
        if response.status_code == 200:
            logger.info("Appium服务器运行正常")
            return True
        else:
            logger.error("Appium服务器响应异常")
            return False
    except Exception as e:
        logger.error(f"无法连接到Appium服务器: {e}")
        logger.info("请确保Appium服务器已启动: appium server")
        return False


def install_dependencies():
    """安装依赖"""
    try:
        logger.info("检查并安装依赖...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        logger.info("依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"依赖安装失败: {e}")
        return False


def run_tests():
    """运行测试"""
    try:
        logger.info("开始运行自动化测试...")
        
        # 创建必要的目录
        os.makedirs("logs", exist_ok=True)
        os.makedirs("screenshots", exist_ok=True)
        os.makedirs("reports", exist_ok=True)
        
        # 运行pytest
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/test_tiktok_shop_automation.py",
            "-v", "-s",
            "--tb=short",
            "--alluredir=reports/allure-results"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("测试执行成功")
            logger.info(result.stdout)
        else:
            logger.error("测试执行失败")
            logger.error(result.stderr)
            
        return result.returncode == 0
        
    except Exception as e:
        logger.error(f"运行测试失败: {e}")
        return False


def main():
    """主函数"""
    setup_logging()
    
    logger.info("=== TikTok商城自动化测试启动 ===")
    
    # 1. 安装依赖
    if not install_dependencies():
        logger.error("依赖安装失败，退出")
        return 1
    
    # 2. 检查Appium服务器
    if not check_appium_server():
        logger.error("Appium服务器未运行，请先启动Appium服务器")
        logger.info("启动命令: appium server")
        return 1
    
    # 3. 运行测试
    if run_tests():
        logger.info("=== 测试执行完成 ===")
        return 0
    else:
        logger.error("=== 测试执行失败 ===")
        return 1


if __name__ == "__main__":
    sys.exit(main())
