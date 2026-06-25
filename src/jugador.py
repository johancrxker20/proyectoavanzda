from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

start_position = (10, 4, 0)
jugador = None

def init_jugador():
    global jugador
    jugador = FirstPersonController(position=start_position)
