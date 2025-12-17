import heapq
import math
import numpy as np

"""
"""

DIRS = [
    (1, 0), # 위쪽 (북) 
    (0, -1),  # 왼쪽 (서)
    (-1, 0), # 아래쪽 (남)
    (0, 1) # 오른쪽 (동)
]  # (dx, dy)


def is_free(x, y, occ):
    """해당 셀이 free인지"""
    height, width = occ.shape
    if 0 <= x < width and 0 <= y < height:
        return occ[y, x] == 0
    return False


def next_direction(dir_idx, turn):
    """turn = 0(직진), +1(좌), -1(우)"""
    return (dir_idx + turn) % 4


def turn_cost(prev_dir, new_dir):
    """회전 패널티"""
    if prev_dir == new_dir:
        return 0          # 직진
    if abs(prev_dir - new_dir) == 2:
        return 2          # U-turn
    return 1              # 90도 회전


def manhattan_h(a, b):
    """맨해튼 휴리스틱"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# ---------------------------
# 이웃(=후보) 생성
# ---------------------------
def neighbors_dir(x, y, dir_idx, occ):
    """
    3가지 후보:
        직진(turn = 0)
        좌회전(turn = +1)
        우회전(turn = -1)
    """
    result = []
    for turn in [0, +1, -1]:
        nd = next_direction(dir_idx, turn)
        dx, dy = DIRS[nd]
        nx, ny = x + dx, y + dy
        if is_free(nx, ny, occ):
            result.append(((nx, ny, nd), turn))
    return result


# ---------------------------
# 경로 복원
# ---------------------------
def reconstruct_path(parent, goal_state):
    path = []
    node = goal_state
    while node in parent:
        path.append(node)
        node = parent[node]
        if node is None:
            break
    path.reverse()
    return path


# ---------------------------
# 회전 지점(직각 waypoint) 추출
# ---------------------------
def extract_corners(path):
    if len(path) < 3:
        return path

    corners = [path[0]]
    for i in range(1, len(path) - 1):
        (x0, y0, d0) = path[i - 1]
        (x1, y1, d1) = path[i]
        (x2, y2, d2) = path[i + 1]

        dx1, dy1 = x1 - x0, y1 - y0
        dx2, dy2 = x2 - x1, y2 - y1

        if (dx1, dy1) != (dx2, dy2):
            corners.append(path[i])

    corners.append(path[-1])
    return corners

# 장애물 주변 2칸 (r칸)을 1로 채운 벽 주위 buffer zone 생성
def inflate_costmap(occ, radius):
    height, width = occ.shape
    inflated = occ.copy()

    for y in range(height):
        for x in range(width):
            if occ[y, x] == 1: # 장애물이면
                for dy in range(-radius, radius + 1):
                    for dx in range(-radius, radius + 1):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            inflated[ny, nx] = 1
    return inflated

# ---------------------------
# 직각주행
# ---------------------------
def right_angle_astar(start, goal, occ, init_dir=0):
    """
    start = (x, y)
    goal  = (x, y)
    init_dir = 초기 진행 방향 (0:북,1:서,2:남,3:동) (좌측 하단 xy기준축 + 오른쪽 방향 y축 + 위쪽 방향 x축 좌표계 기준)
    """
    start_state = (start[0], start[1], init_dir)
    goal_xy = goal

    openq = []
    heapq.heappush(openq, (0, start_state))

    # 초기 goal : cost = 0, e.g. { (0, 0, 1) : 0 }
    g = {start_state: 0}
    parent = {start_state: None}

    while openq:
        _, current = heapq.heappop(openq)
        x, y, dir_idx = current

        if (x, y) == goal_xy:
            return reconstruct_path(parent, current)

        for (next_state, turn) in neighbors_dir(x, y, dir_idx, occ):
            nx, ny, nd = next_state
            # 이동 비용 1 + 회전 패널티
            move_cost = 1
            rot_cost = turn_cost(dir_idx, nd)
            new_cost = g[current] + move_cost + rot_cost

            if new_cost < g.get(next_state, float("inf")):
                g[next_state] = new_cost
                parent[next_state] = current

                h = manhattan_h((nx, ny), goal_xy)
                f = new_cost + h
                heapq.heappush(openq, (f, next_state))

    return []  # 실패


if __name__ == "__main__":
    # 0은 free, 1은 obstacle
    occ = np.zeros((20, 20), dtype=np.uint8)

    # 장애물 예시
    occ[5, 0:15] = 1
    occ[12, 5:20] = 1
    inflated = inflate_costmap(occ, radius=2)

    # 예상 waypoint
    # s(0,0) -> w1(17,0) -> w2(17,9) -> w3(2,9) -> g(2,13)
    # 방향 ( , , <방향값> ) 
    # 0 : 위쪽 (북)
    # 1 : 왼쪽 (서)
    # 2 : 아래쪽 (남)
    # 3 : 오른쪽 (동)
    start = (0, 0)
    goal  = (2, 18)

    # path = right_angle_astar(start, goal, occ, init_dir=0)
    path = right_angle_astar(start, goal, inflated, init_dir=0)
    print("원본 경로:")
    print(path)

    corners = extract_corners(path)
    print("\n직각 waypoint:")
    print(corners)
