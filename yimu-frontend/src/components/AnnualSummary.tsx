import React, { useMemo, useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import FinancialOverview from './FinancialOverview';

// 移除不再需要的接口定义和常量

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
  backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 20 20'%3E%3Cg fill='%23000000' fill-opacity='0.4'%3E%3Cpolygon points='20,15 15,20 5,20 0,15 0,5 5,0 15,0 20,5'/%3E%3C/g%3E%3C/svg%3E")`,
  zIndex: 1
};

const AnnualSummary: React.FC = () => {
  console.log('AnnualSummary: Component function called');
  
  console.log('AnnualSummary: Component rendered');

  // 页面状态管理 - 支持刷新后状态保持
  const [currentPage, setCurrentPage] = useState(() => {
    const savedPage = sessionStorage.getItem('yimu-current-page');
    return savedPage ? parseInt(savedPage, 10) : 0;
  });
  
  // 页面列表
  const pages = ['welcome', 'financial-overview'];
  
  // 处理滚轮事件进行页面切换
  const handleWheel = (e: React.WheelEvent) => {
    if (e.deltaY > 0 && currentPage < pages.length - 1) {
      const newPage = currentPage + 1;
      setCurrentPage(newPage);
      sessionStorage.setItem('yimu-current-page', newPage.toString());
    } else if (e.deltaY < 0 && currentPage > 0) {
      const newPage = currentPage - 1;
      setCurrentPage(newPage);
      sessionStorage.setItem('yimu-current-page', newPage.toString());
    }
  };

  // 键盘上下键切换页面
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowDown' && currentPage < pages.length - 1) {
        const newPage = currentPage + 1;
        setCurrentPage(newPage);
        sessionStorage.setItem('yimu-current-page', newPage.toString());
      } else if (e.key === 'ArrowUp' && currentPage > 0) {
        const newPage = currentPage - 1;
        setCurrentPage(newPage);
        sessionStorage.setItem('yimu-current-page', newPage.toString());
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentPage, pages.length]);

  // 开屏页面 - 手帐剪贴风格  
  const WelcomePage = useMemo(() => {
    const timestamp = new Date().toISOString();
    console.log(`WelcomePage: Memo creating component at ${timestamp}`);
    
    return (
      <section key="welcome-page-static" className="h-screen relative overflow-hidden" 
        style={UNIFIED_BACKGROUND}
      >
      
      {/* 纸质背景纹理 */}
      <div className="absolute inset-0 opacity-[0.03]" 
        style={PAPER_TEXTURE}
      />

             {/* 和纸胶带装饰 - 斜向条纹 */}
       <motion.div
         initial={{ opacity: 0, x: -100, rotate: -25 }}
         animate={{ opacity: 1, x: 0, rotate: -15 }}
         transition={{ duration: 1.2, delay: 0.5, ease: "easeOut" }}
         className="absolute top-32 -left-8 w-96 h-12 z-40"
                 style={{
           background: `
             linear-gradient(45deg, 
               rgba(254, 202, 202, 0.4) 0%, 
               rgba(252, 165, 165, 0.5) 25%, 
               rgba(254, 202, 202, 0.4) 50%, 
               rgba(252, 165, 165, 0.5) 75%, 
               rgba(254, 202, 202, 0.4) 100%
             ),
             repeating-linear-gradient(
               90deg,
               transparent,
               transparent 2px,
               rgba(255, 255, 255, 0.25) 2px,
               rgba(255, 255, 255, 0.25) 3px
             ),
             radial-gradient(circle at 15% 25%, rgba(255, 255, 255, 0.3) 1.5px, transparent 1.5px),
             radial-gradient(circle at 85% 75%, rgba(255, 255, 255, 0.25) 1px, transparent 1px)
           `,
           backgroundSize: '100% 100%, 100% 100%, 15px 15px, 12px 12px',
          clipPath: `polygon(
            0% 20%, 5% 0%, 95% 5%, 100% 30%, 
            98% 80%, 95% 100%, 8% 95%, 2% 70%
          )`,
          filter: 'drop-shadow(2px 4px 8px rgba(0,0,0,0.1))',
          borderRadius: '2px',
          transform: 'rotate(-15deg)'
        }}
      />

             {/* 和纸胶带装饰 - 右下角 */}
       <motion.div
         initial={{ opacity: 0, x: 100, rotate: 25 }}
         animate={{ opacity: 1, x: 0, rotate: 35 }}
         transition={{ duration: 1.2, delay: 0.8, ease: "easeOut" }}
         className="absolute bottom-40 -right-8 w-80 h-10 z-40"
                 style={{
           background: `
             linear-gradient(45deg, 
               rgba(196, 253, 191, 0.4) 0%, 
               rgba(134, 239, 172, 0.5) 25%, 
               rgba(196, 253, 191, 0.4) 50%, 
               rgba(134, 239, 172, 0.5) 75%, 
               rgba(196, 253, 191, 0.4) 100%
             ),
             repeating-linear-gradient(
               45deg,
               transparent,
               transparent 3px,
               rgba(255, 255, 255, 0.25) 3px,
               rgba(255, 255, 255, 0.25) 4px
             ),
             radial-gradient(circle at 25% 35%, rgba(255, 255, 255, 0.3) 1.5px, transparent 1.5px),
             radial-gradient(circle at 75% 65%, rgba(255, 255, 255, 0.25) 1px, transparent 1px)
           `,
           backgroundSize: '100% 100%, 100% 100%, 18px 18px, 14px 14px',
          clipPath: `polygon(
            2% 15%, 8% 0%, 98% 10%, 100% 40%, 
            95% 85%, 92% 100%, 5% 90%, 0% 60%
          )`,
          filter: 'drop-shadow(2px 4px 8px rgba(0,0,0,0.1))',
          borderRadius: '2px',
          transform: 'rotate(35deg)'
        }}
      />

      {/* 主标题卡片 - "一木记账" */}
      <motion.div
        initial={{ opacity: 0, y: -30, rotate: -5 }}
        animate={{ opacity: 1, y: 0, rotate: -3 }}
        transition={{ duration: 1, delay: 1, ease: "easeOut" }}
        className="absolute top-20 left-16 z-30"
      >
        <div 
          className="bg-white p-6 relative"
          style={{
            clipPath: `polygon(
              5% 0%, 95% 2%, 98% 85%, 92% 100%, 
              3% 98%, 0% 15%
            )`,
            filter: 'drop-shadow(4px 6px 12px rgba(0,0,0,0.15))',
            transform: 'rotate(-3deg)'
          }}
        >
          <h1 className="text-5xl font-bold text-gray-800 mb-2">
            一木记账
          </h1>
          <div className="w-16 h-1 bg-amber-400 rounded-full"></div>
        </div>
      </motion.div>

      {/* 年份大卡片 - 报纸剪贴风格 */}
      <motion.div
        initial={{ opacity: 0, scale: 0.8, rotate: 5 }}
        animate={{ opacity: 1, scale: 1, rotate: 2 }}
        transition={{ duration: 1.5, delay: 1.3, ease: "easeOut" }}
        className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-25"
      >
        <div 
          className="bg-gradient-to-br from-orange-50 to-amber-50 p-12 relative border border-orange-200"
          style={{
            clipPath: `polygon(
              2% 8%, 12% 0%, 88% 3%, 98% 12%, 
              95% 88%, 85% 98%, 15% 95%, 5% 85%
            )`,
            filter: 'drop-shadow(6px 8px 20px rgba(0,0,0,0.12))',
            transform: 'rotate(2deg)',
            backgroundImage: `
              linear-gradient(45deg, transparent 40%, rgba(251, 191, 36, 0.05) 45%, rgba(251, 191, 36, 0.05) 55%, transparent 60%),
              radial-gradient(circle at 30% 70%, rgba(254, 215, 170, 0.3) 0%, transparent 50%)
            `
          }}
        >
          <svg width="400" height="200" className="select-none" style={{ filter: 'drop-shadow(2px 2px 4px rgba(0,0,0,0.1))' }}>
            <defs>
              <linearGradient id="flowingGradient" x1="0%" y1="0%" x2="100%" y2="0%" gradientUnits="objectBoundingBox">
                <stop offset="0%" stopColor="#fbbf24">
                   <animate attributeName="stop-color"
                     values="#fbbf24;#f59e0b;#10b981;#84cc16;#fbbf24"
                     dur="8s"
                     repeatCount="indefinite" />
                 </stop>
                 <stop offset="33%" stopColor="#f59e0b">
                   <animate attributeName="stop-color"
                     values="#f59e0b;#10b981;#84cc16;#fbbf24;#f59e0b"
                     dur="8s"
                     repeatCount="indefinite" />
                 </stop>
                 <stop offset="66%" stopColor="#10b981">
                   <animate attributeName="stop-color"
                     values="#10b981;#84cc16;#fbbf24;#f59e0b;#10b981"
                     dur="8s"
                     repeatCount="indefinite" />
                 </stop>
                 <stop offset="100%" stopColor="#84cc16">
                   <animate attributeName="stop-color"
                     values="#84cc16;#fbbf24;#f59e0b;#10b981;#84cc16"
                     dur="8s"
                     repeatCount="indefinite" />
                 </stop>
              </linearGradient>
            </defs>
            <text x="50%" y="70%" textAnchor="middle" dominantBaseline="middle"
                  className="text-[8rem] font-bold leading-none"
                  fill="url(#flowingGradient)"
                  style={{ fontSize: '8rem', fontWeight: 'bold' }}>
              2024
            </text>
          </svg>
          
          {/* 报纸剪贴效果的边缘装饰 */}
          <div className="absolute -top-2 -left-2 w-8 h-8 bg-yellow-200 opacity-60 transform rotate-45"></div>
          <div className="absolute -bottom-3 -right-1 w-6 h-6 bg-orange-200 opacity-60 transform rotate-12"></div>
        </div>
      </motion.div>

             {/* "年度总结" 贴纸 */}
       <motion.div
         initial={{ opacity: 0, x: 50, rotate: -10 }}
         animate={{ opacity: 1, x: 0, rotate: -8 }}
         transition={{ duration: 1, delay: 1.6, ease: "easeOut" }}
         className="absolute top-16 right-48 z-30"
      >
        <div 
          className="bg-gradient-to-br from-pink-100 to-rose-200 px-6 py-4 relative"
          style={{
            clipPath: `polygon(
              8% 5%, 95% 0%, 100% 78%, 92% 95%, 
              5% 100%, 0% 22%
            )`,
            filter: 'drop-shadow(3px 5px 10px rgba(0,0,0,0.12))',
            transform: 'rotate(-8deg)',
            borderRadius: '8px'
          }}
        >
          <h2 className="text-2xl font-semibold text-gray-700">
            年度总结
          </h2>
          <div className="absolute top-1 right-1 w-3 h-3 bg-white rounded-full opacity-80"></div>
        </div>
      </motion.div>

             {/* 装饰贴纸1 - 圆形 */}
       <motion.div
         initial={{ opacity: 0, scale: 0.5, rotate: 45 }}
         animate={{ opacity: 1, scale: 1, rotate: 25 }}
         transition={{ duration: 0.8, delay: 2, ease: "easeOut" }}
         className="absolute top-80 right-60 z-15"
      >
        <div className="w-16 h-16 bg-gradient-to-br from-blue-200 to-indigo-300 rounded-full relative"
          style={{
            filter: 'drop-shadow(2px 3px 6px rgba(0,0,0,0.1))',
            transform: 'rotate(25deg)'
          }}>
          <div className="absolute inset-2 bg-white rounded-full opacity-40"></div>
          <div className="absolute top-2 left-2 w-2 h-2 bg-white rounded-full opacity-80"></div>
        </div>
      </motion.div>

             {/* 装饰贴纸2 - 心形 */}
       <motion.div
         initial={{ opacity: 0, scale: 0.3, rotate: -30 }}
         animate={{ opacity: 1, scale: 1, rotate: -15 }}
         transition={{ duration: 0.8, delay: 2.3, ease: "easeOut" }}
         className="absolute top-72 left-60 z-15"
      >
        <div className="w-12 h-12 relative"
          style={{
            filter: 'drop-shadow(2px 3px 6px rgba(0,0,0,0.1))',
            transform: 'rotate(-15deg)'
          }}>
          <div className="w-full h-full bg-gradient-to-br from-yellow-200 to-amber-300"
            style={{
              clipPath: `polygon(
                50% 85%, 25% 60%, 15% 40%, 25% 20%, 
                45% 15%, 50% 25%, 55% 15%, 75% 20%, 
                85% 40%, 75% 60%
              )`
            }}>
          </div>
        </div>
      </motion.div>

             {/* 装饰贴纸3 - 星形 */}
       <motion.div
         initial={{ opacity: 0, scale: 0.4, rotate: 60 }}
         animate={{ opacity: 1, scale: 1, rotate: 45 }}
         transition={{ duration: 0.8, delay: 2.6, ease: "easeOut" }}
         className="absolute bottom-80 right-60 z-15"
      >
        <div className="w-10 h-10 bg-gradient-to-br from-green-200 to-emerald-300 relative"
          style={{
            clipPath: `polygon(
              50% 0%, 61% 35%, 98% 35%, 68% 57%, 
              79% 91%, 50% 70%, 21% 91%, 32% 57%, 
              2% 35%, 39% 35%
            )`,
            filter: 'drop-shadow(2px 3px 6px rgba(0,0,0,0.1))',
            transform: 'rotate(45deg)'
          }}>
        </div>
      </motion.div>

             {/* 日常碎碎念卡片1 */}
       <motion.div
         initial={{ opacity: 0, x: -30, rotate: -8 }}
         animate={{ opacity: 1, x: 0, rotate: -5 }}
         transition={{ duration: 0.8, delay: 1.8, ease: "easeOut" }}
         className="absolute top-72 left-12 z-35"
       >
         <div 
           className="bg-yellow-100 border-l-4 border-yellow-300 p-5 relative w-56"
           style={{
             clipPath: `polygon(
               5% 3%, 95% 0%, 98% 92%, 90% 100%, 
               2% 97%, 0% 8%
             )`,
             filter: 'drop-shadow(2px 3px 6px rgba(0,0,0,0.1))',
             transform: 'rotate(-5deg)'
           }}
         >
           <p className="text-base text-gray-700 leading-relaxed">
             又是小小的冲动消费<img src="/SavedStickers/✏_AgADSUcAAqiycUo.webp" alt="📝" className="w-4 h-4 inline-block ml-1" /><br/>
             计划总是赶不上变化<br/>
             明天要更理性一些！<br/>
             <span className="text-xs text-gray-500">理财路上的小插曲</span>
           </p>
         </div>
         
         {/* 胶带装饰 */}
         <motion.div
           initial={{ opacity: 0, rotate: 15 }}
           animate={{ opacity: 1, rotate: 10 }}
           transition={{ duration: 0.6, delay: 2.2, ease: "easeOut" }}
           className="absolute -top-2 right-3 w-20 h-7 z-50"
           style={{
             background: `
               linear-gradient(45deg, 
                 rgba(251, 146, 60, 0.4) 0%, 
                 rgba(249, 115, 22, 0.5) 50%, 
                 rgba(251, 146, 60, 0.4) 100%
               ),
               repeating-linear-gradient(
                 30deg,
                 transparent,
                 transparent 1.5px,
                 rgba(255, 255, 255, 0.3) 1.5px,
                 rgba(255, 255, 255, 0.3) 2.5px
               )
             `,
             clipPath: `polygon(
               5% 15%, 95% 8%, 98% 85%, 92% 95%, 
               8% 88%, 2% 25%
             )`,
             filter: 'drop-shadow(1px 2px 4px rgba(0,0,0,0.15))',
             transform: 'rotate(10deg)'
           }}
         />
       </motion.div>

       {/* 日常碎碎念卡片2 */}
       <motion.div
         initial={{ opacity: 0, y: 20, rotate: 10 }}
         animate={{ opacity: 1, y: 0, rotate: 7 }}
         transition={{ duration: 0.8, delay: 2.1, ease: "easeOut" }}
         className="absolute top-32 right-12 z-35"
       >
         <div 
           className="bg-blue-50 border border-blue-200 p-5 relative w-52"
           style={{
             clipPath: `polygon(
               8% 0%, 92% 5%, 100% 88%, 85% 100%, 
               0% 95%, 3% 12%
             )`,
             filter: 'drop-shadow(2px 3px 6px rgba(0,0,0,0.1))',
             transform: 'rotate(7deg)'
           }}
         >
           <p className="text-base text-gray-700 leading-relaxed">
             收入到账啦<img src="/SavedStickers/🥳_AgADoEcAAr8SkEs.webp" alt="🎉" className="w-4 h-4 inline-block ml-1" /><br/>
             终于有了盈余<br/>
             这个月收支平衡！<br/>
             <span className="text-xs text-gray-500">财务状况在好转</span>
           </p>
         </div>
         
         {/* 长胶带装饰 */}
         <motion.div
           initial={{ opacity: 0, rotate: -20 }}
           animate={{ opacity: 1, rotate: -15 }}
           transition={{ duration: 0.6, delay: 2.5, ease: "easeOut" }}
           className="absolute top-1 left-2 w-24 h-6 z-50"
           style={{
             background: `
               linear-gradient(45deg, 
                 rgba(96, 165, 250, 0.4) 0%, 
                 rgba(59, 130, 246, 0.5) 50%, 
                 rgba(96, 165, 250, 0.4) 100%
               ),
               repeating-linear-gradient(
                 60deg,
                 transparent,
                 transparent 2px,
                 rgba(255, 255, 255, 0.3) 2px,
                 rgba(255, 255, 255, 0.3) 3px
               )
             `,
             clipPath: `polygon(
               5% 15%, 95% 8%, 98% 85%, 92% 95%, 
               3% 88%, 0% 25%
             )`,
             filter: 'drop-shadow(1px 2px 4px rgba(0,0,0,0.15))',
             transform: 'rotate(-15deg)'
           }}
         />
       </motion.div>

       {/* 日常碎碎念卡片3 */}
       <motion.div
         initial={{ opacity: 0, x: 30, rotate: -12 }}
         animate={{ opacity: 1, x: 0, rotate: -8 }}
         transition={{ duration: 0.8, delay: 2.4, ease: "easeOut" }}
         className="absolute top-1/3 left-1/3 z-35"
       >
         <div 
           className="bg-green-50 border-r-4 border-green-300 p-5 relative w-60"
           style={{
             clipPath: `polygon(
               3% 5%, 97% 2%, 95% 85%, 88% 98%, 
               5% 100%, 0% 15%
             )`,
             filter: 'drop-shadow(2px 3px 6px rgba(0,0,0,0.1))',
             transform: 'rotate(-8deg)'
           }}
         >
           <p className="text-base text-gray-700 leading-relaxed">
             理财小目标<img src="/SavedStickers/💰_AgADClAAAmeMcEs.webp" alt="💰" className="w-4 h-4 inline-block ml-1" /><br/>
             这个月要控制支出<br/>
             培养好习惯！<br/>
             <span className="text-xs text-gray-500">目标：支出优化20%</span>
           </p>
         </div>
         
         {/* 胶带装饰 */}
         <motion.div
           initial={{ opacity: 0, rotate: 25 }}
           animate={{ opacity: 1, rotate: 20 }}
           transition={{ duration: 0.6, delay: 2.8, ease: "easeOut" }}
           className="absolute -top-1 right-4 w-20 h-7 z-50"
           style={{
             background: `
               linear-gradient(45deg, 
                 rgba(34, 197, 94, 0.4) 0%, 
                 rgba(22, 163, 74, 0.5) 50%, 
                 rgba(34, 197, 94, 0.4) 100%
               ),
               repeating-linear-gradient(
                 -30deg,
                 transparent,
                 transparent 1.8px,
                 rgba(255, 255, 255, 0.25) 1.8px,
                 rgba(255, 255, 255, 0.25) 2.8px
               )
             `,
             clipPath: `polygon(
               2% 10%, 98% 5%, 95% 90%, 85% 95%, 
               5% 88%, 0% 20%
             )`,
             filter: 'drop-shadow(1px 2px 4px rgba(0,0,0,0.15))',
             transform: 'rotate(20deg)',
             width: '70px'
           }}
         />
       </motion.div>

       {/* 日常碎碎念卡片4 */}
       <motion.div
         initial={{ opacity: 0, y: -20, rotate: 15 }}
         animate={{ opacity: 1, y: 0, rotate: 12 }}
         transition={{ duration: 0.8, delay: 2.7, ease: "easeOut" }}
         className="absolute bottom-40 right-16 z-35"
       >
         <div 
           className="bg-pink-50 border border-pink-200 p-5 relative w-56"
           style={{
             clipPath: `polygon(
               10% 2%, 90% 8%, 98% 90%, 80% 95%, 
               2% 88%, 5% 20%
             )`,
             filter: 'drop-shadow(2px 3px 6px rgba(0,0,0,0.1))',
             transform: 'rotate(12deg)'
           }}
         >
           <p className="text-base text-gray-700 leading-relaxed">
             记账让我发现<img src="/SavedStickers/💡_AgAD00wAAovVUEo.webp" alt="💡" className="w-4 h-4 inline-block mr-1" /><br/>
             钱都花在哪里了<img src="/SavedStickers/💰_AgADClAAAmeMcEs.webp" alt="💸" className="w-4 h-4 inline-block ml-1" /><br/>
             支出分布很有趣！<br/>
             <span className="text-xs text-gray-500">数据分析的意外收获</span>
           </p>
         </div>
         
         {/* 胶带装饰 */}
         <motion.div
           initial={{ opacity: 0, rotate: -25 }}
           animate={{ opacity: 1, rotate: -18 }}
           transition={{ duration: 0.6, delay: 3.1, ease: "easeOut" }}
           className="absolute top-2 left-3 w-20 h-6 z-50"
           style={{
             background: `
               linear-gradient(45deg, 
                 rgba(244, 114, 182, 0.4) 0%, 
                 rgba(236, 72, 153, 0.5) 50%, 
                 rgba(244, 114, 182, 0.4) 100%
               ),
               repeating-linear-gradient(
                 75deg,
                 transparent,
                 transparent 2px,
                 rgba(255, 255, 255, 0.25) 2px,
                 rgba(255, 255, 255, 0.25) 3px
               )
             `,
             clipPath: `polygon(
               5% 18%, 95% 12%, 92% 82%, 88% 92%, 
               8% 85%, 2% 28%
             )`,
             filter: 'drop-shadow(1px 2px 4px rgba(0,0,0,0.15))',
             transform: 'rotate(-18deg)'
           }}
         />
       </motion.div>

       {/* 日常碎碎念卡片5 */}
       <motion.div
         initial={{ opacity: 0, x: -40, rotate: -18 }}
         animate={{ opacity: 1, x: 0, rotate: -12 }}
         transition={{ duration: 0.8, delay: 3.0, ease: "easeOut" }}
         className="absolute bottom-16 left-16 z-35"
       >
         <div 
           className="bg-purple-50 border border-purple-200 p-5 relative w-54"
           style={{
             clipPath: `polygon(
               6% 8%, 94% 3%, 97% 88%, 85% 95%, 
               3% 92%, 0% 18%
             )`,
             filter: 'drop-shadow(2px 3px 6px rgba(0,0,0,0.1))',
             transform: 'rotate(-12deg)'
           }}
         >
           <p className="text-base text-gray-700 leading-relaxed">
             开始学习理财<img src="/SavedStickers/⬆_AgADjkoAAnEqcEs.webp" alt="📈" className="w-4 h-4 inline-block ml-1" /><br/>
             每一分钱都有意义<br/>
             这是个好开始！<br/>
             <span className="text-xs text-gray-500">财富自由的第一步</span>
           </p>
         </div>
         
         {/* 胶带装饰 */}
         <motion.div
           initial={{ opacity: 0, rotate: 30 }}
           animate={{ opacity: 1, rotate: 25 }}
           transition={{ duration: 0.6, delay: 3.4, ease: "easeOut" }}
           className="absolute top-1 right-2 w-20 h-7 z-50"
           style={{
             background: `
               linear-gradient(45deg, 
                 rgba(147, 51, 234, 0.4) 0%, 
                 rgba(126, 34, 206, 0.5) 50%, 
                 rgba(147, 51, 234, 0.4) 100%
               ),
               repeating-linear-gradient(
                 -45deg,
                 transparent,
                 transparent 2px,
                 rgba(255, 255, 255, 0.25) 2px,
                 rgba(255, 255, 255, 0.25) 3px
               )
             `,
             clipPath: `polygon(
               8% 12%, 92% 5%, 95% 88%, 88% 92%, 
               5% 85%, 2% 22%
             )`,
             filter: 'drop-shadow(1px 2px 4px rgba(0,0,0,0.15))',
             transform: 'rotate(25deg)'
           }}
         />
       </motion.div>

       {/* 贴纸装饰 - 左下角 */}
       <motion.div
         initial={{ opacity: 0, scale: 0, rotate: -15 }}
         animate={{ opacity: 1, scale: 1, rotate: -10 }}
         transition={{ duration: 0.8, delay: 2.2, ease: "easeOut" }}
         className="absolute bottom-8 z-40"
         style={{ left: 'calc(2rem + 3 * 160px - 80px)' }}
         onAnimationComplete={() => console.log('左下角贴纸渲染完成')}
       >
         <img 
           src="/SavedStickers/🥳_AgADoEcAAr8SkEs.webp" 
           alt="庆祝贴纸"
           className="w-40 h-40 object-contain"
           onLoad={(e) => {
             const img = e.target as HTMLImageElement;
             console.log('左下角贴纸加载完成:', img.naturalWidth, 'x', img.naturalHeight);
           }}
           style={{
             transform: 'rotate(-10deg)',
             maxWidth: '160px',
             maxHeight: '160px'
           }}
         />
       </motion.div>

       {/* 贴纸装饰 - 上方 */}
       <motion.div
         initial={{ opacity: 0, scale: 0, rotate: 20 }}
         animate={{ opacity: 1, scale: 1, rotate: 15 }}
         transition={{ duration: 0.8, delay: 2.5, ease: "easeOut" }}
         className="absolute top-12 left-1/2 transform -translate-x-1/2 z-40"
         onAnimationComplete={() => console.log('上方贴纸渲染完成')}
       >
         <img 
           src="/SavedStickers/👍_AgADsk0AAtLogUg.webp" 
           alt="点赞贴纸"
           className="w-40 h-40 object-contain"
           onLoad={(e) => {
             const img = e.target as HTMLImageElement;
             console.log('上方贴纸加载完成:', img.naturalWidth, 'x', img.naturalHeight);
           }}
           style={{
             transform: 'rotate(15deg)',
             maxWidth: '160px',
             maxHeight: '160px'
           }}
         />
       </motion.div>

       {/* 贴纸装饰 - 右边中间位置 */}
       <motion.div
         initial={{ opacity: 0, scale: 0, rotate: 25 }}
         animate={{ opacity: 1, scale: 1, rotate: 20 }}
         transition={{ duration: 0.8, delay: 2.8, ease: "easeOut" }}
         className="absolute top-1/2 right-8 transform -translate-y-1/2 z-40"
         onAnimationComplete={() => console.log('右边贴纸渲染完成')}
       >
         <img 
           src="/SavedStickers/⭐_AgADrUUAAt3FKEs.webp" 
           alt="星星贴纸"
           className="w-40 h-40 object-contain"
           onLoad={(e) => {
             const img = e.target as HTMLImageElement;
             console.log('右边贴纸加载完成:', img.naturalWidth, 'x', img.naturalHeight);
           }}
           style={{
             transform: 'rotate(20deg)',
             maxWidth: '160px',
             maxHeight: '160px'
           }}
         />
       </motion.div>

       {/* 随机散落的小圆点装饰 */}
       {[...Array(6)].map((_, i) => (
         <motion.div
           key={i}
           initial={{ opacity: 0, scale: 0 }}
           animate={{ opacity: 0.4, scale: 1 }}
           transition={{ 
             duration: 0.5, 
             delay: 2.8 + i * 0.1, 
             ease: "easeOut" 
           }}
           className="absolute w-1.5 h-1.5 rounded-full z-10"
           style={{
             left: `${30 + Math.random() * 40}%`,
             top: `${30 + Math.random() * 40}%`,
             backgroundColor: [
               '#fbbf24', '#fb923c', '#f87171', 
               '#a78bfa', '#60a5fa', '#34d399'
             ][i % 6],
             filter: 'drop-shadow(1px 1px 2px rgba(0,0,0,0.1))'
           }}
         />
       ))}

      {/* 交互提示 - 手写风格 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1, delay: 2.5, ease: "easeOut" }}
        className="absolute bottom-16 left-1/2 transform -translate-x-1/2 z-30"
      >
        <motion.div
          animate={{
            y: [0, -5, 0],
            opacity: [0.7, 1, 0.7]
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        >
          <p className="text-gray-600 text-lg text-center"
            style={{ 
              transform: 'rotate(-1deg)'
            }}>
            滚动鼠标，探索你的财务故事
          </p>
        </motion.div>
      </motion.div>

    </section>
    );
  }, []);

  // 渲染当前页面
  const renderCurrentPage = () => {
    switch (pages[currentPage]) {
      case 'welcome':
        return WelcomePage;
      case 'financial-overview':
        return <FinancialOverview />;
      default:
        return WelcomePage;
    }
  };
  
  return (
    <div 
      className="relative w-full h-screen overflow-hidden"
      onWheel={handleWheel}
    >
      <AnimatePresence mode="wait">
        <motion.div
          key={currentPage}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.6, ease: "easeInOut" }}
          className="w-full h-full"
        >
          {renderCurrentPage()}
        </motion.div>
      </AnimatePresence>
    </div>
  );
};

export default AnnualSummary;