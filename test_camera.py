from camera import Camera
from point import Point

camera = Camera(
    position=Point(0, 0, 10),
    target=Point(0, 0, 0),
    up=Point(0, 1, 0),
    aspect_ratio=1.0
)

print(f"Начальное состояние: {camera.is_rotating}")

# Тест 1: Включение
camera.toggle_rotation()
print(f"После toggle: {camera.is_rotating}")

# Тест 2: Выключение
camera.toggle_rotation()
print(f"После второго toggle: {camera.is_rotating}")

# Тест 3: Проверка update_rotation
print("\nПроверка update_rotation:")
print(f"До: позиция=({camera.position.x}, {camera.position.z})")
camera.update_rotation()
print(f"После (is_rotating=False): позиция=({camera.position.x}, {camera.position.z})")

camera.is_rotating = True
print(f"До: позиция=({camera.position.x}, {camera.position.z})")
camera.update_rotation()
print(f"После (is_rotating=True): позиция=({camera.position.x}, {camera.position.z})")