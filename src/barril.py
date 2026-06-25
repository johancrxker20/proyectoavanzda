from ursina import *
from src.escenario import Plataforma
import src.jugador as jug

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
        hit = raycast(self.position, (0, -1, 0), distance=1.5, ignore=(self, jug.jugador))
        
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
        dist_x = abs(self.x - jug.jugador.x)
        dist_z = abs(self.z - jug.jugador.z)
        dist_y = abs(self.y - jug.jugador.y)
        
        if dist_x < 1.5 and dist_z < 1.5 and dist_y < 2.0:
            print("¡Juego Terminado! Te golpeó un barril.")
            jug.jugador.position = jug.start_position

def spawn_barril():
    # El barril aparece en la plataforma superior (Nivel 4), y rueda hacia la derecha (1)
    Barril(position=(-12, 22, 0), direction=1)
    # Invocar el siguiente barril en 4 segundos
    invoke(spawn_barril, delay=4)
