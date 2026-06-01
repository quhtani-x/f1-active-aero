import math
import sys
import pygame

# DISCLAIMER , some comments has been added by ai to explain the code , as the code had a bunch of random comments initially  and a lot of commented code 

W, H = 1000, 640
pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("F1 active aero - AI wing controller")
font = pygame.font.SysFont("consolas", 18)
big = pygame.font.SysFont("consolas", 26, bold=True)
clock = pygame.time.Clock()

# build a track as a closed loop (rounded rectangle) 
def build_track():
    pts = []
    cx, cy = W // 2, H // 2 + 20
    rx, ry = 360, 200      # half width / height of the straights
    corner = 120           
    # walk around the rounded rectangle, sampling points
    for a in range(0, 360, 2):
        rad = math.radians(a)
        # this makes a "squircle"-ish loop with clear straights + corners
        x = cx + (rx) * math.copysign(abs(math.cos(rad)) ** 0.6, math.cos(rad))
        y = cy + (ry) * math.copysign(abs(math.sin(rad)) ** 0.6, math.sin(rad))
        pts.append((x, y))
    return pts

TRACK = build_track()
N = len(TRACK)


def curvature_at(i):
    # estimate how sharp the track bends here using 3 nearby points.
    # bigger number = tighter corner.
    p0 = TRACK[(i - 4) % N]
    p1 = TRACK[i % N]
    p2 = TRACK[(i + 4) % N]
    a1 = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    a2 = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    d = abs(a2 - a1)
    if d > math.pi:
        d = 2 * math.pi - d
    return d


#some physics
pos_i = 0.0          # index along the track
speed = 60.0         # km/h-ish, just a number for feel
wing = 0.5           # 0 = flat (fast/low drag), 1 = full (grippy/high drag)


def target_speed(curv, wing_angle):
    # cornering grip goes up with wing (downforce). straights reward low wing.
    grip = 90 + wing_angle * 160          # max corner speed scales with downforce
    if curv < 0.02:
        # basically a straight: top speed limited by drag (low wing = faster)
        return 340 - wing_angle * 120
    # corner tighter (more curv) = slower, but more wing helps
    return max(70, grip / (curv * 14 + 0.4))


def ai_wing(lookahead_curv):
    # THE CONTROLLER. look at the track a bit ahead and pick the wing angle.
    # sharp corner ahead -> raise wing. open straight ahead -> drop it flat.
    # smooth target between 0 and 1.
    if lookahead_curv < 0.015:
        return 0.05          # straight -> wing flat (DRS open)
    return min(1.0, 0.3 + lookahead_curv * 18)


def lerp(a, b, t):
    return a + (b - a) * t


running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    i = int(pos_i) % N
    curv = curvature_at(i)
    # look around 25 points ahead so the wing moves BEFORE the corner, like a real driver
    look_curv = max(curvature_at((i + k) % N) for k in range(8, 28))

    # ai decides target wing, the actuator moves toward it smoothly (not instant)
    want = ai_wing(look_curv)
    wing = lerp(wing, want, 0.08)

    # accelerate/brake toward the target speed for this point
    tgt = target_speed(curv, wing)
    speed = lerp(speed, tgt, 0.06)

    # advance along the track, faster speed = more points per frame
    pos_i = (pos_i + speed * 0.0009 * N / 60) % N
    
    screen.fill((22, 24, 30))

    # track
    pygame.draw.lines(screen, (70, 74, 88), True, TRACK, 26)
    pygame.draw.lines(screen, (40, 42, 52), True, TRACK, 20)
    # color the track by wing usage just ahead (red = high downforce zones)
    for k in range(0, N, 3):
        c = curvature_at(k)
        col = (200, 80, 80) if c > 0.04 else (90, 160, 110)
        pygame.draw.circle(screen, col, (int(TRACK[k][0]), int(TRACK[k][1])), 2)

    # car
    cx, cy = TRACK[i]
    nxt = TRACK[(i + 3) % N]
    heading = math.atan2(nxt[1] - cy, nxt[0] - cx)
    pygame.draw.circle(screen, (240, 220, 60), (int(cx), int(cy)), 9)
    # little heading line
    pygame.draw.line(screen, (255, 255, 255), (cx, cy),
                     (cx + 18 * math.cos(heading), cy + 18 * math.sin(heading)), 3)

    #hud
    mode = "STRAIGHT  (DRS open)" if look_curv < 0.015 else "CORNER  (downforce)"
    screen.blit(big.render("F1 ACTIVE AERO", True, (255, 255, 255)), (24, 18))
    screen.blit(font.render(f"mode:  {mode}", True, (200, 220, 255)), (24, 60))
    screen.blit(font.render(f"speed: {speed:5.0f} km/h", True, (220, 220, 220)), (24, 86))

    # wing bar
    screen.blit(font.render("wing angle", True, (200, 200, 200)), (24, 120))
    pygame.draw.rect(screen, (60, 60, 70), (24, 144, 220, 22), border_radius=6)
    pygame.draw.rect(screen, (240, 120, 80), (24, 144, int(220 * wing), 22), border_radius=6)
    screen.blit(font.render(f"{wing*100:3.0f}%", True, (255, 255, 255)), (252, 145))

    wx, wy = 130, 230
    angle = wing * 0.9  
    dx, dy = 40 * math.cos(angle), 40 * math.sin(angle)
    pygame.draw.line(screen, (180, 180, 200), (wx - dx, wy - dy), (wx + dx, wy + dy), 8)
    screen.blit(font.render("rear wing", True, (150, 150, 160)), (wx - 40, wy + 24))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
