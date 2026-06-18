import sys
import json
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import pygame
from pygame import *

# --- PERSISTENCIA DE DATOS (TIENDA) ---
CONFIG_FILE = "progreso_tienda.json"

CONFIG_DEFECTO = {
    "monedas": 100,
    "raqueta_p1": "Clásica",
    "raqueta_p2": "Clásica",
    "compradas": ["Clásica"]
}

OPCIONES_RAQUETAS = {
    "Clásica": {"img": "raqueta1.png", "width": 70, "height": 100, "speed": 5, "precio": 0},
    "Veloz": {"img": "raqueta_fast.png", "width": 60, "height": 90, "speed": 8, "precio": 50},
    "Gigante": {"img": "raqueta_big.png", "width": 80, "height": 150, "speed": 4, "precio": 75}
}

def cargar_progreso():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            return CONFIG_DEFECTO
    return CONFIG_DEFECTO

def guardar_progreso(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


# --- CÓDIGO DEL JUEGO (PYGAME) ---
def iniciar_juego_pygame(config_progreso):
    pygame.init()
    font.init()
    mixer.init()

    ANCHO, ALTO = 750, 550
    FONDO = 'fondo.png'
    BLANCO = (255, 255, 255) # Corregido color blanco visible para el texto
    NEGRO = (0, 0, 0)
    FPS = 120

    # Obtener características de la tienda
    p1_stats = OPCIONES_RAQUETAS[config_progreso["raqueta_p1"]]
    p2_stats = OPCIONES_RAQUETAS[config_progreso["raqueta_p2"]]

    screen = display.set_mode((ANCHO, ALTO))
    display.set_caption('PING_PONG')
    
    # Manejo de error por si no existe el fondo
    try:
        fondo = transform.scale(image.load(FONDO), (ANCHO, ALTO))
    except:
        fondo = Surface((ANCHO, ALTO))
        fondo.fill((30, 30, 30))

    try:
        font_1 = font.Font('fuente.ttf', 50)
        font_pausa = font.Font('fuente.ttf', 60)
    except:
        font_1 = font.SysFont('Arial', 50)
        font_pausa = font.SysFont('Arial', 60)

    try:
        mixer.music.load('bgm1.mp3')
        mixer.music.play(-1)
    except:
        pass

    class GameSprite(sprite.Sprite):
        def __init__(self, img, cor_x, cor_y, width, height, speed=0):
            super().__init__()
            self.width = width
            self.height = height
            try:
                self.image = transform.scale(image.load(img), (self.width, self.height))
            except:
                self.image = Surface((self.width, self.height))
                self.image.fill(BLANCO)
            self.rect = self.image.get_rect()
            self.rect.x = cor_x
            self.rect.y = cor_y
            self.speed = speed

        def reset(self):
            screen.blit(self.image, (self.rect.x, self.rect.y))

    class Player(GameSprite):
        def update_1(self):
            llaves = key.get_pressed()
            if llaves[K_w] and self.rect.y > 0:
                self.rect.y -= self.speed
            if llaves[K_s] and self.rect.y < ALTO - self.height:
                self.rect.y += self.speed

        def update_2(self):
            llaves = key.get_pressed()
            if llaves[K_UP] and self.rect.y > 0:
                self.rect.y -= self.speed
            if llaves[K_DOWN] and self.rect.y < ALTO - self.height:
                self.rect.y += self.speed

    # Inicializar jugadores con los datos cargados de la tienda
    player_1 = Player(p1_stats["img"], 5, 250, p1_stats["width"], p1_stats["height"], p1_stats["speed"])
    player_2 = Player(p2_stats["img"], ANCHO - (p2_stats["width"] + 5), 250, p2_stats["width"], p2_stats["height"], p2_stats["speed"])
    pelota = GameSprite('pelota.png', 150, 50, 40, 40, 1)

    speed_x, speed_y = 5, 5
    clok = time.Clock()
    finish = False
    run = True
    pausado = False

    while run:
        for e in event.get():
            if e.type == QUIT:
                run = False
            if e.type == KEYDOWN: 
                if e.key == K_r:
                    finish = False
                    pelota.rect.x = 150 
                    pelota.rect.y = 50
                    speed_x, speed_y = 5, 5
                    try: mixer.music.play(-1) 
                    except: pass
                if e.key == K_p: # Tecla P para Pausar/Despausar
                    if not finish:
                        pausado = not pausado

        if not finish and not pausado:
            screen.blit(fondo, (0, 0))
            player_1.reset()
            player_1.update_1()
            player_2.reset()
            player_2.update_2()
            pelota.reset()

            pelota.rect.x += speed_x
            pelota.rect.y += speed_y

            if pelota.rect.y >= ALTO - pelota.height or pelota.rect.y <= 0:
                speed_y *= -1
            
            if sprite.collide_rect(pelota, player_1) or sprite.collide_rect(pelota, player_2):
                speed_x *= -1

            if pelota.rect.x > ANCHO:
                win_p1 = font_1.render('GANADOR JUGADOR 1', 1, BLANCO)
                screen.blit(win_p1, (100, 250))
                finish = True

            if pelota.rect.x < -50:
                win_p2 = font_1.render('GANADOR JUGADOR 2', 1, BLANCO)
                screen.blit(win_p2, (100, 250))
                finish = True
                
        elif pausado and not finish:
            # Renderizado de pantalla de pausa
            texto_pausa = font_pausa.render("JUEGO PAUSADO", True, BLANCO)
            subtexto_pausa = font_1.render("Presiona 'P' para continuar", True, BLANCO)
            screen.blit(texto_pausa, (160, 200))
            screen.blit(subtexto_pausa, (110, 280))

        if finish:
            try: mixer.music.stop()
            except: pass
       
        display.update()
        clok.tick(FPS)

    pygame.quit()


# --- INTERFAZ GRÁFICA (PYQT5) ---
class VentanaTienda(QWidget):
    def __init__(self, menu_principal):
        super().__init__()
        self.menu_principal = menu_principal
        self.progreso = cargar_progreso()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Tienda de Raquetas')
        self.resize(400, 350)
        layout = QVBoxLayout()

        self.lbl_monedas = QLabel(f"Monedas Disponibles: {self.progreso['monedas']}")
        self.lbl_monedas.setFont(QFont('Arial', 12, QFont.Bold))
        layout.addWidget(self.lbl_monedas, alignment=Qt.AlignCenter)

        # Configuración de Selección / Compra
        layout.addWidget(QLabel("Selecciona o compra raquetas para los jugadores:"))
        
        # Jugador 1
        layout.addWidget(QLabel("<b>Jugador 1 (W/S):</b>"))
        self.cb_p1 = QComboBox()
        layout.addWidget(self.cb_p1)

        # Jugador 2
        layout.addWidget(QLabel("<b>Jugador 2 (Flechas):</b>"))
        self.cb_p2 = QComboBox()
        layout.addWidget(self.cb_p2)

        self.actualizar_combos()

        # Botón para Comprar/Equipar las raquetas seleccionadas
        btn_guardar = QPushButton("Confirmar y Equipar")
        btn_guardar.clicked.connect(self.guardar_seleccion)
        layout.addWidget(btn_guardar)

        # Sección de simulación de compras (Para desbloquear nuevas raquetas)
        layout.addWidget(QLabel("<b>Desbloquear Nuevas Raquetas:</b>"))
        self.cb_tienda = QComboBox()
        for nombre, stats in OPCIONES_RAQUETAS.items():
            if nombre not in self.progreso["compradas"]:
                self.cb_tienda.addItem(f"{nombre} (${stats['precio']})", nombre)
        
        if self.cb_tienda.count() == 0:
            self.cb_tienda.addItem("¡Todo comprado!")
            self.cb_tienda.setEnabled(False)

        layout.addWidget(self.cb_tienda)

        self.btn_comprar = QPushButton("Comprar Seleccionada")
        self.btn_comprar.clicked.connect(self.comprar_raqueta)
        if self.cb_tienda.count() == 0 or not self.cb_tienda.isEnabled():
            self.btn_comprar.setEnabled(False)
        layout.addWidget(self.btn_comprar)

        # Botón de Regreso
        btn_regresar = QPushButton('Regresar al Menú')
        btn_regresar.clicked.connect(self.regresar)
        layout.addWidget(btn_regresar)

        self.setLayout(layout)

    def actualizar_combos(self):
        self.cb_p1.clear()
        self.cb_p2.clear()
        for item in self.progreso["compradas"]:
            self.cb_p1.addItem(item)
            self.cb_p2.addItem(item)
        
        # Posicionar en los actuales equipados
        self.cb_p1.setCurrentText(self.progreso["raqueta_p1"])
        self.cb_p2.setCurrentText(self.progreso["raqueta_p2"])

    def comprar_raqueta(self):
        nombre_raqueta = self.cb_tienda.currentData()
        if not nombre_raqueta:
            return
        
        precio = OPCIONES_RAQUETAS[nombre_raqueta]["precio"]
        if self.progreso["monedas"] >= precio:
            self.progreso["monedas"] -= precio
            self.progreso["compradas"].append(nombre_raqueta)
            
            # Actualizar UI
            self.lbl_monedas.setText(f"Monedas Disponibles: {self.progreso['monedas']}")
            self.actualizar_combos()
            
            # Quitar de la lista de compra
            idx = self.cb_tienda.currentIndex()
            self.cb_tienda.removeItem(idx)
            if self.cb_tienda.count() == 0:
                self.cb_tienda.addItem("¡Todo comprado!")
                self.cb_tienda.setEnabled(False)
                self.btn_comprar.setEnabled(False)
                
            guardar_progreso(self.progreso)

    def guardar_seleccion(self):
        self.progreso["raqueta_p1"] = self.cb_p1.currentText()
        self.progreso["raqueta_p2"] = self.cb_p2.currentText()
        guardar_progreso(self.progreso)

    def regresar(self):
        # Al salir, nos aseguramos de guardar todo de forma automática
        self.guardar_seleccion()
        self.menu_principal.show()
        self.close()


class InicioJuego(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Ping Pong - Menú Principal')
        self.resize(350, 250)

        layout = QVBoxLayout()

        titulo = QLabel("PONG ULTRA")
        titulo.setFont(QFont('Arial', 24, QFont.Bold))
        layout.addWidget(titulo, alignment=Qt.AlignCenter)

        btn_jugar = QPushButton('JUGAR')
        btn_jugar.setFont(QFont('Arial', 14))
        btn_jugar.clicked.connect(self.lanzar_juego)
        layout.addWidget(btn_jugar)

        btn_tienda = QPushButton('TIENDA')
        btn_tienda.setFont(QFont('Arial', 14))
        btn_tienda.clicked.connect(self.abrir_tienda)
        layout.addWidget(btn_tienda)

        self.setLayout(layout)

    def lanzar_juego(self):
        self.hide() # Oculta PyQt5
        progreso_actual = cargar_progreso()
        iniciar_juego_pygame(progreso_actual) # Lanza Pygame
        self.show() # Muestra PyQt5 de nuevo al cerrar Pygame

    def abrir_tienda(self):
        self.tienda = VentanaTienda(self)
        self.tienda.show()
        self.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    menu = InicioJuego()
    menu.show()
    sys.exit(app.exec_())
