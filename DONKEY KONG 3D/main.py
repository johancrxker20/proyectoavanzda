from ursina import (
    Ursina, camera, window, color, DirectionalLight, AmbientLight, Text, Vec3, scene, destroy
)
from mapa import construir_nivel
from entidades import Jugador, Meta, generar_martillos
from enemigos import Enemigo, BarrilAceite
import pausa

app = Ursina(title='Donkey Kong 2.5D', borderless=False, fullscreen=True, development_mode=False)
window.color = color.Color(0.05, 0.05, 0.15, 1)
window.exit_button.visible = False

# Iluminación
luz = DirectionalLight()
luz.look_at(Vec3(1, -2, 1))
AmbientLight(color=color.Color(0, 0, 0.3, 0.2))

# ── CÁMARA FIJA 2.5D ────────────────────────────
camera.orthographic = False
camera.position = (0, 14, -90)
camera.rotation_x = 8

# Variables de Progresión Arcade
nivel_actual = 1
puntos_actuales = 0
high_score = 0

# HUD Arcade (Como en Pygame)
ui_high = Text(text=f'TOP: {high_score}', position=(0.60, 0.46), scale=2.2, color=color.cyan, background=True)
Text(text='A/D: Mover | W/S: Subir | ESPACIO: Saltar', origin=(0, 0), position=(0, -0.47), scale=1.4, color=color.white,
     background=True)


def _limpiar_nivel():
    tipos = {'viga', 'escalera', 'muerte', 'barril', 'enemigo', 'meta', 'martillo', 'aceite', 'llama'}
    for e in scene.entities[:]:
        if hasattr(e, 'type') and e.type in tipos:
            destroy(e)
        elif hasattr(e, 'vidas'):
            destroy(e)


def iniciar_nivel(puntos=0, nivel=1):
    global nivel_actual, puntos_actuales
    nivel_actual = nivel
    puntos_actuales = puntos

    _limpiar_nivel()
    construir_nivel()
    generar_martillos()

    # Jugador y Entidades
    jugador = Jugador(posicion=(-8.5, -10.7, 0))
    jugador.puntos = puntos_actuales
    jugador.high_score = high_score
    jugador.texto_puntos.text = f'PUNTOS: {puntos_actuales}'
    jugador.ui_high_ref = ui_high  # Para actualizar el high score al morir/ganar

    # DK, Pauline y el Nuevo Barril de Aceite (Pygame adaptation)
    Enemigo(posicion=(-5.5, 13.5, 0), nivel=nivel_actual)
    Meta(posicion=(5.5, 14.8, 0))
    BarrilAceite(posicion=(-8.5, -11.0, 0))  # Zona inferior izquierda


# ── FUNCIONES DE FLUJO ───────────────────
def reinicio_nivel(): iniciar_nivel(puntos_actuales, nivel_actual)


def reinicio_total(): iniciar_nivel(puntos=0, nivel=1)


def siguiente_nivel(puntos_ganados): iniciar_nivel(puntos=puntos_ganados, nivel=nivel_actual + 1)


pausa._reinicio_nivel_ref = reinicio_nivel
pausa._reinicio_total_ref = reinicio_total
pausa._siguiente_nivel_ref = siguiente_nivel

iniciar_nivel()


def input(key):
    if key == 'escape':
        if pausa.esta_pausado():
            pausa.cerrar_menu()
        else:
            pausa.abrir_pausa()


app.run()