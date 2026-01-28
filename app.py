import os
import google.generativeai as genai
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# --- 1. การตั้งค่าหน้าจอ (UI แบบ app.py) ---
st.set_page_config(
    page_title="CompTech AI", 
    page_icon="💻", 
    layout="centered",
    initial_sidebar_state="expanded" 
)

# --- 2. CSS Styles (คงเดิมจาก app.py เพื่อความสวยงาม) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600&display=swap');

    /* ตั้งค่าฟอนต์ */
    html, body, p, h1, h2, h3, h4, h5, h6, span, div, label, button, input, textarea {
        font-family: 'Kanit', sans-serif;
    }

    /* ซ่อนแถบสีด้านบน */
    div[data-testid="stDecoration"] {
        visibility: hidden;
        height: 0px;
    }

    /* Sidebar สีเดียวกับ Theme */
    [data-testid="stSidebar"] {
        background-color: var(--primary-background-color); 
        border-right: 1px solid rgba(0, 242, 255, 0.2); 
    }

    /* Header Styling */
    .header-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding-top: 10px;
        padding-bottom: 20px;
    }

    .logo-title-wrapper {
        display: flex;
        align-items: center;
        gap: 20px;
    }

    /* Neon Text */
    .neon-text {
        font-size: 3.5rem;
        font-weight: 700;
        color: #00f2ff;
        text-shadow: 0 0 10px #00f2ff, 0 0 20px #00f2ff;
        margin: 0;
        line-height: 1.2;
    }

    .subtitle {
        font-size: 1.2rem;
        color: #888;
        margin-top: 5px;
        letter-spacing: 0.5px;
    }

    /* Button Styling */
    div.stButton > button {
        background-color: transparent !important;
        border: 1px solid #ff4b4b !important;
        color: #ff4b4b !important;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: 0.3s;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #ff4b4b !important;
        color: white !important;
        box-shadow: 0 0 15px rgba(255, 75, 75, 0.6);
    }

    /* Chat Styling */
    [data-testid="stChatMessage"] {
        border-radius: 20px !important;
        border: 1px solid rgba(0, 242, 255, 0.1) !important;
    }
    
    .element-container:has(iframe) { display: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. โหลดค่า Environment และ API (Logic แบบ app_2.py) ---
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

if not GOOGLE_API_KEY:
    st.error("🔑 กรุณาตั้งค่า API Key ในระบบก่อนใช้งาน")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# --- 4. System Instruction และ Model Config (ใช้ของ app_2.py ทั้งหมด) ---
PROMPT_WORKAW = """
คุณคือ 'ผู้ช่วยอัจฉริยะด้านคอมพิวเตอร์และสารสนเทศ' CompTech AI ทำหน้าที่เป็นผู้ช่วยในห้องเรียนคอมพิวเตอร์ ให้ข้อมูลที่ถูกต้อง แม่นยำ และเป็นมืออาชีพเกี่ยวกับความรู้คอมพิวเตอร์ ฮาร์ดแวร์ ซอฟต์แวร์ และระบบปฏิบัติการ Windows

I. ฐานข้อมูลและการตีความ:

ยึดถือข้อมูลหลัก: ให้ค้นหาและอ้างอิงคำตอบจากไฟล์ข้อมูลที่ให้มาเป็นลำดับแรก (Primary Source)

การจัดการภาษาพูด: หากผู้ใช้ใช้ภาษาพูด พิมพ์ผิด หรือถามในลักษณะสถานการณ์สมมติ (คำถามประเภท 1) ให้ใช้ความสามารถในการคิดวิเคราะห์เพื่อเชื่อมโยงเจตนาของผู้ใช้เข้ากับเนื้อหาที่ถูกต้องในฐานข้อมูล

การขยายความ: สามารถใช้ความรู้พื้นฐานด้านคอมพิวเตอร์เพื่ออธิบายเพิ่มเติมให้ผู้ใช้เข้าใจง่ายขึ้นได้ แต่ต้องไม่ขัดแย้งกับหลักการในไฟล์ข้อมูล และขยายความให้สั้นที่สุด

กรณีไม่พบข้อมูล: หากวิเคราะห์แล้วไม่มีเนื้อหาที่ใกล้เคียงเลย ให้ตอบว่า: "ขออภัยค่ะ ฉันไม่พบข้อมูลที่เฉพาะเจาะจงในขณะนี้ นักเรียนสนใจสอบถามเรื่องอื่นเกี่ยวกับคอมพิวเตอร์หรือระบบ Windows ไหมคะ"

ความกระชับ: ตอบเนื้อหาที่เฉพาะเจาะจงและตรงประเด็น โดยมีความยาวประมาณ 6-8 บรรทัด

II. รูปแบบการสื่อสารและการจัดรูปแบบ:

โทนเสียง: สุภาพ เป็นทางการ และเป็นมืออาชีพ (ใช้ "ค่ะ/คะ")

อิโมจิ: ห้ามใช้เครื่องหมายอิโมจิในคำตอบเด็ดขาด

การจัดรูปแบบ (Formatting): หากเป็นการอธิบายรายละเอียด หรือตอบคำถามที่มีหลายหัวข้อ (เช่น มีอะไรบ้าง, อย่างไร) ให้ดำเนินการดังนี้:

ขึ้นบรรทัดใหม่ (\n) เพื่อแยกส่วนเนื้อหา

ใช้ หัวข้อตัวหนา (Bold Headings)

ใช้ ลำดับตัวเลข (Numbered Lists) หรือ จุดไข่ปลา (Bullet Points) เพื่อให้สแกนอ่านง่าย

III. การจัดการลำดับการสนทนา:

หากคำถามกว้างเกินไปจนไม่สามารถระบุคำตอบที่ชัดเจนได้ ให้ตอบด้วยประโยคมาตรฐาน: "CompTech AI สวัสดีค่ะ นักเรียน สอบถามข้อมูลเกี่ยวกับคอมพิวเตอร์หรือระบบปฏิบัติการเรื่องใดคะ" เพื่อให้ผู้ใช้ระบุหัวข้อใหม่
"""

generation_config = {
    "temperature": 0.1, # ใช้ค่าตาม app_2.py เพื่อความยืดหยุ่น
    "top_p": 0.9,
    "max_output_tokens": 2048,
}

model = genai.GenerativeModel(
    model_name="models/gemini-2.5-flash-lite",
    generation_config=generation_config,
    system_instruction=PROMPT_WORKAW
)

# --- 5. ฟังก์ชันจัดการข้อมูล (ใช้ Logic การโหลดแบบ app_2.py) ---
@st.cache_data
def load_context(path):
    try:
        if os.path.exists(path):
            df = pd.read_excel(path, engine='openpyxl')
            return df.to_string(index=False)
        return None
    except Exception as e:
        return None

file_path = "context_for_chatbot.xlsx" 
file_content = load_context(file_path)

# --- 6. ส่วน SIDEBAR (Visual แบบ app.py แต่ Logic ปุ่มเหมือน app_2) ---
with st.sidebar:
    st.markdown("### ⚙️ Control Panel")
    st.image("https://cdn-icons-png.flaticon.com/512/2001/2001405.png", width=80)
    st.write("")
    
    # ปุ่ม Reset (ใช้ Logic การเคลียร์ค่าแบบ app_2 แต่หน้าตาปุ่มแบบ app.py)
    if st.button("🗑️ ล้างการสนทนา (Reset)", use_container_width=True):
        st.session_state["messages"] = [
            {"role": "assistant", "content": "CompTech AI สวัสดีค่ะ นักเรียน สอบถามข้อมูลเกี่ยวกับคอมพิวเตอร์หรือระบบปฏิบัติการเรื่องใดคะ"}
        ]
        st.rerun()

# --- 7. ส่วน HEADER (Visual แบบ app.py) ---
st.markdown(f"""
    <div class="header-container">
        <div class="logo-title-wrapper">
            <img src="https://cdn-icons-png.flaticon.com/512/4712/4712035.png" width="65">
            <h1 class="neon-text">CompTech AI</h1>
        </div>
        <div class="subtitle">Professional Computer & Technology Assistant</div>
    </div>
    <hr style="border: 1px solid rgba(0, 242, 255, 0.2); margin-bottom: 30px;">
    """, unsafe_allow_html=True)

# --- 8. ส่วนแชท (Logic การทำงานแบบ app_2.py ทั้งหมด) ---
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "CompTech AI สวัสดีค่ะ นักเรียน สอบถามข้อมูลเกี่ยวกับคอมพิวเตอร์หรือระบบปฏิบัติการเรื่องใดคะ"}
    ]

# แสดงผลข้อความเก่า (ใช้ Avatar สวยๆ แบบ app.py)
for msg in st.session_state["messages"]:
    av = "https://cdn-icons-png.flaticon.com/512/4712/4712035.png" if msg["role"] == "assistant" else "https://cdn-icons-png.flaticon.com/512/3048/3048122.png"
    with st.chat_message(msg["role"], avatar=av):
        st.write(msg["content"])

# รับค่า input และประมวลผล (Core Logic จาก app_2.py)
if prompt := st.chat_input("พิมพ์คำถามของคุณที่นี่..."):
    # แสดงข้อความ User
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="https://cdn-icons-png.flaticon.com/512/3048/3048122.png"):
        st.write(prompt)

    # ประมวลผลและตอบกลับ
    with st.chat_message("assistant", avatar="https://cdn-icons-png.flaticon.com/512/4712/4712035.png"):
        with st.spinner("Processing..."):
            try:
                # --- ส่วนสำคัญ: สร้าง History แบบ app_2.py ---
                history = []
                
                # 1. ใส่ Context (Knowledge Base)
                if file_content:
                    history.append({"role": "user", "parts": [f"Technical Knowledge Base: {file_content}"]})
                    history.append({"role": "model", "parts": ["รับทราบข้อมูลเทคนิคพื้นฐานครับ"]})
                
                # 2. ดึงประวัติการคุยล่าสุดเพื่อให้ต่อเนื่อง (Context Window)
                for msg in st.session_state["messages"][-6:]:
                    role = "model" if msg["role"] == "assistant" else "user"
                    history.append({"role": role, "parts": [msg["content"]]})

                # 3. ส่งเข้า Chat Session
                chat_session = model.start_chat(history=history)
                response = chat_session.send_message(prompt)
                ans = response.text
                
            except Exception as e:
                ans = f"เกิดข้อผิดพลาดของระบบ: {str(e)}"
            
            # แสดงผลและบันทึก
            st.write(ans)
            st.session_state["messages"].append({"role": "assistant", "content": ans})
