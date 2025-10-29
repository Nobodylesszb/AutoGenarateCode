from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models import ActivationCode, ActivationCodeStatus

router = APIRouter()


@router.get("/admin/stats")
def get_admin_stats(db: Session = Depends(get_db)):
  """管理后台统计卡片 + 近7天使用趋势"""
  total = db.query(ActivationCode).count()
  used = db.query(ActivationCode).filter(ActivationCode.status == ActivationCodeStatus.USED).count()
  usage_rate = round((used / total) * 100, 2) if total else 0.0

  today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
  today_used = db.query(ActivationCode).filter(
    ActivationCode.status == ActivationCodeStatus.USED,
    ActivationCode.used_at >= today_start
  ).count()

  # 最近7天每天使用量
  days = []
  for i in range(6, -1, -1):
    day_start = (today_start - timedelta(days=i))
    day_end = day_start + timedelta(days=1)
    cnt = db.query(ActivationCode).filter(
      ActivationCode.status == ActivationCodeStatus.USED,
      ActivationCode.used_at >= day_start,
      ActivationCode.used_at < day_end
    ).count()
    days.append({
      "date": day_start.strftime("%m-%d"),
      "count": cnt
    })

  return {
    "total_codes": total,
    "used_codes": used,
    "usage_rate": usage_rate,  # 百分比值，前端可显示 77.78%
    "today_new_used": today_used,
    "usage_trend": days
  }


