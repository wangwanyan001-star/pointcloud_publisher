import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header
import numpy as np

class PointCloudSubscriber(Node):
    def __init__(self):
        super().__init__('pointcloud_subscriber')
        # 订阅原始点云
        self.subscription = self.create_subscription(
            PointCloud2, '/pointcloud/raw', self.callback, 10)
        # 发布处理后的点云
        self.publisher_ = self.create_publisher(PointCloud2, '/pointcloud/filtered', 10)
        self.get_logger().info('PointCloud Subscriber started, listening to /pointcloud/raw')

    def pointcloud2_to_numpy(self, msg):
        """将 PointCloud2 消息解析为 numpy 数组"""
        points = np.frombuffer(msg.data, dtype=np.float32)
        points = points.reshape(-1, 3)
        return points

    def voxel_downsample(self, points, voxel_size=0.2):
        """体素降采样：将点云按格子分组，每格只保留一个点"""
        voxel_indices = np.floor(points / voxel_size).astype(int)
        _, unique_idx = np.unique(voxel_indices, axis=0, return_index=True)
        return points[unique_idx]

    def callback(self, msg):
        # 解析点云
        points = self.pointcloud2_to_numpy(msg)

        # 统计原始点云信息
        self.get_logger().info(f'Received {len(points)} points')
        self.get_logger().info(
            f'Z range: {points[:,2].min():.2f} ~ {points[:,2].max():.2f} m')

        # 体素降采样
        filtered = self.voxel_downsample(points, voxel_size=0.2)
        self.get_logger().info(
            f'After voxel downsample (0.2m): {len(filtered)} points '
            f'({len(filtered)/len(points)*100:.1f}% retained)')

        # 高度滤波：只保留 z > 0.1m 的点（去掉地板噪声）
        filtered = filtered[filtered[:, 2] > 0.1]
        self.get_logger().info(f'After height filter (z>0.1m): {len(filtered)} points')

        # 发布处理后的点云
        out_msg = self.numpy_to_pointcloud2(filtered, msg.header)
        self.publisher_.publish(out_msg)

    def numpy_to_pointcloud2(self, points, header):
        fields = [
            PointField(name='x', offset=0,  datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4,  datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8,  datatype=PointField.FLOAT32, count=1),
        ]
        return PointCloud2(
            header=header,
            height=1,
            width=len(points),
            fields=fields,
            is_bigendian=False,
            point_step=12,
            row_step=12 * len(points),
            data=points.astype(np.float32).tobytes(),
            is_dense=True,
        )


def main(args=None):
    rclpy.init(args=args)
    node = PointCloudSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
