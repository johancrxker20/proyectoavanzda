from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

def input(key):
    if key == 'p':
        print(f"--- COORDENADAS DEL MODELO ---")
        print(f"Posición: {modelo_dk.position}")
        print(f"Escala:   {modelo_dk.scale}")


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

class Barril(Entity):
    def __init__(self, position, direction):
        super().__init__(
            model='sphere', # En Ursina 'cylinder' no viene por defecto en algunas versiones, usamos esfera
            color=color.brown,
            texture='white_cube',
            collider='sphere',
            position=position,
            scale=(1.5, 1.5, 1.5),
            rotation_x=90 # Para que ruede visualmente
        )
        self.direction = direction # 1 para derecha, -1 para izquierda
        self.speed = 4.0
        self.fall_speed = 0
        self.was_falling = False

    def update(self):
        # Raycast hacia abajo para detectar plataformas
        # El radio del barril es 0.75 (escala 1.5 / 2). Usamos distancia 1.5 para el raycast.
        hit = raycast(self.position, (0, -1, 0), distance=1.5, ignore=(self, jugador))
        
        if hit.hit and isinstance(hit.entity, Plataforma):
            # Ajustar la altura para que ruede sobre la plataforma inclinada
            self.y = hit.world_point.y + 0.75
            
            # Si acabamos de aterrizar, invertimos la dirección para ir al otro lado
            if self.was_falling:
                self.direction *= -1
                self.was_falling = False
                
            # Mover horizontalmente
            self.x += self.direction * self.speed * time.dt
            # Rotar visualmente para simular rodamiento
            self.rotation_z += self.speed * self.direction * 100 * time.dt
            self.fall_speed = 0
        else:
            # No hay plataforma debajo, comienza a caer
            self.was_falling = True
            self.fall_speed += 15.0 * time.dt
            self.y -= self.fall_speed * time.dt
            # Se mueve ligeramente en el eje x mientras cae (como el original)
            self.x += self.direction * (self.speed * 0.2) * time.dt

        # Destruir el barril si cae fuera del nivel
        if self.y < -5:
            destroy(self)
            return

        # Colisión simple con el jugador usando cajas de colisión manuales (bounding box)
        dist_x = abs(self.x - jugador.x)
        dist_z = abs(self.z - jugador.z)
        dist_y = abs(self.y - jugador.y)
        
        if dist_x < 1.5 and dist_z < 1.5 and dist_y < 2.0:
            print("¡Juego Terminado! Te golpeó un barril.")
            jugador.position = start_position

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
plataformas = []
# Nivel 1 (inclinado a la derecha). Va desde x=-18 hasta x=12
plataformas.append(Plataforma(position=(-3, 2, 0), rotation_z=3))   
# Nivel 2 (inclinado a la izquierda). Va desde x=-12 hasta x=18
plataformas.append(Plataforma(position=(3, 8, 0), rotation_z=-3))  
# Nivel 3 (inclinado a la derecha). Va desde x=-18 hasta x=12
plataformas.append(Plataforma(position=(-3, 14, 0), rotation_z=3))  
# Nivel 4 (Cima, plana y más corta). Va desde x=-17 hasta x=-7
plataformas.append(Plataforma(position=(-12, 20, 0), rotation_z=0, scale=(10, 1, 5)))  

# Crear escaleras para conectar las plataformas (separadas en zig-zag)
escaleras = []
# Escalera de Nivel 1 a Nivel 2 (a la izquierda)
escaleras.append(Escalera(position=(-10, 5, 2.5)))
# Escalera de Nivel 2 a Nivel 3 (a la derecha)
escaleras.append(Escalera(position=(10, 11, 2.5)))
# Escalera de Nivel 3 a Nivel 4 (a la izquierda)
escaleras.append(Escalera(position=(-12, 17, 2.5)))

# El jugador (comienza en la parte inferior derecha, caminando contra los barriles)
start_position = (10, 4, 0)
jugador = FirstPersonController(position=start_position)

# Lógica general del juego (update)
def update():
    # Lógica para subir escaleras
    en_escalera = False
    for escalera in escaleras:
        # Usar distancia para saber si estamos cerca de una escalera
        dist_x = abs(jugador.x - escalera.x)
        dist_z = abs(jugador.z - escalera.z)
        dist_y = abs(jugador.y - escalera.y)
        
        # El jugador debe estar cerca en X y Z, y dentro del rango Y de la escalera
        if dist_x < 1.5 and dist_z < 1.5 and dist_y < (escalera.scale_y / 2 + 1):
            en_escalera = True
            break
            
    if en_escalera:
        # Desactivar gravedad mientras estamos en la escalera
        jugador.gravity = 0
        # Permitir subir y bajar con W y S
        if held_keys['w']:
            jugador.y += 5 * time.dt
        if held_keys['s']:
            jugador.y -= 5 * time.dt
    else:
        # Restaurar la gravedad normal
        jugador.gravity = 1

    # ---- CONTROLES PARA AJUSTAR EL MODELO 3D ----
    # Presiona estas teclas para mover y escalar el modelo y alinearlo con el nivel
    velocidad_ajuste = 10 * time.dt
    if held_keys['up arrow']: modelo_dk.z += velocidad_ajuste
    if held_keys['down arrow']: modelo_dk.z -= velocidad_ajuste
    if held_keys['right arrow']: modelo_dk.x += velocidad_ajuste
    if held_keys['left arrow']: modelo_dk.x -= velocidad_ajuste
    if held_keys['page up']: modelo_dk.y += velocidad_ajuste
    if held_keys['page down']: modelo_dk.y -= velocidad_ajuste
    if held_keys['+']: modelo_dk.scale += Vec3(1,1,1) * velocidad_ajuste
    if held_keys['-']: modelo_dk.scale -= Vec3(1,1,1) * velocidad_ajuste

# Spawner de barriles
def spawn_barril():
    # El barril aparece en la plataforma superior (Nivel 4), y rueda hacia la derecha (1)
    Barril(position=(-12, 22, 0), direction=1)
    # Invocar el siguiente barril en 4 segundos
    invoke(spawn_barril, delay=4)

# Iniciar el ciclo de barriles
invoke(spawn_barril, delay=2)

app.run()