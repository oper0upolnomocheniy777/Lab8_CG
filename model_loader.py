# model_loader.py
import numpy as np
from point import Point

class Face:
    def __init__(self, vertex_indices, normal=None):
        self.vertex_indices = vertex_indices  # Индексы вершин
        self.normal = normal  # Вектор нормали (Point)
        self.color = (100, 150, 200)  # Цвет по умолчанию
    
    def __str__(self):
        return f"Face({self.vertex_indices}, normal={self.normal})"
    
    def copy(self):
        """Создание копии грани"""
        normal_copy = self.normal.copy() if self.normal else None
        return Face(self.vertex_indices.copy(), normal_copy)
    
    def calculate_normal(self, vertices):
        """Вычисление нормали грани по вершинам"""
        if len(self.vertex_indices) < 3:
            return None
        
        v0 = vertices[self.vertex_indices[0]].to_array()
        v1 = vertices[self.vertex_indices[1]].to_array()
        v2 = vertices[self.vertex_indices[2]].to_array()
        
        edge1 = v1 - v0
        edge2 = v2 - v0
        normal_vec = np.cross(edge1, edge2)
        
        # Нормализация
        norm = np.linalg.norm(normal_vec)
        if norm > 0:
            normal_vec = normal_vec / norm
        
        self.normal = Point.from_array(normal_vec)
        return self.normal

class Model3D:
    def __init__(self, vertices=None, faces=None):
        self.vertices = vertices if vertices is not None else []
        self.faces = faces if faces is not None else []
        self.center = Point(0, 0, 0)
    
    def __str__(self):
        return f"Model3D({len(self.vertices)} vertices, {len(self.faces)} faces)"
    
    def copy(self):
        """Создание глубокой копии модели"""
        new_vertices = [v.copy() for v in self.vertices]
        new_faces = [f.copy() for f in self.faces]
        return Model3D(new_vertices, new_faces)
    
    def apply_transform(self, matrix):
        """Применение матрицы преобразования к модели"""
        # Преобразование вершин
        for vertex in self.vertices:
            vertex.transform(matrix)
        
        # Пересчет нормалей
        for face in self.faces:
            face.calculate_normal(self.vertices)
        
        # Обновление центра
        self.update_center()
    
    def update_center(self):
        """Вычисление центра модели"""
        if not self.vertices:
            self.center = Point(0, 0, 0)
            return
        
        sum_x = sum_y = sum_z = 0.0
        for vertex in self.vertices:
            sum_x += vertex.x
            sum_y += vertex.y
            sum_z += vertex.z
        
        self.center = Point(
            sum_x / len(self.vertices),
            sum_y / len(self.vertices),
            sum_z / len(self.vertices)
        )
    
    def get_bounding_box(self):
        """Получение ограничивающего параллелепипеда"""
        if not self.vertices:
            return None, None
        
        min_point = Point(float('inf'), float('inf'), float('inf'))
        max_point = Point(float('-inf'), float('-inf'), float('-inf'))
        
        for vertex in self.vertices:
            min_point.x = min(min_point.x, vertex.x)
            min_point.y = min(min_point.y, vertex.y)
            min_point.z = min(min_point.z, vertex.z)
            
            max_point.x = max(max_point.x, vertex.x)
            max_point.y = max(max_point.y, vertex.y)
            max_point.z = max(max_point.z, vertex.z)
        
        return min_point, max_point

def load_obj(filename):
    """Загружает модель из файла .obj"""
    if filename == "default_cube":
        return create_cube()
    
    vertices = []
    faces = []
    
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split()
                if not parts:
                    continue
                
                if parts[0] == 'v':
                    # Вершина
                    if len(parts) >= 4:
                        vertex = Point(float(parts[1]), float(parts[2]), float(parts[3]))
                        vertices.append(vertex)
                
                elif parts[0] == 'f':
                    # Грань
                    vertex_indices = []
                    for part in parts[1:]:
                        # Разделяем по '/'
                        indices = part.split('/')
                        # Индекс вершин в OBJ начинается с 1
                        vertex_idx = int(indices[0]) - 1
                        if vertex_idx >= 0 and vertex_idx < len(vertices):
                            vertex_indices.append(vertex_idx)
                    
                    if len(vertex_indices) >= 3:
                        face = Face(vertex_indices)
                        faces.append(face)
        
        # Вычисление нормалей
        for face in faces:
            face.calculate_normal(vertices)
        
        model = Model3D(vertices, faces)
        model.update_center()
        
        print(f"Loaded {filename}: {len(vertices)} vertices, {len(faces)} faces")
        return model
    
    except FileNotFoundError:
        print(f"File {filename} not found")
        raise
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return create_cube()

def create_cube():
    """Создает куб для тестирования"""
    vertices = [
        Point(-1, -1, -1), Point(1, -1, -1), Point(1, 1, -1), Point(-1, 1, -1),
        Point(-1, -1, 1),  Point(1, -1, 1),  Point(1, 1, 1),  Point(-1, 1, 1)
    ]
    
    faces = [
        Face([0, 3, 2, 1]),  # задняя
        Face([4, 5, 6, 7]),  # передняя
        Face([0, 4, 7, 3]),  # левая
        Face([1, 2, 6, 5]),  # правая
        Face([0, 1, 5, 4]),  # нижняя
        Face([2, 3, 7, 6])   # верхняя
    ]
    
    # Вычисление нормалей
    for face in faces:
        face.calculate_normal(vertices)
    
    model = Model3D(vertices, faces)
    model.update_center()
    return model