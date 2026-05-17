# python_savior_game.py
import streamlit as st
import time
import random
import json
import os
from datetime import datetime

# ================== CẤU HÌNH GAME ==================
class GameConfig:
    GAME_NAME = "🐍 PYTHON SAVIOR - CỨU THẾ GIỚI BẰNG CODE 🐍"
    VIRUSES = [
        {"name": "🦠 VIRUS LOGIC", "level": 1, "hp": 30, "attack": 5},
        {"name": "🧬 VIRUS LOOP", "level": 2, "hp": 50, "attack": 8},
        {"name": "🎯 VIRUS FUNCTION", "level": 3, "hp": 70, "attack": 12},
        {"name": "📦 VIRUS LIST", "level": 4, "hp": 100, "attack": 15},
        {"name": "🏆 BOSS DICTIONARY", "level": 5, "hp": 150, "attack": 20},
    ]
    DATA_FILE = "game_scores.json"

# ================== CÂU HỎI THEO LEVEL ==================
QUESTIONS = {
    1: [  # Level 1: Biến và in ra
        {"question": "In ra dòng chữ 'Xin chào Python'", 
         "code_start": "print(", "answer": "'Xin chào Python'", "hint": "Dùng dấu nháy đơn hoặc nháy kép"},
        {"question": "Tạo biến ten = 'Bom' và in ra 'Tên tôi là Bom'", 
         "code_start": "ten = 'Bom'\nprint(", "answer": "'Tên tôi là ' + ten", "hint": "Dùng phép cộng chuỗi"},
        {"question": "Tính tổng 15 và 27, in ra kết quả", 
         "code_start": "print(", "answer": "15 + 27", "hint": "Chỉ cần viết phép tính trong print"},
    ],
    2: [  # Level 2: If else
        {"question": "Viết code kiểm tra: nếu x > 10 in 'Lớn hơn 10'", 
         "code_start": "x = 15\nif x > 10:\n    print(", "answer": "'Lớn hơn 10'", "hint": "Dùng print trong if"},
        {"question": "Kiểm tra số chẵn lẻ: in 'Chẵn' nếu so % 2 == 0", 
         "code_start": "so = 8\nif so % 2 == 0:\n    print(", "answer": "'Chẵn'", "hint": "số % 2 == 0 là chẵn"},
        {"question": "Nhập tuổi, in 'Được xem phim' nếu tuổi >= 18", 
         "code_start": "tuoi = 16\nif tuoi >= 18:\n    print(", "answer": "'Được xem phim'", "hint": "Dùng >= so sánh"},
    ],
    3: [  # Level 3: Vòng lặp for
        {"question": "In các số từ 1 đến 5, mỗi số trên 1 dòng", 
         "code_start": "for i in range(1, 6):\n    print(", "answer": "i", "hint": "Biến i chạy từ 1 đến 5"},
        {"question": "In 'Python' 3 lần bằng vòng lặp", 
         "code_start": "for i in range(3):\n    print(", "answer": "'Python'", "hint": "Dùng range(3)"},
        {"question": "Tính tổng các số từ 1 đến 10, in ra kết quả", 
         "code_start": "tong = 0\nfor i in range(1, 11):\n    tong = tong + i\nprint(", "answer": "tong", "hint": "In biến tong sau vòng lặp"},
    ],
    4: [  # Level 4: List
        {"question": "Tạo list mon_hoc = ['Toán', 'Văn', 'Anh'] và in ra phần tử thứ 2", 
         "code_start": "mon_hoc = ['Toán', 'Văn', 'Anh']\nprint(", "answer": "mon_hoc[1]", "hint": "List bắt đầu từ 0, vị trí 1 là Văn"},
        {"question": "Thêm 'Tin học' vào list và in ra list", 
         "code_start": "mon_hoc = ['Toán', 'Văn']\nmon_hoc.append(", "answer": "'Tin học'", "hint": "append() thêm vào cuối"},
        {"question": "In ra số lượng phần tử của list", 
         "code_start": "ds = [1, 2, 3, 4, 5]\nprint(", "answer": "len(ds)", "hint": "Hàm len() trả về độ dài"},
    ],
    5: [  # Level 5 - BOSS: Dictionary
        {"question": "Tạo dict sv = {'ten': 'Bom', 'tuoi': 11} và in ra tên", 
         "code_start": "sv = {'ten': 'Bom', 'tuoi': 11}\nprint(", "answer": "sv['ten']", "hint": "Dùng key để truy xuất"},
        {"question": "Thêm cặp 'lop': '5A' vào dict và in ra", 
         "code_start": "sv = {'ten': 'Bom'}\nsv['lop'] = ", "answer": "'5A'", "hint": "dict[key] = value"},
        {"question": "In ra tất cả các keys của dict", 
         "code_start": "sv = {'ten': 'Bom', 'tuoi': 11}\nprint(", "answer": "sv.keys()", "hint": "Dùng phương thức keys()"},
    ]
}

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
    
    def get_player_best(self, player_name):
        player_scores = [s for s in self.scores if s["name"] == player_name]
        if player_scores:
            return max(player_scores, key=lambda x: x["score"])
        return None

# ================== GAME ENGINE ==================
class PythonSaviorGame:
    def __init__(self):
        self.score_manager = ScoreManager()
        self.reset_game()
    
    def reset_game(self):
        self.current_level = 1
        self.current_question_idx = 0
        self.player_hp = 100
        self.player_name = ""
        self.score = 0
        self.start_time = None
        self.game_active = False
        self.victory = False
        self.attack_mode = False
        self.attack_damage = 0
    
    def start_game(self, player_name):
        self.reset_game()
        self.player_name = player_name
        self.game_active = True
        self.start_time = time.time()
        return True
    
    def get_current_virus(self):
        return GameConfig.VIRUSES[self.current_level - 1]
    
    def get_current_question(self):
        level_questions = QUESTIONS.get(self.current_level, [])
        if self.current_question_idx < len(level_questions):
            return level_questions[self.current_question_idx]
        return None
    
    def check_answer(self, user_code):
        current_q = self.get_current_question()
        if not current_q:
            return False
        
        expected = current_q["answer"]
        user_code_clean = user_code.strip().strip('"').strip("'")
        expected_clean = expected.strip().strip('"').strip("'")
        
        # So sánh đáp án
        if user_code_clean == expected_clean:
            return True
        
        # Thử chạy code an toàn
        try:
            full_code = current_q["code_start"] + user_code + ")"
            # Kiểm tra an toàn (không cho import, exec, eval độc hại)
            if "import" in full_code or "exec" in full_code or "__" in full_code:
                return False
            exec_locals = {}
            exec(full_code, {"__builtins__": __builtins__}, exec_locals)
            return True
        except:
            return False
    
    def submit_answer(self, user_code):
        if not self.game_active:
            return {"success": False, "message": "Game chưa bắt đầu!"}
        
        current_q = self.get_current_question()
        if not current_q:
            return {"success": False, "message": "Hết câu hỏi!"}
        
        if self.check_answer(user_code):
            # Tính sát thương
            base_damage = 10
            time_bonus = max(0, 30 - (time.time() - self.last_question_time)) // 3
            damage = base_damage + int(time_bonus)
            self.attack_damage = damage
            self.attack_mode = True
            
            # Chuyển sang câu tiếp theo hoặc level tiếp theo
            level_questions = QUESTIONS.get(self.current_level, [])
            if self.current_question_idx + 1 < len(level_questions):
                self.current_question_idx += 1
                self.last_question_time = time.time()
                return {
                    "success": True, 
                    "message": f"🎉 CHÍNH XÁC! Sát thương: {damage}",
                    "next_question": True,
                    "damage": damage
                }
            else:
                # Hoàn thành level
                virus = self.get_current_virus()
                self.score += 100 * self.current_level
                
                if self.current_level < 5:
                    self.current_level += 1
                    self.current_question_idx = 0
                    self.last_question_time = time.time()
                    return {
                        "success": True,
                        "message": f"✨ HOÀN THÀNH LEVEL {self.current_level - 1}! ✨\nSát thương: {damage}\nLên level {self.current_level}!",
                        "level_up": True,
                        "damage": damage
                    }
                else:
                    # Chiến thắng game
                    self.game_active = False
                    self.victory = True
                    time_taken = int(time.time() - self.start_time)
                    self.score_manager.add_score(self.player_name, 5, self.score, time_taken)
                    return {
                        "success": True,
                        "message": f"🏆 TUYỆT VỜI! Bạn đã cứu thế giới! 🏆\nĐiểm: {self.score}\nThời gian: {time_taken // 60} phút {time_taken % 60} giây",
                        "victory": True,
                        "damage": damage
                    }
        else:
            # Sai, bị virus tấn công
            virus = self.get_current_virus()
            damage = random.randint(5, virus["attack"])
            self.player_hp -= damage
            self.attack_mode = False
            
            if self.player_hp <= 0:
                self.game_active = False
                return {
                    "success": False,
                    "message": f"💀 GAME OVER! Bạn đã bị {virus['name']} đánh bại! 💀\nHãy chơi lại để cứu thế giới!",
                    "game_over": True,
                    "damage_taken": damage
                }
            
            return {
                "success": False,
                "message": f"❌ SAI RỒI! {virus['name']} tấn công bạn -{damage} HP! ❌\nGợi ý: {current_q['hint']}",
                "damage_taken": damage
            }
    
    def set_last_question_time(self):
        self.last_question_time = time.time()

# ================== GIAO DIỆN STREAMLIT ==================

def setup_page():
    st.set_page_config(
        page_title="Python Savior - Học Code Cứu Thế Giới",
        page_icon="🐍",
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
        border: 2px solid #00ff88;
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
    .code-area {
        background: #1e1e1e;
        border-radius: 10px;
        padding: 15px;
        font-family: monospace;
        border: 1px solid #00ff88;
    }
    .damage-animation {
        animation: shake 0.5s;
    }
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    </style>
    """, unsafe_allow_html=True)

def display_header():
    st.markdown("""
    <div class="game-title">
        <h1 style='color: #00ff88; margin: 0;'>🐍 PYTHON SAVIOR 🐍</h1>
        <h3 style='color: #ffffff;'>Cứu thế giới khỏi virus máy tính bằng code!</h3>
        <p style='color: #aaa;'>🔐 Nhập đúng code → Đánh bay virus → Cứu nhân loại 🔐</p>
    </div>
    """, unsafe_allow_html=True)

def display_battle_status(game):
    virus = game.get_current_virus()
    
    col1, col2 = st.columns(2)
    
    with col1:
        hp_percent = game.player_hp
        st.markdown(f"""
        <div class="player-card">
            <h3>🦸‍♂️ {game.player_name}</h3>
            <p>❤️ HP: {game.player_hp}/100</p>
            <p>⭐ Điểm: {game.score}</p>
            <p>🎯 Level: {game.current_level}/5</p>
        </div>
        """, unsafe_allow_html=True)
        st.progress(game.player_hp / 100)
    
    with col2:
        virus_hp = virus["hp"]
        st.markdown(f"""
        <div class="virus-card">
            <h3>{virus['name']}</h3>
            <p>💀 HP: {virus_hp}</p>
            <p>⚔️ Sát thương: {virus['attack']}/đòn</p>
            <p>📊 Level: {virus['level']}/5</p>
        </div>
        """, unsafe_allow_html=True)
        # Thanh HP virus (giả định virus chưa chết)
        st.progress(1.0)

def display_question(game):
    current_q = game.get_current_question()
    if not current_q:
        return None
    
    st.markdown(f"""
    <div class="code-area">
        <p><b>📝 THỬ THÁCH LEVEL {game.current_level}:</b></p>
        <p>{current_q['question']}</p>
        <p><i>💡 Gợi ý: {current_q['hint']}</i></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Hiển thị code template
    st.code(current_q["code_start"], language="python")
    
    # Input cho người chơi
    user_code = st.text_area(
        "✏️ Viết code của bạn vào đây (không cần viết lại phần đã có):",
        key=f"code_{game.current_level}_{game.current_question_idx}",
        height=80,
        placeholder="Ví dụ: 'Xin chào Python'"
    )
    
    # Hiển thị preview code hoàn chỉnh
    if user_code:
        full_code = current_q["code_start"] + user_code + ")"
        st.caption(f"📄 Code hoàn chỉnh:\n```python\n{full_code}\n```")
    
    return user_code

def display_leaderboard(score_manager):
    st.markdown("### 🏆 BẢNG XẾP HẠNG LẬP TRÌNH VIÊN 🏆")
    
    top_scores = score_manager.get_top_scores(10)
    if top_scores:
        for i, s in enumerate(top_scores):
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
            st.markdown(f"""
            <div style='background: #1a1a2e; border-radius: 10px; padding: 8px; margin: 5px 0; border-left: 3px solid #00ff88;'>
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
        <p style='color: #ffaa00;'>Hãy học code nhiều hơn để cứu nhân loại!</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 CHƠI LẠI", use_container_width=True):
        st.session_state.game = PythonSaviorGame()
        st.session_state.game_active = False
        st.rerun()

def display_victory(game):
    st.markdown("""
    <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #00ff88, #006400); border-radius: 20px; animation: shake 0.5s;'>
        <h1 style='color: #ffd700;'>🏆 CHIẾN THẮNG! 🏆</h1>
        <h2 style='color: white;'>Bạn đã cứu thế giới khỏi virus máy tính!</h2>
        <p style='color: #fff;'>🏅 Bạn xứng đáng là Lập trình viên xuất sắc nhất! 🏅</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 CHƠI LẠI", use_container_width=True):
            st.session_state.game = PythonSaviorGame()
            st.session_state.game_active = False
            st.rerun()
    with col2:
        if st.button("🏆 XEM BẢNG XẾP HẠNG", use_container_width=True):
            st.session_state.show_leaderboard = True

def display_attack_animation(damage, is_player_attack=True):
    if is_player_attack:
        st.markdown(f"""
        <div style='text-align: center; animation: shake 0.3s;'>
            <h2 style='color: #00ff88;'>💥 CHÍNH XÁC! -{damage} HP 💥</h2>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='text-align: center; animation: shake 0.3s;'>
            <h2 style='color: #ff4444;'>💀 SAI RỒI! Mất {damage} HP 💀</h2>
        </div>
        """, unsafe_allow_html=True)

# ================== MAIN ==================
def main():
    setup_page()
    display_header()
    
    # Khởi tạo game
    if "game" not in st.session_state:
        st.session_state.game = PythonSaviorGame()
        st.session_state.game_active = False
        st.session_state.show_leaderboard = False
        st.session_state.attack_animation = None
    
    # Hiển thị bảng xếp hạng ở sidebar
    with st.sidebar:
        st.markdown("## 🎮 MENU")
        if st.button("🆕 BẮT ĐẦU MỚI"):
            st.session_state.game = PythonSaviorGame()
            st.session_state.game_active = False
            st.session_state.show_leaderboard = False
            st.rerun()
        
        st.markdown("---")
        display_leaderboard(st.session_state.game.score_manager)
    
    if st.session_state.show_leaderboard:
        st.markdown("## 🏆 BẢNG XẾP HẠNG TOÀN THỜI GIAN 🏆")
        top = st.session_state.game.score_manager.get_top_scores(20)
        if top:
            for i, s in enumerate(top):
                medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
                st.markdown(f"{medal} **{s['name']}** - {s['score']} điểm (Level {s['level']}) - {s['date']}")
        if st.button("🔙 QUAY LẠI GAME"):
            st.session_state.show_leaderboard = False
            st.rerun()
        return
    
    # Chưa bắt đầu game
    if not st.session_state.game_active and not st.session_state.game.game_active:
        st.markdown("""
        <div style='text-align: center; padding: 40px;'>
            <h2>🐍 CHÀO MỪNG ĐẾN VỚI PYTHON SAVIOR! 🐍</h2>
            <p>Thế giới đang bị virus máy tính tấn công! Chỉ có code Python mới có thể đánh bay chúng!</p>
            <p>📖 <b>Luật chơi:</b></p>
            <p>• Mỗi level có 3 câu hỏi Python</p>
            <p>• Trả lời đúng → Gây sát thương cho virus</p>
            <p>• Trả lời sai → Bị virus tấn công mất HP</p>
            <p>• Hoàn thành 5 level để cứu thế giới!</p>
        </div>
        """, unsafe_allow_html=True)
        
        name = st.text_input("👤 Nhập tên lập trình viên:", max_chars=20)
        if st.button("🚀 BẮT ĐẦU CỨU THẾ GIỚI", use_container_width=True):
            if name:
                st.session_state.game.start_game(name)
                st.session_state.game.set_last_question_time()
                st.session_state.game_active = True
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
    
    # Hiển thị câu hỏi
    user_code = display_question(game)
    
    # Nút nộp bài
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("⚔️ CHIẾN ĐẤU - NỘP CODE ⚔️", use_container_width=True):
            if user_code:
                result = game.submit_answer(user_code)
                
                if result.get("attack_mode") or result.get("damage"):
                    display_attack_animation(
                        result.get("damage", result.get("damage_taken", 0)), 
                        is_player_attack=result.get("success", False)
                    )
                    time.sleep(0.5)
                
                if result.get("victory"):
                    st.balloons()
                    st.rerun()
                elif result.get("game_over"):
                    st.error(result["message"])
                    st.rerun()
                else:
                    if result["success"]:
                        st.success(result["message"])
                    else:
                        st.error(result["message"])
                    time.sleep(1)
                    st.rerun()
            else:
                st.warning("✏️ Hãy viết code trước khi chiến đấu!")
    
    # Hiển thị tips
    with st.expander("💡 MẸO NHỎ CHO NGƯỜI MỚI"):
        st.markdown("""
        - **Print:** `print('nội dung')` để in ra màn hình
        - **Biến:** `ten = 'Bom'` để lưu giá trị
        - **If:** `if so > 10:` để kiểm tra điều kiện
        - **For:** `for i in range(5):` để lặp 5 lần
        - **List:** `ds = [1, 2, 3]` tạo danh sách
        - **Dictionary:** `sv = {'ten': 'Bom', 'tuoi': 11}`
        """)

if __name__ == "__main__":
    main()