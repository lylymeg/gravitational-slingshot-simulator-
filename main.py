import pygame
import math
import random
import sys

pygame.init()

# Dimensions de la fenêtre
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Slingshot Space Simulator")
clock = pygame.time.Clock()

# Couleurs (Thème Espace Profond & Néon)
DARK_BG = (10, 12, 18)
WHITE = (255, 255, 255)
GRAY = (140, 150, 170)
PLANET_COLOR = (0, 162, 255)  # Bleu cyan
BLACKHOLE_COLOR = (180, 50, 255) # Violet sombre
TARGET_COLOR = (0, 255, 157)  # Vert néon
SHIP_COLOR = (255, 230, 0)    # Jaune doré

# Polices
font_medium = pygame.font.SysFont("Arial", 20, bold=True)
font_small = pygame.font.SysFont("Arial", 15)

class CelestialBody:
    def __init__(self, x, y, mass, radius, color, is_blackhole=False):
        self.x = x
        self.y = y
        self.mass = mass
        self.radius = radius
        self.color = color
        self.is_blackhole = is_blackhole

class Spaceship:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.trail = []
        self.active = False

# Éléments du niveau
bodies = [
    CelestialBody(350, 250, 3000, 24, PLANET_COLOR),
    CelestialBody(600, 420, 5000, 30, PLANET_COLOR),
    CelestialBody(500, 180, 8000, 20, BLACKHOLE_COLOR, is_blackhole=True)
]

target = {"x": 780, "y": 120, "radius": 22}
ship = Spaceship(150, 500, 0, 0)

aiming = False
aim_start = (150, 500)
level_status = "READY"  # READY, FLYING, WON, LOST

def reset_ship():
    global ship, level_status
    ship = Spaceship(150, 500, 0, 0)
    level_status = "READY"

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if level_status == "READY":
                aiming = True
                aim_start = (ship.x, ship.y)
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if aiming:
                aiming = False
                # Calculer le vecteur de poussée en fonction de la visée
                dx = ship.x - mouse_pos[0]
                dy = ship.y - mouse_pos[1]
                ship.vx = dx * 0.08
                ship.vy = dy * 0.08
                ship.active = True
                level_status = "FLYING"
                
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_ship()
            elif event.key == pygame.K_c:
                # Ajouter une planète aléatoire au clic ou réinitialiser
                reset_ship()

    # --- PHYSIQUE DE LA GRAVITÉ (Si le vaisseau est en vol) ---
    if ship.active and level_status == "FLYING":
        G = 1.2
        for b in bodies:
            dx = b.x - ship.x
            dy = b.y - ship.y
            dist_sq = dx**2 + dy**2 + 300 # Adoucissement
            dist = math.sqrt(dist_sq)
            
            # Attraction gravitationnelle
            force = (G * b.mass) / dist_sq
            ship.vx += force * (dx / dist)
            ship.vy += force * (dy / dist)
            
            # Collision avec une planète ou un trou noir
            if dist < b.radius + 5:
                if b.is_blackhole:
                    level_status = "LOST"
                    ship.active = False
                else:
                    level_status = "LOST" # Crash sur la planète
                    ship.active = False

        # Mettre à jour la position du vaisseau
        ship.x += ship.vx
        ship.y += ship.vy

        # Enregistrer la trajectoire
        ship.trail.append((int(ship.x), int(ship.y)))
        if len(ship.trail) > 100:
            ship.trail.pop(0)

        # Vérifier si le vaisseau sort de l'écran
        if not (0 <= ship.x <= WIDTH and 0 <= ship.y <= HEIGHT):
            level_status = "LOST"
            ship.active = False

        # Vérifier si le vaisseau atteint la cible
        dist_target = math.hypot(ship.x - target["x"], ship.y - target["y"])
        if dist_target < target["radius"] + 8:
            level_status = "WON"
            ship.active = False

    screen.fill(DARK_BG)

    # 1. Dessiner les trajectoires / lignes de visée
    if aiming:
        pygame.draw.line(screen, WHITE, aim_start, mouse_pos, 2)
        # Aperçu de la direction opposée (trajectoire estimée)
        pred_vx = (aim_start[0] - mouse_pos[0]) * 0.08
        pred_vy = (aim_start[1] - mouse_pos[1]) * 0.08
        px, py = aim_start
        for _ in range(15):
            px += pred_vx
            py += pred_vy
            pygame.draw.circle(screen, GRAY, (int(px), int(py)), 3)

    if len(ship.trail) > 1:
        pygame.draw.aalines(screen, (80, 100, 140), False, ship.trail)

    # 2. Dessiner la Cible
    pygame.draw.circle(screen, TARGET_COLOR, (target["x"], target["y"]), target["radius"], 3)
    pygame.draw.circle(screen, (0, 100, 80), (target["x"], target["y"]), target["radius"] - 6)

    # 3. Dessiner les corps célestes (Planètes & Trous noirs)
    for b in bodies:
        pygame.draw.circle(screen, b.color, (b.x, b.y), b.radius)
        # Effet lumineux autour des planètes
        pygame.draw.circle(screen, WHITE, (b.x, b.y), b.radius, 1)

    # 4. Dessiner le Vaisseau
    pygame.draw.circle(screen, SHIP_COLOR, (int(ship.x), int(ship.y)), 6)

    # 5. HUD et Messages
    title_txt = font_medium.render("SLINGSHOT SPACE SIMULATOR", True, WHITE)
    screen.blit(title_txt, (WIDTH // 2 - title_txt.get_width() // 2, 20))

    if level_status == "READY":
        inst_txt = font_small.render("Clique & Glisse depuis le vaisseau pour viser et propulser | R : Réinitialiser", True, GRAY)
        screen.blit(inst_txt, (WIDTH // 2 - inst_txt.get_width() // 2, 55))
    elif level_status == "WON":
        win_txt = font_medium.render("SUCCÈS ! Cible atteinte avec l'effet de fronde ! (R pour rejouer)", True, TARGET_COLOR)
        screen.blit(win_txt, (WIDTH // 2 - win_txt.get_width() // 2, 55))
    elif level_status == "LOST":
        loss_txt = font_medium.render("CRASH / PERDU ! Appuie sur R pour réessayer", True, (255, 75, 75))
        screen.blit(loss_txt, (WIDTH // 2 - loss_txt.get_width() // 2, 55))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()