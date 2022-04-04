import math
from operator import ne
from turtle import pos
from sympy import true
from app.collision_map import Collision
from queue import PriorityQueue

# TODO Optimize
def astar(start: tuple[int,int], end: tuple[int,int], size: tuple[int, int], graph: list[list[Collision]]):
    def dst(start, end: tuple[int, int]):
        return math.sqrt(abs(start[0]-end[0])**2 + abs(start[1]-end[1])**2)
    
    def estimate_dist(position: tuple[int, int]):
        return abs(position[0]-end[0]) + abs(position[1]-end[1])
    open_set = PriorityQueue()
    open_set.put((0, start))

    gScore  = {start: 0}  # list of all visited nodes
    parents = {}  # predecessors
    while not open_set.empty():
        _, current = open_set.get()
        if current == end:
            path = [end]
            while path[-1] != start:
                path.append(parents[path[-1]])
            return list(reversed(path))

        for neighbor in get_legal_adjacent_with_size(current, size, graph):
            tentative_gScore = gScore[current] + dst(current, neighbor)
            if neighbor not in gScore or tentative_gScore < gScore[neighbor]:
                parents[neighbor] = current
                gScore[neighbor] = tentative_gScore
                open_set.put((tentative_gScore + estimate_dist(neighbor), neighbor))

    raise Exception("failed to find path")

def get_legal_adjacent_with_size(position: tuple[int,int],  size: tuple[int, int], graph: list[list[Collision]]) -> list[tuple[int,int]]:
    def is_legal_with_size(position: tuple[int,int]) -> bool:
        x, y = position

        if x+size[0] >= len(graph):
            return False
        if y+size[1] >= len(graph[0]):
            return False

        for i in range(size[0]):
            if graph[x+i][y] is not Collision.EMPTY:
                return False
            if graph[x+i][y+size[1]] is not Collision.EMPTY:
                return False
        
        for j in range(size[1]):
            if graph[x][y+j] is not Collision.EMPTY:
                return False
            if graph[x+size[0]][y+j] is not Collision.EMPTY:
                return False
        return True
    
    adj = get_adjacent(position)
    return list(filter(is_legal_with_size, adj))

def get_adjacent(position: tuple[int,int]) -> tuple[tuple[int, int]]:
    x, y = position
    return (
        (x+1, y+1),
        (x+1, y+1),
        (x+1, y),
        (x+1, y-1),
        (x, y+1),
        (x, y-1),
        (x-1, y+1),
        (x-1, y),
        (x-1, y-1),
    )
