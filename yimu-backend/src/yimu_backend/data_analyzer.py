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
            
            # 获取新的分析维度数据
            time_analysis = self.get_time_consumption_analysis(year)
            behavior_analysis = self.get_consumption_behavior_analysis(year)
            growth_analysis = self.get_financial_growth_analysis(year)
            events_analysis = self.get_special_events_analysis(year)

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
                # 新增的分析维度
                'time_analysis': time_analysis,
                'behavior_analysis': behavior_analysis,
                'growth_analysis': growth_analysis,
                'events_analysis': events_analysis,
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
    
    def get_time_consumption_analysis(self, year: Optional[int] = None) -> Dict:
        """获取时间维度消费分析

        Args:
            year: 指定年份，默认为当前年份

        Returns:
            Dict: 时间维度分析数据
        """
        try:
            conn = self._get_connection()

            if year is None:
                year = datetime.now().year

            year_filter = "WHERE strftime('%Y', date) = ?"
            params = [str(year)]

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

            # 按月份前中后期统计
            month_period_query = f"""
            SELECT
                CASE
                    WHEN CAST(strftime('%d', date) AS INTEGER) <= 10 THEN '月初'
                    WHEN CAST(strftime('%d', date) AS INTEGER) <= 20 THEN '月中'
                    ELSE '月末'
                END as period,
                COUNT(*) as transaction_count,
                SUM(ABS(amount)) as total_amount
            FROM transactions
            {year_filter}
            GROUP BY period
            """

            # 按季节统计
            season_query = f"""
            SELECT
                CASE
                    WHEN CAST(strftime('%m', date) AS INTEGER) IN (3,4,5) THEN '春天'
                    WHEN CAST(strftime('%m', date) AS INTEGER) IN (6,7,8) THEN '夏天'
                    WHEN CAST(strftime('%m', date) AS INTEGER) IN (9,10,11) THEN '秋天'
                    ELSE '冬天'
                END as season,
                COUNT(*) as transaction_count,
                SUM(ABS(amount)) as total_amount
            FROM transactions
            {year_filter}
            GROUP BY season
            """

            hour_df = pd.read_sql_query(hour_query, conn, params=params)
            weekday_df = pd.read_sql_query(weekday_query, conn, params=params)
            month_period_df = pd.read_sql_query(month_period_query, conn, params=params)
            season_df = pd.read_sql_query(season_query, conn, params=params)
            conn.close()

            # 处理小时数据，找出消费高峰时间
            peak_hours = hour_df.nlargest(3, 'total_amount')
            peak_hour = peak_hours.iloc[0] if not peak_hours.empty else None

            # 处理星期数据
            weekday_names = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
            peak_weekday = weekday_df.nlargest(1, 'total_amount').iloc[0] if not weekday_df.empty else None

            # 处理月份周期数据
            peak_period = month_period_df.nlargest(1, 'total_amount').iloc[0] if not month_period_df.empty else None

            # 处理季节数据
            peak_season = season_df.nlargest(1, 'total_amount').iloc[0] if not season_df.empty else None

            result = {
                'year': year,
                'peak_hour': {
                    'hour': int(peak_hour['hour']) if peak_hour is not None else None,
                    'amount': float(peak_hour['total_amount']) if peak_hour is not None else 0,
                    'count': int(peak_hour['transaction_count']) if peak_hour is not None else 0
                },
                'peak_weekday': {
                    'weekday': weekday_names[int(peak_weekday['weekday'])] if peak_weekday is not None else None,
                    'amount': float(peak_weekday['total_amount']) if peak_weekday is not None else 0,
                    'count': int(peak_weekday['transaction_count']) if peak_weekday is not None else 0
                },
                'peak_period': {
                    'period': peak_period['period'] if peak_period is not None else None,
                    'amount': float(peak_period['total_amount']) if peak_period is not None else 0,
                    'count': int(peak_period['transaction_count']) if peak_period is not None else 0
                },
                'peak_season': {
                    'season': peak_season['season'] if peak_season is not None else None,
                    'amount': float(peak_season['total_amount']) if peak_season is not None else 0,
                    'count': int(peak_season['transaction_count']) if peak_season is not None else 0
                }
            }

            logger.info(f"获取{year}年时间维度消费分析数据成功")
            return result

        except Exception as e:
            logger.error(f"获取时间维度消费分析数据时发生错误: {str(e)}")
            raise

    def get_consumption_behavior_analysis(self, year: Optional[int] = None) -> Dict:
        """获取消费行为模式分析

        Args:
            year: 指定年份，默认为当前年份

        Returns:
            Dict: 消费行为分析数据
        """
        try:
            conn = self._get_connection()

            if year is None:
                year = datetime.now().year

            year_filter = "WHERE strftime('%Y', date) = ?"
            params = [str(year)]

            # 获取所有支出交易
            expense_query = f"""
            SELECT
                DATE(date) as date,
                ABS(amount) as amount,
                COUNT(*) as daily_count
            FROM transactions
            {year_filter} AND type = '支出'
            GROUP BY DATE(date)
            ORDER BY date
            """

            expense_df = pd.read_sql_query(expense_query, conn, params=params)

            if expense_df.empty:
                conn.close()
                return {
                    'year': year,
                    'consumption_type': '暂无数据',
                    'impulse_days': 0,
                    'stability_score': 0,
                    'max_consecutive_days': 0
                }

            # 分析消费频率和金额模式
            total_amount = expense_df['amount'].sum()
            total_transactions = expense_df['daily_count'].sum()
            avg_transaction = total_amount / total_transactions if total_transactions > 0 else 0

            # 小额高频 vs 大额低频分析
            small_amount_threshold = avg_transaction * 0.5
            large_amount_threshold = avg_transaction * 2

            small_transactions = expense_df[expense_df['amount'] <= small_amount_threshold]['daily_count'].sum()
            large_transactions = expense_df[expense_df['amount'] >= large_amount_threshold]['daily_count'].sum()

            # 判断消费类型
            if small_transactions > large_transactions * 2:
                consumption_type = "小确幸收集者"
                type_description = f"{int(small_transactions/total_transactions*100)}%的消费都是小额快乐"
            elif large_transactions > small_transactions:
                consumption_type = "品质生活家"
                type_description = f"偏爱大额消费，追求品质生活"
            else:
                consumption_type = "均衡消费者"
                type_description = f"大小额消费比较均衡"

            # 冲动消费检测（单日多笔交易）
            impulse_days = len(expense_df[expense_df['daily_count'] >= 3])
            max_daily_transactions = expense_df['daily_count'].max()
            max_impulse_day = expense_df[expense_df['daily_count'] == max_daily_transactions].iloc[0] if max_daily_transactions > 1 else None

            # 消费稳定性分析（月度支出标准差）
            expense_df['month'] = pd.to_datetime(expense_df['date']).dt.to_period('M')
            monthly_expense = expense_df.groupby('month')['amount'].sum()
            stability_score = 100 - min(100, (monthly_expense.std() / monthly_expense.mean() * 100)) if len(monthly_expense) > 1 else 100

            # 连续消费天数分析
            expense_df['date_dt'] = pd.to_datetime(expense_df['date'])
            expense_df = expense_df.sort_values('date_dt')

            consecutive_days = 1
            max_consecutive_days = 1

            for i in range(1, len(expense_df)):
                if (expense_df.iloc[i]['date_dt'] - expense_df.iloc[i-1]['date_dt']).days == 1:
                    consecutive_days += 1
                    max_consecutive_days = max(max_consecutive_days, consecutive_days)
                else:
                    consecutive_days = 1

            conn.close()

            result = {
                'year': year,
                'consumption_type': consumption_type,
                'type_description': type_description,
                'impulse_days': int(impulse_days),
                'max_daily_transactions': int(max_daily_transactions),
                'max_impulse_day': {
                    'date': max_impulse_day['date'] if max_impulse_day is not None else None,
                    'count': int(max_impulse_day['daily_count']) if max_impulse_day is not None else 0,
                    'amount': float(max_impulse_day['amount']) if max_impulse_day is not None else 0
                },
                'stability_score': round(stability_score, 1),
                'max_consecutive_days': int(max_consecutive_days),
                'avg_transaction_amount': round(avg_transaction, 2)
            }

            logger.info(f"获取{year}年消费行为分析数据成功")
            return result

        except Exception as e:
            logger.error(f"获取消费行为分析数据时发生错误: {str(e)}")
            raise

    def get_financial_growth_analysis(self, year: Optional[int] = None) -> Dict:
        """获取财务成长轨迹分析

        Args:
            year: 指定年份，默认为当前年份

        Returns:
            Dict: 财务成长分析数据
        """
        try:
            conn = self._get_connection()

            if year is None:
                year = datetime.now().year

            year_filter = "WHERE strftime('%Y', date) = ?"
            params = [str(year)]

            # 按月统计收支
            monthly_query = f"""
            SELECT
                strftime('%m', date) as month,
                type,
                SUM(amount) as total_amount,
                COUNT(*) as transaction_count,
                AVG(ABS(amount)) as avg_amount
            FROM transactions
            {year_filter}
            GROUP BY month, type
            ORDER BY month
            """

            monthly_df = pd.read_sql_query(monthly_query, conn, params=params)
            conn.close()

            if monthly_df.empty:
                return {
                    'year': year,
                    'peak_income_month': None,
                    'peak_expense_month': None,
                    'savings_trend': '暂无数据',
                    'consumption_upgrade': '暂无数据'
                }

            # 分离收入和支出数据
            income_df = monthly_df[monthly_df['type'] == '收入'].copy()
            expense_df = monthly_df[monthly_df['type'] == '支出'].copy()

            # 找出收入和支出峰值月份
            peak_income_month = None
            peak_expense_month = None

            if not income_df.empty:
                peak_income = income_df.loc[income_df['total_amount'].idxmax()]
                peak_income_month = {
                    'month': int(peak_income['month']),
                    'amount': float(peak_income['total_amount']),
                    'count': int(peak_income['transaction_count'])
                }

            if not expense_df.empty:
                expense_df['abs_amount'] = expense_df['total_amount'].abs()
                peak_expense = expense_df.loc[expense_df['abs_amount'].idxmax()]
                peak_expense_month = {
                    'month': int(peak_expense['month']),
                    'amount': float(peak_expense['abs_amount']),
                    'count': int(peak_expense['transaction_count'])
                }

            # 储蓄率趋势分析
            monthly_summary = []
            for month in range(1, 13):
                month_str = f"{month:02d}"
                month_income = income_df[income_df['month'] == month_str]['total_amount'].sum()
                month_expense = expense_df[expense_df['month'] == month_str]['total_amount'].abs().sum()
                month_savings = month_income - month_expense
                savings_rate = (month_savings / month_income * 100) if month_income > 0 else 0

                monthly_summary.append({
                    'month': month,
                    'income': month_income,
                    'expense': month_expense,
                    'savings': month_savings,
                    'savings_rate': savings_rate
                })

            # 计算储蓄率趋势
            valid_months = [m for m in monthly_summary if m['income'] > 0]
            if len(valid_months) >= 2:
                first_half_rate = sum(m['savings_rate'] for m in valid_months[:len(valid_months)//2]) / (len(valid_months)//2)
                second_half_rate = sum(m['savings_rate'] for m in valid_months[len(valid_months)//2:]) / (len(valid_months) - len(valid_months)//2)

                if second_half_rate > first_half_rate + 5:
                    savings_trend = f"储蓄能力在进步，从{first_half_rate:.1f}%涨到{second_half_rate:.1f}%"
                elif first_half_rate > second_half_rate + 5:
                    savings_trend = f"储蓄率有所下降，从{first_half_rate:.1f}%降到{second_half_rate:.1f}%"
                else:
                    savings_trend = f"储蓄率比较稳定，保持在{(first_half_rate + second_half_rate)/2:.1f}%左右"
            else:
                savings_trend = "数据不足，无法分析趋势"

            # 消费升级分析
            if not expense_df.empty and len(expense_df) >= 2:
                first_half_avg = expense_df[:len(expense_df)//2]['avg_amount'].mean()
                second_half_avg = expense_df[len(expense_df)//2:]['avg_amount'].mean()

                if second_half_avg > first_half_avg * 1.2:
                    consumption_upgrade = f"消费在升级，平均单笔从¥{first_half_avg:.0f}涨到¥{second_half_avg:.0f} <img src=\"/CuteEmoji/🆙_AgADbUkAAuaZWEs.webp\" alt=\"🆙\" style=\"width: 14px; height: 14px; display: inline-block; margin-left: 4px; vertical-align: middle;\" />"
                elif first_half_avg > second_half_avg * 1.2:
                    consumption_upgrade = f"消费更理性了，平均单笔从¥{first_half_avg:.0f}降到¥{second_half_avg:.0f} <img src=\"/CuteEmoji/👍_AgAD3kUAAksEWUs.webp\" alt=\"👍\" style=\"width: 14px; height: 14px; display: inline-block; margin-left: 4px; vertical-align: middle;\" />"
                else:
                    consumption_upgrade = f"消费水平比较稳定，平均单笔¥{(first_half_avg + second_half_avg)/2:.0f}左右 <img src=\"/CuteEmoji/😌_AgADA0cAAgG0WUs.webp\" alt=\"😌\" style=\"width: 14px; height: 14px; display: inline-block; margin-left: 4px; vertical-align: middle;\" />"
            else:
                consumption_upgrade = "数据不足，无法分析消费变化"

            result = {
                'year': year,
                'peak_income_month': peak_income_month,
                'peak_expense_month': peak_expense_month,
                'savings_trend': savings_trend,
                'consumption_upgrade': consumption_upgrade,
                'monthly_summary': monthly_summary
            }

            logger.info(f"获取{year}年财务成长分析数据成功")
            return result

        except Exception as e:
            logger.error(f"获取财务成长分析数据时发生错误: {str(e)}")
            raise

    def get_special_events_analysis(self, year: Optional[int] = None) -> Dict:
        """获取特殊事件与纪念时刻分析

        Args:
            year: 指定年份，默认为当前年份

        Returns:
            Dict: 特殊事件分析数据
        """
        try:
            conn = self._get_connection()

            if year is None:
                year = datetime.now().year

            year_filter = "WHERE strftime('%Y', date) = ?"
            params = [str(year)]

            # 获取每日支出数据
            daily_expense_query = f"""
            SELECT
                DATE(date) as date,
                SUM(ABS(amount)) as daily_expense,
                COUNT(*) as transaction_count
            FROM transactions
            {year_filter} AND type = '支出'
            GROUP BY DATE(date)
            ORDER BY daily_expense DESC
            """

            daily_df = pd.read_sql_query(daily_expense_query, conn, params=params)

            # 周末vs工作日分析
            weekend_workday_query = f"""
            SELECT
                CASE
                    WHEN strftime('%w', date) IN ('0', '6') THEN '周末'
                    ELSE '工作日'
                END as day_type,
                AVG(ABS(amount)) as avg_amount,
                COUNT(*) as transaction_count,
                SUM(ABS(amount)) as total_amount
            FROM transactions
            {year_filter} AND type = '支出'
            GROUP BY day_type
            """

            weekend_df = pd.read_sql_query(weekend_workday_query, conn, params=params)
            conn.close()

            # 特殊日期定义 - 包含传统节日、现代节日、网络节日
            special_dates = {
                # 传统节日
                f'{year}-01-01': '元旦',
                f'{year}-05-01': '劳动节',
                f'{year}-10-01': '国庆节',
                f'{year}-12-25': '圣诞节',

                # 情侣节日
                f'{year}-02-14': '情人节',
                f'{year}-03-14': '白色情人节',
                f'{year}-05-20': '520网络情人节',
                f'{year}-05-21': '521网络情人节',
                f'{year}-08-07': '七夕节',  # 农历七月初七，这里用公历近似

                # 购物节日
                f'{year}-06-18': '618购物节',
                f'{year}-08-18': '818购物节',
                f'{year}-11-11': '双11购物节',
                f'{year}-12-12': '双12购物节',

                # 其他特殊日期
                f'{year}-03-08': '妇女节',
                f'{year}-06-01': '儿童节',
                f'{year}-09-10': '教师节',
                f'{year}-11-24': '黑色星期五',  # 感恩节后第一天，这里用固定日期近似

                # 网络节日
                f'{year}-01-11': '光棍节前奏',
                f'{year}-04-01': '愚人节',
                f'{year}-05-04': '青年节',
                f'{year}-12-24': '平安夜'
            }

            # 分析特殊日期消费
            special_events = []
            if not daily_df.empty:
                for date_str, event_name in special_dates.items():
                    event_data = daily_df[daily_df['date'] == date_str]
                    if not event_data.empty:
                        event_expense = event_data.iloc[0]
                        avg_daily_expense = daily_df['daily_expense'].mean()

                        if event_expense['daily_expense'] > avg_daily_expense * 1.5:
                            special_events.append({
                                'date': date_str,
                                'event': event_name,
                                'amount': float(event_expense['daily_expense']),
                                'count': int(event_expense['transaction_count']),
                                'multiplier': round(event_expense['daily_expense'] / avg_daily_expense, 1)
                            })

            # TOP5破产日
            top_expense_days = []
            if not daily_df.empty:
                top_5 = daily_df.head(5)
                for _, row in top_5.iterrows():
                    date_obj = datetime.strptime(row['date'], '%Y-%m-%d')
                    top_expense_days.append({
                        'date': row['date'],
                        'month': date_obj.month,
                        'day': date_obj.day,
                        'amount': float(row['daily_expense']),
                        'count': int(row['transaction_count'])
                    })

            # 周末vs工作日对比
            weekend_vs_workday = {}
            if not weekend_df.empty:
                weekend_data = weekend_df[weekend_df['day_type'] == '周末']
                workday_data = weekend_df[weekend_df['day_type'] == '工作日']

                if not weekend_data.empty and not workday_data.empty:
                    weekend_avg = weekend_data.iloc[0]['avg_amount']
                    workday_avg = workday_data.iloc[0]['avg_amount']

                    if weekend_avg > workday_avg:
                        ratio = weekend_avg / workday_avg
                        weekend_vs_workday = {
                            'pattern': '周末更爱花钱',
                            'description': f'周末消费比工作日多{ratio:.1f}倍',
                            'weekend_avg': float(weekend_avg),
                            'workday_avg': float(workday_avg)
                        }
                    else:
                        ratio = workday_avg / weekend_avg
                        weekend_vs_workday = {
                            'pattern': '工作日消费更多',
                            'description': f'工作日消费比周末多{ratio:.1f}倍',
                            'weekend_avg': float(weekend_avg),
                            'workday_avg': float(workday_avg)
                        }

            result = {
                'year': year,
                'special_events': special_events,
                'top_expense_days': top_expense_days,
                'weekend_vs_workday': weekend_vs_workday
            }

            logger.info(f"获取{year}年特殊事件分析数据成功")
            return result

        except Exception as e:
            logger.error(f"获取特殊事件分析数据时发生错误: {str(e)}")
            raise

    def get_available_years(self) -> List[int]:
        """获取数据库中存在交易数据的所有年份

        Returns:
            List[int]: 可用年份列表，按降序排列（最新年份在前）
        """
        try:
            conn = self._get_connection()

            query = """
            SELECT DISTINCT strftime('%Y', date) as year
            FROM transactions
            WHERE date IS NOT NULL
            ORDER BY year DESC
            """

            df = pd.read_sql_query(query, conn)
            conn.close()

            if df.empty:
                logger.warning("数据库中没有找到任何交易数据")
                return []

            years = [int(year) for year in df['year'].tolist()]
            logger.info(f"找到可用年份: {years}")
            return years

        except Exception as e:
            logger.error(f"获取可用年份时发生错误: {str(e)}")
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