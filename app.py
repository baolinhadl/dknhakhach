from __future__ import annotations

from datetime import datetime, date
from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy

BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_DIR / 'nhakhach.db'}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "changeme"  # For flash messages; replace in production.

db = SQLAlchemy(app)


# Models
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    dangky = db.relationship("DangKyThamThan", backref="quannhan", cascade="all, delete")
    tutuong = db.relationship("TuTuong", backref="quannhan", cascade="all, delete")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<QuanNhan {self.hovaten}>"


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
        db.Enum("Chờ duyệt", "Đã duyệt", "Từ chối", name="trangthai_duyet_enum"),
        nullable=False,
        default="Chờ duyệt",
    )
    nguoi_duyet = db.Column(db.String(120))
    thoigian_duyet = db.Column(db.DateTime)
    ghichu = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    nhakhach = db.relationship("NhaKhachTham", backref="dangky", cascade="all, delete")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<DangKy {self.id} - {self.hoten_nguoitham}>"


class NhaKhachTham(db.Model):
    __tablename__ = "nhakhach_tham"

    id = db.Column(db.Integer, primary_key=True)
    dangky_id = db.Column(db.Integer, db.ForeignKey("dangky_thamthan.id"), nullable=False)
    thoigian_den = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    thoigian_ve = db.Column(db.DateTime)
    trangthai = db.Column(db.Enum("Đang ở", "Đã rời", name="trangthai_enum"), default="Đang ở")
    canbo_tiepnhan = db.Column(db.String(120))
    ghichu = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<NhaKhachTham {self.id}>"


class TuTuong(db.Model):
    __tablename__ = "tutuong"

    id = db.Column(db.Integer, primary_key=True)
    quannhan_id = db.Column(db.Integer, db.ForeignKey("quannhan.id"), nullable=False)
    nam = db.Column(db.Integer, nullable=False)
    thang = db.Column(db.Integer, nullable=False)
    tuan = db.Column(db.Integer, nullable=False, default=0)
    phanloai = db.Column(db.Enum("Tốt", "Khá", "Trung bình", "Yếu", name="phanloai_enum"))
    guongtot = db.Column(db.Text)
    khenthuong = db.Column(db.Text)
    kyluat = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("quannhan_id", "nam", "thang", "tuan", name="uq_tutuong_time"),)


# CLI utilities
@app.cli.command("init-db")
def init_db() -> None:
    """Initialize the SQLite database and create tables."""
    db.create_all()
    app.logger.info("Database initialized at %s", app.config["SQLALCHEMY_DATABASE_URI"])


# Helper functions

def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


# Routes
@app.route("/")
def dashboard():
    cho_don = DangKyThamThan.query.filter_by(trangthai_duyet="Chờ duyệt").order_by(DangKyThamThan.created_at.desc()).all()
    da_duyet = DangKyThamThan.query.filter_by(trangthai_duyet="Đã duyệt").order_by(DangKyThamThan.tungay).all()
    dang_o = NhaKhachTham.query.filter_by(trangthai="Đang ở").order_by(NhaKhachTham.thoigian_den.desc()).all()
    lich_su = NhaKhachTham.query.order_by(NhaKhachTham.thoigian_den.desc()).limit(10).all()
    return render_template(
        "dashboard.html",
        cho_don=cho_don,
        da_duyet=da_duyet,
        dang_o=dang_o,
        lich_su=lich_su,
    )


@app.route("/quannhan", methods=["GET", "POST"])
def manage_quannhan():
    if request.method == "POST":
        hovaten = request.form.get("hovaten", "").strip()
        if not hovaten:
            flash("Họ và tên là bắt buộc", "danger")
            return redirect(url_for("manage_quannhan"))
        quannhan = QuanNhan(
            hovaten=hovaten,
            ngaysinh=parse_date(request.form.get("ngaysinh")),
            nhapngu=parse_date(request.form.get("nhapngu")),
            capbac=request.form.get("capbac"),
            chucvu=request.form.get("chucvu"),
            donvi=request.form.get("donvi"),
            dantoc=request.form.get("dantoc"),
            tongiao=request.form.get("tongiao"),
            vanhoa=request.form.get("vanhoa"),
            hotencha=request.form.get("hotencha"),
            quequan=request.form.get("quequan"),
            sdtgiadinh=request.form.get("sdtgiadinh"),
            ghichu=request.form.get("ghichu"),
        )
        db.session.add(quannhan)
        db.session.commit()
        flash("Đã thêm quân nhân", "success")
        return redirect(url_for("manage_quannhan"))

    danh_sach = QuanNhan.query.order_by(QuanNhan.hovaten).all()
    return render_template("quannhan.html", danh_sach=danh_sach)


@app.route("/dangky", methods=["GET", "POST"])
def dangky():
    quannhan_list = QuanNhan.query.order_by(QuanNhan.hovaten).all()
    if not quannhan_list:
        flash("Hãy thêm quân nhân trước khi đăng ký", "warning")
        return redirect(url_for("manage_quannhan"))

    if request.method == "POST":
        quannhan_id = request.form.get("quannhan_id")
        tungay = parse_date(request.form.get("tungay"))
        denngay = parse_date(request.form.get("denngay"))
        if not (quannhan_id and tungay and denngay):
            flash("Thiếu thông tin bắt buộc", "danger")
            return redirect(url_for("dangky"))

        dangky_tham = DangKyThamThan(
            quannhan_id=int(quannhan_id),
            hoten_nguoitham=request.form.get("hoten_nguoitham", "").strip(),
            moiquanhe=request.form.get("moiquanhe"),
            sodienthoai=request.form.get("sodienthoai"),
            tungay=tungay,
            denngay=denngay,
            ghichu=request.form.get("ghichu"),
        )
        db.session.add(dangky_tham)
        db.session.commit()
        flash("Đã gửi đăng ký", "success")
        return redirect(url_for("dangky"))

    danh_sach = DangKyThamThan.query.order_by(DangKyThamThan.created_at.desc()).all()
    return render_template("dangky.html", danh_sach=danh_sach, quannhan_list=quannhan_list)


@app.route("/dangky/<int:dangky_id>/duyet", methods=["POST"])
def duyet_dangky(dangky_id: int):
    dangky_item = DangKyThamThan.query.get_or_404(dangky_id)
    action = request.form.get("action")
    nguoi_duyet = request.form.get("nguoi_duyet", "")
    dangky_item.nguoi_duyet = nguoi_duyet or None
    dangky_item.thoigian_duyet = datetime.utcnow()
    if action == "approve":
        dangky_item.trangthai_duyet = "Đã duyệt"
    elif action == "reject":
        dangky_item.trangthai_duyet = "Từ chối"
    else:
        flash("Hành động không hợp lệ", "danger")
        return redirect(url_for("dangky"))

    db.session.commit()
    flash("Đã cập nhật trạng thái", "success")
    return redirect(url_for("dangky"))


@app.route("/nhakhach/checkin", methods=["GET", "POST"])
def checkin():
    ds_duyet = (
        DangKyThamThan.query.filter_by(trangthai_duyet="Đã duyệt")
        .order_by(DangKyThamThan.tungay)
        .all()
    )
    if request.method == "POST":
        dangky_id = request.form.get("dangky_id")
        if not dangky_id:
            flash("Chọn một đăng ký đã duyệt", "danger")
            return redirect(url_for("checkin"))

        nhakhach = NhaKhachTham(
            dangky_id=int(dangky_id),
            canbo_tiepnhan=request.form.get("canbo_tiepnhan"),
            ghichu=request.form.get("ghichu"),
        )
        db.session.add(nhakhach)
        db.session.commit()
        flash("Đã check-in khách", "success")
        return redirect(url_for("checkin"))

    return render_template("checkin.html", ds_duyet=ds_duyet)


@app.route("/nhakhach/<int:nhakhach_id>/checkout", methods=["POST"])
def checkout(nhakhach_id: int):
    nhakhach = NhaKhachTham.query.get_or_404(nhakhach_id)
    nhakhach.trangthai = "Đã rời"
    nhakhach.thoigian_ve = datetime.utcnow()
    db.session.commit()
    flash("Đã cập nhật rời nhà khách", "success")
    return redirect(url_for("dashboard"))


@app.route("/nhakhach")
def danh_sach_nhakhach():
    dang_o = NhaKhachTham.query.filter_by(trangthai="Đang ở").order_by(NhaKhachTham.thoigian_den.desc()).all()
    lich_su = NhaKhachTham.query.order_by(NhaKhachTham.thoigian_den.desc()).all()
    return render_template("nhakhach.html", dang_o=dang_o, lich_su=lich_su)


@app.template_filter("fmt_date")
def fmt_date(value: date | datetime | None, with_time: bool = False) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime) and with_time:
        return value.strftime("%d/%m/%Y %H:%M")
    if isinstance(value, datetime):
        value = value.date()
    return value.strftime("%d/%m/%Y")


if __name__ == "__main__":  # pragma: no cover
    app.run(debug=True)
