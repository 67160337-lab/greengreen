import streamlit as st
import pickle
import sqlite3
import hashlib

# 1. ฟังก์ชันต้นแบบสำหรับการคำนวณ
def predict_profit(revenue, expenses):
    return revenue - expenses 

# ตั้งค่าหน้าเว็บให้ขยายกว้างและดูทันสมัย
st.set_page_config(
    page_title="ระบบวิเคราะห์ผลประกอบการ", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 💾 ฟังก์ชันจัดการฐานข้อมูล SQLite
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    # สร้างตารางเก็บข้อมูลผู้ใช้ถ้ายังไม่มี
    c.execute("""
        CREATE TABLE IF NOT EXISTS users 
        (username TEXT PRIMARY KEY, password TEXT)
    """)
    conn.commit()
    conn.close()

# ฟังก์ชันเข้ารหัสรหัสผ่านเพื่อความปลอดภัย (ไม่เก็บรหัสผ่านตรงๆ ลง DB)
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# ฟังก์ชันตรวจสอบรหัสผ่านตอน Login
def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return True
    return False

# เรียกใช้งานฐานข้อมูลตอนเปิดแอป
init_db()

# 🔐 ระบบ Session State สำหรับจัดการการเข้ารหัสหน้าจอ
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_page" not in st.session_state:
    st.session_state.user_page = "Login" # ค่าเริ่มต้นคือหน้า Login

# 🎨 Custom CSS ตกแต่งความสวยงาม
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600&display=swap');
    html, body, [class*="css"]  { font-family: 'Sarabun', sans-serif; }
    div[data-testid="stNumberInput"], div[data-testid="stTextInput"] {
        background-color: #1e222b; padding: 12px; border-radius: 12px;
        border: 1px solid #3e4451; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .result-card { padding: 25px; border-radius: 15px; margin-top: 20px; box-shadow: 0 8px 16px rgba(0,0,0,0.2); }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white; border: none; padding: 10px 24px; border-radius: 8px; font-weight: 600; width: 100%;
    }
    </style>
""", unsafe_allow_html=True)


# ==========================================
# 🛑 ส่วนที่ 1: หน้าจอสลับระหว่าง LOGIN และ REGISTER
# ==========================================
if not st.session_state.logged_in:
    _, center_col, _ = st.columns([3, 4, 3])
    
    with center_col:
        # ปุ่มสลับเมนูระหว่าง เข้าสู่ระบบ กับ สมัครสมาชิก
        menu = ["เข้าสู่ระบบ (Login)", "สมัครสมาชิก (Sign Up)"]
        choice = st.radio("เลือกทำรายการ", menu, horizontal=True)
        st.divider()

        if choice == "เข้าสู่ระบบ (Login)":
            st.markdown("<h2 style='text-align: center; color: #4FACFE;'>🔐 เข้าสู่ระบบ</h2>", unsafe_allow_html=True)
            username = st.text_input("Username", placeholder="กรอกชื่อผู้ใช้")
            password = st.text_input("Password", type="password", placeholder="กรอกรหัสผ่าน")
            
            if st.button("Sign In"):
                conn = sqlite3.connect("users.db")
                c = conn.cursor()
                c.execute("SELECT password FROM users WHERE username = ?", (username,))
                user_data = c.fetchone()
                conn.close()
                
                if user_data and check_hashes(password, user_data[0]):
                    st.session_state.logged_in = True
                    st.success(f"ยินดีต้อนรับคุณ {username}!")
                    st.rerun()
                else:
                    st.error("❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

        elif choice == "สมัครสมาชิก (Sign Up)":
            st.markdown("<h2 style='text-align: center; color: #00f2fe;'>📝 สมัครสมาชิกใหม่</h2>", unsafe_allow_html=True)
            new_user = st.text_input("กำหนด Username", placeholder="เช่น myusername123")
            new_password = st.text_input("กำหนด Password", type="password", placeholder="รหัสผ่านเข้าใช้งาน")
            confirm_password = st.text_input("ยืนยัน Password อีกครั้ง", type="password", placeholder="กรอกรหัสผ่านให้ตรงกัน")
            
            if st.button("ลงทะเบียน (Register)"):
                if new_user == "" or new_password == "":
                    st.warning("⚠️ กรุณากรอกข้อมูลให้ครบถ้วน")
                elif new_password != confirm_password:
                    st.error("❌ รหัสผ่านทั้งสองช่องไม่ตรงกัน")
                else:
                    hashed_password = make_hashes(new_password)
                    try:
                        conn = sqlite3.connect("users.db")
                        c = conn.cursor()
                        c.execute("INSERT INTO users(username, password) VALUES (?,?)", (new_user, hashed_password))
                        conn.commit()
                        conn.close()
                        st.success("🎉 สมัครสมาชิกสำเร็จแล้ว! คุณสามารถสลับไปหน้า Login เพื่อใช้งานได้ทันที")
                    except sqlite3.IntegrityError:
                        st.error("❌ Username นี้มีคนใช้ไปแล้ว กรุณาตั้งชื่อใหม่")

# ==========================================
# 📈 ส่วนที่ 2: หน้า DASHBOARD หลัก (แสดงเมื่อ Login สำเร็จ)
# ==========================================
else:
    def load_my_model():
        try:
            with open("profit_model.pkl", "rb") as file: return pickle.load(file)
        except Exception: return predict_profit

    profit_model = load_my_model()

    header_col1, header_col2 = st.columns([8, 2])
    with header_col1:
        st.markdown("<h1 style='color: #4FACFE; font-weight: 600; margin:0;'>📊 Profit Analysis Dashboard</h1>", unsafe_allow_html=True)
    with header_col2:
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.logged_in = False
            st.rerun()

    st.divider()

    main_col1, main_col2 = st.columns([5, 5], gap="large")

    with main_col1:
        st.markdown("<h3 style='color: #00f2fe; margin-bottom: 15px;'>📥 ระบุตัวเลขทางการเงิน</h3>", unsafe_allow_html=True)
        input_col1, input_col2 = st.columns(2)
        with input_col1:
            revenue = st.number_input("💵 รายได้ทั้งหมด (บาท)", min_value=0.0, value=0.0, step=5000.0, format="%.2f")
        with input_col2:
            expenses = st.number_input("📉 รายจ่ายทั้งหมด (บาท)", min_value=0.0, value=0.0, step=5000.0, format="%.2f")

    with main_col2:
        st.markdown("<h3 style='color: #00f2fe; margin-bottom: 15px;'>📋 ผลวิเคราะห์ประกอบการ</h3>", unsafe_allow_html=True)
        profit = profit_model(revenue, expenses)
        
        if profit > 0:
            st.markdown(f"""
                <div class='result-card' style='background: linear-gradient(135deg, #11998e, #38ef7d); color: white;'>
                    <h4 style='margin: 0;'>🎉 สถานะ: ได้กำไรสุทธิ</h4>
                    <p style='font-size: 36px; font-weight: bold; margin: 10px 0;'>{profit:,.2f} <span style='font-size: 18px;'>บาท</span></p>
                </div>
            """, unsafe_allow_html=True)
            st.metric(label="Growth Delta", value=f"{profit:,.2f} THB", delta=f"+{profit:,.2f}")
        elif profit < 0:
            st.markdown(f"""
                <div class='result-card' style='background: linear-gradient(135deg, #cb2d3e, #ef473a); color: white;'>
                    <h4 style='margin: 0;'>⚠️ สถานะ: ขาดทุนสุทธิ</h4>
                    <p style='font-size: 36px; font-weight: bold; margin: 10px 0;'>{abs(profit):,.2f} <span style='font-size: 18px;'>บาท</span></p>
                </div>
            """, unsafe_allow_html=True)
            st.metric(label="Growth Delta", value=f"{profit:,.2f} THB", delta=f"{profit:,.2f}")
        else:
            st.markdown(f"""
                <div class='result-card' style='background: linear-gradient(135deg, #4d5656, #7f8c8d); color: white;'>
                    <h4 style='margin: 0;'>📊 สถานะ: เท่าทุน (เสมอตัว)</h4>
                    <p style='font-size: 36px; font-weight: bold; margin: 10px 0;'>0.00 <span style='font-size: 18px;'>บาท</span></p>
                </div>
            """, unsafe_allow_html=True)