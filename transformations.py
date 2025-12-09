# transformations.py
import numpy as np
from point import Point

def identity_matrix():
    """Единичная матрица 4x4"""
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
    """Вращение вокруг оси X"""
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
    """Вращение вокруг оси Y"""
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
    """Вращение вокруг оси Z"""
    angle = np.radians(angle_degrees)
    cos_a = np.cos(angle)
    sin_a = np.sin(angle)
    
    return np.array([
        [cos_a, -sin_a, 0, 0],
        [sin_a, cos_a, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ], dtype=float)

def composite_transformation(*matrices):
    """Композиция матричных преобразований"""
    if not matrices:
        return identity_matrix()
    
    result = matrices[0]
    for matrix in matrices[1:]:
        result = matrix @ result
    
    return result