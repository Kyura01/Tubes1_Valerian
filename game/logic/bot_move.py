import random
from typing import Optional, Tuple

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position

class Bot_logic(BaseLogic):
    def __init__(self):
        # Waktu sisa (dalam milidetik) sebagai ambang batas untuk pulang
        self.TIME_TO_GO_HOME_THRESHOLD = 15000

    def get_game_objects(self, board: Board):
        """Memindai dan mengkategorikan semua objek di papan."""
        self.diamonds = [obj for obj in board.game_objects if obj.type == "DiamondGameObject"]
        self.bots = [obj for obj in board.game_objects if obj.type == "BotGameObject"]
        self.teleports = [obj for obj in board.game_objects if obj.type == "TeleportGameObject"]

    def calculate_distance(self, pos1: Position, pos2: Position) -> float:
        """Menghitung jarak Euclidean antara dua objek Position."""
        return ((pos2.x - pos1.x) ** 2 + (pos2.y - pos1.y) ** 2) ** 0.5
    
    # --- FUNGSI BARU ---
    def is_diamond_nearby(self, current_pos: Position, radius: int) -> bool:
        """
        Mengecek apakah ada berlian dalam radius blok tertentu (jarak kotak).
        """
        for diamond in self.diamonds:
            # Hitung jarak horizontal dan vertikal
            dist_x = abs(diamond.position.x - current_pos.x)
            dist_y = abs(diamond.position.y - current_pos.y)
            # Jika ada satu saja berlian dalam jangkauan, kembalikan True
            if dist_x <= radius and dist_y <= radius:
                return True
        # Jika loop selesai dan tidak ada berlian terdekat, kembalikan False
        return False

    def find_path(self, current_pos: Position, target_pos: Position) -> Tuple[float, Position]:
        """
        Menemukan jalur tercepat ke target, mempertimbangkan teleport.
        Mengembalikan (jarak, posisi_langkah_selanjutnya).
        """
        # 1. Hitung jarak langsung
        direct_distance = self.calculate_distance(current_pos, target_pos)
        path_cost = direct_distance
        next_step_pos = target_pos

        # 2. Hitung jarak via teleport jika ada teleport
        if len(self.teleports) >= 2:
            # Cari teleport terdekat dari posisi saat ini
            nearest_teleport_in = min(self.teleports, key=lambda t: self.calculate_distance(current_pos, t.position))
            
            # Cari teleport terdekat dari tujuan akhir
            nearest_teleport_out = min(self.teleports, key=lambda t: self.calculate_distance(target_pos, t.position))

            teleport_distance = self.calculate_distance(current_pos, nearest_teleport_in.position) + self.calculate_distance(nearest_teleport_out.position, target_pos)

            # Jika rute teleport lebih pendek, gunakan itu
            if teleport_distance < path_cost:
                path_cost = teleport_distance
                next_step_pos = nearest_teleport_in.position

        return path_cost, next_step_pos

    def next_move(self, board_bot: GameObject, board: Board) -> Tuple[int, int]:
        """Fungsi utama untuk menentukan langkah logis berikutnya."""
        self.get_game_objects(board)
        props = board_bot.properties
        current_pos = board_bot.position

        # --- HIRARKI PENGAMBILAN KEPUTUSAN ---

        # 1. PRIORITAS TERTINGGI: Waktu hampir habis? Segera pulang!
        time_left = props.milliseconds_left or float('inf')
        if time_left < self.TIME_TO_GO_HOME_THRESHOLD and props.diamonds > 0:
            _, goals_pos = self.find_path(current_pos, props.base)

        # 2. PRIORITAS KEDUA: Inventaris penuh? Pulang!
        elif props.diamonds >= props.inventory_size:
            _, goals_pos = self.find_path(current_pos, props.base)

        # --- LOGIKA BARU ---
        # 3. PRIORITAS KETIGA: Punya >= 3 berlian & tidak ada berlian lain di sekitar? Pulang!
        elif props.diamonds >= 3 and not self.is_diamond_nearby(current_pos, 5):
            _, goals_pos = self.find_path(current_pos, props.base)

        # 4. PRIORITAS TERAKHIR: Cari berlian yang paling "menguntungkan"
       # --- LOGIKA BARU ---
        # 4. PRIORITAS TERAKHIR: Cari berlian yang paling "MENGUNTUNGKAN"
        else:
            best_target_pos = None
            # Kita tidak lagi menggunakan biaya, tapi "skor keuntungan"
            best_profit_score = -1.0 
            inventory_space = props.inventory_size - props.diamonds

            for diamond in self.diamonds:
                points = diamond.properties.points or 1
                if points <= inventory_space:
                    # Hitung biaya (jarak) untuk mendapatkan berlian ini
                    cost, _ = self.find_path(current_pos, diamond.position)
                    
                    # Hindari pembagian dengan nol jika bot sudah di atas berlian
                    if cost == 0:
                        cost = 0.01

                    # Hitung skor keuntungan (poin dibagi jarak)
                    profit_score = points / cost
                    
                    # Jika skor keuntungan berlian ini lebih baik, jadikan target baru
                    if profit_score > best_profit_score:
                        best_profit_score = profit_score
                        best_target_pos = diamond.position
            
            # Jika ditemukan berlian yang menguntungkan, kejar itu
            if best_target_pos:
                _, goals_pos = self.find_path(current_pos, best_target_pos)
            # Jika tidak ada berlian yang bisa dikejar, pulang saja
            else:
                _, goals_pos = self.find_path(current_pos, props.base)
        # --- PERHITUNGAN GERAKAN AKHIR ---
        if goals_pos.x == current_pos.x and goals_pos.y == current_pos.y:
            return random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

        delta_x, delta_y = 0, 0
        if current_pos.x < goals_pos.x:
            delta_x = 1
        elif current_pos.x > goals_pos.x:
            delta_x = -1
        
        if current_pos.y < goals_pos.y:
            delta_y = 1
        elif current_pos.y > goals_pos.y:
            delta_y = -1
        
        if delta_x != 0 and delta_y != 0:
            if random.random() < 0.5:
                delta_y = 0
            else:
                delta_x = 0
        
        return delta_x, delta_y