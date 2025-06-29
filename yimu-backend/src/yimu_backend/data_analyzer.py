# -*- coding: utf-8 -*-
"""
数据分析模块
提供一木记账数据的各种统计分析功能
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from loguru import logger
import os
from collections import Counter


class YimuDataAnalyzer:
    """一木记账数据分析器"""
    
    def __init__(self, db_path: str = "output/yimu_data.db"):
        self.db_path = db_path
        
    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"数据库文件不存在: {self.db_path}")
        return sqlite3.connect(self.db_path)
        
    def get_monthly_trend(self, year: Optional[int] = None) -> Dict:
        """获取月度收支趋势
        
        Args:
            year: 指定年份，默认为当前年份
            
        Returns:
            Dict: 月度趋势数据
        """
        try:
            conn = self._get_connection()
            
            if year is None:
                year = datetime.now().year
                
            query = """
            SELECT 
                strftime('%m', date) as month,
                type,
                SUM(amount) as total_amount,
                COUNT(*) as transaction_count
            FROM transactions 
            WHERE strftime('%Y', date) = ?
            GROUP BY month, type
            ORDER BY month
            """
            
            df = pd.read_sql_query(query, conn, params=[str(year)])
            conn.close()
            
            # 重组数据
            result = {}
            for month in range(1, 13):
                month_str = f"{month:02d}"
                month_data = df[df['month'] == month_str]
                
                income = month_data[month_data['type'] == '收入']['total_amount'].sum()
                expense = abs(month_data[month_data['type'] == '支出']['total_amount'].sum())
                
                result[month_str] = {
                    'month': month_str,
                    'income': float(income) if income else 0.0,
                    'expense': float(expense) if expense else 0.0,
                    'net': float(income - expense) if (income or expense) else 0.0,
                    'transaction_count': int(month_data['transaction_count'].sum()) if not month_data.empty else 0
                }
                
            logger.info(f"获取{year}年月度趋势数据成功")
            return {
                'year': year,
                'monthly_data': result
            }
            
        except Exception as e:
            logger.error(f"获取月度趋势数据时发生错误: {str(e)}")
            raise
            
    def get_category_analysis(self, transaction_type: str = '支出', year: Optional[int] = None) -> Dict:
        """获取分类分析
        
        Args:
            transaction_type: 交易类型（收入/支出）
            year: 指定年份
            
        Returns:
            Dict: 分类分析数据
        """
        try:
            conn = self._get_connection()
            
            year_filter = ""
            params = [transaction_type]
            if year:
                year_filter = "AND strftime('%Y', date) = ?"
                params.append(str(year))
                
            query = f"""
            SELECT 
                category,
                subcategory,
                SUM(ABS(amount)) as total_amount,
                COUNT(*) as transaction_count,
                AVG(ABS(amount)) as avg_amount
            FROM transactions 
            WHERE type = ? {year_filter}
            GROUP BY category, subcategory
            ORDER BY total_amount DESC
            """
            
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            # 按主分类汇总
            category_summary = df.groupby('category').agg({
                'total_amount': 'sum',
                'transaction_count': 'sum',
                'avg_amount': 'mean'
            }).reset_index()
            
            category_summary = category_summary.sort_values('total_amount', ascending=False)
            
            # 计算百分比
            total_amount = category_summary['total_amount'].sum()
            category_summary['percentage'] = (category_summary['total_amount'] / total_amount * 100).round(2)
            
            result = {
                'transaction_type': transaction_type,
                'year': year,
                'total_amount': float(total_amount),
                'categories': [],
                'subcategories': []
            }
            
            # 主分类数据
            for _, row in category_summary.iterrows():
                result['categories'].append({
                    'category': row['category'],
                    'amount': float(row['total_amount']),
                    'count': int(row['transaction_count']),
                    'avg_amount': float(row['avg_amount']),
                    'percentage': float(row['percentage'])
                })
                
            # 子分类数据
            for _, row in df.iterrows():
                result['subcategories'].append({
                    'category': row['category'],
                    'subcategory': row['subcategory'],
                    'amount': float(row['total_amount']),
                    'count': int(row['transaction_count']),
                    'avg_amount': float(row['avg_amount'])
                })
                
            logger.info(f"获取{transaction_type}分类分析数据成功")
            return result
            
        except Exception as e:
            logger.error(f"获取分类分析数据时发生错误: {str(e)}")
            raise
            
    def get_account_analysis(self, year: Optional[int] = None) -> Dict:
        """获取账户使用分析
        
        Args:
            year: 指定年份
            
        Returns:
            Dict: 账户分析数据
        """
        try:
            conn = self._get_connection()
            
            year_filter = ""
            params = []
            if year:
                year_filter = "WHERE strftime('%Y', date) = ?"
                params.append(str(year))
                
            query = f"""
            SELECT 
                account,
                type,
                SUM(ABS(amount)) as total_amount,
                COUNT(*) as transaction_count
            FROM transactions 
            {year_filter}
            GROUP BY account, type
            ORDER BY total_amount DESC
            """
            
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            # 按账户汇总
            account_summary = df.groupby('account').agg({
                'total_amount': 'sum',
                'transaction_count': 'sum'
            }).reset_index()
            
            account_summary = account_summary.sort_values('total_amount', ascending=False)
            
            result = {
                'year': year,
                'accounts': [],
                'account_type_breakdown': []
            }
            
            # 账户汇总数据
            for _, row in account_summary.iterrows():
                result['accounts'].append({
                    'account': row['account'],
                    'total_amount': float(row['total_amount']),
                    'transaction_count': int(row['transaction_count'])
                })
                
            # 账户类型明细
            for _, row in df.iterrows():
                result['account_type_breakdown'].append({
                    'account': row['account'],
                    'type': row['type'],
                    'amount': float(row['total_amount']),
                    'count': int(row['transaction_count'])
                })
                
            logger.info(f"获取账户分析数据成功")
            return result
            
        except Exception as e:
            logger.error(f"获取账户分析数据时发生错误: {str(e)}")
            raise
            
    def get_location_analysis(self, year: Optional[int] = None, limit: int = 20) -> Dict:
        """获取消费地点分析
        
        Args:
            year: 指定年份
            limit: 返回记录数限制
            
        Returns:
            Dict: 地点分析数据
        """
        try:
            conn = self._get_connection()
            
            year_filter = ""
            params = []
            if year:
                year_filter = "AND strftime('%Y', date) = ?"
                params.append(str(year))
                
            query = f"""
            SELECT 
                address,
                SUM(ABS(amount)) as total_amount,
                COUNT(*) as transaction_count,
                AVG(ABS(amount)) as avg_amount
            FROM transactions 
            WHERE address != '' AND address IS NOT NULL {year_filter}
            GROUP BY address
            ORDER BY total_amount DESC
            LIMIT ?
            """
            
            params.append(limit)
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            result = {
                'year': year,
                'locations': []
            }
            
            for _, row in df.iterrows():
                result['locations'].append({
                    'address': row['address'],
                    'total_amount': float(row['total_amount']),
                    'transaction_count': int(row['transaction_count']),
                    'avg_amount': float(row['avg_amount'])
                })
                
            logger.info(f"获取地点分析数据成功")
            return result
            
        except Exception as e:
            logger.error(f"获取地点分析数据时发生错误: {str(e)}")
            raise
            
    def get_time_pattern_analysis(self, year: Optional[int] = None) -> Dict:
        """获取时间模式分析
        
        Args:
            year: 指定年份
            
        Returns:
            Dict: 时间模式分析数据
        """
        try:
            conn = self._get_connection()
            
            year_filter = ""
            params = []
            if year:
                year_filter = "WHERE strftime('%Y', date) = ?"
                params.append(str(year))
                
            # 按小时统计
            hour_query = f"""
            SELECT 
                strftime('%H', date) as hour,
                COUNT(*) as transaction_count,
                SUM(ABS(amount)) as total_amount
            FROM transactions 
            {year_filter}
            GROUP BY hour
            ORDER BY hour
            """
            
            # 按星期统计
            weekday_query = f"""
            SELECT 
                strftime('%w', date) as weekday,
                COUNT(*) as transaction_count,
                SUM(ABS(amount)) as total_amount
            FROM transactions 
            {year_filter}
            GROUP BY weekday
            ORDER BY weekday
            """
            
            hour_df = pd.read_sql_query(hour_query, conn, params=params)
            weekday_df = pd.read_sql_query(weekday_query, conn, params=params)
            conn.close()
            
            # 星期映射
            weekday_names = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
            
            result = {
                'year': year,
                'hourly_pattern': [],
                'weekday_pattern': []
            }
            
            # 小时模式
            for _, row in hour_df.iterrows():
                result['hourly_pattern'].append({
                    'hour': int(row['hour']),
                    'transaction_count': int(row['transaction_count']),
                    'total_amount': float(row['total_amount'])
                })
                
            # 星期模式
            for _, row in weekday_df.iterrows():
                weekday_idx = int(row['weekday'])
                result['weekday_pattern'].append({
                    'weekday': weekday_idx,
                    'weekday_name': weekday_names[weekday_idx],
                    'transaction_count': int(row['transaction_count']),
                    'total_amount': float(row['total_amount'])
                })
                
            logger.info(f"获取时间模式分析数据成功")
            return result
            
        except Exception as e:
            logger.error(f"获取时间模式分析数据时发生错误: {str(e)}")
            raise
            
    def get_financial_overview(self, year: Optional[int] = None) -> Dict:
        """获取年度财务总览
        
        Args:
            year: 指定年份
            
        Returns:
            Dict: 年度财务总览数据
        """
        try:
            conn = self._get_connection()
            
            if year is None:
                year = datetime.now().year
                
            year_filter = "WHERE strftime('%Y', date) = ?"
            params = [str(year)]
            
            # 获取年度收入总额
            income_query = f"""
            SELECT SUM(amount) as total_income, COUNT(*) as income_count
            FROM transactions 
            {year_filter} AND type = '收入'
            """
            
            # 获取年度支出总额
            expense_query = f"""
            SELECT SUM(ABS(amount)) as total_expense, COUNT(*) as expense_count
            FROM transactions 
            {year_filter} AND type = '支出'
            """
            
            # 获取最大单笔收入详情（包含备注）
            max_income_query = f"""
            SELECT amount as max_income, category, subcategory, date, note, account
            FROM transactions 
            {year_filter} AND type = '收入'
            ORDER BY amount DESC
            LIMIT 1
            """
            
            # 获取最大单笔支出详情（包含备注）
            max_expense_query = f"""
            SELECT ABS(amount) as max_expense, category, subcategory, date, note, account
            FROM transactions 
            {year_filter} AND type = '支出'
            ORDER BY ABS(amount) DESC
            LIMIT 1
            """
            
            # 获取总交易笔数
            total_transactions_query = f"""
            SELECT COUNT(*) as total_transactions
            FROM transactions 
            {year_filter}
            """
            
            # 获取账户使用情况
            account_usage_query = f"""
            SELECT account, COUNT(*) as usage_count
            FROM transactions 
            {year_filter}
            GROUP BY account
            ORDER BY usage_count DESC
            """
            
            # 获取地点消费统计（支出）
            location_stats_query = f"""
            SELECT address, COUNT(*) as location_count
            FROM transactions 
            {year_filter} AND type = '支出' AND address IS NOT NULL AND address != ''
            GROUP BY address
            ORDER BY location_count DESC
            LIMIT 5
            """
            
            # 获取分类支出统计（一级分类）
            category_expense_query = f"""
            SELECT category, SUM(ABS(amount)) as category_expense
            FROM transactions 
            {year_filter} AND type = '支出'
            GROUP BY category
            ORDER BY category_expense DESC
            """
            
            # 获取最常购买物品（通过备注统计）
            frequent_items_query = f"""
            SELECT note, COUNT(*) as note_count
            FROM transactions 
            {year_filter} AND type = '支出' AND note IS NOT NULL AND note != ''
            GROUP BY note
            ORDER BY note_count DESC
            LIMIT 1
            """
            
            # 获取收入来源分析（备注 > 二级分类 > 一级分类）
            income_source_query = f"""
            SELECT 
                CASE 
                    WHEN note IS NOT NULL AND note != '' THEN note
                    WHEN subcategory IS NOT NULL AND subcategory != '' THEN subcategory  
                    ELSE category
                END as income_source,
                SUM(amount) as total_amount,
                COUNT(*) as transaction_count
            FROM transactions 
            {year_filter} AND type = '收入'
            GROUP BY income_source
            ORDER BY total_amount DESC
            LIMIT 1
            """
            
            # 执行查询
            income_result = pd.read_sql_query(income_query, conn, params=params)
            expense_result = pd.read_sql_query(expense_query, conn, params=params)
            max_income_result = pd.read_sql_query(max_income_query, conn, params=params)
            max_expense_result = pd.read_sql_query(max_expense_query, conn, params=params)
            total_transactions_result = pd.read_sql_query(total_transactions_query, conn, params=params)
            account_usage_result = pd.read_sql_query(account_usage_query, conn, params=params)
            location_stats_result = pd.read_sql_query(location_stats_query, conn, params=params)
            category_expense_result = pd.read_sql_query(category_expense_query, conn, params=params)
            frequent_items_result = pd.read_sql_query(frequent_items_query, conn, params=params)
            income_source_result = pd.read_sql_query(income_source_query, conn, params=params)
            
            conn.close()
            
            # 提取基础数据
            total_income = float(income_result.iloc[0]['total_income'] or 0)
            income_count = int(income_result.iloc[0]['income_count'] or 0)
            
            total_expense = float(expense_result.iloc[0]['total_expense'] or 0)
            expense_count = int(expense_result.iloc[0]['expense_count'] or 0)
            
            total_transactions = int(total_transactions_result.iloc[0]['total_transactions'] or 0)
            
            # 提取最高收入详情
            max_income_data = {
                'amount': float(max_income_result.iloc[0]['max_income'] or 0),
                'category': max_income_result.iloc[0]['category'] or '',
                'subcategory': max_income_result.iloc[0]['subcategory'] or '',
                'date': max_income_result.iloc[0]['date'] or '',
                'note': max_income_result.iloc[0]['note'] or '',
                'account': max_income_result.iloc[0]['account'] or ''
            } if not max_income_result.empty else {'amount': 0, 'category': '', 'subcategory': '', 'date': '', 'note': '', 'account': ''}
            
            # 提取最高支出详情
            max_expense_data = {
                'amount': float(max_expense_result.iloc[0]['max_expense'] or 0),
                'category': max_expense_result.iloc[0]['category'] or '',
                'subcategory': max_expense_result.iloc[0]['subcategory'] or '',
                'date': max_expense_result.iloc[0]['date'] or '',
                'note': max_expense_result.iloc[0]['note'] or '',
                'account': max_expense_result.iloc[0]['account'] or ''
            } if not max_expense_result.empty else {'amount': 0, 'category': '', 'subcategory': '', 'date': '', 'note': '', 'account': ''}
            
            # 提取账户使用情况
            account_usage = []
            total_account_usage = account_usage_result['usage_count'].sum() if not account_usage_result.empty else 0
            for _, row in account_usage_result.iterrows():
                account_usage.append({
                    'account': row['account'],
                    'usage_count': int(row['usage_count']),
                    'percentage': round(row['usage_count'] / total_account_usage * 100, 2) if total_account_usage > 0 else 0
                })
            
            # 提取地点消费统计
            location_stats = []
            total_location_count = location_stats_result['location_count'].sum() if not location_stats_result.empty else 0
            for _, row in location_stats_result.iterrows():
                location_stats.append({
                    'location': row['address'],
                    'count': int(row['location_count']),
                    'percentage': round(row['location_count'] / total_location_count * 100, 2) if total_location_count > 0 else 0
                })
            
            # 提取分类支出统计
            category_expenses = []
            for _, row in category_expense_result.iterrows():
                category_expenses.append({
                    'category': row['category'],
                    'expense': float(row['category_expense'])
                })
            
            # 提取最常购买物品
            most_frequent_item = {
                'note': frequent_items_result.iloc[0]['note'] if not frequent_items_result.empty else '',
                'count': int(frequent_items_result.iloc[0]['note_count']) if not frequent_items_result.empty else 0
            }
            
            # 提取主要收入来源
            main_income_source = {
                'source': income_source_result.iloc[0]['income_source'] if not income_source_result.empty else '',
                'amount': float(income_source_result.iloc[0]['total_amount']) if not income_source_result.empty else 0,
                'count': int(income_source_result.iloc[0]['transaction_count']) if not income_source_result.empty else 0,
                'percentage': round(float(income_source_result.iloc[0]['total_amount']) / total_income * 100, 2) if not income_source_result.empty and total_income > 0 else 0
            }
            
            # 计算衍生指标
            net_savings = total_income - total_expense
            savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0
            avg_monthly_income = total_income / 12
            avg_monthly_expense = total_expense / 12
            avg_daily_expense = total_expense / 365 if total_expense > 0 else 0
            
            # 简化的资产负债数据（基于账户余额概念）
            # 注：这里假设正余额为资产，负余额为负债
            total_assets = total_income  # 简化处理
            total_liabilities = 0  # 简化处理，实际应根据具体业务逻辑
            net_assets = total_assets - total_liabilities
            
            result = {
                'year': year,
                'annual_total_income': total_income,
                'annual_total_expense': total_expense,
                'annual_net_savings': net_savings,
                'annual_savings_rate': round(savings_rate, 2),
                'year_end_total_assets': total_assets,
                'year_end_total_liabilities': total_liabilities,
                'year_end_net_assets': net_assets,
                'avg_monthly_income': round(avg_monthly_income, 2),
                'avg_monthly_expense': round(avg_monthly_expense, 2),
                'avg_daily_expense': round(avg_daily_expense, 2),
                'annual_total_transactions': total_transactions,
                'max_single_income_data': max_income_data,
                'max_single_expense_data': max_expense_data,
                'income_transaction_count': income_count,
                'expense_transaction_count': expense_count,
                'account_usage': account_usage,
                'location_stats': location_stats,
                'category_expenses': category_expenses,
                'most_frequent_item': most_frequent_item,
                'main_income_source': main_income_source,
                # 保持向后兼容
                'max_single_income': max_income_data['amount'],
                'max_single_expense': max_expense_data['amount']
            }
            
            logger.info(f"获取{year}年度财务总览数据成功")
            return result
            
        except Exception as e:
            logger.error(f"获取年度财务总览数据时发生错误: {str(e)}")
            raise
    
    def get_annual_summary(self, year: Optional[int] = None) -> Dict:
        """获取年度总结
        
        Args:
            year: 指定年份
            
        Returns:
            Dict: 年度总结数据
        """
        try:
            if year is None:
                year = datetime.now().year
                
            # 获取各项分析数据
            financial_overview = self.get_financial_overview(year)
            monthly_trend = self.get_monthly_trend(year)
            expense_categories = self.get_category_analysis('支出', year)
            income_categories = self.get_category_analysis('收入', year)
            account_analysis = self.get_account_analysis(year)
            location_analysis = self.get_location_analysis(year, 10)
            time_pattern = self.get_time_pattern_analysis(year)
            
            # 计算总体统计
            total_income = sum([month['income'] for month in monthly_trend['monthly_data'].values()])
            total_expense = sum([month['expense'] for month in monthly_trend['monthly_data'].values()])
            total_transactions = sum([month['transaction_count'] for month in monthly_trend['monthly_data'].values()])
            
            # 最高支出月份
            max_expense_month = max(monthly_trend['monthly_data'].items(), key=lambda x: x[1]['expense'])
            
            # 最高收入月份
            max_income_month = max(monthly_trend['monthly_data'].items(), key=lambda x: x[1]['income'])
            
            result = {
                'year': year,
                'financial_overview': financial_overview,
                'overview': {
                    'total_income': total_income,
                    'total_expense': total_expense,
                    'net_income': total_income - total_expense,
                    'total_transactions': total_transactions,
                    'avg_monthly_expense': total_expense / 12,
                    'avg_monthly_income': total_income / 12,
                    'max_expense_month': {
                        'month': max_expense_month[0],
                        'amount': max_expense_month[1]['expense']
                    },
                    'max_income_month': {
                        'month': max_income_month[0],
                        'amount': max_income_month[1]['income']
                    }
                },
                'monthly_trend': monthly_trend,
                'expense_categories': expense_categories,
                'income_categories': income_categories,
                'account_analysis': account_analysis,
                'location_analysis': location_analysis,
                'time_pattern': time_pattern
            }
            
            logger.info(f"获取{year}年度总结数据成功")
            return result
            
        except Exception as e:
            logger.error(f"获取年度总结数据时发生错误: {str(e)}")
            raise
    
    def get_daily_data(self, year: Optional[int] = None) -> Dict:
        """获取每日收支数据，用于热力图显示
        
        Args:
            year: 指定年份，默认为当前年份
            
        Returns:
            Dict: 每日数据
        """
        try:
            conn = self._get_connection()
            
            if year is None:
                year = datetime.now().year
                
            query = """
            SELECT 
                DATE(date) as date,
                type,
                SUM(amount) as total_amount,
                COUNT(*) as transaction_count
            FROM transactions 
            WHERE strftime('%Y', date) = ?
            GROUP BY DATE(date), type
            ORDER BY DATE(date)
            """
            
            params = (str(year),)
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            # 处理数据，按日期组织
            daily_data = {}
            
            for _, row in df.iterrows():
                date_str = row['date']
                transaction_type = row['type']
                amount = float(row['total_amount'])
                count = int(row['transaction_count'])
                
                if date_str not in daily_data:
                    daily_data[date_str] = {
                        'date': date_str,
                        'income': 0,
                        'expense': 0,
                        'income_count': 0,
                        'expense_count': 0
                    }
                
                if transaction_type == '收入':
                    daily_data[date_str]['income'] = amount
                    daily_data[date_str]['income_count'] = count
                elif transaction_type == '支出':
                    # 支出金额取绝对值，确保为正数
                    daily_data[date_str]['expense'] = abs(amount)
                    daily_data[date_str]['expense_count'] = count
            
            # 转换为列表格式
            result = {
                'year': year,
                'daily_data': list(daily_data.values())
            }
            
            logger.info(f"获取{year}年每日数据成功，共{len(daily_data)}天有交易记录")
            return result
            
        except Exception as e:
            logger.error(f"获取每日数据时发生错误: {str(e)}")
            raise