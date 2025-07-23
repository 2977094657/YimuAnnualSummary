import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

// 统一的背景样式 - 手帐剪贴风格
const UNIFIED_BACKGROUND = {
  background: `
    radial-gradient(circle at 15% 85%, rgba(254, 240, 238, 0.3) 0%, transparent 70%),
    radial-gradient(circle at 85% 15%, rgba(253, 246, 178, 0.3) 0%, transparent 70%),
    radial-gradient(circle at 15% 15%, rgba(219, 234, 254, 0.3) 0%, transparent 70%),
    radial-gradient(circle at 85% 85%, rgba(240, 253, 244, 0.3) 0%, transparent 70%),
    radial-gradient(circle at 50% 50%, rgba(253, 230, 138, 0.2) 0%, transparent 80%),
    linear-gradient(135deg, 
      #f8fafc 0%, 
      #fef3f2 15%, 
      #fefce8 30%, 
      #eff6ff 45%, 
      #f0fdf4 60%, 
      #fef3f2 75%, 
      #f8fafc 100%
    )
  `
};

// 纸质背景纹理样式
const PAPER_TEXTURE = {
  backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 20 20'%3E%3Cg fill='%23000000' fill-opacity='0.4'%3E%3Cpolygon points='20,15 15,20 5,20 0,15 0,5 5,0 15,0 20,5'/%3E%3C/g%3E%3C/svg%3E")`
};

interface FinancialData {
  annual_total_income: number;
  annual_total_expense: number;
  annual_net_savings: number;
  annual_savings_rate: number;
  year_end_total_assets: number;
  year_end_total_liabilities: number;
  year_end_net_assets: number;
  avg_monthly_income: number;
  avg_monthly_expense: number;
  annual_total_transactions: number;
  max_single_income: number;
  max_single_expense: number;
  main_income_source?: {
    source: string;
    amount: number;
    count: number;
    percentage: number;
  };
}

const FinancialOverview: React.FC = () => {
  const [financialData, setFinancialData] = useState<FinancialData | null>(null);
  const [dailyData, setDailyData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedYear, setSelectedYear] = useState<number>(new Date().getFullYear() - 1);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // 同时获取财务概览和每日数据
        const [financialResponse, dailyResponse] = await Promise.all([
          fetch(`http://localhost:8000/api/financial-overview?year=${selectedYear}`),
          fetch(`http://localhost:8000/api/daily-data?year=${selectedYear}`)
        ]);
        
        if (!financialResponse.ok || !dailyResponse.ok) {
          throw new Error(`HTTP error! financial: ${financialResponse.status}, daily: ${dailyResponse.status}`);
        }
        
        const [financialData, dailyData] = await Promise.all([
          financialResponse.json(),
          dailyResponse.json()
        ]);
        
        // console.log('获取到的每日数据:', dailyData);
        setFinancialData(financialData);
        setDailyData(dailyData);
        setError(null);
      } catch (err) {
        console.error('获取数据失败:', err);
        setError(err instanceof Error ? err.message : '获取数据失败');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [selectedYear]);

  // 键盘快捷键切换年份
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const yearOptions = getYearOptions();
      const currentIndex = yearOptions.indexOf(selectedYear);
      
      if (e.key === 'ArrowLeft' && currentIndex < yearOptions.length - 1) {
        // 左箭头 - 切换到上一年
        setSelectedYear(yearOptions[currentIndex + 1]);
      } else if (e.key === 'ArrowRight' && currentIndex > 0) {
        // 右箭头 - 切换到下一年
        setSelectedYear(yearOptions[currentIndex - 1]);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedYear]);

  // 生成年份选项（当前年份前5年到当前年份）
  const getYearOptions = () => {
    const currentYear = new Date().getFullYear();
    const years = [];
    for (let i = currentYear; i >= currentYear - 5; i--) {
      years.push(i);
    }
    return years;
  };

  const fetchFinancialData = async (targetYear?: number) => {
    try {
      setLoading(true);
      // 默认分析上一年份的数据
      const year = targetYear || new Date().getFullYear() - 1;
      const response = await fetch(`http://localhost:8000/api/financial-overview?year=${year}`);
      if (!response.ok) {
        throw new Error('Failed to fetch financial data');
      }
      const data = await response.json();
      setFinancialData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: 'CNY',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  const formatPercentage = (rate: number): string => {
    return `${(rate * 100).toFixed(1)}%`;
  };

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center" style={UNIFIED_BACKGROUND}>
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full"
        />
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-screen flex items-center justify-center" style={UNIFIED_BACKGROUND}>
        <div className="bg-white p-6 max-w-md rounded-lg shadow-lg">
          <h2 className="text-xl font-semibold text-red-600 mb-2">加载失败</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => fetchFinancialData(selectedYear)}
            className="px-4 py-2 bg-amber-500 text-white rounded hover:bg-amber-600 transition-colors"
          >
            重试
          </button>
        </div>
      </div>
    );
  }

  if (!financialData) {
    return (
      <div className="h-screen flex items-center justify-center" style={UNIFIED_BACKGROUND}>
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <p className="text-gray-600">暂无数据</p>
        </div>
      </div>
    );
  }

  // 核心财务指标（精简版）
  const coreMetrics = [
    {
      title: '今年一共赚了',
      value: formatCurrency(financialData.annual_total_income),
      icon: <img src="/SavedStickers/💰_AgADClAAAmeMcEs.webp" alt="💰" className="w-6 h-6" />,
      bgColor: 'from-green-100 to-emerald-200',
      borderColor: 'border-green-300',
      description: '辛苦一年的收获'
    },
    {
      title: '今年一共花了',
      value: formatCurrency(financialData.annual_total_expense),
      icon: <img src="/SavedStickers/💰_AgADClAAAmeMcEs.webp" alt="💸" className="w-6 h-6" />,
      bgColor: 'from-red-100 to-rose-200',
      borderColor: 'border-red-300',
      description: '生活的必要开销'
    },
    {
      title: '今年存下了',
      value: formatCurrency(financialData.annual_net_savings),
      icon: <img src="/SavedStickers/🏠_AgADeVUAAhYwcEo.webp" alt="🏦" className="w-6 h-6" />,
      bgColor: financialData.annual_net_savings >= 0 ? 'from-blue-100 to-sky-200' : 'from-orange-100 to-amber-200',
      borderColor: financialData.annual_net_savings >= 0 ? 'border-blue-300' : 'border-orange-300',
      description: financialData.annual_net_savings >= 0 ? '为未来积累的财富' : '需要调整的地方'
    }
  ];

  // 生成多维度财务分析总结
  const generateInsights = () => {
    const totalIncome = financialData.annual_total_income;
    const totalExpense = financialData.annual_total_expense;
    const netSavings = financialData.annual_net_savings;
    const totalTransactions = financialData.annual_total_transactions;
    const avgDailyExpense = financialData.avg_daily_expense;
    const accountUsage = financialData.account_usage || [];
    const locationStats = financialData.location_stats || [];
    const categoryExpenses = financialData.category_expenses || [];
    const mostFrequentItem = financialData.most_frequent_item || { note: '', count: 0 };
    const maxExpenseData = financialData.max_single_expense_data || { amount: 0, date: '', note: '', category: '' };
    const maxIncomeData = financialData.max_single_income_data || { amount: 0, date: '', note: '', category: '' };
    
    let insights = [];
    
    // 基础统计信息
    const accountCount = accountUsage.length;
    const mostUsedAccount = accountUsage[0] || { account: '', usage_count: 0, percentage: 0 };
    
    // 主要内容 - 温馨日常碎碎念风格（简化版）
    let mainContent = `这一年和 **一木记账** 记录了 **${totalTransactions}** 条小账单，用过 **${accountCount}** 个账户`;
    
    if (mostUsedAccount.account) {
      mainContent += `，最爱用 **${mostUsedAccount.account}**，占了 **${mostUsedAccount.percentage}%**`;
    }
    
    mainContent += ` 收获了 **${formatCurrency(totalIncome)}** 小确幸，花掉 **${formatCurrency(totalExpense)}**，存下 **${formatCurrency(netSavings)}** 小金库，平均每天花费 **${formatCurrency(avgDailyExpense)}**`;
    
    // 添加收入来源洞察
    if (financialData.main_income_source && financialData.main_income_source.source) {
      const incomeSource = financialData.main_income_source;
      mainContent += `，这一年大部分收入都来源于 **${incomeSource.source}**，贡献了 **${incomeSource.percentage}%** 的收入呢`;
    }
    
    // 最高支出信息 - 温馨化（简化）
    if (maxExpenseData.amount > 0) {
      const expenseDate = new Date(maxExpenseData.date);
      const month = expenseDate.getMonth() + 1;
      const day = expenseDate.getDate();
      
      if (maxExpenseData.note && maxExpenseData.note.trim()) {
        mainContent += ` **${month}月${day}日** 为 **${maxExpenseData.note}** 花了 **${formatCurrency(maxExpenseData.amount)}**，是今年最大手笔呢`;
      } else {
        mainContent += ` **${month}月${day}日** 在 **${maxExpenseData.category}** 花了 **${formatCurrency(maxExpenseData.amount)}**，是今年最大手笔呢`;
      }
    }
    
    // 最高收入信息 - 温馨化（简化）
    if (maxIncomeData.amount > 0) {
      const incomeDate = new Date(maxIncomeData.date);
      const month = incomeDate.getMonth() + 1;
      const day = incomeDate.getDate();
      
      mainContent += ` **${month}月${day}日** 收到 **${formatCurrency(maxIncomeData.amount)}`;
      if (maxIncomeData.note && maxIncomeData.note.trim()) {
        mainContent += ` ${maxIncomeData.note}**`;
      } else {
        mainContent += ` ${maxIncomeData.category}**`;
      }
      mainContent += ` 的惊喜，是今年最大收入呢`;
    }
    
    insights.push(mainContent);
    
    // 地点消费统计 - 温馨化
    if (locationStats.length > 0) {
      const topLocation = locationStats[0];
      insights.push(`**${topLocation.location}** 真是我的心头好呢，在那里的消费占了全部的 **${topLocation.percentage}%**，每次去都忍不住买买买～`);
    }
    
    // 分类支出统计 - 温馨化
    if (categoryExpenses.length > 0) {
      const topCategory = categoryExpenses[0];
      const categoryCount = categoryExpenses.length;
      insights.push(`生活被我分成了 **${categoryCount}** 个小类别，其中 **${topCategory.category}** 最得我心，花费了 **${formatCurrency(topCategory.expense)}**，果然是我最舍得投资的地方呀`);
    }
    
    // 最常购买物品 - 温馨化
    if (mostFrequentItem.note && mostFrequentItem.count > 0) {
      insights.push(`说到最爱，**${mostFrequentItem.note}** 绝对是我的心头宝，忍不住买了 **${mostFrequentItem.count}** 次，真是越买越开心呢`);
    }
    
    return insights;
  };

  const insights = generateInsights();

  return (
    <section className="h-screen relative overflow-visible" style={UNIFIED_BACKGROUND}>
      {/* 纸质背景纹理 */}
      <div className="absolute inset-0 opacity-[0.03]" style={PAPER_TEXTURE} />
      
      {/* 年份显示 - 可爱便签风格 */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.8, rotate: 10 }}
        animate={{ opacity: 1, scale: 1, rotate: -3 }}
        transition={{ duration: 1, delay: 1.5, ease: "easeOut" }}
        className="absolute top-8 right-24 z-50"
      >
        <div className="relative">
          {/* 便签纸背景 */}
          <div 
            className="bg-gradient-to-br from-yellow-100 to-amber-50 p-3 relative"
            style={{
              clipPath: `polygon(
                0% 8%, 8% 0%, 92% 0%, 100% 12%, 
                100% 88%, 88% 100%, 12% 100%, 0% 85%
              )`,
              filter: 'drop-shadow(2px 3px 6px rgba(0,0,0,0.15))',
              transform: 'rotate(-3deg)',
              backgroundImage: `
                radial-gradient(circle at 20% 80%, rgba(255, 193, 7, 0.1) 0%, transparent 50%),
                linear-gradient(45deg, transparent 48%, rgba(255, 255, 255, 0.3) 49%, rgba(255, 255, 255, 0.3) 51%, transparent 52%)
              `
            }}
          >
                                                   <div className="text-center">
               <div className="text-2xl font-bold mb-1 px-2" 
                   style={{ 
                     fontFamily: '"Comic Sans MS", cursive',
                     color: '#a16207',
                     textShadow: '0 1px 2px rgba(255,255,255,0.9), 0 2px 4px rgba(161,98,7,0.3)',
                     filter: 'brightness(1.15)',
                   }}>
                   {selectedYear}
                 </div>
               
               <div className="text-xs text-amber-600 font-medium" 
                 dangerouslySetInnerHTML={{
                   __html: `<span style="background: linear-gradient(45deg, transparent 40%, #fbbf2477 50%, transparent 60%); font-weight: bold; padding: 2px; position: relative; border-radius: 2px; color: #92400e;"><span style="text-shadow: 1px 1px 0px #fbbf24; filter: brightness(1.1);">← → 年份</span></span>`
                 }}
               />
             </div>
          </div>
          
          {/* 图钉装饰 */}
          <motion.div 
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.6, delay: 2, ease: "easeOut" }}
            className="absolute -top-2 left-1/2 transform -translate-x-1/2 w-3 h-3 bg-red-400 rounded-full shadow-sm border border-red-500"
            style={{
              background: 'radial-gradient(circle at 30% 30%, #fca5a5, #ef4444)',
              filter: 'drop-shadow(0 1px 2px rgba(0,0,0,0.2))'
            }}
          />
          
          
           
           {/* 小装饰点 */}
           <div className="absolute -bottom-1 -left-1 w-1.5 h-1.5 bg-orange-300 rounded-full opacity-70" />
           <div className="absolute -top-1 -right-1 w-1 h-1 bg-yellow-400 rounded-full opacity-60" />
        </div>
      </motion.div>


      
      {/* 和纸胶带装饰 - 左上角 */}
      <motion.div
        initial={{ opacity: 0, x: -100, rotate: -25 }}
        animate={{ opacity: 1, x: 0, rotate: -15 }}
        transition={{ duration: 1.2, delay: 0.3, ease: "easeOut" }}
        className="absolute top-16 -left-8 w-80 h-10 z-40"
        style={{
          background: `
            linear-gradient(45deg, 
              rgba(196, 253, 191, 0.4) 0%, 
              rgba(134, 239, 172, 0.5) 25%, 
              rgba(196, 253, 191, 0.4) 50%, 
              rgba(134, 239, 172, 0.5) 75%, 
              rgba(196, 253, 191, 0.4) 100%
            )
          `,
          clipPath: `polygon(
            2% 15%, 8% 0%, 98% 10%, 100% 40%, 
            95% 85%, 92% 100%, 5% 90%, 0% 60%
          )`,
          filter: 'drop-shadow(2px 4px 8px rgba(0,0,0,0.1))',
          transform: 'rotate(-15deg)'
        }}
      />
      
      {/* 主标题卡片 */}
      <motion.div
        initial={{ opacity: 0, y: -30, rotate: -5 }}
        animate={{ opacity: 1, y: 0, rotate: -2 }}
        transition={{ duration: 1, delay: 0.5, ease: "easeOut" }}
        className="absolute top-12 left-16 z-30"
      >
        <div 
          className="bg-white p-6 relative"
          style={{
            clipPath: `polygon(
              5% 0%, 95% 2%, 98% 85%, 92% 100%, 
              3% 98%, 0% 15%
            )`,
            filter: 'drop-shadow(4px 6px 12px rgba(0,0,0,0.15))',
            transform: 'rotate(-2deg)'
          }}
        >
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            {selectedYear}年财务总览
          </h1>
          <div className="w-12 h-1 bg-blue-400 rounded-full"></div>
        </div>
      </motion.div>

      {/* 核心指标卡片 - 不规则分布 */}
      <div className="absolute inset-0 z-10">
        {coreMetrics.map((metric, index) => {
          // 为每个卡片设置不同的位置 - 上面两个，下面一个
          const positions = [
            { top: '6%', left: '28%', rotate: '-3deg' },
            { top: '6%', left: '50%', rotate: '2deg' },
            { top: '85%', left: '22%', rotate: '-1deg' }
          ];
          
          const position = positions[index];
          
          return (
            <motion.div
              key={metric.title}
              initial={{ opacity: 0, x: -100, rotate: -10 }}
              animate={{ opacity: 1, x: 0, rotate: 0 }}
              transition={{ duration: 0.8, delay: index * 0.4, ease: "easeOut" }}
              className={`absolute ${index === 2 ? 'w-40' : 'w-32'}`}
              style={{
                top: position.top,
                left: position.left,
                transform: `rotate(${position.rotate})`,
                overflow: 'visible'
              }}
            >
              {/* 胶带装饰 - 移到clipPath容器外面 */}
              {index === 0 && (
                <div className="absolute -top-1 left-1/3 w-10 h-3 bg-yellow-200 opacity-80 rotate-12 z-20"
                  style={{
                    clipPath: 'polygon(5% 0%, 95% 10%, 100% 90%, 0% 100%)',
                    backgroundImage: 'repeating-linear-gradient(45deg, transparent, transparent 4px, rgba(0,0,0,0.04) 4px, rgba(0,0,0,0.04) 8px)'
                  }}
                />
              )}
              
              {index === 1 && (
                <div className="absolute -top-2 right-1/4 w-8 h-4 bg-blue-200 opacity-70 -rotate-6 z-20"
                  style={{
                    clipPath: 'polygon(10% 5%, 90% 0%, 95% 95%, 5% 100%)',
                    backgroundImage: 'repeating-linear-gradient(-30deg, transparent, transparent 3px, rgba(0,0,0,0.03) 3px, rgba(0,0,0,0.03) 6px)'
                  }}
                />
              )}
              
              {index === 2 && (
                <div className="absolute -top-0.5 left-1/2 w-6 h-5 bg-pink-200 opacity-75 rotate-45 z-20"
                  style={{
                    clipPath: 'polygon(0% 20%, 80% 0%, 100% 80%, 20% 100%)',
                    backgroundImage: 'repeating-linear-gradient(60deg, transparent, transparent 3px, rgba(0,0,0,0.05) 3px, rgba(0,0,0,0.05) 6px)'
                  }}
                />
              )}
              
              <div 
                className={`bg-gradient-to-br ${metric.bgColor} p-2 relative border ${metric.borderColor}`}
                style={{
                  clipPath: `polygon(
                    3% 6%, 7% 1%, 93% 3%, 97% 9%, 
                    95% 91%, 89% 97%, 11% 95%, 5% 89%
                  )`,
                  filter: 'drop-shadow(2px 3px 6px rgba(0,0,0,0.15))'
                }}
              >
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{metric.icon}</span>
                  <div className="flex-1">
                    <h3 className="text-xs font-semibold text-gray-700 mb-0.5">{metric.title}</h3>
                    <p className="text-sm font-bold text-gray-800">{metric.value}</p>
                    <p className="text-xs text-gray-600 mt-0.5">{metric.description}</p>
                  </div>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* 数据洞察卡片 */}
      <motion.div
        initial={{ opacity: 0, x: 50, rotate: 8 }}
        animate={{ opacity: 1, x: 0, rotate: 5 }}
        transition={{ duration: 1, delay: 1.5, ease: "easeOut" }}
        className="absolute top-20 right-16 z-50 w-80"
      >
        {/* 移除左上角胶带装饰 */}
        
        {/* 胶带装饰 - 右下角 - 移到外层避免被clip-path裁剪 */}
        <div className="absolute -bottom-5 right-4 w-14 h-6 bg-purple-200 opacity-70 -rotate-20 z-10"
          style={{
            clipPath: 'polygon(10% 0%, 90% 15%, 100% 85%, 0% 100%)',
            backgroundImage: 'repeating-linear-gradient(-45deg, transparent, transparent 5px, rgba(0,0,0,0.03) 5px, rgba(0,0,0,0.03) 10px)'
          }}
        />
        
        <div 
          className="bg-yellow-100 border-l-4 border-yellow-300 p-5 relative"
          style={{
            clipPath: `polygon(
              5% 3%, 95% 0%, 98% 92%, 90% 100%, 
              2% 97%, 0% 8%
            )`,
            filter: 'drop-shadow(3px 5px 10px rgba(0,0,0,0.12))',
            transform: 'rotate(5deg)'
          }}
        >
          
          <h3 className="text-lg font-semibold text-gray-700 mb-3 flex items-center"><img src="/SavedStickers/💖_AgADlVUAAltsiEg.webp" alt="💝" className="w-8 h-8 mr-2" /> 今年的财务小结</h3>
          <div className="space-y-1">
            {insights.map((insight, index) => (
              <div key={index} className="relative">
                {/* 手绘装饰元素 - 在外层避免被clip-path裁剪 */}
                {index === 0 && (
                  <>
                    <div className="absolute -top-3 left-1 text-red-400 text-xs transform -rotate-12 z-10">★</div>
                    <div className="absolute -bottom-2 right-6 w-8 h-1 bg-yellow-300 opacity-40 transform rotate-3 z-10"></div>
                  </>
                )}
                {index === 1 && (
                  <>
                    <div className="absolute -top-2 right-2 w-6 h-3 bg-yellow-300 opacity-60 rotate-45 z-10"
                      style={{
                        clipPath: 'polygon(20% 0%, 100% 20%, 80% 100%, 0% 80%)',
                        backgroundImage: 'repeating-linear-gradient(30deg, transparent, transparent 2px, rgba(0,0,0,0.05) 2px, rgba(0,0,0,0.05) 4px)'
                      }}
                    />
                    <div className="absolute top-2 left-0 text-blue-400 text-xs z-10">→</div>
                  </>
                )}
                {index === 2 && (
                  <>
                    <div className="absolute -top-2 left-4 w-4 h-4 border-2 border-green-400 rounded-full opacity-30 z-10"></div>
                    <div className="absolute bottom-1 right-1 text-purple-400 text-xs transform rotate-45 z-10">✓</div>
                  </>
                )}
                {index === 3 && (
                  <>
                    <div className="absolute -top-1 right-0 w-3 h-8 bg-pink-300 opacity-40 transform -rotate-12 z-10"></div>
                    <div className="absolute -bottom-2 left-2 text-orange-400 text-xs z-10">♡</div>
                  </>
                )}
                {index >= 4 && (
                  <>
                    <div className="absolute top-0 right-0 w-2 h-2 bg-indigo-400 rounded-full opacity-50 z-10"></div>
                    <div className="absolute bottom-0 left-0 w-6 h-1 bg-teal-300 opacity-30 transform -rotate-2 z-10"></div>
                  </>
                )}
                
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.6, delay: 3 + index * 0.2, ease: "easeOut" }}
                  className="text-sm text-gray-600 leading-relaxed p-3 bg-gray-50 rounded-lg border border-gray-200 relative"
                  style={{
                    clipPath: `polygon(
                      1% 10%, 5% 2%, 95% 5%, 99% 15%, 
                      97% 85%, 93% 98%, 7% 95%, 3% 85%
                    )`,
                    background: `linear-gradient(${120 + index * 30}deg, #fefefe 0%, #f8f9fa 100%)`,
                    transform: `rotate(${(index % 2 === 0 ? 1 : -1) * 0.5}deg)`
                  }}
                >
                  {/* 内容区域 */}
                <span dangerouslySetInnerHTML={{ 
                   __html: insight
                     .replace(/\*\*(.*?)\*\*/g, (match, p1, offset, string) => {
                       // 根据内容判断是收入还是支出，选择对应颜色
                       const isIncome = /收入|获得|进账/.test(p1) || /收入|获得|进账/.test(string.substring(Math.max(0, offset - 20), offset + 20));
                       const isExpense = /支出|消费|花费|购买/.test(p1) || /支出|消费|花费|购买/.test(string.substring(Math.max(0, offset - 20), offset + 20));
                       const isHighestExpense = /最高.*支出/.test(string) && /¥/.test(p1);
                       // 新增：检测"收获了xx小确幸"、"花掉xx"和"收到最多钱"的特定模式
                       const isHappiness = /小确幸/.test(p1) || (/收获了/.test(string.substring(Math.max(0, offset - 10), offset)) && /小确幸/.test(string.substring(offset, offset + 20)));
                       const isSpending = /花掉/.test(string.substring(Math.max(0, offset - 10), offset)) && /¥/.test(p1);
                       const isMaxIncome = /收到/.test(string.substring(Math.max(0, offset - 10), offset)) && /¥/.test(p1) && (/最大|最多|最高/.test(string) || /惊喜/.test(string));
                       
                       let colors;
                       if (isHappiness) {
                         colors = ['#22c55e', '#16a34a', '#15803d', '#166534']; // 绿色系 - 专门为小确幸
                       } else if (isSpending) {
                         colors = ['#ef4444', '#dc2626', '#b91c1c', '#991b1b']; // 红色系 - 专门为花掉
                       } else if (isMaxIncome) {
                         colors = ['#22c55e', '#eab308', '#f59e0b', '#d97706']; // 绿色向黄色渐变 - 专门为收到最多钱
                       } else if (isIncome) {
                         colors = ['#22c55e', '#16a34a', '#15803d', '#166534']; // 绿色系
                       } else if (isExpense || isHighestExpense) {
                         colors = ['#ef4444', '#dc2626', '#b91c1c', '#991b1b']; // 红色系
                       } else {
                         colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#ff9ff3', '#54a0ff', '#fd79a8', '#6c5ce7', '#a29bfe'];
                       }
                       
                       // 为收到最多钱特殊处理绿色向黄色流动渐变
                       if (isMaxIncome) {
                         return `<span style="background: linear-gradient(90deg, #22c55e 0%, #eab308 25%, #f59e0b 50%, #d97706 75%, #22c55e 100%); background-size: 200% 100%; animation: flowGradient 3s ease-in-out infinite; padding: 3px 6px; border-radius: 8px; font-weight: bold; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.3); display: inline-block; transform: rotate(${(offset % 2 === 0 ? 2 : -2)}deg); box-shadow: 0 2px 8px rgba(34, 197, 94, 0.4);">${p1}</span><style>@keyframes flowGradient { 0%, 100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }</style>`;
                       }
                       
                       const decorations = [
                         // 波浪下划线 + 高亮背景
                         `<span style="background: linear-gradient(120deg, ${colors[offset % colors.length]}22 0%, ${colors[offset % colors.length]}44 100%); padding: 2px 4px; border-radius: 3px; font-weight: bold; position: relative; box-shadow: 0 2px 4px ${colors[offset % colors.length]}33;"><span style="border-bottom: 2px wavy ${colors[offset % colors.length]}; text-decoration: underline; text-decoration-color: ${colors[offset % colors.length]}; text-decoration-style: wavy;">${p1}</span></span>`,
                         // 圆角边框 + 虚线
                         `<span style="background: ${colors[offset % colors.length]}33; padding: 1px 3px; border-radius: 50px; font-weight: bold; border: 2px dashed ${colors[offset % colors.length]}; position: relative; transform: rotate(${Math.random() > 0.5 ? 1 : -1}deg);">${p1}</span>`,
                         // 荧光笔效果
                         `<span style="background: linear-gradient(45deg, transparent 40%, ${colors[offset % colors.length]}77 50%, transparent 60%); font-weight: bold; padding: 2px; position: relative; border-radius: 2px;"><span style="text-shadow: 1px 1px 0px ${colors[offset % colors.length]}; filter: brightness(1.1);">${p1}</span></span>`,
                         // 手写框框
                         `<span style="border: 2px solid ${colors[offset % colors.length]}; border-radius: 8px; padding: 2px 4px; background: ${colors[offset % colors.length]}11; font-weight: bold; position: relative; transform: rotate(${(offset % 3 - 1) * 1.5}deg); display: inline-block; box-shadow: 1px 2px 3px ${colors[offset % colors.length]}44;">${p1}</span>`,
                         // 左侧标记条
                         `<span style="background: ${colors[offset % colors.length]}22; padding: 2px 4px; font-weight: bold; position: relative; border-left: 4px solid ${colors[offset % colors.length]}; border-radius: 0 4px 4px 0; margin: 0 1px;">${p1}</span>`,
                         // 不规则圆圈包围 (特别为最高支出设计)
                         isHighestExpense ? 
                           `<span style="border: 3px solid #ef4444; border-radius: 45% 55% 52% 48%; padding: 2px 6px; background: #ef444415; font-weight: bold; display: inline-block; transform: rotate(${(offset % 2 === 0 ? 3 : -3)}deg); box-shadow: 0 0 8px #ef444444;">${p1}</span>` :
                           `<span style="border: 3px solid ${colors[offset % colors.length]}; border-radius: 50px; padding: 1px 6px; background: ${colors[offset % colors.length]}15; font-weight: bold; display: inline-block; transform: rotate(${(offset % 2 === 0 ? 2 : -2)}deg);">${p1}</span>`,
                         // 双重下划线
                         `<span style="font-weight: bold; position: relative; color: ${colors[offset % colors.length]}; text-shadow: 1px 1px 0px rgba(0,0,0,0.1);"><span style="border-bottom: 3px double ${colors[offset % colors.length]}; padding-bottom: 1px;">${p1}</span></span>`,
                         // 手写箭头指向 (收入向上，支出向下)
                         `<span style="background: ${colors[offset % colors.length]}25; padding: 2px 4px; font-weight: bold; border-radius: 4px; position: relative; margin: 0 2px;"><span style="color: ${colors[offset % colors.length]};">${p1}</span><span style="position: absolute; top: -8px; right: -8px; color: ${colors[offset % colors.length]}; font-size: 12px; transform: rotate(${isIncome ? '-45deg' : isExpense ? '135deg' : '45deg'});">${isIncome ? '↗' : isExpense ? '↘' : '↗'}</span></span>`,
                         // 星星装饰
                         `<span style="background: linear-gradient(135deg, ${colors[offset % colors.length]}33, ${colors[offset % colors.length]}55); padding: 2px 4px; font-weight: bold; border-radius: 6px; position: relative; box-shadow: 0 1px 3px ${colors[offset % colors.length]}66;"><span style="color: ${colors[offset % colors.length]};">${p1}</span><span style="position: absolute; top: -6px; left: -4px; color: ${colors[offset % colors.length]}; font-size: 8px;">★</span></span>`,
                         // 手绘感边框
                         `<span style="border: 2px solid ${colors[offset % colors.length]}; padding: 1px 3px; font-weight: bold; background: ${colors[offset % colors.length]}18; position: relative; display: inline-block; transform: skew(-2deg) rotate(${(offset % 2 === 0 ? 1 : -1)}deg); border-radius: 3px 8px 3px 8px;">${p1}</span>`
                       ];
                       return decorations[offset % decorations.length];
                     })
                 }} />
                </motion.div>
              </div>
              ))}
            </div>
        </div>
      </motion.div>

      {/* 手绘涂鸦装饰元素 */}
      {/* 左上角手绘涂鸦 */}
      <motion.div
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1.2, delay: 2, ease: "easeOut" }}
        className="absolute top-6 left-6 z-30"
      >
        <svg width="80" height="60" className="text-blue-400 opacity-60">
          {/* 手绘云朵 */}
          <path d="M15 35 Q10 25 20 25 Q25 15 35 25 Q45 20 50 30 Q55 25 60 35 Q50 45 40 40 Q30 50 20 40 Q10 45 15 35" 
                stroke="currentColor" 
                strokeWidth="2" 
                fill="none" 
                strokeLinecap="round"
                strokeLinejoin="round"/>
          <circle cx="25" cy="32" r="1.5" fill="currentColor" opacity="0.8"/>
          <circle cx="40" cy="30" r="1" fill="currentColor" opacity="0.6"/>
        </svg>
      </motion.div>

      {/* 右上角手绘太阳 */}
      <motion.div
        initial={{ opacity: 0, rotate: -180 }}
        animate={{ opacity: 1, rotate: 0 }}
        transition={{ duration: 1.5, delay: 2.5, ease: "easeOut" }}
        className="absolute top-8 right-8 z-30"
      >
        <svg width="70" height="70" className="text-yellow-500 opacity-70">
          {/* 手绘太阳 */}
          <circle cx="35" cy="35" r="12" stroke="currentColor" strokeWidth="2" fill="none"/>
          <path d="M35 8 L35 18 M35 52 L35 62 M62 35 L52 35 M18 35 L8 35" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          <path d="M53 17 L47 23 M23 47 L17 53 M53 53 L47 47 M23 23 L17 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          <circle cx="35" cy="35" r="3" fill="currentColor" opacity="0.8"/>
        </svg>
      </motion.div>

      {/* 左侧手绘箭头涂鸦 */}
      <motion.div
        initial={{ opacity: 0, x: -30 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 1, delay: 3, ease: "easeOut" }}
        className="absolute top-1/3 left-2 z-30"
      >
        <svg width="60" height="100" className="text-green-500 opacity-50">
          {/* 手绘弯曲箭头 */}
          <path d="M10 20 Q30 10 40 30 Q35 50 25 70 Q20 85 30 90" 
                stroke="currentColor" 
                strokeWidth="3" 
                fill="none" 
                strokeLinecap="round"
                strokeDasharray="5,3"/>
          <path d="M25 85 L30 90 L35 85" stroke="currentColor" strokeWidth="3" strokeLinecap="round" fill="none"/>
          <text x="45" y="50" className="text-xs fill-current" transform="rotate(15)">Good!</text>
        </svg>
      </motion.div>

      {/* 右侧手绘心形涂鸦 */}
      <motion.div
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1, delay: 3.5, ease: "easeOut" }}
        className="absolute top-1/2 right-6 z-30"
      >
        <svg width="50" height="50" className="text-pink-400 opacity-60">
          {/* 手绘心形 */}
          <path d="M25 40 Q15 25 10 20 Q5 10 15 15 Q25 20 25 25 Q25 20 35 15 Q45 10 40 20 Q35 25 25 40" 
                stroke="currentColor" 
                strokeWidth="2" 
                fill="currentColor" 
                fillOpacity="0.2"
                strokeLinecap="round"/>
        </svg>
      </motion.div>

      {/* 底部手绘波浪线 */}
      <motion.div
        initial={{ opacity: 0, pathLength: 0 }}
        animate={{ opacity: 1, pathLength: 1 }}
        transition={{ duration: 2, delay: 4, ease: "easeInOut" }}
        className="absolute bottom-12 left-1/4 z-30"
      >
        <svg width="300" height="40" className="text-purple-400 opacity-40">
          <path d="M10 20 Q30 10 50 20 Q70 30 90 20 Q110 10 130 20 Q150 30 170 20 Q190 10 210 20 Q230 30 250 20 Q270 10 290 20" 
                stroke="currentColor" 
                strokeWidth="2" 
                fill="none" 
                strokeLinecap="round"
                strokeDasharray="3,2"/>
        </svg>
      </motion.div>

      {/* 随机手绘星星散布 */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 4.5, ease: "easeOut" }}
        className="absolute top-1/4 left-1/3 z-30"
      >
        <svg width="30" height="30" className="text-yellow-400 opacity-50">
          <path d="M15 5 L17 12 L24 12 L18 17 L20 24 L15 20 L10 24 L12 17 L6 12 L13 12 Z" 
                stroke="currentColor" 
                strokeWidth="1" 
                fill="currentColor" 
                fillOpacity="0.3"/>
        </svg>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 5, ease: "easeOut" }}
        className="absolute top-2/3 right-1/3 z-30"
      >
        <svg width="25" height="25" className="text-orange-400 opacity-60">
          <path d="M12.5 3 L14 9 L20 9 L15 13 L16.5 19 L12.5 16 L8.5 19 L10 13 L5 9 L11 9 Z" 
                stroke="currentColor" 
                strokeWidth="1" 
                fill="currentColor" 
                fillOpacity="0.4"/>
        </svg>
      </motion.div>

      {/* 手绘文字涂鸦 */}
      <motion.div
        initial={{ opacity: 0, rotate: -10 }}
        animate={{ opacity: 1, rotate: 5 }}
        transition={{ duration: 1, delay: 5.5, ease: "easeOut" }}
        className="absolute bottom-1/4 right-8 z-30"
      >
        <svg width="80" height="30" className="text-indigo-400 opacity-50">
          <text x="10" y="20" className="text-sm fill-current font-handwriting" transform="rotate(-5)">Nice!</text>
          <path d="M5 25 Q40 15 75 25" stroke="currentColor" strokeWidth="1" fill="none" strokeDasharray="2,1"/>
        </svg>
      </motion.div>

      {/* 年度财务热力图 - 日级别 */}
       <motion.div
         initial={{ opacity: 0, y: 50 }}
         animate={{ opacity: 1, y: 0 }}
         transition={{ duration: 1, delay: 3.5, ease: "easeOut" }}
         className="absolute top-1/4 left-1/8 transform -translate-x-1/8 -translate-y-1/2 z-20 rotate-1"
       >
         {/* 胶带装饰 - 只保留顶部 */}
          <div className="absolute -top-3 left-1/4 w-1/2 h-6 bg-yellow-100 opacity-80 rotate-1 z-20"
            style={{
              clipPath: 'polygon(0% 0%, 100% 5%, 98% 100%, 2% 95%)',
              backgroundImage: 'repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(0,0,0,0.05) 10px, rgba(0,0,0,0.05) 20px)'
            }}
          />
         
         {/* 热力图卡片贴纸 - 移到卡片外面 */}
         <motion.div
           initial={{ opacity: 0, scale: 0, rotate: 25 }}
           animate={{ opacity: 1, scale: 1, rotate: 20 }}
           transition={{ duration: 0.8, delay: 4, ease: "easeOut" }}
           className="absolute z-[100]"
           style={{ bottom: 'calc(-40px)', left: 'calc(1rem - 20px)' }}
           onAnimationComplete={() => console.log('热力图贴纸渲染完成')}
         >
           <img 
             src="/stickers/油画风格钱币.png" 
             alt="钱币贴纸"
             className="w-40 h-40 object-contain"
             onLoad={(e) => {
               const img = e.target as HTMLImageElement;
               console.log('热力图贴纸加载完成:', img.naturalWidth, 'x', img.naturalHeight);
             }}
             style={{
               filter: 'drop-shadow(3px 4px 8px rgba(0,0,0,0.15))',
               transform: 'rotate(20deg)',
               maxWidth: '160px',
               maxHeight: '160px'
             }}
           />
         </motion.div>
         
         <div 
           className="bg-white p-8 relative border-2 border-gray-200 w-[1200px]"
           style={{
             clipPath: `polygon(
               2% 5%, 8% 0%, 92% 2%, 98% 8%, 
               96% 92%, 90% 98%, 10% 96%, 4% 90%
             )`,
             filter: 'drop-shadow(4px 6px 12px rgba(0,0,0,0.1))'
           }}
         >
           
           <h4 className="text-lg font-semibold text-gray-700 mb-6 text-center flex items-center justify-center"><img src="/SavedStickers/🔥_AgADg0wAAi7eSUs.webp" alt="🔥" className="w-6 h-6 mr-2" /> {selectedYear}年度财务热力图</h4>
           
           {/* 月份标签 - 与热力图列对应 */}
           <div className="flex mb-2" style={{ marginLeft: '24px' }}>
             {/* 星期标签占位 */}
             <div className="mr-2" style={{ width: '30px' }}></div>
             {/* 月份标签网格 */}
             <div className="grid text-xs text-gray-500" style={{ gridTemplateColumns: 'repeat(53, 1fr)', width: '900px', gap: '3px' }}>
               {Array.from({ length: 53 }, (_, weekIndex) => {
                 // 2025年1月1日是星期三(3)
                 const startDate = new Date(2025, 0, 1);
                 const startDayOfWeek = startDate.getDay(); // 0=周日, 1=周一, ..., 6=周六
                 
                 // 计算这一周的第一天（周日）的日期
                 const weekStartDate = new Date(2025, 0, 1 + weekIndex * 7 - startDayOfWeek);
                 
                 // 检查这一周是否包含某个月的第一天
                 let monthName = '';
                 for (let dayOffset = 0; dayOffset < 7; dayOffset++) {
                   const checkDate = new Date(weekStartDate.getTime() + dayOffset * 24 * 60 * 60 * 1000);
                   if (checkDate.getFullYear() === 2025 && checkDate.getDate() === 1) {
                     monthName = `${checkDate.getMonth() + 1}月`;
                     break;
                   }
                 }
                 
                 return (
                   <div key={weekIndex} className="text-center" style={{ width: '16px' }}>
                     {monthName}
                   </div>
                 );
               })}
             </div>
           </div>
           
           {/* 日级别热力图 */}
          <div className="relative mb-8">
             
             <div className="flex ml-4">
               {/* 星期标签 */}
               <div className="flex flex-col mr-2 text-xs text-gray-600" style={{ height: '180px', width: '30px', paddingTop: '12px', paddingBottom: '12px' }}>
                 <div className="flex-1 flex items-center justify-center">日</div>
                 <div className="flex-1 flex items-center justify-center">一</div>
                 <div className="flex-1 flex items-center justify-center">二</div>
                 <div className="flex-1 flex items-center justify-center">三</div>
                 <div className="flex-1 flex items-center justify-center">四</div>
                 <div className="flex-1 flex items-center justify-center">五</div>
                 <div className="flex-1 flex items-center justify-center">六</div>
               </div>
               
               {/* 热力图网格 */}
               <div className="grid p-3" style={{ gridTemplateColumns: 'repeat(53, 1fr)', gridTemplateRows: 'repeat(7, 1fr)', height: '180px', width: '900px', gap: '3px' }}>
                 {/* 生成365天的热力格子 - 标准热力图布局 */}
                 {Array.from({ length: 53 * 7 }, (_, index) => {
                   // 计算当前格子对应的周和星期
                   const dayOfWeek = Math.floor(index / 53); // 星期几 (0=周日, 1=周一, ..., 6=周六)
                   const weekIndex = index % 53; // 第几周 (0-52)
                   
                   // 计算年份的1月1日是星期几
                   const startDate = new Date(selectedYear, 0, 1);
                   const startDayOfWeek = startDate.getDay(); // 0=周日, 1=周一, ..., 6=周六
                   
                   // 计算实际日期
                   const dayOffset = weekIndex * 7 + dayOfWeek - startDayOfWeek;
                   const currentDate = new Date(selectedYear, 0, 1 + dayOffset);
                   
                   // 如果超出当前年份范围或日期无效，返回空格子
                   if (currentDate.getFullYear() !== selectedYear || dayOffset < 0) {
                     return (
                       <div 
                         key={`empty-${index}`}
                         className="rounded-[2px]"
                         style={{ width: '16px', height: '16px', backgroundColor: '#e2e8f0' }}
                       />
                     );
                   }
                 
                 const month = currentDate.getMonth();
                 const day = currentDate.getDate();
                 const dateStr = currentDate.toISOString().split('T')[0]; // YYYY-MM-DD格式
                 
                 // 从后端数据中查找当天的交易数据
                 const dayData = dailyData?.daily_data?.find((d: any) => d.date === dateStr) || {
                   income: 0,
                   expense: 0,
                   income_count: 0,
                   expense_count: 0
                 };
                 
                 // 数据已正确获取和匹配
                 
                 const incomeAmount = dayData.income || 0;
                 const expenseAmount = dayData.expense || 0;
                 const totalAmount = incomeAmount + expenseAmount;
                 const hasIncome = incomeAmount > 0;
                 const hasExpense = expenseAmount > 0;
                 
                 // 计算收入和支出的比例
                 const incomeRatio = totalAmount > 0 ? incomeAmount / totalAmount : 0;
                 const expenseRatio = totalAmount > 0 ? expenseAmount / totalAmount : 0;
                 
                 return (
                   <motion.div
                     key={`day-${index}`}
                     initial={{ opacity: 0, scale: 0.3 }}
                     animate={{ opacity: 1, scale: 1 }}
                     transition={{ 
                       duration: 0.3, 
                       delay: 3.5 + (index % 30) * 0.002,
                       ease: "easeOut"
                     }}
                     className="rounded-[2px] relative overflow-hidden cursor-pointer"
                     style={{ 
                       width: '16px',
                       height: '16px',
                       backgroundColor: totalAmount > 0 ? '#ffffff' : '#e2e8f0',
                       ...(totalAmount > 1000 && {
                         backgroundColor: incomeAmount > expenseAmount 
                           ? 'rgba(16, 185, 129, 0.15)'  // 绿色弥散背景 (收入多)
                           : 'rgba(239, 68, 68, 0.15)',  // 红色弥散背景 (支出多)
                         border: '2px solid',
                         borderImage: incomeAmount > expenseAmount 
                           ? 'linear-gradient(45deg, #10b981, #eab308, #10b981) 1'  // 绿色到黄色循环 (收入多)
                           : 'linear-gradient(45deg, #ef4444, #000000, #ef4444) 1',  // 红色到黑色循环 (支出多)
                         boxShadow: incomeAmount > expenseAmount
                           ? '0 0 8px rgba(16, 185, 129, 0.6), 0 0 12px rgba(234, 179, 8, 0.4)'  // 绿黄弥散阴影
                           : '0 0 8px rgba(239, 68, 68, 0.6), 0 0 12px rgba(0, 0, 0, 0.3)',      // 红黑弥散阴影
                         animation: incomeAmount > expenseAmount
                           ? 'pulseGreen 2s ease-in-out infinite'
                           : 'pulseRed 2s ease-in-out infinite'
                       })
                     }}
                     whileHover={{ scale: 1.5, zIndex: 10 }}
                     transition={{ type: "spring", stiffness: 300, damping: 20 }}
                     title={`${month+1}月${day}日 ${hasIncome ? `收入: ${formatCurrency(incomeAmount)}` : ''} ${hasExpense ? `支出: ${formatCurrency(expenseAmount)}` : ''} ${!hasIncome && !hasExpense ? '无交易' : ''}`}
                   >
                     {/* 收入部分 - 绿色 */}
                     {hasIncome && (
                       <div 
                         className="absolute top-0 left-0 bg-green-400"
                         style={{
                           width: '100%',
                           height: `${incomeRatio * 100}%`,
                           opacity: 0.8
                         }}
                       />
                     )}
                     
                     {/* 支出部分 - 红色 */}
                     {hasExpense && (
                       <div 
                         className="absolute bottom-0 left-0 bg-red-400"
                         style={{
                           width: '100%',
                           height: `${expenseRatio * 100}%`,
                           opacity: 0.8
                         }}
                       />
                     )}
                     
                     {/* 月初显示日期数字 */}
                     {day === 1 && (
                       <div className="absolute inset-0 flex items-center justify-center z-10">
                         <span className="text-[8px] font-bold text-gray-800 drop-shadow-sm">{month+1}</span>
                       </div>
                     )}
                     

                   </motion.div>
                 );
               })}
             </div>
           </div>
           </div>
           
           {/* 图例说明 */}
           <div className="flex justify-center space-x-6 mb-4 text-xs">
             <div className="flex items-center space-x-1">
               <div className="w-3 h-3 bg-green-500 opacity-70 rounded-sm"></div>
               <span className="text-gray-600">收入</span>
             </div>
             <div className="flex items-center space-x-1">
               <div className="w-3 h-3 bg-red-500 opacity-70 rounded-sm"></div>
               <span className="text-gray-600">支出</span>
             </div>
             <div className="flex items-center space-x-1">
               <div className="w-3 h-3 bg-gray-200 rounded-sm"></div>
               <span className="text-gray-600">无交易</span>
             </div>
           </div>
           
           {/* 年度总结 */}
           <div className="bg-gray-50 rounded-lg p-3 text-center relative">
             {/* 胶带装饰 - 右下角 */}
             <div className="absolute -bottom-2 -right-3 w-8 h-10 bg-green-100 opacity-70 rotate-25"
               style={{
                 clipPath: 'polygon(0% 10%, 90% 0%, 100% 90%, 10% 100%)',
                 backgroundImage: 'repeating-linear-gradient(30deg, transparent, transparent 6px, rgba(0,0,0,0.03) 6px, rgba(0,0,0,0.03) 12px)'
               }}
             />
             
             <div className="grid grid-cols-3 gap-2 text-xs">
               <div>
                 <div className="text-green-600 font-bold">{formatCurrency(financialData.annual_total_income)}</div>
                 <div className="text-gray-500">年度总收入</div>
               </div>
               <div>
                 <div className="text-red-600 font-bold">{formatCurrency(financialData.annual_total_expense)}</div>
                 <div className="text-gray-500">年度总支出</div>
               </div>
               <div>
                 <div className={`font-bold ${
                   financialData.annual_net_savings >= 0 ? 'text-blue-600' : 'text-orange-600'
                 }`}>
                   {formatCurrency(financialData.annual_net_savings)}
                 </div>
                 <div className="text-gray-500">年度净储蓄</div>
               </div>
             </div>
             <div className="mt-2 text-[10px] relative">
               <div 
                 dangerouslySetInnerHTML={{
                   __html: `<span style="background: linear-gradient(45deg, transparent 40%, #fbbf2477 50%, transparent 60%); font-weight: bold; padding: 2px 4px; position: relative; border-radius: 2px; color: #7c3aed;"><span style="text-shadow: 1px 1px 0px #fbbf24; filter: brightness(1.1);"><img src="/SavedStickers/💡_AgAD00wAAovVUEo.webp" alt="💡" style="width: 12px; height: 12px; display: inline-block; margin-right: 2px; vertical-align: middle;" /> 发光边框的格子代表高金额交易(>1000元)，带有炫酷流动渐变效果</span></span>`
                 }}
               />
               {/* 装饰性小星星 */}
               <img src="/SavedStickers/✨_AgAD10YAAmyJkUs.webp" alt="✨" className="absolute -top-1 -right-2 w-4 h-4 animate-pulse" />
               <img src="/SavedStickers/⭐_AgADrUUAAt3FKEs.webp" alt="💫" className="absolute -bottom-1 -left-1 w-4 h-4 animate-bounce" />
             </div>
           </div>
         </div>
       </motion.div>

       {/* 手写涂鸦装饰元素 */}
       {/* 装饰星星 */}
       <motion.div
         initial={{ opacity: 0, scale: 0.3, rotate: 45 }}
         animate={{ opacity: 1, scale: 1, rotate: 25 }}
         transition={{ duration: 0.8, delay: 3, ease: "easeOut" }}
         className="absolute bottom-32 right-32 z-15"
       >
         <div className="w-8 h-8 bg-gradient-to-br from-pink-200 to-rose-300"
           style={{
             clipPath: `polygon(
               50% 0%, 61% 35%, 98% 35%, 68% 57%, 
               79% 91%, 50% 70%, 21% 91%, 32% 57%, 
               2% 35%, 39% 35%
             )`,
             filter: 'drop-shadow(2px 3px 6px rgba(0,0,0,0.1))',
             transform: 'rotate(25deg)'
           }} />
       </motion.div>
       
       {/* 随机涂鸦元素 */}
       <motion.div
         initial={{ opacity: 0 }}
         animate={{ opacity: 0.6 }}
         transition={{ duration: 1, delay: 4 }}
         className="absolute top-40 left-20 transform -rotate-12 z-10"
       >
         <img src="/SavedStickers/✨_AgAD10YAAmyJkUs.webp" alt="✨" className="w-6 h-6" />
       </motion.div>
       
       <motion.div
         initial={{ opacity: 0 }}
         animate={{ opacity: 0.5 }}
         transition={{ duration: 1, delay: 4.5 }}
         className="absolute top-60 right-40 text-lg text-purple-300 transform rotate-45 z-10"
       >
         💫
       </motion.div>
       
       <motion.div
         initial={{ opacity: 0 }}
         animate={{ opacity: 0.4 }}
         transition={{ duration: 1, delay: 5 }}
         className="absolute bottom-40 left-40 text-xl text-green-300 transform -rotate-6 z-10"
       >
         🌟
       </motion.div>
       
       {/* 手绘箭头 */}
       <motion.div
         initial={{ opacity: 0, pathLength: 0 }}
         animate={{ opacity: 0.3, pathLength: 1 }}
         transition={{ duration: 2, delay: 3.5 }}
         className="absolute top-80 left-60 z-10"
       >
         <svg width="60" height="40" viewBox="0 0 60 40" className="text-red-300">
           <motion.path
             d="M10,30 Q30,10 50,25"
             stroke="currentColor"
             strokeWidth="2"
             fill="none"
             strokeDasharray="3,3"
             initial={{ pathLength: 0 }}
             animate={{ pathLength: 1 }}
             transition={{ duration: 2, delay: 3.5 }}
           />
           <polygon points="45,20 50,25 45,30" fill="currentColor" />
         </svg>
       </motion.div>
       
       {/* 手绘圆圈 */}
       <motion.div
         initial={{ opacity: 0, scale: 0 }}
         animate={{ opacity: 0.25, scale: 1 }}
         transition={{ duration: 1.5, delay: 4.2 }}
         className="absolute bottom-60 right-60 z-10"
       >
         <svg width="50" height="50" viewBox="0 0 50 50" className="text-yellow-400">
           <motion.circle
             cx="25"
             cy="25"
             r="20"
             stroke="currentColor"
             strokeWidth="3"
             fill="none"
             strokeDasharray="2,4"
             initial={{ pathLength: 0, rotate: 0 }}
             animate={{ pathLength: 1, rotate: 360 }}
             transition={{ duration: 3, delay: 4.2 }}
           />
         </svg>
       </motion.div>
       
       {/* 手写感叹号 */}
       <motion.div
         initial={{ opacity: 0, y: 10 }}
         animate={{ opacity: 0.4, y: 0 }}
         transition={{ duration: 0.8, delay: 5.5 }}
         className="absolute top-96 right-80 text-3xl text-orange-400 transform rotate-12 z-10"
         style={{ fontFamily: 'cursive' }}
       >
         !
       </motion.div>
    </section>
  );
};

export default FinancialOverview;