from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db, User, Farm, VWU, SensorReading


def register_routes(app):

    # ============================================================
    # مسیرهای احراز هویت
    # ============================================================
    @app.route('/api/register', methods=['POST'])
    def register():
        data = request.get_json()

        if not data.get('phone') or not data.get('password'):
            return jsonify({'error': 'شماره موبایل و رمز عبور الزامی است'}), 400

        existing = User.query.filter_by(phone=data['phone']).first()
        if existing:
            return jsonify({'error': 'این شماره قبلاً ثبت شده است'}), 409

        hashed_password = generate_password_hash(data['password'])

        user = User(
            phone=data['phone'],
            password_hash=hashed_password,
            full_name=data.get('full_name'),
            user_type=data.get('user_type', 'farmer')
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({
            'message': 'ثبت‌نام موفق',
            'user_id': user.id,
            'user_type': user.user_type
        }), 201

    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json()

        user = User.query.filter_by(phone=data['phone']).first()

        if not user or not check_password_hash(user.password_hash, data['password']):
            return jsonify({'error': 'شماره موبایل یا رمز عبور اشتباه است'}), 401

        access_token = create_access_token(identity={'user_id': user.id, 'user_type': user.user_type})

        return jsonify({
            'token': access_token,
            'user_id': user.id,
            'user_type': user.user_type,
            'full_name': user.full_name
        }), 200

    @app.route('/api/profile', methods=['GET'])
    @jwt_required()
    def get_profile():
        current_user = get_jwt_identity()
        user = User.query.get(current_user['user_id'])

        if not user:
            return jsonify({'error': 'کاربر یافت نشد'}), 404

        return jsonify({
            'id': user.id,
            'phone': user.phone,
            'full_name': user.full_name,
            'user_type': user.user_type,
            'balance': user.balance,
            'is_verified': user.is_verified,
            'farms_count': len(user.farms)
        }), 200

    # ============================================================
    # مسیرهای مدیریت مزرعه
    # ============================================================
    @app.route('/api/farms', methods=['POST'])
    @jwt_required()
    def create_farm():
        current_user = get_jwt_identity()
        data = request.get_json()

        farm = Farm(
            farmer_id=current_user['user_id'],
            name=data['name'],
            area=data['area'],
            crop_type=data.get('crop_type'),
            region=data.get('region'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )

        db.session.add(farm)
        db.session.commit()

        return jsonify({
            'message': 'مزرعه با موفقیت ثبت شد',
            'farm_id': farm.id
        }), 201

    @app.route('/api/farms', methods=['GET'])
    @jwt_required()
    def get_farms():
        current_user = get_jwt_identity()
        farms = Farm.query.filter_by(farmer_id=current_user['user_id']).all()

        return jsonify([{
            'id': f.id,
            'name': f.name,
            'area': f.area,
            'crop_type': f.crop_type,
            'region': f.region,
            'vwu_count': VWU.query.filter_by(farm_id=f.id).count()
        } for f in farms]), 200

    # ============================================================
    # مسیرهای VWU
    # ============================================================
    @app.route('/api/vwu', methods=['POST'])
    @jwt_required()
    def create_vwu():
        current_user = get_jwt_identity()
        data = request.get_json()

        farm = Farm.query.get(data['farm_id'])
        if not farm or farm.farmer_id != current_user['user_id']:
            return jsonify({'error': 'دسترسی غیرمجاز به مزرعه'}), 403

        vwu = VWU(
            farm_id=data['farm_id'],
            batch_number=f"VWU-{datetime.now().strftime('%Y%m%d')}-{data['farm_id']}-{VWU.query.count()+1}",
            water_saved=data['water_saved'],
            price_per_unit=data.get('price_per_unit', 500),
            total_price=data['water_saved'] * data.get('price_per_unit', 500),
            status='pending'
        )

        db.session.add(vwu)
        db.session.commit()

        return jsonify({
            'message': 'VWU با موفقیت ایجاد شد',
            'vwu_id': vwu.id,
            'batch_number': vwu.batch_number
        }), 201

    @app.route('/api/vwu/market', methods=['GET'])
    def get_market_vwus():
        vwus = VWU.query.filter_by(status='listed').all()

        return jsonify([{
            'id': v.id,
            'farm_id': v.farm_id,
            'batch_number': v.batch_number,
            'water_saved': v.water_saved,
            'price_per_unit': v.price_per_unit,
            'total_price': v.total_price,
            'farm_name': v.farm.name if v.farm else 'نامشخص',
            'created_at': v.created_at.isoformat()
        } for v in vwus]), 200

    @app.route('/api/vwu/buy', methods=['POST'])
    @jwt_required()
    def buy_vwu():
        current_user = get_jwt_identity()
        data = request.get_json()

        vwu = VWU.query.get(data['vwu_id'])
        if not vwu:
            return jsonify({'error': 'VWU یافت نشد'}), 404

        if vwu.status != 'listed':
            return jsonify({'error': 'این VWU قابل خرید نیست'}), 400

        vwu.status = 'sold'
        vwu.buyer_id = current_user['user_id']

        seller = User.query.get(vwu.farm.farmer_id)
        buyer = User.query.get(current_user['user_id'])

        if seller:
            seller.balance += int(vwu.total_price * 0.8)

        if buyer:
            buyer.balance -= int(vwu.total_price)

        db.session.commit()

        return jsonify({
            'message': 'خرید با موفقیت انجام شد',
            'vwu_id': vwu.id,
            'seller_id': vwu.farm.farmer_id,
            'buyer_id': current_user['user_id']
        }), 200

    # ============================================================
    # مسیر دریافت داده از سنسور (IoT)
    # ============================================================
    @app.route('/api/iot/data', methods=['POST'])
    def receive_iot_data():
        try:
            data = request.get_json()

            if not data.get('sensor_id') or not data.get('water_flow'):
                return jsonify({'error': 'داده‌های ناقص'}), 400

            reading = SensorReading(
                sensor_id=data['sensor_id'],
                farm_id=data['farm_id'],
                water_flow=data['water_flow'],
                pressure=data.get('pressure')
            )

            db.session.add(reading)
            db.session.commit()

            print(f"📡 داده از سنسور {data['sensor_id']}: {data['water_flow']} L/s")

            return jsonify({
                'message': 'داده با موفقیت دریافت شد',
                'received_at': datetime.now().isoformat()
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ============================================================
    # مسیرهای ادمین
    # ============================================================
    @app.route('/api/admin/pending-vwus', methods=['GET'])
    @jwt_required()
    def get_pending_vwus():
        current_user = get_jwt_identity()
        user = User.query.get(current_user['user_id'])

        if user.user_type != 'admin':
            return jsonify({'error': 'دسترسی غیرمجاز'}), 403

        pending = VWU.query.filter_by(status='pending').all()

        return jsonify([{
            'id': v.id,
            'farm_id': v.farm_id,
            'batch_number': v.batch_number,
            'water_saved': v.water_saved,
            'price_per_unit': v.price_per_unit,
            'total_price': v.total_price,
            'farm_name': v.farm.name if v.farm else 'نامشخص',
            'farmer_phone': v.farm.owner.phone if v.farm and v.farm.owner else 'نامشخص',
            'created_at': v.created_at.isoformat()
        } for v in pending]), 200

    @app.route('/api/admin/verify-vwu/<int:vwu_id>', methods=['POST'])
    @jwt_required()
    def verify_vwu(vwu_id):
        current_user = get_jwt_identity()
        user = User.query.get(current_user['user_id'])

        if user.user_type != 'admin':
            return jsonify({'error': 'دسترسی غیرمجاز'}), 403

        vwu = VWU.query.get(vwu_id)
        if not vwu:
            return jsonify({'error': 'VWU یافت نشد'}), 404

        if vwu.status != 'pending':
            return jsonify({'error': 'این VWU قبلاً تایید یا لغو شده است'}), 400

        vwu.status = 'listed'
        db.session.commit()

        return jsonify({
            'message': f'✅ VWU {vwu.batch_number} تایید و در بازار لیست شد.',
            'vwu_id': vwu.id
        }), 200

    @app.route('/api/admin/reject-vwu/<int:vwu_id>', methods=['POST'])
    @jwt_required()
    def reject_vwu(vwu_id):
        current_user = get_jwt_identity()
        user = User.query.get(current_user['user_id'])

        if user.user_type != 'admin':
            return jsonify({'error': 'دسترسی غیرمجاز'}), 403

        vwu = VWU.query.get(vwu_id)
        if not vwu:
            return jsonify({'error': 'VWU یافت نشد'}), 404

        vwu.status = 'cancelled'
        db.session.commit()

        return jsonify({
            'message': f'❌ VWU {vwu.batch_number} رد شد.',
            'vwu_id': vwu.id
        }), 200

    # ============================================================
    # مسیر گزارش ESG برای صنایع
    # ============================================================
    @app.route('/api/industry/esg-report', methods=['GET'])
    @jwt_required()
    def get_esg_report():
        current_user = get_jwt_identity()
        user = User.query.get(current_user['user_id'])

        if user.user_type != 'industry':
            return jsonify({'error': 'این بخش فقط برای صنایع است'}), 403

        total_bought = db.session.query(db.func.sum(VWU.water_saved)).filter(
            VWU.buyer_id == user.id,
            VWU.status == 'sold'
        ).scalar() or 0

        return jsonify({
            'total_vwu_bought': total_bought,
            'co2_reduction': total_bought * 0.5,
            'trees_equivalent': total_bought / 1000,
            'report_date': datetime.now().isoformat()
        }), 200

    # ============================================================
    # مسیر پیش‌بینی (هوش مصنوعی)
    # ============================================================
    @app.route('/api/predict/vwu/<int:farm_id>', methods=['GET'])
    @jwt_required()
    def predict_vwu(farm_id):
        current_user = get_jwt_identity()
        farm = Farm.query.get(farm_id)

        if not farm or farm.farmer_id != current_user['user_id']:
            return jsonify({'error': 'دسترسی غیرمجاز'}), 403

        historical = VWU.query.filter_by(farm_id=farm_id).order_by(VWU.created_at).all()

        if len(historical) < 7:
            return jsonify({'error': 'داده‌های کافی برای پیش‌بینی وجود ندارد'}), 400

        total_vwu = sum([v.water_saved for v in historical])
        avg_vwu = total_vwu / len(historical)

        return jsonify({
            'farm_id': farm_id,
            'farm_name': farm.name,
            'average_vwu_per_day': round(avg_vwu, 2),
            'total_vwu_so_far': total_vwu,
            'predicted_next_30_days': round(avg_vwu * 30, 2),
            'data_points': len(historical)
        }), 200