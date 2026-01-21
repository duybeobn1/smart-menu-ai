import streamlit as st
import json
import os

# =========================
# 1. SETUP & DATA
# =========================
st.set_page_config(page_title="Meta-Chef Smart Menu", page_icon="🍲")

# Load Data (Giả sử file json nằm cùng thư mục)
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
def calculate_score(survey):
    weights = {
        "sleep": {"a": 2, "b": 0, "c": -2},
        "temp": {"a": 2, "b": 0, "c": -2},
        "mood": {"a": 1, "b": 0, "c": -1},
        "energy": {"a": 2, "b": 0, "c": -2}
    }
    score = 0
    reasons = []
    for k, v in survey.items():
        score += weights[k][v]
        if v == 'a': reasons.append(f"{k} (Yang)")
        if v == 'c': reasons.append(f"{k} (Yin)")
    return score, ", ".join(reasons)

def get_recommendations(current_score):
    matches = []
    for name, data in recipes_db.items():
        dish_val = data.get("yin_yang_value", 0)
        proj_score = current_score + dish_val
        # Strict Range [-1, 1]
        if -1 <= proj_score <= 1:
            matches.append({
                "name": name,
                "val": dish_val,
                "new_score": proj_score,
                "desc": data.get("health_benefits", [""])[0],
                "price": data.get("price", "Contact Chef") # Ví dụ thêm giá
            })
    matches.sort(key=lambda x: abs(x["new_score"]))
    return matches

# =========================
# 3. UI LAYOUT
# =========================
st.title("🍲 AI Smart Menu & Therapy")
st.markdown("### Diagnosis & Food Prescription")

# Lấy Customer ID từ URL (khi quét QR)
query_params = st.query_params
cust_id = query_params.get("id", "Unknown")
st.caption(f"Serving Customer ID: {cust_id}")

with st.form("health_survey"):
    st.write("Please answer honestly to get your medicinal food:")
    
    q1 = st.radio("1. Sleep Quality?", 
                  ["a. Insomnia (Yang)", "b. Normal", "c. Heavy sleep (Yin)"], index=1)
    
    q2 = st.radio("2. Body Temperature?", 
                  ["a. Always Hot (Yang)", "b. Normal", "c. Always Cold (Yin)"], index=1)
    
    q3 = st.radio("3. Emotional State?", 
                  ["a. Irritable (Yang)", "b. Normal", "c. Low Energy (Yin)"], index=1)
    
    q4 = st.radio("4. Energy Level?", 
                  ["a. Hyperactive (Yang)", "b. Normal", "c. Tired (Yin)"], index=1)
    
    submitted = st.form_submit_button("🩺 Diagnose & Order")

if submitted:
    # Map answers back to keys
    mapping = {0: 'a', 1: 'b', 2: 'c'}
    survey = {
        "sleep": mapping[["Insomnia" in q1, "Normal" in q1, "Heavy" in q1].index(True)],
        "temp": mapping[["Hot" in q2, "Normal" in q2, "Cold" in q2].index(True)],
        "mood": mapping[["Irritable" in q3, "Normal" in q3, "Low" in q3].index(True)],
        "energy": mapping[["Hyper" in q4, "Normal" in q4, "Tired" in q4].index(True)],
    }
    
    score, reason = calculate_score(survey)
    
    st.divider()
    col1, col2 = st.columns(2)
    col1.metric("Your Yin-Yang Score", f"{score}")
    col2.write(f"**Symptoms:** {reason if reason else 'Balanced'}")
    
    matches = get_recommendations(score)
    
    st.subheader("🥗 Your Prescribed Menu")
    
    if not matches:
        st.error("🚫 No single dish fits your severe imbalance.")
        st.info("💡 Recommendation: Please consult the Meta-Chef for a custom medical combo.")
    else:
        for dish in matches:
            with st.container():
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"**{dish['name']}**")
                c1.caption(f"Benefit: {dish['desc']}")
                c2.success(f"Score: {dish['val']}")
                st.divider()