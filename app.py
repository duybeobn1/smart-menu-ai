import streamlit as st
import json
import os

# =========================
# 0. LANGUAGE CONFIGURATION
# =========================
# Dictionary containing all text for both languages
TRANSLATIONS = {
    "en": {
        "title": "🍲 Meta-Chef AI Smart Menu",
        "subtitle": "Personalized Food Therapy",
        "intro": "Please answer 4 simple questions to let the AI design your perfect meal.",
        "serving": "Serving Customer ID:",
        "q1": "1. How is your sleep recently?",
        "q1_opts": ["a. Insomnia / Restless (Yang)", "b. Normal / Good", "c. Heavy / Tired (Yin)"],
        "q2": "2. How does your body temperature feel?",
        "q2_opts": ["a. Always Hot / Sweating (Yang)", "b. Normal", "c. Always Cold / Chills (Yin)"],
        "q3": "3. Current Emotional State?",
        "q3_opts": ["a. Irritable / Angry (Yang)", "b. Calm / Normal", "c. Low Energy / Sad (Yin)"],
        "q4": "4. Energy Level?",
        "q4_opts": ["a. Hyperactive / Restless (Yang)", "b. Stable", "c. Exhausted / Fatigue (Yin)"],
        "btn_submit": "🩺 Analyze & Order",
        "result_score": "Body Balance Score",
        "result_symptom": "Detected State",
        "menu_header": "🥗 Your Prescribed Menu",
        "dish_benefit": "Health Benefit",
        "dish_impact": "Balancing Effect",
        "error_no_dish": "🚫 Your imbalance is quite severe.",
        "error_advice": "💡 Recommendation: Please consult the Chef for a custom medicinal combo.",
        "balanced": "Balanced",
        "yang": "Yang (Heat)",
        "yin": "Yin (Cold)"
    },
    "vi": {
        "title": "🍲 Thực Đơn Thông Minh Meta-Chef",
        "subtitle": "Trị Liệu Qua Ẩm Thực",
        "intro": "Hãy trả lời 4 câu hỏi đơn giản để AI thiết kế bữa ăn phù hợp nhất với thể trạng của bạn.",
        "serving": "Đang phục vụ Khách hàng:",
        "q1": "1. Giấc ngủ gần đây của bạn thế nào?",
        "q1_opts": ["a. Khó ngủ / Trằn trọc (Dương)", "b. Bình thường / Ngủ ngon", "c. Ngủ li bì / Vẫn mệt (Âm)"],
        "q2": "2. Bạn cảm thấy thân nhiệt thế nào?",
        "q2_opts": ["a. Hay nóng / Đổ mồ hôi (Dương)", "b. Bình thường", "c. Hay lạnh / Sợ gió (Âm)"],
        "q3": "3. Trạng thái cảm xúc hiện tại?",
        "q3_opts": ["a. Dễ cáu gắt / Nóng tính (Dương)", "b. Bình tĩnh / Thư thái", "c. Buồn chán / Ít năng lượng (Âm)"],
        "q4": "4. Mức năng lượng làm việc?",
        "q4_opts": ["a. Dư thừa / Bồn chồn (Dương)", "b. Ổn định", "c. Uể oải / Kiệt sức (Âm)"],
        "btn_submit": "🩺 Chẩn đoán & Gọi món",
        "result_score": "Điểm Cân Bằng",
        "result_symptom": "Trạng thái cơ thể",
        "menu_header": "🥗 Thực Đơn Dành Riêng Cho Bạn",
        "dish_benefit": "Tác dụng",
        "dish_impact": "Hiệu quả cân bằng",
        "error_no_dish": "🚫 Mức độ mất cân bằng khá cao.",
        "error_advice": "💡 Lời khuyên: Vui lòng liên hệ Bếp trưởng để phối hợp món thuốc đặc biệt.",
        "balanced": "Cân bằng",
        "yang": "Dương (Nóng)",
        "yin": "Âm (Lạnh)"
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
# Set current language code
L_CODE = "en" if "English" in lang_option else "vi"
T = TRANSLATIONS[L_CODE]  # Shortcut to access text

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
def calculate_score(survey_indices):
    """
    survey_indices: Dict like {'sleep': 0, 'temp': 2...} 
    0 = a (Yang), 1 = b (Normal), 2 = c (Yin)
    """
    # Mapping index to score: 0->+2, 1->0, 2->-2
    # Mood mapping: 0->+1, 1->0, 2->-1
    
    score = 0
    reasons = []
    
    # Generic weights logic based on index (0=a, 1=b, 2=c)
    # Weights: [Yang_Score, Normal_Score, Yin_Score]
    logic_map = {
        "sleep":  [2, 0, -2],
        "temp":   [2, 0, -2],
        "mood":   [1, 0, -1],
        "energy": [2, 0, -2]
    }

    for category, idx in survey_indices.items():
        points = logic_map[category][idx]
        score += points
        
        # Determine label for reason based on current language
        if idx == 0: reasons.append(f"{T['yang']}")
        if idx == 2: reasons.append(f"{T['yin']}")

    return score, ", ".join(reasons)

def get_recommendations(current_score):
    matches = []
    for name, data in recipes_db.items():
        dish_val = data.get("yin_yang_value", 0)
        proj_score = current_score + dish_val
        
        # STRICT MODE: Range [-1, 1]
        if -1 <= proj_score <= 1:
            # Handle bilingual description if available in JSON, else fallback
            benefits = data.get("health_benefits", [""])
            # Note: Assuming DB is English. Real production needs "health_benefits_vi" in JSON
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
    # We display Translated Text, but we logic based on Index (0,1,2)
    # This keeps logic safe regardless of language
    
    q1_val = st.radio(T["q1"], T["q1_opts"], index=1)
    q2_val = st.radio(T["q2"], T["q2_opts"], index=1)
    q3_val = st.radio(T["q3"], T["q3_opts"], index=1)
    q4_val = st.radio(T["q4"], T["q4_opts"], index=1)
    
    submitted = st.form_submit_button(T["btn_submit"])

if submitted:
    # 1. Find the index of the selected answer (0, 1, or 2)
    # This makes the logic language-independent
    survey_indices = {
        "sleep":  T["q1_opts"].index(q1_val),
        "temp":   T["q2_opts"].index(q2_val),
        "mood":   T["q3_opts"].index(q3_val),
        "energy": T["q4_opts"].index(q4_val),
    }
    
    # 2. Calculate
    score, reason = calculate_score(survey_indices)
    
    # 3. Display Diagnosis
    st.divider()
    c1, c2 = st.columns(2)
    c1.metric(T["result_score"], f"{score}")
    c2.write(f"**{T['result_symptom']}:**")
    c2.warning(reason if reason else T["balanced"])
    
    # 4. Get Menu
    matches = get_recommendations(score)
    
    st.markdown(f"### {T['menu_header']}")
    
    if not matches:
        st.error(T["error_no_dish"])
        st.info(T["error_advice"])
    else:
        for dish in matches:
            with st.container():
                col_img, col_text, col_stat = st.columns([1, 4, 2])
                
                # Mock Image (Optional: You can add real images later)
                col_img.markdown("🍲") 
                
                with col_text:
                    st.markdown(f"**{dish['name']}**")
                    st.caption(f"{T['dish_benefit']}: {dish['desc']}")
                
                with col_stat:
                    # Visual Indicator for Score
                    if dish['val'] > 0: arrow = "🔥 Yang" 
                    elif dish['val'] < 0: arrow = "❄️ Yin"
                    else: arrow = "⚖️ Neutral"
                    
                    st.success(f"{T['dish_impact']}: {arrow} ({dish['val']})")
                
                st.divider()