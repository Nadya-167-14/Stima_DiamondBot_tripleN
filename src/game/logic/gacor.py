#ANT Squad_123140186_123140167_123140157
from abc import ABC
from typing import Tuple, Optional, List, Dict
from collections import deque
from game.logic.base import BaseLogic

from game.models import Board, GameObject, Position, Properties
   
class tripleN(BaseLogic):
    def __init__(self):
        self.visited_cells = set()
        self.current_target_position: Optional[Position] = None
        self.current_target_diamond_id: Optional[str] = None
        self.TACKLE_DIAMOND_THRESHOLD = 3 
        self.EVADE_DIAMOND_THRESHOLD = 2 
        self.EVADE_DETECTION_RANGE = 3 

    def _calculate_all_distances(self, start: Position, board: Board) -> Tuple[Dict[Tuple[int, int], int], Dict[Tuple[int, int], Tuple[int, int]]]:
        # BFS untuk mencari jarak terpendek ke semua sel yang dapat dijangkau
        queue = deque([(start, 0)])
        distance_map = {(start.x, start.y): 0}
        parent_map = {}
        visited_bfs = set([(start.x, start.y)])
        possible_moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        while queue:
            current_pos, dist = queue.popleft()
            for dx, dy in possible_moves:
                next_x, next_y = current_pos.x + dx, current_pos.y + dy
                next_pos_obj = Position(y=next_y, x=next_x)
                next_pos_coord = (next_x, next_y)
                # Memastikan gerakan valid (tidak melewati dinding/batas) dan belum dikunjungi
                if board.is_valid_move(current_pos, dx, dy) and next_pos_coord not in visited_bfs:
                    visited_bfs.add(next_pos_coord)
                    distance_map[next_pos_coord] = dist + 1
                    parent_map[next_pos_coord] = (current_pos.x, current_pos.y)
                    queue.append((next_pos_obj, dist + 1))
        return distance_map, parent_map

    def _reconstruct_path_moves(self, start: Position, target: Position, parent_map: Dict[Tuple[int, int], Tuple[int, int]]) -> Optional[List[Tuple[int, int]]]:
        # Merekonstruksi jalur dari parent_map yang dihasilkan BFS
        path_positions = []
        target_coord = (target.x, target.y)
        current_coord = (target.x, target.y)
        start_coord = (start.x, start.y)

        # Jika target tidak di parent_map (tidak dapat dijangkau)
        if target_coord not in parent_map and current_coord != start_coord: return None
        
        while current_coord != start_coord:
            path_positions.append(Position(x=current_coord[0], y=current_coord[1]))
            if current_coord not in parent_map: return None 
            current_coord = parent_map[current_coord]
        
        path_positions.append(Position(x=start_coord[0], y=start_coord[1]))
        path_positions.reverse() # Membalik jalur agar dari start ke target
        path_moves = [(p2.x - p1.x, p2.y - p1.y) for p1, p2 in zip(path_positions, path_positions[1:])]
        return path_moves

    def _find_best_diamond(self, diamonds: List[GameObject], from_pos: Position, distance_map: Dict[Tuple[int, int], int], diamond_type: Optional[str] = None, prioritize_distance_only: bool = False) -> Optional[Position]:
        best_diamond_target = None
        best_metric = float('inf') if prioritize_distance_only else -1.0

        for diamond in diamonds:
            diamond_value = diamond.properties.points if diamond.properties and diamond.properties.points is not None else 1
            if (diamond_type == 'red' and diamond_value < 2) or (diamond_type == 'blue' and diamond_value > 1): continue
            
            diamond_coord = (diamond.position.x, diamond.position.y)
            if diamond_coord in distance_map:
                distance = distance_map[diamond_coord]
                if distance == 0: continue

                current_metric = distance if prioritize_distance_only else diamond_value / (distance + 1e-6) # Metric = nilai/jarak
                if (prioritize_distance_only and current_metric < best_metric) or (not prioritize_distance_only and current_metric > best_metric):
                    best_metric = current_metric
                    best_diamond_target = diamond.position
        return best_diamond_target

    def _find_nearest_unvisited(self, current_pos: Position, board: Board, distance_map: Dict[Tuple[int, int], int]) -> Optional[Position]:
        nearest_unvisited_pos = None
        min_dist_unvisited = float('inf')
        for cell_coord, dist in distance_map.items():
            if cell_coord not in self.visited_cells:
                if dist < min_dist_unvisited:
                    min_dist_unvisited = dist
                    nearest_unvisited_pos = Position(x=cell_coord[0], y=cell_coord[1])
        return nearest_unvisited_pos

    def _find_closest_diamond_from_start(self, diamonds: List[GameObject], start_pos: Position, board: Board) -> Optional[Position]:
        # Mencari diamond terdekat dari start_pos (biasanya base)
        base_distance_map, _ = self._calculate_all_distances(start_pos, board)
        best_diamond_from_base = None
        min_dist_from_base = float('inf')

        for diamond in diamonds:
            diamond_coord = (diamond.position.x, diamond.position.y)
            if diamond_coord in base_distance_map:
                distance_from_base = base_distance_map[diamond_coord]
                if distance_from_base < min_dist_from_base:
                    min_dist_from_base = distance_from_base
                    best_diamond_from_base = diamond.position
        return best_diamond_from_base

    def _find_red_button(self, board: Board, current_pos: Position, distance_map: Dict[Tuple[int, int], int]) -> Optional[Position]:
        # Mencari red button terdekat
        red_buttons = [obj for obj in board.game_objects if obj.type == 'artifact'] 
        closest_button = None
        min_dist = float('inf')
        for button in red_buttons:
            button_coord = (button.position.x, button.position.y)
            if button_coord in distance_map:
                dist = distance_map[button_coord]
                if dist < min_dist:
                    min_dist = dist
                    closest_button = button.position
        return closest_button

    def _find_tackle_target(self, board_bot: GameObject, board: Board, distance_map: Dict[Tuple[int, int], int]) -> Optional[Position]:
        # Mencari target tackle
        if not board_bot.properties or not board_bot.properties.can_tackle: return None
        best_tackle_target = None
        max_diamonds_on_target = -1
        all_other_bots = [bot for bot in board.bots if bot.id != board_bot.id]

        for other_bot in all_other_bots:
            other_bot_pos = other_bot.position
            other_bot_coord = (other_bot_pos.x, other_bot_pos.y)
            # Hanya tackle jika lawan di samping bot
            if other_bot_coord in distance_map and distance_map[other_bot_coord] == 1:
                if other_bot.properties and other_bot.properties.diamonds is not None and \
                   other_bot.properties.diamonds >= self.TACKLE_DIAMOND_THRESHOLD:
                    if other_bot.properties.diamonds > max_diamonds_on_target:
                        max_diamonds_on_target = other_bot.properties.diamonds
                        best_tackle_target = other_bot_pos
        return best_tackle_target

    def _get_farthest_safe_neighbor(self, current_pos: Position, board: Board, other_bots: List[GameObject]) -> Optional[Tuple[int, int]]:
        # Mencari gerakan tetangga yang paling jauh dari bot lawan
        possible_moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        best_move = None
        max_min_distance_to_enemy = -1 

        for dx, dy in possible_moves:
            next_x, next_y = current_pos.x + dx, current_pos.y + dy
            next_pos = Position(x=next_x, y=next_y)

            if board.is_valid_move(current_pos, dx, dy):
                min_distance_to_enemy_for_this_move = float('inf')
                for other_bot in other_bots:
                    dist_to_enemy = abs(next_pos.x - other_bot.position.x) + abs(next_pos.y - other_bot.position.y)
                    min_distance_to_enemy_for_this_move = min(min_distance_to_enemy_for_this_move, dist_to_enemy)
                
                if not other_bots or min_distance_to_enemy_for_this_move == float('inf'): return (dx, dy) 
                if min_distance_to_enemy_for_this_move > max_min_distance_to_enemy:
                    max_min_distance_to_enemy = min_distance_to_enemy_for_this_move
                    best_move = (dx, dy)
        
        # Fallback jika tidak ada gerakan yang menjauhkan, pilih yang valid
        if best_move is None and possible_moves:
             for dx, dy in possible_moves:
                if board.is_valid_move(current_pos, dx, dy): return (dx, dy)
        return best_move

    def next_move(self, board_bot: GameObject, board: Board) -> Tuple[int, int]:
        current_pos = board_bot.position
        self.visited_cells.add((current_pos.x, current_pos.y))
        props = board_bot.properties
        target_pos = None
        distance_map_from_current, parent_map = self._calculate_all_distances(current_pos, board)
        remaining_time_seconds = props.milliseconds_left / 1000 if props.milliseconds_left is not None else float('inf')
        other_bots = [bot for bot in board.bots if bot.id != board_bot.id]

        # 1. Greedy by Return (Waktu Kritis)
        if remaining_time_seconds < 10 and props.diamonds is not None and props.diamonds > 0 and props.base:
            base_coord = (props.base.x, props.base.y)
            if base_coord in distance_map_from_current: target_pos = props.base
                
        # 2. Greedy by Escape (Menghindari Bot Lain)
        if target_pos is None and props.diamonds is not None and props.diamonds > self.EVADE_DIAMOND_THRESHOLD and other_bots:
            should_evade = False
            for other_bot in other_bots:
                dist_to_other_bot = abs(current_pos.x - other_bot.position.x) + abs(current_pos.y - other_bot.position.y)
                if dist_to_other_bot <= self.EVADE_DETECTION_RANGE: should_evade = True; break
            if should_evade:
                safe_move = self._get_farthest_safe_neighbor(current_pos, board, other_bots)
                if safe_move: return safe_move # Langsung gerak menghindari

        # 3. Greedy by Tackle
        if target_pos is None and props.can_tackle and props.diamonds is not None and props.diamonds < 5:
            tackle_target = self._find_tackle_target(board_bot, board, distance_map_from_current)
            if tackle_target: target_pos = tackle_target

        # 4. Greedy by Return (Inventori Penuh)
        if target_pos is None and props.diamonds is not None and props.diamonds >= 5 and props.base:
            base_coord = (props.base.x, props.base.y)
            if base_coord in distance_map_from_current: target_pos = props.base
        
        # 5. Greedy by Return (Inventori Hampir Penuh - Blue Diamond)
        if target_pos is None and props.diamonds is not None and props.diamonds == 4:
            target_pos = self._find_best_diamond(board.diamonds, current_pos, distance_map_from_current, diamond_type='blue', prioritize_distance_only=True)
            if target_pos is None and props.base:
                base_coord = (props.base.x, props.base.y)
                if (current_pos.x, current_pos.y) != base_coord and base_coord in distance_map_from_current: target_pos = props.base

        # 6. Greedy by Red Button
        if target_pos is None and not board.diamonds:
             target_pos = self._find_red_button(board, current_pos, distance_map_from_current)

        # 7. Greedy by Diamond (densitas Terbaik / Jarak dari Base)
        # Jika belum ada target, prioritaskan diamond terdekat dari base
        if target_pos is None and props.base:
            closest_diamond_from_base_pos = self._find_closest_diamond_from_start(board.diamonds, props.base, board)
            if closest_diamond_from_base_pos and (closest_diamond_from_base_pos.x, closest_diamond_from_base_pos.y) in distance_map_from_current:
                target_pos = closest_diamond_from_base_pos

        # Jika belum ada target, cari diamond densitas terbaik (merah dulu, lalu biru)
        if target_pos is None:
            target_pos = self._find_best_diamond(board.diamonds, current_pos, distance_map_from_current, diamond_type='red', prioritize_distance_only=False)
        if target_pos is None:
            target_pos = self._find_best_diamond(board.diamonds, current_pos, distance_map_from_current, diamond_type='blue', prioritize_distance_only=False)

        # Fallback deposit jika ada diamond tapi tidak ada target lain
        if target_pos is None and props.diamonds is not None and props.diamonds > 0 and props.base:
            base_coord = (props.base.x, props.base.y)
            if (current_pos.x, current_pos.y) != base_coord and base_coord in distance_map_from_current: target_pos = props.base
        
        # 8. Greedy by Exploration (Unvisited Cells)
        if target_pos is None:
            target_pos = self._find_nearest_unvisited(current_pos, board, distance_map_from_current)
        
        # Eksekusi Gerakan
        if target_pos:
            self.current_target_position = target_pos
            path_moves = self._reconstruct_path_moves(current_pos, target_pos, parent_map)
            if path_moves: return path_moves[0]
            else: # Jika jalur ke target utama tidak ditemukan
                self.current_target_position = None 
                # Coba eksplorasi terdekat sebagai fallback
                force_explore_target = self._find_nearest_unvisited(current_pos, board, distance_map_from_current)
                if force_explore_target and (force_explore_target.x, force_explore_target.y) != (current_pos.x, current_pos.y):
                    path_to_explore = self._reconstruct_path_moves(current_pos, force_explore_target, parent_map)
                    if path_to_explore: return path_to_explore[0]

        # Fallback: Gerakan acak jika semua gagal
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            if board.is_valid_move(current_pos, dx, dy): return (dx, dy)
        return (0, 0) # Tetap di tempat
