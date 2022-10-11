import numpy as np
from random import sample, choice, randint
from json import dump, load


# Generation de carte


class Map:
    TRUE = 'true'
    NO_ADJACENT = 'no_adjacent'
    NO_CROSSOVER = 'no_crossover'

    def __init__(self, m=10, n=10, n_walls=10, path_generator=NO_ADJACENT, n_enemies=0, enemy_cross_walls=True):
        self.n = n
        self.m = m
        self.enemy_cross_walls = enemy_cross_walls
        self.grid = np.zeros((m, n), int)  # Create an empty map

        self.border_cells = [(0, y) for y in range(n)]
        self.border_cells += [(m - 1, y) for y in range(n)]
        self.border_cells += [(x, 0) for x in range(m)]
        self.border_cells += [(x, n - 1) for x in range(m)]

        self.entry_coordinates = choice(self.border_cells)  # Define the entry point

        # Create a possible path: random walk from the starting point until it reaches a border
        self.path = [self.entry_coordinates]
        next_cell = [cell for cell in self.immediately_surrounding_cells_coordinates(self.entry_coordinates)
                     if cell not in self.border_cells]
        if next_cell:  # A border starting point
            self.path += next_cell
        else:  # A corner starting point
            self.path += sample(self.immediately_surrounding_cells_coordinates(self.entry_coordinates), 1)
            self.path += [cell for cell in self.surrounding_cells_coordinates(self.entry_coordinates)
                          if cell not in self.border_cells]

        if path_generator == self.NO_ADJACENT:
            self.path_generator_random_no_adjacent()
        if path_generator == self.NO_CROSSOVER:
            self.path_generator_random_no_crossover()
        if path_generator == self.TRUE:
            self.path_generator_true_random()

        self.exit_coordinates = self.path[-1]  # Define the exit point

        # Add the walls
        possible_cells = [(x, y) for x in range(self.m) for y in range(self.n)]
        possible_cells = [cell for cell in possible_cells if cell not in self.path]

        wall_cells = sample(possible_cells, min(n_walls, len(possible_cells)))

        for cell in wall_cells:
            self.grid[cell] = 1  # In the grid: 0 means no wall and 1 means a wall

        # Add enemies
        if enemy_cross_walls:
            possible_cells = [(x, y) for x in range(self.m) for y in range(self.n)]
        else:
            possible_cells = possible_cells + self.path
        possible_cells.remove(self.entry_coordinates)
        possible_cells.remove(self.exit_coordinates)

        self.enemy_starting_coordinates = sample(possible_cells, min(n_enemies, len(possible_cells)))

    def surrounding_cells_coordinates(self, coordinates):
        cells_coordinate = []
        for x in range(max(0, coordinates[0] - 1), min(self.m, coordinates[0] + 2)):
            for y in range(max(0, coordinates[1] - 1), min(self.n, coordinates[1] + 2)):
                if (x, y) != coordinates:
                    cells_coordinate += [(x, y)]
        return cells_coordinate

    def immediately_surrounding_cells_coordinates(self, coordinates):
        cells_coordinate = []
        for x in range(max(0, coordinates[0] - 1), min(self.m, coordinates[0] + 2)):
            if x != coordinates[0]:
                cells_coordinate += [(x, coordinates[1])]
        for y in range(max(0, coordinates[1] - 1), min(self.n, coordinates[1] + 2)):
            if y != coordinates[1]:
                cells_coordinate += [(coordinates[0], y)]
        return cells_coordinate

    def path_generator_true_random(self):
        while self.path[-1] not in self.border_cells:
            self.path += sample(self.immediately_surrounding_cells_coordinates(self.path[-1]), 1)
        return

    def path_generator_random_no_crossover(self):
        initial_path = self.path.copy()
        while self.path[-1] not in self.border_cells:
            possible_next_cells = [cell for cell in self.immediately_surrounding_cells_coordinates(self.path[-1])
                                   if cell not in self.path]
            if not possible_next_cells:  # Path stuck inside itself
                break
            self.path += sample(possible_next_cells, 1)
        if self.path[-1] not in self.border_cells:  # The path got stuck inside itself, try again
            self.path = initial_path
            self.path_generator_random_no_crossover()
        return

    def path_generator_random_no_adjacent(self):
        initial_path = self.path.copy()
        forbidden_cells = self.path.copy()
        for cell in self.path[:-2]:
            forbidden_cells += self.surrounding_cells_coordinates(cell)
        while self.path[-1] not in self.border_cells:
            possible_next_cells = [cell for cell in self.immediately_surrounding_cells_coordinates(self.path[-1])
                                   if cell not in forbidden_cells]
            if not possible_next_cells:  # Path stuck inside itself
                break
            self.path += sample(possible_next_cells, 1)
            forbidden_cells += self.surrounding_cells_coordinates(self.path[-3])

        if self.path[-1] not in self.border_cells:  # The path got stuck inside itself, try again
            self.path = initial_path
            self.path_generator_random_no_crossover()
        return

    def get_proximity_classes(self, starting_coordinates, ending_coordinates=(-1, -1)):
        """
        return a list of list, from the cell, to cells within distance 1, to cells within distance 2....
        walls block this propagation
        If ending coordinates are given, will not stop when reached
        """
        if self.grid[starting_coordinates]:  # A wall -> no path
            return []

        proximity_classes = [[], [starting_coordinates]]
        while ending_coordinates not in proximity_classes[-1] and proximity_classes[-1]:
            # Ending condition : no more cell to reach or reached the ending cell
            new_cells = []
            for cell in proximity_classes[-1]:
                new_cells += self.immediately_surrounding_cells_coordinates(cell)  # find surrounding cells
            new_cells = list(dict.fromkeys(new_cells))  # remove duplicates
            new_cells = [cell for cell in new_cells
                         if cell not in proximity_classes[-1] + proximity_classes[-2]  # not already seen
                         and not self.grid[cell]]  # not a wall
            proximity_classes += [new_cells]

        proximity_classes = [proximity_class for proximity_class in proximity_classes if proximity_class]

        return proximity_classes

    def optimal_path(self, starting_coordinates):
        """
        Return a (non unique) shortest list of coordinates to go from the starting coordinates to the exit cell
        Contains the initial and exit coordinate

        If no path is possible, returns an empty list
        """
        proximity_classes = self.get_proximity_classes(starting_coordinates, self.exit_coordinates)

        if not proximity_classes or self.exit_coordinates not in proximity_classes[-1]:  # Stuck/wall -> no path
            return []

        proximity_classes.pop(-1)
        path = [self.exit_coordinates]

        while proximity_classes:  # There is a path and the initial coordinate is not the exit cell
            inner_ring = proximity_classes.pop(-1)
            neighbours = self.immediately_surrounding_cells_coordinates(path[0])
            for cell in neighbours:
                if cell in inner_ring:
                    path = [cell] + path
                    break
        return path


class RandomPlayer:
    def play(self, coordinates, reward):
        return choice([Environment.GAUCHE, Environment.DROITE, Environment.HAUT, Environment.BAS])


class QSearcherPlayer:
    def __init__(self, q_grid_dict):
        self.q_grid_dict = q_grid_dict

    def play(self, coordinates, reward):
        d = self.q_grid_dict[coordinates[0]][coordinates[1]]
        return max(d, key=d.get)

class Environment:
    HAUT = 'H'
    BAS = 'B'
    DROITE = 'D'
    GAUCHE = 'G'
    action_list = [HAUT, DROITE, BAS, GAUCHE]
    gamma = 0.5
    base_reward = -1
    wall_reward = -5
    exit_reward = 25
    min_score = -200
    enemy_reward = -100

    def __init__(self, map, player=RandomPlayer()):
        self.map = map
        self.current_step = 0
        self.score = 0
        self.agent_coordinates = self.map.entry_coordinates
        self.player = player
        self.path_taken = []
        self.enemy_coordinates = self.map.enemy_starting_coordinates

    def new_coordinates_from_action(self, coordinates, action):
        if action == self.HAUT:
            new_coordinates = (coordinates[0] - 1, coordinates[1])
        elif action == self.BAS:
            new_coordinates = (coordinates[0] + 1, coordinates[1])
        elif action == self.DROITE:
            new_coordinates = (coordinates[0], coordinates[1] + 1)
        elif action == self.GAUCHE:
            new_coordinates = (coordinates[0], coordinates[1] - 1)
        return new_coordinates

    def step(self, action):
        if action not in self.action_list:  # Action error
            print('Wrong action')
            return self.agent_coordinates, 0, 0

        if self.agent_coordinates in self.enemy_coordinates:          # Hit an enemy
            self.agent_coordinates = self.map.entry_coordinates       # Back to starting position
            self.score += self.enemy_reward                           # Lose points

        if self.score < self.min_score:                               # GAME OVER
            return self.agent_coordinates, 0, 1

        self.current_step += 1

        # Get where to move
        new_coordinates = self.new_coordinates_from_action(self.agent_coordinates, action)

        if not 0 <= new_coordinates[0] <= self.map.m - 1 \
                or not 0 <= new_coordinates[1] <= self.map.n - 1 \
                or self.map.grid[new_coordinates] == 1:              # Outside or a wall
            self.score += self.wall_reward
            new_coordinates = self.agent_coordinates
            reward = self.wall_reward + self.base_reward
            game_over = 0

        elif new_coordinates == self.map.exit_coordinates:           # Exit found
            self.score += self.exit_reward + self.base_reward
            self.agent_coordinates = new_coordinates
            reward = self.exit_reward + self.base_reward
            game_over = 1

        else:                                                        # No wall, no exit
            self.agent_coordinates = new_coordinates
            self.score += self.base_reward
            reward = self.base_reward
            game_over = 0

        # move enemies
        new_positions = []
        for enemy in self.enemy_coordinates:
            possible_move = self.map.immediately_surrounding_cells_coordinates(enemy)
            if not self.map.enemy_cross_walls:
                possible_move = [move for move in possible_move if not self.map.grid[move]]
            if not possible_move:
                possible_move = [enemy]
            new_positions += [choice(possible_move)]
        self.enemy_coordinates = new_positions
        return new_coordinates, reward, game_over

    def play_game(self, render_every_turn=False):
        end = 0
        reward = self.score
        self.path_taken += [self.agent_coordinates]
        while end == 0:
            new_coordinates, reward, end = self.step(self.player.play(self.agent_coordinates, reward))
            self.path_taken += [self.agent_coordinates]
            if render_every_turn:
                print('________________________')
                self.render(enemy_current_position=True)
                print('________________________')
        return

    def reset(self):
        self.agent_coordinates = self.map.entry_coordinates
        self.enemy_coordinates = self.map.enemy_starting_coordinates
        self.score = 0
        self.current_step = 0
        self.path_taken = []
        return self.agent_coordinates

    def render(self, render_path=False, enemy_current_position=False):
        grid = np.array([['¤' if self.map.grid[(x, y)] else ' '
                          for y in range(self.map.n)] for x in range(self.map.m)], str)
        if render_path:
            for cell in self.path_taken:
                grid[cell] = '.'
        grid[self.map.entry_coordinates] = 'S'
        grid[self.map.exit_coordinates] = 'F'

        if enemy_current_position:
            for enemy in self.enemy_coordinates:
                grid[enemy] = 'A'
        else:
            for enemy in self.map.enemy_starting_coordinates:
                grid[enemy] = 'A'

        grid[self.agent_coordinates] = 'X'

        print(str(grid).replace(' [', '').replace('[', '').replace(']', '').replace("'", ''))

    def q_star_grid_dict(self):
        """
        m x n matrix containing a dictionary per cell whose keys are the possible actions
        Initialized at -200 for walls and cells stuck
        Computed with the optimal policy
        """
        grid_dict = []
        remaining_q_sum = np.ones((self.map.m, self.map.n)) * self.min_score
        proximity_to_exit = self.map.get_proximity_classes(self.map.exit_coordinates)

        rest = (self.exit_reward + self.base_reward) * self.gamma
        remaining_q_sum[self.map.exit_coordinates] = 0
        proximity_to_exit.pop(0)
        while proximity_to_exit:
            proximity_class = proximity_to_exit.pop(0)
            for cell in proximity_class:
                remaining_q_sum[cell] = rest
            rest = self.base_reward * self.gamma + self.gamma * rest

        for x in range(0, self.map.m):
            grid_dict += [[]]
            for y in range(0, self.map.n):
                grid_dict[-1] += [{}]
                if remaining_q_sum[(x, y)] == self.min_score:    # Is a wall/stuck -> minimal score
                    for action in self.action_list:
                        grid_dict[-1][-1][action] = self.min_score
                elif (x, y) == self.map.exit_coordinates:       # Is the exit point -> maximal score
                    for action in self.action_list:
                        grid_dict[-1][-1][action] = self.exit_reward
                else:                                        # Is not a wall nor the exit
                    for action in self.action_list:
                        self.agent_coordinates = (x, y)
                        self.score = 0
                        new_coordinates, reward, finished = self.step(action)
                        grid_dict[-1][-1][action] = reward + remaining_q_sum[new_coordinates]
        return grid_dict

    def q_iterative_grid_dict_player(self, learning_rate=0.1, number_iterations=100):
        """
        m x n matrix containing a dictionary per cell whose keys are the possible actions
        Initialized at 0 everywhere
        A player tries to follow the Q value for a game and update it each move
        """

        grid_dict = [[{action: 0 for action in self.action_list} for y in range(self.map.n)] for x in range(self.map.m)]
        for iteration in range(number_iterations):
            starting_position = (randint(0, self.map.m - 1), randint(0, self.map.n - 1))
            self.reset()
            self.agent_coordinates = starting_position
            self.player = QSearcherPlayer(grid_dict)
            end = 0
            reward = self.score
            self.path_taken += [self.agent_coordinates]
            while end == 0:
                action = self.player.play(self.agent_coordinates, reward)
                new_coordinates, reward, end = self.step(action)
                grid_dict[self.path_taken[-1][0]][self.path_taken[-1][1]][action] += learning_rate * (
                    reward + self.gamma * (max(grid_dict[new_coordinates[0]][new_coordinates[1]].values())
                                           - grid_dict[self.path_taken[-1][0]][self.path_taken[-1][1]][action])
                )
                self.path_taken += [new_coordinates]
        return grid_dict

    def q_iterative_grid_dict(self, learning_rate=0.1, number_iterations=100):
        """
        m x n matrix containing a dictionary per cell whose keys are the possible actions
        Initialized at -200 for walls
        Every cell make all possible action, update Q
        """
        # Initialize: start everywhere and make every possible move
        grid_dict = []
        for x in range(0, self.map.m):
            grid_dict += [[]]
            for y in range(0, self.map.n):
                grid_dict[-1] += [{}]
                if self.map.grid[(x, y)]:                                          # Is a wall
                    for action in self.action_list:
                        grid_dict[-1][-1][action] = self.min_score
                elif (x, y) == self.map.exit_coordinates:                          # Is the exit
                    for action in self.action_list:
                        grid_dict[-1][-1][action] = self.exit_reward
                else:
                    for action in self.action_list:
                        self.agent_coordinates = (x, y)
                        self.score = 0
                        new_coordinates, reward, finished = self.step(action)
                        grid_dict[-1][-1][action] = reward
        for iteration in range(number_iterations):
            new_grid_dict = grid_dict.copy()
            for x in range(0, self.map.m):
                for y in range(0, self.map.n):
                    for action in self.action_list:

                        self.agent_coordinates = (x, y)
                        self.score = 0
                        new_coordinates, reward, finished = self.step(action)

                        new_grid_dict[x][y][action] += learning_rate * (
                            reward + self.gamma * (max(grid_dict[new_coordinates[0]][new_coordinates[1]].values())
                                                   - grid_dict[x][y][action]))
            grid_dict = new_grid_dict

        return grid_dict


if __name__ == '__main__':
    map = Map(10, 10, 30, Map.NO_ADJACENT)

    env = Environment(map)
    env.render()
    print(env.q_star_grid_dict())
