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
        # Правильный порядок: Масштаб -> Вращение -> Перенос
        scale_mat = scaling_matrix(self.scale.x, self.scale.y, self.scale.z)
        rot_x = rotation_x_matrix(self.rotation.x)
        rot_y = rotation_y_matrix(self.rotation.y)
        rot_z = rotation_z_matrix(self.rotation.z)
        trans_mat = translation_matrix(self.position.x, self.position.y, self.position.z)
        
        # Комбинируем: сначала масштаб, затем вращение, затем перенос
        rotation_mat = composite_transformation(rot_z, rot_y, rot_x)
        transform_mat = composite_transformation(trans_mat, rotation_mat, scale_mat)
        
        return self.model.get_transformed_copy(transform_mat)

def create_scene_with_three_objects():
    """Создание сцены с тремя объектами"""
    print("\n" + "="*60)
    print("Z-БУФЕР: ДЕМОНСТРАЦИЯ АЛГОРИТМА УДАЛЕНИЯ НЕВИДИМЫХ ГРАНЕЙ")
    print("="*60)
    print("1. Куб (выпуклый) - красный")
    print("2. Ромб/октаэдр (выпуклый) - зеленый")
    print("3. Пирамида (невыпуклая) - синяя")
    print("\n=== УПРАВЛЕНИЕ ===")
    print("W: Каркас вкл/выкл")
    print("F: Заливка вкл/выкл (Z-буфер)")
    print("C: Отсечение граней вкл/выкл")
    print("O: Ортографическая проекция")
    print("I: Перспективная проекция")
    print("K: Вращение камеры вкл/выкл")
    print("P: Вращение объектов вкл/выкл")
    print("T: Тест перекрытия объектов (куб перед пирамидой)")
    print("U: Тест фигуры внутри фигуры (пирамида в кубе)")
    print("Y: Нормальная сцена")
    print("R: Сброс вращения")
    print("ESC: Выход")
    print("="*60 + "\n")
    
    # Три объекта с разным положением и вращением
    objects = [
        SceneObject(create_cube(), Point(-3, 0, 0), Point(30, 45, 0), Point(1, 1, 1), "Куб"),
        SceneObject(create_diamond(), Point(3, 0, 2), Point(0, 0, 0), Point(1.2, 1.2, 1.2), "Ромб"),
        SceneObject(create_pyramid(), Point(0, -2, 1), Point(0, 30, 0), Point(1, 1, 1), "Пирамида"),
    ]
    
    return objects

def create_scene_test_overlap():
    """Создание сцены для теста перекрытия Z-буфера"""
    print("\n" + "="*60)
    print("ТЕСТ ПЕРЕКРЫТИЯ Z-БУФЕРА")
    print("="*60)
    print("Куб (красный) должен полностью закрывать пирамиду (синюю)")
    print("Ромб (зеленый) должен быть частично виден")
    print("Если видна пирамида за кубом - Z-буфер работает некорректно")
    print("Нажмите Y для возврата к нормальной сцене")
    print("="*60 + "\n")
    
    # Располагаем объекты так, чтобы они перекрывались
    objects = [
        SceneObject(create_cube(), Point(0, 0, 2), Point(0, 30, 0), Point(2, 2, 2), "Куб"),
        SceneObject(create_diamond(), Point(3, 1, 4), Point(45, 0, 0), Point(1.5, 1.5, 1.5), "Ромб"),
        SceneObject(create_pyramid(), Point(0, 0, 6), Point(0, 0, 0), Point(1.5, 1.5, 1.5), "Пирамида"),
    ]
    
    return objects

def create_scene_figure_inside_figure():
    """Создание сцены: маленькая пирамида внутри большого куба"""
    print("\n" + "="*60)
    print("ТЕСТ: ФИГУРА ВНУТРИ ФИГУРЫ")
    print("="*60)
    print("Маленькая пирамида находится внутри большого куба")
    print("При включенном Z-буфере должна быть видна только внешняя поверхность куба")
    print("При выключенной заливке (каркас) видны обе фигуры")
    print("Нажмите Y для возврата к нормальной сцене")
    print("="*60 + "\n")
    
    # Большой куб и маленькая пирамида внутри него
    objects = [
        SceneObject(create_cube(), Point(0, 0, 0), Point(0, 0, 0), Point(3, 3, 3), "Большой куб"),
        SceneObject(create_pyramid(), Point(0, 0, 0), Point(0, 0, 0), Point(0.8, 0.8, 0.8), "Маленькая пирамида внутри"),
    ]
    
    return objects

def display_info(screen, show_wireframe, show_filled, backface_culling, 
                 projection_type, width, height, fps, camera_rotating, objects_rotating,
                 test_mode):
    """Отображение информации на экране"""
    font = pygame.font.Font(None, 28)
    small_font = pygame.font.Font(None, 22)
    
    # Левая панель - управление
    left_info = [
        "=== УПРАВЛЕНИЕ ===",
        f"Режим: {test_mode}",
        "",
        "W: Каркас вкл/выкл",
        "F: Заливка вкл/выкл",
        "C: Отсечение граней вкл/выкл",
        "O: Ортографическая проекция",
        "I: Перспективная проекция",
        "",
        "=== ВРАЩЕНИЕ ===",
        "K: Вращение камеры вкл/выкл",
        "P: Вращение объектов вкл/выкл",
        f"  Камера: {'ВКЛ' if camera_rotating else 'ВЫКЛ'}",
        f"  Объекты: {'ВКЛ' if objects_rotating else 'ВЫКЛ'}",
        "",
        "=== ТЕСТЫ ===",
        "T: Тест перекрытия (куб перед пирамидой)",
        "U: Тест фигуры внутри фигуры",
        "Y: Нормальная сцена",
        "R: Сброс вращения",
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
        f"Разрешение: {width}x{height}",
        f"Каркас: {'ВКЛ' if show_wireframe else 'ВЫКЛ'}",
        f"Заливка: {'ВКЛ' if show_filled else 'ВЫКЛ'}",
        f"Отсечение: {'ВКЛ' if backface_culling else 'ВЫКЛ'}",
        f"Проекция: {'ОРТО' if projection_type == 'orthographic' else 'ПЕРСП'}",
        "",
        "=== Z-БУФЕР ===",
        "Работа алгоритма:",
        "• Включите заливку (F)",
        "• Включите отсечение (C)",
        "• Используйте тест (T/U)",
        "• Наблюдайте перекрытие",
        "",
        "=== МОДЕЛИ ===",
        "• Куб: выпуклый, красный",
        "• Ромб: выпуклый, зеленый",
        "• Пирамида: невыпуклая, синяя",
        "",
        "=== ТЕСТ U ===",
        "Фигура внутри фигуры:",
        "• С заливкой: виден только куб",
        "• Без заливки: видны обе фигуры",
        "• Проверка работы Z-буфера",
    ]
    
    # Отображение левой панели
    y_pos = 10
    for i, text in enumerate(left_info):
        color = (220, 220, 220)
        
        if text.startswith("==="):
            color = (255, 200, 100)
            y_pos += 5
        elif "Режим:" in text:
            if test_mode == "ТЕСТ ПЕРЕКРЫТИЯ":
                color = (255, 100, 100)
            elif test_mode == "ФИГУРА ВНУТРИ ФИГУРЫ":
                color = (100, 255, 200)
            else:
                color = (100, 255, 100)
        elif "ВКЛ" in text:
            color = (100, 255, 100)
        elif "ВЫКЛ" in text:
            color = (255, 100, 100)
        elif "красный" in text.lower():
            color = (255, 100, 100)
        elif "зеленый" in text.lower():
            color = (100, 255, 100)
        elif "синяя" in text.lower():
            color = (100, 100, 255)
        elif "Z-БУФЕР" in text:
            color = (255, 220, 100)
        
        if text.startswith("==="):
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
        elif "ТЕСТ U" in text:
            color = (100, 255, 200)
        
        text_surface = small_font.render(text, True, color)
        screen.blit(text_surface, (width - 400, y_pos))
        y_pos += 24

def main():
    # Инициализация Pygame
    pygame.init()
    
    # Настройки окна
    WIDTH, HEIGHT = 1200, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Z-буфер: Алгоритм удаления невидимых граней")
    
    clock = pygame.time.Clock()
    
    # Создание рендерера
    renderer = Renderer(WIDTH, HEIGHT)
    
    # Создание камеры
    camera = Camera(
        position=Point(0, 5, 15),
        target=Point(0, 0, 0),
        up=Point(0, 1, 0),
        aspect_ratio=WIDTH/HEIGHT
    )
    
    # Устанавливаем перспективную проекцию по умолчанию
    camera.set_projection_type('perspective')
    
    # Создание начальной сцены
    scene_objects = create_scene_with_three_objects()
    current_test_mode = "НОРМАЛЬНАЯ СЦЕНА"
    
    # Параметры отображения
    show_wireframe = True
    show_filled = True
    backface_culling = True
    
    # Флаги вращения
    camera_rotating = False
    objects_rotating = True
    
    # Флаги для ручного вращения
    manual_rotation_active = False
    
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
        
        # Обновление камеры
        if camera_rotating:
            camera.update()
        
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
                    print("Проекция: ОРТОГРАФИЧЕСКАЯ")
                
                elif event.key == pygame.K_i:
                    camera.set_projection_type('perspective')
                    print("Проекция: ПЕРСПЕКТИВНАЯ")
                
                # Сброс вращения
                elif event.key == pygame.K_r:
                    for obj in scene_objects:
                        obj.rotation = Point(0, 0, 0)
                    print("Вращение объектов сброшено")
                
                # Тест перекрытия (T)
                elif event.key == pygame.K_t:
                    scene_objects = create_scene_test_overlap()
                    current_test_mode = "ТЕСТ ПЕРЕКРЫТИЯ"
                    objects_rotating = False  # Выключаем вращение для теста
                    print("Тест перекрытия активирован")
                
                # Тест фигуры внутри фигуры (U)
                elif event.key == pygame.K_u:
                    scene_objects = create_scene_figure_inside_figure()
                    current_test_mode = "ФИГУРА ВНУТРИ ФИГУРЫ"
                    objects_rotating = False  # Выключаем вращение для теста
                    print("Тест 'Фигура внутри фигуры' активирован")
                
                # Нормальная сцена (Y)
                elif event.key == pygame.K_y:
                    scene_objects = create_scene_with_three_objects()
                    current_test_mode = "НОРМАЛЬНАЯ СЦЕНА"
                    objects_rotating = True  # Включаем вращение обратно
                    print("Нормальная сцена восстановлена")
                
                # Управление вращением камеры
                elif event.key == pygame.K_k:
                    camera_rotating = not camera_rotating
                    if camera_rotating:
                        camera.start_rotation()
                    else:
                        camera.stop_rotation()
                    print(f"Вращение камеры: {'ВКЛ' if camera_rotating else 'ВЫКЛ'}")
                
                # Управление вращением объектов
                elif event.key == pygame.K_p:
                    # В тестовых режимах не включаем вращение
                    if current_test_mode == "НОРМАЛЬНАЯ СЦЕНА":
                        objects_rotating = not objects_rotating
                        print(f"Вращение объектов: {'ВКЛ' if objects_rotating else 'ВЫКЛ'}")
                    else:
                        print("Вращение объектов отключено в тестовых режимах. Вернитесь в нормальную сцену (Y)")
                
                # Ручное вращение объектов - только в нормальном режиме
                elif event.key in [pygame.K_q, pygame.K_e, pygame.K_a, pygame.K_d, pygame.K_z, pygame.K_x]:
                    if current_test_mode == "НОРМАЛЬНАЯ СЦЕНА":
                        manual_rotation_active = True
                        rotation_amount = 5
                        
                        if event.key == pygame.K_q:
                            scene_objects[0].rotation.y -= rotation_amount
                        elif event.key == pygame.K_e:
                            scene_objects[0].rotation.y += rotation_amount
                        elif event.key == pygame.K_a:
                            scene_objects[1].rotation.x -= rotation_amount
                        elif event.key == pygame.K_d:
                            scene_objects[1].rotation.x += rotation_amount
                        elif event.key == pygame.K_z:
                            scene_objects[2].rotation.z -= rotation_amount
                        elif event.key == pygame.K_x:
                            scene_objects[2].rotation.z += rotation_amount
                    else:
                        print("Ручное вращение доступно только в нормальном режиме. Нажмите Y")
            
            elif event.type == pygame.KEYUP:
                # При отпускании клавиш ручного вращения
                if event.key in [pygame.K_q, pygame.K_e, pygame.K_a, pygame.K_d, pygame.K_z, pygame.K_x]:
                    manual_rotation_active = False
        
        # Обработка непрерывных клавиш для вращения объектов
        keys = pygame.key.get_pressed()
        rotation_speed = 0.5
        
        # Автоматическое вращение объектов если включено и в нормальном режиме
        if objects_rotating and not manual_rotation_active and current_test_mode == "НОРМАЛЬНАЯ СЦЕНА":
            scene_objects[0].rotation.y += rotation_speed
            scene_objects[1].rotation.x += rotation_speed * 0.7
            scene_objects[2].rotation.y += rotation_speed * 0.8
        
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
                    camera.projection_type, WIDTH, HEIGHT, fps, 
                    camera_rotating, objects_rotating, current_test_mode)
        
        # Отображение подсказки для текущего теста
        font = pygame.font.Font(None, 36)
        hint_text = ""
        
        if not show_filled and current_test_mode == "ФИГУРА ВНУТРИ ФИГУРЫ":
            hint_text = "Нажмите F для включения Z-буфера (должен быть виден только куб)"
            color = (255, 255, 100)
        elif not show_filled:
            hint_text = "Нажмите F для включения Z-буфера (заливки)"
            color = (255, 255, 100)
        elif current_test_mode == "ФИГУРА ВНУТРИ ФИГУРЫ" and show_filled:
            hint_text = "Z-буфер активен: видна только внешняя поверхность куба"
            color = (100, 255, 100)
        elif current_test_mode == "ТЕСТ ПЕРЕКРЫТИЯ" and show_filled:
            hint_text = "Z-буфер активен: куб должен закрывать пирамиду"
            color = (100, 255, 100)
        
        if hint_text:
            text_surface = font.render(hint_text, True, color)
            text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(text_surface, text_rect)
        
        # Отображение названия текущего теста вверху
        if current_test_mode != "НОРМАЛЬНАЯ СЦЕНА":
            title_font = pygame.font.Font(None, 48)
            if current_test_mode == "ТЕСТ ПЕРЕКРЫТИЯ":
                title_color = (255, 100, 100)
            else:
                title_color = (100, 255, 200)
            
            title_surface = title_font.render(current_test_mode, True, title_color)
            title_rect = title_surface.get_rect(center=(WIDTH//2, 40))
            screen.blit(title_surface, title_rect)
        
        # Обновление экрана
        pygame.display.flip()
        
        # Ограничение FPS
        clock.tick(60)
    
    # Завершение
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()