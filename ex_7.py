from main import Map, Environment, QSearcherPlayer

if __name__ == '__main__':

    map = Map(10, 12, 30, Map.NO_ADJACENT)
    env = Environment(map)

    print('Map')
    env.render()

    print("Q star")
    q_star_grid = env.q_star_grid_dict()
    print(q_star_grid)

    print("Iterative Q")
    q_iterative_grid = env.q_iterative_grid_dict_player(learning_rate=0.5, number_iterations=1000)
    print(q_iterative_grid)

    env.player = QSearcherPlayer(q_star_grid)
    env.reset()
    env.play_game()
    print('Path taken by the player which looks at the best option according to the Q star value')
    env.render(render_path=True)

    env.player = QSearcherPlayer(q_iterative_grid)
    env.reset()
    env.play_game()
    print('Path taken by the player which looks at the best option according to the iterated Q value')
    env.render(render_path=True)