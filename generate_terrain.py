import numpy as np

def generate_terrain(seed:int=1, resolution:int=8, adjascents:list=None):
    np.random.seed(seed)

    cells = np.random.choice(2,
                            size=(resolution+2, resolution+2),
                            p=[0.4, 0.6])
    
    if adjascents == None:
        cells[0:resolution+1, 0] = 2
        cells[0, 0:resolution+1] = 2
        cells[0:resolution+1, resolution+1] = 2
        cells[resolution+1, 0:resolution+2] = 2

    return cells