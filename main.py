# main.py
import numpy as np
import pygame
import sys
from model_loader import create_cube, create_diamond, create_pyramid
from renderer import Renderer
from camera import Camera
from transformations import *
from point import Point

class SceneObject:
    def __init__(self, model, position=None, rotation=None, scale=None, name="Объект"):
        self.model = model
        self.position = position or Point(0, 0, 0)
        self.rotation = rotation or Point(0, 0, 0)
        self.scale = scale or Point(1, 1, 1)
        self.name = name
    
    def get_transformed_model(self):
        """Получение преобразованной копии модели"""
        # Создаем матрицу преобразования
        scale_mat = scaling_matrix(self.scale.x, self.scale.y, self.scale.z)
        rot_x = rotation_x_matrix(self.rotation.x)
        rot_y = rotation_y_matrix(self.rotation.y)
        rot_z = rotation_z_matrix(self.rotation.z)
        trans_mat = translation_matrix(self.position.x, self.position.y, self.position.z)
        
        # Комбинируем: масштаб -> вращение -> перенос
        rotation_mat = composite_transformation(rot_z, rot_y, rot_x)
        transform_mat = composite_transformation(trans_mat, rotation_mat, scale_mat)
        
        return self.model.get_transformed_copy(transform_mat)

def create_scene_with_three_objects():
    """Создание сцены с тремя объектами"""
    print("\n" + "="*50)
    print("СЦЕНА С ТРЕМЯ ОБЪЕКТАМИ")
    print("="*50)
    print("1. Куб (выпуклый) - красный")
    print("2. Ромб/октаэдр (выпуклый) - зеленый")
    print("3. Пирамида (невыпуклая) - синяя")
    print("="*50 + "\n")
    
    # Три объекта с разным положением и вращением
    objects = [
        SceneObject(create_cube(), Point(-3, 0, 0), Point(30, 45, 0), Point(1, 1, 1), "Куб"),
        SceneObject(create_diamond(), Point(3, 0, 2), Point(0, 0, 0), Point(1.2, 1.2, 1.2), "Ромб"),
        SceneObject(create_pyramid(), Point(0, -2, 1), Point(0, 30, 0), Point(1, 1, 1), "Пирамида"),
    ]
    
    return objects

def display_info(screen, show_wireframe, show_filled, backface_culling, 
                 projection_type, width, height, fps):
    """Отображение информации на экране"""
    font = pygame.font.Font(None, 28)
    small_font = pygame.font.Font(None, 22)
    
    # Левая панель - управление
    left_info = [
        "=== УПРАВЛЕНИЕ ===",
        "W: Каркас вкл/выкл",
        "F: Заливка вкл/выкл (Z-буфер)",
        "C: Отсечение граней вкл/выкл",
        "O: Ортографическая проекция",
        "I: Перспективная проекция",
        "T: Тест перекрытия объектов",
        "R: Сброс сцены",
        "",
        "=== ВРАЩЕНИЕ ОБЪЕКТОВ ===",
        "Куб (красный):",
        "  Q - вращение по оси Y-",
        "  E - вращение по оси Y+",
        "",
        "Ромб (зеленый):",
        "  A - вращение по оси X-",
        "  D - вращение по оси X+",
        "",
        "Пирамида (синяя):",
        "  Z - вращение по оси Z-",
        "  X - вращение по оси Z+",
        "",
        "ESC: Выход",
    ]
    
    # Правая панель - статус
    right_info = [
        "=== СТАТУС ===",
        f"FPS: {fps}",
        f"Каркас: {'ВКЛ' if show_wireframe else 'ВЫКЛ'}",
        f"Заливка: {'ВКЛ' if show_filled else 'ВЫКЛ'}",
        f"Отсечение: {'ВКЛ' if backface_culling else 'ВЫКЛ'}",
        f"Проекция: {'ОРТОГРАФИЧЕСКАЯ' if projection_type == 'orthographic' else 'ПЕРСПЕКТИВНАЯ'}",
        "",
        "=== МОДЕЛИ ===",
        "• Куб: выпуклый, красный",
        "• Ромб: выпуклый, зеленый",
        "• Пирамида: невыпуклая, синяя",
        "",
        "=== Z-БУФЕР ===",
        "Работа алгоритма:",
        "• Включите заливку (F)",
        "• Включите отсечение (C)",
        "• Используйте тест (T)",
        "• Наблюдайте перекрытие",
    ]
    
    # Отображение левой панели
    y_pos = 10
    for i, text in enumerate(left_info):
        color = (220, 220, 220)
        if text.startswith("==="):
            color = (255, 200, 100)
            y_pos += 5
        elif "Z-буфер" in text:
            color = (100, 255, 200)
        elif "ВКЛ" in text:
            color = (100, 255, 100)
        elif "ВЫКЛ" in text:
            color = (255, 100, 100)
        elif "красный" in text:
            color = (255, 100, 100)
        elif "зеленый" in text:
            color = (100, 255, 100)
        elif "синяя" in text:
            color = (100, 100, 255)
        
        # Выбираем шрифт в зависимости от типа текста
        if text.startswith("===") or "ВКЛ" in text or "ВЫКЛ" in text:
            text_surface = font.render(text, True, color)
            screen.blit(text_surface, (10, y_pos))
            y_pos += 30
        else:
            text_surface = small_font.render(text, True, color)
            screen.blit(text_surface, (10, y_pos))
            y_pos += 24
    
    # Отображение правой панели
    y_pos = 10
    for i, text in enumerate(right_info):
        color = (200, 230, 255)
        if text.startswith("==="):
            color = (255, 220, 100)
            y_pos += 5
        elif "✓" in text:
            color = (100, 255, 100)
        elif "ВКЛ" in text:
            color = (100, 255, 100)
        elif "ВЫКЛ" in text:
            color = (255, 100, 100)
        elif "красный" in text:
            color = (255, 100, 100)
        elif "зеленый" in text:
            color = (100, 255, 100)
        elif "синяя" in text:
            color = (100, 100, 255)
        
        text_surface = small_font.render(text, True, color)
        screen.blit(text_surface, (width - 350, y_pos))
        y_pos += 24

def main():
    # Инициализация Pygame
    pygame.init()
    
    # Настройки окна
    WIDTH, HEIGHT = 1200, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Z-буфер: Демонстрация работы алгоритма")
    
    clock = pygame.time.Clock()
    
    # Создание рендерера
    renderer = Renderer(WIDTH, HEIGHT)
    
    # Создание камеры
    camera = Camera(
        position=Point(0, 0, 0),
        target=Point(0, 0, -1),
        up=Point(0, 1, 0),
        aspect_ratio=WIDTH/HEIGHT
    )
    
    # Создание сцены с тремя объектами
    scene_objects = create_scene_with_three_objects()
    
    # Параметры отображения
    show_wireframe = True
    show_filled = True  # Включаем заливку по умолчанию
    backface_culling = True
    
    # Переменные для FPS
    fps = 60
    last_time = pygame.time.get_ticks()
    frame_count = 0
    
    # Основной цикл
    running = True
    while running:
        # Расчет FPS
        current_time = pygame.time.get_ticks()
        frame_count += 1
        if current_time - last_time > 1000:
            fps = frame_count
            frame_count = 0
            last_time = current_time
        
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                # Выход
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                # Управление отображением
                elif event.key == pygame.K_w:
                    show_wireframe = not show_wireframe
                    print(f"Каркас: {'ВКЛ' if show_wireframe else 'ВЫКЛ'}")
                
                elif event.key == pygame.K_f:
                    show_filled = not show_filled
                    print(f"Заливка (Z-буфер): {'ВКЛ' if show_filled else 'ВЫКЛ'}")
                
                elif event.key == pygame.K_c:
                    backface_culling = not backface_culling
                    print(f"Отсечение граней: {'ВКЛ' if backface_culling else 'ВЫКЛ'}")
                
                # Переключение проекций
                elif event.key == pygame.K_o:
                    camera.set_projection_type('orthographic')
                    print("Проекция: ОРТОГРАФИЧЕСКАЯ (параллельная)")
                
                elif event.key == pygame.K_i:
                    camera.set_projection_type('perspective')
                    print("Проекция: ПЕРСПЕКТИВНАЯ")
                
                # Сброс
                elif event.key == pygame.K_r:
                    scene_objects = create_scene_with_three_objects()
                    print("Сцена сброшена")
                
                # Тест перекрытия
                elif event.key == pygame.K_t:
                    # Располагаем объекты так, чтобы они перекрывались
                    scene_objects[0].position = Point(-1.5, 0, 0)   # Куб слева
                    scene_objects[1].position = Point(1.5, 0, 2)    # Ромб справа (дальше)
                    scene_objects[2].position = Point(0, 0, 4)      # Пирамида в центре (самая дальняя)
                    print("\n=== ТЕСТ ПЕРЕКРЫТИЯ ОБЪЕКТОВ ===")
                    print("Объекты расположены на разной глубине:")
                    print("• Куб: Z = 0 (ближе всех)")
                    print("• Ромб: Z = 2 (дальше)")
                    print("• Пирамида: Z = 4 (самая дальняя)")
                    print("\nВключите заливку (F) для наблюдения работы Z-буфера")
                    print("Вращайте объекты, чтобы увидеть перекрытие со всех сторон")
        
        # Обработка непрерывных клавиш для вращения
        keys = pygame.key.get_pressed()
        rotation_speed = 2.0
        
        # Куб - Q/E (вращение по оси Y)
        if keys[pygame.K_q]:
            scene_objects[0].rotation.y -= rotation_speed
        if keys[pygame.K_e]:
            scene_objects[0].rotation.y += rotation_speed
        
        # Ромб - A/D (вращение по оси X)
        if keys[pygame.K_a]:
            scene_objects[1].rotation.x -= rotation_speed
        if keys[pygame.K_d]:
            scene_objects[1].rotation.x += rotation_speed
        
        # Пирамида - Z/X (вращение по оси Z)
        if keys[pygame.K_z]:
            scene_objects[2].rotation.z -= rotation_speed
        if keys[pygame.K_x]:
            scene_objects[2].rotation.z += rotation_speed
        
        # Автоматическое вращение если нет ручного управления
        if not any(keys[k] for k in [pygame.K_q, pygame.K_e, pygame.K_a, pygame.K_d, pygame.K_z, pygame.K_x]):
            scene_objects[0].rotation.y += 0.5  # Куб вращается по Y
            scene_objects[1].rotation.x += 0.3  # Ромб вращается по X
            scene_objects[2].rotation.y += 0.4  # Пирамида вращается по Y
        
        # Очистка экрана
        screen.fill((30, 30, 40))
        
        # Получаем преобразованные модели
        transformed_models = [obj.get_transformed_model() for obj in scene_objects]
        
        # Рендеринг всех объектов
        renderer.render(
            screen=screen,
            models=transformed_models,
            camera=camera,
            show_wireframe=show_wireframe,
            show_filled=show_filled,
            backface_culling=backface_culling
        )
        
        # Отображение информации
        display_info(screen, show_wireframe, show_filled, backface_culling,
                    camera.projection_type, WIDTH, HEIGHT, fps)
        
        # Обновление экрана
        pygame.display.flip()
        
        # Ограничение FPS
        clock.tick(60)

    # Завершение
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()