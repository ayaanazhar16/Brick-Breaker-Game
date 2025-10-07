# 🧱 Brick Breaker Game (Python + Tkinter)

## 🎮 Overview
This project is a **Brick Breaker** game built entirely in **Python using Tkinter** for the GUI and **Pillow (PIL)** for image handling.  

Players control a paddle to bounce a ball and break bricks. The game includes features like:
- Multiple brick durability levels  
- Score tracking and leaderboard  
- Save and load functionality  
- Cheat codes  
- Boss key (hides the game as a spreadsheet)  
- Dynamic difficulty increases  

---

## 🖼️ Features
✅ Smooth real-time gameplay with keyboard controls  
✅ Leaderboard persistence (`leaderboard.txt`)  
✅ Game save/load system (`game.json`)  
✅ Cheat codes for testing:
  - **Ctrl + B** → Big Ball  
  - **Ctrl + D** → Remove 10 Bricks  
✅ **Boss Key** (press **Z**) → Instantly hides game with a fake spreadsheet  
✅ Pause/Unpause (press **P**)  
✅ Level progression: ball speed increases as you score  

---

## 🕹️ Controls

| Action | Key |
|--------|-----|
| Move Paddle Left | ← (Left Arrow) |
| Move Paddle Right | → (Right Arrow) |
| Start Game | Space |
| Pause / Resume | P |
| Boss Key | Z |
| Big Ball Cheat | Ctrl + B |
| Delete 10 Bricks Cheat | Ctrl + D |

---

## 💾 Save / Load System
- Click **Save Game** to store your progress in `game.json`
- Click **Load Game** to resume your previous session  
- Game data includes:
  - Username  
  - Score  
  - Lives  
  - Ball position, velocity, and size  
  - Paddle and brick states  

---

## 🧑‍💻 Installation

### 1️⃣ Clone or download the repository
```bash
git clone https://github.com/ayaanazhar16/Brick-Breaker-Game.git
cd "Tkinter Game"
