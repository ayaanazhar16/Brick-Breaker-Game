import tkinter as tk
from PIL import Image, ImageTk
import os
import json


class CanvasObject:
    def __init__(self, canvas, object_id):
        self.canvas = canvas
        self.object_id = object_id

    def get_coordinates(self):
        return self.canvas.coords(self.object_id)

    def move_object(self, delta_x, delta_y):
        self.canvas.move(self.object_id, delta_x, delta_y)

    def remove_object(self):
        self.canvas.delete(self.object_id)


class Ball(CanvasObject):
    def __init__(self, canvas, initial_x, initial_y):
        self.radius = 10
        self.velocity = [1, -1]
        self.speed = 5  # Adjust this to change ball speed
        ball_id = canvas.create_oval(
            initial_x - self.radius, initial_y - self.radius,
            initial_x + self.radius, initial_y + self.radius,
            fill='#FF5733'  # Ball color: orange-red
        )
        super().__init__(canvas, ball_id)

    def update_size(self, new_radius):
        self.radius = new_radius
        ball_coords = self.get_coordinates()
        center_x = (ball_coords[0] + ball_coords[2]) / 2
        center_y = (ball_coords[1] + ball_coords[3]) / 2

        self.canvas.coords(self.object_id,
                           center_x - self.radius,
                           center_y - self.radius,
                           center_x + self.radius,
                           center_y + self.radius)

    def update_position(self):
        ball_coords = self.get_coordinates()
        canvas_width = self.canvas.winfo_width()

        # Reverse direction if ball hits canvas sides
        if ball_coords[0] <= 0 or ball_coords[2] >= canvas_width:
            self.velocity[0] *= -1
        if ball_coords[1] <= 0:
            self.velocity[1] *= -1

        # Move ball
        delta_x = self.velocity[0] * self.speed
        delta_y = self.velocity[1] * self.speed
        self.move_object(delta_x, delta_y)

    def handle_collision(self, colliding_objects):
        ball_coords = self.get_coordinates()
        ball_center_x = (ball_coords[0] + ball_coords[2]) / 2

        if len(colliding_objects) > 1:
            self.velocity[1] *= -1
        elif len(colliding_objects) == 1:
            colliding_object = colliding_objects[0]
            obj_coords = colliding_object.get_coordinates()

            if ball_center_x > obj_coords[2]:
                self.velocity[0] = 1
            elif ball_center_x < obj_coords[0]:
                self.velocity[0] = -1
            else:
                self.velocity[1] *= -1

        for obj in colliding_objects:
            if isinstance(obj, Brick):
                obj.reduce_hits()


class Paddle(CanvasObject):
    def __init__(self, canvas, initial_x, initial_y):
        self.width = 80
        self.height = 10
        self.attached_ball = None
        paddle_id = canvas.create_rectangle(
            initial_x - self.width / 2, initial_y - self.height / 2,
            initial_x + self.width / 2, initial_y + self.height / 2,
            fill='#4287f5'  # Paddle color: blue
        )
        super().__init__(canvas, paddle_id)

    def attach_ball(self, ball):
        self.attached_ball = ball

    def move_paddle(self, delta_x):
        paddle_coords = self.get_coordinates()
        canvas_width = self.canvas.winfo_width()

        if (
            0 <= paddle_coords[0] + delta_x
            and paddle_coords[2] + delta_x <= canvas_width
        ):
            super().move_object(delta_x, 0)
            if self.attached_ball:
                self.attached_ball.move_object(delta_x, 0)


class Brick(CanvasObject):
    HIT_COLORS = {1: '#89d9de', 2: '#FFD700', 3: '#32CD32'}

    def __init__(self, canvas, center_x, center_y, hit_points):
        self.width = 75
        self.height = 20
        self.hit_points = hit_points
        brick_color = Brick.HIT_COLORS[hit_points]
        brick_id = canvas.create_rectangle(
            center_x - self.width / 2, center_y - self.height / 2,
            center_x + self.width / 2, center_y + self.height / 2,
            fill=brick_color, tags='brick'
        )
        super().__init__(canvas, brick_id)

    def reduce_hits(self):
        self.hit_points -= 1
        if self.hit_points == 0:
            self.remove_object()
        else:
            self.canvas.itemconfig(self.object_id,
                                   fill=Brick.HIT_COLORS[self.hit_points])

        game = self.canvas.master
        game.score += 10
        game.update_hud()


class StartPage(tk.Frame):
    def __init__(self, parent, on_start):
        super().__init__(parent)
        self.parent = parent
        self.on_start = on_start  # Callback to start the game

        self.pack()

        # Title Label
        tk.Label(self, text="Welcome to Brick Breaker!",
                 font=("Forte", 24)).pack(pady=20)

        # Username Input
        self.username_label = tk.Label(self, text="Enter your username:",
                                       font=("Arial", 14))
        self.username_label.pack(pady=10)

        self.username_entry = tk.Entry(self, font=("Arial", 14))
        self.username_entry.pack(pady=5)

        # Start Button
        self.start_button = tk.Button(self, text="Start Game",
                                      font=("Arial", 14),
                                      command=self.start_game)
        self.start_button.pack(pady=20)

        # Error Label
        self.error_label = tk.Label(self, text="", fg="red",
                                    font=("Arial", 12))
        self.error_label.pack()

        # Leaderboard Button
        leaderboard_button = tk.Button(self, text="View Leaderboard",
                                       font=("Arial", 14),
                                       command=self.display_leaderboard)
        leaderboard_button.pack(pady=10)

    def start_game(self):
        username = self.username_entry.get().strip()
        if username:
            self.on_start(username)
        else:
            self.error_label.config(text="Username cannot be empty!")

    def display_leaderboard(self):
        leaderboard = self.load_leaderboard()
        popup = tk.Toplevel(self)
        popup.title("Leaderboard")
        popup.geometry("400x300")
        tk.Label(popup, text="Leaderboard", font=("Arial", 20)).pack(pady=10)
        for i, (user, score) in enumerate(leaderboard[:10], start=1):
            tk.Label(popup, text=f"{i}. {user}: {score}",
                     font=("Arial", 14)).pack()
        tk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)

    def load_leaderboard(self):
        leaderboard_file = (
            "C:/GitRepos/comp16321-labs_w03052aa/Tkinter Game/leaderboard.txt")
        if os.path.exists(leaderboard_file):
            with open(leaderboard_file, "r") as file:
                return [line.strip().split(":") for line in file]
        return []


class BrickBreakerGame(tk.Frame):
    def __init__(self, root_window, username):
        super().__init__(root_window)
        self.username = username
        self.restart_button = None
        self.remaining_lives = 3
        self.score = 0
        self.level = 1
        self.paused = False
        self.canvas_width = 900
        self.canvas_height = 500

        self.canvas = tk.Canvas(self,
                                bg='#2E2E2E',  # Background color: dark gray
                                width=self.canvas_width,
                                height=self.canvas_height)
        self.canvas.pack()
        self.pack()

        save_button = tk.Button(self, text="Save Game", font=("Arial", 14),
                                command=self.save_game)
        save_button.place(relx=0.1, rely=0.95, anchor="center")

        load_button = tk.Button(self, text="Load Game", font=("Arial", 14),
                                command=self.load_game)
        load_button.place(relx=0.25, rely=0.95, anchor="center")

        self.hud_display = None
        self.canvas.bind('<p>', self.pause_key)
        self.canvas.bind('<z>', self.boss_key)
        self.canvas.bind('<Control-b>', self.ball_cheat_code)
        self.canvas.bind('<Control-d>', self.brick_cheat_code)

        self.game_objects = {}
        self.game_ball = None
        self.player_paddle = Paddle(self.canvas, self.canvas_width / 2, 326)
        self.game_objects[self.player_paddle.object_id] = self.player_paddle

        # Add bricks with varying hit capacities
        for x in range(5, self.canvas_width - 5, 75):
            self.add_brick(x + 37.5, 50, 3)
            self.add_brick(x + 37.5, 70, 2)
            self.add_brick(x + 37.5, 90, 1)

        self.hud_display = None
        self.initialize_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>',
                         lambda _: self.player_paddle.move_paddle(-10))
        self.canvas.bind('<Right>',
                         lambda _: self.player_paddle.move_paddle(10))

    def initialize_game(self):
        self.create_ball()
        self.update_hud()
        self.start_message = self.display_text(
            300, 200, f'Press Space to Start, {self.username}!')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def create_ball(self):
        if self.game_ball:
            self.game_ball.remove_object()

        paddle_coords = self.player_paddle.get_coordinates()
        ball_start_x = (paddle_coords[0] + paddle_coords[2]) / 2
        self.game_ball = Ball(self.canvas, ball_start_x, 310)
        self.player_paddle.attach_ball(self.game_ball)

    def add_brick(self, center_x, center_y, hit_points):
        brick = Brick(self.canvas, center_x, center_y, hit_points)
        self.game_objects[brick.object_id] = brick

    def display_text(self, x, y, text, font_size=40):
        font = ('Forte', font_size)
        return self.canvas.create_text(x, y, text=text, font=font)

    def update_hud(self):
        text = (
            f'{self.username} | '
            f'Lives: {self.remaining_lives} | '
            f'Score: {self.score}'
        )
        if not self.hud_display:
            self.hud_display = self.display_text(200, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud_display, text=text)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.start_message)
        self.player_paddle.attached_ball = None
        self.run_game_loop()

    def pause_key(self, event=None):
        if self.paused:
            self.unpause_game()
        else:
            self.pause_game()

    def pause_game(self):
        self.paused = True
        self.canvas.create_text(self.canvas_width / 2, self.canvas_height / 2,
                                text="PAUSED", font=("Arial", 30),
                                fill="white", tags="paused_text")

    def unpause_game(self):
        self.paused = False
        self.canvas.delete("paused_text")
        self.run_game_loop()

    def run_game_loop(self):
        if self.paused:
            return

        self.check_collisions()
        self.check_score()
        bricks_remaining = len(self.canvas.find_withtag('brick'))

        if bricks_remaining == 0:
            self.game_ball.speed = None
            self.display_text(500, 200,
                              f'You Win, {self.username}! Breaker of Bricks!')
            self.save_leaderboard(self.username, self.score)  # Save score
            self.display_leaderboard()  # Show leaderboard
            self.display_restart_button()
        elif self.game_ball.get_coordinates()[3] >= self.canvas_height:
            self.game_ball.speed = None
            self.remaining_lives -= 1
            if self.remaining_lives == 0:
                self.display_text(500, 200,
                                  f'Game Over, {self.username}! You Lose.')
                self.save_leaderboard(self.username, self.score)  # Save score
                self.display_leaderboard()  # Show leaderboard
                self.display_restart_button()
            else:
                self.after(1000, self.initialize_game)
        else:
            self.game_ball.update_position()
            self.after(50, self.run_game_loop)

    def check_score(self):
        next_level = (self.level) * 70

        if self.score >= next_level:
            self.level += 1
            self.game_ball.speed += 2
            self.print_message(f"Speed increased! Level: {self.level}")

    def print_message(self, message, duration=2000):
        message_id = self.display_text(self.canvas_width // 2,
                                       self.canvas_height // 2,
                                       message, font_size=20)
        self.after(duration, lambda: self.canvas.delete(message_id))

    def display_restart_button(self):
        if not self.restart_button:
            self.restart_button = tk.Button(
                self, text="Restart Game",
                font=("Arial", 14),
                command=self.restart_game)
            self.restart_button.place(relx=0.5, rely=0.8, anchor="center")

    def restart_game(self):
        if self.restart_button:
            self.restart_button.destroy()
            self.restart_button = None

        for obj in list(self.game_objects.values()):
            obj.remove_object()
        self.game_objects.clear()

        self.remaining_lives = 3
        self.score = 0
        self.level = 1
        self.paused = False

        self.canvas.delete("all")

        self.player_paddle = Paddle(self.canvas, self.canvas_width / 2, 326)
        self.game_objects[self.player_paddle.object_id] = self.player_paddle

        for x in range(5, self.canvas_width - 5, 75):
            self.add_brick(x + 37.5, 50, 3)
            self.add_brick(x + 37.5, 70, 2)
            self.add_brick(x + 37.5, 90, 1)

        self.hud_display = None
        self.create_ball()
        self.update_hud()

        self.start_message = self.display_text(
            300, 200, f'Press Space to Start, {self.username}!')
        self.canvas.bind('<space>', lambda _: self.start_game())
        self.canvas.focus_set()

        if os.path.exists(self.SAVED_FILE):
            os.remove(self.SAVED_FILE)

    def boss_key(self, event=None):
        boss_pic = tk.Toplevel(self)
        boss_pic.title("Spreadsheet Data")
        boss_pic.geometry("1500x900")

        spreadsheet_img = Image.open(
            "C:/GitRepos/comp16321-labs_w03052aa/Tkinter Game/spreadsheet.png")
        spreadsheet_img = spreadsheet_img.resize((1500, 900),
                                                 Image.Resampling.LANCZOS)
        spreadsheet_ph = ImageTk.PhotoImage(spreadsheet_img)

        image_label = tk.Label(boss_pic, image=spreadsheet_ph)
        image_label.pack(fill=tk.BOTH, expand=True)
        image_label.image = spreadsheet_ph

        boss_pic.grab_set()
        boss_pic.transient(self)

    def ball_cheat_code(self, event=None):
        if self.game_ball:
            self.game_ball.update_size(20)
            self.display_ball_message("Cheat Code: Big Ball")

    def display_ball_message(self, message, duration=2000):
        message_id = self.display_text(self.canvas_width // 2,
                                       self.canvas_height // 2, message,
                                       font_size=20)
        self.after(duration, lambda: self.canvas.delete(message_id))

    def brick_cheat_code(self, event=None):
        brick_ids = [obj_id for obj_id, obj in self.game_objects.items()
                     if isinstance(obj, Brick)]
        bricks_to_remove = brick_ids[:10]
        for brick_id in bricks_to_remove:
            brick = self.game_objects.pop(brick_id)
            brick.remove_object()
        self.display_brick_message("Cheat Code: Delete Bricks")

    def display_brick_message(self, message, duration=2000):
        message_id = self.display_text(self.canvas_width // 2,
                                       self.canvas_height // 2,
                                       message, font_size=20)
        self.after(duration, lambda: self.canvas.delete(message_id))

    def check_collisions(self):
        ball_coords = self.game_ball.get_coordinates()
        overlapping_items = self.canvas.find_overlapping(*ball_coords)
        colliding_objects = [self.game_objects[obj_id]
                             for obj_id in overlapping_items
                             if obj_id in self.game_objects]
        self.game_ball.handle_collision(colliding_objects)

    LEADERBOARD_FILE = (
        "C:/GitRepos/comp16321-labs_w03052aa/Tkinter Game/leaderboard.txt")

    def load_leaderboard(self):
        if os.path.exists(self.LEADERBOARD_FILE):
            with open(self.LEADERBOARD_FILE, "r") as file:
                return [line.strip().split(":") for line in file]
        return []

    def save_leaderboard(self, username, score):
        leaderboard = self.load_leaderboard()
        leaderboard.append((username, str(score)))
        leaderboard = sorted(leaderboard,
                             key=lambda x: int(x[1]), reverse=True)

        with open(self.LEADERBOARD_FILE, "w") as file:
            for user, score in leaderboard:
                file.write(f"{user}:{score}\n")

    def display_leaderboard(self):
        leaderboard = self.load_leaderboard()
        popup = tk.Toplevel(self)
        popup.title("Leaderboard")
        popup.geometry("400x300")
        tk.Label(popup, text="Leaderboard", font=("Arial", 20)).pack(pady=10)
        for i, (user, score) in enumerate(leaderboard[:10], start=1):
            tk.Label(popup, text=f"{i}. {user}: {score}",
                     font=("Arial", 14)).pack()
        tk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)

    SAVED_FILE = "C:/GitRepos/comp16321-labs_w03052aa/Tkinter Game/game.json"

    def save_game(self):
        game_state = {
            "username": self.username,
            "score": self.score,
            "lives": self.remaining_lives,
            "level": self.level,
            "ball": {
                "position": self.game_ball.get_coordinates(),
                "velocity": self.game_ball.velocity,
                "radius": self.game_ball.radius,
            },
            "paddle": {
                "position": self.player_paddle.get_coordinates(),
            },
            "bricks": [
                {
                    "position": brick.get_coordinates(),
                    "hit_points": brick.hit_points,
                }
                for obj_id, brick in self.game_objects.items()
                if isinstance(brick, Brick) and brick.hit_points > 0
            ]
        }
        with open(self.SAVED_FILE, "w") as file:
            json.dump(game_state, file)
        self.print_message(f"Game Saved for {self.username}")

    def load_game(self):
        if not os.path.exists(self.SAVED_FILE):
            self.print_message("No saved game data available")
            return

        with open(self.SAVED_FILE, "r") as file:
            game_state = json.load(file)

        saved_username = game_state.get("username", None)
        if not saved_username or saved_username != self.username:
            self.print_message("Save file doesn't match the current user!")
            return

        for obj in list(self.game_objects.values()):
            obj.remove_object()
        self.game_objects.clear()
        self.canvas.delete("all")

        self.score = game_state["score"]
        self.remaining_lives = game_state["lives"]
        self.level = game_state["level"]

        paddle_coords = game_state["paddle"]["position"]
        self.player_paddle = Paddle(self.canvas,
                                    (paddle_coords[0] + paddle_coords[2]) / 2,
                                    paddle_coords[1])
        self.game_objects[self.player_paddle.object_id] = self.player_paddle

        ball_state = game_state["ball"]
        self.game_ball = Ball(
            self.canvas,
            (ball_state["position"][0] + ball_state["position"][2]) / 2,
            ball_state["position"][1])
        self.game_ball.velocity = ball_state["velocity"]
        self.game_ball.update_size(ball_state["radius"])

        for brick_state in game_state["bricks"]:
            brick_coords = brick_state["position"]
            hit_points = brick_state.get("hit_points", 1)

            if hit_points <= 0:
                continue

            center_x = (brick_coords[0] + brick_coords[2]) / 2
            center_y = (brick_coords[1] + brick_coords[3]) / 2
            self.add_brick(center_x, center_y, hit_points)

        self.update_hud()
        self.print_message("Game Loaded!")
        self.canvas.focus_set()


if __name__ == '__main__':
    def start_game(username):
        start_page.destroy()
        game = BrickBreakerGame(root, username)
        game.pack()

    root = tk.Tk()
    root.title('Brick Breaker Game')

    start_page = StartPage(root, start_game)
    start_page.pack()

    root.mainloop()
