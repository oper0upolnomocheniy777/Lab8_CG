# camera.py
import numpy as np
from point import Point

class Camera:
    def __init__(self, position, target, up, aspect_ratio, near=0.1, far=100.0):
        self.position = position
        self.target = target
        self.up = up
        self.aspect_ratio = aspect_ratio
        self.near = near
        self.far = far
        self.projection_type = 'orthographic'
        self.fov = 60
    
    def set_projection_type(self, proj_type):
        self.projection_type = proj_type
        print(f"Установлена проекция: {proj_type}")
    
    def get_view_projection_matrix(self):
        """Матрица вида-проекции"""
        # Упрощенная матрица вида
        view_matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=float)
        
        # Матрица проекции в зависимости от типа
        if self.projection_type == 'perspective':
            # Перспективная проекция
            f = 1.0 / np.tan(np.radians(self.fov) / 2)
            proj_matrix = np.array([
                [f / self.aspect_ratio, 0, 0, 0],
                [0, f, 0, 0],
                [0, 0, (self.far + self.near) / (self.near - self.far), 
                 (2 * self.far * self.near) / (self.near - self.far)],
                [0, 0, -1, 0]
            ], dtype=float)
        else:
            # Ортографическая проекция (параллельная)
            scale = 0.1
            proj_matrix = np.array([
                [scale / self.aspect_ratio, 0, 0, 0],
                [0, scale, 0, 0],
                [0, 0, -2/(self.far - self.near), -(self.far + self.near)/(self.far - self.near)],
                [0, 0, 0, 1]
            ], dtype=float)
        
        # Перенос объектов в центр и отодвигаем
        translate = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, -10],  # Отодвигаем по Z
            [0, 0, 0, 1]
        ], dtype=float)
        
        return proj_matrix @ view_matrix @ translate