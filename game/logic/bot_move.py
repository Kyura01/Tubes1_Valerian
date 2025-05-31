import random
from typing import Optional, Tuple, List

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position

class Bot_logic(BaseLogic):
    """
    Bot ini berfokus pada pengumpulan berlian secara efisien dengan menghitung
    rasio "keuntungan" (poin per jarak) dan memiliki strategi untuk kembali ke markas
    secara strategis.
    """
    def __init__(self):
        # Waktu sisa (dalam milidetik) yang memicu bot untuk segera pulang.
        self.URGENCY_TIMER_LIMIT = 15000
        # Jumlah minimum berlian yang dimiliki untuk mempertimbangkan pulang jika tidak ada berlian lain di sekitar.
        self.CASH_OUT_THRESHOLD = 3
        # Jarak radius untuk memeriksa keberadaan berlian di sekitar.
        self.NEARBY_RADIUS = 5

        # Properti ini akan diisi oleh 'scan_board_state'
        self.gem_locations: List[GameObject] = []
        self.other_bots: List[GameObject] = []
        self.portals: List[GameObject] = []

    def scan_board_state(self, game_state: Board):
        """Mengkategorikan semua objek game di papan untuk akses yang lebih mudah."""
        # Reset daftar sebelum setiap pemindaian
        self.gem_locations.clear()
        self.other_bots.clear()
        self.portals.clear()
        
        for item in game_state.game_objects:
            if item.type == "DiamondGameObject":
                self.gem_locations.append(item)
            elif item.type == "BotGameObject":
                self.other_bots.append(item)
            elif item.type == "TeleportGameObject":
                self.portals.append(item)

    def calculate_dist(self, p1: Position, p2: Position) -> float:
        """Menghitung jarak garis lurus antara dua objek Position."""
        return ((p1.x - p2.x)**2 + (p1.y - p2.y)**2)**0.5

    def check_local_gem_presence(self, my_location: Position, search_radius: int) -> bool:
        """
        Memeriksa apakah ada berlian dalam radius kotak tertentu (jarak Manhattan).
        """
        for gem in self.gem_locations:
            # Hitung jarak absolut pada sumbu x dan y
            delta_x = abs(gem.position.x - my_location.x)
            delta_y = abs(gem.position.y - my_location.y)
            # Jika ada berlian dalam jangkauan pencarian, kembalikan True
            if delta_x <= search_radius and delta_y <= search_radius:
                return True
        return False

    def determine_optimal_route(self, start_pos: Position, end_pos: Position) -> Tuple[float, Position]:
        """
        Menentukan rute terbaik ke tujuan, dengan mempertimbangkan teleport.
        Mengembalikan tuple berisi (total_jarak, tujuan_langkah_berikutnya).
        Tujuan berikutnya bisa berupa posisi akhir atau teleport masuk.
        """
        # Rute 1: Perjalanan langsung
        direct_route_dist = self.calculate_dist(start_pos, end_pos)

        # Rute 2: Menggunakan teleport (jika tersedia)
        if len(self.portals) >= 2:
            # Cari portal terdekat dari posisi awal
            entry_portal = min(self.portals, key=lambda p: self.calculate_dist(start_pos, p.position))
            # Cari portal terdekat dari posisi tujuan
            exit_portal = min(self.portals, key=lambda p: self.calculate_dist(end_pos, p.position))
            
            # Hitung total jarak jika melalui portal
            portal_route_dist = self.calculate_dist(start_pos, entry_portal.position) + self.calculate_dist(exit_portal.position, end_pos)

            # Jika rute portal lebih pendek, gunakan itu
            if portal_route_dist < direct_route_dist:
                # Tujuan langsung berikutnya adalah portal masuk
                return portal_route_dist, entry_portal.position

        # Jika tidak ada portal atau rute langsung lebih cepat, tuju langsung ke 'end_pos'
        return direct_route_dist, end_pos

    def next_move(self, my_robot: GameObject, game_state: Board) -> Tuple[int, int]:
        """Fungsi pengambilan keputusan utama untuk bot."""
        self.scan_board_state(game_state)
        robot_stats = my_robot.properties
        my_location = my_robot.position
        
        # Secara default, bot akan pulang jika tidak ada target lain
        target_destination = robot_stats.base
        is_returning_home = False

        # --- HIRARKI KEPUTUSAN ---
        time_left = robot_stats.milliseconds_left or float('inf')

        # 1. Prioritas Tinggi: Waktu hampir habis dan membawa berlian. Pulang!
        if time_left < self.URGENCY_TIMER_LIMIT and robot_stats.diamonds > 0:
            is_returning_home = True
        # 2. Inventaris Penuh: Tidak bisa membawa lebih banyak. Pulang!
        elif robot_stats.diamonds >= robot_stats.inventory_size:
            is_returning_home = True
        # 3. Mundur Strategis: Punya cukup berlian dan tidak ada lagi di sekitar. Pulang!
        elif robot_stats.diamonds >= self.CASH_OUT_THRESHOLD and not self.check_local_gem_presence(my_location, self.NEARBY_RADIUS):
            is_returning_home = True

        # Tentukan tujuan berdasarkan keputusan di atas
        if is_returning_home:
            _, target_destination = self.determine_optimal_route(my_location, robot_stats.base)
        else:
            # 4. Aksi Standar: Cari berlian yang paling menguntungkan.
            optimal_gem_location = None
            max_value_ratio = -1.0 # Inisialisasi dengan nilai negatif
            inventory_room = robot_stats.inventory_size - robot_stats.diamonds

            for gem in self.gem_locations:
                gem_points = gem.properties.points or 1
                if gem_points <= inventory_room:
                    # Hitung "biaya" (jarak) untuk mendapatkan berlian ini
                    cost_to_reach, _ = self.determine_optimal_route(my_location, gem.position)
                    
                    # Hindari pembagian dengan nol jika bot berada tepat di atas berlian
                    cost_to_reach = max(cost_to_reach, 0.01)

                    # Keuntungan = Poin / Jarak
                    value_per_distance = gem_points / cost_to_reach
                    
                    if value_per_distance > max_value_ratio:
                        max_value_ratio = value_per_distance
                        optimal_gem_location = gem.position
            
            # Jika ditemukan berlian yang cocok, kejar. Jika tidak, bot akan tetap pada tujuan default (pulang).
            if optimal_gem_location:
                _, target_destination = self.determine_optimal_route(my_location, optimal_gem_location)

        # --- EKSEKUSI GERAKAN ---
        # Jika sudah berada di tujuan (misalnya, terjebak), bergerak acak
        if target_destination == my_location:
            return random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

        # Hitung vektor gerakan
        move_x, move_y = 0, 0
        if target_destination.x > my_location.x:
            move_x = 1
        elif target_destination.x < my_location.x:
            move_x = -1
        
        if target_destination.y > my_location.y:
            move_y = 1
        elif target_destination.y < my_location.y:
            move_y = -1

        # Mencegah gerakan diagonal dengan memprioritaskan sumbu dengan jarak terbesar
        if move_x != 0 and move_y != 0:
            if abs(target_destination.x - my_location.x) > abs(target_destination.y - my_location.y):
                move_y = 0
            else:
                move_x = 0
                
        return move_x, move_y