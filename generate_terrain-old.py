import numpy as np
from collections import deque

def generate_terrain(seed:int=1, resolution:int=64, adjascents:list=None):
    #np.random.seed(seed)

    cells = np.random.choice(2,
                            size=(resolution+2, resolution+2),
                            p=[0.5, 0.5])
    
    if adjascents == None:
        cells[0:resolution+1, 0] = 0
        cells[0, 0:resolution+1] = 0
        cells[0:resolution+1, resolution+1] = 0
        cells[resolution+1, 0:resolution+2] = 0

    generating = True
    delta_height_history = deque(maxlen = 5)
    height_map = cells.copy()

    while generating:
        frame = cells.copy()

        for row, col in np.ndindex(cells.shape):
            walls = np.sum(cells[row - 1:row + 2, col-1:col+2]) - cells[row, col]
            if walls > 4:
                cells[row, col] = 0
            else:
                cells[row, col] = 1

       

        delta_height = 0
        for row, col in np.ndindex(cells.shape):
            height_map += cells[row, col]
            delta_height += cells[row, col] - frame[row, col]
        delta_height_history.append(delta_height)
        
        sum_delta_height = 0
        for val in delta_height_history:
            sum_delta_height += val

        mean_delta_height = sum_delta_height / len(delta_height_history)

        if mean_delta_height == 0: generating = False
        
    return cells