from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Index
import base64
import hashlib
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config

# 初始化 Flask App
app = Flask(__name__)
app.config.from_object(config)

# 建立資料庫連線
db = SQLAlchemy(app)

# 定義 User 資料表
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 唯一識別 ID
    account = db.Column(db.String(100), unique=True, nullable=False)  # 帳號
    password = db.Column(db.String(256), nullable=False)  # 密碼（加密）
    name = db.Column(db.String(100), nullable=False)  # 名字
    role_code = db.Column(db.Integer, nullable=False)  # 角色 code
    login_at = db.Column(db.DateTime(timezone=True), nullable=True)  # 最後登入時間
    token = db.Column(db.String(512), nullable=True)  # JWT Token
    tokenrefresh_at = db.Column(db.DateTime(timezone=True), nullable=True)  # Token 更新時間
    deleted = db.Column(db.Boolean, nullable=False, server_default="false") # 紀錄是否刪除  
    create_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))  # 建立時間（預設當前時間）
    create_by = db.Column(db.Integer, nullable=False, default=1)  # 建立者 ID
    modify_at = db.Column(db.DateTime(timezone=True), nullable=True)  # 最後更改時間
    modify_by = db.Column(db.Integer, nullable=True)  # 更改者

    # 設定索引
    __table_args__ = (
        Index('idx_users_account', account),  # 帳號索引，加速登入查詢
        Index('idx_users_name', name),  # 名字索引，加速查詢
        Index('idx_users_role_code', role_code),  # 角色索引，加速篩選
        Index('idx_users_deleted', deleted),  # 加快 `deleted=False` 查詢
        Index('idx_users_login_at', login_at.desc()),  # 加快最後登入排序
        Index('idx_users_create_at', create_at.desc()),  # 加快排序最新建立帳戶
    )

    # 設定密碼時自動加密
    def set_password(self, raw_password):
        self.password = hashlib.sha256(raw_password.encode()).hexdigest()

    # 驗證密碼
    def check_password(self, raw_password):
        return self.password == hashlib.sha256(raw_password.encode()).hexdigest()


# 定義 Roles 資料表
class Roles(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 唯一識別 ID
    role_code = db.Column(db.Integer, unique=True, nullable=False)  # 角色識別碼
    name = db.Column(db.String(100), nullable=False)  # 名字
    description = db.Column(db.String(255), nullable=True)  # 說明
    deleted = db.Column(db.Boolean, nullable=False, server_default="false") # 紀錄是否刪除
    create_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))  # 建立時間（預設當前時間）
    create_by = db.Column(db.Integer, nullable=False, default=1)  # 建立者 ID
    modify_at = db.Column(db.DateTime(timezone=True), nullable=True)  # 最後更改時間
    modify_by = db.Column(db.Integer, nullable=True)  # 更改者

    # 設定索引
    __table_args__ = (
        Index('idx_roles_role_code', role_code),  # 角色碼索引（加快查詢）
        Index('idx_roles_name', name),  # 角色名稱索引（加快查詢）
        Index('idx_roles_deleted', deleted),  # 針對 deleted=False 進行查詢加速
        Index('idx_roles_create_at', create_at.desc()),  # 讓建立時間查詢更快
    )

# 定義 InteractiveResources 資料表
class InteractiveResources(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 唯一識別 ID
    description = db.Column(db.String(255), nullable=True)  # 說明
    picture = db.Column(db.LargeBinary, nullable=False) # 圖片
    picture_small = db.Column(db.LargeBinary, nullable=False) # 圖片縮圖
    deleted = db.Column(db.Boolean, nullable=False, server_default="false") # 紀錄是否刪除
    create_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))  # 建立時間（預設當前時間）
    create_by = db.Column(db.Integer, nullable=False, default=1)  # 建立者 ID
    modify_at = db.Column(db.DateTime(timezone=True), nullable=True)  # 最後更改時間
    modify_by = db.Column(db.Integer, nullable=True)  # 更改者

    # 設定索引
    __table_args__ = (
        Index('idx_interactiveresources_deleted', deleted),  # 加快 `deleted = False` 查詢
        Index('idx_interactiveresources_description', description),
        Index('idx_interactiveresources_create_at', create_at.desc()),  # 加快 `ORDER BY create_at DESC` 查詢最新圖片
        Index('idx_interactiveresources_modify_at', modify_at.desc()),  
    )

class ResourceSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 唯一識別 ID
    resourceId = db.Column(db.Integer, nullable=False) # resourceId
    lable_data = db.Column(JSONB, nullable=False) # 用 JSONB 紀錄標記的資料
    create_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))  # 建立時間（預設當前時間）
    create_by = db.Column(db.Integer, nullable=False, default=1)  # 建立者 ID
    modify_at = db.Column(db.DateTime(timezone=True), nullable=True)  # 最後更改時間
    modify_by = db.Column(db.Integer, nullable=True)  # 更改者
    
    # 設定索引
    __table_args__ = (
        Index('idx_resourcesetting_resourceId', resourceId),  # 加速 resourceId 查詢
        Index('idx_resourcesetting_create_at', create_at.desc()),  # 提高按建立時間排序的效率
        Index('idx_resourcesetting_lable_data', lable_data, postgresql_using='gin'),  # JSONB GIN 索引，提升 JSON 查詢效能
    )
