from ursina import *

plataformas = []
escaleras = []
modelo_dk = None
suelo = None

class Plataforma(Entity):
    def __init__(self, position, rotation_z, scale=(30, 1, 5)):
        super().__init__(
            model='cube',
            color=color.clear, # Invisible, solo para colisiones
            collider='box',
            position=position,
            rotation_z=rotation_z,
            scale=scale
        )

class Escalera(Entity):
    def __init__(self, position, scale=(2, 10, 0.5)):
        super().__init__(
            model='cube',
            color=color.clear, # Invisible, solo para detectar si subimos
            collider='box',
            position=position,
            scale=scale
        )

def init_escenario():
    global plataformas, escaleras, modelo_dk, suelo
    
    # El suelo base (Lo hacemos invisible para ver solo tu modelo 3D)
    suelo = Entity(model='cube', scale=(50, 1, 50), color=color.clear, collider='box', position=(0, -0.5, 0))

    # Cargar el modelo 3D proporcionado
    modelo_dk = Entity(
        model='donkey_kong/scene.gltf', 
        position=(-22.088218, 20.20544, 11.450036), 
        scale=3.1798005,
        double_sided=True 
    )

    # Crear el nivel (Plataformas desplazadas para que los barriles caigan en cascada)
    # Nivel 1 (inclinado a la derecha). Va desde x=-18 hasta x=12
    plataformas.append(Plataforma(position=(-3, 2, 0), rotation_z=3))   
    # Nivel 2 (inclinado a la izquierda). Va desde x=-12 hasta x=18
    plataformas.append(Plataforma(position=(3, 8, 0), rotation_z=-3))  
    # Nivel 3 (inclinado a la derecha). Va desde x=-18 hasta x=12
    plataformas.append(Plataforma(position=(-3, 14, 0), rotation_z=3))  
    # Nivel 4 (Cima, plana y más corta). Va desde x=-17 hasta x=-7
    plataformas.append(Plataforma(position=(-12, 20, 0), rotation_z=0, scale=(10, 1, 5)))  

    # Crear escaleras para conectar las plataformas (separadas en zig-zag)
    # Escalera de Nivel 1 a Nivel 2 (a la izquierda)
    escaleras.append(Escalera(position=(-10, 5, 2.5)))
    # Escalera de Nivel 2 a Nivel 3 (a la derecha)
    escaleras.append(Escalera(position=(10, 11, 2.5)))
    # Escalera de Nivel 3 a Nivel 4 (a la izquierda)
    escaleras.append(Escalera(position=(-12, 17, 2.5)))
