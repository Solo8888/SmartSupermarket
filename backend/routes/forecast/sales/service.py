from datetime import date, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from models import Forecast, ForecastAdjustment, Product


def generate_forecast_data(db: Session, product_id: str, forecast_period: str, start_date: date) -> List[Forecast]:
    """
    生成模拟预测数据
    
    Args:
        db: 数据库会话
        product_id: 商品ID
        forecast_period: 预测周期 (short/medium/long)
        start_date: 开始日期
    
    Returns:
        预测数据列表
    """
    # 验证商品是否存在
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return []
    
    # 根据预测周期确定预测天数
    period_days = {
        'short': 7,    # 短期：7天
        'medium': 30,  # 中期：30天
        'long': 90     # 长期：90天
    }
    days = period_days.get(forecast_period, 7)
    
    # 生成预测数据
    forecasts = []
    for i in range(days):
        forecast_date = start_date + timedelta(days=i)
        # 模拟预测销量（基于商品价格的简单计算）
        base_sales = 100 + (i % 7) * 10  # 基础销量
        # 模拟置信度
        confidence = 0.8 + (i % 10) * 0.02
        if confidence > 0.95:
            confidence = 0.95
        
        # 检查是否已存在该日期的预测
        existing_forecast = db.query(Forecast).filter(
            Forecast.product_id == product_id,
            Forecast.forecast_date == forecast_date
        ).first()
        
        if existing_forecast:
            forecasts.append(existing_forecast)
        else:
            # 创建新的预测
            forecast = Forecast(
                product_id=product_id,
                forecast_date=forecast_date,
                predicted_sales=base_sales,
                confidence=confidence
            )
            db.add(forecast)
            forecasts.append(forecast)
    
    db.commit()
    return forecasts


def get_forecasts(db: Session, product_id: str, forecast_period: str, start_date: date) -> List[Forecast]:
    """
    获取销量预测
    
    Args:
        db: 数据库会话
        product_id: 商品ID
        forecast_period: 预测周期
        start_date: 开始日期
    
    Returns:
        预测数据列表
    """
    # 生成预测数据
    forecasts = generate_forecast_data(db, product_id, forecast_period, start_date)
    return forecasts


def adjust_forecast(db: Session, forecast_id: int, adjusted_value: float, reason: str) -> Optional[Forecast]:
    """
    调整预测结果
    
    Args:
        db: 数据库会话
        forecast_id: 预测ID
        adjusted_value: 调整后的值
        reason: 调整原因
    
    Returns:
        调整后的预测对象
    """
    # 查找预测
    forecast = db.query(Forecast).filter(Forecast.id == forecast_id).first()
    if not forecast:
        return None
    
    # 更新调整值
    forecast.adjusted_value = adjusted_value
    
    # 创建调整记录
    adjustment = ForecastAdjustment(
        forecast_id=forecast_id,
        adjusted_value=adjusted_value,
        reason=reason
    )
    db.add(adjustment)
    
    db.commit()
    db.refresh(forecast)
    return forecast


def get_forecasts_for_export(db: Session, product_id: Optional[str] = None, 
                           start_date: Optional[date] = None, 
                           end_date: Optional[date] = None) -> List[Forecast]:
    """
    获取用于导出的预测数据
    
    Args:
        db: 数据库会话
        product_id: 商品ID（可选）
        start_date: 开始日期（可选）
        end_date: 结束日期（可选）
    
    Returns:
        预测数据列表
    """
    query = db.query(Forecast)
    
    if product_id:
        query = query.filter(Forecast.product_id == product_id)
    
    if start_date:
        query = query.filter(Forecast.forecast_date >= start_date)
    
    if end_date:
        query = query.filter(Forecast.forecast_date <= end_date)
    
    return query.all()