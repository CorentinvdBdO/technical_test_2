from main import Map, Environment, QSearcherPlayer

if __name__ == '__main__':

    map = Map(10, 12, 30, Map.NO_ADJACENT, n_enemies=2, enemy_cross_walls=False)
    env = Environment(map)

    print('Map, enemy starting positions are represented as a A')
    env.render()

    q_star_grid = env.q_star_grid_dict()
    q_iterative_grid = env.q_iterative_grid_dict_player(learning_rate=0.5, number_iterations=1000)

    env.player = QSearcherPlayer(q_star_grid)
    env.reset()
    env.play_game()
    print('Path taken by the player which looks at the best option according to the Q star value')
    env.render(render_path=True)

    env.player = QSearcherPlayer(q_iterative_grid)
    env.reset()
    env.play_game(render_every_turn=False)
    print('Path taken by the player which looks at the best option according to the iterated Q value')
    env.render(render_path=True)
    print("The more enemies, the harder it is to get to the exit for the iterative Q, but it can learn to avoid their "
          "zones of influence.")
    print("The Q star version learns the better path without the enemies, and then never tries to avoid them.")
