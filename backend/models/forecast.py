from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from . import Base


class Forecast(Base):
    """
    销量预测模型
    """
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(CHAR(36), ForeignKey("products.id"), nullable=False)
    forecast_date = Column(Date, nullable=False, index=True)
    predicted_sales = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    adjusted_value = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关联关系
    adjustments = relationship("ForecastAdjustment", back_populates="forecast")


class ForecastAdjustment(Base):
    """
    预测调整记录模型
    """
    __tablename__ = "forecast_adjustments"

    id = Column(Integer, primary_key=True, index=True)
    forecast_id = Column(Integer, ForeignKey("forecasts.id"), nullable=False)
    adjusted_value = Column(Float, nullable=False)
    reason = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联关系
    forecast = relationship("Forecast", back_populates="adjustments")