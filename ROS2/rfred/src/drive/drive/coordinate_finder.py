import rclpy
from rclpy.node import Node
from tf2_ros import Buffer, TransformListener
from tf2_ros import LookupException, ConnectivityException, ExtrapolationException
import math

class CoorFinder(Node):

    def __init__(self):
        super().__init__('coordinate_finder')
        
        # 1. TF를 사용하기 위한 Buffer와 Listener 생성
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        
        # 테스트를 위해 0.1초마다 위치 출력
        self.timer = self.create_timer(0.1, self.get_current_pose)

    def get_current_pose(self):
        try:
            # 2. 'map' 좌표계 기준 'base_link'의 위치를 조회 (가장 최근 시간 기준)
            # to_frame_rel='map', from_frame_rel='base_link'
            t = self.tf_buffer.lookup_transform(
                'map', 
                'base_link', 
                rclpy.time.Time()) 

            x = t.transform.translation.x
            y = t.transform.translation.y
            
            # 3. 쿼터니언(x,y,z,w)을 오일러 각도(Yaw)로 변환
            qx = t.transform.rotation.x
            qy = t.transform.rotation.y
            qz = t.transform.rotation.z
            qw = t.transform.rotation.w
            
            # Yaw(회전각) 계산 공식
            siny_cosp = 2 * (qw * qz + qx * qy)
            cosy_cosp = 1 - 2 * (qy * qy + qz * qz)
            yaw = math.atan2(siny_cosp, cosy_cosp)

            self.get_logger().info(f'현재 위치 -> x: {x:.3f}, y: {y:.3f}, 각도: {yaw:.3f} rad')
            return x, y, yaw

        except (LookupException, ConnectivityException, ExtrapolationException) as e:
            self.get_logger().warn(f'위치를 찾을 수 없음: {e}')
            return None

def main():
    rclpy.init()
    node = CoorFinder()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()