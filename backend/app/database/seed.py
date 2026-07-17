"""数据库初始化：建表 + 种子数据。"""
import logging
from sqlalchemy import inspect, text
from app.database.session import Base, get_engine

logger = logging.getLogger(__name__)


def init_db() -> None:
    """创建所有 ORM 表（如果不存在）。"""
    engine = get_engine()
    inspector = inspect(engine)
    existing = set(inspector.get_table_names())
    needed = set(Base.metadata.tables.keys())
    if needed - existing:
        logger.info("创建数据库表: %s", sorted(needed - existing))
    Base.metadata.create_all(bind=engine)


def init_seed() -> None:
    """填充必要的种子数据（幂等，已存在则跳过）。"""
    from sqlalchemy.orm import Session
    from app.entity.db_models import DetectionScene

    engine = get_engine()
    with Session(engine) as db:
        # ---- 默认食物检测场景 ----
        existing = db.query(DetectionScene).filter(
            DetectionScene.name == "food_detection"
        ).first()
        if not existing:
            scene = DetectionScene(
                name="food_detection",
                display_name="食物检测（默认）",
                category="food",
                class_names=["food"],
                class_names_cn=["食物"],
                conf_threshold=0.25,
                iou_threshold=0.45,
                is_active=True,
                description="UECFOOD-256 训练的 YOLO11s 食物检测模型",
            )
            db.add(scene)
            db.commit()
            logger.info("已创建默认检测场景: food_detection")
