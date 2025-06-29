#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动转换Excel文件脚本
"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from yimu_backend.data_converter import YimuDataConverter
from loguru import logger

def main():
    """主函数"""
    try:
        # 初始化转换器
        converter = YimuDataConverter()
        
        # Excel文件路径
        excel_path = "data/账单_0621185011.xls"
        
        if not os.path.exists(excel_path):
            logger.error(f"Excel文件不存在: {excel_path}")
            return False
            
        logger.info(f"开始转换Excel文件: {excel_path}")
        
        # 执行转换
        success = converter.convert_excel_to_sqlite(excel_path)
        
        if success:
            logger.info("Excel文件转换成功!")
            
            # 获取数据库统计信息
            stats = converter.get_database_stats()
            logger.info(f"数据库统计信息: {stats}")
            
            return True
        else:
            logger.error("Excel文件转换失败")
            return False
            
    except Exception as e:
        logger.error(f"转换过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("转换成功!")
    else:
        print("转换失败!")
        sys.exit(1)