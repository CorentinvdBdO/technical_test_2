
from main import Map, Environment, QSearcherPlayer

if __name__ == '__main__':
    n_games_per_method = 10
    model_dict = {
        'n_maps': 0,
        'q_star': 0,
        'q_player': 0
    }
    per_path_length = {}
    for n_map in range(100):
        print('map #', n_map)
        map = Map(50, 50, 30, Map.NO_ADJACENT, n_enemies=10, enemy_cross_walls=False)
        env = Environment(map)

        path_length = len(map.optimal_path(map.entry_coordinates))
        if path_length not in per_path_length.keys():
            per_path_length[path_length] = model_dict.copy()
        per_path_length[path_length]['n_maps'] += 1

        q_star_grid = env.q_star_grid_dict()
        q_iterative_player_grid = env.q_iterative_grid_dict_player(learning_rate=0.5, number_iterations=1000)

        env.player = QSearcherPlayer(q_star_grid)
        for i in range(n_games_per_method):
            env.reset()
            env.play_game()
            if env.score > env.min_score:
                per_path_length[path_length]['q_star'] += 1

        env.player = QSearcherPlayer(q_iterative_player_grid)
        for i in range(n_games_per_method):
            env.reset()
            env.play_game()
            if env.score > env.min_score:
                per_path_length[path_length]['q_player'] += 1
    for key in sorted(per_path_length.keys()):
        print('For a path of length ', key)
        print(per_path_length[key])
