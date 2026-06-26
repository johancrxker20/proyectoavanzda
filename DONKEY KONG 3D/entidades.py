from ursina import (
    Entity, color, held_keys, time, Text, destroy,
    Vec3, raycast, clamp, invoke, scene, mouse
)
import pausa

GRAVEDAD = 20.0
FUERZA_SALTO = 8.0
VELOCIDAD_MOV = 5.5
DISTANCIA_PISO = 0.45
RAY_DISTANCIA = 1.2
RADIO_ESCALERA_X = 0.70
RADIO_ESCALERA_Y = 0.55


def _obtener_escalera_cercana(jugador):
    jx, jy = jugador.x, jugador.y
    for e in scene.entities:
        if not (hasattr(e, 'type') and e.type == 'escalera'): continue
        sx, sy = e.scale_x * 0.5, e.scale_y * 0.5
        if (abs(jx - e.x) < RADIO_ESCALERA_X + sx and abs(jy - e.y) < RADIO_ESCALERA_Y + sy):
            return e
    return None


class Martillo(Entity):
    def __init__(self, posicion):
        super().__init__(model='cube', color=color.yellow, scale=(0.4, 0.6, 0.4), position=posicion, collider='box')
        self.type = 'martillo'
        self._t = 0

    def update(self):
        if pausa.esta_pausado(): return
        self._t += time.dt
        self.y += 0.005 * (1 if (self._t % 1) < 0.5 else -1)


class Meta(Entity):
    def __init__(self, posicion):
        super().__init__(model='cube', color=color.violet, scale=(1.0, 1.4, 1.0), position=posicion, collider='box')
        self.type = 'meta'


class Jugador(Entity):
    def __init__(self, posicion):
        super().__init__(position=posicion, collider='box', model='cube', scale=(0.7, 0.8, 0.7), color=color.blue)
        self.vel_y = 0.0
        self.en_suelo = False
        self.escalando = False
        self.velocidad = VELOCIDAD_MOV
        self.vidas = 3

        # Puntos
        self.puntos = 0
        self.high_score = 0
        self.ui_high_ref = None

        self.tiene_martillo = False
        self._invulnerable = False
        self._spawn = Vec3(posicion)
        self._ganando = False

        self.texto_vidas = Text(text='VIDA: 3', position=(-0.83, 0.46), scale=2.2, color=color.red, background=True)
        self.texto_puntos = Text(text='PUNTOS: 0', position=(-0.02, 0.46), origin=(0, 0), scale=2.0, color=color.yellow,
                                 background=True)
        self.texto_martillo = Text(text='', position=(0.35, 0.46), scale=2.0, color=color.yellow, background=True)

        mouse.locked = False
        mouse.visible = False

    def input(self, key):
        if key == 'space' and self.en_suelo and not self.escalando:
            self.vel_y = FUERZA_SALTO
            self.en_suelo = False

    def update(self):
        if self._ganando or pausa.esta_pausado(): return
        dt = time.dt

        # 1. ESCALERAS
        escalera_cercana = _obtener_escalera_cercana(self)
        if escalera_cercana:
            if not self.escalando and (
                    held_keys['w'] or held_keys['up arrow'] or held_keys['s'] or held_keys['down arrow']):
                self.escalando = True
                self.x = escalera_cercana.x
        else:
            self.escalando = False

        if self.escalando and self.en_suelo and (
                held_keys['a'] or held_keys['left arrow'] or held_keys['d'] or held_keys['right arrow']):
            self.escalando = False

        # 2. MOVIMIENTO
        if not self.escalando:
            if held_keys['d'] or held_keys['right arrow']: self.x += self.velocidad * dt
            if held_keys['a'] or held_keys['left arrow']:  self.x -= self.velocidad * dt
            self.x = clamp(self.x, -10.5, 10.5)

        # 3. GRAVEDAD
        if self.escalando:
            self.vel_y = 0
            if held_keys['w'] or held_keys['up arrow']: self.y += 3.5 * dt
            if held_keys['s'] or held_keys['down arrow']:
                ray_abajo = raycast(self.world_position, Vec3(0, -1, 0), distance=DISTANCIA_PISO + 0.1, ignore=(self,))
                if ray_abajo.hit:
                    self.y = ray_abajo.world_point.y + DISTANCIA_PISO
                    self.escalando = False
                    self.en_suelo = True
                else:
                    self.y -= 3.5 * dt
        else:
            ray = raycast(self.world_position, Vec3(0, -1, 0), distance=RAY_DISTANCIA, ignore=(self,))
            if ray.hit and self.vel_y <= 0:
                self.y = ray.world_point.y + DISTANCIA_PISO
                self.vel_y = 0
                self.en_suelo = True
            else:
                self.en_suelo = False

            if not self.en_suelo:
                self.vel_y -= GRAVEDAD * dt
                self.y += self.vel_y * dt

        self._revisar_colisiones()
        self._revisar_salto_barriles()
        if self.y < -20: self._recibir_danio()

    def _revisar_salto_barriles(self):
        # Si estás en el aire, busca barriles debajo de ti
        if not self.en_suelo and not self.escalando:
            for e in scene.entities:
                if hasattr(e, 'type') and e.type == 'barril' and not getattr(e, 'saltado', False):
                    # Si pasaste por encima del barril
                    if abs(self.x - e.x) < 1.0 and self.y > e.y and self.y < e.y + 3:
                        e.saltado = True
                        self._sumar_puntos(100)

    def _revisar_colisiones(self):
        hit_info = self.intersects()
        if not hit_info.hit: return
        e = hit_info.entity
        if not hasattr(e, 'type'): return

        if e.type == 'martillo':
            self.tiene_martillo = True
            self.texto_martillo.text = 'MARTILLO!'
            destroy(e)
            invoke(self._perder_martillo, delay=10)  # 10 Segundos de Martillo

        # Enemigos (Barril o Llama de Fuego)
        elif e.type == 'barril' or e.type == 'llama':
            if self._invulnerable: return
            if self.tiene_martillo:
                self._sumar_puntos(500)
                destroy(e)
            else:
                self._recibir_danio()

        elif e.type == 'meta':
            self._ganar()
        elif e.type == 'muerte':
            self._recibir_danio()

    def _sumar_puntos(self, cantidad):
        self.puntos += cantidad
        self.texto_puntos.text = f'PUNTOS: {self.puntos}'
        if self.puntos > self.high_score:
            self.high_score = self.puntos
            if self.ui_high_ref: self.ui_high_ref.text = f'TOP: {self.high_score}'

    def _ganar(self):
        if self._ganando: return
        self._ganando = True
        self._sumar_puntos(1000)  # Regresa el premio fijo de 1000 puntos al ganar
        pausa.mostrar_victoria(self.puntos)

    def _recibir_danio(self):
        if self._invulnerable: return
        self.vidas -= 1
        self._invulnerable = True
        self.texto_vidas.text = f'VIDA: {self.vidas}'

        # Limpiar enemigos actuales
        for e in scene.entities[:]:
            if hasattr(e, 'type') and e.type in ['barril', 'llama']: destroy(e)

        self.x, self.y, self.z = self._spawn.x, self._spawn.y, self._spawn.z
        self.vel_y = 0
        self.escalando = False
        self.tiene_martillo = False
        self.texto_martillo.text = ''

        invoke(self._fin_invulnerabilidad, delay=2)
        if self.vidas <= 0: self._game_over()

    def _fin_invulnerabilidad(self):
        self._invulnerable = False

    def _perder_martillo(self):
        self.tiene_martillo = False
        self.texto_martillo.text = ''

    def _game_over(self):
        pausa.mostrar_game_over()

    def on_destroy(self):
        if hasattr(self, 'texto_vidas') and self.texto_vidas: destroy(self.texto_vidas)
        if hasattr(self, 'texto_puntos') and self.texto_puntos: destroy(self.texto_puntos)
        if hasattr(self, 'texto_martillo') and self.texto_martillo: destroy(self.texto_martillo)


def generar_martillos():
    Martillo(posicion=(-6.0, -6.8, 0))
    Martillo(posicion=(5.5, 0.8, 0))