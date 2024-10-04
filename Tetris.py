import pygame
import random
import json
import os

pygame.init()

ANCHO, ALTO = 800, 600
ANCHO_TABLERO, ALTO_TABLERO = 300, 600
TAMANO_BLOQUE = 30
FILAS = ALTO_TABLERO // TAMANO_BLOQUE
COLUMNAS = ANCHO_TABLERO // TAMANO_BLOQUE

NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
GRIS = (128, 128, 128)
CYAN = (0, 255, 255)
AZUL = (0, 0, 255)
NARANJA = (255, 165, 0)
AMARILLO = (255, 255, 0)
VERDE = (0, 255, 0)
MORADO = (128, 0, 128)
ROJO = (255, 0, 0)

FORMAS = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
]

COLORES = [CYAN, AMARILLO, MORADO, AZUL, NARANJA, VERDE, ROJO]

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Tetris")

fuente_grande = pygame.font.Font(None, 74)
fuente_mediana = pygame.font.Font(None, 48)
fuente_pequeña = pygame.font.Font(None, 36)

controles = {
    "izquierda": pygame.K_LEFT,
    "derecha": pygame.K_RIGHT,
    "rotar": pygame.K_UP,
    "bajar": pygame.K_DOWN,
    "caer": pygame.K_SPACE,
    "pausa": pygame.K_ESCAPE,
}


class Pieza:
    def __init__(self, x, y, forma):
        self.x = x
        self.y = y
        self.forma = forma
        self.color = COLORES[FORMAS.index(forma)]
        self.rotacion = 0


class Tetris:
    def __init__(self, filas, columnas):
        self.filas = filas
        self.columnas = columnas
        self.tablero = [[0 for _ in range(columnas)] for _ in range(filas)]
        self.pieza_actual = self.nueva_pieza()
        self.game_over = False
        self.score = 0

    def nueva_pieza(self):
        forma = random.choice(FORMAS)
        return Pieza(self.columnas // 2 - len(forma[0]) // 2, 0, forma)

    def intersecta(self):
        for i, fila in enumerate(self.pieza_actual.forma):
            for j, celda in enumerate(fila):
                if celda:
                    if (
                        self.pieza_actual.y + i >= self.filas
                        or self.pieza_actual.x + j < 0
                        or self.pieza_actual.x + j >= self.columnas
                        or self.tablero[self.pieza_actual.y + i][
                            self.pieza_actual.x + j
                        ]
                    ):
                        return True
        return False

    def limpiar_filas(self):
        filas_llenas = [i for i, fila in enumerate(self.tablero) if all(fila)]
        for fila in filas_llenas:
            del self.tablero[fila]
            self.tablero.insert(0, [0 for _ in range(self.columnas)])
        return len(filas_llenas)

    def caer(self):
        self.pieza_actual.y += 1
        if self.intersecta():
            self.pieza_actual.y -= 1
            self.fijar_pieza()

    def fijar_pieza(self):
        for i, fila in enumerate(self.pieza_actual.forma):
            for j, celda in enumerate(fila):
                if celda:
                    self.tablero[self.pieza_actual.y + i][
                        self.pieza_actual.x + j
                    ] = self.pieza_actual.color
        self.score += self.limpiar_filas() * 100
        self.pieza_actual = self.nueva_pieza()
        if self.intersecta():
            self.game_over = True

    def mover(self, dx):
        self.pieza_actual.x += dx
        if self.intersecta():
            self.pieza_actual.x -= dx

    def rotar(self):
        forma_rotada = [list(fila) for fila in zip(*self.pieza_actual.forma[::-1])]
        rotacion_anterior = self.pieza_actual.forma
        self.pieza_actual.forma = forma_rotada
        if self.intersecta():
            self.pieza_actual.forma = rotacion_anterior


def dibujar_tablero(pantalla, tetris):
    for i, fila in enumerate(tetris.tablero):
        for j, celda in enumerate(fila):
            if celda:
                pygame.draw.rect(
                    pantalla,
                    celda,
                    (
                        j * TAMANO_BLOQUE,
                        i * TAMANO_BLOQUE,
                        TAMANO_BLOQUE - 1,
                        TAMANO_BLOQUE - 1,
                    ),
                )


def dibujar_pieza(pantalla, pieza):
    for i, fila in enumerate(pieza.forma):
        for j, celda in enumerate(fila):
            if celda:
                pygame.draw.rect(
                    pantalla,
                    pieza.color,
                    (
                        (pieza.x + j) * TAMANO_BLOQUE,
                        (pieza.y + i) * TAMANO_BLOQUE,
                        TAMANO_BLOQUE - 1,
                        TAMANO_BLOQUE - 1,
                    ),
                )


def menu_principal():
    seleccion = 0
    opciones = ["Jugar", "Personalizar Controles", "Salir"]
    while True:
        pantalla.fill(NEGRO)
        texto_titulo = fuente_grande.render("Tetris", True, BLANCO)
        pantalla.blit(
            texto_titulo, (ANCHO // 2 - texto_titulo.get_width() // 2, ALTO // 4)
        )
        for i, opcion in enumerate(opciones):
            color = BLANCO if i == seleccion else GRIS
            texto_opcion = fuente_pequeña.render(opcion, True, color)
            pantalla.blit(
                texto_opcion,
                (ANCHO // 2 - texto_opcion.get_width() // 2, ALTO // 2 + i * 50),
            )
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "salir"
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    seleccion = (seleccion - 1) % len(opciones)
                if evento.key == pygame.K_DOWN:
                    seleccion = (seleccion + 1) % len(opciones)
                if evento.key == pygame.K_RETURN:
                    return opciones[seleccion].lower()
        pygame.display.flip()


def personalizar_controles():
    fuente = pygame.font.Font(None, 36)
    fuente_titulo = pygame.font.Font(None, 46)
    fuente_instrucciones = pygame.font.Font(None, 26)
    controles_orden = ["izquierda", "derecha", "rotar", "bajar", "caer", "pausa"]
    seleccion = 0
    esperando_tecla = False
    while True:
        pantalla.fill(NEGRO)
        texto_titulo = fuente_titulo.render("Personalizar Controles", True, BLANCO)
        pantalla.blit(
            texto_titulo, (ANCHO // 2 - texto_titulo.get_width() // 2, ALTO // 6)
        )
        for i, control in enumerate(controles_orden):
            color = AZUL if i == seleccion else BLANCO
            texto = f"{control.capitalize()}: {pygame.key.name(controles[control])}"
            if esperando_tecla and i == seleccion:
                texto = f"{control.capitalize()}: Presiona una tecla..."
            texto_renderizado = fuente.render(texto, True, color)
            pantalla.blit(
                texto_renderizado,
                (ANCHO // 2 - texto_renderizado.get_width() // 2, ALTO // 3 + i * 50),
            )
        texto_instruccion = fuente_instrucciones.render(
            "Presiona ENTER para personalizar", True, GRIS
        )
        pantalla.blit(
            texto_instruccion,
            (ANCHO // 2 - texto_instruccion.get_width() // 2, ALTO - 100),
        )
        texto_volver = fuente_instrucciones.render(
            "Presiona ESC para volver", True, GRIS
        )
        pantalla.blit(
            texto_volver, (ANCHO // 2 - texto_volver.get_width() // 2, ALTO - 60)
        )
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return
            if evento.type == pygame.KEYDOWN:
                if esperando_tecla:
                    controles[controles_orden[seleccion]] = evento.key
                    esperando_tecla = False
                else:
                    if evento.key == pygame.K_UP:
                        seleccion = (seleccion - 1) % len(controles_orden)
                    elif evento.key == pygame.K_DOWN:
                        seleccion = (seleccion + 1) % len(controles_orden)
                    elif evento.key == pygame.K_RETURN:
                        esperando_tecla = True
                    elif evento.key == pygame.K_ESCAPE:
                        return
        pygame.display.flip()


def pausar():
    fuente = pygame.font.Font(None, 74)
    fuente_pequeña = pygame.font.Font(None, 36)
    seleccion = 0
    opciones = ["Continuar", "Reiniciar", "Menu Principal"]
    while True:
        pantalla.fill(NEGRO)
        texto_pausa = fuente.render("Pausa", True, BLANCO)
        pantalla.blit(
            texto_pausa, (ANCHO // 2 - texto_pausa.get_width() // 2, ALTO // 4)
        )
        for i, opcion in enumerate(opciones):
            color = BLANCO if i == seleccion else GRIS
            texto_opcion = fuente_pequeña.render(opcion, True, color)
            pantalla.blit(
                texto_opcion,
                (ANCHO // 2 - texto_opcion.get_width() // 2, ALTO // 2 + i * 50),
            )
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "salir"
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    seleccion = (seleccion - 1) % len(opciones)
                if evento.key == pygame.K_DOWN:
                    seleccion = (seleccion + 1) % len(opciones)
                if evento.key == pygame.K_RETURN:
                    return opciones[seleccion].lower()
        pygame.display.flip()


def guardar_puntaje_mas_alto(puntaje, ruta_txt, ruta_json):
    with open(ruta_txt, "w") as archivo_txt:
        archivo_txt.write(f"Puntaje más alto: {puntaje}\n")
    datos_puntaje = {"puntaje_mas_alto": puntaje}
    with open(ruta_json, "w") as archivo_json:
        json.dump(datos_puntaje, archivo_json, indent=4)


def juego():
    reloj = pygame.time.Clock()
    tetris = Tetris(FILAS, COLUMNAS)
    caida_rapida = False
    tiempo_caida = 0
    tiempo_caida_rapida = 50
    tiempo_caida_normal = 300
    ruta_txt = "Configuraciones/Puntaje.txt"
    ruta_json = "Configuraciones/Puntaje.json"
    puntaje_mas_alto = 0
    if os.path.exists(ruta_json):
        with open(ruta_json, "r") as archivo_json:
            datos_puntaje = json.load(archivo_json)
            puntaje_mas_alto = datos_puntaje.get("puntaje_mas_alto", 0)
    while not tetris.game_over:
        tiempo_caida += reloj.get_rawtime()
        reloj.tick()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "salir"
            if evento.type == pygame.KEYDOWN:
                if evento.key == controles["izquierda"]:
                    tetris.mover(-1)
                elif evento.key == controles["derecha"]:
                    tetris.mover(1)
                elif evento.key == controles["rotar"]:
                    tetris.rotar()
                elif evento.key == controles["bajar"]:
                    caida_rapida = True
                elif evento.key == controles["caer"]:
                    while not tetris.intersecta():
                        tetris.pieza_actual.y += 1
                    tetris.pieza_actual.y -= 1
                    tetris.fijar_pieza()
                elif evento.key == controles["pausa"]:
                    accion = pausar()
                    if accion == "continuar":
                        continue
                    elif accion == "reiniciar":
                        return "jugar"
                    elif accion == "menu principal":
                        return "menu principal"
                    elif accion == "salir":
                        return "salir"
            if evento.type == pygame.KEYUP:
                if evento.key == controles["bajar"]:
                    caida_rapida = False
        if tiempo_caida > (
            tiempo_caida_rapida if caida_rapida else tiempo_caida_normal
        ):
            tetris.caer()
            tiempo_caida = 0
        pantalla.fill(NEGRO)
        dibujar_tablero(pantalla, tetris)
        dibujar_pieza(pantalla, tetris.pieza_actual)
        texto_score = fuente_mediana.render(f"Puntaje: {tetris.score}", True, BLANCO)
        pantalla.blit(texto_score, (ANCHO_TABLERO + 10, 20))
        texto_max_score = fuente_mediana.render(
            f"Puntaje mas alto: {puntaje_mas_alto}", True, BLANCO
        )
        pantalla.blit(texto_max_score, (ANCHO_TABLERO + 10, 60))
        pygame.display.flip()
    if tetris.score > puntaje_mas_alto:
        guardar_puntaje_mas_alto(tetris.score, ruta_txt, ruta_json)
    pantalla.fill(NEGRO)
    texto_game_over = fuente_grande.render("Fin del juego", True, BLANCO)
    texto_score = fuente_mediana.render(f"Puntaje: {tetris.score}", True, BLANCO)
    pantalla.blit(
        texto_game_over, (ANCHO // 2 - texto_game_over.get_width() // 2, ALTO // 3)
    )
    pantalla.blit(texto_score, (ANCHO // 2 - texto_score.get_width() // 2, ALTO // 2))
    pygame.display.flip()
    pygame.time.wait(2000)
    return "menu principal"


def main():
    while True:
        opcion = menu_principal()
        if opcion == "jugar":
            while juego() == "jugar":
                pass
        elif opcion == "personalizar controles":
            personalizar_controles()
        elif opcion == "salir":
            break


main()
pygame.quit()
