import itertools
import random


class Minesweeper():
    """
    Minesweeper 游戏的表示
    """

    def __init__(self, height=8, width=8, mines=8):

        # 设置初始宽度、高度和地雷数量
        self.height = height
        self.width = width
        self.mines = set()

        # 初始化一个没有地雷的空区域
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # 随机添加地雷
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # 最初，玩家没有找到任何地雷
        self.mines_found = set()

    def print(self):
        """
        打印地雷位置的文本表示形式。
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        返回给定单元格一行和一列内
        （不包括单元格本身）的地雷数量。
        """

        # 记录附近的地雷数量
        count = 0

        # 遍历一行和一列内的所有单元格
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # 忽略单元格本身
                if (i, j) == cell:
                    continue

                # 如果单元格在边界内并且是地雷，则更新计数
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        检查是否所有地雷都已被标记。
        """
        return self.mines_found == self.mines


class Sentence():
    """
    关于 Minesweeper 游戏的逻辑语句。
    一个语句由一组棋盘单元格和一个表示这些单元格中有多少是地雷的计数组成。
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        返回 self.cells 中所有已知是地雷的单元格的集合。
        """
        if len(self.cells) == self.count and self.count > 0:
            return self.cells.copy()
        return set()

    def known_safes(self):
        """
        返回 self.cells 中所有已知是安全单元格的集合。
        """
        if self.count == 0:
            # If count is 0, all cells in the sentence are safe
            return self.cells.copy()
        return set()

    def mark_mine(self, cell):
        """
        根据一个单元格已知是地雷这一事实，更新内部知识表示。
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        根据一个单元格已知是安全单元格这一事实，更新内部知识表示。
        """
        if cell in self.cells:
            self.cells.remove(cell)
            # Count remains unchanged as the removed cell was safe


class MinesweeperAI():
    """
    Minesweeper 游戏玩家
    """

    def __init__(self, height=8, width=8):

        # 设置初始高度和宽度
        self.height = height
        self.width = width

        # 跟踪哪些单元格已被点击
        self.moves_made = set()

        # 跟踪已知是安全或地雷的单元格
        self.mines = set()
        self.safes = set()

        # 关于游戏已知为真的语句列表
        self.knowledge = []

    def mark_mine(self, cell):
        """
        将单元格标记为地雷，并更新所有知识以也将该单元格标记为地雷。
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        将单元格标记为安全，并更新所有知识以也将该单元格标记为安全。
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        当 Minesweeper 棋盘告诉我们，对于给定的安全单元格，
        有多少相邻单元格是地雷时调用。

        此函数应：
            1) 将单元格标记为已执行的移动
            2) 将单元格标记为安全
            3) 根据 `cell` 和 `count` 的值向 AI 的知识库添加一个新语句
            4) 如果可以根据 AI 的知识库推断出，则将任何其他单元格标记为安全或地雷
            5) 如果可以从现有知识推断出，则向 AI 的知识库添加任何新语句
        """
        # 1) 将单元格标记为已执行的移动
        self.moves_made.add(cell)

        # 2) 将单元格标记为安全, 并更新所有知识
        self.mark_safe(cell)

        # 3) 根据 `cell` 和 `count` 的值向 AI 的知识库添加一个新语句
        #    确保只包括状态未定的单元格。
        
        neighbors = set()
        # 遍历周围8个单元格
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # 忽略单元格本身
                if (i, j) == cell:
                    continue
                # 确保单元格在棋盘范围内
                if 0 <= i < self.height and 0 <= j < self.width:
                    neighbors.add((i, j))
        
        undetermined_neighbors = set()
        # 'count' 是 `cell` 周围地雷的总数。
        # 我们需要形成的语句是 {未确定邻居} = count - (已知在邻居中的地雷数)
        effective_count = count

        for neighbor_cell in neighbors:
            if neighbor_cell in self.mines:
                effective_count -= 1  # 这个已知的地雷已计入count，所以为未知邻居的语句减去它
            elif neighbor_cell in self.safes:
                pass  # 已知安全，不包括在新语句的单元格中
            else:
                undetermined_neighbors.add(neighbor_cell)
        
        # 如果有未确定的邻居，则创建并添加新语句
        if undetermined_neighbors:
            new_sentence = Sentence(undetermined_neighbors, effective_count)
            if new_sentence not in self.knowledge: # __eq__ 已定义
                self.knowledge.append(new_sentence)

        # 4 & 5) 迭代更新知识：标记地雷/安全格，并推断新语句
        while True:
            knowledge_changed_this_iteration = False

            # 从当前知识中推断并标记已知的地雷/安全格
            safes_identified = set()
            mines_identified = set()

            for sentence in list(self.knowledge): # 迭代副本，因为 mark_mine/safe 会修改语句
                for mine_cell in sentence.known_mines():
                    if mine_cell not in self.mines:
                        mines_identified.add(mine_cell)
                
                for safe_cell in sentence.known_safes():
                    if safe_cell not in self.safes:
                        safes_identified.add(safe_cell)
            
            if mines_identified:
                for mc in mines_identified:
                    if mc not in self.mines: # 再次检查，以防在同一次迭代中被其他路径处理
                        self.mark_mine(mc) # 这会更新 self.mines 和 self.knowledge 中的语句
                        knowledge_changed_this_iteration = True
            
            if safes_identified:
                for sc in safes_identified:
                    if sc not in self.safes: # 再次检查
                        self.mark_safe(sc) # 这会更新 self.safes 和 self.knowledge 中的语句
                        knowledge_changed_this_iteration = True

            # 清理：移除空的语句 (单元格集合为空)
            prev_knowledge_len = len(self.knowledge)
            self.knowledge = [s for s in self.knowledge if s.cells]
            if len(self.knowledge) != prev_knowledge_len:
                knowledge_changed_this_iteration = True

            # 使用子集逻辑推断新语句
            newly_derived_sentences_in_pass = [] # 存储本轮推断出的新语句
            
            # 使用知识库的快照进行稳定的比较
            current_knowledge_snapshot = list(self.knowledge)
            
            for s1 in current_knowledge_snapshot:
                for s2 in current_knowledge_snapshot:
                    if s1 == s2: # 不要将语句与自身比较
                        continue
                    
                    # 如果 s2.cells 是 s1.cells 的真子集:
                    # 新语句是 s1.cells - s2.cells = s1.count - s2.count
                    if s2.cells.issubset(s1.cells) and s1.cells != s2.cells:
                        derived_cells = s1.cells - s2.cells
                        derived_count = s1.count - s2.count
                        
                        if derived_cells: # 仅当新语句中有单元格时
                            inferred_s = Sentence(derived_cells, derived_count)
                            
                            # 检查此推断语句是否已知或在本轮中等待添加
                            is_already_present_or_pending = False
                            # 检查主知识库
                            for existing_s in self.knowledge:
                                if existing_s == inferred_s:
                                    is_already_present_or_pending = True
                                    break
                            if not is_already_present_or_pending:
                                # 检查本轮已推断的语句列表
                                for pending_s in newly_derived_sentences_in_pass:
                                    if pending_s == inferred_s:
                                        is_already_present_or_pending = True
                                        break
                            
                            if not is_already_present_or_pending:
                                newly_derived_sentences_in_pass.append(inferred_s)
                                knowledge_changed_this_iteration = True # 发现了一个新的独特语句

            # 将本轮发现的独特新语句添加到主知识库
            if newly_derived_sentences_in_pass:
                for nds in newly_derived_sentences_in_pass:
                    # 最后检查是否已通过其他方式添加到 self.knowledge
                    is_still_new_for_master_list = True
                    for ks_master in self.knowledge:
                        if ks_master == nds:
                            is_still_new_for_master_list = False
                            break
                    if is_still_new_for_master_list:
                        self.knowledge.append(nds)
                        # knowledge_changed_this_iteration 已在上面设置

            if not knowledge_changed_this_iteration:
                break # 如果此完整迭代中没有进行任何更改，则退出循环

    def make_safe_move(self):
        """
        返回 Minesweeper 棋盘上的一个安全单元格以供选择。
        该移动必须已知是安全的，并且尚未执行。

        此函数可以使用 self.mines、self.safes 和 self.moves_made 中的知识，
        但不应修改这些值中的任何一个。
        """
        for safe_cell in self.safes:
            if safe_cell not in self.moves_made:
                return safe_cell
        return None

    def make_random_move(self):
        """
        返回要在 Minesweeper 棋盘上执行的移动。
        应在以下单元格中随机选择：
            1) 尚未选择，并且
            2) 未知是地雷
        """
        possible_moves = []
        for r in range(self.height):
            for c in range(self.width):
                move = (r, c)
                if move not in self.moves_made and move not in self.mines:
                    possible_moves.append(move)
        
        if not possible_moves:
            return None
        else:
            return random.choice(possible_moves)
