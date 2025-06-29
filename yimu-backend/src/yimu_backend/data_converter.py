# -*- coding: utf-8 -*-
"""
数据转换模块
将一木记账的Excel文件转换为SQLite数据库
"""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, List, Tuple
from loguru import logger
import os
import re
from datetime import datetime


class YimuDataConverter:
    """一木记账数据转换器"""
    
    def __init__(self, db_path: str = "output/yimu_data.db", project_root: str = None):
        self.db_path = db_path
        self.project_root = project_root or os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.ensure_output_dir()
        
    def ensure_output_dir(self):
        """确保输出目录存在"""
        output_dir = Path(self.db_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
    def scan_bill_folders(self) -> List[Tuple[str, str, datetime]]:
        """扫描项目根目录下的账单文件夹
        
        Returns:
            List[Tuple[str, str, datetime]]: (文件夹名, Excel文件路径, 时间戳) 的列表
        """
        bill_folders = []
        project_path = Path(self.project_root)
        
        # 扫描符合 账单_{时间信息} 格式的文件夹
        pattern = re.compile(r'^账单_(\d{10})$')
        
        for item in project_path.iterdir():
            if item.is_dir():
                match = pattern.match(item.name)
                if match:
                    time_str = match.group(1)
                    # 查找文件夹内的Excel文件
                    excel_files = list(item.glob('*.xls')) + list(item.glob('*.xlsx'))
                    
                    if excel_files:
                        # 使用第一个找到的Excel文件
                        excel_path = str(excel_files[0])
                        # 解析时间戳（假设格式为MMDDHHMISS）
                        try:
                            # 尝试解析时间戳
                            if len(time_str) == 10:
                                month = int(time_str[:2])
                                day = int(time_str[2:4])
                                hour = int(time_str[4:6])
                                minute = int(time_str[6:8])
                                second = int(time_str[8:10])
                                # 假设是当前年份
                                current_year = datetime.now().year
                                timestamp = datetime(current_year, month, day, hour, minute, second)
                            else:
                                # 如果格式不匹配，使用文件夹的修改时间
                                timestamp = datetime.fromtimestamp(item.stat().st_mtime)
                        except (ValueError, OSError):
                            # 如果解析失败，使用文件夹的修改时间
                            timestamp = datetime.fromtimestamp(item.stat().st_mtime)
                        
                        bill_folders.append((item.name, excel_path, timestamp))
                        logger.info(f"发现账单文件夹: {item.name}, Excel文件: {excel_path}")
        
        # 按时间戳排序，最新的在前
        bill_folders.sort(key=lambda x: x[2], reverse=True)
        return bill_folders
    
    def get_latest_bill_file(self) -> Optional[str]:
        """获取最新的账单Excel文件路径
        
        Returns:
            Optional[str]: 最新账单文件路径，如果没有找到则返回None
        """
        bill_folders = self.scan_bill_folders()
        
        if bill_folders:
            latest_folder, latest_excel, timestamp = bill_folders[0]
            logger.info(f"使用最新账单文件: {latest_excel} (来自文件夹: {latest_folder})")
            return latest_excel
        
        # 如果没有找到账单文件夹，尝试从传统的data目录查找
        data_dir = Path(self.project_root) / "yimu-backend" / "data"
        if data_dir.exists():
            excel_files = list(data_dir.glob('*.xls')) + list(data_dir.glob('*.xlsx'))
            if excel_files:
                # 按修改时间排序，使用最新的
                excel_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                fallback_path = str(excel_files[0])
                logger.info(f"未找到账单文件夹，使用传统data目录中的文件: {fallback_path}")
                return fallback_path
        
        logger.warning("未找到任何账单文件")
        return None
        
    def create_database_schema(self):
        """创建数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建账单记录表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,                    -- 日期
            type TEXT NOT NULL,                    -- 收支类型
            amount REAL NOT NULL,                  -- 金额
            category TEXT,                         -- 类别
            subcategory TEXT,                      -- 二级分类
            account TEXT,                          -- 账户
            notebook TEXT,                         -- 账本
            refund TEXT,                           -- 退款
            discount TEXT,                         -- 优惠
            note TEXT,                             -- 备注
            tags TEXT,                             -- 标签
            reimburse_account TEXT,                -- 报销账户
            reimburse_amount TEXT,                 -- 报销金额
            reimburse_detail TEXT,                 -- 报销明细
            multi_currency TEXT,                   -- 多币种
            address TEXT,                          -- 地址
            creator TEXT,                          -- 创建用户
            other TEXT,                            -- 其他
            attachment1 TEXT,                      -- 附件1
            attachment2 TEXT,                      -- 附件2
            attachment3 TEXT,                      -- 附件3
            attachment4 TEXT,                      -- 附件4
            attachment5 TEXT,                      -- 附件5
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 创建索引以提高查询性能
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON transactions(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_type ON transactions(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON transactions(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_amount ON transactions(amount)")
        
        conn.commit()
        conn.close()
        logger.info(f"数据库表结构创建完成: {self.db_path}")
        
    def convert_excel_to_sqlite(self, excel_path: str = None) -> bool:
        """将Excel文件转换为SQLite数据库
        
        Args:
            excel_path: Excel文件路径，如果为None则自动检测最新的账单文件
            
        Returns:
            bool: 转换是否成功
        """
        try:
            # 如果没有指定文件路径，自动检测最新的账单文件
            if excel_path is None:
                excel_path = self.get_latest_bill_file()
                if excel_path is None:
                    logger.error("未找到任何可用的账单文件")
                    return False
            
            logger.info(f"开始转换Excel文件: {excel_path}")
            
            # 检查文件是否存在
            if not os.path.exists(excel_path):
                logger.error(f"Excel文件不存在: {excel_path}")
                return False
                
            # 读取Excel文件，自动检测文件格式
            try:
                # 先尝试使用openpyxl引擎（适用于.xlsx文件）
                df = pd.read_excel(excel_path, engine='openpyxl')
            except Exception as e:
                logger.warning(f"使用openpyxl引擎失败: {e}，尝试使用xlrd引擎")
                # 如果失败，尝试使用xlrd引擎（适用于.xls文件）
                df = pd.read_excel(excel_path, engine='xlrd')
            
            logger.info(f"成功读取Excel文件，共 {len(df)} 条记录")
            
            # 打印列名以便调试
            logger.info(f"Excel列名: {list(df.columns)}")
            
            # 创建数据库表结构
            self.create_database_schema()
            
            # 数据清洗和转换
            df_cleaned = self._clean_data(df)
            
            # 插入数据到SQLite
            conn = sqlite3.connect(self.db_path)
            
            # 定义列映射（Excel列名 -> 数据库列名）
            column_mapping = {
                '日期': 'date',
                '收支类型': 'type', 
                '金额': 'amount',
                '类别': 'category',
                '二级分类': 'subcategory',
                '账户': 'account',
                '账本': 'notebook',
                '退款': 'refund',
                '优惠': 'discount',
                '备注': 'note',
                '标签': 'tags',
                '报销账户': 'reimburse_account',
                '报销金额': 'reimburse_amount',
                '报销明细': 'reimburse_detail',
                '多币种': 'multi_currency',
                '地址': 'address',
                '创建用户': 'creator',
                '其他': 'other',
                '附件1': 'attachment1',
                '附件2': 'attachment2',
                '附件3': 'attachment3',
                '附件4': 'attachment4',
                '附件5': 'attachment5'
            }
            
            # 重命名列
            df_renamed = df_cleaned.rename(columns=column_mapping)
            
            # 只保留存在的列
            available_columns = [col for col in column_mapping.values() if col in df_renamed.columns]
            df_final = df_renamed[available_columns]
            
            # 插入数据
            df_final.to_sql('transactions', conn, if_exists='replace', index=False)
            
            conn.close()
            
            logger.info(f"数据转换完成，共插入 {len(df_final)} 条记录到数据库")
            return True
            
        except Exception as e:
            logger.error(f"转换Excel文件时发生错误: {str(e)}")
            return False
            
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """清洗数据
        
        Args:
            df: 原始数据框
            
        Returns:
            pd.DataFrame: 清洗后的数据框
        """
        df_cleaned = df.copy()
        
        # 处理日期列
        if '日期' in df_cleaned.columns:
            df_cleaned['日期'] = pd.to_datetime(df_cleaned['日期'], errors='coerce')
            df_cleaned['日期'] = df_cleaned['日期'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
        # 处理金额列
        if '金额' in df_cleaned.columns:
            df_cleaned['金额'] = pd.to_numeric(df_cleaned['金额'], errors='coerce')
            
        # 填充空值
        df_cleaned = df_cleaned.fillna('')
        
        # 移除完全空白的行
        df_cleaned = df_cleaned.dropna(how='all')
        
        logger.info(f"数据清洗完成，剩余 {len(df_cleaned)} 条有效记录")
        return df_cleaned
        
    def get_database_stats(self) -> dict:
        """获取数据库统计信息
        
        Returns:
            dict: 统计信息
        """
        if not os.path.exists(self.db_path):
            return {"error": "数据库文件不存在"}
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 总记录数
            cursor.execute("SELECT COUNT(*) FROM transactions")
            total_records = cursor.fetchone()[0]
            
            # 收支统计
            cursor.execute("SELECT type, COUNT(*), SUM(amount) FROM transactions GROUP BY type")
            type_stats = cursor.fetchall()
            
            # 日期范围
            cursor.execute("SELECT MIN(date), MAX(date) FROM transactions")
            date_range = cursor.fetchone()
            
            conn.close()
            
            return {
                "total_records": total_records,
                "type_statistics": type_stats,
                "date_range": date_range,
                "database_path": self.db_path
            }
            
        except Exception as e:
            logger.error(f"获取数据库统计信息时发生错误: {str(e)}")
            return {"error": str(e)}