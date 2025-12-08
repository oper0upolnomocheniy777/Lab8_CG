# main.py (добавляем отладочную информацию)
import numpy as np
import pygame
import sys
from model_loader import load_obj
from renderer import Renderer
from camera import Camera
from transformations import *

def main():
    # Инициализация Pygame
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Миша мишенька медведь научи меня пердеть")
    clock = pygame.time.Clock()
    
    # Загрузка модели
    try:
        model = load_obj("models/cube.obj")
    except FileNotFoundError:
        print("Model files not found. Creating default cube...")
        model = load_obj("default_cube")
    
    # Создание камеры
    camera = Camera(
        position=Point(0, 0, 10),
        target=Point(0, 0, 0),
        up=Point(0, 1, 0),
        aspect_ratio=WIDTH/HEIGHT
    )
    
    # Создание рендерера
    renderer = Renderer(WIDTH, HEIGHT)
    
    # Параметры вращения
    angle_x = 0
    angle_y = 0
    rotation_speed = 1.0  # Увеличил скорость вращения для тестирования
    
    # Настройки отображения
    show_wireframe = True
    show_filled = True
    backface_culling = True
    show_normals = False
    
    # Отладочная информация
    debug_mode = False
    
    # Основной цикл
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    show_wireframe = not show_wireframe
                elif event.key == pygame.K_f:
                    show_filled = not show_filled
                elif event.key == pygame.K_c:
                    backface_culling = not backface_culling
                    print(f"Back-face culling: {'ON' if backface_culling else 'OFF'}")
                elif event.key == pygame.K_n:
                    show_normals = not show_normals
                    print(f"Normals visualization: {'ON' if show_normals else 'OFF'}")
                elif event.key == pygame.K_1:
                    try:
                        model = load_obj("models/cube.obj")
                        print("Loaded cube")
                    except:
                        print("cube.obj not found, creating default cube")
                        model = load_obj("default_cube")
                elif event.key == pygame.K_2:
                    try:
                        model = load_obj("models/sphere.obj")
                        print("Loaded sphere")
                    except:
                        print("sphere.obj not found, loading cube instead")
                        model = load_obj("default_cube")
                elif event.key == pygame.K_UP:
                    camera.position.y += 0.5
                    camera.target.y += 0.5
                elif event.key == pygame.K_DOWN:
                    camera.position.y -= 0.5
                    camera.target.y -= 0.5
                elif event.key == pygame.K_LEFT:
                    camera.position.x -= 0.5
                    camera.target.x -= 0.5
                elif event.key == pygame.K_RIGHT:
                    camera.position.x += 0.5
                    camera.target.x += 0.5
                elif event.key == pygame.K_r:
                    angle_x = angle_y = 0
                    camera.position = Point(0, 0, 10)
                    camera.target = Point(0, 0, 0)
                    print("Reset rotation and camera")
                elif event.key == pygame.K_s:
                    shear_matrix = shearing_matrix(0.2, 0.1, 0, 0, 0, 0)
                    model.apply_transform(shear_matrix)
                    print("Applied shearing transformation")
                elif event.key == pygame.K_v:
                    debug_mode = not debug_mode
                    print(f"Debug mode: {'ON' if debug_mode else 'OFF'}")
                elif event.key == pygame.K_SPACE:
                    # Вывод информации о нормалях
                    print("\n=== Face Normals ===")
                    for i, face in enumerate(model.faces[:6]):  # Первые 6 граней
                        if face.normal:
                            print(f"Face {i}: normal = ({face.normal.x:.2f}, {face.normal.y:.2f}, {face.normal.z:.2f})")
        
        # Обработка непрерывных клавиш
        keys = pygame.key.get_pressed()
        
        # Вращение объекта
        if keys[pygame.K_a]:
            angle_y -= rotation_speed
        if keys[pygame.K_d]:
            angle_y += rotation_speed
        if keys[pygame.K_z]:
            angle_x -= rotation_speed
        if keys[pygame.K_x]:
            angle_x += rotation_speed
        
        # Приближение/отдаление (Q/E)
        if keys[pygame.K_q]:
            direction = Point(
                camera.target.x - camera.position.x,
                camera.target.y - camera.position.y,
                camera.target.z - camera.position.z
            )
            length = np.sqrt(direction.x**2 + direction.y**2 + direction.z**2)
            if length > 0:
                move_distance = 0.5
                camera.position.x += (direction.x / length) * move_distance
                camera.position.y += (direction.y / length) * move_distance
                camera.position.z += (direction.z / length) * move_distance
        
        if keys[pygame.K_e]:
            direction = Point(
                camera.target.x - camera.position.x,
                camera.target.y - camera.position.y,
                camera.target.z - camera.position.z
            )
            length = np.sqrt(direction.x**2 + direction.y**2 + direction.z**2)
            if length > 0:
                move_distance = 0.5
                camera.position.x -= (direction.x / length) * move_distance
                camera.position.y -= (direction.y / length) * move_distance
                camera.position.z -= (direction.z / length) * move_distance
        
        # Создание матрицы вращения
        rot_x = rotation_x_matrix(angle_x)
        rot_y = rotation_y_matrix(angle_y)
        rotation = composite_transformation(rot_y, rot_x)
        
        # Применение преобразований к модели
        model_transformed = model.copy()
        model_transformed.apply_transform(rotation)
        
        # Очистка экрана
        screen.fill((30, 30, 40))
        
        # Рендеринг модели
        renderer.render(
            screen=screen,
            model=model_transformed,
            camera=camera,
            show_wireframe=show_wireframe,
            show_filled=show_filled,
            backface_culling=backface_culling,
            show_normals=show_normals
        )
        
        # Отображение информации
        font = pygame.font.Font(None, 24)
        info = [
            f"W: Wireframe ({'ON' if show_wireframe else 'OFF'})",
            f"F: Filled ({'ON' if show_filled else 'OFF'})",
            f"C: Back-face culling ({'ON' if backface_culling else 'OFF'})",
            f"N: Show normals ({'ON' if show_normals else 'OFF'})",
            f"1/2: Load cube/sphere",
            f"Arrows: Move camera",
            f"A/D/Z/X: Rotate object (HOLD)",
            f"R: Reset",
            f"Projection: ORTHOGRAPHIC",
        ]
        
        for i, text in enumerate(info):
            text_surface = font.render(text, True, (200, 200, 200))
            screen.blit(text_surface, (10, 10 + i * 25))
        
        # Отображение углов вращения
        rotation_info = f"Rotation X: {angle_x:.1f}°, Y: {angle_y:.1f}°"
        rotation_surface = font.render(rotation_info, True, (255, 255, 100))
        screen.blit(rotation_surface, (WIDTH - 250, 10))
        
        # Отображение направления камеры
        direction = Point(
            camera.target.x - camera.position.x,
            camera.target.y - camera.position.y,
            camera.target.z - camera.position.z
        )
        length = np.sqrt(direction.x**2 + direction.y**2 + direction.z**2)
        if length > 0:
            direction.x /= length
            direction.y /= length
            direction.z /= length
            
            cam_dir_info = f"View dir: ({direction.x:.2f}, {direction.y:.2f}, {direction.z:.2f})"
            cam_dir_surface = font.render(cam_dir_info, True, (100, 255, 255))
            screen.blit(cam_dir_surface, (WIDTH - 250, 35))
        
        # Обновление экрана
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()