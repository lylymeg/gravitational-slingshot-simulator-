import pygame
import math
import random
import sys

pygame.init()

# Dimensions de la fenêtre
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Slingshot Space Simulator — Niveaux Procéduraux")
clock = pygame.time.Clock()

# Couleurs (Thème Espace Profond & Néon)
DARK_BG = (10, 12, 18)
WHITE = (255, 255, 255)
GRAY = (140, 150, 170)
PLANET_COLORS = [
    (0, 162, 255),  # Bleu cyan
    (255, 150, 0),  # Orange
    (180, 100, 255),# Violet
    (0, 255, 200)   # Turquoise
]
BLACKHOLE_COLOR = (255, 50, 80) # Rouge / Violet intense
TARGET_COLOR = (0, 255, 157)    # Vert néon
SHIP_COLOR = (255, 230, 0)      # Jaune doré

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
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.trail = []
        self.active = False

# Variables de niveau
level = 1
score = 0
bodies = []
target = {}
ship = None
aiming = False
aim_start = (0, 0)
level_status = "READY"  # READY, FLYING, WON, LOST

def generate_new_system():
    """Génère un tout nouveau système stellaire procédural avec des planètes et obstacles aléatoires."""
    global bodies, target, ship, level_status, aiming
    
    bodies = []
    level_status = "READY"
    aiming = False

    # 1. Position du vaisseau (dans le coin inférieur gauche)
    ship_x = random.randint(80, 180)
    ship_y = random.randint(HEIGHT - 180, HEIGHT - 80)
    ship = Spaceship(ship_x, ship_y)

    # 2. Position de la cible (dans le coin supérieur droit)
    target_x = random.randint(WIDTH - 200, WIDTH - 80)
    target_y = random.randint(80, 200)
    target = {"x": target_x, "y": target_y, "radius": random.randint(20, 26)}

    # 3. Génération de 2 à 5 planètes/obstacles aléatoires entre le vaisseau et la cible
    num_bodies = random.randint(2, 4)
    for _ in range(num_bodies):
        attempts = 0
        while attempts < 100:
            bx = random.randint(180, WIDTH - 180)
            by = random.randint(100, HEIGHT - 100)
            
            # Vérifier que l'astre ne chevauche ni le vaisseau ni la cible
            dist_ship = math.hypot(bx - ship_x, by - ship_y)
            dist_target = math.hypot(bx - target_x, by - target_y)
            
            if dist_ship > 120 and dist_target > 100:
                is_blackhole = (random.random() < 0.25)  # 25% de chance d'être un trou noir
                radius = random.randint(18, 32)
                mass = radius * random.randint(120, 220)
                color = BLACKHOLE_COLOR if is_blackhole else random.choice(PLANET_COLORS)
                
                bodies.append(CelestialBody(bx, by, mass, radius, color, is_blackhole))
                break
            attempts += 1

generate_new_system()

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if level_status == "READY":
                # Vérifier si le clic est proche du vaisseau
                if math.hypot(mouse_pos[0] - ship.x, mouse_pos[1] - ship.y) < 40:
                    aiming = True
                    aim_start = (ship.x, ship.y)
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if aiming:
                aiming = False
                dx = ship.x - mouse_pos[0]
                dy = ship.y - mouse_pos[1]
                ship.vx = dx * 0.08
                ship.vy = dy * 0.08
                ship.active = True
                level_status = "FLYING"
                
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                generate_new_system()  # Générer directement un nouveau système

    # --- PHYSIQUE ET GRAVITÉ ---
    if ship.active and level_status == "FLYING":
        G = 1.2
        for b in bodies:
            dx = b.x - ship.x
            dy = b.y - ship.y
            dist_sq = dx**2 + dy**2 + 250  # Adoucissement
            dist = math.sqrt(dist_sq)
            
            # Force d'attraction
            force = (G * b.mass) / dist_sq
            ship.vx += force * (dx / dist)
            ship.vy += force * (dy / dist)
            
            # Collision avec un obstacle
            if dist < b.radius + 4:
                level_status = "LOST"
                ship.active = False
                break

        # Mise à jour position
        ship.x += ship.vx
        ship.y += ship.vy

        # Trajectoire visuelle
        ship.trail.append((int(ship.x), int(ship.y)))
        if len(ship.trail) > 120:
            ship.trail.pop(0)

        # Sortie de l'écran (Perdu)
        if not (-50 <= ship.x <= WIDTH + 50 and -50 <= ship.y <= HEIGHT + 50):
            level_status = "LOST"
            ship.active = False

        # Victoire (Atteindre la cible)
        dist_target = math.hypot(ship.x - target["x"], ship.y - target["y"])
        if dist_target < target["radius"] + 8:
            score += 100 + int(len(ship.trail) * 0.5)
            level_status = "WON"
            ship.active = False

    screen.fill(DARK_BG)

    # 1. Ligne de visée
    if aiming:
        pygame.draw.line(screen, WHITE, aim_start, mouse_pos, 2)
        pred_vx = (aim_start[0] - mouse_pos[0]) * 0.08
        pred_vy = (aim_start[1] - mouse_pos[1]) * 0.08
        px, py = aim_start
        for _ in range(15):
            px += pred_vx
            py += pred_vy
            pygame.draw.circle(screen, GRAY, (int(px), int(py)), 2)

    # 2. Sillage du vaisseau
    if len(ship.trail) > 1:
        pygame.draw.aalines(screen, (80, 110, 160), False, ship.trail)

    # 3. Dessin de la Cible
    pygame.draw.circle(screen, TARGET_COLOR, (target["x"], target["y"]), target["radius"], 3)
    pygame.draw.circle(screen, (0, 120, 90), (target["x"], target["y"]), target["radius"] - 6)

    # 4. Dessin des corps célestes
    for b in bodies:
        pygame.draw.circle(screen, b.color, (int(b.x), int(b.y)), b.radius)
        border_color = (255, 100, 100) if b.is_blackhole else WHITE
        pygame.draw.circle(screen, border_color, (int(b.x), int(b.y)), b.radius, 1 if not b.is_blackhole else 2)

    # 5. Dessin du Vaisseau
    pygame.draw.circle(screen, SHIP_COLOR, (int(ship.x), int(ship.y)), 6)

    # 6. En-tête HUD et Messages
    title_txt = font_medium.render("SLINGSHOT SPACE SIMULATOR", True, WHITE)
    screen.blit(title_txt, (WIDTH // 2 - title_txt.get_width() // 2, 15))

    score_txt = font_small.render(f"Score : {score} | Niveau : {level}", True, TARGET_COLOR)
    screen.blit(score_txt, (30, 20))

    if level_status == "READY":
        inst_txt = font_small.render("Clique & Glisse sur le vaisseau pour viser et propulser | R : Nouveau système", True, GRAY)
        screen.blit(inst_txt, (WIDTH // 2 - inst_txt.get_width() // 2, 48))

    elif level_status == "WON":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        won_txt = font_medium.render("SUCCÈS ! Cible atteinte !", True, TARGET_COLOR)
        next_txt = font_small.render("Chargement d'un nouveau système stellaire...", True, WHITE)
        screen.blit(won_txt, (WIDTH // 2 - won_txt.get_width() // 2, HEIGHT // 2 - 20))
        screen.blit(next_txt, (WIDTH // 2 - next_txt.get_width() // 2, HEIGHT // 2 + 15))

        pygame.display.flip()
        pygame.time.delay(1600)  # Pause avant de générer le prochain niveau
        level += 1
        generate_new_system()
        continue

    elif level_status == "LOST":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        loss_txt = font_medium.render("CRASH OU ÉCHAPPE !", True, BLACKHOLE_COLOR)
        next_txt = font_small.render("Génération d'une nouvelle carte en cours...", True, WHITE)
        screen.blit(loss_txt, (WIDTH // 2 - loss_txt.get_width() // 2, HEIGHT // 2 - 20))
        screen.blit(next_txt, (WIDTH // 2 - next_txt.get_width() // 2, HEIGHT // 2 + 15))

        pygame.display.flip()
        pygame.time.delay(1600)  # Pause avant de régénérer après un crash
        generate_new_system()
        continue

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()