import numpy as np

class RasterizedCard:
    def __init__(self, width, height, scale=10):
        self.scale = scale
        self.width = width * scale
        self.height = height * scale
        self.reset_card()

    def reset_card(self):
        self.mask = np.zeros((self.height, self.width), dtype=np.int8)

    def add_block(self, block_id, x, y, width, height):
        x1, y1 = int(x * self.scale), int(y * self.scale)
        x2, y2 = int((x + width) * self.scale), int((y + height) * self.scale)
        self.mask[y1:y2, x1:x2] += 1

    def calculate_overlap_area(self):
        return np.sum(self.mask > 1) / (self.scale ** 2)
    
    def calculate_left_right_areas(self):
        middle = self.width // 2
        left_area = np.sum(self.mask[:, :middle] > 0)
        right_area = np.sum(self.mask[:, middle:] > 0)
        left_area /= (self.scale ** 2)
        right_area /= (self.scale ** 2)
        return left_area, right_area

    def calculate_symmetry(self):
        left_area, right_area = self.calculate_left_right_areas()
        total_area = np.sum(self.mask > 0) / (self.scale ** 2)
        area_symmetry_diff = abs(left_area - right_area)
        symmetry_score = 1 - (area_symmetry_diff / total_area)
        return symmetry_score

    def calculate_total_area(self):
        return np.sum(self.mask > 0) / (self.scale ** 2)