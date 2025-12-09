# model_loader.py
import numpy as np
from point import Point

class Face:
    """Класс для представления грани 3D модели"""
    def __init__(self, vertex_indices):
        self.vertex_indices = vertex_indices  # Индексы вершин грани
        self.normal = None  # Вектор нормали грани
    
    def __str__(self):
        return f"Face({self.vertex_indices}, normal={self.normal})"
    
    def copy(self):
        """Создание копии грани"""
        return Face(self.vertex_indices.copy())
    
    def calculate_normal(self, vertices):
        """Вычисление нормали грани по вершинам"""
        if len(self.vertex_indices) < 3:
            return None
        
        # Берем первые три вершины для вычисления нормали
        v0 = vertices[self.vertex_indices[0]].to_array()
        v1 = vertices[self.vertex_indices[1]].to_array()
        v2 = vertices[self.vertex_indices[2]].to_array()
        
        # Векторы двух ребер
        edge1 = v1 - v0
        edge2 = v2 - v0
        
        # Векторное произведение для получения нормали
        normal_vec = np.cross(edge1, edge2)
        
        # Нормализация вектора
        norm = np.linalg.norm(normal_vec)
        if norm > 0:
            normal_vec = normal_vec / norm
        
        # Сохраняем нормаль как объект Point
        self.normal = Point.from_array(normal_vec)
        return self.normal

class Model3D:
    """Класс для представления 3D модели"""
    def __init__(self, vertices=None, faces=None):
        self.vertices = vertices if vertices is not None else []
        self.faces = faces if faces is not None else []
    
    def __str__(self):
        return f"Model3D({len(self.vertices)} вершин, {len(self.faces)} граней)"
    
    def copy(self):
        """Создание глубокой копии модели"""
        # Копируем вершины
        new_vertices = [Point(v.x, v.y, v.z) for v in self.vertices]
        
        # Копируем грани
        new_faces = [Face(f.vertex_indices.copy()) for f in self.faces]
        
        # Копируем нормали (если они есть)
        for i, face in enumerate(self.faces):
            if face.normal:
                new_faces[i].normal = Point(face.normal.x, face.normal.y, face.normal.z)
        
        return Model3D(new_vertices, new_faces)
    
    def apply_transform(self, matrix):
        """Применение матрицы преобразования ко всем вершинам модели"""
        for vertex in self.vertices:
            vertex.transform(matrix)
        
        # Пересчет нормалей после преобразования
        for face in self.faces:
            face.calculate_normal(self.vertices)
    
    def get_transformed_copy(self, matrix):
        """Создание преобразованной копии модели"""
        transformed = self.copy()
        transformed.apply_transform(matrix)
        return transformed

def create_cube():
    """Создает куб (выпуклый многогранник)"""
    # Вершины куба (размер 2x2x2, центр в начале координат)
    vertices = [
        Point(-1, -1, -1),  # 0: задний-нижний-левый
        Point(1, -1, -1),   # 1: задний-нижний-правый
        Point(1, 1, -1),    # 2: задний-верхний-правый
        Point(-1, 1, -1),   # 3: задний-верхний-левый
        Point(-1, -1, 1),   # 4: передний-нижний-левый
        Point(1, -1, 1),    # 5: передний-нижний-правый
        Point(1, 1, 1),     # 6: передний-верхний-правый
        Point(-1, 1, 1),    # 7: передний-верхний-левый
    ]
    
    # Грани куба (каждая грань - четырехугольник)
    faces = [
        Face([0, 3, 2, 1]),  # Задняя грань
        Face([4, 5, 6, 7]),  # Передняя грань
        Face([0, 4, 7, 3]),  # Левая грань
        Face([1, 2, 6, 5]),  # Правая грань
        Face([0, 1, 5, 4]),  # Нижняя грань
        Face([2, 3, 7, 6]),  # Верхняя грань
    ]
    
    # Создаем модель
    model = Model3D(vertices, faces)
    
    # Вычисляем нормали для всех граней
    for face in model.faces:
        face.calculate_normal(model.vertices)
    
    print(f"✓ Создан куб: {len(vertices)} вершин, {len(faces)} граней")
    return model

def create_diamond():
    """Создает ромб (октаэдр) - выпуклый многогранник"""
    # Вершины октаэдра (ромба)
    vertices = [
        Point(0, 1, 0),    # 0: верхняя вершина
        Point(0, -1, 0),   # 1: нижняя вершина
        Point(1, 0, 0),    # 2: правая вершина
        Point(-1, 0, 0),   # 3: левая вершина
        Point(0, 0, 1),    # 4: передняя вершина
        Point(0, 0, -1),   # 5: задняя вершина
    ]
    
    # Грани октаэдра (все грани - треугольники)
    faces = [
        Face([0, 2, 4]),  # Верхний-правый-передний треугольник
        Face([0, 4, 3]),  # Верхний-передний-левый треугольник
        Face([0, 3, 5]),  # Верхний-левый-задний треугольник
        Face([0, 5, 2]),  # Верхний-задний-правый треугольник
        
        Face([1, 4, 2]),  # Нижний-передний-правый треугольник
        Face([1, 3, 4]),  # Нижний-левый-передний треугольник
        Face([1, 5, 3]),  # Нижний-задний-левый треугольник
        Face([1, 2, 5]),  # Нижний-правый-задний треугольник
    ]
    
    # Создаем модель
    model = Model3D(vertices, faces)
    
    # Вычисляем нормали для всех граней
    for face in model.faces:
        face.calculate_normal(model.vertices)
    
    print(f"✓ Создан ромб (октаэдр): {len(vertices)} вершин, {len(faces)} граней")
    return model

def create_pyramid():
    """Создает квадратную пирамиду (невыпуклый объект)"""
    # Вершины пирамиды
    vertices = [
        Point(0, 1, 0),      # 0: вершина пирамиды
        Point(-1, -1, -1),   # 1: задний-левый угол основания
        Point(1, -1, -1),    # 2: задний-правый угол основания
        Point(1, -1, 1),     # 3: передний-правый угол основания
        Point(-1, -1, 1),    # 4: передний-левый угол основания
    ]
    
    # Грани пирамиды
    faces = [
        Face([0, 1, 2]),      # Задняя треугольная грань
        Face([0, 2, 3]),      # Правая треугольная грань
        Face([0, 3, 4]),      # Передняя треугольная грань
        Face([0, 4, 1]),      # Левая треугольная грань
        Face([1, 4, 3, 2]),   # Квадратное основание
    ]
    
    # Создаем модель
    model = Model3D(vertices, faces)
    
    # Вычисляем нормали для всех граней
    for face in model.faces:
        face.calculate_normal(model.vertices)
    
    print(f"✓ Создана пирамида: {len(vertices)} вершин, {len(faces)} граней")
    return model

def load_obj(filename):
    """Загружает модель из файла формата .obj (опционально)"""
    if filename == "default_cube":
        return create_cube()
    elif filename == "default_diamond":
        return create_diamond()
    elif filename == "default_pyramid":
        return create_pyramid()
    
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
                    # Вершина: v x y z
                    if len(parts) >= 4:
                        x = float(parts[1])
                        y = float(parts[2])
                        z = float(parts[3])
                        vertices.append(Point(x, y, z))
                
                elif parts[0] == 'f':
                    # Грань: f v1/vt1/vn1 v2/vt2/vn2 ...
                    vertex_indices = []
                    for part in parts[1:]:
                        # Разделяем по '/'
                        indices = part.split('/')
                        # Берем индекс вершины (в OBJ индексы начинаются с 1)
                        vertex_idx = int(indices[0]) - 1
                        if 0 <= vertex_idx < len(vertices):
                            vertex_indices.append(vertex_idx)
                    
                    if len(vertex_indices) >= 3:
                        faces.append(Face(vertex_indices))
        
        # Создаем модель
        model = Model3D(vertices, faces)
        
        # Вычисляем нормали
        for face in model.faces:
            face.calculate_normal(model.vertices)
        
        print(f"✓ Загружено из {filename}: {len(vertices)} вершин, {len(faces)} граней")
        return model
    
    except FileNotFoundError:
        print(f"✗ Файл {filename} не найден. Создаю куб по умолчанию.")
        return create_cube()
    except Exception as e:
        print(f"✗ Ошибка загрузки {filename}: {e}. Создаю куб по умолчанию.")
        return create_cube()

# Экспорт функций для создания моделей
__all__ = ['Face', 'Model3D', 'create_cube', 'create_diamond', 'create_pyramid', 'load_obj']