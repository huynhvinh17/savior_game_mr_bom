# combat_game.py
import streamlit as st
import time
import random
import json
import os
from datetime import datetime

# ================== CẤU HÌNH GAME ==================
class GameConfig:
    GAME_NAME = "⚔️ PYTHON SAVIOR - CHIẾN ĐẤU GIẢI CỨU ⚔️"
    DATA_FILE = "combat_scores.json"
    
    VIRUSES = [
        {"name": "VIRUS LOGIC", "level": 1, "hp": 30, "attack": 5, "exp": 50, "icon": "🦠"},
        {"name": "VIRUS LOOP", "level": 2, "hp": 50, "attack": 8, "exp": 80, "icon": "🧬"},
        {"name": "VIRUS FUNCTION", "level": 3, "hp": 70, "attack": 12, "exp": 120, "icon": "🎯"},
        {"name": "VIRUS LIST", "level": 4, "hp": 100, "attack": 15, "exp": 180, "icon": "📦"},
        {"name": "BOSS DICTIONARY", "level": 5, "hp": 150, "attack": 20, "exp": 300, "icon": "🏆"},
    ]

# ================== QUẢN LÝ ĐIỂM ==================
class ScoreManager:
    def __init__(self):
        self.data_file = GameConfig.DATA_FILE
        self.scores = self.load_scores()
    
    def load_scores(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_scores(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.scores, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def add_score(self, player_name, level, score, time_taken):
        record = {
            "name": player_name,
            "level": level,
            "score": score,
            "time": time_taken,
            "date": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        self.scores.append(record)
        self.save_scores()
    
    def get_top_scores(self, limit=10):
        sorted_scores = sorted(self.scores, key=lambda x: x["score"], reverse=True)
        return sorted_scores[:limit]

# ================== GAME ENGINE ==================
class CombatGame:
    def __init__(self):
        self.score_manager = ScoreManager()
        self.reset_game()
    
    def reset_game(self):
        self.current_level = 1
        self.player_name = ""
        self.player_hp = 100
        self.player_max_hp = 100
        self.player_attack = 12
        self.player_level = 1
        self.player_exp = 0
        self.player_exp_needed = 100
        self.score = 0
        self.start_time = None
        self.game_active = False
        self.victory = False
        self.current_virus = None
        self.current_virus_hp = 0
        self.combat_log = []
    
    def start_game(self, player_name):
        self.reset_game()
        self.player_name = player_name
        self.game_active = True
        self.start_time = time.time()
        self.load_virus()
        return True
    
    def load_virus(self):
        if self.current_level <= len(GameConfig.VIRUSES):
            self.current_virus = GameConfig.VIRUSES[self.current_level - 1].copy()
            self.current_virus_hp = self.current_virus["hp"]
        return self.current_virus
    
    def get_current_virus(self):
        if self.current_virus is None:
            self.load_virus()
        return self.current_virus
    
    def player_attack_action(self):
        virus = self.get_current_virus()
        
        is_crit = random.random() < 0.2
        damage = random.randint(self.player_attack - 3, self.player_attack + 3)
        if is_crit:
            damage = int(damage * 1.5)
        
        self.current_virus_hp -= damage
        
        result = {
            "action": "attack",
            "damage": damage,
            "is_crit": is_crit,
            "virus_hp_remaining": max(0, self.current_virus_hp),
            "virus_defeated": self.current_virus_hp <= 0
        }
        
        if result["virus_defeated"]:
            exp_gain = virus["exp"]
            self.player_exp += exp_gain
            self.score += 100 * self.current_level
            
            level_up = False
            if self.player_exp >= self.player_exp_needed:
                self.player_level += 1
                self.player_exp -= self.player_exp_needed
                self.player_exp_needed = int(self.player_exp_needed * 1.2)
                self.player_attack += 3
                self.player_max_hp += 20
                self.player_hp = min(self.player_hp + 10, self.player_max_hp)
                level_up = True
            
            if self.current_level < 5:
                self.current_level += 1
                self.load_virus()
                result["next_level"] = True
                result["level_up"] = level_up
                result["exp_gain"] = exp_gain
                result["new_level"] = self.current_level
            else:
                self.game_active = False
                self.victory = True
                time_taken = int(time.time() - self.start_time)
                self.score_manager.add_score(self.player_name, 5, self.score, time_taken)
                result["victory"] = True
                result["time_taken"] = time_taken
                result["final_score"] = self.score
        else:
            virus_damage = random.randint(max(1, virus["attack"] - 3), virus["attack"])
            self.player_hp -= virus_damage
            
            result["virus_attack"] = virus_damage
            result["player_hp_remaining"] = max(0, self.player_hp)
            
            if self.player_hp <= 0:
                self.game_active = False
                result["game_over"] = True
        
        return result
    
    def heal_action(self):
        if self.score >= 20:
            heal_amount = random.randint(15, 30)
            self.player_hp = min(self.player_hp + heal_amount, self.player_max_hp)
            self.score -= 20
            
            virus = self.get_current_virus()
            virus_damage = random.randint(max(1, virus["attack"] - 2), virus["attack"])
            self.player_hp -= virus_damage
            
            result = {
                "action": "heal",
                "heal_amount": heal_amount,
                "virus_attack": virus_damage,
                "player_hp_remaining": max(0, self.player_hp),
                "score_cost": 20,
                "current_score": self.score
            }
            
            if self.player_hp <= 0:
                self.game_active = False
                result["game_over"] = True
            
            return result
        else:
            return {"action": "heal", "insufficient": True, "need": 20, "current": self.score}
    
    def defend_action(self):
        virus = self.get_current_virus()
        virus_damage = random.randint(max(1, virus["attack"] - 5), max(2, virus["attack"] - 2))
        virus_damage = max(1, virus_damage)
        self.player_hp -= virus_damage
        
        result = {
            "action": "defend",
            "damage_reduced": True,
            "virus_attack": virus_damage,
            "player_hp_remaining": max(0, self.player_hp)
        }
        
        if self.player_hp <= 0:
            self.game_active = False
            result["game_over"] = True
        
        return result

# ================== GIAO DIỆN ==================

def setup_page():
    st.set_page_config(
        page_title="Python Savior - Chiến Đấu Giải Cứu",
        page_icon="⚔️",
        layout="wide"
    )
    
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0a0a0a 0%, #0d1b2a 100%); }
    .game-title {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #1b263b 0%, #415a77 100%);
        border-radius: 20px;
        border: 2px solid #ff4444;
        margin-bottom: 20px;
    }
    .virus-card {
        background: linear-gradient(135deg, #4a0000 0%, #8b0000 100%);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        border: 2px solid #ff0000;
    }
    .player-card {
        background: linear-gradient(135deg, #0d3b0d 0%, #1a5c1a 100%);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        border: 2px solid #00ff88;
    }
    .stButton > button {
        background: linear-gradient(135deg, #ff6600, #ff3300);
        color: white;
        font-size: 18px;
        font-weight: bold;
        border: none;
        border-radius: 10px;
        padding: 12px;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

def display_header():
    st.markdown("""
    <div class="game-title">
        <h1 style='color: #ff4444; margin: 0;'>⚔️ PYTHON SAVIOR - CHIẾN ĐẤU ⚔️</h1>
        <h3 style='color: #ffffff;'>Đánh bay virus máy tính, cứu thế giới!</h3>
        <p style='color: #aaa;'>⚡ Chọn hành động thông minh để chiến thắng ⚡</p>
    </div>
    """, unsafe_allow_html=True)

def display_battle_status(game):
    # Lấy virus hiện tại an toàn
    virus = game.get_current_virus()
    
    # Kiểm tra nếu virus tồn tại
    if virus is not None:
        virus_hp_percent = game.current_virus_hp / virus["hp"] if virus["hp"] > 0 else 0
        virus_name = virus.get("name", "UNKNOWN")
        virus_icon = virus.get("icon", "🦠")
        virus_attack = virus.get("attack", 5)
        virus_level = virus.get("level", game.current_level)
        virus_hp_current = max(0, game.current_virus_hp)
        virus_hp_max = virus.get("hp", 30)
    else:
        virus_hp_percent = 0
        virus_name = "??? VIRUS ???"
        virus_icon = "🦠"
        virus_attack = 5
        virus_level = game.current_level
        virus_hp_current = 0
        virus_hp_max = 30
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Avatar người chơi theo level
        player_avatar_list = ["🐣", "⚔️", "🦸", "🦸‍♂️", "🦸‍♂️✨", "👑"]
        player_avatar = player_avatar_list[min(game.player_level, 5)]
        
        st.markdown(f"""
        <div class="player-card">
            <div style='font-size: 48px;'>{player_avatar}</div>
            <h3>⚔️ {game.player_name} ⚔️</h3>
            <p>❤️ HP: {max(0, game.player_hp)}/{game.player_max_hp}</p>
            <p>⚔️ Sát thương: {game.player_attack}</p>
            <p>⭐ Điểm: {game.score}</p>
            <p>📊 Cấp {game.player_level} | EXP: {game.player_exp}/{game.player_exp_needed}</p>
        </div>
        """, unsafe_allow_html=True)
        st.progress(max(0, game.player_hp) / game.player_max_hp if game.player_max_hp > 0 else 1)
    
    with col2:
        st.markdown(f"""
        <div class="virus-card">
            <div style='font-size: 48px;'>{virus_icon}</div>
            <h3>{virus_name}</h3>
            <p>💀 HP: {virus_hp_current}/{virus_hp_max}</p>
            <p>⚔️ Sát thương: {virus_attack}/đòn</p>
            <p>🎯 Level: {virus_level}/5</p>
        </div>
        """, unsafe_allow_html=True)
        st.progress(virus_hp_percent)

def display_combat_log(combat_log):
    st.markdown("### 📜 NHẬT KÝ CHIẾN ĐẤU")
    
    if combat_log:
        for msg in combat_log[-8:]:
            if "💥" in msg or "tấn công" in msg:
                st.markdown(f"<p style='color: #ff8888;'>⚔️ {msg}</p>", unsafe_allow_html=True)
            elif "❤️" in msg or "HỒI" in msg:
                st.markdown(f"<p style='color: #88ff88;'>💚 {msg}</p>", unsafe_allow_html=True)
            elif "🌟" in msg or "LEVEL UP" in msg:
                st.markdown(f"<p style='color: #ffd700;'>✨ {msg}</p>", unsafe_allow_html=True)
            elif "🏆" in msg or "CHIẾN THẮNG" in msg:
                st.markdown(f"<p style='color: #ffd700; font-size: 18px;'>🏆 {msg}</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='color: #cccccc;'>📌 {msg}</p>", unsafe_allow_html=True)
    else:
        st.info("⚔️ Hãy bắt đầu chiến đấu!")

def display_leaderboard(score_manager):
    st.markdown("### 🏆 BẢNG XẾP HẠNG 🏆")
    
    top_scores = score_manager.get_top_scores(10)
    if top_scores:
        for i, s in enumerate(top_scores):
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
            st.markdown(f"{medal} **{s['name']}** - {s['score']} điểm - 📅 {s['date']}")
    else:
        st.info("Chưa có ai cứu thế giới! Hãy là người đầu tiên!")

def display_game_over():
    st.markdown("""
    <div style='text-align: center; padding: 40px; background: #4a0000; border-radius: 20px;'>
        <h1 style='color: #ff4444;'>💀 GAME OVER 💀</h1>
        <p style='color: white;'>Virus máy tính đã chiếm thế giới...</p>
        <p style='color: #ffaa00;'>Hãy chiến đấu thông minh hơn để cứu nhân loại!</p>
    </div>
    """, unsafe_allow_html=True)

def display_victory(game):
    st.markdown(f"""
    <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #00aa44, #006400); border-radius: 20px;'>
        <h1 style='color: #ffd700;'>🏆 CHIẾN THẮNG! 🏆</h1>
        <h2 style='color: white;'>Bạn đã cứu thế giới khỏi virus máy tính!</h2>
        <p style='color: #fff; font-size: 24px;'>⭐ Điểm số: {game.score} ⭐</p>
        <p style='color: #ffd700;'>🏅 Bạn xứng đáng là Chiến binh xuất sắc nhất! 🏅</p>
    </div>
    """, unsafe_allow_html=True)

# ================== MAIN ==================
def main():
    setup_page()
    display_header()
    
    # Khởi tạo session state
    if "game" not in st.session_state:
        st.session_state.game = CombatGame()
        st.session_state.game_active = False
        st.session_state.show_leaderboard = False
        st.session_state.page_id = random.randint(0, 999999)
    
    page_id = st.session_state.page_id
    game = st.session_state.game
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎮 MENU")
        if st.button("🆕 BẮT ĐẦU MỚI", key=f"new_game_{page_id}"):
            st.session_state.game = CombatGame()
            st.session_state.game_active = False
            st.session_state.show_leaderboard = False
            st.session_state.page_id = random.randint(0, 999999)
            st.rerun()
        
        st.markdown("---")
        
        st.markdown("### 📖 HƯỚNG DẪN")
        st.markdown("""
        - ⚔️ **Tấn công** → Gây 9-15 sát thương
        - 💊 **Hồi máu** → Hồi 15-30 HP (tốn 20đ)
        - 🛡️ **Phòng thủ** → Giảm sát thương
        - 🏆 **Thắng 5 level** → Cứu thế giới!
        """)
        
        st.markdown("---")
        display_leaderboard(game.score_manager)
    
    if st.session_state.show_leaderboard:
        st.markdown("## 🏆 BẢNG XẾP HẠNG TOÀN THỜI GIAN 🏆")
        top = game.score_manager.get_top_scores(20)
        if top:
            for i, s in enumerate(top):
                medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
                st.markdown(f"{medal} **{s['name']}** - {s['score']} điểm - 📅 {s['date']}")
        if st.button("🔙 QUAY LẠI GAME", key=f"back_{page_id}"):
            st.session_state.show_leaderboard = False
            st.rerun()
        return
    
    # Màn hình bắt đầu game
    if not st.session_state.game_active and not game.game_active:
        st.markdown("""
        <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 20px;'>
            <div style='font-size: 80px;'>⚔️ 🐍 ⚔️</div>
            <h2>CHÀO MỪNG CHIẾN BINH!</h2>
            <p>Thế giới đang bị virus máy tính tấn công! Hãy chiến đấu để giải cứu!</p>
            <p style='color: #ffaa00;'>🎯 Mẹo: Tấn công thường xuyên, hồi máu khi HP thấp!</p>
        </div>
        """, unsafe_allow_html=True)
        
        name = st.text_input("👤 Nhập tên chiến binh:", max_chars=20, key=f"player_name_{page_id}")
        if st.button("🚀 BẮT ĐẦU CHIẾN ĐẤU", key=f"start_{page_id}", use_container_width=True):
            if name and name.strip():
                game.start_game(name.strip())
                st.session_state.game_active = True
                game.combat_log = [f"🦸‍♂️ {name} bước vào trận chiến!"]
                st.rerun()
            else:
                st.error("❌ Hãy nhập tên của bạn!")
        return
    
    # Kiểm tra game over
    if game.player_hp <= 0:
        display_game_over()
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 CHƠI LẠI", key=f"play_again_over_{page_id}", use_container_width=True):
                st.session_state.game = CombatGame()
                st.session_state.game_active = False
                st.session_state.page_id = random.randint(0, 999999)
                st.rerun()
        return
    
    # Kiểm tra victory
    if game.victory:
        display_victory(game)
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 CHƠI LẠI", key=f"play_again_victory_{page_id}", use_container_width=True):
                st.session_state.game = CombatGame()
                st.session_state.game_active = False
                st.session_state.page_id = random.randint(0, 999999)
                st.rerun()
        with col2:
            if st.button("🏆 BẢNG XẾP HẠNG", key=f"view_rank_{page_id}", use_container_width=True):
                st.session_state.show_leaderboard = True
                st.rerun()
        return
    
    # Hiển thị trạng thái chiến đấu
    display_battle_status(game)
    st.markdown("---")
    display_combat_log(game.combat_log)
    st.markdown("---")
    
    # Nút hành động
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⚔️ TẤN CÔNG ⚔️", key=f"attack_{page_id}", use_container_width=True):
            result = game.player_attack_action()
            
            if result["action"] == "attack":
                if result.get("is_crit"):
                    game.combat_log.append(f"🔥 CHÍ MẠNG! Bạn tấn công gây {result['damage']} sát thương!")
                else:
                    game.combat_log.append(f"💥 Bạn tấn công gây {result['damage']} sát thương!")
                
                if result.get("virus_defeated"):
                    virus_name = game.current_virus["name"] if game.current_virus else "Virus"
                    game.combat_log.append(f"🎉 {virus_name} đã bị đánh bại! 🎉")
                    if result.get("exp_gain"):
                        game.combat_log.append(f"✨ Nhận {result['exp_gain']} EXP! ✨")
                    if result.get("level_up"):
                        game.combat_log.append(f"🌟 LEVEL UP! Cấp {game.player_level}! 🌟")
                    if result.get("next_level"):
                        game.combat_log.append(f"⚔️ Bước vào level {result['new_level']}!")
                    if result.get("victory"):
                        game.combat_log.append(f"🏆 CHIẾN THẮNG! Bạn đã cứu thế giới! 🏆")
                else:
                    game.combat_log.append(f"💀 Virus tấn công lại, bạn mất {result['virus_attack']} HP!")
            
            if result.get("game_over"):
                game.combat_log.append("💀 GAME OVER! Bạn đã thất bại... 💀")
            
            time.sleep(0.3)
            st.rerun()
    
    with col2:
        if st.button("💊 HỒI MÁU (20đ) 💊", key=f"heal_{page_id}", use_container_width=True):
            result = game.heal_action()
            
            if result.get("insufficient"):
                game.combat_log.append(f"❌ Không đủ điểm! Cần {result['need']} điểm, bạn có {result['current']} điểm!")
            else:
                game.combat_log.append(f"💚 Hồi máu {result['heal_amount']} HP! (tốn 20 điểm, còn {result['current_score']} điểm)")
                game.combat_log.append(f"💀 Virus tấn công, bạn mất {result['virus_attack']} HP!")
                
                if result.get("game_over"):
                    game.combat_log.append("💀 GAME OVER! Bạn đã thất bại... 💀")
            
            time.sleep(0.3)
            st.rerun()
    
    with col3:
        if st.button("🛡️ PHÒNG THỦ 🛡️", key=f"defend_{page_id}", use_container_width=True):
            result = game.defend_action()
            
            game.combat_log.append(f"🛡️ Bạn phòng thủ, giảm sát thương nhận vào!")
            game.combat_log.append(f"💀 Virus tấn công, bạn mất {result['virus_attack']} HP!")
            
            if result.get("game_over"):
                game.combat_log.append("💀 GAME OVER! Bạn đã thất bại... 💀")
            
            time.sleep(0.3)
            st.rerun()

if __name__ == "__main__":
    main()# combat_game.py
import streamlit as st
import time
import random
import json
import os
from datetime import datetime

# ================== CẤU HÌNH GAME ==================
class GameConfig:
    GAME_NAME = "⚔️ PYTHON SAVIOR - CHIẾN ĐẤU GIẢI CỨU ⚔️"
    DATA_FILE = "combat_scores.json"
    
    VIRUSES = [
        {"name": "VIRUS LOGIC", "level": 1, "hp": 30, "attack": 5, "exp": 50, "icon": "🦠", "emoji": "🧠"},
        {"name": "VIRUS LOOP", "level": 2, "hp": 50, "attack": 8, "exp": 80, "icon": "🧬", "emoji": "🔄"},
        {"name": "VIRUS FUNCTION", "level": 3, "hp": 70, "attack": 12, "exp": 120, "icon": "🎯", "emoji": "⚙️"},
        {"name": "VIRUS LIST", "level": 4, "hp": 100, "attack": 15, "exp": 180, "icon": "📦", "emoji": "📋"},
        {"name": "BOSS DICTIONARY", "level": 5, "hp": 150, "attack": 20, "exp": 300, "icon": "🏆", "emoji": "👑"},
    ]

# ================== QUẢN LÝ ĐIỂM ==================
class ScoreManager:
    def __init__(self):
        self.data_file = GameConfig.DATA_FILE
        self.scores = self.load_scores()
    
    def load_scores(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_scores(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.scores, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def add_score(self, player_name, level, score, time_taken):
        record = {
            "name": player_name,
            "level": level,
            "score": score,
            "time": time_taken,
            "date": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        self.scores.append(record)
        self.save_scores()
    
    def get_top_scores(self, limit=10):
        sorted_scores = sorted(self.scores, key=lambda x: x["score"], reverse=True)
        return sorted_scores[:limit]

# ================== GAME ENGINE ==================
class CombatGame:
    def __init__(self):
        self.score_manager = ScoreManager()
        self.reset_game()
    
    def reset_game(self):
        self.current_level = 1
        self.player_name = ""
        self.player_hp = 100
        self.player_max_hp = 100
        self.player_attack = 12
        self.player_level = 1
        self.player_exp = 0
        self.player_exp_needed = 100
        self.score = 0
        self.start_time = None
        self.game_active = False
        self.victory = False
        self.current_virus = None
        self.current_virus_hp = 0
        self.combat_log = []
    
    def start_game(self, player_name):
        self.reset_game()
        self.player_name = player_name
        self.game_active = True
        self.start_time = time.time()
        self.load_virus()
        return True
    
    def load_virus(self):
        if self.current_level <= len(GameConfig.VIRUSES):
            self.current_virus = GameConfig.VIRUSES[self.current_level - 1].copy()
            self.current_virus_hp = self.current_virus["hp"]
        return self.current_virus
    
    def get_current_virus(self):
        if self.current_virus is None:
            self.load_virus()
        return self.current_virus
    
    def player_attack_action(self):
        virus = self.get_current_virus()
        
        is_crit = random.random() < 0.2
        damage = random.randint(self.player_attack - 3, self.player_attack + 3)
        if is_crit:
            damage = int(damage * 1.5)
        
        self.current_virus_hp -= damage
        
        result = {
            "action": "attack",
            "damage": damage,
            "is_crit": is_crit,
            "virus_hp_remaining": max(0, self.current_virus_hp),
            "virus_defeated": self.current_virus_hp <= 0
        }
        
        if result["virus_defeated"]:
            exp_gain = virus["exp"]
            self.player_exp += exp_gain
            self.score += 100 * self.current_level
            
            level_up = False
            if self.player_exp >= self.player_exp_needed:
                self.player_level += 1
                self.player_exp -= self.player_exp_needed
                self.player_exp_needed = int(self.player_exp_needed * 1.2)
                self.player_attack += 3
                self.player_max_hp += 20
                self.player_hp = min(self.player_hp + 10, self.player_max_hp)
                level_up = True
            
            if self.current_level < 5:
                self.current_level += 1
                self.load_virus()
                result["next_level"] = True
                result["level_up"] = level_up
                result["exp_gain"] = exp_gain
                result["new_level"] = self.current_level
            else:
                self.game_active = False
                self.victory = True
                time_taken = int(time.time() - self.start_time)
                self.score_manager.add_score(self.player_name, 5, self.score, time_taken)
                result["victory"] = True
                result["time_taken"] = time_taken
                result["final_score"] = self.score
        else:
            virus_damage = random.randint(max(1, virus["attack"] - 3), virus["attack"])
            self.player_hp -= virus_damage
            
            result["virus_attack"] = virus_damage
            result["player_hp_remaining"] = max(0, self.player_hp)
            
            if self.player_hp <= 0:
                self.game_active = False
                result["game_over"] = True
        
        return result
    
    def heal_action(self):
        if self.score >= 20:
            heal_amount = random.randint(15, 30)
            self.player_hp = min(self.player_hp + heal_amount, self.player_max_hp)
            self.score -= 20
            
            virus = self.get_current_virus()
            virus_damage = random.randint(max(1, virus["attack"] - 2), virus["attack"])
            self.player_hp -= virus_damage
            
            result = {
                "action": "heal",
                "heal_amount": heal_amount,
                "virus_attack": virus_damage,
                "player_hp_remaining": max(0, self.player_hp),
                "score_cost": 20,
                "current_score": self.score
            }
            
            if self.player_hp <= 0:
                self.game_active = False
                result["game_over"] = True
            
            return result
        else:
            return {"action": "heal", "insufficient": True, "need": 20, "current": self.score}
    
    def defend_action(self):
        virus = self.get_current_virus()
        virus_damage = random.randint(max(1, virus["attack"] - 5), max(2, virus["attack"] - 2))
        virus_damage = max(1, virus_damage)
        self.player_hp -= virus_damage
        
        result = {
            "action": "defend",
            "damage_reduced": True,
            "virus_attack": virus_damage,
            "player_hp_remaining": max(0, self.player_hp)
        }
        
        if self.player_hp <= 0:
            self.game_active = False
            result["game_over"] = True
        
        return result

# ================== GIAO DIỆN ==================

def setup_page():
    st.set_page_config(
        page_title="Python Savior - Chiến Đấu Giải Cứu",
        page_icon="⚔️",
        layout="wide"
    )
    
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0a0a0a 0%, #0d1b2a 100%); }
    .game-title {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #1b263b 0%, #415a77 100%);
        border-radius: 20px;
        border: 2px solid #ff4444;
        margin-bottom: 20px;
    }
    .virus-card {
        background: linear-gradient(135deg, #4a0000 0%, #8b0000 100%);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        border: 2px solid #ff0000;
    }
    .player-card {
        background: linear-gradient(135deg, #0d3b0d 0%, #1a5c1a 100%);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        border: 2px solid #00ff88;
    }
    .stButton > button {
        background: linear-gradient(135deg, #ff6600, #ff3300);
        color: white;
        font-size: 18px;
        font-weight: bold;
        border: none;
        border-radius: 10px;
        padding: 12px;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

def display_header():
    st.markdown("""
    <div class="game-title">
        <h1 style='color: #ff4444; margin: 0;'>⚔️ PYTHON SAVIOR - CHIẾN ĐẤU ⚔️</h1>
        <h3 style='color: #ffffff;'>Đánh bay virus máy tính, cứu thế giới!</h3>
        <p style='color: #aaa;'>⚡ Chọn hành động thông minh để chiến thắng ⚡</p>
    </div>
    """, unsafe_allow_html=True)

def display_battle_status(game):
    virus = game.get_current_virus()
    if virus:
        virus_hp_percent = game.current_virus_hp / virus["hp"] if virus["hp"] > 0 else 0
    else:
        virus_hp_percent = 0
    
    col1, col2 = st.columns(2)
    
    with col1:
        player_avatar = ["🐣", "⚔️", "🦸", "🦸‍♂️", "🦸‍♂️✨", "👑"][min(game.player_level, 5)]
        
        st.markdown(f"""
        <div class="player-card">
            <div style='font-size: 48px;'>{player_avatar}</div>
            <h3>⚔️ {game.player_name} ⚔️</h3>
            <p>❤️ HP: {max(0, game.player_hp)}/{game.player_max_hp}</p>
            <p>⚔️ Sát thương: {game.player_attack}</p>
            <p>⭐ Điểm: {game.score}</p>
            <p>📊 Cấp {game.player_level} | EXP: {game.player_exp}/{game.player_exp_needed}</p>
        </div>
        """, unsafe_allow_html=True)
        st.progress(max(0, game.player_hp) / game.player_max_hp if game.player_max_hp > 0 else 1)
    
    with col2:
        virus_avatar = virus["icon"] if virus else "🦠"
        st.markdown(f"""
        <div class="virus-card">
            <div style='font-size: 48px;'>{virus_avatar} {virus['emoji'] if virus else ''}</div>
            <h3>{virus['name'] if virus else '???'}</h3>
            <p>💀 HP: {max(0, game.current_virus_hp)}/{virus["hp"] if virus else 0}</p>
            <p>⚔️ Sát thương: {virus['attack'] if virus else 0}/đòn</p>
            <p>🎯 Level: {virus['level'] if virus else 0}/5</p>
        </div>
        """, unsafe_allow_html=True)
        st.progress(virus_hp_percent)

def display_combat_log(combat_log):
    st.markdown("### 📜 NHẬT KÝ CHIẾN ĐẤU")
    
    if combat_log:
        for msg in combat_log[-8:]:
            if "💥" in msg or "tấn công" in msg:
                st.markdown(f"<p style='color: #ff8888;'>⚔️ {msg}</p>", unsafe_allow_html=True)
            elif "❤️" in msg or "HỒI" in msg:
                st.markdown(f"<p style='color: #88ff88;'>💚 {msg}</p>", unsafe_allow_html=True)
            elif "🌟" in msg or "LEVEL UP" in msg:
                st.markdown(f"<p style='color: #ffd700;'>✨ {msg}</p>", unsafe_allow_html=True)
            elif "🏆" in msg or "CHIẾN THẮNG" in msg:
                st.markdown(f"<p style='color: #ffd700; font-size: 18px;'>🏆 {msg}</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='color: #cccccc;'>📌 {msg}</p>", unsafe_allow_html=True)
    else:
        st.info("⚔️ Hãy bắt đầu chiến đấu!")

def display_leaderboard(score_manager):
    st.markdown("### 🏆 BẢNG XẾP HẠNG 🏆")
    
    top_scores = score_manager.get_top_scores(10)
    if top_scores:
        for i, s in enumerate(top_scores):
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
            st.markdown(f"{medal} **{s['name']}** - {s['score']} điểm - 📅 {s['date']}")
    else:
        st.info("Chưa có ai cứu thế giới! Hãy là người đầu tiên!")

def display_game_over():
    st.markdown("""
    <div style='text-align: center; padding: 40px; background: #4a0000; border-radius: 20px;'>
        <h1 style='color: #ff4444;'>💀 GAME OVER 💀</h1>
        <p style='color: white;'>Virus máy tính đã chiếm thế giới...</p>
        <p style='color: #ffaa00;'>Hãy chiến đấu thông minh hơn để cứu nhân loại!</p>
    </div>
    """, unsafe_allow_html=True)

def display_victory(game):
    st.markdown(f"""
    <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #00aa44, #006400); border-radius: 20px;'>
        <h1 style='color: #ffd700;'>🏆 CHIẾN THẮNG! 🏆</h1>
        <h2 style='color: white;'>Bạn đã cứu thế giới khỏi virus máy tính!</h2>
        <p style='color: #fff; font-size: 24px;'>⭐ Điểm số: {game.score} ⭐</p>
        <p style='color: #ffd700;'>🏅 Bạn xứng đáng là Chiến binh xuất sắc nhất! 🏅</p>
    </div>
    """, unsafe_allow_html=True)

# ================== MAIN ==================
def main():
    setup_page()
    display_header()
    
    # Khởi tạo session state
    if "game" not in st.session_state:
        st.session_state.game = CombatGame()
        st.session_state.game_active = False
        st.session_state.show_leaderboard = False
        st.session_state.page_id = random.randint(0, 999999)
    
    # Tạo unique id cho page để tránh trùng key
    page_id = st.session_state.page_id
    
    game = st.session_state.game
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎮 MENU")
        if st.button("🆕 BẮT ĐẦU MỚI", key=f"new_game_{page_id}"):
            st.session_state.game = CombatGame()
            st.session_state.game_active = False
            st.session_state.show_leaderboard = False
            st.session_state.page_id = random.randint(0, 999999)
            st.rerun()
        
        st.markdown("---")
        
        st.markdown("### 📖 HƯỚNG DẪN")
        st.markdown("""
        - ⚔️ **Tấn công** → Gây 9-15 sát thương
        - 💊 **Hồi máu** → Hồi 15-30 HP (tốn 20đ)
        - 🛡️ **Phòng thủ** → Giảm sát thương
        - 🏆 **Thắng 5 level** → Cứu thế giới!
        """)
        
        st.markdown("---")
        display_leaderboard(game.score_manager)
    
    if st.session_state.show_leaderboard:
        st.markdown("## 🏆 BẢNG XẾP HẠNG TOÀN THỜI GIAN 🏆")
        top = game.score_manager.get_top_scores(20)
        if top:
            for i, s in enumerate(top):
                medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
                st.markdown(f"{medal} **{s['name']}** - {s['score']} điểm - 📅 {s['date']}")
        if st.button("🔙 QUAY LẠI GAME", key=f"back_{page_id}"):
            st.session_state.show_leaderboard = False
            st.rerun()
        return
    
    # Màn hình bắt đầu game
    if not st.session_state.game_active and not game.game_active:
        st.markdown("""
        <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 20px;'>
            <div style='font-size: 80px;'>⚔️ 🐍 ⚔️</div>
            <h2>CHÀO MỪNG CHIẾN BINH!</h2>
            <p>Thế giới đang bị virus máy tính tấn công! Hãy chiến đấu để giải cứu!</p>
            <p style='color: #ffaa00;'>🎯 Mẹo: Tấn công thường xuyên, hồi máu khi HP thấp!</p>
        </div>
        """, unsafe_allow_html=True)
        
        name = st.text_input("👤 Nhập tên chiến binh:", max_chars=20, key=f"player_name_{page_id}")
        if st.button("🚀 BẮT ĐẦU CHIẾN ĐẤU", key=f"start_{page_id}", use_container_width=True):
            if name and name.strip():
                game.start_game(name.strip())
                st.session_state.game_active = True
                game.combat_log = [f"🦸‍♂️ {name} bước vào trận chiến!"]
                st.rerun()
            else:
                st.error("❌ Hãy nhập tên của bạn!")
        return
    
    # Kiểm tra game over
    if game.player_hp <= 0:
        display_game_over()
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 CHƠI LẠI", key=f"play_again_over_{page_id}", use_container_width=True):
                st.session_state.game = CombatGame()
                st.session_state.game_active = False
                st.session_state.page_id = random.randint(0, 999999)
                st.rerun()
        return
    
    # Kiểm tra victory
    if game.victory:
        display_victory(game)
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 CHƠI LẠI", key=f"play_again_victory_{page_id}", use_container_width=True):
                st.session_state.game = CombatGame()
                st.session_state.game_active = False
                st.session_state.page_id = random.randint(0, 999999)
                st.rerun()
        with col2:
            if st.button("🏆 BẢNG XẾP HẠNG", key=f"view_rank_{page_id}", use_container_width=True):
                st.session_state.show_leaderboard = True
                st.rerun()
        return
    
    # Hiển thị trạng thái chiến đấu
    display_battle_status(game)
    st.markdown("---")
    display_combat_log(game.combat_log)
    st.markdown("---")
    
    # Nút hành động
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⚔️ TẤN CÔNG ⚔️", key=f"attack_{page_id}", use_container_width=True):
            result = game.player_attack_action()
            
            if result["action"] == "attack":
                if result.get("is_crit"):
                    game.combat_log.append(f"🔥 CHÍ MẠNG! Bạn tấn công gây {result['damage']} sát thương!")
                else:
                    game.combat_log.append(f"💥 Bạn tấn công gây {result['damage']} sát thương!")
                
                if result.get("virus_defeated"):
                    game.combat_log.append(f"🎉 {game.current_virus['name']} đã bị đánh bại! 🎉")
                    if result.get("exp_gain"):
                        game.combat_log.append(f"✨ Nhận {result['exp_gain']} EXP! ✨")
                    if result.get("level_up"):
                        game.combat_log.append(f"🌟 LEVEL UP! Cấp {game.player_level}! 🌟")
                    if result.get("next_level"):
                        game.combat_log.append(f"⚔️ Bước vào level {result['new_level']}!")
                    if result.get("victory"):
                        game.combat_log.append(f"🏆 CHIẾN THẮNG! Bạn đã cứu thế giới! 🏆")
                else:
                    game.combat_log.append(f"💀 Virus tấn công lại, bạn mất {result['virus_attack']} HP!")
            
            if result.get("game_over"):
                game.combat_log.append("💀 GAME OVER! Bạn đã thất bại... 💀")
            
            time.sleep(0.3)
            st.rerun()
    
    with col2:
        if st.button("💊 HỒI MÁU (20đ) 💊", key=f"heal_{page_id}", use_container_width=True):
            result = game.heal_action()
            
            if result.get("insufficient"):
                game.combat_log.append(f"❌ Không đủ điểm! Cần {result['need']} điểm, bạn có {result['current']} điểm!")
            else:
                game.combat_log.append(f"💚 Hồi máu {result['heal_amount']} HP! (tốn 20 điểm, còn {result['current_score']} điểm)")
                game.combat_log.append(f"💀 Virus tấn công, bạn mất {result['virus_attack']} HP!")
                
                if result.get("game_over"):
                    game.combat_log.append("💀 GAME OVER! Bạn đã thất bại... 💀")
            
            time.sleep(0.3)
            st.rerun()
    
    with col3:
        if st.button("🛡️ PHÒNG THỦ 🛡️", key=f"defend_{page_id}", use_container_width=True):
            result = game.defend_action()
            
            game.combat_log.append(f"🛡️ Bạn phòng thủ, giảm sát thương nhận vào!")
            game.combat_log.append(f"💀 Virus tấn công, bạn mất {result['virus_attack']} HP!")
            
            if result.get("game_over"):
                game.combat_log.append("💀 GAME OVER! Bạn đã thất bại... 💀")
            
            time.sleep(0.3)
            st.rerun()

if __name__ == "__main__":
    main()# combat_game.py
import streamlit as st
import time
import random
import json
import os
from datetime import datetime
import base64

# ================== CẤU HÌNH GAME ==================
class GameConfig:
    GAME_NAME = "⚔️ PYTHON SAVIOR - CHIẾN ĐẤU GIẢI CỨU ⚔️"
    DATA_FILE = "combat_scores.json"
    
    VIRUSES = [
        {"name": "VIRUS LOGIC", "level": 1, "hp": 30, "attack": 5, "exp": 50, "icon": "🦠", "emoji": "🧠"},
        {"name": "VIRUS LOOP", "level": 2, "hp": 50, "attack": 8, "exp": 80, "icon": "🧬", "emoji": "🔄"},
        {"name": "VIRUS FUNCTION", "level": 3, "hp": 70, "attack": 12, "exp": 120, "icon": "🎯", "emoji": "⚙️"},
        {"name": "VIRUS LIST", "level": 4, "hp": 100, "attack": 15, "exp": 180, "icon": "📦", "emoji": "📋"},
        {"name": "BOSS DICTIONARY", "level": 5, "hp": 150, "attack": 20, "exp": 300, "icon": "🏆", "emoji": "👑"},
    ]

# ================== QUẢN LÝ ĐIỂM ==================
class ScoreManager:
    def __init__(self):
        self.data_file = GameConfig.DATA_FILE
        self.scores = self.load_scores()
    
    def load_scores(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_scores(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.scores, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def add_score(self, player_name, level, score, time_taken):
        record = {
            "name": player_name,
            "level": level,
            "score": score,
            "time": time_taken,
            "date": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        self.scores.append(record)
        self.save_scores()
    
    def get_top_scores(self, limit=10):
        sorted_scores = sorted(self.scores, key=lambda x: x["score"], reverse=True)
        return sorted_scores[:limit]

# ================== GAME ENGINE ==================
class CombatGame:
    def __init__(self):
        self.score_manager = ScoreManager()
        self.reset_game()
    
    def reset_game(self):
        self.current_level = 1
        self.player_name = ""
        self.player_hp = 100
        self.player_max_hp = 100
        self.player_attack = 12
        self.player_level = 1
        self.player_exp = 0
        self.player_exp_needed = 100
        self.score = 0
        self.start_time = None
        self.game_active = False
        self.victory = False
        self.current_virus = None
        self.current_virus_hp = 0
        self.combat_log = []
        self.animation_trigger = None
    
    def start_game(self, player_name):
        self.reset_game()
        self.player_name = player_name
        self.game_active = True
        self.start_time = time.time()
        self.load_virus()
        return True
    
    def load_virus(self):
        if self.current_level <= len(GameConfig.VIRUSES):
            self.current_virus = GameConfig.VIRUSES[self.current_level - 1].copy()
            self.current_virus_hp = self.current_virus["hp"]
        return self.current_virus
    
    def get_current_virus(self):
        if self.current_virus is None:
            self.load_virus()
        return self.current_virus
    
    def player_attack_action(self):
        virus = self.get_current_virus()
        
        is_crit = random.random() < 0.2
        damage = random.randint(self.player_attack - 3, self.player_attack + 3)
        if is_crit:
            damage = int(damage * 1.5)
        
        self.current_virus_hp -= damage
        
        result = {
            "action": "attack",
            "damage": damage,
            "is_crit": is_crit,
            "virus_hp_remaining": max(0, self.current_virus_hp),
            "virus_defeated": self.current_virus_hp <= 0
        }
        
        if result["virus_defeated"]:
            exp_gain = virus["exp"]
            self.player_exp += exp_gain
            self.score += 100 * self.current_level
            
            level_up = False
            if self.player_exp >= self.player_exp_needed:
                self.player_level += 1
                self.player_exp -= self.player_exp_needed
                self.player_exp_needed = int(self.player_exp_needed * 1.2)
                self.player_attack += 3
                self.player_max_hp += 20
                self.player_hp = min(self.player_hp + 10, self.player_max_hp)
                level_up = True
            
            if self.current_level < 5:
                self.current_level += 1
                self.load_virus()
                result["next_level"] = True
                result["level_up"] = level_up
                result["exp_gain"] = exp_gain
                result["new_level"] = self.current_level
            else:
                self.game_active = False
                self.victory = True
                time_taken = int(time.time() - self.start_time)
                self.score_manager.add_score(self.player_name, 5, self.score, time_taken)
                result["victory"] = True
                result["time_taken"] = time_taken
                result["final_score"] = self.score
        else:
            virus_damage = random.randint(max(1, virus["attack"] - 3), virus["attack"])
            self.player_hp -= virus_damage
            
            result["virus_attack"] = virus_damage
            result["player_hp_remaining"] = max(0, self.player_hp)
            
            if self.player_hp <= 0:
                self.game_active = False
                result["game_over"] = True
        
        return result
    
    def heal_action(self):
        if self.score >= 20:
            heal_amount = random.randint(15, 30)
            self.player_hp = min(self.player_hp + heal_amount, self.player_max_hp)
            self.score -= 20
            
            virus = self.get_current_virus()
            virus_damage = random.randint(max(1, virus["attack"] - 2), virus["attack"])
            self.player_hp -= virus_damage
            
            result = {
                "action": "heal",
                "heal_amount": heal_amount,
                "virus_attack": virus_damage,
                "player_hp_remaining": max(0, self.player_hp),
                "score_cost": 20,
                "current_score": self.score
            }
            
            if self.player_hp <= 0:
                self.game_active = False
                result["game_over"] = True
            
            return result
        else:
            return {"action": "heal", "insufficient": True, "need": 20, "current": self.score}
    
    def defend_action(self):
        virus = self.get_current_virus()
        virus_damage = random.randint(max(1, virus["attack"] - 5), max(2, virus["attack"] - 2))
        virus_damage = max(1, virus_damage)
        self.player_hp -= virus_damage
        
        result = {
            "action": "defend",
            "damage_reduced": True,
            "virus_attack": virus_damage,
            "player_hp_remaining": max(0, self.player_hp)
        }
        
        if self.player_hp <= 0:
            self.game_active = False
            result["game_over"] = True
        
        return result

# ================== GIAO DIỆN VỚI ANIMATION ==================

def get_animation_html(animation_type):
    """Trả về HTML animation"""
    animations = {
        "attack": """
        <div style='text-align: center; animation: shake 0.3s ease-in-out;'>
            <h2 style='color: #ff6600; font-size: 28px;'>💥 CHÍNH XÁC! 💥</h2>
        </div>
        <style>
        @keyframes shake {
            0%,100% { transform: translateX(0); }
            25% { transform: translateX(-8px); }
            75% { transform: translateX(8px); }
        }
        </style>
        """,
        "crit": """
        <div style='text-align: center; animation: crit 0.5s ease-in-out;'>
            <h1 style='color: #ff0000; font-size: 36px; text-shadow: 0 0 10px #ff0000;'>🔥 CHÍ MẠNG! 🔥</h1>
        </div>
        <style>
        @keyframes crit {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.5); color: #ffff00; }
            100% { transform: scale(1); opacity: 1; }
        }
        </style>
        """,
        "heal": """
        <div style='text-align: center; animation: heal 0.3s ease-in-out;'>
            <h2 style='color: #00ff88; font-size: 28px;'>💚 HỒI MÁU! 💚</h2>
        </div>
        <style>
        @keyframes heal {
            0%,100% { transform: scale(1); }
            50% { transform: scale(1.2); }
        }
        </style>
        """,
        "defend": """
        <div style='text-align: center; animation: defend 0.3s ease-in-out;'>
            <h2 style='color: #4488ff; font-size: 28px;'>🛡️ PHÒNG THỦ! 🛡️</h2>
        </div>
        <style>
        @keyframes defend {
            0%,100% { transform: rotate(0deg); }
            25% { transform: rotate(-5deg); }
            75% { transform: rotate(5deg); }
        }
        </style>
        """,
        "level_up": """
        <div style='text-align: center; animation: levelup 0.6s ease-in-out;'>
            <h1 style='color: #ffd700; font-size: 40px; text-shadow: 0 0 20px #ffd700;'>🌟 LEVEL UP! 🌟</h1>
        </div>
        <style>
        @keyframes levelup {
            0% { transform: scale(0.5); opacity: 0; }
            50% { transform: scale(1.2); }
            100% { transform: scale(1); opacity: 1; }
        }
        </style>
        """,
        "victory": """
        <div style='text-align: center; animation: victory 1s ease-in-out;'>
            <h1 style='color: #ffd700; font-size: 48px; text-shadow: 0 0 20px #ffd700;'>🏆 CHIẾN THẮNG! 🏆</h1>
            <div style='font-size: 50px;'>🎉 🎊 🎉</div>
        </div>
        <style>
        @keyframes victory {
            0% { transform: scale(0); opacity: 0; }
            50% { transform: scale(1.2); }
            100% { transform: scale(1); opacity: 1; }
        }
        </style>
        """,
        "game_over": """
        <div style='text-align: center; animation: gameover 0.8s ease-in-out;'>
            <h1 style='color: #ff0000; font-size: 48px; text-shadow: 0 0 20px #ff0000;'>💀 GAME OVER 💀</h1>
        </div>
        <style>
        @keyframes gameover {
            0% { transform: translateY(-50px); opacity: 0; }
            100% { transform: translateY(0); opacity: 1; }
        }
        </style>
        """
    }
    return animations.get(animation_type, "")

def setup_page():
    st.set_page_config(
        page_title="Python Savior - Chiến Đấu Giải Cứu",
        page_icon="⚔️",
        layout="wide"
    )
    
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0a0a0a 0%, #0d1b2a 100%); }
    
    .game-title {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #1b263b 0%, #415a77 100%);
        border-radius: 20px;
        border: 2px solid #ff4444;
        margin-bottom: 20px;
        animation: glow 2s infinite;
    }
    
    @keyframes glow {
        0%,100% { box-shadow: 0 0 10px #ff4444; }
        50% { box-shadow: 0 0 30px #ff4444; }
    }
    
    .virus-card {
        background: linear-gradient(135deg, #4a0000 0%, #8b0000 100%);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        border: 2px solid #ff0000;
        animation: pulse 1s infinite;
    }
    
    @keyframes pulse {
        0%,100% { transform: scale(1); }
        50% { transform: scale(1.02); border-color: #ff6600; }
    }
    
    .player-card {
        background: linear-gradient(135deg, #0d3b0d 0%, #1a5c1a 100%);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        border: 2px solid #00ff88;
    }
    
    .health-bar {
        height: 20px;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #ff6600, #ff3300);
        color: white;
        font-size: 18px;
        font-weight: bold;
        border: none;
        border-radius: 10px;
        padding: 12px;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 15px #ff6600;
    }
    
    .log-entry {
        padding: 5px;
        margin: 3px 0;
        border-radius: 8px;
        animation: fadeIn 0.3s;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    </style>
    """, unsafe_allow_html=True)

def display_header():
    st.markdown("""
    <div class="game-title">
        <h1 style='color: #ff4444; margin: 0; font-size: 48px;'>⚔️ PYTHON SAVIOR - CHIẾN ĐẤU ⚔️</h1>
        <h3 style='color: #ffffff;'>Đánh bay virus máy tính, cứu thế giới!</h3>
        <p style='color: #aaa;'>⚡ Chọn hành động thông minh để chiến thắng ⚡</p>
    </div>
    """, unsafe_allow_html=True)

def display_battle_status(game):
    virus = game.get_current_virus()
    if virus:
        virus_hp_percent = game.current_virus_hp / virus["hp"] if virus["hp"] > 0 else 0
    else:
        virus_hp_percent = 0
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Avatar người chơi theo level
        player_avatar = ["🐣", "⚔️", "🦸", "🦸‍♂️", "🦸‍♂️✨", "👑"][min(game.player_level, 5)]
        
        st.markdown(f"""
        <div class="player-card">
            <div style='font-size: 48px;'>{player_avatar}</div>
            <h3>⚔️ {game.player_name} ⚔️</h3>
            <div style='background: #333; border-radius: 10px; margin: 10px 0;'>
                <div class="health-bar" style='width: {max(0, game.player_hp / game.player_max_hp * 100)}%; background: #00ff88; border-radius: 10px; text-align: center;'>
                    ❤️ {max(0, game.player_hp)}/{game.player_max_hp}
                </div>
            </div>
            <p>⚔️ Sát thương: {game.player_attack}</p>
            <p>⭐ Điểm: {game.score}</p>
            <p>📊 Cấp {game.player_level} | EXP: {game.player_exp}/{game.player_exp_needed}</p>
        </div>
        """, unsafe_allow_html=True)
        st.progress(max(0, game.player_hp) / game.player_max_hp if game.player_max_hp > 0 else 1)
    
    with col2:
        virus_avatar = virus["icon"] if virus else "🦠"
        st.markdown(f"""
        <div class="virus-card">
            <div style='font-size: 48px;'>{virus_avatar} {virus['emoji'] if virus else ''}</div>
            <h3>{virus['name'] if virus else '???'}</h3>
            <div style='background: #333; border-radius: 10px; margin: 10px 0;'>
                <div class="health-bar" style='width: {virus_hp_percent * 100}%; background: #ff0000; border-radius: 10px; text-align: center;'>
                    💀 {max(0, game.current_virus_hp)}/{virus["hp"] if virus else 0}
                </div>
            </div>
            <p>⚔️ Sát thương: {virus['attack'] if virus else 0}/đòn</p>
            <p>🎯 Level: {virus['level'] if virus else 0}/5</p>
        </div>
        """, unsafe_allow_html=True)
        st.progress(virus_hp_percent)

def display_combat_log(combat_log):
    st.markdown("### 📜 NHẬT KÝ CHIẾN ĐẤU")
    st.markdown('<div style="height: 150px; overflow-y: auto; background: #0a0a2e; border-radius: 10px; padding: 10px;">', unsafe_allow_html=True)
    
    if combat_log:
        for msg in combat_log[-8:]:
            if "💥" in msg or "tấn công" in msg:
                st.markdown(f"<div class='log-entry' style='color: #ff8888;'>⚔️ {msg}</div>", unsafe_allow_html=True)
            elif "❤️" in msg or "HỒI" in msg:
                st.markdown(f"<div class='log-entry' style='color: #88ff88;'>💚 {msg}</div>", unsafe_allow_html=True)
            elif "🌟" in msg or "LEVEL UP" in msg:
                st.markdown(f"<div class='log-entry' style='color: #ffd700; font-size: 16px;'>✨ {msg}</div>", unsafe_allow_html=True)
            elif "🏆" in msg or "CHIẾN THẮNG" in msg:
                st.markdown(f"<div class='log-entry' style='color: #ffd700; font-size: 18px;'>🏆 {msg}</div>", unsafe_allow_html=True)
            elif "💀" in msg or "GAME OVER" in msg:
                st.markdown(f"<div class='log-entry' style='color: #ff4444; font-size: 16px;'>💀 {msg}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='log-entry' style='color: #cccccc;'>📌 {msg}</div>", unsafe_allow_html=True)
    else:
        st.info("⚔️ Hãy bắt đầu chiến đấu!")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_leaderboard(score_manager):
    st.markdown("### 🏆 BẢNG XẾP HẠNG 🏆")
    
    top_scores = score_manager.get_top_scores(10)
    if top_scores:
        for i, s in enumerate(top_scores):
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
            st.markdown(f"""
            <div style='background: #1a1a2e; border-radius: 10px; padding: 8px; margin: 5px 0; border-left: 3px solid #ff4444;'>
                {medal} <b>{s['name']}</b> - {s['score']} điểm - 📅 {s['date']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Chưa có ai cứu thế giới! Hãy là người đầu tiên!")

def display_game_over(game):
    st.markdown(get_animation_html("game_over"), unsafe_allow_html=True)

def display_victory(game):
    st.markdown(get_animation_html("victory"), unsafe_allow_html=True)
    st.markdown(f"""
    <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #00aa44, #006400); border-radius: 20px; margin-top: 20px;'>
        <p style='color: #fff; font-size: 24px;'>⭐ Điểm số: {game.score} ⭐</p>
        <p style='color: #ffd700;'>🏅 Bạn xứng đáng là Chiến binh xuất sắc nhất! 🏅</p>
    </div>
    """, unsafe_allow_html=True)

# ================== MAIN ==================
def main():
    setup_page()
    display_header()
    
    # Khởi tạo session state
    if "game" not in st.session_state:
        st.session_state.game = CombatGame()
        st.session_state.game_active = False
        st.session_state.show_leaderboard = False
        st.session_state.animation = None
    
    game = st.session_state.game
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎮 MENU")
        if st.button("🆕 BẮT ĐẦU MỚI", key="new_game"):
            st.session_state.game = CombatGame()
            st.session_state.game_active = False
            st.session_state.show_leaderboard = False
            st.session_state.animation = None
            st.rerun()
        
        st.markdown("---")
        
        st.markdown("### 📖 HƯỚNG DẪN")
        st.markdown("""
        <div style='background: #1a1a2e; padding: 10px; border-radius: 10px;'>
            <p><span style='color:#ff8888'>⚔️ Tấn công</span> → Gây 9-15 sát thương<br>
            <span style='color:#88ff88'>💊 Hồi máu</span> → Hồi 15-30 HP (tốn 20đ)<br>
            <span style='color:#88aaff'>🛡️ Phòng thủ</span> → Giảm sát thương<br>
            <span style='color:#ffd700'>🏆 Thắng 5 level</span> → Cứu thế giới!</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        display_leaderboard(game.score_manager)
    
    if st.session_state.show_leaderboard:
        st.markdown("## 🏆 BẢNG XẾP HẠNG TOÀN THỜI GIAN 🏆")
        top = game.score_manager.get_top_scores(20)
        if top:
            for i, s in enumerate(top):
                medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
                st.markdown(f"{medal} **{s['name']}** - {s['score']} điểm - 📅 {s['date']}")
        if st.button("🔙 QUAY LẠI GAME", key="back"):
            st.session_state.show_leaderboard = False
            st.rerun()
        return
    
    # Màn hình bắt đầu game
    if not st.session_state.game_active and not game.game_active:
        st.markdown("""
        <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 20px;'>
            <div style='font-size: 80px;'>⚔️ 🐍 ⚔️</div>
            <h2>CHÀO MỪNG CHIẾN BINH!</h2>
            <p>Thế giới đang bị virus máy tính tấn công! Hãy chiến đấu để giải cứu!</p>
            <p style='color: #ffaa00;'>🎯 Mẹo: Tấn công thường xuyên, hồi máu khi HP thấp!</p>
        </div>
        """, unsafe_allow_html=True)
        
        name = st.text_input("👤 Nhập tên chiến binh:", max_chars=20, key="player_name_input")
        if st.button("🚀 BẮT ĐẦU CHIẾN ĐẤU", key="start_btn", use_container_width=True):
            if name and name.strip():
                game.start_game(name.strip())
                st.session_state.game_active = True
                game.combat_log = [f"🦸‍♂️ {name} bước vào trận chiến!"]
                st.rerun()
            else:
                st.error("❌ Hãy nhập tên của bạn!")
        return
    
    # Đang chơi - Kiểm tra các trạng thái
    if game.player_hp <= 0:
        display_game_over(game)
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 CHƠI LẠI", key="play_again_over", use_container_width=True):
                st.session_state.game = CombatGame()
                st.session_state.game_active = False
                st.rerun()
        return
    
    if game.victory:
        display_victory(game)
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 CHƠI LẠI", key="play_again_victory", use_container_width=True):
                st.session_state.game = CombatGame()
                st.session_state.game_active = False
                st.rerun()
        with col2:
            if st.button("🏆 BẢNG XẾP HẠNG", key="view_rank", use_container_width=True):
                st.session_state.show_leaderboard = True
                st.rerun()
        return
    
    # Hiển thị trạng thái chiến đấu
    display_battle_status(game)
    st.markdown("---")
    display_combat_log(game.combat_log)
    st.markdown("---")
    
    # Nút hành động
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⚔️ TẤN CÔNG ⚔️", key="attack_btn", use_container_width=True):
            result = game.player_attack_action()
            
            if result["action"] == "attack":
                if result.get("is_crit"):
                    st.markdown(get_animation_html("crit"), unsafe_allow_html=True)
                    game.combat_log.append(f"🔥 CHÍ MẠNG! 🔥 Bạn tấn công gây {result['damage']} sát thương!")
                else:
                    st.markdown(get_animation_html("attack"), unsafe_allow_html=True)
                    game.combat_log.append(f"💥 Bạn tấn công gây {result['damage']} sát thương!")
                
                if result.get("virus_defeated"):
                    game.combat_log.append(f"🎉 {game.current_virus['name']} đã bị đánh bại! 🎉")
                    if result.get("exp_gain"):
                        game.combat_log.append(f"✨ Nhận {result['exp_gain']} EXP! ✨")
                    if result.get("level_up"):
                        st.markdown(get_animation_html("level_up"), unsafe_allow_html=True)
                        game.combat_log.append(f"🌟 LEVEL UP! Cấp {game.player_level}! 🌟")
                    if result.get("next_level"):
                        game.combat_log.append(f"⚔️ Bước vào level {result['new_level']}!")
                    if result.get("victory"):
                        game.combat_log.append(f"🏆 CHIẾN THẮNG! Bạn đã cứu thế giới! 🏆")
                else:
                    game.combat_log.append(f"💀 Virus tấn công lại, bạn mất {result['virus_attack']} HP!")
            
            if result.get("game_over"):
                game.combat_log.append("💀 GAME OVER! Bạn đã thất bại... 💀")
            
            time.sleep(0.3)
            st.rerun()
    
    with col2:
        if st.button("💊 HỒI MÁU 💊", key="heal_btn", use_container_width=True):
            result = game.heal_action()
            
            if result.get("insufficient"):
                game.combat_log.append(f"❌ Không đủ điểm! Cần {result['need']} điểm, bạn có {result['current']} điểm!")
            else:
                st.markdown(get_animation_html("heal"), unsafe_allow_html=True)
                game.combat_log.append(f"💚 Hồi máu {result['heal_amount']} HP! (tốn 20 điểm, còn {result['current_score']} điểm)")
                game.combat_log.append(f"💀 Virus tấn công, bạn mất {result['virus_attack']} HP!")
                
                if result.get("game_over"):
                    game.combat_log.append("💀 GAME OVER! Bạn đã thất bại... 💀")
            
            time.sleep(0.3)
            st.rerun()
    
    with col3:
        if st.button("🛡️ PHÒNG THỦ 🛡️", key="defend_btn", use_container_width=True):
            result = game.defend_action()
            
            st.markdown(get_animation_html("defend"), unsafe_allow_html=True)
            game.combat_log.append(f"🛡️ Bạn phòng thủ, giảm sát thương nhận vào!")
            game.combat_log.append(f"💀 Virus tấn công, bạn mất {result['virus_attack']} HP!")
            
            if result.get("game_over"):
                game.combat_log.append("💀 GAME OVER! Bạn đã thất bại... 💀")
            
            time.sleep(0.3)
            st.rerun()

if __name__ == "__main__":
    main()# combat_game.py
import streamlit as st
import time
import random
import json
import os
from datetime import datetime

# ================== CẤU HÌNH GAME ==================
class GameConfig:
    GAME_NAME = "⚔️ PYTHON SAVIOR - CHIẾN ĐẤU GIẢI CỨU ⚔️"
    DATA_FILE = "combat_scores.json"
    
    VIRUSES = [
        {"name": "🦠 VIRUS LOGIC", "level": 1, "hp": 30, "attack": 5, "exp": 50, "icon": "🦠"},
        {"name": "🧬 VIRUS LOOP", "level": 2, "hp": 50, "attack": 8, "exp": 80, "icon": "🧬"},
        {"name": "🎯 VIRUS FUNCTION", "level": 3, "hp": 70, "attack": 12, "exp": 120, "icon": "🎯"},
        {"name": "📦 VIRUS LIST", "level": 4, "hp": 100, "attack": 15, "exp": 180, "icon": "📦"},
        {"name": "🏆 BOSS DICTIONARY", "level": 5, "hp": 150, "attack": 20, "exp": 300, "icon": "🏆"},
    ]

# ================== QUẢN LÝ ĐIỂM ==================
class ScoreManager:
    def __init__(self):
        self.data_file = GameConfig.DATA_FILE
        self.scores = self.load_scores()
    
    def load_scores(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_scores(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.scores, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def add_score(self, player_name, level, score, time_taken):
        record = {
            "name": player_name,
            "level": level,
            "score": score,
            "time": time_taken,
            "date": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        self.scores.append(record)
        self.save_scores()
    
    def get_top_scores(self, limit=10):
        sorted_scores = sorted(self.scores, key=lambda x: x["score"], reverse=True)
        return sorted_scores[:limit]

# ================== GAME ENGINE ==================
class CombatGame:
    def __init__(self):
        self.score_manager = ScoreManager()
        self.reset_game()
    
    def reset_game(self):
        self.current_level = 1
        self.player_name = ""
        self.player_hp = 100
        self.player_max_hp = 100
        self.player_attack = 12
        self.player_level = 1
        self.player_exp = 0
        self.player_exp_needed = 100
        self.score = 0
        self.start_time = None
        self.game_active = False
        self.victory = False
        # Khởi tạo virus hiện tại
        self.current_virus = None
        self.current_virus_hp = 0
        self.combat_log = []
    
    def start_game(self, player_name):
        self.reset_game()
        self.player_name = player_name
        self.game_active = True
        self.start_time = time.time()
        self.load_virus()
        return True
    
    def load_virus(self):
        """Tải virus cho level hiện tại"""
        if self.current_level <= len(GameConfig.VIRUSES):
            self.current_virus = GameConfig.VIRUSES[self.current_level - 1].copy()
            self.current_virus_hp = self.current_virus["hp"]
        return self.current_virus
    
    def get_current_virus(self):
        if self.current_virus is None:
            self.load_virus()
        return self.current_virus
    
    def player_attack_action(self):
        virus = self.get_current_virus()
        
        # Tính sát thương (có crit 20%)
        is_crit = random.random() < 0.2
        damage = random.randint(self.player_attack - 3, self.player_attack + 3)
        if is_crit:
            damage = int(damage * 1.5)
        
        self.current_virus_hp -= damage
        
        result = {
            "action": "attack",
            "damage": damage,
            "is_crit": is_crit,
            "virus_hp_remaining": max(0, self.current_virus_hp),
            "virus_defeated": self.current_virus_hp <= 0
        }
        
        if result["virus_defeated"]:
            # Nhận EXP và điểm
            exp_gain = virus["exp"]
            self.player_exp += exp_gain
            self.score += 100 * self.current_level
            
            # Check level up
            level_up = False
            if self.player_exp >= self.player_exp_needed:
                self.player_level += 1
                self.player_exp -= self.player_exp_needed
                self.player_exp_needed = int(self.player_exp_needed * 1.2)
                self.player_attack += 3
                self.player_max_hp += 20
                self.player_hp = min(self.player_hp + 10, self.player_max_hp)
                level_up = True
            
            # Chuyển level hoặc kết thúc game
            if self.current_level < 5:
                self.current_level += 1
                self.load_virus()
                result["next_level"] = True
                result["level_up"] = level_up
                result["exp_gain"] = exp_gain
                result["new_level"] = self.current_level
            else:
                # Chiến thắng game
                self.game_active = False
                self.victory = True
                time_taken = int(time.time() - self.start_time)
                self.score_manager.add_score(self.player_name, 5, self.score, time_taken)
                result["victory"] = True
                result["time_taken"] = time_taken
                result["final_score"] = self.score
        else:
            # Virus tấn công lại
            virus_damage = random.randint(max(1, virus["attack"] - 3), virus["attack"])
            self.player_hp -= virus_damage
            
            result["virus_attack"] = virus_damage
            result["player_hp_remaining"] = max(0, self.player_hp)
            
            if self.player_hp <= 0:
                self.game_active = False
                result["game_over"] = True
        
        return result
    
    def heal_action(self):
        # Hồi máu (tiêu tốn 20 điểm)
        if self.score >= 20:
            heal_amount = random.randint(15, 30)
            self.player_hp = min(self.player_hp + heal_amount, self.player_max_hp)
            self.score -= 20
            
            # Virus tấn công khi hồi máu
            virus = self.get_current_virus()
            virus_damage = random.randint(max(1, virus["attack"] - 2), virus["attack"])
            self.player_hp -= virus_damage
            
            result = {
                "action": "heal",
                "heal_amount": heal_amount,
                "virus_attack": virus_damage,
                "player_hp_remaining": max(0, self.player_hp),
                "score_cost": 20,
                "current_score": self.score
            }
            
            if self.player_hp <= 0:
                self.game_active = False
                result["game_over"] = True
            
            return result
        else:
            return {"action": "heal", "insufficient": True, "need": 20, "current": self.score}
    
    def defend_action(self):
        # Phòng thủ (giảm sát thương nhận)
        virus = self.get_current_virus()
        virus_damage = random.randint(max(1, virus["attack"] - 5), max(2, virus["attack"] - 2))
        virus_damage = max(1, virus_damage)
        self.player_hp -= virus_damage
        
        result = {
            "action": "defend",
            "damage_reduced": True,
            "virus_attack": virus_damage,
            "player_hp_remaining": max(0, self.player_hp)
        }
        
        if self.player_hp <= 0:
            self.game_active = False
            result["game_over"] = True
        
        return result

# ================== GIAO DIỆN ==================

def setup_page():
    st.set_page_config(
        page_title="Python Savior - Chiến Đấu Giải Cứu",
        page_icon="⚔️",
        layout="wide"
    )
    
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0a0a0a 0%, #0d1b2a 100%); }
    .game-title {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #1b263b 0%, #415a77 100%);
        border-radius: 20px;
        border: 2px solid #ff4444;
        margin-bottom: 20px;
    }
    .virus-card {
        background: linear-gradient(135deg, #4a0000 0%, #8b0000 100%);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        border: 2px solid #ff0000;
    }
    .player-card {
        background: linear-gradient(135deg, #0d3b0d 0%, #1a5c1a 100%);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        border: 2px solid #00ff88;
    }
    .damage-text {
        color: #ff4444;
        font-size: 20px;
        font-weight: bold;
    }
    .heal-text {
        color: #00ff88;
        font-size: 20px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

def display_header():
    st.markdown("""
    <div class="game-title">
        <h1 style='color: #ff4444; margin: 0;'>⚔️ PYTHON SAVIOR - CHIẾN ĐẤU ⚔️</h1>
        <h3 style='color: #ffffff;'>Đánh bay virus máy tính, cứu thế giới!</h3>
        <p style='color: #aaa;'>⚡ Chọn hành động thông minh để chiến thắng ⚡</p>
    </div>
    """, unsafe_allow_html=True)

def display_battle_status(game):
    virus = game.get_current_virus()
    if virus:
        virus_hp_percent = game.current_virus_hp / virus["hp"] if virus["hp"] > 0 else 0
    else:
        virus_hp_percent = 0
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="player-card">
            <h3>🦸‍♂️ {game.player_name}</h3>
            <p>❤️ HP: {max(0, game.player_hp)}/{game.player_max_hp}</p>
            <p>⚔️ Sát thương: {game.player_attack}</p>
            <p>⭐ Điểm: {game.score}</p>
            <p>📊 Cấp {game.player_level} | EXP: {game.player_exp}/{game.player_exp_needed}</p>
        </div>
        """, unsafe_allow_html=True)
        st.progress(max(0, game.player_hp) / game.player_max_hp if game.player_max_hp > 0 else 1)
    
    with col2:
        if virus:
            st.markdown(f"""
            <div class="virus-card">
                <h3>{virus['icon']} {virus['name']} {virus['icon']}</h3>
                <p>💀 HP: {max(0, game.current_virus_hp)}/{virus['hp']}</p>
                <p>⚔️ Sát thương: {virus['attack']}/đòn</p>
                <p>🎯 Level: {virus['level']}/5</p>
            </div>
            """, unsafe_allow_html=True)
            st.progress(virus_hp_percent)

def display_combat_log(combat_log):
    st.markdown("### 📜 NHẬT KÝ CHIẾN ĐẤU")
    if combat_log:
        for msg in combat_log[-5:]:
            if "💥" in msg or "CHÍNH XÁC" in msg or "tấn công" in msg:
                st.markdown(f"<p style='color: #ff8888;'>{msg}</p>", unsafe_allow_html=True)
            elif "❤️" in msg or "HỒI" in msg:
                st.markdown(f"<p style='color: #88ff88;'>{msg}</p>", unsafe_allow_html=True)
            elif "🏆" in msg or "CHIẾN THẮNG" in msg:
                st.markdown(f"<p style='color: #ffd700; font-size: 18px;'>{msg}</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='color: #cccccc;'>{msg}</p>", unsafe_allow_html=True)
    else:
        st.info("⚔️ Hãy bắt đầu chiến đấu!")

def display_leaderboard(score_manager):
    st.markdown("### 🏆 BẢNG XẾP HẠNG 🏆")
    
    top_scores = score_manager.get_top_scores(10)
    if top_scores:
        for i, s in enumerate(top_scores):
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
            st.markdown(f"""
            <div style='background: #1a1a2e; border-radius: 10px; padding: 8px; margin: 5px 0; border-left: 3px solid #ff4444;'>
                {medal} <b>{s['name']}</b> - {s['score']} điểm - 📅 {s['date']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Chưa có ai cứu thế giới! Hãy là người đầu tiên!")

def display_game_over(game):
    st.markdown("""
    <div style='text-align: center; padding: 40px; background: #4a0000; border-radius: 20px;'>
        <h1 style='color: #ff4444;'>💀 GAME OVER 💀</h1>
        <p style='color: white;'>Virus máy tính đã chiếm thế giới...</p>
        <p style='color: #ffaa00;'>Hãy chiến đấu thông minh hơn để cứu nhân loại!</p>
    </div>
    """, unsafe_allow_html=True)

def display_victory(game):
    st.markdown(f"""
    <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #00aa44, #006400); border-radius: 20px;'>
        <h1 style='color: #ffd700;'>🏆 CHIẾN THẮNG! 🏆</h1>
        <h2 style='color: white;'>Bạn đã cứu thế giới khỏi virus máy tính!</h2>
        <p style='color: #fff;'>⭐ Điểm số: {game.score} ⭐</p>
        <p style='color: #fff;'>🏅 Bạn xứng đáng là Chiến binh xuất sắc nhất! 🏅</p>
    </div>
    """, unsafe_allow_html=True)

# ================== MAIN ==================
def main():
    setup_page()
    display_header()
    
    # Khởi tạo session state
    if "game" not in st.session_state:
        st.session_state.game = CombatGame()
        st.session_state.game_active = False
        st.session_state.show_leaderboard = False
    
    game = st.session_state.game
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎮 MENU")
        if st.button("🆕 BẮT ĐẦU MỚI", key="new_game"):
            st.session_state.game = CombatGame()
            st.session_state.game_active = False
            st.session_state.show_leaderboard = False
            st.rerun()
        
        st.markdown("---")
        
        st.markdown("### 📖 HƯỚNG DẪN")
        st.markdown("""
        **⚔️ Tấn công**: Gây 9-15 sát thương  
        *Có 20% chance chí mạng (x1.5)*
        
        **💊 Hồi máu**: Hồi 15-30 HP  
        *Tốn 20 điểm, vẫn bị tấn công*
        
        **🛡️ Phòng thủ**: Giảm sát thương  
        *Bị tấn công nhưng ít hơn*
        
        **🏆 Thắng 5 level để cứu thế giới!**
        """)
        
        st.markdown("---")
        display_leaderboard(game.score_manager)
    
    if st.session_state.show_leaderboard:
        st.markdown("## 🏆 BẢNG XẾP HẠNG TOÀN THỜI GIAN 🏆")
        top = game.score_manager.get_top_scores(20)
        if top:
            for i, s in enumerate(top):
                medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
                st.markdown(f"{medal} **{s['name']}** - {s['score']} điểm - 📅 {s['date']}")
        if st.button("🔙 QUAY LẠI GAME", key="back"):
            st.session_state.show_leaderboard = False
            st.rerun()
        return
    
    # Màn hình bắt đầu game
    if not st.session_state.game_active and not game.game_active:
        st.markdown("""
        <div style='text-align: center; padding: 40px;'>
            <h2>⚔️ CHÀO MỪNG CHIẾN BINH! ⚔️</h2>
            <p>Thế giới đang bị virus máy tính tấn công! Hãy chiến đấu để giải cứu!</p>
            <p>📖 <b>Cách chơi:</b></p>
            <p>• Bấm <b style='color:#ff8888'>TẤN CÔNG</b> để gây sát thương cho virus</p>
            <p>• Bấm <b style='color:#88ff88'>HỒI MÁU</b> để phục hồi HP (tốn 20 điểm)</p>
            <p>• Bấm <b style='color:#ffaa88'>PHÒNG THỦ</b> để giảm sát thương nhận vào</p>
            <p>• Đánh bại 5 con virus để cứu thế giới!</p>
            <p style='color: #ffaa00;'>🎯 Mẹo: Tấn công thường xuyên, hồi máu khi HP thấp!</p>
        </div>
        """, unsafe_allow_html=True)
        
        name = st.text_input("👤 Nhập tên chiến binh:", max_chars=20, key="player_name_input")
        if st.button("🚀 BẮT ĐẦU CHIẾN ĐẤU", key="start_btn", use_container_width=True):
            if name and name.strip():
                game.start_game(name.strip())
                st.session_state.game_active = True
                game.combat_log = [f"🦸‍♂️ {name} bước vào trận chiến!"]
                st.rerun()
            else:
                st.error("❌ Hãy nhập tên của bạn!")
        return
    
    # Đang chơi
    if game.player_hp <= 0:
        display_game_over(game)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 CHƠI LẠI", key="play_again_over"):
                st.session_state.game = CombatGame()
                st.session_state.game_active = False
                st.rerun()
        return
    
    if game.victory:
        display_victory(game)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 CHƠI LẠI", key="play_again_victory"):
                st.session_state.game = CombatGame()
                st.session_state.game_active = False
                st.rerun()
        with col2:
            if st.button("🏆 XEM BẢNG XẾP HẠNG", key="view_rank"):
                st.session_state.show_leaderboard = True
                st.rerun()
        return
    
    # Hiển thị trạng thái chiến đấu
    display_battle_status(game)
    st.markdown("---")
    display_combat_log(game.combat_log)
    st.markdown("---")
    
    # Nút hành động
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⚔️ TẤN CÔNG ⚔️", key="attack_btn", use_container_width=True):
            result = game.player_attack_action()
            
            if result["action"] == "attack":
                crit_text = "🔥 CHÍ MẠNG! 🔥 " if result.get("is_crit") else ""
                game.combat_log.append(f"💥 {crit_text}Bạn tấn công gây {result['damage']} sát thương!")
                
                if result.get("virus_defeated"):
                    game.combat_log.append(f"🎉 {game.current_virus['name']} đã bị đánh bại! 🎉")
                    if result.get("exp_gain"):
                        game.combat_log.append(f"✨ Nhận {result['exp_gain']} EXP! ✨")
                    if result.get("level_up"):
                        game.combat_log.append(f"🌟 LEVEL UP! Cấp {game.player_level}! 🌟")
                    if result.get("next_level"):
                        game.combat_log.append(f"⚔️ Bước vào level {result['new_level']}!")
                    if result.get("victory"):
                        game.combat_log.append(f"🏆 CHIẾN THẮNG! Bạn đã cứu thế giới! 🏆")
                else:
                    game.combat_log.append(f"💀 Virus tấn công lại, bạn mất {result['virus_attack']} HP!")
            
            if result.get("game_over"):
                game.combat_log.append("💀 GAME OVER! Bạn đã thất bại... 💀")
            
            st.rerun()
    
    with col2:
        if st.button("💊 HỒI MÁU (20 điểm) 💊", key="heal_btn", use_container_width=True):
            result = game.heal_action()
            
            if result.get("insufficient"):
                game.combat_log.append(f"❌ Không đủ điểm! Cần {result['need']} điểm, bạn có {result['current']} điểm!")
            else:
                game.combat_log.append(f"❤️ Hồi máu {result['heal_amount']} HP! (tốn 20 điểm, còn {result['current_score']} điểm)")
                game.combat_log.append(f"💀 Virus tấn công, bạn mất {result['virus_attack']} HP!")
                
                if result.get("game_over"):
                    game.combat_log.append("💀 GAME OVER! Bạn đã thất bại... 💀")
            
            st.rerun()
    
    with col3:
        if st.button("🛡️ PHÒNG THỦ 🛡️", key="defend_btn", use_container_width=True):
            result = game.defend_action()
            
            game.combat_log.append(f"🛡️ Bạn phòng thủ, giảm sát thương nhận vào!")
            game.combat_log.append(f"💀 Virus tấn công, bạn mất {result['virus_attack']} HP!")
            
            if result.get("game_over"):
                game.combat_log.append("💀 GAME OVER! Bạn đã thất bại... 💀")
            
            st.rerun()

if __name__ == "__main__":
    main()# combat_game.py
import streamlit as st
import time
import random
import json
import os
from datetime import datetime

# ================== CẤU HÌNH GAME ==================
class GameConfig:
    GAME_NAME = "⚔️ PYTHON SAVIOR - CHIẾN ĐẤU GIẢI CỨU ⚔️"
    DATA_FILE = "combat_scores.json"
    
    VIRUSES = [
        {"name": "🦠 VIRUS LOGIC", "level": 1, "hp": 30, "attack": 5, "exp": 50, "icon": "🦠"},
        {"name": "🧬 VIRUS LOOP", "level": 2, "hp": 50, "attack": 8, "exp": 80, "icon": "🧬"},
        {"name": "🎯 VIRUS FUNCTION", "level": 3, "hp": 70, "attack": 12, "exp": 120, "icon": "🎯"},
        {"name": "📦 VIRUS LIST", "level": 4, "hp": 100, "attack": 15, "exp": 180, "icon": "📦"},
        {"name": "🏆 BOSS DICTIONARY", "level": 5, "hp": 150, "attack": 20, "exp": 300, "icon": "🏆"},
    ]

# ================== QUẢN LÝ ĐIỂM ==================
class ScoreManager:
    def __init__(self):
        self.data_file = GameConfig.DATA_FILE
        self.scores = self.load_scores()
    
    def load_scores(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_scores(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.scores, f, indent=2, ensure_ascii=False)
    
    def add_score(self, player_name, level, score, time_taken):
        record = {
            "name": player_name,
            "level": level,
            "score": score,
            "time": time_taken,
            "date": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        self.scores.append(record)
        self.save_scores()
    
    def get_top_scores(self, limit=10):
        sorted_scores = sorted(self.scores, key=lambda x: x["score"], reverse=True)
        return sorted_scores[:limit]

# ================== GAME ENGINE ==================
class CombatGame:
    def __init__(self):
        self.score_manager = ScoreManager()
        self.reset_game()
    
    def reset_game(self):
        self.current_level = 1
        self.player_name = ""
        self.player_hp = 100
        self.player_max_hp = 100
        self.player_attack = 12
        self.player_level = 1
        self.player_exp = 0
        self.player_exp_needed = 100
        self.score = 0
        self.start_time = None
        self.game_active = False
        self.victory = False
        self.current_virus_hp = 0
    
    def start_game(self, player_name):
        self.reset_game()
        self.player_name = player_name
        self.game_active = True
        self.start_time = time.time()
        self.load_virus()
        return True
    
    def load_virus(self):
        virus = GameConfig.VIRUSES[self.current_level - 1]
        self.current_virus_hp = virus["hp"]
        self.current_virus = virus
        return virus
    
    def get_current_virus(self):
        return GameConfig.VIRUSES[self.current_level - 1]
    
    def player_attack_action(self):
        virus = self.get_current_virus()
        
        # Tính sát thương (có crit 20%)
        is_crit = random.random() < 0.2
        damage = random.randint(self.player_attack - 3, self.player_attack + 3)
        if is_crit:
            damage = int(damage * 1.5)
        
        self.current_virus_hp -= damage
        
        result = {
            "action": "attack",
            "damage": damage,
            "is_crit": is_crit,
            "virus_hp_remaining": max(0, self.current_virus_hp),
            "virus_defeated": self.current_virus_hp <= 0
        }
        
        if result["virus_defeated"]:
            # Nhận EXP và điểm
            exp_gain = virus["exp"]
            self.player_exp += exp_gain
            self.score += 100 * self.current_level
            
            # Check level up
            level_up = False
            if self.player_exp >= self.player_exp_needed:
                self.player_level += 1
                self.player_exp -= self.player_exp_needed
                self.player_exp_needed = int(self.player_exp_needed * 1.2)
                self.player_attack += 3
                self.player_max_hp += 20
                self.player_hp = min(self.player_hp + 10, self.player_max_hp)
                level_up = True
            
            # Chuyển level hoặc kết thúc game
            if self.current_level < 5:
                self.current_level += 1
                self.load_virus()
                result["next_level"] = True
                result["level_up"] = level_up
                result["exp_gain"] = exp_gain
            else:
                # Chiến thắng game
                self.game_active = False
                self.victory = True
                time_taken = int(time.time() - self.start_time)
                self.score_manager.add_score(self.player_name, 5, self.score, time_taken)
                result["victory"] = True
                result["time_taken"] = time_taken
        else:
            # Virus tấn công lại
            virus_damage = random.randint(virus["attack"] - 3, virus["attack"])
            self.player_hp -= virus_damage
            
            result["virus_attack"] = virus_damage
            result["player_hp_remaining"] = max(0, self.player_hp)
            
            if self.player_hp <= 0:
                self.game_active = False
                result["game_over"] = True
        
        return result
    
    def heal_action(self):
        # Hồi máu (tiêu tốn 20 điểm)
        if self.score >= 20:
            heal_amount = random.randint(15, 30)
            self.player_hp = min(self.player_hp + heal_amount, self.player_max_hp)
            self.score -= 20
            
            # Virus tấn công khi hồi máu
            virus = self.get_current_virus()
            virus_damage = random.randint(virus["attack"] - 2, virus["attack"])
            self.player_hp -= virus_damage
            
            result = {
                "action": "heal",
                "heal_amount": heal_amount,
                "virus_attack": virus_damage,
                "player_hp_remaining": max(0, self.player_hp),
                "score_cost": 20
            }
            
            if self.player_hp <= 0:
                self.game_active = False
                result["game_over"] = True
            
            return result
        else:
            return {"action": "heal", "insufficient": True, "need": 20, "current": self.score}
    
    def defend_action(self):
        # Phòng thủ (giảm sát thương nhận)
        virus = self.get_current_virus()
        virus_damage = random.randint(virus["attack"] - 5, virus["attack"] - 2)
        virus_damage = max(1, virus_damage)
        self.player_hp -= virus_damage
        
        result = {
            "action": "defend",
            "damage_reduced": True,
            "virus_attack": virus_damage,
            "player_hp_remaining": max(0, self.player_hp)
        }
        
        if self.player_hp <= 0:
            self.game_active = False
            result["game_over"] = True
        
        return result

# ================== GIAO DIỆN ==================

def setup_page():
    st.set_page_config(
        page_title="Python Savior - Chiến Đấu Giải Cứu",
        page_icon="⚔️",
        layout="wide"
    )
    
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0a0a0a 0%, #0d1b2a 100%); }
    .game-title {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #1b263b 0%, #415a77 100%);
        border-radius: 20px;
        border: 2px solid #ff4444;
        margin-bottom: 20px;
    }
    .virus-card {
        background: linear-gradient(135deg, #4a0000 0%, #8b0000 100%);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        border: 2px solid #ff0000;
        animation: pulse 1s infinite;
    }
    .player-card {
        background: linear-gradient(135deg, #0d3b0d 0%, #1a5c1a 100%);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        border: 2px solid #00ff88;
    }
    .action-button {
        background: linear-gradient(135deg, #ff6600, #ff3300);
        border: none;
        color: white;
        padding: 15px;
        border-radius: 10px;
        font-size: 18px;
        font-weight: bold;
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    .damage-text {
        animation: shake 0.3s;
        color: #ff4444;
        font-size: 24px;
        font-weight: bold;
    }
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    .heal-text {
        color: #00ff88;
        font-size: 24px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

def display_header():
    st.markdown("""
    <div class="game-title">
        <h1 style='color: #ff4444; margin: 0;'>⚔️ PYTHON SAVIOR - CHIẾN ĐẤU ⚔️</h1>
        <h3 style='color: #ffffff;'>Đánh bay virus máy tính, cứu thế giới!</h3>
        <p style='color: #aaa;'>⚡ Chọn hành động thông minh để chiến thắng ⚡</p>
    </div>
    """, unsafe_allow_html=True)

def display_battle_status(game):
    virus = game.get_current_virus()
    virus_hp_percent = game.current_virus_hp / virus["hp"] if game.current_virus_hp > 0 else 0
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="player-card">
            <h3>🦸‍♂️ {game.player_name}</h3>
            <p>❤️ HP: {game.player_hp}/{game.player_max_hp}</p>
            <p>⚔️ Sát thương: {game.player_attack}</p>
            <p>⭐ Điểm: {game.score}</p>
            <p>📊 Level: {game.player_level} | EXP: {game.player_exp}/{game.player_exp_needed}</p>
        </div>
        """, unsafe_allow_html=True)
        st.progress(game.player_hp / game.player_max_hp)
    
    with col2:
        st.markdown(f"""
        <div class="virus-card">
            <h3>{virus['icon']} {virus['name']} {virus['icon']}</h3>
            <p>💀 HP: {max(0, game.current_virus_hp)}/{virus['hp']}</p>
            <p>⚔️ Sát thương: {virus['attack']}/đòn</p>
            <p>🎯 Level: {virus['level']}/5</p>
        </div>
        """, unsafe_allow_html=True)
        st.progress(virus_hp_percent)

def display_combat_log(log_messages):
    st.markdown("### 📜 NHẬT KÝ CHIẾN ĐẤU")
    for msg in log_messages[-5:]:
        if "💥" in msg or "CHÍNH XÁC" in msg:
            st.markdown(f"<p style='color: #ff4444;'>{msg}</p>", unsafe_allow_html=True)
        elif "❤️" in msg or "HỒI" in msg:
            st.markdown(f"<p style='color: #00ff88;'>{msg}</p>", unsafe_allow_html=True)
        elif "🏆" in msg:
            st.markdown(f"<p style='color: #ffd700;'>{msg}</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='color: #cccccc;'>{msg}</p>", unsafe_allow_html=True)

def display_action_buttons():
    col1, col2, col3 = st.columns(3)
    
    with col1:
        attack_btn = st.button("⚔️ TẤN CÔNG ⚔️", use_container_width=True)
    with col2:
        heal_btn = st.button("💊 HỒI MÁU (20 điểm) 💊", use_container_width=True)
    with col3:
        defend_btn = st.button("🛡️ PHÒNG THỦ 🛡️", use_container_width=True)
    
    return attack_btn, heal_btn, defend_btn

def display_leaderboard(score_manager):
    st.markdown("### 🏆 BẢNG XẾP HẠNG 🏆")
    
    top_scores = score_manager.get_top_scores(10)
    if top_scores:
        for i, s in enumerate(top_scores):
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
            st.markdown(f"""
            <div style='background: #1a1a2e; border-radius: 10px; padding: 8px; margin: 5px 0; border-left: 3px solid #ff4444;'>
                {medal} <b>{s['name']}</b> - Level {s['level']} | {s['score']} điểm | 📅 {s['date']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Chưa có ai cứu thế giới! Hãy là người đầu tiên!")

def display_game_over(game):
    st.markdown("""
    <div style='text-align: center; padding: 40px; background: #4a0000; border-radius: 20px;'>
        <h1 style='color: #ff4444;'>💀 GAME OVER 💀</h1>
        <p style='color: white;'>Virus máy tính đã chiếm thế giới...</p>
        <p style='color: #ffaa00;'>Hãy chiến đấu thông minh hơn để cứu nhân loại!</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 CHƠI LẠI", use_container_width=True):
        st.session_state.game = CombatGame()
        st.session_state.game_active = False
        st.session_state.combat_log = []
        st.rerun()

def display_victory(game):
    st.markdown("""
    <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #00ff88, #006400); border-radius: 20px;'>
        <h1 style='color: #ffd700;'>🏆 CHIẾN THẮNG! 🏆</h1>
        <h2 style='color: white;'>Bạn đã cứu thế giới khỏi virus máy tính!</h2>
        <p style='color: #fff;'>🏅 Bạn xứng đáng là Chiến binh xuất sắc nhất! 🏅</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 CHƠI LẠI", use_container_width=True):
            st.session_state.game = CombatGame()
            st.session_state.game_active = False
            st.session_state.combat_log = []
            st.rerun()
    with col2:
        if st.button("🏆 XEM BẢNG XẾP HẠNG", use_container_width=True):
            st.session_state.show_leaderboard = True

# ================== MAIN ==================
def main():
    setup_page()
    display_header()
    
    # Khởi tạo game
    if "game" not in st.session_state:
        st.session_state.game = CombatGame()
        st.session_state.game_active = False
        st.session_state.show_leaderboard = False
        st.session_state.combat_log = []
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎮 MENU")
        if st.button("🆕 BẮT ĐẦU MỚI"):
            st.session_state.game = CombatGame()
            st.session_state.game_active = False
            st.session_state.show_leaderboard = False
            st.session_state.combat_log = []
            st.rerun()
        
        st.markdown("---")
        
        st.markdown("### 📖 HƯỚNG DẪN")
        st.markdown("""
        - ⚔️ **Tấn công**: Gây sát thương lên virus
        - 💊 **Hồi máu**: Hồi 15-30 HP (tốn 20 điểm)
        - 🛡️ **Phòng thủ**: Giảm sát thương nhận vào
        - 🏆 Thắng 5 level để cứu thế giới!
        """)
        
        st.markdown("---")
        display_leaderboard(st.session_state.game.score_manager)
    
    if st.session_state.show_leaderboard:
        st.markdown("## 🏆 BẢNG XẾP HẠNG TOÀN THỜI GIAN 🏆")
        top = st.session_state.game.score_manager.get_top_scores(20)
        if top:
            for i, s in enumerate(top):
                medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
                st.markdown(f"{medal} **{s['name']}** - {s['score']} điểm - 📅 {s['date']}")
        if st.button("🔙 QUAY LẠI GAME"):
            st.session_state.show_leaderboard = False
            st.rerun()
        return
    
    # Chưa bắt đầu game
    if not st.session_state.game_active and not st.session_state.game.game_active:
        st.markdown("""
        <div style='text-align: center; padding: 40px;'>
            <h2>⚔️ CHÀO MỪNG CHIẾN BINH! ⚔️</h2>
            <p>Thế giới đang bị virus máy tính tấn công! Hãy chiến đấu để giải cứu!</p>
            <p>📖 <b>Cách chơi:</b></p>
            <p>• Bấm <b>TẤN CÔNG</b> để gây sát thương cho virus</p>
            <p>• Bấm <b>HỒI MÁU</b> để phục hồi HP (tốn 20 điểm)</p>
            <p>• Bấm <b>PHÒNG THỦ</b> để giảm sát thương nhận vào</p>
            <p>• Đánh bại 5 con virus để cứu thế giới!</p>
            <p style='color: #ffaa00;'>🎯 Mẹo: Tấn công thường xuyên, hồi máu khi HP thấp!</p>
        </div>
        """, unsafe_allow_html=True)
        
        name = st.text_input("👤 Nhập tên chiến binh:", max_chars=20)
        if st.button("🚀 BẮT ĐẦU CHIẾN ĐẤU", use_container_width=True):
            if name:
                st.session_state.game.start_game(name)
                st.session_state.game_active = True
                st.session_state.combat_log = [f"🦸‍♂️ {name} bước vào trận chiến!"]
                st.rerun()
            else:
                st.error("❌ Hãy nhập tên của bạn!")
        return
    
    game = st.session_state.game
    
    # Hiển thị trạng thái chiến đấu
    display_battle_status(game)
    
    st.markdown("---")
    
    # Kiểm tra game over
    if game.player_hp <= 0:
        display_game_over(game)
        return
    
    # Kiểm tra victory
    if game.victory:
        display_victory(game)
        return
    
    # Hiển thị nhật ký chiến đấu
    display_combat_log(st.session_state.combat_log)
    
    st.markdown("---")
    
    # Hiển thị nút hành động
    attack_btn, heal_btn, defend_btn = display_action_buttons()
    
    if attack_btn:
        result = game.player_attack_action()
        
        if result["action"] == "attack":
            crit_text = "🔥 CHÍ MẠNG! 🔥 " if result.get("is_crit") else ""
            st.session_state.combat_log.append(
                f"💥 {crit_text}Bạn tấn công gây {result['damage']} sát thương!"
            )
            
            if result.get("virus_defeated"):
                st.session_state.combat_log.append(f"🎉 {game.current_virus['name']} đã bị đánh bại! 🎉")
                if result.get("exp_gain"):
                    st.session_state.combat_log.append(f"✨ Nhận {result['exp_gain']} EXP! ✨")
                if result.get("level_up"):
                    st.session_state.combat_log.append(f"🌟 LEVEL UP! Cấp {game.player_level}! 🌟")
                if result.get("next_level"):
                    st.session_state.combat_log.append(f"⚔️ Bước vào level {game.current_level}!")
                if result.get("victory"):
                    st.session_state.combat_log.append(f"🏆 CHIẾN THẮNG! Bạn đã cứu thế giới! 🏆")
            else:
                st.session_state.combat_log.append(
                    f"💀 Virus tấn công lại, bạn mất {result['virus_attack']} HP!"
                )
        
        if result.get("game_over"):
            st.session_state.combat_log.append("💀 GAME OVER! Bạn đã thất bại... 💀")
        
        st.rerun()
    
    elif heal_btn:
        result = game.heal_action()
        
        if result.get("insufficient"):
            st.session_state.combat_log.append(f"❌ Không đủ điểm! Cần {result['need']} điểm, bạn có {result['current']} điểm!")
        else:
            st.session_state.combat_log.append(f"❤️ Hồi máu {result['heal_amount']} HP! (tốn 20 điểm)")
            st.session_state.combat_log.append(f"💀 Virus tấn công, bạn mất {result['virus_attack']} HP!")
            
            if result.get("game_over"):
                st.session_state.combat_log.append("💀 GAME OVER! Bạn đã thất bại... 💀")
        
        st.rerun()
    
    elif defend_btn:
        result = game.defend_action()
        
        st.session_state.combat_log.append(f"🛡️ Bạn phòng thủ, giảm sát thương nhận vào!")
        st.session_state.combat_log.append(f"💀 Virus tấn công, bạn mất {result['virus_attack']} HP!")
        
        if result.get("game_over"):
            st.session_state.combat_log.append("💀 GAME OVER! Bạn đã thất bại... 💀")
        
        st.rerun()

if __name__ == "__main__":
    main()
