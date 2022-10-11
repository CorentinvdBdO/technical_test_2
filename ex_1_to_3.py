from main import Map, Environment,  RandomPlayer

if __name__ == '__main__':
    map = Map(10, 15, 60, Map.NO_ADJACENT)
    env = Environment(map)
    print('Starting position')
    env.render()

    env.play_game()
    print('Final score:', env.score)
    print('Number of steps:', env.current_step)
    env.render()