from ursina import Entity, color, time, destroy, Vec3, raycast, Text
import random
import pausa

GRAVEDAD_BARRIL = 18.0
VEL_BARRIL = 4.0


class BarrilAceite(Entity):
    def __init__(self, posicion):
        super().__init__(model='cylinder', color=color.blue, scale=(1.2, 1.5, 1.2), position=posicion, collider='box')
        self.type = 'aceite'
        Text(parent=self, text='OIL', y=0.6, scale=4, color=color.cyan, origin=(0, 0))


class Llama(Entity):
    def __init__(self, posicion):
        super().__init__(model='sphere', color=color.red, scale=0.7, position=posicion, collider='box')
        self.type = 'llama'
        self.vel_x = random.choice([-3, 3])
        self.vel_y = 0

    def update(self):
        if pausa.esta_pausado(): return
        dt = time.dt

        # Movimiento Arcade (como en tu Pygame)
        self.x += self.vel_x * dt
        if self.x > 10.5 or self.x < -10.5:
            self.vel_x *= -1  # Rebote en las paredes

        ray = raycast(self.world_position + Vec3(0, 0.1, 0), Vec3(0, -1, 0), distance=0.8, ignore=(self,))
        if ray.hit and self.vel_y <= 0:
            self.y = ray.world_point.y + 0.35
            self.vel_y = 0
            # Si choca con un borde de plataforma, da la vuelta
            if not raycast(self.world_position + Vec3(self.vel_x * dt * 5, 0.1, 0), Vec3(0, -1, 0), distance=1).hit:
                self.vel_x *= -1
        else:
            self.vel_y -= GRAVEDAD_BARRIL * dt
            self.y += self.vel_y * dt


class Barril(Entity):
    def __init__(self, pos, direccion=1, nivel=1):
        super().__init__(model='sphere', position=pos, collider='sphere', color=color.brown, scale=0.55)
        self.type = 'barril'
        self.saltado = False  # Para el puntaje al saltarlo

        self.multiplicador_vel = 1.0 + (nivel * 0.15)
        self.vel_x = direccion * VEL_BARRIL * self.multiplicador_vel
        self.vel_y = 0.0

    def update(self):
        if pausa.esta_pausado(): return
        dt = time.dt

        self.vel_y -= GRAVEDAD_BARRIL * dt
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt

        if self.x > 11.5 or self.x < -11.5:
            destroy(self)
            return

        # Colisión con el barril de Aceite (Spawnea Llamas)
        hit = self.intersects()
        if hit.hit and hasattr(hit.entity, 'type') and hit.entity.type == 'aceite':
            Llama(posicion=(self.x, self.y + 1, 0))
            destroy(self)
            return

        ray = raycast(self.world_position + Vec3(0, 0.05, 0), Vec3(0, -1, 0), distance=0.7, ignore=(self,))
        if ray.hit and self.vel_y <= 0:
            self.y = ray.world_point.y + 0.40
            self.vel_y = 0.0
            viga = ray.entity
            if hasattr(viga, 'angulo'):
                if viga.angulo > 0:
                    self.vel_x = VEL_BARRIL * self.multiplicador_vel
                elif viga.angulo < 0:
                    self.vel_x = -VEL_BARRIL * self.multiplicador_vel

        self.rotation_z -= self.vel_x * 30 * dt


class Enemigo(Entity):
    def __init__(self, posicion, nivel=1):
        super().__init__(model='cube', color=color.brown, scale=(1.6, 1.4, 1.0), position=posicion)
        self.type = 'enemigo'
        self.nivel = nivel
        self._timer = 0.0
        self.min_interval = max(0.6, 2.0 - (nivel * 0.2))
        self.max_interval = max(1.2, 3.5 - (nivel * 0.2))
        self._intervalo = random.uniform(self.min_interval, self.max_interval)

    def update(self):
        if pausa.esta_pausado(): return
        self._timer += time.dt
        if self._timer >= self._intervalo:
            self._timer = 0.0
            self._intervalo = random.uniform(self.min_interval, self.max_interval)
            Barril(pos=self.position + Vec3(0.9, -0.5, 0), direccion=1, nivel=self.nivel)