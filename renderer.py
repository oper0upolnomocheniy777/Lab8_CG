# renderer.py
import numpy as np
import pygame
from point import Point

class Renderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.half_width = width / 2
        self.half_height = height / 2
        
        # Z-буфер
        self.z_buffer = np.full((height, width), float('inf'), dtype=np.float32)
        
        # Цвета для моделей
        self.colors = [
            (255, 100, 100),  # Красный - куб
            (100, 255, 100),  # Зеленый - сфера
            (100, 100, 255),  # Синий - пирамида
        ]
        
        self.bg_color = (30, 30, 40)
        
        # Статистика
        self.stats = {
            'faces_processed': 0,
            'pixels_drawn': 0,
        }
    
    def clear_buffers(self):
        """Очистка буферов"""
        self.z_buffer.fill(float('inf'))
        self.stats = {'faces_processed': 0, 'pixels_drawn': 0}
    
    def project_point(self, point, view_proj_matrix):
        """Проецирование 3D точки в 2D координаты экрана"""
        homogeneous = point.to_homogeneous()
        transformed = view_proj_matrix @ homogeneous
        
        # Перспективное деление
        if transformed[3] != 0:
            transformed = transformed / transformed[3]
        
        # Преобразование в координаты экрана
        x = transformed[0] * self.half_width + self.half_width
        y = -transformed[1] * self.half_height + self.half_height
        z = transformed[2]
        
        return (int(x), int(y), z)
    
    def rasterize_triangle_simple(self, v0, v1, v2, color):
        """Упрощенная растеризация треугольника"""
        x0, y0, z0 = v0
        x1, y1, z1 = v1
        x2, y2, z2 = v2
        
        # Находим ограничивающий прямоугольник
        min_x = max(0, min(x0, x1, x2))
        max_x = min(self.width - 1, max(x0, x1, x2))
        min_y = max(0, min(y0, y1, y2))
        max_y = min(self.height - 1, max(y0, y1, y2))
        
        if min_x >= max_x or min_y >= max_y:
            return
        
        # Предварительные вычисления для барицентрических координат
        area = (y1 - y2)*(x0 - x2) + (x2 - x1)*(y0 - y2)
        if abs(area) < 1e-6:
            return
        
        inv_area = 1.0 / area
        
        # Растеризация с шагом для производительности
        step = 2  # Рисуем каждый 2-й пиксель для скорости
        
        for y in range(min_y, max_y + 1, step):
            for x in range(min_x, max_x + 1, step):
                # Барицентрические координаты
                w1 = ((y1 - y2)*(x - x2) + (x2 - x1)*(y - y2)) * inv_area
                w2 = ((y2 - y0)*(x - x2) + (x0 - x2)*(y - y2)) * inv_area
                w0 = 1 - w1 - w2
                
                # Проверка внутри треугольника
                if w0 >= -0.001 and w1 >= -0.001 and w2 >= -0.001:
                    # Интерполяция Z
                    z = w0 * z0 + w1 * z1 + w2 * z2
                    
                    # Проверка Z-буфера
                    if z < self.z_buffer[y, x]:
                        self.z_buffer[y, x] = z
                        self.stats['pixels_drawn'] += 1
                        # Рисуем пиксель
                        pygame.draw.rect(pygame.display.get_surface(), color, 
                                        (x, y, step, step))
    
    def render(self, screen, models, camera, show_wireframe=True, 
               show_filled=True, backface_culling=True):
        """Основной метод рендеринга"""
        # Очистка экрана
        screen.fill(self.bg_color)
        
        # Очистка статистики
        self.clear_buffers()
        
        # Получаем матрицу вида-проекции
        view_proj_matrix = camera.get_view_projection_matrix()
        
        # Рендерим модели в порядке их индекса
        for model_idx, model in enumerate(models):
            color = self.colors[model_idx % len(self.colors)]
            
            # Проецируем все вершины
            projected = []
            for vertex in model.vertices:
                proj = self.project_point(vertex, view_proj_matrix)
                projected.append(proj)
            
            # Обработка каждой грани
            for face in model.faces:
                self.stats['faces_processed'] += 1
                
                # Отсечение нелицевых граней
                if backface_culling and face.normal:
                    # Для ортографической проекции
                    if face.normal.z < 0:
                        continue
                
                # Разбиваем на треугольники
                indices = face.vertex_indices
                triangles = []
                
                if len(indices) == 3:
                    triangles.append(indices)
                elif len(indices) == 4:
                    triangles.append([indices[0], indices[1], indices[2]])
                    triangles.append([indices[0], indices[2], indices[3]])
                
                # Рендеринг треугольников
                for tri in triangles:
                    if len(tri) != 3:
                        continue
                    
                    v0 = projected[tri[0]]
                    v1 = projected[tri[1]]
                    v2 = projected[tri[2]]
                    
                    # Заливка
                    if show_filled:
                        self.rasterize_triangle_simple(v0, v1, v2, color)
                    
                    # Каркас
                    if show_wireframe:
                        pygame.draw.line(screen, (255, 255, 255),
                                       (v0[0], v0[1]), (v1[0], v1[1]), 1)
                        pygame.draw.line(screen, (255, 255, 255),
                                       (v1[0], v1[1]), (v2[0], v2[1]), 1)
                        pygame.draw.line(screen, (255, 255, 255),
                                       (v2[0], v2[1]), (v0[0], v0[1]), 1)
        
        # Отображение статистики
        self.display_stats(screen)
    
    def display_stats(self, screen):
        """Отображение статистики"""
        font = pygame.font.Font(None, 24)
        
        stats_text = [
            f"Граней обработано: {self.stats['faces_processed']}",
            f"Пикселей залито: {self.stats['pixels_drawn']}",
            f"Разрешение: {self.width}x{self.height}",
        ]
        
        for i, text in enumerate(stats_text):
            text_surface = font.render(text, True, (200, 255, 200))
            screen.blit(text_surface, (10, self.height - 80 + i * 25))