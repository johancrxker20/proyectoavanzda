from ursina import Entity, color, Vec3

class Viga(Entity):
    """Plataforma inclinada por la que ruedan los barriles."""
    def __init__(self, x, y, ancho, angulo=0):
        super().__init__(
            model='cube',
            color=color.orange,
            scale=(ancho, 0.4, 3),
            position=(x, y, 0),
            rotation_z=angulo,
            collider='box'
        )
        self.type   = 'viga'
        self.angulo = angulo


class Escalera(Entity):
    """
    Escalera visual sin collider físico.
    """
    def __init__(self, x, y, alto):
        super().__init__(
            model='cube',
            color=color.Color(0.1, 0.7, 0.1, 1),
            # --- CORRECCIÓN ---
            # scale_z (profundidad) a 0.5 para que sea plana
            scale=(0.8, alto, 0.5),
            # position_z a 1.2 para empujarla al fondo (detrás del jugador que está en 0)
            position=(x, y, 1.2),
            collider=None
        )
        self.type = 'escalera'
        self.alto = alto


# ──────────────────────────────────────────────────────────────
#  Layout Donkey Kong — patrón alternado
#  Huecos de 2.2 u para que los barriles caigan con holgura.
# ──────────────────────────────────────────────────────────────

_H = 1.1   # semiancho del hueco → hueco total 2.2 u

VIGAS_SEGMENTOS = [
    # viga 0 / suelo — sin hueco
    (   0.00,  -11.5, 22.00,   0.0),

    # viga 1 — hueco en x=+6  (escalera DERECHA)
    (  -3.05,   -7.5, 15.10,   3.0),
    (   9.05,   -7.5,  3.90,   3.0),

    # viga 2 — hueco en x=-6  (escalera IZQUIERDA)
    (  -9.05,   -3.5,  3.90,  -3.0),
    (   3.05,   -3.5, 15.10,  -3.0),

    # viga 3 — hueco en x=+6  (escalera DERECHA)
    (  -3.05,    0.5, 15.10,   3.0),
    (   9.05,    0.5,  3.90,   3.0),

    # viga 4 — hueco en x=-6  (escalera IZQUIERDA)
    (  -9.05,    4.5,  3.90,  -3.0),
    (   3.05,    4.5, 15.10,  -3.0),

    # viga 5 — hueco en x=+6  (escalera DERECHA)
    (  -3.05,    8.5, 15.10,   3.0),
    (   9.05,    8.5,  3.90,   3.0),

    # viga 6 / plataforma DK — hueco en x=-4.5  (escalera IZQUIERDA)
    (  -8.30,   12.0,  5.40,   0.0),
    (  -1.95,   12.0,  2.90,   0.0),

    # viga 7 / plataforma Pauline — sin hueco
    (   4.50,   13.5,  8.00,   0.0),
]

ESCALERAS = [
    # (x,   y_centro, alto)
    (  6.0,  -9.5,  4.2),   # viga0→1  DERECHA
    ( -6.0,  -5.5,  4.2),   # viga1→2  IZQUIERDA
    (  6.0,  -1.5,  4.2),   # viga2→3  DERECHA
    ( -6.0,   2.5,  4.2),   # viga3→4  IZQUIERDA
    (  6.0,   6.5,  4.2),   # viga4→5  DERECHA
    ( -4.5,  10.2,  3.8),   # viga5→DK IZQUIERDA
]


def construir_nivel():
    for (x, y, ancho, ang) in VIGAS_SEGMENTOS:
        Viga(x, y, ancho, ang)

    for (x, y, alto) in ESCALERAS:
        Escalera(x, y, alto)

    # Suelo de muerte
    Entity(
        model='cube',
        color=color.black,
        scale=(40, 0.2, 6),
        position=(0, -14.5, 0),
        collider='box'
    ).type = 'muerte'