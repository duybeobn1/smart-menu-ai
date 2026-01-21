import streamlit as st
import json
import os

# =========================
# 0. LANGUAGE CONFIGURATION
# =========================
TRANSLATIONS = {
    "en": {
        "title": "🍲 Meta-Chef AI Smart Menu",
        "subtitle": "Personalized Food Therapy",
        "intro": "Please answer 4 simple questions to let the AI design your perfect meal.",
        "serving": "Serving Customer ID:",
        "q1": "1. How is your sleep recently?",
        "q1_opts": ["a. Insomnia / Restless", "b. Normal / Good", "c. Heavy / Tired"],
        "q2": "2. How does your body temperature feel?",
        "q2_opts": ["a. Always Hot / Sweating", "b. Normal", "c. Always Cold / Chills"],
        "q3": "3. Current Emotional State?",
        "q3_opts": ["a. Irritable / Angry", "b. Calm / Normal", "c. Low Energy / Sad"],
        "q4": "4. Energy Level?",
        "q4_opts": ["a. Hyperactive / Restless", "b. Stable", "c. Exhausted / Fatigue"],
        "btn_submit": "🩺 Analyze & Order",
        "result_symptom": "Your Body State",
        "menu_header": "🥗 Recommended Menu For You",
        "dish_benefit": "Why it helps",
        "error_no_dish": "🚫 Your imbalance is quite complex.",
        "error_advice": "💡 Recommendation: Please consult the Chef for a custom medicinal combo.",
        # States
        "state_balanced": "✨ Perfect Balance",
        "state_yang": "🔥 Heat Accumulation (Yang)",
        "state_yin": "❄️ Cold Accumulation (Yin)"
    },
    "vi": {
        "title": "🍲 Thực Đơn Thông Minh Meta-Chef",
        "subtitle": "Trị Liệu Qua Ẩm Thực",
        "intro": "Hãy trả lời 4 câu hỏi đơn giản để AI thiết kế bữa ăn phù hợp nhất với thể trạng của bạn.",
        "serving": "Đang phục vụ Khách hàng:",
        "q1": "1. Giấc ngủ gần đây của bạn thế nào?",
        "q1_opts": ["a. Khó ngủ / Trằn trọc", "b. Bình thường / Ngủ ngon", "c. Ngủ li bì / Vẫn mệt"],
        "q2": "2. Bạn cảm thấy thân nhiệt thế nào?",
        "q2_opts": ["a. Hay nóng / Đổ mồ hôi", "b. Bình thường", "c. Hay lạnh / Sợ gió"],
        "q3": "3. Trạng thái cảm xúc hiện tại?",
        "q3_opts": ["a. Dễ cáu gắt / Nóng tính", "b. Bình tĩnh / Thư thái", "c. Buồn chán / Ít năng lượng"],
        "q4": "4. Mức năng lượng làm việc?",
        "q4_opts": ["a. Dư thừa / Bồn chồn", "b. Ổn định", "c. Uể oải / Kiệt sức"],
        "btn_submit": "🩺 Chẩn đoán & Gọi món",
        "result_symptom": "Trạng thái cơ thể",
        "menu_header": "🥗 Thực Đơn Dành Riêng Cho Bạn",
        "dish_benefit": "Tác dụng",
        "error_no_dish": "🚫 Mức độ mất cân bằng khá cao.",
        "error_advice": "💡 Lời khuyên: Vui lòng liên hệ Bếp trưởng để phối hợp món thuốc đặc biệt.",
        # States
        "state_balanced": "✨ Cân Bằng",
        "state_yang": "🔥 Dư Nhiệt (Nóng trong)",
        "state_yin": "❄️ Nhiễm Hàn (Lạnh)"
    }
}

# =========================
# 1. SETUP & DATA
# =========================
st.set_page_config(page_title="Meta-Chef Smart Menu", page_icon="🍲")

# Language Selector (Sidebar)
st.sidebar.header("🌐 Language / Ngôn ngữ")
lang_option = st.sidebar.radio(
    "Choose your language:",
    ("🇬🇧 English", "🇻🇳 Tiếng Việt")
)
L_CODE = "en" if "English" in lang_option else "vi"
T = TRANSLATIONS[L_CODE]

# Load Data
@st.cache_data
def load_recipes():
    try:
        with open("recipes_v2.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

recipes_db = load_recipes()

# =========================
# 2. LOGIC FUNCTION
# =========================
def calculate_score_and_state(survey_indices):
    """
    Calculates numerical score BUT returns a single 'Dominant State' string
    to avoid the 'Yang, Yin, Yang' duplication error.
    """
    score = 0
    
    # Logic Map: 0=Yang(+), 1=Normal(0), 2=Yin(-)
    logic_map = {
        "sleep":  [2, 0, -2],
        "temp":   [2, 0, -2],
        "mood":   [1, 0, -1],
        "energy": [2, 0, -2]
    }

    for category, idx in survey_indices.items():
        score += logic_map[category][idx]

    # Determine Dominant State based on Total Score
    if score >= 2:
        state_text = T["state_yang"]
    elif score <= -2:
        state_text = T["state_yin"]
    else:
        state_text = T["state_balanced"]

    return score, state_text

def get_recommendations(current_score):
    matches = []
    for name, data in recipes_db.items():
        dish_val = data.get("yin_yang_value", 0)
        proj_score = current_score + dish_val
        
        # STRICT MODE: Range [-1, 1]
        if -1 <= proj_score <= 1:
            benefits = data.get("health_benefits", [""])
            desc = benefits[0] if isinstance(benefits, list) else str(benefits)

            matches.append({
                "name": name,
                "val": dish_val,
                "new_score": proj_score,
                "desc": desc, 
            })
    matches.sort(key=lambda x: abs(x["new_score"]))
    return matches

# =========================
# 3. UI LAYOUT
# =========================
st.title(T["title"])
st.subheader(T["subtitle"])
st.info(T["intro"])

# Get Customer ID
query_params = st.query_params
cust_id = query_params.get("id", "Guest")
st.caption(f"{T['serving']} **{cust_id}**")

with st.form("health_survey"):
    q1_val = st.radio(T["q1"], T["q1_opts"], index=1)
    q2_val = st.radio(T["q2"], T["q2_opts"], index=1)
    q3_val = st.radio(T["q3"], T["q3_opts"], index=1)
    q4_val = st.radio(T["q4"], T["q4_opts"], index=1)
    
    submitted = st.form_submit_button(T["btn_submit"])

if submitted:
    # 1. Get Indices
    survey_indices = {
        "sleep":  T["q1_opts"].index(q1_val),
        "temp":   T["q2_opts"].index(q2_val),
        "mood":   T["q3_opts"].index(q3_val),
        "energy": T["q4_opts"].index(q4_val),
    }
    
    # 2. Calculate Score & Get Clean State String
    score, state_text = calculate_score_and_state(survey_indices)
    
    # 3. Display Diagnosis (CLEAN VERSION)
    st.divider()
    
    # No more numeric score displayed here!
    # Just the friendly state name.
    st.markdown(f"#### {T['result_symptom']}: {state_text}")
    
    # 4. Get Menu
    matches = get_recommendations(score)
    
    st.markdown(f"### {T['menu_header']}")
    
    if not matches:
        st.error(T["error_no_dish"])
        st.info(T["error_advice"])
    else:
        for dish in matches:
            with st.container():
                # Simplified Layout: Image + Text only. No technical math column.
                col_img, col_text = st.columns([1, 6])
                
                col_img.markdown("##") 
                
                with col_text:
                    st.markdown(f"#### {dish['name']}")
                    # Simple Benefit description
                    st.write(f"_{T['dish_benefit']}: {dish['desc']}_")
                
                st.divider()