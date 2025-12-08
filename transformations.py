# transformations.py
import numpy as np
from point import Point

def identity_matrix():
    """Единичная матрица"""
    return np.eye(4, dtype=float)

def translation_matrix(dx, dy, dz):
    """Матрица переноса"""
    return np.array([
        [1, 0, 0, dx],
        [0, 1, 0, dy],
        [0, 0, 1, dz],
        [0, 0, 0, 1]
    ], dtype=float)

def scaling_matrix(sx, sy, sz):
    """Матрица масштабирования"""
    return np.array([
        [sx, 0, 0, 0],
        [0, sy, 0, 0],
        [0, 0, sz, 0],
        [0, 0, 0, 1]
    ], dtype=float)

def rotation_x_matrix(angle_degrees):
    """Матрица вращения вокруг оси X"""
    angle = np.radians(angle_degrees)
    cos_a = np.cos(angle)
    sin_a = np.sin(angle)
    
    return np.array([
        [1, 0, 0, 0],
        [0, cos_a, -sin_a, 0],
        [0, sin_a, cos_a, 0],
        [0, 0, 0, 1]
    ], dtype=float)

def rotation_y_matrix(angle_degrees):
    """Матрица вращения вокруг оси Y"""
    angle = np.radians(angle_degrees)
    cos_a = np.cos(angle)
    sin_a = np.sin(angle)
    
    return np.array([
        [cos_a, 0, sin_a, 0],
        [0, 1, 0, 0],
        [-sin_a, 0, cos_a, 0],
        [0, 0, 0, 1]
    ], dtype=float)

def rotation_z_matrix(angle_degrees):
    """Матрица вращения вокруг оси Z"""
    angle = np.radians(angle_degrees)
    cos_a = np.cos(angle)
    sin_a = np.sin(angle)
    
    return np.array([
        [cos_a, -sin_a, 0, 0],
        [sin_a, cos_a, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ], dtype=float)

def perspective_projection_matrix(d):
    """Матрица перспективной проекции"""
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 1/d, 0]
    ], dtype=float)

def orthographic_projection_matrix():
    """Матрица ортографической проекции"""
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 1]
    ], dtype=float)

def shearing_matrix(sh_xy, sh_xz, sh_yx, sh_yz, sh_zx, sh_zy):
    """Матрица сдвига"""
    return np.array([
        [1,   sh_xy, sh_xz, 0],
        [sh_yx, 1,   sh_yz, 0],
        [sh_zx, sh_zy, 1,   0],
        [0,   0,    0,   1]
    ], dtype=float)

def rotation_around_line_matrix(line_point, direction_vector, angle_degrees):
    """Поворот вокруг произвольной прямой"""
    # Нормализация вектора направления
    dx, dy, dz = direction_vector
    length = np.sqrt(dx*dx + dy*dy + dz*dz)
    if length == 0:
        raise ValueError("Direction vector cannot be zero")
    
    u = dx / length
    v = dy / length
    w = dz / length
    
    # Угол поворота в радианах
    angle = np.radians(angle_degrees)
    cos_a = np.cos(angle)
    sin_a = np.sin(angle)
    one_minus_cos = 1 - cos_a
    
    # Матрица поворота вокруг произвольной оси
    rotation = np.array([
        [
            cos_a + u*u*one_minus_cos,
            u*v*one_minus_cos - w*sin_a,
            u*w*one_minus_cos + v*sin_a,
            0
        ],
        [
            u*v*one_minus_cos + w*sin_a,
            cos_a + v*v*one_minus_cos,
            v*w*one_minus_cos - u*sin_a,
            0
        ],
        [
            u*w*one_minus_cos - v*sin_a,
            v*w*one_minus_cos + u*sin_a,
            cos_a + w*w*one_minus_cos,
            0
        ],
        [0, 0, 0, 1]
    ], dtype=float)
    
    # Комбинирование с переносами
    translate_to_origin = translation_matrix(-line_point.x, -line_point.y, -line_point.z)
    translate_back = translation_matrix(line_point.x, line_point.y, line_point.z)
    
    return translate_back @ rotation @ translate_to_origin

def composite_transformation(*matrices):
    """Композиция нескольких матричных преобразований"""
    if not matrices:
        return identity_matrix()
    
    result = matrices[0]
    for matrix in matrices[1:]:
        result = matrix @ result
    
    return result

def transform_point(point, matrix):
    """Применение матрицы преобразования к точке"""
    return point.copy().transform(matrix)

def transform_multiple_points(points, matrix):
    """Применение матрицы преобразования к нескольким точкам"""
    return [transform_point(p, matrix) for p in points]

def create_spiral_transform(center, height, rotations, scale_factor=1.0):
    """Создание спирального преобразования"""
    matrices = []
    
    # Перенос в начало координат
    matrices.append(translation_matrix(-center.x, -center.y, -center.z))
    
    # Постепенный поворот и подъем
    angle_per_step = rotations * 360 / 10
    height_per_step = height / 10
    
    for i in range(1, 11):
        matrices.append(rotation_y_matrix(angle_per_step * i))
        matrices.append(translation_matrix(0, 0, height_per_step * i))
    
    # Масштабирование
    matrices.append(scaling_matrix(scale_factor, scale_factor, scale_factor))
    
    # Возврат обратно
    matrices.append(translation_matrix(center.x, center.y, center.z))
    
    return composite_transformation(*matrices)

def print_matrix_info(matrix, name="Matrix"):
    """Красивый вывод информации о матрице"""
    print(f"\n{name}:")
    for i, row in enumerate(matrix):
        row_str = ", ".join([f"{val:8.3f}" for val in row])
        if i == len(matrix) - 1:
            print(f"[{row_str}]")
        else:
            print(f"[{row_str}],")