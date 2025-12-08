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
        
        # Цвета для разных граней
        self.colors = [
            (200, 100, 100),  # красный
            (100, 200, 100),  # зеленый
            (100, 100, 200),  # синий
            (200, 200, 100),  # желтый
            (200, 100, 200),  # фиолетовый
            (100, 200, 200),  # бирюзовый
        ]
    
    def project_point(self, point, view_proj_matrix):
        """Проецирование 3D точки в 2D координаты экрана"""
        homogeneous = point.to_homogeneous()
        transformed = view_proj_matrix @ homogeneous
        x = transformed[0] * self.half_width + self.half_width
        y = -transformed[1] * self.half_height + self.half_height
        return (x, y)
    
    def is_face_visible(self, face, vertices, camera_position, camera_target):
        """Проверка видимости грани (правильный алгоритм отсечения)"""
        if face.normal is None or len(face.vertex_indices) < 3:
            return True
        
        # 1. Вычисляем направление взгляда камеры (вектор от камеры к цели)
        view_direction = Point(
            camera_target.x - camera_position.x,
            camera_target.y - camera_position.y,
            camera_target.z - camera_position.z
        )
        
        # Нормализуем вектор направления взгляда
        view_len = np.sqrt(view_direction.x**2 + view_direction.y**2 + view_direction.z**2)
        if view_len > 0:
            view_direction.x /= view_len
            view_direction.y /= view_len
            view_direction.z /= view_len
        
        # 2. Для ортографической проекции проверяем угол между нормалью и направлением взгляда
        # Грань видима, если нормаль направлена от камеры (угол > 90°)
        
        # Скалярное произведение нормали и направления взгляда
        dot_product = (
            face.normal.x * view_direction.x +
            face.normal.y * view_direction.y +
            face.normal.z * view_direction.z
        )
        
        # DEBUG: Выводим информацию для первой грани
        if face == vertices[0].faces[0] if hasattr(vertices[0], 'faces') else False:
            print(f"Normal: ({face.normal.x:.2f}, {face.normal.y:.2f}, {face.normal.z:.2f})")
            print(f"View dir: ({view_direction.x:.2f}, {view_direction.y:.2f}, {view_direction.z:.2f})")
            print(f"Dot product: {dot_product:.2f}")
            print(f"Visible: {dot_product < 0}")
        
        # Грань видима если dot_product < 0 (угол > 90°)
        return dot_product < 0
    
    def calculate_face_color(self, face, color_idx, vertices, camera_position, camera_target):
        """Вычисление цвета грани с учетом направления камеры"""
        base_color = self.colors[color_idx % len(self.colors)]
        
        if face.normal is None:
            return base_color
        
        # Направление от камеры к цели
        view_direction = Point(
            camera_target.x - camera_position.x,
            camera_target.y - camera_position.y,
            camera_target.z - camera_position.z
        )
        
        # Нормализуем
        view_len = np.sqrt(view_direction.x**2 + view_direction.y**2 + view_direction.z**2)
        if view_len > 0:
            view_direction.x /= view_len
            view_direction.y /= view_len
            view_direction.z /= view_len
        
        # Скалярное произведение для освещения
        dot = (
            face.normal.x * view_direction.x +
            face.normal.y * view_direction.y +
            face.normal.z * view_direction.z
        )
        
        # Интенсивность: видимые грани ярче, невидимые - темнее
        if dot < 0:  # Грань видима
            intensity = max(0.6, 0.8 - abs(dot) * 0.3)
        else:  # Грань невидима (если отсечение выключено)
            intensity = max(0.2, 0.4 - dot * 0.2)
        
        return (
            min(255, int(base_color[0] * intensity)),
            min(255, int(base_color[1] * intensity)),
            min(255, int(base_color[2] * intensity))
        )
    
    def render(self, screen, model, camera, show_wireframe=True, 
               show_filled=True, backface_culling=True, show_normals=False):
        """Рендеринг модели на экран"""
        view_proj_matrix = camera.get_view_projection_matrix()
        
        # Проецирование всех вершин
        projected_vertices = []
        for vertex in model.vertices:
            projected = self.project_point(vertex, view_proj_matrix)
            projected_vertices.append(projected)
        
        visible_faces = 0
        hidden_faces = 0
        
        # Сортируем грани по глубине для правильного отображения (простейший вариант)
        # Создаем список граней с их средней глубиной
        faces_with_depth = []
        for i, face in enumerate(model.faces):
            # Вычисляем среднюю Z-координату грани
            avg_z = 0
            count = 0
            for idx in face.vertex_indices:
                if idx < len(model.vertices):
                    avg_z += model.vertices[idx].z
                    count += 1
            if count > 0:
                avg_z /= count
                faces_with_depth.append((avg_z, i, face))
        
        # Сортируем по глубине (дальние рисуем первыми)
        faces_with_depth.sort(reverse=True)  # reverse=True: дальние -> ближние
        
        # Рендеринг граней от дальних к ближним
        for depth, i, face in faces_with_depth:
            # Отсечение нелицевых граней
            if backface_culling:
                is_visible = self.is_face_visible(face, model.vertices, camera.position, camera.target)
                if not is_visible:
                    hidden_faces += 1
                    continue
            
            visible_faces += 1
            
            # Координаты вершин грани
            face_points = []
            for idx in face.vertex_indices:
                if 0 <= idx < len(projected_vertices):
                    face_points.append(projected_vertices[idx])
            
            if len(face_points) < 3:
                continue
            
            # Заполненная грань
            if show_filled:
                color = self.calculate_face_color(face, i, model.vertices, camera.position, camera.target)
                pygame.draw.polygon(screen, color, face_points)
            
            # Каркас
            if show_wireframe:
                pygame.draw.polygon(screen, (255, 255, 255), face_points, 1)
            
            # Визуализация нормалей
            if show_normals and face.normal and len(face_points) >= 3:
                # Центр грани на экране
                center_x = sum(p[0] for p in face_points) / len(face_points)
                center_y = sum(p[1] for p in face_points) / len(face_points)
                
                # Нормаль на экране (масштабированная)
                scale = 30
                normal_end_x = center_x + face.normal.x * scale
                normal_end_y = center_y - face.normal.y * scale  # минус, т.к. ось Y вниз
                
                # Рисуем нормаль
                pygame.draw.line(screen, (255, 255, 0), 
                               (center_x, center_y), 
                               (normal_end_x, normal_end_y), 2)
                
                # Направление взгляда камеры (синяя стрелка)
                view_direction = Point(
                    camera.target.x - camera.position.x,
                    camera.target.y - camera.position.y,
                    camera.target.z - camera.position.z
                )
                view_len = np.sqrt(view_direction.x**2 + view_direction.y**2 + view_direction.z**2)
                if view_len > 0:
                    view_direction.x /= view_len
                    view_direction.y /= view_len
                    view_direction.z /= view_len
                    
                    view_end_x = center_x + view_direction.x * scale
                    view_end_y = center_y - view_direction.y * scale
                    
                    pygame.draw.line(screen, (100, 200, 255),
                                   (center_x, center_y),
                                   (view_end_x, view_end_y), 1)
        
        # Статистика
        font = pygame.font.Font(None, 24)
        stats_text = f"Visible: {visible_faces}, Hidden: {hidden_faces}, Total: {len(model.faces)}"
        stats_surface = font.render(stats_text, True, (200, 255, 200))
        screen.blit(stats_surface, (10, self.height - 30))
        
        # Отображение угла для отладки
        if len(model.faces) > 0 and model.faces[0].normal:
            normal = model.faces[0].normal
            view_direction = Point(
                camera.target.x - camera.position.x,
                camera.target.y - camera.position.y,
                camera.target.z - camera.position.z
            )
            view_len = np.sqrt(view_direction.x**2 + view_direction.y**2 + view_direction.z**2)
            if view_len > 0:
                view_direction.x /= view_len
                view_direction.y /= view_len
                view_direction.z /= view_len
                
                dot = (normal.x * view_direction.x + 
                      normal.y * view_direction.y + 
                      normal.z * view_direction.z)
                
                angle = np.degrees(np.arccos(max(-1, min(1, dot))))
                angle_text = f"Angle: {angle:.1f}°"
                angle_surface = font.render(angle_text, True, (255, 200, 100))
                screen.blit(angle_surface, (10, self.height - 60))