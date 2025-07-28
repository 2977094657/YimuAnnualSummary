# -*- coding: utf-8 -*-
"""
FastAPI应用主文件
提供一木记账数据分析的RESTful API接口
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
from loguru import logger
import os
import shutil
from pathlib import Path

from .data_converter import YimuDataConverter
from .data_analyzer import YimuDataAnalyzer

# 配置日志
logger.add("logs/yimu_api.log", rotation="1 day", retention="30 days", level="INFO")

# 应用生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动和关闭时的生命周期管理"""
    # 启动时执行
    logger.info("应用启动中...")
    
    # 初始化组件
    global converter, analyzer
    converter = YimuDataConverter()
    analyzer = YimuDataAnalyzer()
    
    # 检查是否已存在数据库
    if os.path.exists(converter.db_path):
        logger.info(f"数据库已存在: {converter.db_path}，跳过初始化")
        stats = converter.get_database_stats()
        logger.info(f"数据库统计: {stats['total_records']} 条记录")
    else:
        logger.info("数据库不存在，开始自动检测账单文件并初始化...")
        try:
            # 尝试自动检测并转换最新账单文件
            latest_file = converter.get_latest_bill_file()
            if latest_file:
                logger.info(f"检测到账单文件: {latest_file}")
                success = converter.convert_excel_to_sqlite()
                if success:
                    stats = converter.get_database_stats()
                    logger.info(f"自动初始化成功: {stats['total_records']} 条记录")
                else:
                    logger.warning("自动初始化失败")
            else:
                logger.info("未检测到账单文件，等待手动上传")
        except Exception as e:
            logger.error(f"自动初始化过程中发生错误: {str(e)}")
    
    logger.info("应用启动完成")
    
    yield
    
    # 关闭时执行
    logger.info("应用关闭中...")

# 创建FastAPI应用
app = FastAPI(
    title="一木记账年度总结分析API",
    description="提供一木记账数据的转换、分析和年度总结功能",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求模型
class ConvertRequest(BaseModel):
    excel_path: Optional[str] = None  # 如果为None则自动检测最新账单文件
    
class AnalysisRequest(BaseModel):
    year: Optional[int] = None
    transaction_type: Optional[str] = "支出"
    limit: Optional[int] = 20

# 全局变量声明（在lifespan中初始化）
converter = None
analyzer = None

@app.get("/", summary="API根路径", description="返回API基本信息")
async def root():
    """API根路径"""
    return {
        "message": "一木记账年度总结分析API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "运行中"
    }

@app.post("/api/convert", summary="转换Excel文件", description="将一木记账的Excel文件转换为SQLite数据库，支持自动检测最新账单")
async def convert_excel(request: ConvertRequest):
    """转换Excel文件为SQLite数据库
    
    Args:
        request: 包含Excel文件路径的请求，如果excel_path为None则自动检测最新账单
        
    Returns:
        转换结果和数据库统计信息
    """
    try:
        if request.excel_path:
            logger.info(f"开始转换指定Excel文件: {request.excel_path}")
            # 检查文件是否存在
            if not os.path.exists(request.excel_path):
                raise HTTPException(status_code=404, detail=f"Excel文件不存在: {request.excel_path}")
        else:
            logger.info("开始自动检测并转换最新账单文件")
            
        # 执行转换
        success = converter.convert_excel_to_sqlite(request.excel_path)
        
        if not success:
            raise HTTPException(status_code=500, detail="Excel文件转换失败")
            
        # 获取数据库统计信息
        stats = converter.get_database_stats()
        
        return {
            "success": True,
            "message": "Excel文件转换成功",
            "database_stats": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"转换Excel文件时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")

@app.post("/api/upload", summary="上传Excel文件", description="上传一木记账的Excel文件并自动转换")
async def upload_excel(file: UploadFile = File(...)):
    """上传Excel文件并自动转换
    
    Args:
        file: 上传的Excel文件
        
    Returns:
        上传和转换结果
    """
    try:
        # 检查文件类型
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="只支持Excel文件(.xlsx, .xls)")
            
        # 确保上传目录存在
        upload_dir = Path("data")
        upload_dir.mkdir(exist_ok=True)
        
        # 保存上传的文件
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"文件上传成功: {file_path}")
        
        # 自动转换
        success = converter.convert_excel_to_sqlite(str(file_path))
        
        if not success:
            raise HTTPException(status_code=500, detail="文件转换失败")
            
        # 获取数据库统计信息
        stats = converter.get_database_stats()
        
        return {
            "success": True,
            "message": "文件上传并转换成功",
            "filename": file.filename,
            "file_path": str(file_path),
            "database_stats": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传文件时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@app.get("/api/stats", summary="获取数据库统计", description="获取当前数据库的基本统计信息")
async def get_database_stats():
    """获取数据库统计信息"""
    try:
        stats = converter.get_database_stats()
        return stats
    except Exception as e:
        logger.error(f"获取数据库统计信息时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

@app.post("/api/analysis/monthly", summary="月度趋势分析", description="获取指定年份的月度收支趋势数据")
async def get_monthly_analysis(request: AnalysisRequest):
    """获取月度趋势分析
    
    Args:
        request: 分析请求参数
        
    Returns:
        月度趋势分析数据
    """
    try:
        result = analyzer.get_monthly_trend(request.year)
        return result
    except Exception as e:
        logger.error(f"获取月度分析数据时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@app.post("/api/analysis/category", summary="分类分析", description="获取收入或支出的分类统计分析")
async def get_category_analysis(request: AnalysisRequest):
    """获取分类分析
    
    Args:
        request: 分析请求参数
        
    Returns:
        分类分析数据
    """
    try:
        result = analyzer.get_category_analysis(request.transaction_type, request.year)
        return result
    except Exception as e:
        logger.error(f"获取分类分析数据时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@app.post("/api/analysis/account", summary="账户分析", description="获取各账户的使用情况分析")
async def get_account_analysis(request: AnalysisRequest):
    """获取账户分析
    
    Args:
        request: 分析请求参数
        
    Returns:
        账户分析数据
    """
    try:
        result = analyzer.get_account_analysis(request.year)
        return result
    except Exception as e:
        logger.error(f"获取账户分析数据时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@app.post("/api/analysis/location", summary="地点分析", description="获取消费地点的统计分析")
async def get_location_analysis(request: AnalysisRequest):
    """获取地点分析
    
    Args:
        request: 分析请求参数
        
    Returns:
        地点分析数据
    """
    try:
        result = analyzer.get_location_analysis(request.year, request.limit)
        return result
    except Exception as e:
        logger.error(f"获取地点分析数据时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@app.post("/api/analysis/time-pattern", summary="时间模式分析", description="获取消费时间模式的统计分析")
async def get_time_pattern_analysis(request: AnalysisRequest):
    """获取时间模式分析
    
    Args:
        request: 分析请求参数
        
    Returns:
        时间模式分析数据
    """
    try:
        result = analyzer.get_time_pattern_analysis(request.year)
        return result
    except Exception as e:
        logger.error(f"获取时间模式分析数据时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@app.get("/api/annual-summary", summary="年度总结", description="获取指定年份的完整年度总结数据")
async def get_annual_summary(year: Optional[int] = None):
    """获取年度总结数据
    
    Args:
        year: 年份，默认为当前年份
        
    Returns:
        年度总结数据
    """
    try:
        from datetime import datetime
        if year is None:
            year = datetime.now().year
            
        result = analyzer.get_annual_summary(year)
        return result
        
    except Exception as e:
        logger.error(f"获取年度总结数据时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取年度总结数据失败: {str(e)}")

@app.get("/api/daily-data", summary="每日数据", description="获取指定年份的每日收支数据，用于热力图显示")
async def get_daily_data(year: Optional[int] = None):
    """获取每日数据
    
    Args:
        year: 年份，默认为当前年份
        
    Returns:
        每日收支数据
    """
    try:
        from datetime import datetime
        if year is None:
            year = datetime.now().year
            
        result = analyzer.get_daily_data(year)
        return result
        
    except Exception as e:
        logger.error(f"获取每日数据时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取每日数据失败: {str(e)}")

@app.get("/api/bill-folders", summary="获取账单文件夹列表", description="获取项目中可用的账单文件夹列表")
async def get_bill_folders():
    """获取可用的账单文件夹列表"""
    try:
        bill_folders = converter.scan_bill_folders()
        result = []
        
        for folder_name, excel_path, timestamp in bill_folders:
            result.append({
                "folder_name": folder_name,
                "excel_path": excel_path,
                "timestamp": timestamp.isoformat(),
                "is_latest": (bill_folders[0][0] == folder_name) if bill_folders else False
            })
            
        return {
            "success": True,
            "bill_folders": result,
            "total": len(result),
            "latest": result[0] if result else None
        }
    except Exception as e:
        logger.error(f"获取账单文件夹列表时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取账单文件夹列表失败: {str(e)}")

@app.get("/api/available-years", summary="获取可用年份", description="获取数据库中存在交易数据的所有年份")
async def get_available_years():
    """获取可用年份列表

    Returns:
        可用年份列表，按降序排列
    """
    try:
        years = analyzer.get_available_years()
        return {
            "success": True,
            "years": years,
            "total": len(years),
            "latest": years[0] if years else None,
            "earliest": years[-1] if years else None
        }
    except Exception as e:
        logger.error(f"获取可用年份时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取可用年份失败: {str(e)}")

@app.get("/api/financial-overview", summary="年度财务总览", description="获取年度财务总览数据")
async def get_financial_overview(year: Optional[int] = None):
    """获取年度财务总览数据

    Args:
        year: 指定年份，默认为当前年份

    Returns:
        年度财务总览数据
    """
    try:
        result = analyzer.get_financial_overview(year)
        return result
    except Exception as e:
        logger.error(f"获取年度财务总览数据时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取财务总览失败: {str(e)}")

@app.get("/api/health", summary="健康检查", description="检查API服务状态")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "message": "API服务运行正常",
        "database_exists": os.path.exists(converter.db_path)
    }

# 异常处理
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "请求的资源不存在"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)