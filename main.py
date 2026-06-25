from ursina import *
import src.escenario as esc
import src.jugador as jug
from src.barril import spawn_barril

app = Ursina()

# Inicializar componentes del juego
esc.init_escenario()
jug.init_jugador()

def input(key):
    if key == 'p':
        print(f"--- COORDENADAS DEL MODELO ---")
        print(f"Posición: {esc.modelo_dk.position}")
        print(f"Escala:   {esc.modelo_dk.scale}")

def update():
    # Lógica para subir escaleras
    en_escalera = False
    for escalera in esc.escaleras:
        # Usar distancia para saber si estamos cerca de una escalera
        dist_x = abs(jug.jugador.x - escalera.x)
        dist_z = abs(jug.jugador.z - escalera.z)
        dist_y = abs(jug.jugador.y - escalera.y)
        
        # El jugador debe estar cerca en X y Z, y dentro del rango Y de la escalera
        if dist_x < 1.5 and dist_z < 1.5 and dist_y < (escalera.scale_y / 2 + 1):
            en_escalera = True
            break
            
    if en_escalera:
        # Desactivar gravedad mientras estamos en la escalera
        jug.jugador.gravity = 0
        # Permitir subir y bajar con W y S
        if held_keys['w']:
            jug.jugador.y += 5 * time.dt
        if held_keys['s']:
            jug.jugador.y -= 5 * time.dt
    else:
        # Restaurar la gravedad normal
        jug.jugador.gravity = 1

    # ---- CONTROLES PARA AJUSTAR EL MODELO 3D ----
    # Presiona estas teclas para mover y escalar el modelo y alinearlo con el nivel
    velocidad_ajuste = 10 * time.dt
    if held_keys['up arrow']: esc.modelo_dk.z += velocidad_ajuste
    if held_keys['down arrow']: esc.modelo_dk.z -= velocidad_ajuste
    if held_keys['right arrow']: esc.modelo_dk.x += velocidad_ajuste
    if held_keys['left arrow']: esc.modelo_dk.x -= velocidad_ajuste
    if held_keys['page up']: esc.modelo_dk.y += velocidad_ajuste
    if held_keys['page down']: esc.modelo_dk.y -= velocidad_ajuste
    if held_keys['+']: esc.modelo_dk.scale += Vec3(1,1,1) * velocidad_ajuste
    if held_keys['-']: esc.modelo_dk.scale -= Vec3(1,1,1) * velocidad_ajuste

# Iniciar el ciclo de barriles
invoke(spawn_barril, delay=2)

app.run()
