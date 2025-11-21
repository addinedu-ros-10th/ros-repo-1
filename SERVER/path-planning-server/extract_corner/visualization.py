import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

def draw_path(grid, start, goal, path, title="Path Visualization"):
    """
    grid : numpy 배열 (0=free, 1=obstacle)
    start, goal : (x, y)
    path : [(x, y), ...] 또는 [(x, y, dir), ...]
    """
    # --- 1. 맵 반전 (0행이 위쪽이므로 y축 뒤집기)
    grid_flipped = np.flipud(grid)

    # --- 2. Figure 생성
    fig, ax = plt.subplots(figsize=(8, 10))
    ax.imshow(grid_flipped, cmap='gray_r', origin='lower', interpolation='nearest')

    rows, cols = grid.shape
    ax.set_aspect('equal')

    # --- 3. 경로 좌표 추출
    if len(path[0]) == 2:
        xs, ys = zip(*path)
    else:
        xs, ys, _ = zip(*path)

    # y좌표 반전 보정 (상하 뒤집힘 대응)
    ys = [rows - 1 - y for y in ys]
    # ys = [rows - 1 - y for y in ys]

    # --- 4. 경로 선 그리기
    ax.plot(xs, ys, color='blue', linewidth=1.5, label='Path')

    # --- 5. Start / Goal 표시
    sx, sy = start
    gx, gy = goal
    sy_plot = rows - 1 - sy
    gy_plot = rows - 1 - gy

    ax.scatter(sx, sy_plot, c='green', s=60, marker='o', label='Start')
    ax.scatter(gx, gy_plot, c='red', s=60, marker='X', label='Goal')

    # --- 6. 축 및 격자 설정
    ax.set_xticks(np.arange(-0.5, cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, rows, 1), minor=True)
    ax.grid(which='minor', color='lightgray', linewidth=0.5)

    # 5칸마다 좌표 표시
    ax.xaxis.set_major_locator(MultipleLocator(5))
    ax.yaxis.set_major_locator(MultipleLocator(5))
    ax.tick_params(which='major', length=0)

    ax.set_xlabel("X (grid index)")
    ax.set_ylabel("Y (grid index)")
    ax.set_title(title)
    ax.legend(loc='upper right')

    plt.show()



def draw_path_1(grid, start, goal, path, title="Path Visualization"):
    """
    grid : numpy 배열 (0=free, 1=obstacle)
    start, goal : (x, y)
    path : [(x, y), ...] 또는 [(x, y, dir), ...]
    """
    # --- 1. 맵 반전 (0행이 위쪽이므로 y축 뒤집기)
    # grid_flipped = np.flipud(grid)

    # --- 2. Figure 생성
    fig, ax = plt.subplots(figsize=(8, 10))
    ax.imshow(grid, cmap='gray_r', origin='lower', interpolation='nearest')

    rows, cols = grid.shape
    ax.set_aspect('equal')

    # --- 3. 경로 좌표 추출
    if len(path[0]) == 2:
        xs, ys = zip(*path)
    else:
        xs, ys, _ = zip(*path)

    # y좌표 반전 보정 (상하 뒤집힘 대응)
    # ys = [rows - 1 - y for y in ys]
    # ys = [rows - 1 - y for y in ys]

    # --- 4. 경로 선 그리기
    ax.plot(xs, ys, color='blue', linewidth=1.5, label='Path')

    # --- 5. Start / Goal 표시
    sx, sy = start
    gx, gy = goal
    # sy_plot = rows - 1 - sy
    # gy_plot = rows - 1 - gy

    ax.scatter(sx, sy, c='green', s=60, marker='o', label='Start')
    ax.scatter(gx, gy, c='red', s=60, marker='X', label='Goal')

    # --- 6. 축 및 격자 설정
    ax.set_xticks(np.arange(-0.5, cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, rows, 1), minor=True)
    ax.grid(which='minor', color='lightgray', linewidth=0.5)

    # 5칸마다 좌표 표시
    ax.xaxis.set_major_locator(MultipleLocator(5))
    ax.yaxis.set_major_locator(MultipleLocator(5))
    ax.tick_params(which='major', length=0)

    ax.set_xlabel("X (grid index)")
    ax.set_ylabel("Y (grid index)")
    ax.set_title(title)
    ax.legend(loc='upper right')

    plt.show()


def draw_waypoint_segments(grid, start, goal, waypoints, segments, title="Waypoint Path Visualization"):
    """
    grid       : numpy 2D map (0=free, 1=obstacle)
    start      : (x, y)
    goal       : (x, y)
    waypoints  : [(x, y), ...]
    segments   : [segment1, segment2, ...]
                 각 segment는 [(x,y,dir)] 또는 [(x,y)]
    """
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MultipleLocator

    # --- 1. 맵 반전 (grid 0행이 위로 가는 형태 보정)
    # grid_flipped = np.flipud(grid)

    rows, cols = grid.shape

    # fig, ax = plt.subplots(figsize=(8, 10))
    # ax.imshow(grid_flipped, cmap='gray_r', origin='lower', interpolation='nearest')
    # ax.imshow(grid, cmap='gray_r', origin='lower', interpolation='nearest')
    # ax.set_aspect('equal')

    # --- 1. 맵 반전
    grid_flipped = np.flipud(grid)

    fig, ax = plt.subplots(figsize=(8, 10))
    ax.imshow(grid_flipped, cmap='gray_r', origin='lower', interpolation='nearest')
    ax.set_aspect('equal')


    colors = ["blue", "orange", "green", "purple", "cyan", "magenta", "yellow"]

    # --- 2. 각 segment 표시
    for idx, seg in enumerate(segments):
        if len(seg[0]) == 2:
            xs, ys = zip(*seg)
        else:
            xs, ys, _ = zip(*seg)

        ys_plot = [rows - 1 - y for y in ys]
        ax.plot(xs, ys_plot, linewidth=2, color=colors[idx % len(colors)], label=f"Segment {idx+1}")

    # --- 3. waypoint 표시
    for (wx, wy) in waypoints:
        wy_plot = rows - 1 - wy
        ax.scatter(wx, wy_plot, c='yellow', edgecolors='black', s=80, marker='s', label="Waypoint")

    # --- 4. Start / Goal
    sx, sy = start
    gx, gy = goal
    sy_plot = rows - 1 - sy
    gy_plot = rows - 1 - gy
    ax.scatter(sx, sy_plot, c='green', s=100, marker='o', label='Start')
    ax.scatter(gx, gy_plot, c='red', s=120, marker='X', label='Goal')

    # --- 5. Grid + ticks
    ax.set_xticks(np.arange(-0.5, cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, rows, 1), minor=True)
    ax.grid(which='minor', color='lightgray', linewidth=0.5)

    ax.xaxis.set_major_locator(MultipleLocator(5))
    ax.yaxis.set_major_locator(MultipleLocator(5))

    ax.set_title(title)
    ax.set_xlabel("X index")
    ax.set_ylabel("Y index")
    ax.legend(loc="upper right")

    plt.show()
