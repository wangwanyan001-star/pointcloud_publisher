# ROS2 Point Cloud Publisher & Subscriber

基于 ROS2 Humble 实现的点云数据发布与处理 pipeline，演示 ROS2 核心通信机制（Node / Topic / Publisher / Subscriber）在点云场景下的应用。

## 节点架构

```
PointCloudPublisher
    ↓ /pointcloud/raw (sensor_msgs/PointCloud2, 1Hz)
PointCloudSubscriber
    ↓ 体素降采样 (voxel_size=0.2m) + 高度滤波 (z>0.1m)
    ↓ /pointcloud/filtered (sensor_msgs/PointCloud2)
```

## 功能说明

**publisher_node.py**
- 模拟室内场景点云（地板 + 前墙 + 侧墙，共4000点）
- 以 1Hz 频率发布到 `/pointcloud/raw`
- 消息类型：`sensor_msgs/PointCloud2`，坐标系 `map`

**subscriber_node.py**
- 订阅 `/pointcloud/raw`，实时处理点云
- 体素降采样（0.2m）：4000点 → ~3111点（保留77.8