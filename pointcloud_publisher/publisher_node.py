import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header
import numpy as np
import struct

class PointCloudPublisher(Node):
    def __init__(self):
        super().__init__('pointcloud_publisher')
        self.publisher_ = self.create_publisher(PointCloud2, '/pointcloud/raw', 10)
        self.timer = self.create_timer(1.0, self.publish_pointcloud)
        self.get_logger().info('PointCloud Publisher started')

    def create_pointcloud2(self, points):
        """将 numpy 点云数组转换为 ROS2 PointCloud2 消息"""
        header = Header()
        header.stamp = self.get_clock().now().to_msg()
        header.frame_id = 'map'

        fields = [
            PointField(name='x', offset=0,  datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4,  datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8,  datatype=PointField.FLOAT32, count=1),
        ]

        point_step = 12  # 3 x float32 = 12 bytes
        data = points.astype(np.float32).tobytes()

        msg = PointCloud2(
            header=header,
            height=1,
            width=len(points),
            fields=fields,
            is_bigendian=False,
            point_step=point_step,
            row_step=point_step * len(points),
            data=data,
            is_dense=True,
        )
        return msg

    def publish_pointcloud(self):
        # 模拟一个室内场景点云（墙面 + 地板，共4000点）
        np.random.seed(42)

        # 地板
        floor = np.column_stack([
            np.random.uniform(-5, 5, 2000),
            np.random.uniform(-5, 5, 2000),
            np.random.normal(0, 0.02, 2000),
        ])
        # 前墙
        front_wall = np.column_stack([
            np.random.uniform(-5, 5, 1000),
            np.full(1000, 5.0) + np.random.normal(0, 0.02, 1000),
            np.random.uniform(0, 3, 1000),
        ])
        # 側墙
        side_wall = np.column_stack([
            np.full(1000, 5.0) + np.random.normal(0, 0.02, 1000),
            np.random.uniform(-5, 5, 1000),
            np.random.uniform(0, 3, 1000),
        ])

        points = np.vstack([floor, front_wall, side_wall])

        msg = self.create_pointcloud2(points)
        self.publisher_.publish(msg)
        self.get_logger().info(f'Published {len(points)} points to /pointcloud/raw')


def main(args=None):
    rclpy.init(args=args)
    node = PointCloudPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
