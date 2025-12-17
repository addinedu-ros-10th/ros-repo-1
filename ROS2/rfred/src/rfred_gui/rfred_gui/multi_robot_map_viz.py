#!/usr/bin/env python3
# 멀티 로봇 위치 
import time
import rclpy
import numpy as np
import multiprocessing
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from rclpy.node import Node
from map.map_grid import grid
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
from matplotlib.transforms import Affine2D
from matplotlib.patches import Wedge

# from map_grid import grid
from tf2_ros import Buffer, TransformListener
from tf2_ros import TransformException
from rclpy.time import Time
from matplotlib.patches import Rectangle, Arc
from matplotlib.lines import Line2D
from matplotlib.transforms import Affine2D
from matplotlib.patches import Circle


robots = [
    {"domain": 11, "robot_id": "pinky1", "topic": "/tf"},
    {"domain": 12, "robot_id": "pinky2", "topic": "/tf"},
    {"domain": 13, "robot_id": "pinky3", "topic": "/tf"},
]


# ROS2 Twist 구독 노드
    # 메인 프로세스로 큐를 넘겨주는 ROS 노드
class RobotSubscriber(Node):
    def __init__(self, robot_id, topic, queue):
        super().__init__(f"robot_sub_{robot_id}")
        self.robot_id = robot_id
        self.queue = queue

        # TF Buffer & Listener 초기화
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # 주기적 TF 조회 (예: 20Hz)
        self.timer = self.create_timer(0.05, self.timer_callback)

    def timer_callback(self):
        try:
            # odom → base_link 변환 조회
            t = self.tf_buffer.lookup_transform(
                "odom",
                "base_link",
                Time(),
            )
            x = t.transform.translation.x
            y = t.transform.translation.y

            # 큐로 (로봇ID, 위치) 전달
            self.queue.put((self.robot_id, x, y))

        except TransformException:
            pass


def ros_process(domain_id: int, robot_id: str, topic: str, queue: multiprocessing.Queue):
    """
    ROS_DOMAIN_ID마다 프로세스에서 rclpy 호출
    """
    rclpy.init(args=None, domain_id=domain_id)
    node = RobotSubscriber(robot_id, topic, queue)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

from matplotlib.patches import Wedge, Rectangle
from matplotlib.transforms import Affine2D

def make_overlay_axes(fig, base_ax, rows, cols, pad=8):
    ax_overlay = fig.add_axes(
        base_ax.get_position(),
        frameon=False,
        label="overlay"
    )
    ax_overlay.set_aspect("equal")
    ax_overlay.set_xlim(-pad, cols - 1 + pad)
    ax_overlay.set_ylim(-pad, rows - 1 + pad)
    ax_overlay.patch.set_alpha(0.0)
    ax_overlay.set_xticks([]); ax_overlay.set_yticks([])
    ax_overlay.set_zorder(base_ax.get_zorder() + 1)

    def _sync(event=None):
        ax_overlay.set_position(base_ax.get_position())

    fig.canvas.mpl_connect("resize_event", _sync)
    fig.canvas.mpl_connect("draw_event", _sync)
    return ax_overlay


def draw_door_absolute(ax, pos, width=1.5, height=1.5, angle_deg=0,
                       face="lightgray", edge="black", alpha=0.3, zorder=10):
    x, y = pos
    door = Wedge((0.0, 0.0), r=1.0, theta1=0, theta2=90,
                 facecolor=face, edgecolor=edge, alpha=alpha, zorder=zorder)

    trans = (Affine2D()
             .scale(width, height)
             .rotate_deg(angle_deg)
             .translate(x, y)
             + ax.transData)
    door.set_transform(trans)
    door.set_clip_on(False)
    ax.add_patch(door)




def draw_block_2x2(ax, x, y, color, alpha=0.2, zorder=2):
    block = Rectangle((x - 0.5, y - 0.5), 2.0, 2.0,
                      facecolor=color, edgecolor="none",
                      alpha=alpha, zorder=zorder)
    ax.add_patch(block)


def draw_label(ax, pos, text, fontsize=9, color="black", zorder=4):
    x, y = pos
    ax.text(x, y, text, ha="left", va="bottom",
            fontsize=fontsize, color=color, zorder=zorder)


def draw(viz, pad=8):
    """
    main에서 이 함수만 호출.
    함수 내부에서:
      1) overlay axes 생성
      2) 문/블록/라벨 등 정적 에셋 생성 및 추가
    """
    # overlay가 이미 있으면 재생성하지 않음
    if not hasattr(viz, "ax_overlay") or viz.ax_overlay is None:
        viz.ax_overlay = make_overlay_axes(
            viz.fig, viz.ax, viz.rows, viz.cols, pad=pad
        )

    axo = viz.ax_overlay  # overlay axes
    axb = viz.ax          # base axes (grid)

    # ---- 문(door) 에셋: overlay에 그림 ----
    # 현관
    draw_door_absolute(axo, (-11.4, -18),  width=6.9, height=6.9, angle_deg=270)
    draw_door_absolute(axo, (2.4, -18),  width=6.9, height=6.9, angle_deg=180)

    # 생활관
    draw_door_absolute(axo, (-12, 10),  width=6.9, height=6.9, angle_deg=90)
    draw_door_absolute(axo, (-12, 36.5),  width=6.9, height=6.9, angle_deg=90)
    draw_door_absolute(axo, (-12, 63),  width=6.9, height=6.9, angle_deg=90)

    draw_door_absolute(axo, (-2, 85),  width=6.9, height=6.9, angle_deg=0)

    # draw_robot_dot_absolute((-2, 85))
    # ---- 예시: 2x2 영역/라벨이 필요하면 base에 ----
    # draw_block_2x2(axb, 10, 16, "orange")
    # draw_label(axb, (4, 20), "생활실1")



# 멀티로봇 지도 시각화
class MultiRobotGridVisualizer:
    def __init__(self, grid: np.ndarray, robot_ids):
        """
        grid : rfred_map_init.py 의 grid (0=free, 1=obstacle)
        robot_ids : ["pinky1", "pinky2", ...]
        """
        self.grid = grid
        self.rows, self.cols = grid.shape
        self.robot_positions = {rid: None for rid in robot_ids}




        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(7, 11))



        # self.draw_door_absolute_0((0, 0),  width=4.5, height=4.5)
        # self.draw_door_absolute_270((0, 0), width=4.5, height=4.5)

        self.draw_door_absolute_0((17, 0),  width=4.5, height=4.5)
        self.draw_door_absolute_270((17, 9), width=4.5, height=4.5)

        self.draw_door_absolute_0((14, 27), width=5.0, height=5.0)
        self.draw_door_absolute_270((14, 37), width=5.0, height=5.0)

        self.im = self.ax.imshow(
            grid,
            cmap="gray_r",
            origin="lower",
            interpolation="nearest",
        )



        self.ax.set_aspect("equal")


        # 로봇별 색상
        base_colors = ["red", "blue", "green", "orange", "magenta", "cyan", "yellow"]
        self.robot_colors = {
            rid: base_colors[i % len(base_colors)]
            for i, rid in enumerate(robot_ids)
        }

        # 로봇별 scatter
        self.scatter_handles = {}
        for rid in robot_ids:
            sc = self.ax.scatter([], [], c=self.robot_colors[rid], s=60, marker="o", label=rid)
            self.scatter_handles[rid] = sc

        # 로봇별 위치 라벨 (이름 + 좌표)
        self.text_handles = {}
        for rid in robot_ids:
            txt = self.ax.text(
                0, 0, "",                         # 초기 위치/텍스트는 빈 값
                color=self.robot_colors[rid],
                fontsize=8,
                ha="left", va="bottom",
                fontweight="bold",
                bbox=dict(facecolor="white", alpha=0.6,
                          edgecolor="none", pad=1),
            )
            self.text_handles[rid] = txt

        self.ax.set_xticks(np.arange(-0.5, self.cols, 1), minor=True)
        self.ax.set_yticks(np.arange(-0.5, self.rows, 1), minor=True)
        self.ax.grid(which="minor", color="lightgray", linewidth=0.5)

        from matplotlib.ticker import MultipleLocator
        self.ax.xaxis.set_major_locator(MultipleLocator(5))
        self.ax.yaxis.set_major_locator(MultipleLocator(5))
        self.ax.tick_params(which="major", length=0)

        # PAD = 6  # 셀 단위
        # self.ax.set_xlim(-PAD, self.cols - 1 + PAD)
        # self.ax.set_ylim(-PAD, self.rows - 1 + PAD)
        self.ax.set_xlim([0, self.cols - 1])
        self.ax.set_ylim([0, self.rows - 1])
        self.ax.set_xlabel("X (5cm)")
        self.ax.set_ylabel("Y (5cm)")
        # self.ax.set_title("")

        # 문, 지역, 텍스트 라벨 시각화
        # self.draw_door() # (x, y, 방향)
        # self.draw_block_2x2((10, 15)) # (x, y, 색깔)
        # self.draw_label # (x, y, 문구)
        # 문, 지역, 텍스트 라벨 시각화
        # self.draw_door(16, 1, "W")          # (x, y, 방향)
        self.draw_block_2x2(10, 16, "red")  # 핑키 마킹
        self.draw_block_2x2(10, 20, "red")  
        self.draw_block_2x2(10, 24, "red")  

        self.draw_block_2x2(18, 62, "orange")  # 배식대 마킹
        self.draw_block_2x2(22, 62, "orange")  # 배식대 마킹
        self.draw_block_2x2(26, 62, "orange")  # 배식대 마킹
        
        self.draw_block_2x2(32, 62, "blue")  # 퇴식대 마킹
        self.draw_block_2x2(36, 62, "blue")  # 퇴식대 마킹
        self.draw_block_2x2(40, 62, "blue")  # 퇴식대 마킹

        self.draw_block_2x2(25, 27, "yellow")  # 식탁 마킹
        self.draw_block_2x2(25, 42, "yellow")  # 식탁 마킹
        self.draw_block_2x2(25, 57, "yellow")  # 식탁 마킹

        self.draw_block_2x2(40, 27, "yellow")  # 식탁 마킹
        self.draw_block_2x2(40, 42, "yellow")  # 식탁 마킹
        self.draw_block_2x2(40, 57, "yellow")  # 식탁 마킹


        # self.draw_label(10, 15, "생활실1")  # (x, y, 문구)

        # self.ax.legend(loc="upper right")
        plt.show()

    # def update_robot(self, robot_id: str, x_raw: float, y_raw: float):
    #     """
    #     x_raw, y_raw -> 시각화 그리드 좌표에 맞게 변환
    #     """
    #     gx = int(np.clip(x_raw, 0, self.cols - 1))
    #     gy = int(np.clip(y_raw, 0, self.rows - 1))

    #     # y 변환 (visualization.draw_path)
    #     #    ys_plot = rows - 1 - y
    #     # plot_y = self.rows - 1 - gy
    #     plot_y = gy
    #     plot_x = gx

    #     self.robot_positions[robot_id] = (plot_x, plot_y)

    def update_robot(self, robot_id: str, x_meter: float, y_meter: float):
        # 맵 resolution (5cm = 0.05m)
        resolution = 0.05

        # TF(m) → grid index
        gx = int(x_meter / resolution)
        gy = int(y_meter / resolution)

        # grid 크기 범위로 클립
        gx = int(np.clip(gx, 0, self.cols - 1))
        gy = int(np.clip(gy, 0, self.rows - 1))

        # 시각화용 Y 방향(필요 시 반전)
        # plot_y = self.rows - 1 - gy  # 사용하려면 반전
        plot_y = gy
        plot_x = gx
        print(robot_id)
        print(gx)
        print(gy)

        self.robot_positions[robot_id] = (plot_x, plot_y)


    def render(self):
        """
        수신된 로봇 위치 갱신
        """
        for rid, pos in self.robot_positions.items():
            if pos is None:
                continue
            self.scatter_handles[rid].set_offsets([pos])

            x, y = pos

            # 라벨 텍스트: "pinky1 (12, 7)" 형태
            label = f"{rid} ({x}, {y})"
            # 점에서 약간 오른쪽 위로 띄워서 보이게
            self.text_handles[rid].set_position((x + 0.3, y + 0.3))
            self.text_handles[rid].set_text(label)

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()




    def draw_door_absolute_0(self, pos, width=1.5, height=1.5, color="black"):
        """
        pos: (x, y) — 문 힌지(좌하단 기준)의 '절대 데이터 좌표'
        width, height: 문 반지름(가로/세로) 크기, 데이터 좌표 기준
        """
        x, y = pos

        # 1) 로컬 좌표(원점 기준)에서 단위(반지름=1) 사분원 생성
        door = Wedge(
            (0.0, 0.0),
            r=1.0,
            theta1=0,
            theta2=90,
            facecolor="lightgray",
            edgecolor="black",
            alpha=0.3,
            zorder=10
        )

        # 2) 로컬 도형 -> (width, height) 스케일 -> (x, y)로 평행이동 -> 데이터좌표에 고정
        trans = (
            Affine2D()
            .scale(width, height)
            .translate(x, y)
            + self.ax.transData
        )
        door.set_transform(trans)

        door.set_clip_on(False)   # 핵심: 축 밖에서도 안 잘리게
        self.ax.add_patch(door)

    # def draw_door_absolute_0(self, pos, width=1.5, height=0.3, color="black"):
    #     """
    #     pos: (x, y) — 문 좌하단의 '절대 데이터 좌표'
    #     width, height: 문 사각형 크기 (데이터 좌표 기준)
    #     """
    #     x, y = pos
    #     # Wedge(start_angle, end_angle) 로 반원 생성
    #     door = Wedge(
    #         (x, y), 
    #         width, 
    #         theta1=0,       # 시작 각도 (도 단위)
    #         theta2=90,     # 끝 각도: 180도면 반원
    #         facecolor="lightgray",
    #         edgecolor="black",
    #         alpha=0.3           # 핵심
    #     )

    #     self.ax.add_patch(door)

    #     # 즉시 반영
    #     self.fig.canvas.draw()
    #     self.fig.canvas.flush_events()


    def draw_door_absolute_90(self, pos, width=1.5, height=0.3, color="black"):
        """
        pos: (x, y) — 문 좌하단의 '절대 데이터 좌표'
        width, height: 문 사각형 크기 (데이터 좌표 기준)
        """
        x, y = pos
        # Wedge(start_angle, end_angle) 로 반원 생성
        door = Wedge(
            (x, y), 
            width, 
            theta1=90,       # 시작 각도 (도 단위)
            theta2=180,     # 끝 각도: 180도면 반원
            facecolor="lightgray",
            edgecolor="black",
            alpha=0.3,
            zorder=10
        )

        self.ax.add_patch(door)

        # 즉시 반영
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


    def draw_door_absolute_180(self, pos, width=1.5, height=0.3, color="black"):
        """
        pos: (x, y) — 문 좌하단의 '절대 데이터 좌표'
        width, height: 문 사각형 크기 (데이터 좌표 기준)
        """
        x, y = pos
        # Wedge(start_angle, end_angle) 로 반원 생성
        door = Wedge(
            (x, y), 
            width, 
            theta1=180,       # 시작 각도 (도 단위)
            theta2=270,     # 끝 각도: 180도면 반원
            facecolor="lightgray",
            edgecolor="black",
            alpha=0.3,
            zorder=10
        )

        self.ax.add_patch(door)

        # 즉시 반영
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def draw_door_absolute_270(self, pos, width=1.5, height=0.3, color="black"):
        """
        pos: (x, y) — 문 좌하단의 '절대 데이터 좌표'
        width, height: 문 사각형 크기 (데이터 좌표 기준)
        """
        x, y = pos
        # Wedge(start_angle, end_angle) 로 반원 생성
        door = Wedge(
            (x, y), 
            width, 
            theta1=270,       # 시작 각도 (도 단위)
            theta2=360,     # 끝 각도: 180도면 반원
            facecolor="lightgray",
            edgecolor="black",
            alpha=0.3,
            zorder=10
        )

        self.ax.add_patch(door)

        # 즉시 반영
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def draw_block_2x2(self, x, y, color):
        """
        (x, y): 2x2 블록의 좌하단 셀 인덱스
        color: matplotlib color string/tuple
        """
        alpha = 0.2  # "연한 색" 표현

        block = Rectangle(
            (x - 0.5, y - 0.5),
            2.0, 2.0,
            facecolor=color,
            edgecolor="none",
            alpha=alpha,
            zorder=2
        )
        self.ax.add_patch(block)

        def draw_label(self, pos, text):
            x, y = pos  # pos는 라벨의 좌하단 기준점(그리드 기준)
            self.ax.text(
                x, y, text,
                ha="left", va="bottom",
                fontsize=9,
                color="black",
                zorder=4
            )

    def draw_label(self, x, y, text):
        """
        (x, y): 라벨의 좌하단 기준점(그리드 좌표)
        text: 표기할 문구
        """
        self.ax.text(
            x, y, text,
            ha="left", va="bottom",
            fontsize=9,
            color="black",
            zorder=4
        )

# 도메인 + 멀티 로봇 시각화
def main():

    robot_ids = [rb["robot_id"] for rb in robots]

    # ROS / matplotlib 공유 자료 큐 (로봇 위치 전달)
    queue: multiprocessing.Queue = multiprocessing.Queue()

    # ROS 프로세스 시작
    processes = []
    for rb in robots:
        p = multiprocessing.Process(
            target=ros_process,
            args=(rb["domain"], rb["robot_id"], rb["topic"], queue),
        )
        p.daemon = True
        p.start()
        processes.append(p)

    # 시각화 초기화
    viz = MultiRobotGridVisualizer(grid, robot_ids)
    
    print("rfred 요양로봇 위치 시각화를 시작합니다.")
    draw(viz, pad=12)
    # 문이 좌표계 오른쪽(그리드 바깥)에도 위치 가능
    # viz.draw_door_absolute((45, 8), width=2.0, height=0.4)

    # 입구 문을 그리드 경계에 정확히 맞춰 배치
    # viz.draw_door_absolute_0((17, 0), width=4.0, height=4.0)
    # viz.draw_door_absolute_270((17, 8), width=4.0, height=4.0)
    

    try:
        while True:
            # 로봇 위치 시각화 (ROS -> 큐 -> matplotlib)
            while not queue.empty():
                robot_id, x, y = queue.get()
                viz.update_robot(robot_id, x, y)

            viz.render()
            time.sleep(0.05)  # 20Hz
    except KeyboardInterrupt:
        print("\n종료 요청, 프로세스 정리 중...")
    finally:
        for p in processes:
            if p.is_alive():
                p.terminate()
        for p in processes:
            p.join()
        print("정상 종료.")


if __name__ == "__main__":
    main()

# 스폰 데모 위치
# pinky1 : (12, 7)
# pinky2 : (35, 20)
# pinky3 : (55, 5)
