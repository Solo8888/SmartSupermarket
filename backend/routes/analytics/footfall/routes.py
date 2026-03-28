# Footfall analytics routes
# Provides API endpoints for footfall analysis

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import Response, StreamingResponse
from typing import Optional, IO
import io
import csv
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from .schemas import TimeDistributionResponse, TimeDistributionQuery, ExportRequest
from .service import TimeDistributionService, ExportService
from core.permitions import require_role

footfall_router = APIRouter(
    prefix="",
    tags=["footfall"],
    responses={404: {"description": "Not found"}},
)

time_distribution_service = TimeDistributionService()
export_service = ExportService()


@footfall_router.get("/time-distribution", response_model=TimeDistributionResponse)
async def get_time_distribution(
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    store_id: Optional[str] = Query(None, description="门店ID（可选）"),
    current_user = Depends(require_role(["operations_manager"], mode="in"))
):
    """获取时段客流分布
    
    - **start_date**: 开始日期 (YYYY-MM-DD)
    - **end_date**: 结束日期 (YYYY-MM-DD)
    - **store_id**: 门店ID（可选）
    """
    # 权限检查由require_role依赖处理
    
    try:
        # 验证时间范围
        from datetime import datetime
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        if start > end:
            raise HTTPException(status_code=400, detail="开始日期不能晚于结束日期")
        
        # 获取时间分布数据
        data = time_distribution_service.get_time_distribution(start_date, end_date, store_id)
        
        # 构建响应
        response = TimeDistributionResponse(
            data=data
        )
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取时段客流分布失败: {str(e)}")


@footfall_router.post("/export")
async def export_footfall_report(
    request: ExportRequest,
    current_user = Depends(require_role(["operations_manager"], mode="in"))
):
    """导出客流分析报告
    
    - **start_date**: 开始日期 (YYYY-MM-DD)
    - **end_date**: 结束日期 (YYYY-MM-DD)
    - **store_id**: 门店ID（可选）
    - **format**: 导出格式 (pdf/excel)
    """
    # 权限检查由require_role依赖处理
    
    try:
        # 验证时间范围
        from datetime import datetime
        start = datetime.strptime(request.start_date, "%Y-%m-%d")
        end = datetime.strptime(request.end_date, "%Y-%m-%d")
        
        if start > end:
            raise HTTPException(status_code=400, detail="开始日期不能晚于结束日期")
        
        # 验证导出格式
        if request.format not in ["pdf", "excel"]:
            raise HTTPException(status_code=400, detail="不支持的导出格式，支持的格式：pdf, excel")
        
        # 获取客流数据
        raw_data, hourly_counts = export_service.get_footfall_data(
            request.start_date, 
            request.end_date, 
            request.store_id
        )
        
        # 根据格式生成文件
        if request.format == "excel":
            # 生成CSV文件（作为Excel的替代）
            output = io.StringIO()
            writer = csv.writer(output)
            
            # 写入表头
            writer.writerow(["小时", "客流量"])
            
            # 写入数据
            for hour, count in sorted(hourly_counts.items()):
                writer.writerow([hour, count])
            
            output.seek(0)
            
            # 构建响应
            return Response(
                content=output.getvalue(),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=footfall_report_{request.start_date}_{request.end_date}.csv"
                }
            )
        elif request.format == "pdf":
            # 使用reportlab生成真正的PDF文件，支持中文
            from reportlab.pdfbase.cidfonts import UnicodeCIDFont
            
            # 注册中文字体
            try:
                pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
                chinese_font = 'STSong-Light'
            except:
                # 如果STSong-Light不可用，尝试使用其他中文字体
                try:
                    pdfmetrics.registerFont(UnicodeCIDFont('AdobeSongStd-Light'))
                    chinese_font = 'AdobeSongStd-Light'
                except:
                    # 如果都不可用，使用默认字体（中文会显示为方框）
                    chinese_font = 'Helvetica'
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            
            # 创建样式
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontName=chinese_font,
                fontSize=24,
                spaceAfter=30,
                alignment=1  # 居中
            )
            
            info_style = ParagraphStyle(
                'InfoStyle',
                parent=styles["Normal"],
                fontName=chinese_font,
                fontSize=12
            )
            
            # 构建PDF内容
            elements = []
            
            # 标题
            elements.append(Paragraph("客流分析报告", title_style))
            elements.append(Spacer(1, 20))
            
            # 基本信息
            elements.append(Paragraph(f"<b>时间范围：</b>{request.start_date} 至 {request.end_date}", info_style))
            if request.store_id:
                elements.append(Paragraph(f"<b>门店ID：</b>{request.store_id}", info_style))
            elements.append(Spacer(1, 20))
            
            # 数据表格
            table_data = [["小时", "客流量"]]
            for hour, count in sorted(hourly_counts.items()):
                table_data.append([hour, str(count)])
            
            # 创建表格
            table = Table(table_data, colWidths=[200, 200])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), chinese_font),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), chinese_font),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            elements.append(table)
            
            # 生成PDF
            doc.build(elements)
            
            # 获取PDF内容
            pdf_content = buffer.getvalue()
            buffer.close()
            
            return Response(
                content=pdf_content,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=footfall_report_{request.start_date}_{request.end_date}.pdf"
                }
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出客流分析报告失败: {str(e)}")