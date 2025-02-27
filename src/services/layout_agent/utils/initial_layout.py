import random
from collections import namedtuple
import math

Block = namedtuple('Block', ['id', 'content_type', 'content_length', 'min_width', 'min_height'])

class PreciseLayoutManager:
    def __init__(self, card_width, card_height):
        self.card_width = card_width
        self.card_height = card_height
        self.positions = []
        self.spacing_factor = 1.05
        self._block_size_ratio = 0.95

    def layout_blocks(self, blocks):
        sorted_blocks = sorted(blocks, key=lambda b: b.content_length)
        is_row_based = True
        # is_row_based = random.choice([True, False])
        if(len(blocks) <= 1): 
            initial_random_number = 1
        else:
            initial_random_number = random.randint(1, len(blocks) - 1)
            
        layout = self.find_valid_layout(sorted_blocks, is_row_based, initial_random_number)
        
        if layout:
            self.apply_layout(layout, sorted_blocks, is_row_based, layout)
        else:
            self.apply_fallback_layout(sorted_blocks, is_row_based, initial_random_number)
        
        return self.positions

    def find_valid_layout(self, blocks, is_row_based, initial_random_number):
        is_out_card = False
        blocks_per_group = initial_random_number
        total_dimension = 0 
        for i in range(len(blocks)):
            if is_out_card: 
                blocks_per_group -= 1
                is_out_card = False
            if total_dimension >self.card_width:
                blocks_per_group += 1
                total_dimension = 0

            if blocks_per_group >len(blocks):
                return None
            
            num_groups = math.ceil(len(blocks) / blocks_per_group)
            
            for group in range(num_groups):
                start = group * blocks_per_group
                end = min((group + 1) * blocks_per_group, len(blocks))
                group_blocks = blocks[start:end]
                
                if is_row_based:
                    group_dimension = max(block.min_height for block in group_blocks)
                    sum_blocks_width = sum(block.min_width for block in group_blocks)
                    if sum_blocks_width > self.card_width:
                        is_out_card = True
                        break
                else:
                    group_dimension = max(block.min_width for block in group_blocks)
                    sum_blocks_height = sum(block.min_height for block in group_blocks)
                    if sum_blocks_height > self.card_width:
                        is_out_card = True
                        break
                
                total_dimension += group_dimension * self.spacing_factor
            
            if is_row_based and total_dimension <= self.card_height and is_out_card == False:
                return blocks_per_group
            elif not is_row_based and total_dimension <= self.card_width and is_out_card == False:
                return blocks_per_group
        
        return None
    
    def center_layout_horizontally(self, remain, is_row_based):
        if remain > 0:
            offset = remain / 2
            if is_row_based:
                for i, position in enumerate(self.positions):
                    if position:
                        self.positions[i] = [position[0], position[1] + offset, position[2], position[3]]
            else:
                for i, position in enumerate(self.positions):
                    if position:
                        self.positions[i] = [position[0] + offset, position[1], position[2], position[3]]

    def apply_layout(self, blocks_per_group, blocks, is_row_based, initial_random_number):
        num_groups = math.ceil(len(blocks) / blocks_per_group)
        self.positions = [None] * len(blocks)
        sum_height = 0
        sum_width = 0
        for group in range(num_groups):
            start = group * blocks_per_group
            end = min((group + 1) * blocks_per_group, len(blocks))
            group_blocks = blocks[start:end]
            act_len = len(group_blocks)
            number_regions = min(act_len, initial_random_number)
            if is_row_based:
                row_height = max(block.min_height for block in group_blocks) * self.spacing_factor
                x = 0
                for block in group_blocks:
                    region_width = self.card_width / number_regions
                    current_x = (region_width - region_width * self._block_size_ratio)/2 + x
                    current_y = (row_height - row_height * self._block_size_ratio)/2 +sum_height
                    self.positions[block.id] = [current_x, current_y, region_width * self._block_size_ratio, row_height * self._block_size_ratio]
                    x += region_width
                sum_height += row_height
            else:
                column_width = max(block.min_width for block in group_blocks) * self.spacing_factor
                y = 0
                for block in group_blocks:
                    region_height = self.card_height / number_regions
                    current_x = (column_width - column_width * self._block_size_ratio)/2 +sum_width
                    current_y = (region_height - region_height * self._block_size_ratio)/2 + y
                    self.positions[block.id] = [current_x, current_y, column_width * self._block_size_ratio, region_height *self._block_size_ratio]
                    y += region_height
                sum_width +=column_width

        if is_row_based:
            remain = self.card_height - sum_height
            self.center_layout_horizontally(remain, True)
        else :
            remain = self.card_width - sum_width
            self.center_layout_horizontally(remain, False)

    def apply_fallback_layout(self, blocks, is_row_based, initial_random_number):
        num_groups = math.ceil(len(blocks) / initial_random_number)
        self.positions = [None] * len(blocks)
        
        if is_row_based:
            row_height = self.card_height / num_groups
            for i, block in enumerate(blocks):
                row = i // initial_random_number
                col = i % initial_random_number
                x = (col / initial_random_number) * self.card_width
                y = row * row_height
                current_x = x + ((self.card_width / initial_random_number) * (1 - self._block_size_ratio))/2
                current_y = y + (row_height * (1 - self._block_size_ratio))/2
                width = (self.card_width / initial_random_number) * self._block_size_ratio
                height = row_height * self._block_size_ratio
                self.positions[block.id] = [current_x, current_y, width, height]
        else:
            column_width = self.card_width / num_groups
            for i, block in enumerate(blocks):
                col = i // initial_random_number
                row = i % initial_random_number
                x = col * column_width
                y = (row / initial_random_number) * self.card_height
                current_x = x + (column_width * (1 - self._block_size_ratio))/2
                current_y = y + ((self.card_height / initial_random_number) * (1 - self._block_size_ratio))/2
                width = column_width * self._block_size_ratio
                height = (self.card_height / initial_random_number) * self._block_size_ratio
                self.positions[block.id] = [current_x, current_y, width, height]
        
        # Merge remaining areas for the last block if necessary
        if len(blocks) < num_groups * initial_random_number:
            last_block = blocks[-1]
            last_position = self.positions[last_block.id]
            if is_row_based:
                last_position[0] -= ((self.card_width / initial_random_number) * (1 - self._block_size_ratio))/2
                last_position[2] = (self.card_width - last_position[0]) * self._block_size_ratio
                last_position[0] += ((self.card_width - last_position[0])* (1 - self._block_size_ratio))/2
            else:
                last_position[1] -= ((self.card_height / initial_random_number) * (1 - self._block_size_ratio))/2
                last_position[3] = (self.card_height - last_position[1]) * self._block_size_ratio
                last_position[1] += ((self.card_height - last_position[1]) *(1 - self._block_size_ratio))/2

def layout_blocks(blocks, card_width, card_height):
    layout_manager = PreciseLayoutManager(card_width, card_height)
    return layout_manager.layout_blocks(blocks)
