import os
import google.generativeai as genai
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(
    page_title="CompTech AI", 
    page_icon="💻", 
    layout="centered",
    initial_sidebar_state="expanded" 
)

# --- 2. CSS Styles (แก้ไขให้ Sidebar เปลี่ยนสีตาม Theme อัตโนมัติ) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600&display=swap');

    /* ตั้งค่าฟอนต์ */
    html, body, p, h1, h2, h3, h4, h5, h6, span, div, label, button, input, textarea {
        font-family: 'Kanit', sans-serif;
    }

    /* ซ่อนเฉพาะแถบสีรุ้งด้านบนสุด */
    div[data-testid="stDecoration"] {
        visibility: hidden;
        height: 0px;
    }

    /* --- ส่วนที่แก้ไข: ทำให้ Sidebar สีเดียวกับหน้าจอหลัก ตาม System Theme --- */
    [data-testid="stSidebar"] {
        /* ใช้ตัวแปรนี้ เพื่อให้สีเปลี่ยนตาม Light/Dark Mode ของระบบอัตโนมัติ */
        background-color: var(--primary-background-color); 
        
        /* เส้นขอบจางๆ (ถ้าโหมด Light อาจจะดูแปลกตาเล็กน้อย แต่ยังคงเส้นไว้ตามดีไซน์เดิม) */
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

    /* Neon Text (จะสวยที่สุดใน Dark Mode) */
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

# --- 3. โหลดค่า Environment ---
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# --- 4. System Instruction ---
PROMPT_WORKAW = """
SYSTEM INSTRUCTION:

คุณคือ 'ผู้ช่วยอัจฉริยะด้านคอมพิวเตอร์และสารสนเทศ' (Workaw Chatbot) ทำหน้าที่ให้ข้อมูลที่ถูกต้อง แม่นยำ และเป็นมืออาชีพเกี่ยวกับความรู้คอมพิวเตอร์ ฮาร์ดแวร์ ซอฟต์แวร์ และระบบปฏิบัติการ Windows ตามข้อมูลที่ได้รับมอบหมายเท่านั้น

I. ฐานข้อมูลและความถูกต้อง:
- ทุกคำตอบต้องอ้างอิงจากข้อมูลในไฟล์ Excel/CSV ที่ให้มาเท่านั้น (Single Source of Truth)
- ห้ามใช้ความรู้ทั่วไป ความเห็นส่วนตัว หรือข้อมูลที่ไม่มีอยู่ในไฟล์ข้อมูลที่กำหนด
- หากไม่พบข้อมูลในไฟล์ ให้ตอบว่า "ขออภัยค่ะ ฉันไม่พบข้อมูลที่คุณต้องการในขณะนี้ คุณลูกค้าสนใจสอบถามเรื่องอื่นเกี่ยวกับคอมพิวเตอร์หรือระบบ Windows ไหมคะ"

II. รูปแบบการสื่อสารและการจัดรูปแบบ:
- **โทนเสียง:** สุภาพ เป็นทางการ และเป็นมืออาชีพ (ใช้ "ค่ะ/คะ")
- **อิโมจิ:** ห้ามใช้เครื่องหมายอิโมจิในคำตอบเด็ดขาด
- **กฎการจัดรูปแบบพิเศษ:** หากผู้ใช้ถามรายละเอียด หรือใช้คำว่า "ยังไงบ้าง", "เป็นอย่างไร", "มีอะไรบ้าง" คำตอบต้องจัดรูปแบบให้สแกนอ่านง่ายดังนี้:
    - ใช้การขึ้นบรรทัดใหม่ (\n)
    - ใช้หัวข้อตัวหนา (Bold Headings)
    - ใช้ลำดับตัวเลข (Numbered Lists) หรือ จุดไข่ปลา (Bullet Points)

III. การจัดการลำดับการสนทนา:
- **การทักทายและการขอคำอธิบายเพิ่มเติม:**
    - หากคำถามของผู้ใช้ไม่ชัดเจน กว้างเกินไป หรือเริ่มต้นบทสนทนาโดยไม่มีหัวข้อเฉพาะเจาะจง ให้ใช้ประโยคมาตรฐานดังนี้:
    - **ประโยคมาตรฐาน:** "Workaw สวัสดีค่ะ คุณลูกค้า สอบถามข้อมูลเกี่ยวกับคอมพิวเตอร์หรือระบบปฏิบัติการเรื่องใดคะ"

IV. ตัวอย่างการตอบ (Example Dialogue):
- User: "ระบบคอมพิวเตอร์ประกอบด้วยหน่วยอะไรบ้าง"
- Bot: "ระบบคอมพิวเตอร์ประกอบด้วยหน่วยองค์ประกอบหลัก ดังนี้:\n
1. **หน่วยรับข้อมูล (Input Unit)**\n
2. **หน่วยประมวลผล (Processing Unit)**\n
3. **หน่วยความจำ (Memory Unit)**\n
4. **หน่วยแสดงผล (Output Unit)**\n
ไม่ทราบว่าคุณลูกค้าต้องการทราบรายละเอียดของหน่วยไหนเพิ่มเติมไหมคะ"
"""

# --- 5. ตั้งค่า Model ---
model_name = "models/gemini-2.5-flash-lite"
try:
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config = {
            "temperature": 0.1, 
            "top_p": 0.9,
            "max_output_tokens": 2048,
        },
        system_instruction=PROMPT_WORKAW
    )
except Exception as e:
    st.error(f"Error initializing model: {e}")

# --- 6. ฟังก์ชันจัดการข้อมูล ---
@st.cache_data
def load_hidden_context(path):
    if os.path.exists(path):
        try:
            df = pd.read_excel(path, engine='openpyxl')
            return df.to_string(index=False)
        except: return ""
    return ""

hidden_knowledge = load_hidden_context("context_for_chatbot.xlsx")

# --- 7. ส่วน SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ Control Panel")
    st.image("https://cdn-icons-png.flaticon.com/512/2001/2001405.png", width=80)
    st.write("")
    if st.button("🗑️ ล้างการสนทนา (Reset)", use_container_width=True):
        st.session_state["messages"] = [{"role": "assistant", "content": "CompTech AI สวัสดีค่ะ นักเรียน สอบถามข้อมูลเกี่ยวกับคอมพิวเตอร์หรือระบบปฏิบัติการเรื่องใดคะ"}]
        st.rerun()

# --- 8. ส่วน HEADER ---
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

# --- 9. ส่วนแชท ---
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "CompTech AI สวัสดีค่ะ นักเรียน สอบถามข้อมูลเกี่ยวกับคอมพิวเตอร์หรือระบบปฏิบัติการเรื่องใดคะ"}]

for msg in st.session_state["messages"]:
    av = "https://cdn-icons-png.flaticon.com/512/4712/4712035.png" if msg["role"] == "assistant" else "https://cdn-icons-png.flaticon.com/512/3048/3048122.png"
    with st.chat_message(msg["role"], avatar=av):
        st.write(msg["content"])

if prompt := st.chat_input("พิมพ์คำถามของคุณที่นี่..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="https://cdn-icons-png.flaticon.com/512/3048/3048122.png"):
        st.write(prompt)

    with st.chat_message("assistant", avatar="https://cdn-icons-png.flaticon.com/512/4712/4712035.png"):
        with st.spinner("Processing..."):
            try:
                rich_prompt = f"Context from Database:\n{hidden_knowledge}\n\nStudent Question: {prompt}"
                response = model.generate_content(rich_prompt)
                ans = response.text
            except Exception as e:
                ans = f"เกิดข้อผิดพลาดของระบบ: {str(e)}"
            
            st.write(ans)
            st.session_state["messages"].append({"role": "assistant", "content": ans})

