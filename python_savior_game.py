# combat_game.py
import streamlit as st
import random
import json
import os
from datetime import datetime

# ================== CẤU HÌNH ==================
VIRUSES = [
    {"name": "🦠 VIRUS LOGIC", "hp": 30, "attack": 5, "exp": 50},
    {"name": "🧬 VIRUS LOOP", "hp": 50, "attack": 8, "exp": 80},
    {"name": "🎯 VIRUS FUNCTION", "hp": 70, "attack": 12, "exp": 120},
    {"name": "📦 VIRUS LIST", "hp": 100, "attack": 15, "exp": 180},
    {"name": "👑 BOSS DICTIONARY", "hp": 150, "attack": 20, "exp": 300},
]

DATA_FILE = "combat_scores.json"

# ================== QUẢN LÝ ĐIỂM ==================
def load_scores():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_score(name, score):
    scores = load_scores()
    scores.append({
        "name": name,
        "score": score,
        "date": datetime.now().strftime("%d/%m/%Y %H:%M")
    })
    scores.sort(key=lambda x: x["score"], reverse=True)
    scores = scores[:10]
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(scores, f, indent=2, ensure_ascii=False)

def get_top_scores():
    return load_scores()[:10]

# ================== GAME STATE ==================
def init_game_state():
    return {
        "current_level": 1,
        "player_name": "",
        "player_hp": 100,
        "player_max_hp": 100,
        "player_attack": 12,
        "player_level": 1,
        "player_exp": 0,
        "player_exp_needed": 100,
        "score": 0,
        "game_active": False,
        "victory": False,
        "current_virus_hp": VIRUSES[0]["hp"],
        "combat_log": [],
        "reset_counter": 0
    }

# ================== GIAO DIỆN ==================
st.set_page_config(page_title="Python Savior", page_icon="⚔️", layout="wide")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0a0a0a 0%, #0d1b2a 100%); }
.title-box {
    text-align: center;
    padding: 20px;
    background: linear-gradient(135deg, #1b263b, #415a77);
    border-radius: 20px;
    border: 2px solid #ff4444;
    margin-bottom: 20px;
}
.virus-card {
    background: linear-gradient(135deg, #4a0000, #8b0000);
    border-radius: 15px;
    padding: 15px;
    text-align: center;
    border: 2px solid #ff0000;
}
.player-card {
    background: linear-gradient(135deg, #0d3b0d, #1a5c1a);
    border-radius: 15px;
    padding: 15px;
    text-align: center;
    border: 2px solid #00ff88;
}
button {
    background: linear-gradient(135deg, #ff6600, #ff3300) !important;
    color: white !important;
    font-size: 18px !important;
    font-weight: bold !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px !important;
}
button:hover {
    transform: scale(1.02);
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="title-box">
    <h1 style='color: #ff4444; margin: 0;'>⚔️ PYTHON SAVIOR - CHIẾN ĐẤU ⚔️</h1>
    <h3 style='color: #ffffff;'>Đánh bay virus máy tính, cứu thế giới!</h3>
    <p style='color: #aaa;'>⚡ Chọn hành động thông minh để chiến thắng ⚡</p>
</div>
""", unsafe_allow_html=True)

# Khởi tạo session state
if "game" not in st.session_state:
    st.session_state.game = init_game_state()
if "show_rank" not in st.session_state:
    st.session_state.show_rank = False

game = st.session_state.game

# Sidebar
with st.sidebar:
    st.markdown("## 🎮 MENU")
    if st.button("🆕 BẮT ĐẦU MỚI", key=f"new_game_{game['reset_counter']}"):
        st.session_state.game = init_game_state()
        st.session_state.show_rank = False
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📖 HƯỚNG DẪN")
    st.markdown("⚔️ **Tấn công** → Gây 9-15 sát thương")
    st.markdown("💊 **Hồi máu** → Hồi 15-30 HP (tốn 20đ)")
    st.markdown("🛡️ **Phòng thủ** → Giảm sát thương")
    st.markdown("🏆 **Thắng 5 level** → Cứu thế giới!")
    
    st.markdown("---")
    st.markdown("### 🏆 BẢNG XẾP HẠNG")
    top = get_top_scores()
    if top:
        for i, s in enumerate(top):
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
            st.markdown(f"{medal} **{s['name']}** - {s['score']} điểm")
    else:
        st.info("Chưa có ai!")

# Màn hình xếp hạng
if st.session_state.show_rank:
    st.markdown("## 🏆 BẢNG XẾP HẠNG TOÀN THỜI GIAN 🏆")
    top = get_top_scores()
    if top:
        for i, s in enumerate(top):
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
            st.markdown(f"{medal} **{s['name']}** - {s['score']} điểm - 📅 {s['date']}")
    if st.button("🔙 QUAY LẠI GAME", key=f"back_{game['reset_counter']}"):
        st.session_state.show_rank = False
        st.rerun()
    st.stop()

# Màn hình bắt đầu
if not game["game_active"] and not game["victory"] and game["player_name"] == "":
    st.markdown("""
    <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 20px;'>
        <div style='font-size: 80px;'>⚔️ 🐍 ⚔️</div>
        <h2>CHÀO MỪNG CHIẾN BINH!</h2>
        <p>Thế giới đang bị virus máy tính tấn công! Hãy chiến đấu để giải cứu!</p>
    </div>
    """, unsafe_allow_html=True)
    
    name = st.text_input("👤 Nhập tên chiến binh:", key=f"name_input_{game['reset_counter']}")
    if st.button("🚀 BẮT ĐẦU CHIẾN ĐẤU", key=f"start_{game['reset_counter']}", use_container_width=True):
        if name and name.strip():
            game["player_name"] = name.strip()
            game["game_active"] = True
            game["combat_log"] = [f"🦸‍♂️ {name} bước vào trận chiến!"]
            st.rerun()
        else:
            st.error("❌ Hãy nhập tên của bạn!")
    st.stop()

# Game over
if game["player_hp"] <= 0:
    st.markdown("""
    <div style='text-align: center; padding: 40px; background: #4a0000; border-radius: 20px;'>
        <h1 style='color: #ff4444;'>💀 GAME OVER 💀</h1>
        <p style='color: white;'>Virus máy tính đã chiếm thế giới...</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔄 CHƠI LẠI", key=f"over_{game['reset_counter']}", use_container_width=True):
        st.session_state.game = init_game_state()
        st.rerun()
    st.stop()

# Victory
if game["victory"]:
    st.markdown(f"""
    <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #00aa44, #006400); border-radius: 20px;'>
        <h1 style='color: #ffd700;'>🏆 CHIẾN THẮNG! 🏆</h1>
        <h2 style='color: white;'>Bạn đã cứu thế giới!</h2>
        <p style='color: #ffd700; font-size: 24px;'>⭐ Điểm: {game['score']} ⭐</p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 CHƠI LẠI", key=f"victory_play_{game['reset_counter']}", use_container_width=True):
            st.session_state.game = init_game_state()
            st.rerun()
    with col2:
        if st.button("🏆 BẢNG XẾP HẠNG", key=f"victory_rank_{game['reset_counter']}", use_container_width=True):
            st.session_state.show_rank = True
            st.rerun()
    st.stop()

# Hiển thị trạng thái chiến đấu
current_virus = VIRUSES[game["current_level"] - 1]
virus_hp_percent = game["current_virus_hp"] / current_virus["hp"]

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="player-card">
        <div style='font-size: 48px;'>⚔️</div>
        <h3>{game['player_name']}</h3>
        <p>❤️ HP: {max(0, game['player_hp'])}/{game['player_max_hp']}</p>
        <p>⚔️ Sát thương: {game['player_attack']}</p>
        <p>⭐ Điểm: {game['score']}</p>
        <p>📊 Cấp {game['player_level']}</p>
    </div>
    """, unsafe_allow_html=True)
    st.progress(max(0, game['player_hp']) / game['player_max_hp'])

with col2:
    st.markdown(f"""
    <div class="virus-card">
        <div style='font-size: 48px;'>{current_virus['name'][0]}</div>
        <h3>{current_virus['name']}</h3>
        <p>💀 HP: {max(0, game['current_virus_hp'])}/{current_virus['hp']}</p>
        <p>⚔️ Sát thương: {current_virus['attack']}</p>
        <p>🎯 Level {game['current_level']}/5</p>
    </div>
    """, unsafe_allow_html=True)
    st.progress(virus_hp_percent)

st.markdown("---")

# Nhật ký chiến đấu
st.markdown("### 📜 NHẬT KÝ CHIẾN ĐẤU")
log_container = st.container()
with log_container:
    for msg in game["combat_log"][-8:]:
        if "💥" in msg:
            st.markdown(f"<p style='color: #ff8888;'>⚔️ {msg}</p>", unsafe_allow_html=True)
        elif "💚" in msg:
            st.markdown(f"<p style='color: #88ff88;'>💚 {msg}</p>", unsafe_allow_html=True)
        elif "🌟" in msg:
            st.markdown(f"<p style='color: #ffd700;'>✨ {msg}</p>", unsafe_allow_html=True)
        elif "🏆" in msg:
            st.markdown(f"<p style='color: #ffd700; font-size: 18px;'>🏆 {msg}</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='color: #cccccc;'>📌 {msg}</p>", unsafe_allow_html=True)

st.markdown("---")

# Nút hành động
col_a, col_b, col_c = st.columns(3)

# Hàm xử lý tấn công
def do_attack():
    virus = VIRUSES[game["current_level"] - 1]
    damage = random.randint(game["player_attack"] - 3, game["player_attack"] + 3)
    is_crit = random.random() < 0.2
    if is_crit:
        damage = int(damage * 1.5)
    
    game["current_virus_hp"] -= damage
    game["combat_log"].append(f"{'🔥 CHÍ MẠNG! ' if is_crit else '💥'}Bạn tấn công gây {damage} sát thương!")
    
    if game["current_virus_hp"] <= 0:
        # Thắng virus
        game["score"] += 100 * game["current_level"]
        game["player_exp"] += virus["exp"]
        game["combat_log"].append(f"🎉 {virus['name']} đã bị đánh bại! +{100 * game['current_level']} điểm!")
        
        # Level up nhân vật
        if game["player_exp"] >= game["player_exp_needed"]:
            game["player_level"] += 1
            game["player_exp"] -= game["player_exp_needed"]
            game["player_exp_needed"] = int(game["player_exp_needed"] * 1.2)
            game["player_attack"] += 3
            game["player_max_hp"] += 20
            game["player_hp"] = min(game["player_hp"] + 10, game["player_max_hp"])
            game["combat_log"].append(f"🌟 LEVEL UP! Cấp {game['player_level']}! 🌟")
        
        if game["current_level"] < 5:
            game["current_level"] += 1
            game["current_virus_hp"] = VIRUSES[game["current_level"] - 1]["hp"]
            game["combat_log"].append(f"⚔️ Bước vào level {game['current_level']}!")
        else:
            game["game_active"] = False
            game["victory"] = True
            save_score(game["player_name"], game["score"])
            game["combat_log"].append(f"🏆 CHIẾN THẮNG! Bạn đã cứu thế giới! 🏆")
    else:
        # Virus tấn công lại
        virus_damage = random.randint(max(1, virus["attack"] - 3), virus["attack"])
        game["player_hp"] -= virus_damage
        game["combat_log"].append(f"💀 Virus tấn công lại, bạn mất {virus_damage} HP!")

# Hàm xử lý hồi máu
def do_heal():
    if game["score"] >= 20:
        heal_amount = random.randint(15, 30)
        game["player_hp"] = min(game["player_hp"] + heal_amount, game["player_max_hp"])
        game["score"] -= 20
        game["combat_log"].append(f"💚 Hồi máu {heal_amount} HP! (tốn 20 điểm, còn {game['score']} điểm)")
        
        virus = VIRUSES[game["current_level"] - 1]
        virus_damage = random.randint(max(1, virus["attack"] - 2), virus["attack"])
        game["player_hp"] -= virus_damage
        game["combat_log"].append(f"💀 Virus tấn công, bạn mất {virus_damage} HP!")
    else:
        game["combat_log"].append(f"❌ Không đủ điểm! Cần 20 điểm, bạn có {game['score']} điểm!")

# Hàm xử lý phòng thủ
def do_defend():
    virus = VIRUSES[game["current_level"] - 1]
    virus_damage = random.randint(max(1, virus["attack"] - 5), max(2, virus["attack"] - 2))
    virus_damage = max(1, virus_damage)
    game["player_hp"] -= virus_damage
    game["combat_log"].append(f"🛡️ Bạn phòng thủ, giảm sát thương!")
    game["combat_log"].append(f"💀 Virus tấn công, bạn mất {virus_damage} HP!")

with col_a:
    if st.button("⚔️ TẤN CÔNG ⚔️", key=f"attack_{game['reset_counter']}", use_container_width=True):
        do_attack()
        st.rerun()

with col_b:
    if st.button("💊 HỒI MÁU (20đ) 💊", key=f"heal_{game['reset_counter']}", use_container_width=True):
        do_heal()
        st.rerun()

with col_c:
    if st.button("🛡️ PHÒNG THỦ 🛡️", key=f"defend_{game['reset_counter']}", use_container_width=True):
        do_defend()
        st.rerun()
