from models import db, app, Users, Roles
from datetime import datetime, timezone

# 確保在 Flask 應用程式上下文內執行
with app.app_context():
    db.create_all()

    # Users 預設資料鍵入
    if not Users.query.filter_by(account="admin").first():
        admin_user = Users(
            account="admin",
            name="admin",
            role_code="0",
            create_at=datetime.now(timezone.utc),
            create_by=1
        )
        admin_user.set_password("admin")  # 設定加密密碼

        db.session.add(admin_user)
        db.session.commit()
        print("Users 預設資料建立完成")

    # Roles 預設資料鍵入
    if not Roles.query.filter_by(role_code=0).first():
        default_role = [
            Roles(role_code=0, name='system', description='系統管理員', create_by=1),
            Roles(role_code=1, name='teacher', description='老師', create_by=1),
            Roles(role_code=2, name='student', description='學生', create_by=1)
        ]

        db.session.add_all(default_role)
        db.session.commit()
        print("Roles 預設資料建立完成")
    print("database create success!")
