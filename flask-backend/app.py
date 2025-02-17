from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from database.models import db, app  # 引入的資料庫
from database.models import Users, InteractiveResources, ResourceSetting  #引入資料表
from sqlalchemy.exc import SQLAlchemyError
import base64
import re
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity,
    set_access_cookies, unset_jwt_cookies, get_jwt
)
from datetime import timedelta, datetime, timezone, UTC

# JWT 設定
app.config["JWT_SECRET_KEY"] = "oldmoon789"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=5)
jwt = JWTManager(app)

# 設定 Flask 應用，CORS 預檢請求處理
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)
@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response
@app.route('/api/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    return jsonify({"message": "Preflight OK"}), 200

#------------------ API ---------------
# 取得互動教材清單 API
@app.route('/api/getInteractiveResourceslist', methods=['GET'])
def get_interactive_resources_list():
    user, token_response, token_status_code = check_token_logic() 
    
    if token_status_code != 200:
        return token_response, token_status_code
    token_data = token_response.get_json()  # 轉換 JSON 回應
    access_token = token_data.get("access_token") if token_data else None
    
    interactive_resources = InteractiveResources.query.all()
    response = jsonify({
        "message": "success",
        "access_token": access_token,
        "result": [
            {
                "id": resource.id, 
                "description": resource.description, 
                "picture_small": base64.b64encode(resource.picture_small).decode('utf-8') if resource.picture_small else None,  # 轉換 bytes 為 Base64
                "create_at": resource.create_at
            } 
            for resource in interactive_resources
        ]
    })

    return response

# 儲存/更新互動教材 API
@app.route('/api/saveResource', methods=['POST'])
def save_resource():
    # 解析 token
    user, token_response, token_status_code = check_token_logic()
    if token_status_code != 200:
        return token_response, token_status_code
    token_data = token_response.get_json()
    access_token = token_data.get("access_token") if token_data else None

    try:
        data = request.get_json()
        action = data.get('action')
        head = data.get('head', {})
        detail = data.get('detail', [])

        if not action or action not in ['create', 'edit']:
            return jsonify({"access_token": access_token, "error": "Invalid action"}), 400

        # 取得當前時間與操作者 ID
        now = datetime.now(timezone.utc)
        operator_id = user["id"]  # 從 token 取得操作者 ID

        if action == 'create':
            # 創建 InteractiveResources 資料
            new_resource = InteractiveResources(
                description=head.get('description'),
                picture=decode_base64(head.get('picture')),
                picture_small=decode_base64(head.get('picture_small')),
                create_at=now,
                create_by=operator_id
            )
            db.session.add(new_resource)
            db.session.flush()  # 取得 new_resource.id

            # 確保 new_resource.id 正確
            db.session.refresh(new_resource)

            # 使用 bulk_save_objects 批量插入，提高效能
            new_settings = [
                ResourceSetting(
                    resourceId=new_resource.id,
                    lable_data=item,
                    create_at=now,
                    create_by=operator_id
                ) for item in detail
            ]
            db.session.bulk_save_objects(new_settings)

        elif action == 'edit':
            resource_id = head.get('id')
            if not resource_id:
                return jsonify({"access_token": access_token, "error": "Missing resource ID"}), 400

            resource = InteractiveResources.query.filter_by(id=resource_id).first()
            if not resource:
                return jsonify({"access_token": access_token, "error": "Resource not found"}), 404

            # 更新 `InteractiveResources` 欄位（只更新變更的欄位）
            resource.description = head.get('description', resource.description)
            resource.modify_at = now
            resource.modify_by = operator_id
            if head.get('picture'):
                resource.picture = decode_base64(head.get('picture'))
            if head.get('picture_small'):
                resource.picture_small = decode_base64(head.get('picture_small'))

            # 查詢已存在的 ResourceSetting
            existing_settings = {
                setting.id: setting for setting in ResourceSetting.query.filter_by(resourceId=resource_id).all()
            }

            new_details = []
            delete_ids = []  # 存放要刪除的記錄 ID

            for item in detail:
                status = item.get("status")  # 取得 status 值
                item_id = item.get("id")

                if status == 'edit' and item_id in existing_settings:
                    # 更新現有標記資料
                    setting = existing_settings[item_id]
                    setting.lable_data = item
                    setting.modify_at = now
                    setting.modify_by = operator_id

                elif status == 'add':
                    # 新增新標記資料
                    new_details.append(ResourceSetting(
                        resourceId=resource_id,
                        lable_data=item,
                        create_at=now,
                        create_by=operator_id
                    ))

                elif status == 'dele':
                    # 刪除符合 resourceId 且 lable_data.color 相同的記錄
                    color_to_delete = item.get("color")
                    if color_to_delete:
                        settings_to_delete = ResourceSetting.query.filter(ResourceSetting.resourceId == resource_id).all()
                        for setting in settings_to_delete:
                            if isinstance(setting.lable_data, dict) and setting.lable_data.get("color") == color_to_delete:
                                delete_ids.append(setting.id)

            # 執行刪除操作
            if delete_ids:
                ResourceSetting.query.filter(ResourceSetting.id.in_(delete_ids)).delete(synchronize_session=False)

            # 批量新增
            if new_details:
                db.session.bulk_save_objects(new_details)

        db.session.commit()

        return jsonify({
            "message": "資料寫入成功",
            "access_token": access_token
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"access_token": access_token, "error": "Database error", "details": str(e)}), 500

    except Exception as e:
        db.session.rollback()
        return jsonify({"access_token": access_token, "error": "Unexpected error", "details": str(e)}), 500


# 取得互動教材資料
@app.route('/api/getInteractiveResource', methods=['POST'])
def get_interactive_resource():
    try:
        # 解析 token
        user, token_response, token_status_code = check_token_logic()
        if token_status_code != 200:
            return token_response, token_status_code
        token_data = token_response.get_json()
        access_token = token_data.get("access_token") if token_data else None

        # 取得請求數據
        data = request.get_json()
        resource_id = int(data.get('id')) if data and 'id' in data else None  

        if not resource_id:
            return jsonify({"access_token": access_token, "error": "Missing 'id' parameter"}), 400

        # 查詢 head 資料
        head = InteractiveResources.query.filter(InteractiveResources.id == resource_id).first()
        if not head:
            return jsonify({"access_token": access_token, "error": "Resource not found"}), 404

        # 查詢 detail 資料
        details = ResourceSetting.query.filter(ResourceSetting.resourceId == resource_id).all()

        # 轉換為 JSON 格式（不使用 to_dict()）
        response_data = {
            "message": "success",
            "access_token": access_token,
            "result": {
                "head": {
                    "id": head.id,
                    "description": head.description,
                    "picture": base64.b64encode(head.picture).decode('utf-8') if head.picture else None,
                },
                "detail": [
                    {
                        "id": d.id,
                        "resourceId": d.resourceId,
                        "lable_data": d.lable_data,
                        "create_at": d.create_at.isoformat() if d.create_at else None
                    }
                    for d in details
                ]
            }
        }

        return jsonify(response_data), 200

    except ValueError:
        return jsonify({"access_token": access_token, "error": "Invalid 'id' parameter, must be an integer"}), 400

    except Exception as e:
        return jsonify({"access_token": access_token, "error": str(e)}), 500

# 刪除互動教材資料
@app.route('/api/deleteInteractiveResource', methods=['DELETE'])
def delete_interactive_resource():
    try:
        # 解析 token
        user, token_response, token_status_code = check_token_logic()
        if token_status_code != 200:
            return token_response, token_status_code
        token_data = token_response.get_json()
        access_token = token_data.get("access_token") if token_data else None

        # 取得請求數據
        data = request.get_json()
        resource_ids = data.get('ids') if data and 'ids' in data else None

        if not resource_ids or not isinstance(resource_ids, list):
            return jsonify({"access_token": access_token, "error": "Missing or invalid 'ids' parameter"}), 400

        # 開啟資料庫 session
        with db.session.begin_nested():
            for resource_id in resource_ids:
                if not isinstance(resource_id, int):
                    return jsonify({"access_token": access_token, "error": f"Invalid id: {resource_id}, must be an integer"}), 400
                
                # 查詢 head 資料
                head = InteractiveResources.query.filter_by(id=resource_id).first()
                if not head:
                    continue  # 若資料不存在則跳過

                # 刪除 detail 資料
                ResourceSetting.query.filter_by(resourceId=resource_id).delete()

                # 刪除 head 資料
                InteractiveResources.query.filter_by(id=resource_id).delete()

        # 提交變更
        db.session.commit()

        return jsonify({"access_token": access_token, "message": "Resources deleted successfully"}), 200

    except ValueError:
        db.session.rollback()
        return jsonify({"access_token": access_token, "error": "Invalid 'ids' parameter, must be an array of integers"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"access_token": access_token, "error": str(e)}), 500

# 使用者登入 API
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = Users.query.filter_by(account=data["account"]).first()

    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "帳號或密碼錯誤"}), 401

    access_token = create_access_token(identity=user.account)

    user.token = access_token
    user.tokenrefresh_at = datetime.now(UTC)
    user.login_at = datetime.now(UTC)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"資料庫錯誤: {str(e)}"}), 500

    response = jsonify({
        "message": "登入成功",
        "access_token": access_token,
        "result": {
            "id": user.id,
            "account": user.account,
            "name": user.name,
            "role_code": user.role_code
        }
    })
    
    return response

# 檢查 Token API
@app.route('/api/checkToken', methods=['GET'])
def check_token():
    user, response, status_code = check_token_logic()  # 正確解包回傳值
    return response, status_code  # 回傳 JSON 給前端

#------------------ 函式 ---------------
# Bearer Token 解析函式
def get_token_from_headers():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    return auth_header.split(" ")[1]

# 檢查 Token函式
def check_token_logic():
    token = get_token_from_headers()
    if not token:
        return None, jsonify({"error": "Token 未提供"}), 401

    user = Users.query.filter_by(token=token).first()
    if not user:
        return None, jsonify({"error": "Token 無效"}), 401

    now = datetime.now(UTC)  # 這是有時區的 datetime

    # ✅ 確保 tokenrefresh_at 具有時區資訊
    if user.tokenrefresh_at.tzinfo is None:
        user.tokenrefresh_at = user.tokenrefresh_at.replace(tzinfo=UTC)  # 明確設置為 UTC

    if (now - user.tokenrefresh_at) > timedelta(minutes=15):
        return None, jsonify({"error": "Token 已過期"}), 401

    # 生成新 token
    new_token = create_access_token(identity=user.account)
    user.token = new_token
    user.tokenrefresh_at = now

    try:
        db.session.commit()
        return {
            "id": user.id,
            "account": user.account
        }, jsonify({"access_token": new_token}), 200
    except Exception as e:
        db.session.rollback()
        return None, jsonify({"error": f"資料庫錯誤: {str(e)}"}), 500

# 安全解碼 Base64
def decode_base64(data):
    if not data:
        return None
    
    # 使用正則表達式移除 `data:image/png;base64,` 類似的前綴
    data = re.sub(r'^data:image\/\w+;base64,', '', data)
    
    try:
        return base64.b64decode(data)
    except Exception as e:
        print(f"Base64 decoding error: {e}")
        return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
