# 方案设计

目标：

- [ ] 实现基本与Osmos相同的2D模拟环境（暂不考虑帧率和高性能计算；设计比较良好的程序结构，用Python+PyGame实现基本逻辑）
- [ ] 通过 使用PyGame精灵组/使用其他更专业2D游戏引擎/使用Java或C++实现游戏逻辑，来实现流畅的模拟
- [ ] 用Python进行AI编程，实现输入游戏画面（一到多帧输入）、输出决策结果的较强的游戏智能体（很可能采用DQN或者PG（策略梯度）等RL算法，可能使用DDPG（深度确定性策略梯度）；在Open AI的Spinning Up学习之后）



## Inbox

- pygame绘图只能绘制整坐标，导致动画很不流畅。需要寻找其他2D绘图库达成更好的效果！

## 作用力分类

- 直接接触：星体吸收时，大的星体受到合并进来的物质影响，而小的星体不受作用力。太阳系或本轮模式下太阳不受直接接触力，需要标注星体是否受直接接触力。
- 引力：只存在于**太阳-太阳**（似乎Osmos中有特殊处理，尚不明确！）/太阳-普通星体/太阳-排斥体（未定义！）之间。因为引力是相互的，太阳在对外施加引力时自身也会有反作用力。但是太阳系或本轮模式下太阳不受引力，需要标注星体是否受引力。
- （暂不考虑）斥力：仅存在于**排斥体-排斥体**（Osmos中对排斥体间的相互作用，包括合并都有特殊处理，排斥体之间的力倾向于吸引力，尚不明确！）/排斥体-普通星体/排斥体-太阳（未定义！）之间。