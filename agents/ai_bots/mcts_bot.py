
# ================= 五子棋棋盘类 =================
import numpy as np
import math
import random
import time

# Zobrist哈希表初始化（全局）
ZOBRIST_SIZE = 15
ZOBRIST_DEPTH = 10
ZOBRIST_TABLE = np.random.randint(1, 2**63, size=(ZOBRIST_SIZE, ZOBRIST_SIZE, 3, ZOBRIST_DEPTH), dtype=np.uint64)

class Board:
    def __init__(self, size=15):
        self.size = size
        self.board = np.zeros((size, size), dtype=int)
        self.last_move = None

    def is_valid(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size and self.board[x, y] == 0

    def place(self, x, y, player):
        if self.is_valid(x, y):
            self.board[x, y] = player
            self.last_move = (x, y, player)
            return True
        return False

    def get_valid_moves(self):
        return [(x, y) for x in range(self.size) for y in range(self.size) if self.board[x, y] == 0]

    def clone(self):
        new_board = Board(self.size)
        new_board.board = self.board.copy()
        new_board.last_move = self.last_move
        return new_board

    def is_terminal(self):
        return self.get_winner() is not None or len(self.get_valid_moves()) == 0

    def get_winner(self):
        for player in [1, 2]:
            for dx, dy in [(1,0),(0,1),(1,1),(1,-1)]:
                for x in range(self.size):
                    for y in range(self.size):
                        count = 0
                        for k in range(5):
                            nx, ny = x + k*dx, y + k*dy
                            if 0 <= nx < self.size and 0 <= ny < self.size and self.board[nx, ny] == player:
                                count += 1
                            else:
                                break
                        if count == 5:
                            return player
        return None

# ================= WU-UCT MCTS节点类 =================
class MCTSNode:
    def __init__(self, board, player, parent=None, action=None):
        self.board = board
        self.player = player
        self.parent = parent
        self.action = action
        self.children = []
        self.visits = 0
        self.wins = 0
        self.untried_actions = board.get_valid_moves()

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0

    def is_terminal(self):
        return self.board.is_terminal()

    def wu_uct_value(self, C=1.4, total_parent_visits=None, untried_count=None):
        if self.visits == 0:
            if untried_count and total_parent_visits:
                return float('inf') * (untried_count / (total_parent_visits + 1))
            return float('inf')
        return (self.wins / self.visits) + C * math.sqrt(math.log(total_parent_visits + 1) / self.visits)

# ================= WU-UCT MCTS算法类 =================
class MCTS:
    def __init__(self, board, player, C=1.4, simulation_count=100):
        self.board = board
        self.player = player
        self.C = C
        self.simulation_count = simulation_count

    def uct_value(self, node, total_parent_visits, untried_count):
        return node.wu_uct_value(self.C, total_parent_visits, untried_count)

    def select_move(self, root):
        total_visits = sum(child.visits for child in root.children) + 1
        untried_count = len([c for c in root.children if c.visits == 0])
        return max(root.children, key=lambda n: self.uct_value(n, total_visits, untried_count))

    def simulate(self, node):
        board = node.board.clone()
        player = node.player
        while not board.is_terminal():
            valid_moves = board.get_valid_moves()
            if not valid_moves:
                break
            move = random.choice(valid_moves)
            board.place(move[0], move[1], player)
            player = 2 if player == 1 else 1
        winner = board.get_winner()
        return winner

    def backpropagate(self, node, winner):
        while node is not None:
            node.visits += 1
            if winner == self.player:
                node.wins += 1
            node = node.parent

    def get_action(self):
        root = MCTSNode(self.board.clone(), self.player)
        for _ in range(self.simulation_count):
            node = root
            # Selection
            while not node.is_terminal() and node.is_fully_expanded() and node.children:
                node = self.select_move(node)
            # Expansion
            if not node.is_terminal() and node.untried_actions:
                move = random.choice(node.untried_actions)
                node.untried_actions.remove(move)
                next_board = node.board.clone()
                next_board.place(move[0], move[1], node.player)
                next_player = 2 if node.player == 1 else 1
                child = MCTSNode(next_board, next_player, parent=node, action=move)
                node.children.append(child)
                node = child
            # Simulation
            winner = self.simulate(node)
            # Backpropagation
            self.backpropagate(node, winner)
        # 选择访问次数最多的子节点
        best_child = max(root.children, key=lambda c: c.visits) if root.children else None
        return best_child.action if best_child else self.board.get_valid_moves()[0]

# ================= 主程序：人机/AI对战 =================
if __name__ == "__main__":
    board = Board(size=15)
    mcts_black = MCTS(board, player=1, simulation_count=50)
    mcts_white = MCTS(board, player=2, simulation_count=50)
    current_player = 1
    print("五子棋游戏开始！黑方=1，白方=2")
    while not board.is_terminal():
        print("当前棋盘:")
        print(board.board)
        if current_player == 1:
            move = mcts_black.get_action()
        else:
            move = mcts_white.get_action()
        board.place(move[0], move[1], current_player)
        print(f"玩家{current_player}落子: {move}")
        current_player = 2 if current_player == 1 else 1
    winner = board.get_winner()
    print("游戏结束！胜利者:", winner if winner else "平局")

# ================= 五子棋棋盘类 =================
import numpy as np
import math
import random
import time

class GomokuBoard:
    def __init__(self, size=15):
        self.size = size
        self.board = np.zeros((size, size), dtype=int)
        self.last_move = None

    def is_valid(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size and self.board[x, y] == 0

    def place(self, x, y, player):
        if self.is_valid(x, y):
            self.board[x, y] = player
            self.last_move = (x, y, player)
            return True
        return False

    def get_valid_moves(self, player=None, eval_func=None, top_n=5):
        moves = [(x, y) for x in range(self.size) for y in range(self.size) if self.board[x, y] == 0]
        if eval_func is not None and player is not None:
            scored_moves = []
            for move in moves:
                board_copy = self.clone()
                board_copy.place(move[0], move[1], player)
                score = eval_func(board_copy)
                scored_moves.append((score, move))
            scored_moves.sort(reverse=True)
            moves = [m for s, m in scored_moves[:top_n]]
        return moves

    def clone(self):
        new_board = GomokuBoard(self.size)
        new_board.board = self.board.copy()
        new_board.last_move = self.last_move
        return new_board

    def is_terminal(self):
        return self.get_winner() is not None or len(self.get_valid_moves()) == 0

    def get_winner(self):
        for player in [1, 2]:
            for dx, dy in [(1,0),(0,1),(1,1),(1,-1)]:
                for x in range(self.size):
                    for y in range(self.size):
                        count = 0
                        for k in range(5):
                            nx, ny = x + k*dx, y + k*dy
                            if 0 <= nx < self.size and 0 <= ny < self.size and self.board[nx, ny] == player:
                                count += 1
                            else:
                                break
                        if count == 5:
                            return player
        return None

# ================= MCTS节点类 =================
class MCTSNode:
    def __init__(self, board: GomokuBoard, player: int, parent=None, action=None):
        self.board = board
        self.player = player
        self.parent = parent
        self.action = action
        self.children = []
        self.visits = 0
        self.wins = 0
        self.untried_actions = board.get_valid_moves()

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0

    def is_terminal(self):
        return self.board.is_terminal()

    def wu_uct_score(self, C=1.4, total_parent_visits=None, untried_count=None):
        # WU-UCT: 未观察节点优先扩展，已观察节点用UCB
        if self.visits == 0:
            # WU-UCT优先扩展未访问节点
            if untried_count and total_parent_visits:
                return float('inf') * (untried_count / (total_parent_visits + 1))
            return float('inf')
        # 已访问节点用UCB
        return (self.wins / self.visits) + C * math.sqrt(math.log(total_parent_visits + 1) / self.visits)


# ================= Minimax-MCTS混合五子棋AI类 =================
class MCTSBot:
    def __init__(self, name="MCTSBot", player_id=1, simulation_count=100, max_depth=4, C=1.4):
        self.name = name
        self.player_id = player_id
        self.simulation_count = simulation_count
        self.max_depth = max_depth
        self.C = C
        self._eval_cache = {}

    def get_action(self, *args, **kwargs):
        import time
        """
        兼容两种调用方式：
        1. get_action(board: GomokuBoard)
        2. get_action(observation, env)（用于原有环境集成）
        """
        if len(args) == 1 and isinstance(args[0], GomokuBoard):
            board = args[0]
        elif len(args) == 2:
            observation, env = args
            board_state = env.game.get_state()['board']
            board = GomokuBoard(size=board_state.shape[0])
            board.board = board_state.copy()
        else:
            raise ValueError("get_action参数错误，需传入GomokuBoard或(observation, env)")
        # 检查对手是否有活三或半活四，且自己没有半活三或四连
        def find_threat_point():
            my_id = self.player_id
            opp_id = 2 if my_id == 1 else 1
            threat_points = []
            my_threat = False
            for x in range(board.size):
                for y in range(board.size):
                    if board.board[x, y] != 0:
                        continue
                    for dx, dy in [(1,0),(0,1),(1,1),(1,-1)]:
                        # 检查对手活三
                        cnt = 1
                        open_left = open_right = False
                        for k in range(1, 5):
                            nx, ny = x + dx * k, y + dy * k
                            if not (0 <= nx < board.size and 0 <= ny < board.size):
                                break
                            if board.board[nx, ny] == opp_id:
                                cnt += 1
                            elif board.board[nx, ny] == 0:
                                open_right = True
                                break
                            else:
                                break
                        for k in range(1, 5):
                            nx, ny = x - dx * k, y - dy * k
                            if not (0 <= nx < board.size and 0 <= ny < board.size):
                                break
                            if board.board[nx, ny] == opp_id:
                                cnt += 1
                            elif board.board[nx, ny] == 0:
                                open_left = True
                                break
                            else:
                                break
                        if cnt == 3 and open_left and open_right:
                            threat_points.append((x, y))
                        # 检查对手半活四
                        if cnt == 4 and (open_left or open_right):
                            threat_points.append((x, y))
                        # 检查自己半活三/四
                        cnt_my = 1
                        my_open_left = my_open_right = False
                        for k in range(1, 5):
                            nx, ny = x + dx * k, y + dy * k
                            if not (0 <= nx < board.size and 0 <= ny < board.size):
                                break
                            if board.board[nx, ny] == my_id:
                                cnt_my += 1
                            elif board.board[nx, ny] == 0:
                                my_open_right = True
                                break
                            else:
                                break
                        for k in range(1, 5):
                            nx, ny = x - dx * k, y - dy * k
                            if not (0 <= nx < board.size and 0 <= ny < board.size):
                                break
                            if board.board[nx, ny] == my_id:
                                cnt_my += 1
                            elif board.board[nx, ny] == 0:
                                my_open_left = True
                                break
                            else:
                                break
                        if (cnt_my == 3 and (my_open_left or my_open_right)) or (cnt_my == 4):
                            my_threat = True
            return threat_points, my_threat
        threat_points, my_threat = find_threat_point()
        if threat_points and not my_threat:
            # 直接防守第一个威胁点
            return threat_points[0]
        root = MCTSNode(board.clone(), self.player_id)
        start_time = time.time()
        simulations = 0
        while simulations < self.simulation_count:
            if time.time() - start_time > 10:
                break
            node = root
            # 1. Selection
            while not node.is_terminal() and node.is_fully_expanded():
                total_visits = sum(child.visits for child in node.children) + 1
                untried_count = len([c for c in node.children if c.visits == 0])
                node = max(
                    node.children,
                    key=lambda n: n.wu_uct_score(self.C, total_parent_visits=total_visits, untried_count=untried_count)
                )
            # 2. Expansion
            if not node.is_terminal() and node.untried_actions:
                # 用启发式排序裁剪（只保留前5步）
                moves = node.board.get_valid_moves(node.player, self._evaluate, top_n=5)
                move = random.choice(moves) if moves else random.choice(node.untried_actions)
                if move in node.untried_actions:
                    node.untried_actions.remove(move)
                next_board = node.board.clone()
                next_board.place(move[0], move[1], node.player)
                next_player = 2 if node.player == 1 else 1
                child = MCTSNode(next_board, next_player, parent=node, action=move)
                node.children.append(child)
                node = child
            # 3. Simulation（IDDFS+置换表，时间缩短为0.5秒，最大深度8）
            score = self._iddfs_simulation(node.board, node.player, max_time=0.5, max_depth_limit=8)
            # 4. Backpropagation
            self._backpropagate(node, score)
            simulations += 1
        # 选择访问次数最多的子节点
        best_child = max(root.children, key=lambda c: c.visits) if root.children else None
        return best_child.action if best_child else board.get_valid_moves()[0]
    def _iddfs_simulation(self, board, player, max_time=0.5, max_depth_limit=8):
        import time
        start = time.time()
        best_score = None
        trans_table = {}
        # 检查是否有威胁（对手有冲五/活四）
        def has_opp_four():
            opp_id = 2 if player == 1 else 1
            for dx, dy in [(1,0),(0,1),(1,1),(1,-1)]:
                for x in range(board.size):
                    for y in range(board.size):
                        line = []
                        for k in range(-4,5):
                            nx, ny = x+k*dx, y+k*dy
                            if 0<=nx<board.size and 0<=ny<board.size:
                                line.append(board.board[nx,ny])
                            else:
                                line.append(-1)
                        for i in range(len(line)-4):
                            window = line[i:i+5]
                            opp_count = window.count(opp_id)
                            e_count = window.count(0)
                            if opp_count == 4 and e_count == 1:
                                return True
            return False
        # 动态调整最大深度
        if has_opp_four():
            dynamic_max_depth = max_depth_limit  # 有威胁时用原深度
            dynamic_top_n = 8
        else:
            dynamic_max_depth = max(1, int(max_depth_limit * 0.7))  # 否则减少更多
            dynamic_top_n = 3
        max_depth = 1
        while time.time() - start < max_time and max_depth <= dynamic_max_depth:
            score = self._minimax_simulation(board, player, max_depth, True, float('-inf'), float('inf'), trans_table, dynamic_top_n)
            if best_score is None or score > best_score:
                best_score = score
            max_depth += 1
        return best_score if best_score is not None else 0

    def _minimax_simulation(self, board, player, depth, maximizing, alpha, beta, trans_table=None, top_n=5):
        winner = board.get_winner()
        zobrist_key = self._zobrist_hash(board, player, depth)
        if trans_table is not None and zobrist_key in trans_table:
            return trans_table[zobrist_key]
        if winner == self.player_id:
            return 100000
        elif winner is not None:
            return -100000
        if depth == 0 or board.is_terminal():
            val = self._evaluate(board)
            if trans_table is not None:
                trans_table[zobrist_key] = val
            return val
        valid_moves = board.get_valid_moves(player, self._evaluate, top_n=top_n)
        if maximizing:
            max_score = float('-inf')
            for move in valid_moves:
                board_copy = board.clone()
                board_copy.place(move[0], move[1], player)
                score = self._minimax_simulation(board_copy, 2 if player==1 else 1, depth-1, False, alpha, beta, trans_table, top_n)
                max_score = max(max_score, score)
                alpha = max(alpha, score)
                if beta <= alpha or max_score < -1e8:  # 剪枝：分数明显无望时立即return
                    break
            if trans_table is not None:
                trans_table[zobrist_key] = max_score
            return max_score
        else:
            min_score = float('inf')
            opp_id = 2 if player == 1 else 1
            for move in valid_moves:
                board_copy = board.clone()
                board_copy.place(move[0], move[1], opp_id)
                score = self._minimax_simulation(board_copy, player, depth-1, True, alpha, beta, trans_table, top_n)
                min_score = min(min_score, score)
                beta = min(beta, score)
                if beta <= alpha or min_score > 1e8:  # 剪枝：分数明显无望时立即return
                    break
            if trans_table is not None:
                trans_table[zobrist_key] = min_score
            return min_score

    def _zobrist_hash(self, board, player, depth):
        h = 0
        for x in range(board.size):
            for y in range(board.size):
                v = board.board[x, y]
                if v:
                    h ^= int(ZOBRIST_TABLE[x, y, v, depth % ZOBRIST_DEPTH])
        h ^= int(ZOBRIST_TABLE[0, 0, player, depth % ZOBRIST_DEPTH])
        return h

    def _evaluate(self, board):
        key = board.board.tobytes()
        if key in self._eval_cache:
            return self._eval_cache[key]
        my_id = self.player_id
        opp_id = 2 if my_id == 1 else 1
        # 检查自己是否有直接胜利
        if board.get_winner() == my_id:
            return 1e9
        # 检查对手是否有冲五/活四
        def has_opp_four():
            for dx, dy in [(1,0),(0,1),(1,1),(1,-1)]:
                for x in range(board.size):
                    for y in range(board.size):
                        line = []
                        for k in range(-4,5):
                            nx, ny = x+k*dx, y+k*dy
                            if 0<=nx<board.size and 0<=ny<board.size:
                                line.append(board.board[nx,ny])
                            else:
                                line.append(-1)
                        for i in range(len(line)-4):
                            window = line[i:i+5]
                            opp_count = window.count(opp_id)
                            e_count = window.count(0)
                            my_count = window.count(my_id)
                            if opp_count == 4 and e_count == 1 and my_count == 0:
                                return True
            return False
        if has_opp_four():
            return -1e9
        def score_patterns(player):
            score = 0
            patterns = {
                (5, 0): 1000000,   # 活五
                (4, 1): 500000,    # 活四（冲五，优先级极高）
                (4, 0): 200000,     # 冲四
                (3, 2): 10000,     # 活三
                (3, 1): 3000,      # 眠三
                (2, 2): 500,      # 活二
                (2, 1): 100        # 眠二
            }
            # 位置权重：中心高，边缘低
            pos_weight = np.zeros((board.size, board.size))
            center = board.size // 2
            for x in range(board.size):
                for y in range(board.size):
                    pos_weight[x, y] = center - max(abs(x - center), abs(y - center))
            for dx, dy in [(1,0),(0,1),(1,1),(1,-1)]:
                for x in range(board.size):
                    for y in range(board.size):
                        line = []
                        for k in range(-4,5):
                            nx, ny = x+k*dx, y+k*dy
                            if 0<=nx<board.size and 0<=ny<board.size:
                                line.append(board.board[nx,ny])
                            else:
                                line.append(-1)
                        for i in range(len(line)-4):
                            window = line[i:i+5]
                            p_count = window.count(player)
                            e_count = window.count(0)
                            opp_id = 2 if player == 1 else 1
                            opp_count = window.count(opp_id)
                            # 四连进攻（自己四子一空）
                            if p_count == 4 and e_count == 1 and opp_count == 0:
                                score += 400000
                            # 四连防守（对手四子一空）
                            if opp_count == 4 and e_count == 1 and p_count == 0:
                                score += 500000
                            # 三连进攻（自己三子两空）
                            if p_count == 3 and e_count == 2 and opp_count == 0:
                                if window[0]==0 and window[4]==0:
                                    score += 10000
                            # 三连防守（对手三子两空）
                            if opp_count == 3 and e_count == 2 and p_count == 0:
                                if window[0]==0 and window[4]==0:
                                    score += 9000
                            if p_count == 5:
                                score += patterns[(5,0)]
                            elif p_count == 4 and e_count == 1:
                                if window[0]==0 or window[4]==0:
                                    score += patterns[(4,1)]
                                else:
                                    score += patterns[(4,0)]
                            elif p_count == 3 and e_count == 2:
                                if window[0]==0 and window[4]==0:
                                    score += patterns[(3,2)]
                                else:
                                    score += patterns[(3,1)]
                            elif p_count == 2 and e_count == 3:
                                if window[0]==0 and window[4]==0:
                                    score += patterns[(2,2)]
                                else:
                                    score += patterns[(2,1)]
                            # 位置分加权
                            for idx, cell in enumerate(window):
                                if cell == player:
                                    wx, wy = x + (idx-2)*dx, y + (idx-2)*dy
                                    if 0<=wx<board.size and 0<=wy<board.size:
                                        score += 2*pos_weight[wx, wy]  # 中心加权更高
            return score
        my_score = score_patterns(my_id)
        opp_score = score_patterns(opp_id)
        total_score = my_score - opp_score
        self._eval_cache[key] = total_score
        return total_score

    def _backpropagate(self, node, score):
        while node is not None:
            node.visits += 1
            node.wins += score
            node = node.parent

# ================= 测试代码 =================
if __name__ == "__main__":
    board = GomokuBoard(size=15)
    ai = MCTSBot(player_id=1, simulation_count=50, max_depth=3)
    # 人类先手
    board.place(7, 7, 2)
    board.place(7, 8, 1)
    board.place(8, 8, 2)
    board.place(8, 9, 1)
    board.place(9, 9, 2)
    print("当前棋盘:")
    print(board.board)
    move = ai.get_action(board)
    print(f"AI推荐落子: {move}")