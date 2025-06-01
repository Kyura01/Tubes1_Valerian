import random
from typing import Optional, Tuple, List
from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position

class Bot_logic(BaseLogic):
 
    def __init__(self):
        self.URGENCY_TIMER_LIMIT = 15000
        self.CASH_OUT_THRESHOLD = 3
        self.NEARBY_RADIUS = 5
        self.gem_locations: List[GameObject] = []
        self.other_bots: List[GameObject] = []
        self.portals: List[GameObject] = []

    def scan_board_state(self, game_state: Board):
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
        return ((p1.x - p2.x)**2 + (p1.y - p2.y)**2)**0.5

    def check_local_gem_presence(self, my_location: Position, search_radius: int) -> bool:
        
        for gem in self.gem_locations:
            delta_x = abs(gem.position.x - my_location.x)
            delta_y = abs(gem.position.y - my_location.y)
            if delta_x <= search_radius and delta_y <= search_radius:
                return True
        return False

    def determine_optimal_route(self, start_pos: Position, end_pos: Position) -> Tuple[float, Position]:
        direct_route_dist = self.calculate_dist(start_pos, end_pos)

        if len(self.portals) >= 2:
            entry_portal = min(self.portals, key=lambda p: self.calculate_dist(start_pos, p.position))
            exit_portal = min(self.portals, key=lambda p: self.calculate_dist(end_pos, p.position))
            
            portal_route_dist = self.calculate_dist(start_pos, entry_portal.position) + self.calculate_dist(exit_portal.position, end_pos)

            if portal_route_dist < direct_route_dist:
                return portal_route_dist, entry_portal.position

        return direct_route_dist, end_pos

    def next_move(self, my_robot: GameObject, game_state: Board) -> Tuple[int, int]:
        self.scan_board_state(game_state)
        robot_stats = my_robot.properties
        my_location = my_robot.position
        
        target_destination = robot_stats.base
        is_returning_home = False

        time_left = robot_stats.milliseconds_left or float('inf')

        if time_left < self.URGENCY_TIMER_LIMIT and robot_stats.diamonds > 0:
            is_returning_home = True
        elif robot_stats.diamonds >= robot_stats.inventory_size:
            is_returning_home = True
        elif robot_stats.diamonds >= self.CASH_OUT_THRESHOLD and not self.check_local_gem_presence(my_location, self.NEARBY_RADIUS):
            is_returning_home = True

     
        if is_returning_home:
            _, target_destination = self.determine_optimal_route(my_location, robot_stats.base)
        else:
            optimal_gem_location = None
            max_value_ratio = -1.0 
            inventory_room = robot_stats.inventory_size - robot_stats.diamonds

            for gem in self.gem_locations:
                gem_points = gem.properties.points or 1
                if gem_points <= inventory_room:
                    cost_to_reach, _ = self.determine_optimal_route(my_location, gem.position)
                    cost_to_reach = max(cost_to_reach, 0.01)
                    value_per_distance = gem_points / cost_to_reach
                    
                    if value_per_distance > max_value_ratio:
                        max_value_ratio = value_per_distance
                        optimal_gem_location = gem.position
            
            if optimal_gem_location:
                _, target_destination = self.determine_optimal_route(my_location, optimal_gem_location)

        if target_destination == my_location:
            return random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

        move_x, move_y = 0, 0
        if target_destination.x > my_location.x:
            move_x = 1
        elif target_destination.x < my_location.x:
            move_x = -1
        
        if target_destination.y > my_location.y:
            move_y = 1
        elif target_destination.y < my_location.y:
            move_y = -1

        if move_x != 0 and move_y != 0:
            if abs(target_destination.x - my_location.x) > abs(target_destination.y - my_location.y):
                move_y = 0
            else:
                move_x = 0
                
        return move_x, move_y