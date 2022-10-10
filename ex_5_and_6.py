import numpy as np
from main import Map, Environment, QSearcherPlayer

if __name__ == '__main__':
    map = Map(10, 12, 30, Map.NO_ADJACENT)

    env = Environment(map)
    print('Map')
    env.render()
    q_star_grid = env.q_star_grid_dict()
    print(env.q_star_grid_dict())
    haut = np.zeros((map.m, map.n))
    bas = np.zeros((map.m, map.n))
    droite = np.zeros((map.m, map.n))
    gauche = np.zeros((map.m, map.n))

    for x in range(0, map.m):
        for y in range(0, map.n):
            haut[(x, y)] = q_star_grid[x][y][Environment.HAUT]
            bas[(x, y)] = q_star_grid[x][y][Environment.BAS]
            droite[(x, y)] = q_star_grid[x][y][Environment.DROITE]
            gauche[(x, y)] = q_star_grid[x][y][Environment.GAUCHE]
    print('Haut')
    print(haut)
    print('Bas')
    print(bas)
    print('Droite')
    print(droite)
    print('Gauche')
    print(gauche)
    print()
    print('Best move per cell')
    grid = np.array([[max(d, key=d.get)
                      for d in q_star_grid[x]] for x in range(map.m)], str)
    print(str(grid).replace(' [', '').replace('[', '').replace(']', '').replace("'", ''))

    env.player = QSearcherPlayer(q_star_grid)

    env.reset()

    env.play_game()

    print('Path taken by the player which looks at the best option according to the Q value')

    env.render(render_path=True)