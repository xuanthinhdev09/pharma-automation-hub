"""Khởi tạo bảng + dữ liệu mẫu (chạy lần đầu)."""
from .database import Base, SessionLocal, engine
from .models import Department, InventoryRecord, ITAsset, ITTicket, Role, User, WorkflowTemplate
from .services.auth_service import hash_password

DEMO_PASSWORD = "demo123"


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Role).count() == 0:
            _seed(db)
            db.commit()
    finally:
        db.close()


def _seed(db) -> None:
    # Roles
    role_map = {}
    for name in ["EMPLOYEE", "MANAGER", "ACCOUNTANT", "DIRECTOR", "IT_ADMIN"]:
        role = Role(role_name=name, permissions_json={})
        db.add(role)
        role_map[name] = role
    db.flush()

    # Departments
    dept_map = {}
    for code, name in [("KHO", "Kho"), ("KD", "Kinh doanh"), ("KT", "Kế toán"),
                       ("HC", "Hành chính"), ("IT", "CNTT"), ("BGD", "Ban giám đốc")]:
        dept = Department(dept_code=code, dept_name=name)
        db.add(dept)
        dept_map[code] = dept
    db.flush()

    # Users
    password_hash = hash_password(DEMO_PASSWORD)
    users = [
        ("admin", "admin@pharma.demo", "Quản trị hệ thống", "IT_ADMIN", "IT"),
        ("nhanvien", "nhanvien@pharma.demo", "Nguyễn Văn A", "EMPLOYEE", "KHO"),
        ("truongphong", "truongphong@pharma.demo", "Trần Thị B", "MANAGER", "KD"),
        ("ketoan", "ketoan@pharma.demo", "Lê Văn C", "ACCOUNTANT", "KT"),
        ("giamdoc", "giamdoc@pharma.demo", "Phạm Văn D", "DIRECTOR", "BGD"),
    ]
    for username, email, full_name, role, dept in users:
        db.add(User(username=username, email=email, password_hash=password_hash,
                    full_name=full_name, role_id=role_map[role].id, department_id=dept_map[dept].id))

    # Workflow templates
    templates = [
        ("Đề xuất mua hàng vật tư/thiết bị", "Mua sắm; >10 triệu VNĐ tự thêm bước Giám đốc.",
         {"key": "purchase", "steps": ["Nhân viên nộp phiếu", "Trưởng phòng duyệt", "Kế toán kiểm tra"]}),
        ("Đơn xin nghỉ phép", "Nghỉ phép; sau duyệt sẽ trừ quỹ ngày phép.",
         {"key": "leave", "steps": ["Nhân viên nộp đơn", "Trưởng phòng duyệt", "Kế toán xác nhận", "Giám đốc phê duyệt"]}),
        ("Đề nghị thanh toán chi phí", "Thanh toán cần chứng từ và kiểm tra hạn mức.",
         {"key": "payment", "steps": ["Nhân viên nộp phiếu", "Trưởng phòng duyệt", "Kế toán kiểm tra", "Giám đốc phê duyệt"]}),
    ]
    for title, description, steps_config in templates:
        db.add(WorkflowTemplate(title=title, description=description, steps_config_json=steps_config))

    # Inventory (thuốc mẫu)
    medicines = [
        ("MED001", "Paracetamol 500mg", "Paracetamol", "LOT202601", "2026-12-31", 1500, "Hộp", "Dưới 30 độ C"),
        ("MED002", "Amoxicillin 500mg", "Amoxicillin", "LOT202545", "2027-03-15", 320, "Hộp", ""),
        ("MED003", "Vitamin C 1000mg", "Acid Ascorbic", "LOT202611", "2026-11-30", 90, "Lọ", ""),
        ("MED004", "Insulin Glargine", "Insulin Glargine", "LOT202433", "2026-12-05", 45, "Bút tiêm", "2-8 độ C"),
        ("MED005", "Ibuprofen 400mg", "Ibuprofen", "LOT202622", "2027-05-20", 780, "Hộp", ""),
        ("MED006", "Omeprazole 20mg", "Omeprazole", "LOT202518", "2026-12-20", 210, "Hộp", ""),
        ("MED007", "Cetirizine 10mg", "Cetirizine", "LOT202631", "2027-08-10", 540, "Hộp", ""),
        ("MED008", "Metformin 850mg", "Metformin", "LOT202430", "2026-12-02", 65, "Hộp", ""),
    ]
    for code, brand, generic, lot, expiry, stock, unit, cond in medicines:
        db.add(InventoryRecord(item_code=code, item_name=brand, generic_name=generic, batch_number=lot,
                               expiry_date=expiry, quantity_stock=stock, unit=unit, storage_condition=cond))

    # IT tickets (mẫu)
    db.add(ITTicket(category="Máy in", priority="Cao", subject="Máy in tầng 2 kẹt giấy",
                    description="Kẹt giấy liên tục, không in được hóa đơn.", status="Đang xử lý"))
    db.add(ITTicket(category="Wifi / Mạng", priority="Khẩn", subject="Toàn phòng kinh doanh mất mạng",
                    description="Không truy cập internet từ 10h sáng.", status="Đang xử lý"))
    db.add(ITTicket(category="Quên mật khẩu", priority="Trung bình", subject="Không đăng nhập được email",
                    description="Quên mật khẩu email công việc.", status="Đã giải quyết"))

    # IT assets (mẫu)
    assets = [
        ("IT-101", "Laptop Dell Latitude", "SN-DELL-101", "2027-12-31"),
        ("IT-102", "Máy in HP LaserJet", "SN-HP-102", "2026-12-31"),
        ("IT-103", "Laptop ThinkPad", "SN-TP-103", "2027-06-30"),
        ("IT-104", "Màn hình Samsung 24\"", "SN-SS-104", "2028-01-15"),
    ]
    for code, name, serial, warranty in assets:
        db.add(ITAsset(asset_code=code, asset_name=name, serial_number=serial, warranty_expiry=warranty, status="Đang dùng"))
