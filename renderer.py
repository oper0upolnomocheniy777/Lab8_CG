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
        
        # Z-буфер с правильной инициализацией
        self.z_buffer = np.full((height, width), float('inf'), dtype=np.float32)
        
        # Цвета для моделей
        self.colors = [
            (255, 100, 100, 255),  # Красный - куб (добавлен альфа-канал)
            (100, 255, 100, 255),  # Зеленый - ромб
            (100, 100, 255, 255),  # Синий - пирамида
        ]
        
        self.bg_color = (30, 30, 40, 255)
        
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
        z = transformed[2]  # Глубина после проекции
        
        return (int(x), int(y), z)
    
    def rasterize_triangle(self, v0, v1, v2, color):
        """Улучшенная растеризация треугольника с интерполяцией Z"""
        x0, y0, z0 = v0
        x1, y1, z1 = v1
        x2, y2, z2 = v2
        
        # Находим ограничивающий прямоугольник
        min_x = max(0, int(min(x0, x1, x2)))
        max_x = min(self.width - 1, int(max(x0, x1, x2)))
        min_y = max(0, int(min(y0, y1, y2)))
        max_y = min(self.height - 1, int(max(y0, y1, y2)))
        
        if min_x >= max_x or min_y >= max_y:
            return
        
        # Вычисляем векторы ребер
        edge1 = (x1 - x0, y1 - y0)
        edge2 = (x2 - x0, y2 - y0)
        
        # Площадь треугольника (для барицентрических координат)
        area = edge1[0] * edge2[1] - edge1[1] * edge2[0]
        if abs(area) < 1e-6:
            return
        
        inv_area = 1.0 / area
        
        # Получаем поверхность для рисования
        screen = pygame.display.get_surface()
        
        # Растеризация каждого пикселя
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                # Вектор от вершины v0 до текущей точки
                v = (x - x0, y - y0)
                
                # Вычисляем барицентрические координаты
                u = (v[0] * edge2[1] - v[1] * edge2[0]) * inv_area
                v_coord = (edge1[0] * v[1] - edge1[1] * v[0]) * inv_area
                w = 1 - u - v_coord
                
                # Проверка внутри треугольника (с небольшим допуском)
                if u >= -0.001 and v_coord >= -0.001 and w >= -0.001:
                    # Интерполяция Z-координаты
                    z = w * z0 + u * z1 + v_coord * z2
                    
                    # Проверка Z-буфера
                    if z < self.z_buffer[y, x]:
                        self.z_buffer[y, x] = z
                        self.stats['pixels_drawn'] += 1
                        
                        # Рисуем пиксель
                        screen.set_at((x, y), color[:3])
    
    def render(self, screen, models, camera, show_wireframe=True, 
               show_filled=True, backface_culling=True):
        """Основной метод рендеринга"""
        # Очистка экрана и буферов
        screen.fill(self.bg_color[:3])
        self.clear_buffers()
        
        # Получаем матрицу вида-проекции
        view_proj_matrix = camera.get_view_projection_matrix()
        
        # Собираем все треугольники для рендеринга
        all_triangles = []
        
        # Подготовка данных для всех моделей
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
                
                # Отсечение нелицевых граней (backface culling)
                if backface_culling and face.normal:
                    # Вычисляем вектор направления от камеры к грани
                    face_center = Point(0, 0, 0)
                    for idx in face.vertex_indices[:3]:  # Берем первые 3 вершины
                        face_center.x += model.vertices[idx].x
                        face_center.y += model.vertices[idx].y
                        face_center.z += model.vertices[idx].z
                    
                    if len(face.vertex_indices) > 0:
                        face_center.x /= min(3, len(face.vertex_indices))
                        face_center.y /= min(3, len(face.vertex_indices))
                        face_center.z /= min(3, len(face.vertex_indices))
                    
                    # Вектор от камеры к грани
                    view_dir = Point(
                        face_center.x - camera.position.x,
                        face_center.y - camera.position.y,
                        face_center.z - camera.position.z
                    )
                    
                    # Если нормаль смотрит от камеры, отсекаем
                    dot_product = (face.normal.x * view_dir.x + 
                                 face.normal.y * view_dir.y + 
                                 face.normal.z * view_dir.z)
                    
                    if dot_product > 0:
                        continue
                
                # Разбиваем на треугольники
                indices = face.vertex_indices
                triangles = []
                
                if len(indices) == 3:
                    triangles.append((indices, model_idx))
                elif len(indices) == 4:
                    triangles.append(([indices[0], indices[1], indices[2]], model_idx))
                    triangles.append(([indices[0], indices[2], indices[3]], model_idx))
                
                # Добавляем треугольники в общий список
                for tri_indices, model_idx_ref in triangles:
                    if len(tri_indices) != 3:
                        continue
                    
                    v0 = projected[tri_indices[0]]
                    v1 = projected[tri_indices[1]]
                    v2 = projected[tri_indices[2]]
                    
                    # Проверяем, что треугольник видим
                    if (v0[0] < 0 and v1[0] < 0 and v2[0] < 0) or \
                       (v0[0] > self.width and v1[0] > self.width and v2[0] > self.width) or \
                       (v0[1] < 0 and v1[1] < 0 and v2[1] < 0) or \
                       (v0[1] > self.height and v1[1] > self.height and v2[1] > self.height):
                        continue
                    
                    all_triangles.append((v0, v1, v2, model_idx_ref))
        
        # Сортируем треугольники по средней Z-координате (простейшая сортировка)
        all_triangles.sort(key=lambda t: (t[0][2] + t[1][2] + t[2][2]) / 3, reverse=True)
        
        # Рендеринг треугольников (от дальних к ближним)
        for v0, v1, v2, model_idx in all_triangles:
            color = self.colors[model_idx % len(self.colors)]
            
            # Заливка
            if show_filled:
                self.rasterize_triangle(v0, v1, v2, color)
            
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
            f"Z-буфер: {self.width}x{self.height}",
            f"Граней: {self.stats['faces_processed']}",
            f"Пикселей: {self.stats['pixels_drawn']}",
        ]
        
        for i, text in enumerate(stats_text):
            text_surface = font.render(text, True, (200, 255, 200))
            screen.blit(text_surface, (10, self.height - 80 + i * 25))