from __future__ import annotations

import os
from datetime import date, datetime
from typing import Optional

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///nhakhach.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class QuanNhan(db.Model):
    __tablename__ = "quannhan"

    id = db.Column(db.Integer, primary_key=True)
    hovaten = db.Column(db.String(120), nullable=False)
    ngaysinh = db.Column(db.Date)
    nhapngu = db.Column(db.Date)
    capbac = db.Column(db.String(30))
    chucvu = db.Column(db.String(60))
    donvi = db.Column(db.String(60))
    dantoc = db.Column(db.String(30))
    tongiao = db.Column(db.String(30))
    vanhoa = db.Column(db.String(30))
    hotencha = db.Column(db.Text)
    quequan = db.Column(db.Text)
    sdtgiadinh = db.Column(db.String(30))
    ghichu = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=func.now())

    dangky = db.relationship("DangKyThamThan", back_populates="quannhan")
    tutuong = db.relationship("TuTuong", back_populates="quannhan")


class DangKyThamThan(db.Model):
    __tablename__ = "dangky_thamthan"

    id = db.Column(db.Integer, primary_key=True)
    quannhan_id = db.Column(db.Integer, db.ForeignKey("quannhan.id"), nullable=False)
    hoten_nguoitham = db.Column(db.String(255), nullable=False)
    moiquanhe = db.Column(db.String(100))
    sodienthoai = db.Column(db.String(30))
    tungay = db.Column(db.Date, nullable=False)
    denngay = db.Column(db.Date, nullable=False)
    trangthai_duyet = db.Column(
        db.Enum("Chờ duyệt", "Đã duyệt", "Từ chối", name="trangthai_duyet"),
        default="Chờ duyệt",
        nullable=False,
    )
    nguoi_duyet = db.Column(db.String(120))
    thoigian_duyet = db.Column(db.DateTime)
    ghichu = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=func.now())

    quannhan = db.relationship("QuanNhan", back_populates="dangky")
    nhakhach_tham = db.relationship("NhaKhachTham", back_populates="dangky")


class NhaKhachTham(db.Model):
    __tablename__ = "nhakhach_tham"

    id = db.Column(db.Integer, primary_key=True)
    dangky_id = db.Column(db.Integer, db.ForeignKey("dangky_thamthan.id"), nullable=False)
    thoigian_den = db.Column(db.DateTime, default=func.now(), nullable=False)
    thoigian_ve = db.Column(db.DateTime)
    trangthai = db.Column(
        db.Enum("Đang ở", "Đã rời", name="trangthai"), default="Đang ở", nullable=False
    )
    canbo_tiepnhan = db.Column(db.String(120))
    ghichu = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=func.now())

    dangky = db.relationship("DangKyThamThan", back_populates="nhakhach_tham")


class TuTuong(db.Model):
    __tablename__ = "tutuong"

    id = db.Column(db.Integer, primary_key=True)
    quannhan_id = db.Column(db.Integer, db.ForeignKey("quannhan.id"), nullable=False)
    nam = db.Column(db.Integer, nullable=False)
    thang = db.Column(db.Integer, nullable=False)
    tuan = db.Column(db.Integer, default=0, nullable=False)
    phanloai = db.Column(db.Enum("Tốt", "Khá", "Trung bình", "Yếu", name="phanloai"))
    guongtot = db.Column(db.Text)
    khenthuong = db.Column(db.Text)
    kyluat = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=func.now())

    quannhan = db.relationship("QuanNhan", back_populates="tutuong")

    __table_args__ = (
        db.UniqueConstraint("quannhan_id", "nam", "thang", "tuan", name="uq_tutuong_time"),
    )


@app.route("/")
def index():
    pending_registrations = (
        DangKyThamThan.query.filter_by(trangthai_duyet="Chờ duyệt")
        .order_by(DangKyThamThan.created_at.desc())
        .all()
    )
    approved_registrations = (
        DangKyThamThan.query.filter_by(trangthai_duyet="Đã duyệt")
        .order_by(DangKyThamThan.tungay)
        .all()
    )
    active_guests = (
        NhaKhachTham.query.filter_by(trangthai="Đang ở")
        .order_by(NhaKhachTham.thoigian_den.desc())
        .all()
    )
    history = (
        NhaKhachTham.query.order_by(NhaKhachTham.thoigian_den.desc())
        .limit(50)
        .all()
    )
    soldiers = QuanNhan.query.order_by(QuanNhan.hovaten).all()

    return render_template(
        "index.html",
        pending_registrations=pending_registrations,
        approved_registrations=approved_registrations,
        active_guests=active_guests,
        history=history,
        soldiers=soldiers,
    )


def parse_date(date_text: Optional[str]) -> Optional[date]:
    if not date_text:
        return None
    try:
        return datetime.strptime(date_text, "%Y-%m-%d").date()
    except ValueError:
        return None


def parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M")
    except ValueError:
        return None


@app.route("/quannhan/new", methods=["GET", "POST"])
def add_quannhan():
    if request.method == "POST":
        hovaten = request.form.get("hovaten", "").strip()
        if not hovaten:
            flash("Họ và tên không được để trống", "error")
            return redirect(url_for("add_quannhan"))

        quannhan = QuanNhan(
            hovaten=hovaten,
            ngaysinh=parse_date(request.form.get("ngaysinh")),
            nhapngu=parse_date(request.form.get("nhapngu")),
            capbac=request.form.get("capbac") or None,
            chucvu=request.form.get("chucvu") or None,
            donvi=request.form.get("donvi") or None,
            dantoc=request.form.get("dantoc") or None,
            tongiao=request.form.get("tongiao") or None,
            vanhoa=request.form.get("vanhoa") or None,
            hotencha=request.form.get("hotencha") or None,
            quequan=request.form.get("quequan") or None,
            sdtgiadinh=request.form.get("sdtgiadinh") or None,
            ghichu=request.form.get("ghichu") or None,
        )
        db.session.add(quannhan)
        db.session.commit()
        flash("Đã lưu hồ sơ quân nhân", "success")
        return redirect(url_for("index"))

    return render_template("quannhan_form.html")


@app.route("/dangky/new", methods=["GET", "POST"])
def add_dangky():
    soldiers = QuanNhan.query.order_by(QuanNhan.hovaten).all()
    if request.method == "POST":
        quannhan_id = request.form.get("quannhan_id")
        quannhan = QuanNhan.query.get(quannhan_id)
        if not quannhan:
            flash("Chọn quân nhân hợp lệ", "error")
            return redirect(url_for("add_dangky"))

        tungay = parse_date(request.form.get("tungay"))
        denngay = parse_date(request.form.get("denngay"))
        if not tungay or not denngay:
            flash("Thời gian đăng ký không hợp lệ", "error")
            return redirect(url_for("add_dangky"))
        if denngay < tungay:
            flash("Ngày kết thúc phải sau ngày bắt đầu", "error")
            return redirect(url_for("add_dangky"))

        registration = DangKyThamThan(
            quannhan_id=quannhan.id,
            hoten_nguoitham=request.form.get("hoten_nguoitham", "").strip(),
            moiquanhe=request.form.get("moiquanhe") or None,
            sodienthoai=request.form.get("sodienthoai") or None,
            tungay=tungay,
            denngay=denngay,
            ghichu=request.form.get("ghichu") or None,
        )

        if not registration.hoten_nguoitham:
            flash("Họ tên người thăm không được để trống", "error")
            return redirect(url_for("add_dangky"))

        db.session.add(registration)
        db.session.commit()
        flash("Đã lưu đăng ký, chờ duyệt", "success")
        return redirect(url_for("index"))

    if not soldiers:
        flash("Hãy tạo hồ sơ quân nhân trước", "error")
    return render_template("dangky_form.html", soldiers=soldiers)


@app.route("/dangky/<int:dangky_id>/approve", methods=["POST"])
def approve_dangky(dangky_id: int):
    registration = DangKyThamThan.query.get_or_404(dangky_id)
    action = request.form.get("action")
    approver = (request.form.get("nguoi_duyet") or "CB trực").strip()
    now = datetime.now()

    if action == "approve":
        registration.trangthai_duyet = "Đã duyệt"
    else:
        registration.trangthai_duyet = "Từ chối"
    registration.nguoi_duyet = approver
    registration.thoigian_duyet = now
    registration.ghichu = request.form.get("ghichu") or registration.ghichu

    db.session.commit()
    flash("Đã cập nhật trạng thái duyệt", "success")
    return redirect(url_for("index"))


@app.route("/dangky/<int:dangky_id>/checkin", methods=["POST"])
def checkin(dangky_id: int):
    registration = DangKyThamThan.query.get_or_404(dangky_id)
    if registration.trangthai_duyet != "Đã duyệt":
        flash("Chỉ check-in đăng ký đã duyệt", "error")
        return redirect(url_for("index"))

    existing = (
        NhaKhachTham.query.filter_by(dangky_id=dangky_id, trangthai="Đang ở").first()
    )
    if existing:
        flash("Khách đã được check-in", "error")
        return redirect(url_for("index"))

    checkin_time = parse_datetime(request.form.get("thoigian_den")) or datetime.now()
    guest = NhaKhachTham(
        dangky_id=dangky_id,
        thoigian_den=checkin_time,
        canbo_tiepnhan=request.form.get("canbo_tiepnhan") or None,
        ghichu=request.form.get("ghichu") or None,
    )
    db.session.add(guest)
    db.session.commit()
    flash("Đã check-in khách", "success")
    return redirect(url_for("index"))


@app.route("/nhakhach/<int:nhakhach_id>/checkout", methods=["POST"])
def checkout(nhakhach_id: int):
    guest = NhaKhachTham.query.get_or_404(nhakhach_id)
    if guest.trangthai == "Đã rời":
        flash("Khách đã rời trước đó", "error")
        return redirect(url_for("index"))

    guest.trangthai = "Đã rời"
    guest.thoigian_ve = parse_datetime(request.form.get("thoigian_ve")) or datetime.now()
    guest.ghichu = request.form.get("ghichu") or guest.ghichu
    db.session.commit()
    flash("Đã check-out khách", "success")
    return redirect(url_for("index"))


@app.route("/seed", methods=["POST"])
def seed_data():
    """Quick seed for demo data."""

    if QuanNhan.query.count():
        flash("Dữ liệu đã tồn tại", "info")
        return redirect(url_for("index"))

    quan_nhan = QuanNhan(
        hovaten="Nguyễn Văn An",
        capbac="Trung úy",
        chucvu="Trợ lý",
        donvi="Tiểu đoàn 1",
    )
    db.session.add(quan_nhan)
    db.session.commit()

    reg = DangKyThamThan(
        quannhan_id=quan_nhan.id,
        hoten_nguoitham="Trần Thị Bình",
        moiquanhe="Vợ",
        sodienthoai="0912345678",
        tungay=date.today(),
        denngay=date.today(),
        trangthai_duyet="Đã duyệt",
        nguoi_duyet="CB trực",
        thoigian_duyet=datetime.now(),
    )
    db.session.add(reg)
    db.session.commit()

    db.session.add(
        NhaKhachTham(
            dangky_id=reg.id,
            thoigian_den=datetime.now(),
            canbo_tiepnhan="Thượng sĩ Hùng",
        )
    )
    db.session.commit()

    flash("Đã tạo dữ liệu mẫu", "success")
    return redirect(url_for("index"))


@app.before_first_request
def init_db():
    db.create_all()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
