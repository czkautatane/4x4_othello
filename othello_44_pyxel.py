import pyxel
import copy

class OthelloPyxel:
    def __init__(self):
        pyxel.init(120, 140, title="Othello 4x4 (You are Second)")  # Window size and title
        self.board = [[0] * 4 for _ in range(4)]
        self.board[1][1] = self.board[2][2] = -1
        self.board[1][2] = self.board[2][1] = 1
        self.turn = 1  # 1: black (AI), -1: white (Player)
        self.cell_size = 30  # Size of each cell in pixels
        self.offset_x = 0 #for board
        self.offset_y = 20 #for board
        self.message = ""
        self.ai_delay_frames = 0  # 追加: AIの遅延用カウンタ
        self.ai_move()  # 変更: 最初にAI手番ではなく、必要ならパス処理も反映
        pyxel.run(self.update, self.draw)


    def is_valid_move(self, board, row, col, player):
        if board[row][col] != 0:
            return False

        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue

                r, c = row + dr, col + dc
                flipped = 0
                while 0 <= r < 4 and 0 <= c < 4 and board[r][c] == -player:
                    r += dr
                    c += dc
                    flipped += 1

                if 0 <= r < 4 and 0 <= c < 4 and board[r][c] == player and flipped > 0:
                    return True
        return False


    def get_valid_moves(self, board, player):
        valid_moves = []
        for row in range(4):
            for col in range(4):
                if self.is_valid_move(board, row, col, player):
                    valid_moves.append((row, col))
        return valid_moves

    def flip_stones(self, board, row, col, player):
        new_board = copy.deepcopy(board)
        new_board[row][col] = player

        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue

                r, c = row + dr, col + dc
                to_flip = []
                while 0 <= r < 4 and 0 <= c < 4 and new_board[r][c] == -player:
                    to_flip.append((r, c))
                    r += dr
                    c += dc

                if 0 <= r < 4 and 0 <= c < 4 and new_board[r][c] == player:
                    for fr, fc in to_flip:
                        new_board[fr][fc] = player
        return new_board

    def player_move(self, row, col):
        if self.turn == -1:
            if self.is_valid_move(self.board, row, col, -1):
                self.board = self.flip_stones(self.board, row, col, -1)
                self.turn = 1  # Switch to AI's turn
                self.message = ""  # Clear any previous messages
                if not self.get_valid_moves(self.board, 1) and not self.get_valid_moves(self.board,-1):
                  self.game_over()
                  return
                if not self.get_valid_moves(self.board, 1):
                    self.turn = -1
                    self.message = "AI Pass"
                    return

                # 変更: pyxel.call_delayedの代わりにフレーム待ちを設定
                self.ai_delay_frames = 10  
            else:
                self.message = "Invalid move"


    def ai_move(self):
        if self.turn == 1:
            valid_moves = self.get_valid_moves(self.board, 1)
            if not valid_moves:
                if not self.get_valid_moves(self.board, -1):
                    self.game_over()
                else:
                    self.turn = -1
                    self.message = "AI Pass"
                return

            _, best_move = self.minimax(self.board, 1, float('-inf'), float('inf'))
            if best_move:
                self.board = self.flip_stones(self.board, best_move[0], best_move[1], 1)
                self.turn = -1
                self.message = ""

            if not self.get_valid_moves(self.board, -1) and not self.get_valid_moves(self.board, 1):
                self.game_over()
                return

    def minimax(self, board, player, alpha, beta):
      valid_moves = self.get_valid_moves(board, player)

      if not valid_moves:  # No valid moves, check if opponent has moves
          opponent_valid_moves = self.get_valid_moves(board, -player)
          if not opponent_valid_moves: #No valid moves for either, end of the game.
            return self.evaluate(board), None #Game over, return the score
          else:
            score, _ = self.minimax(board, -player, alpha, beta)
            return score, None

      best_move = None

      if player == 1:  # Maximizing player (AI)
          max_score = float('-inf')
          for move in valid_moves:
              new_board = self.flip_stones(board, move[0], move[1], player)
              score, _ = self.minimax(new_board, -player, alpha, beta)
              if score > max_score:
                  max_score = score
                  best_move = move
              alpha = max(alpha, max_score)
              if beta <= alpha:  #Prune.
                  break
          return max_score, best_move

      else:  # Minimizing player (Human, but AI evaluates)
          min_score = float('inf')
          for move in valid_moves:
              new_board = self.flip_stones(board, move[0], move[1], player)
              score, _ = self.minimax(new_board, -player, alpha, beta)

              if score < min_score:
                  min_score = score
                  best_move = move
              beta = min(beta, min_score)
              if beta <= alpha:
                  break

          return min_score, best_move


    def evaluate(self, board):
        # Count the stones for each player
        ai_stones = 0
        player_stones = 0
        for row in range(4):
            for col in range(4):
                if board[row][col] == 1:
                    ai_stones += 1
                elif board[row][col] == -1:
                    player_stones += 1
        return ai_stones - player_stones



    def game_over(self):
        ai_score = sum(row.count(1) for row in self.board)
        player_score = sum(row.count(-1) for row in self.board)
        if ai_score > player_score:
          self.message = f"AI wins! AI:{ai_score} You:{player_score}"
        elif player_score > ai_score:
            self.message = f"You win! You:{player_score} AI:{ai_score}" #Should not happen
        else:
            self.message = f"Tie! AI:{ai_score} You:{player_score}"


    def update(self):
        # 追加: プレイヤーのパス処理（手がなければ自動パス or ゲーム終了）
        if self.turn == -1 and not self.get_valid_moves(self.board, -1):
            if not self.get_valid_moves(self.board, 1):
                self.game_over()
            else:
                self.turn = 1
                self.message = "Player Pass"
                self.ai_delay_frames = 10

        # 追加: AIの遅延処理
        if self.ai_delay_frames > 0:
            self.ai_delay_frames -= 1
            if self.ai_delay_frames == 0 and self.turn == 1:
                self.ai_move()

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if self.turn == -1: # Get player's move only if it is the player's turn
                col = (pyxel.mouse_x - self.offset_x) // self.cell_size
                row = (pyxel.mouse_y - self.offset_y) // self.cell_size
                if 0 <= row < 4 and 0 <= col < 4:
                    self.player_move(row, col)


    def draw(self):
        pyxel.cls(11)  # 変更: 背景色を見やすい色に変更

        # Draw the message (if any)
        pyxel.text(5, 5, self.message, 0)  # Display message at top-left

        # Draw the board
        for row in range(4):
            for col in range(4):
                x = self.offset_x + col * self.cell_size
                y = self.offset_y + row * self.cell_size
                # pyxel.rect(x, y, self.cell_size, self.cell_size, 3)  # Draw cell borders # REMOVED

                if self.board[row][col] == 1:
                    pyxel.circ(x + self.cell_size // 2, y + self.cell_size // 2, self.cell_size // 2 - 2, 0)  # Black stone
                elif self.board[row][col] == -1:
                    pyxel.circ(x + self.cell_size // 2, y + self.cell_size // 2, self.cell_size // 2 - 2, 7)  # White stone

        # Draw grid lines *after* drawing stones, so lines are on top
        for i in range(5):
            # Horizontal lines
            pyxel.line(self.offset_x, self.offset_y + i * self.cell_size,
                       self.offset_x + 4 * self.cell_size, self.offset_y + i * self.cell_size, 0)
            # Vertical lines
            pyxel.line(self.offset_x + i * self.cell_size, self.offset_y,
                       self.offset_x + i * self.cell_size, self.offset_y + 4 * self.cell_size, 0)

        # 追加: プレイヤーのターン時にマウス位置にカーソルを表示
        if self.turn == -1:
            hovered_col = (pyxel.mouse_x - self.offset_x) // self.cell_size
            hovered_row = (pyxel.mouse_y - self.offset_y) // self.cell_size
            if 0 <= hovered_row < 4 and 0 <= hovered_col < 4:
                x = self.offset_x + hovered_col * self.cell_size
                y = self.offset_y + hovered_row * self.cell_size
                pyxel.rectb(x, y, self.cell_size, self.cell_size, 8)

if __name__ == "__main__":
    OthelloPyxel()