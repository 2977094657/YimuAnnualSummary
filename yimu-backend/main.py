# -*- coding: utf-8 -*-
"""
一木记账年度总结分析工具 - 主入口文件
"""

from src.yimu_backend.api import app
from src.yimu_backend.data_converter import YimuDataConverter
from loguru import logger
import os
from pathlib import Path

# 配置日志
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logger.add(
    "logs/yimu_main.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

def initialize_app():
    """初始化应用"""
    logger.info("正在初始化一木记账年度总结分析工具...")
    
    # 创建必要的目录
    directories = ["data", "output", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"确保目录存在: {directory}")
    
    # 检查是否有Excel文件需要自动转换
    data_dir = Path("data")
    excel_files = list(data_dir.glob("*.xls")) + list(data_dir.glob("*.xlsx"))
    
    if excel_files:
        logger.info(f"发现 {len(excel_files)} 个Excel文件，准备自动转换")
        converter = YimuDataConverter()
        
        for excel_file in excel_files:
            logger.info(f"正在转换文件: {excel_file}")
            success = converter.convert_excel_to_sqlite(str(excel_file))
            if success:
                logger.info(f"文件转换成功: {excel_file}")
            else:
                logger.error(f"文件转换失败: {excel_file}")
    else:
        logger.info("未发现Excel文件，跳过自动转换")
    
    logger.info("应用初始化完成")

if __name__ == "__main__":
    # 初始化应用
    initialize_app()
    
    # 启动FastAPI应用
    import uvicorn
    logger.info("正在启动FastAPI服务器...")
    logger.info("API文档地址: http://localhost:8000/docs")
    logger.info("API接口地址: http://localhost:8000/api/")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
