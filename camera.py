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
        
        # Новые поля для вращения камеры
        self.rotation_angle = 0.0
        self.rotation_speed = 0.0
        self.is_rotating = False
        self.rotation_radius = 15.0  # Радиус вращения
        self.center_point = Point(0, 0, 0)  # Точка вокруг которой вращается камера
    
    def set_projection_type(self, proj_type):
        self.projection_type = proj_type
        print(f"Установлена проекция: {proj_type}")
    
    def start_rotation(self):
        """Начать вращение камеры"""
        self.is_rotating = True
        self.rotation_speed = 0.5  # Скорость вращения в градусах за кадр
        print("Камера начала вращение вокруг сцены")
    
    def stop_rotation(self):
        """Остановить вращение камеры"""
        self.is_rotating = False
        self.rotation_speed = 0.0
        print("Камера остановила вращение")
    
    def toggle_rotation(self):
        """Переключить вращение камеры"""
        if self.is_rotating:
            self.stop_rotation()
        else:
            self.start_rotation()
    
    def update(self):
        """Обновление позиции камеры (вызывать каждый кадр)"""
        if self.is_rotating:
            self.rotation_angle += self.rotation_speed
            
            # Вычисляем новую позицию на круговой траектории
            angle_rad = np.radians(self.rotation_angle)
            
            # Вращаемся вокруг центра сцены
            x = self.center_point.x + self.rotation_radius * np.cos(angle_rad)
            z = self.center_point.z + self.rotation_radius * np.sin(angle_rad)
            y = self.center_point.y + 3.0  # Немного приподнимаем камеру
            
            self.position = Point(x, y, z)
            
            # Всегда смотрим на центр сцены
            self.target = self.center_point
    
    def get_view_matrix(self):
        """Матрица вида (lookAt)"""
        # Упрощенная реализация lookAt
        forward = np.array([
            self.target.x - self.position.x,
            self.target.y - self.position.y,
            self.target.z - self.position.z
        ])
        forward = forward / np.linalg.norm(forward)
        
        up = np.array([self.up.x, self.up.y, self.up.z])
        up = up / np.linalg.norm(up)
        
        right = np.cross(forward, up)
        right = right / np.linalg.norm(right)
        
        up = np.cross(right, forward)
        
        view_matrix = np.array([
            [right[0], right[1], right[2], -np.dot(right, [self.position.x, self.position.y, self.position.z])],
            [up[0], up[1], up[2], -np.dot(up, [self.position.x, self.position.y, self.position.z])],
            [-forward[0], -forward[1], -forward[2], np.dot(forward, [self.position.x, self.position.y, self.position.z])],
            [0, 0, 0, 1]
        ], dtype=float)
        
        return view_matrix
    
    def get_view_projection_matrix(self):
        """Матрица вида-проекции"""
        view_matrix = self.get_view_matrix()
        
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
            # Ортографическая проекция
            scale = 0.1
            proj_matrix = np.array([
                [scale / self.aspect_ratio, 0, 0, 0],
                [0, scale, 0, 0],
                [0, 0, -2/(self.far - self.near), -(self.far + self.near)/(self.far - self.near)],
                [0, 0, 0, 1]
            ], dtype=float)
        
        return proj_matrix @ view_matrix