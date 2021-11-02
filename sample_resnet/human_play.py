# ====================
# 人とAIの対戦
# ====================

# パッケージのインポート
from game import State
#変更に注意
from next_action_cnn import next_action

from tensorflow.keras.models import load_model
import numpy as np
from pathlib import Path
from threading import Thread
import tkinter as tk
import random

model = load_model('model/resnet_model.h5')

# ゲームUIの定義
class GameUI(tk.Frame):
    # 初期化
    def __init__(self, master=None, model=None, human_first=None):
        tk.Frame.__init__(self, master)
        self.master.title('リバーシ')

        # ゲーム状態の生成
        self.state = State()
        self.model = model

        #先行後攻を決める
        #指定がない場合はランダムに、ある場合は従う
        if human_first is None:
            self.human_first = random.randint(0, 1)
        elif human_first:
            self.human_first = 1
        else:
            self.human_first = 0


        # キャンバスの生成
        self.c = tk.Canvas(self, width = 320, height = 360, highlightthickness = 0)
        self.c.bind('<Button-1>', self.turn_of_human)
        self.c.pack()

        # 描画の更新
        self.on_draw()

    # 人間のターン
    def turn_of_human(self, event):
        # ゲーム終了時
        if self.state.is_done():
            self.state = State()
            self.on_draw()
            return

        #先行の時
        if self.human_first:
            #先手ではないとき（　AIの思考中）はクリックしても無反応に
            if not self.state.is_first_player():
                return 
        #後攻の時
        else:
            #後攻で初めてクリックした時はAIにターンを渡す
            if self.state.pieces.count(1) == 2 & self.state.enemy_pieces.count(1) == 2:
                self.master.after(1, self.turn_of_ai)
            #後手ではないとき()はクリックしでも無反応
            if self.state.is_first_player():
                return


        #盤面外のクリック時
        if event.y > 320:
            return

         # クリック位置を行動に変換
        x = int(event.x/40)
        y = int(event.y/40)
        if x < 0 or 7 < x or y < 0 or 7 < y: # 範囲外
            return
        action = x + y * 8

        # 合法手でない時
        legal_actions = self.state.legal_actions()
        if legal_actions == [64]:
            action = 64 # パス
        if action != 64 and not (action in legal_actions):
            return

        # 次の状態の取得
        self.state = self.state.next(action)
        self.on_draw()

        # AIのターン
        self.master.after(1, self.turn_of_ai)

    # AIのターン
    def turn_of_ai(self):
        # ゲーム終了時
        if self.state.is_done():
            return

        # 行動の取得
        
        action = next_action(self.model, self.state)
        #ランダム
        # else:
        #     legal_actions = self.state.legal_actions()
        #     action = legal_actions[random.randint(0, len(legal_actions)-1)]

        # 次の状態の取得
        self.state = self.state.next(action)
        self.on_draw()

    # 石の描画
    def draw_piece(self, index, first_player):
        x = (index%8)*40+5
        y = int(index/8)*40+5
        if first_player:
            self.c.create_oval(x, y, x+30, y+30, width = 1.0, outline = '#000000', fill = '#000000')
        else:
            self.c.create_oval(x, y, x+30, y+30, width = 1.0, outline = '#000000', fill = '#FFFFFF')

    # 描画の更新
    def on_draw(self):
        self.c.delete('all')
        self.c.create_rectangle(0, 0, 320, 320, width = 0.0, fill = '#105511')
        for i in range(1, 10):
            self.c.create_line(0, i*40, 320, i*40, width = 1.0, fill = '#000000')
            self.c.create_line(i*40, 0, i*40, 320, width = 1.0, fill = '#000000')
        for i in range(64):
            if self.state.pieces[i] == 1:
                self.draw_piece(i, self.state.is_first_player())
            if self.state.enemy_pieces[i] == 1:
                self.draw_piece(i, not self.state.is_first_player())

        #下部の表示
        self.c.create_line(160, 320, 160, 360, width = 1.0, fill = '#000000')
        self.c.create_oval(5, 325, 5+30, 325+30, width = 1.0, outline = '#000000', fill = '#000000')
        self.c.create_oval(165, 325, 165+30, 325+30, width = 1.0, outline = '#000000', fill = '#FFFFFF')
        #石の数
        my_pieces_num = self.state.pieces.count(1)
        enemy_pieces_num = self.state.enemy_pieces.count(1)
        if self.state.is_first_player():
            self.c.create_text(120, 340, text=str(my_pieces_num), font=('', 30))
            self.c.create_text(280, 340, text=str(enemy_pieces_num), font=('', 30))
        else:
            self.c.create_text(120, 340, text=str(enemy_pieces_num), font=('', 30))
            self.c.create_text(280, 340, text=str(my_pieces_num), font=('', 30))
        #you,aiの表示
        if self.human_first:
            self.c.create_text(40, 340, text='(YOU)', font=('', 20), anchor=tk.W)
            self.c.create_text(200, 340, text='(AI)', font=('', 20), anchor=tk.W)
        else:
            self.c.create_text(40, 340, text='(AI)', font=('', 20), anchor=tk.W)
            self.c.create_text(200, 340, text='(YOU)', font=('', 20), anchor=tk.W)

        

# ゲームUIの実行
f = GameUI(model=model)
f.pack()
f.mainloop()