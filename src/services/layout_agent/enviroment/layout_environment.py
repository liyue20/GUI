
import numpy as np
from collections import namedtuple
from src.services.layout_agent.utils.initial_layout import layout_blocks
from src.services.layout_agent.utils.rasterization import RasterizedCard
from src.utils.logging import logging

Block = namedtuple('Block', ['id', 'content_type', 'content_length', 'min_width', 'min_height'])
logger = logging.getLogger('project_logger')

class LayoutEnvironment:
    def __init__(self, card_width, card_height, blocks):
        self.card_width = card_width
        self.card_height = card_height
        self.blocks = blocks
        self.card_area = card_width * card_height
        self.card = RasterizedCard(card_width, card_height)
    
    def reset(self):
        # 随机初始化布局，将所有块放置到卡片内
        self.positions = layout_blocks(self.blocks, self.card_width, self.card_height)
        self.initial_metrics = self.calculate_metrics(self.positions, self.card)
        self.initial_reward = self.calculate_initial_reward(self.initial_metrics)
        return self.get_state(), self.initial_reward
    
    def get_state(self):
        # 将当前布局状态转换为神经网络可接受的状态表示
        normalized_positions = self.positions / np.array([self.card_width, self.card_height, self.card_width, self.card_height])
        block_info = np.array([
            [block.content_length / max(self.card_width, self.card_height),
             block.min_width / self.card_width,
             block.min_height / self.card_height]
            for block in self.blocks
        ], dtype=np.float32)
        return np.concatenate([normalized_positions, block_info], axis=1)
    
    def step(self, block_selection, action_selection):
        # 保存执行动作前的状态用于比较
        old_positions = self.positions.copy()
        old_metrics = self.calculate_metrics(old_positions, self.card)
        # 根据动作修改对应block的位置或尺寸
        block_id = block_selection
        action_type = action_selection
        pos = self.positions[block_id]
        step_size = 2
        if action_type == 0:  # 左移block
            pos[0] = max(0, pos[0] - step_size)
        elif action_type == 1:  # 右移block
            pos[0] = min(self.card_width - pos[2], pos[0] + step_size)
        elif action_type == 2:  # 上移block
            pos[1] = max(0, pos[1] - step_size)
        elif action_type == 3:  # 下移block
            pos[1] = min(self.card_height - pos[3], pos[1] + step_size)
        elif action_type == 4:  # 增加block宽度
            pos[2] = min(self.card_width - pos[0], pos[2] + step_size)
        elif action_type == 5:  # 减小block宽度
            pos[2] = max(self.blocks[block_id].min_width, pos[2] - step_size)
        elif action_type == 6:  # 增加block高度
            pos[3] = min(self.card_height - pos[1], pos[3] + step_size)
        elif action_type == 7:  # 减小block高度
            pos[3] = max(self.blocks[block_id].min_height, pos[3] - step_size)
        # 计算新指标和奖励
        new_metrics = self.calculate_metrics(self.positions, self.card)
        reward = self.calculate_relative_reward(old_metrics, new_metrics)
        done = self.is_done(new_metrics)
        return self.get_state(), reward, done, {"metrics": new_metrics}
    
    def calculate_initial_reward(self, metrics):
        # 根据初始布局指标计算初始奖励
        reward = 0
        reward += 100 * (1 - metrics['overlap'])
        reward += 100 * (1 - metrics['out_of_bounds'])
        reward += 50 * metrics['size']
        reward += 50 * metrics['area_utilization']
        reward += 10 * (1 - abs(metrics['avg_gap'] - 5) / 5)
        reward += 50 * metrics['alignment']
        reward += 200 * metrics['semantic_order']
        return reward
    
    def calculate_relative_reward(self, old_metrics, new_metrics):
        # 计算相对于前一状态的奖励增量
        reward = 0
        reward += 100 * (new_metrics['overlap'] - old_metrics['overlap'])
        reward += 100 * (new_metrics['out_of_bounds'] - old_metrics['out_of_bounds'])
        reward += 50 * (new_metrics['size'] - old_metrics['size'])
        reward += 50 * (new_metrics['area_utilization'] - old_metrics['area_utilization'])
        reward += 10 * (abs(old_metrics['avg_gap'] - 5) - abs(new_metrics['avg_gap'] - 5))
        reward += 50 * (new_metrics['alignment'] - old_metrics['alignment'])
        reward += 200 * (new_metrics['semantic_order'] - old_metrics['semantic_order'])
        return reward
    
    def calculate_metrics(self, positions, raster_card):
        metrics = {}
        raster_card.reset_card()
        for i, block in enumerate(self.blocks):
            pos = positions[i]
            raster_card.add_block(block.id, pos[0], pos[1], pos[2], pos[3])
        metrics['overlap'] = raster_card.calculate_overlap_area() / self.card_area
        metrics['out_of_bounds'] = self.calculate_out_of_bounds(positions) / self.card_area
        metrics['size'] = self.calculate_size_metric(positions)
        metrics['area_utilization'] = raster_card.calculate_total_area() / self.card_area
        metrics['avg_gap'] = self.calculate_average_gap(positions)
        metrics['alignment'] = self.calculate_alignment(positions)
        metrics['semantic_order'] = self.calculate_semantic_order(positions)
        return metrics
    
    def calculate_alignment(self, positions, threshold=5):
        # 计算所有块之间的对齐得分
        alignment_score = 0
        total_checks = 0
        for i, pos1 in enumerate(positions):
            for j, pos2 in enumerate(positions[i+1:], i+1):
                total_checks += 4
                if abs(pos1[0] - pos2[0]) < threshold:
                    alignment_score += 1
                if abs((pos1[0] + pos1[2]) - (pos2[0] + pos2[2])) < threshold:
                    alignment_score += 1
                if abs(pos1[1] - pos2[1]) < threshold:
                    alignment_score += 1
                if abs((pos1[1] + pos1[3]) - (pos2[1] + pos2[3])) < threshold:
                    alignment_score += 1
        return alignment_score / total_checks if total_checks > 0 else 0
    
    def calculate_out_of_bounds(self, positions):
        # 计算块超出卡片边界的面积总和
        out_of_bounds_area = 0
        for pos in positions:
            out_of_bounds_x = max(0, pos[0] + pos[2] - self.card_width)
            out_of_bounds_y = max(0, pos[1] + pos[3] - self.card_height)
            out_of_bounds_area += out_of_bounds_x * pos[3] + out_of_bounds_y * pos[2]
        return out_of_bounds_area
    
    def calculate_size_metric(self, positions):
        # 计算布局尺寸利用率指标
        size_metric = 0
        for block, pos in zip(self.blocks, positions):
            size_metric += (pos[2] * pos[3]) / (block.min_width * block.min_height)
        return size_metric / len(self.blocks)
    
    def calculate_average_gap(self, positions):
        # 计算平均间隙指标（块之间的最小距离）
        total_gap = 0
        count = 0
        for i, pos1 in enumerate(positions):
            for j, pos2 in enumerate(positions[i+1:], i+1):
                gap_x = min(abs(pos1[0] - (pos2[0] + pos2[2])), abs(pos2[0] - (pos1[0] + pos1[2])))
                gap_y = min(abs(pos1[1] - (pos2[1] + pos2[3])), abs(pos2[1] - (pos1[1] + pos1[3])))
                total_gap += min(gap_x, gap_y)
                count += 1
        return total_gap / count if count > 0 else 0
    
    def calculate_semantic_order(self, positions):
        # 计算布局的语义顺序得分
        order_score = 0
        total_pairs = 0
        block_positions = [(block.id, pos[0], pos[1]) for block, pos in zip(self.blocks, positions)]
        for i in range(len(block_positions)):
            for j in range(i + 1, len(block_positions)):
                total_pairs += 1
                id1, x1, y1 = block_positions[i]
                id2, x2, y2 = block_positions[j]
                if id1 < id2:
                    if y1 + 20 < y2:
                        order_score += 1
                    elif abs(y1 - y2) <= 20:
                        if x1 < x2:
                            order_score += 1
        normalized_score = order_score / total_pairs if total_pairs > 0 else 0
        return normalized_score
    
    def is_done(self, metrics, prev_metrics=None, threshold=0.01, max_steps=1000, current_step=0):
        # 当布局质量达到阈值且改进幅度很小时，判定任务完成
        quality_threshold = 0.80
        reward_improvement = 0
        if prev_metrics:
            reward_improvement = abs(metrics['area_utilization'] - prev_metrics['area_utilization'])
        if current_step >= max_steps:
            return True
        done = (metrics['area_utilization'] > quality_threshold and
                metrics['overlap'] == 0 and
                metrics['out_of_bounds'] == 0 and
                metrics['alignment'] > 0.8 and
                metrics['semantic_order'] > 0.9 and
                reward_improvement < threshold)
        return done

class LayoutEnvironment_old:
    def __init__(self, card_width, card_height, blocks):
        self.card_width = card_width
        self.card_height = card_height
        self.blocks = blocks
        self.card_area = card_width * card_height
        self.card = RasterizedCard(card_width,card_height)
        
    
    def reset(self):
        self.positions = layout_blocks(self.blocks, self.card_width, self.card_height)
        self.initial_metrics = self.calculate_metrics(self.positions, self.card)
        self.initial_reward = self.calculate_initial_reward(self.initial_metrics)
        return self.get_state(), self.initial_reward
    
    def get_state(self):
        normalized_positions = self.positions / np.array([self.card_width, self.card_height, self.card_width, self.card_height])
        block_info = np.array([
            [block.content_length / max(self.card_width, self.card_height),
             block.min_width / self.card_width,
             block.min_height / self.card_height]
            for block in self.blocks
        ], dtype=np.float32)
        return np.concatenate([normalized_positions, block_info], axis=1)

    def step(self, block_selection, action_selection):
        old_positions = self.positions.copy()
        old_metrics = self.calculate_metrics(old_positions, self.card)

        block_id = block_selection
        action_type = action_selection
        pos = self.positions[block_id]
        
        step_size = 2
        if action_type == 0:  # move left
            pos[0] = max(0, pos[0] - step_size)
        elif action_type == 1:  # move right
            pos[0] = min(self.card_width - pos[2], pos[0] + step_size)
        elif action_type == 2:  # move up
            pos[1] = max(0, pos[1] - step_size)
        elif action_type == 3:  # move down
            pos[1] = min(self.card_height - pos[3], pos[1] + step_size)
        elif action_type == 4:  # expand width
            pos[2] = min(self.card_width - pos[0], pos[2] + step_size)
        elif action_type == 5:  # shrink width
            pos[2] = max(self.blocks[block_id].min_width, pos[2] - step_size)
        elif action_type == 6:  # expand height
            pos[3] = min(self.card_height - pos[1], pos[3] + step_size)
        elif action_type == 7:  # shrink height
            pos[3] = max(self.blocks[block_id].min_height, pos[3] - step_size)

        new_metrics = self.calculate_metrics(self.positions, self.card)
        reward = self.calculate_relative_reward(old_metrics, new_metrics)
        done = self.is_done(new_metrics)
        return self.get_state(), reward, done, {"metrics": new_metrics}
    
    def calculate_initial_reward(self, metrics):
        reward = 0
        reward += 100 * (1 - metrics['overlap'])
        reward += 100 * (1 - metrics['out_of_bounds'])
        reward += 50 * metrics['size']
        reward += 50 * metrics['area_utilization']
        reward += 10 * (1 - abs(metrics['avg_gap'] - 5) / 5)
        reward += 50 * metrics['alignment']
        reward += 200 * metrics['semantic_order']
        return reward
    
    def calculate_relative_reward(self, old_metrics, new_metrics):
        reward = 0
        reward += 100 * (new_metrics['overlap'] - old_metrics['overlap'])
        reward += 100 * (new_metrics['out_of_bounds'] - old_metrics['out_of_bounds'])
        reward += 50 * (new_metrics['size'] - old_metrics['size'])
        reward += 50 * (new_metrics['area_utilization'] - old_metrics['area_utilization'])
        reward += 10 * (abs(old_metrics['avg_gap'] - 5) - abs(new_metrics['avg_gap'] - 5))
        reward += 50 * (new_metrics['alignment'] - old_metrics['alignment'])
        reward += 200 * (new_metrics['semantic_order'] - old_metrics['semantic_order'])
        return reward
    
    def calculate_metrics(self, positions, raster_card):
        metrics = {}
        raster_card.reset_card()
        
        for i, block in enumerate(self.blocks):
            pos = positions[i]
            raster_card.add_block(block.id, pos[0], pos[1], pos[2], pos[3])
        
        metrics['overlap'] = raster_card.calculate_overlap_area() / self.card_area
        metrics['out_of_bounds'] = self.calculate_out_of_bounds(positions) / self.card_area
        metrics['size'] = self.calculate_size_metric(positions)
        metrics['area_utilization'] = raster_card.calculate_total_area() / self.card_area
        metrics['avg_gap'] = self.calculate_average_gap(positions)
        metrics['alignment'] = self.calculate_alignment(positions)
        metrics['semantic_order'] = self.calculate_semantic_order(positions)
        
        return metrics
    
    def calculate_alignment(self, positions, threshold=5):
        alignment_score = 0
        total_checks = 0
        for i, pos1 in enumerate(positions):
            for j, pos2 in enumerate(positions[i+1:], i+1):
                total_checks += 4  # 4 possible alignments per pair
                # 左边缘对齐
                if abs(pos1[0] - pos2[0]) < threshold:
                    alignment_score += 1
                # 右边缘对齐
                if abs((pos1[0] + pos1[2]) - (pos2[0] + pos2[2])) < threshold:
                    alignment_score += 1
                # 上边缘对齐
                if abs(pos1[1] - pos2[1]) < threshold:
                    alignment_score += 1
                # 下边缘对齐
                if abs((pos1[1] + pos1[3]) - (pos2[1] + pos2[3])) < threshold:
                    alignment_score += 1
        
        return alignment_score / total_checks if total_checks > 0 else 0
    
    def calculate_out_of_bounds(self, positions):
        out_of_bounds_area = 0
        for pos in positions:
            out_of_bounds_x = max(0, pos[0] + pos[2] - self.card_width)
            out_of_bounds_y = max(0, pos[1] + pos[3] - self.card_height)
            out_of_bounds_area += out_of_bounds_x * pos[3] + out_of_bounds_y * pos[2]
        return out_of_bounds_area
    
    def calculate_size_metric(self, positions):
        size_metric = 0
        for block, pos in zip(self.blocks, positions):
            size_metric += (pos[2] * pos[3]) / (block.min_width * block.min_height)
        return size_metric / len(self.blocks)
    
    def calculate_average_gap(self, positions):
        total_gap = 0
        count = 0
        for i, pos1 in enumerate(positions):
            for j, pos2 in enumerate(positions[i+1:], i+1):
                gap_x = min(abs(pos1[0] - (pos2[0] + pos2[2])), abs(pos2[0] - (pos1[0] + pos1[2])))
                gap_y = min(abs(pos1[1] - (pos2[1] + pos2[3])), abs(pos2[1] - (pos1[1] + pos1[3])))
                total_gap += min(gap_x, gap_y)
                count += 1
        return total_gap / count if count > 0 else 0
    
    def calculate_semantic_order(self, positions):
        """计算布局的语义顺序得分"""
        order_score = 0
        total_pairs = 0
        
        # 创建带ID的位置列表
        block_positions = [(block.id, pos[0], pos[1]) for block, pos in zip(self.blocks, positions)]
        
        # 比较每对块的位置关系
        for i in range(len(block_positions)):
            for j in range(i + 1, len(block_positions)):
                total_pairs += 1
                id1, x1, y1 = block_positions[i]
                id2, x2, y2 = block_positions[j]
                
                # 判断位置关系是否符合语义顺序
                if id1 < id2:  # 编号小的应该在前面（上方或左侧）
                    # 明显的垂直关系（考虑一定的容差）
                    if y1 + 20 < y2:  # 上下关系，较小编号在上方
                        order_score += 1
                    elif abs(y1 - y2) <= 20:  # 近似同一水平线
                        if x1 < x2:  # 左右关系，较小编号在左侧
                            order_score += 1
        
        # 归一化得分 (0-1范围)
        normalized_score = order_score / total_pairs if total_pairs > 0 else 0
        return normalized_score
    
    
    def is_done_old(self, metrics):
        # You can define your own termination condition
        # For example, if the layout reaches a certain quality threshold
        quality_threshold = 0.80
        return (metrics['area_utilization'] > quality_threshold and
                metrics['overlap'] == 0 and
                metrics['out_of_bounds'] == 0)
    def is_done(self, metrics, prev_metrics=None, threshold=0.01, max_steps=1000, current_step=0):
        """
        判断训练是否完成，基于多种指标和收敛性判定
        :param metrics: 当前布局的度量指标
        :param prev_metrics: 上一轮训练的度量指标
        :param threshold: 收敛条件的阈值，用于判断奖励的变化幅度是否足够小
        :param max_steps: 最大训练步数，防止训练时间过长
        :param current_step: 当前的训练步数
        :return: 是否满足训练完成条件
        """

        quality_threshold = 0.80  # 页面利用率阈值
        reward_improvement = 0

        if prev_metrics:
            # 比较当前和上一轮布局指标的变化幅度
            reward_improvement = abs(metrics['area_utilization'] - prev_metrics['area_utilization'])

        # 判断是否达到最大训练步数
        if current_step >= max_steps:
            return True

        # 综合判断多个指标
        done = (metrics['area_utilization'] > quality_threshold and  # 页面利用率大于阈值
                metrics['overlap'] == 0 and                         # 没有重叠
                metrics['out_of_bounds'] == 0 and                   # 没有超出边界
                metrics['alignment'] > 0.8 and                      # 对齐度要高于 0.8
                metrics['semantic_order'] > 0.9 and                 # 语义顺序要高于 0.9
                reward_improvement < threshold)                     # 奖励变化幅度小于设定阈值

        return done

