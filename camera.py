# camera.py
import numpy as np
from point import Point
from transformations import *

class Camera:
    def __init__(self, position, target, up, aspect_ratio, near=0.1, far=100.0):
        self.position = position  # Point
        self.target = target      # Point
        self.up = up              # Point
        self.aspect_ratio = aspect_ratio
        self.near = near
        self.far = far
        
        self.update_view_matrix()
        self.update_projection_matrix()
    
    def update_view_matrix(self):
        """Вычисление матрицы вида"""
        # Вектор направления взгляда
        forward = Point(
            self.target.x - self.position.x,
            self.target.y - self.position.y,
            self.target.z - self.position.z
        )
        
        # Нормализация
        forward_arr = forward.to_array()
        forward_len = np.linalg.norm(forward_arr)
        if forward_len == 0:
            forward_arr = np.array([0, 0, -1])  # Направление по умолчанию
        else:
            forward_arr = forward_arr / forward_len
        
        # Вектор вправо
        up_arr = self.up.to_array()
        right_arr = np.cross(forward_arr, up_arr)
        right_len = np.linalg.norm(right_arr)
        if right_len == 0:
            right_arr = np.array([1, 0, 0])  # Направление по умолчанию
        else:
            right_arr = right_arr / right_len
        
        # Обновленный вектор вверх
        up_arr = np.cross(right_arr, forward_arr)
        up_len = np.linalg.norm(up_arr)
        if up_len == 0:
            up_arr = np.array([0, 1, 0])  # Направление по умолчанию
        else:
            up_arr = up_arr / up_len
        
        # Матрица вида
        pos_arr = self.position.to_array()
        
        self.view_matrix = np.array([
            [right_arr[0], right_arr[1], right_arr[2], -np.dot(right_arr, pos_arr)],
            [up_arr[0], up_arr[1], up_arr[2], -np.dot(up_arr, pos_arr)],
            [-forward_arr[0], -forward_arr[1], -forward_arr[2], np.dot(forward_arr, pos_arr)],
            [0, 0, 0, 1]
        ], dtype=float)
    
    def update_projection_matrix(self):
        """Вычисление матрицы ортографической проекции"""
        # Ортографическая проекция (параллельная)
        # Масштаб подбирается так, чтобы объекты были хорошо видны
        scale = 0.3  # Уменьшенный масштаб для лучшей видимости
        
        self.projection_matrix = np.array([
            [scale / self.aspect_ratio, 0, 0, 0],
            [0, scale, 0, 0],
            [0, 0, -2/(self.far - self.near), -(self.far + self.near)/(self.far - self.near)],
            [0, 0, 0, 1]
        ], dtype=float)
    
    def get_view_projection_matrix(self):
        """Получение комбинированной матрицы вида и проекции"""
        self.update_view_matrix()
        return self.projection_matrix @ self.view_matrix