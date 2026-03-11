"""
Gravity Simulator — Correct Spacetime Fabric
=============================================
Constants  (NIST CODATA 2018 / IAU 2015 / IAU 2012):
  G   = 6.67430e-11 m³ kg⁻¹ s⁻²
  c   = 2.99792458e8 m/s
  AU  = 1.495978707e11 m
  GM☉ = 1.32712440018e20 m³/s²
  Orbital elements: J2000 epoch, NASA JPL Horizons
  Integrator: 4th-order Yoshida symplectic

Spacetime fabric — smooth Lorentzian gravity wells:
  z(d) = peak / sqrt(1 + (d/w)²)
  Deepest at body centre, falls off as 1/d far away.
  Correctly oriented: z < 0 pushes grid nodes AWAY from camera,
  appearing as downward funnel wells in the tilted 3-D view.
  Grid computed with numpy for 60 fps.

Controls:  B = bird's-eye   T = 3-D tilt   SPACE = pause   ESC = quit
"""

import pygame, math, sys
import numpy as np

pygame.init()

W, H = 1200 , 900
WIN  = pygame.display.set_mode((W, H))
pygame.display.set_caption("Gravity Simulator — Spacetime Fabric")

BG      = (3, 5, 12)
WHITE   = (255, 255, 255)
FONT    = pygame.font.SysFont("arial", 14)
FONT_SM = pygame.font.SysFont("arial", 11)
FONT_LG = pygame.font.SysFont("arial", 17, bold=True)

# ── Physical constants ────────────────────────────────────────────────────────
G        = 6.67430e-11
c        = 2.99792458e8
AU       = 1.495978707e11
GM_SUN   = 1.32712440018e20
M_SUN    = GM_SUN / G
DAY      = 86400.0
SCALE    = 280.0 / AU          # px / m

# ── Yoshida 4th-order symplectic ──────────────────────────────────────────────
_cbrt2 = 2.0**(1.0/3.0)
_W0 = -_cbrt2 / (2.0 - _cbrt2)
_W1 =  1.0    / (2.0 - _cbrt2)
_YC = [_W1/2, (_W0+_W1)/2, (_W0+_W1)/2, _W1/2]
_YD = [_W1,    _W0,         _W1,          0.0  ]

# ── View modes ────────────────────────────────────────────────────────────────
BIRD = 0
TILT = 1

# ── 3-D projection ───────────────────────────────────────────────────────────
PITCH    = math.radians(58)
_COSP    = math.cos(PITCH)
_SINP    = math.sin(PITCH)
CAM_DIST = 3000.0          

def _proj3d_arrays(xp, yp, zp):
    """Vectorised 3-D projection (numpy). zp in pixels; zp<0 = away from cam = well."""
    y2  =  yp * _COSP - zp * _SINP
    z2  =  yp * _SINP + zp * _COSP
    w   =  CAM_DIST / (CAM_DIST + z2)
    return xp * w + W/2,  y2 * w + H/2,  w

def _proj_single(xp, yp, zp=0.0):
    """Single-point 3-D projection."""
    y2 = yp*_COSP - zp*_SINP
    z2 = yp*_SINP + zp*_COSP
    w  = CAM_DIST / (CAM_DIST + z2)
    return xp*w + W/2,  y2*w + H/2,  w

def proj(xm, ym, view):
    """World metres → screen (sx, sy, depth_w)."""
    xp = xm * SCALE;  yp = ym * SCALE
    if view == BIRD:
        return xp + W/2,  yp + H/2,  1.0
    return _proj_single(xp, yp)

# ── Grid — world-space uniform lattice ───────────────────────────────────────
EXTENT_AU = 5.5           # ± AU
STEP_AU   = 0.09          # node spacing — fine enough to show planet dents
_N        = int(2 * EXTENT_AU / STEP_AU) + 1
_xs       = np.linspace(-EXTENT_AU * AU, EXTENT_AU * AU, _N)
_GX, _GY  = np.meshgrid(_xs, _xs)    # (_N,_N) world-metre grids
_GXP      = _GX * SCALE              # pixel-space (static)
_GYP      = _GY * SCALE

# ── Well parameters: (peak_px, width_m) per body name ────────────────────────
# Lorentzian: z(d) = peak / sqrt(1 + (d/width)²)
# Peak heights are tuned so every planet makes a visible dent.
# Widths scale with body size / Hill sphere — controls lateral spread.
_WELLS = {
    "Sun":      (210, 0.90 * AU),
    "Jupiter":  ( 88, 0.32 * AU),
    "Earth":    ( 60, 0.14 * AU),
    "Venus":    ( 56, 0.13 * AU),
    "Mars":     ( 44, 0.10 * AU),
    "Mercury":  ( 38.75, 0.08 * AU),
}

# ── Build grid ────────────────────────────────────────────────────────────────
def build_grid(bodies, view):
    """Returns (sx_arr, sy_arr, z_arr) all shape (_N,_N)."""
    z = np.zeros((_N, _N))
    for p in bodies:
        pk, wd = _WELLS[p.name]
        dx = _GX - p.x;  dy = _GY - p.y
        z += pk / np.sqrt(1.0 + (dx*dx + dy*dy) / (wd*wd))

    if view == BIRD:
        return _GXP + W/2,  _GYP + H/2,  z
    else:
        sx, sy, _ = _proj3d_arrays(_GXP, _GYP, -z)   # -z = away from camera
        return sx, sy, z

# ── Draw grid ────────────────────────────────────────────────────────────────
def draw_spacetime(win, bodies, view):
    sx, sy, z = build_grid(bodies, view)
    max_z = max(float(z.max()), 1.0)

    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    t_arr = np.clip((z / max_z) ** 0.42, 0.0, 1.0)    # gamma compress

    N = _N
    for yi in range(N - 1):
        for xi in range(N - 1):
            t  = float(t_arr[yi, xi])
            rc = int(  6 + t * 218)
            gc = int( 42 + t * 192)
            bc = int(162 + t *  93)
            ac = int( 28 + t * 218)
            col = (rc, gc, bc, ac)
            lw  = 2 if t > 0.42 else 1

            x0 = int(sx[yi,   xi  ]);  y0 = int(sy[yi,   xi  ])
            x1 = int(sx[yi,   xi+1]);  y1 = int(sy[yi,   xi+1])
            x2 = int(sx[yi+1, xi  ]);  y2 = int(sy[yi+1, xi  ])

            if -500 < x0 < W+500 and -400 < y0 < H+700:
                pygame.draw.line(surf, col, (x0,y0), (x1,y1), lw)
                pygame.draw.line(surf, col, (x0,y0), (x2,y2), lw)

    win.blit(surf, (0, 0))

# ── Trail ─────────────────────────────────────────────────────────────────────
TRAIL_MAX  = 320
TRAIL_SHOW = TRAIL_MAX // 2

# ── Planet ────────────────────────────────────────────────────────────────────
class Planet:
    def __init__(self, name, x, y, vx, vy, mass, gm, rpx, color, is_sun=False):
        self.name    = name
        self.x,  self.y  = float(x), float(y)
        self.vx, self.vy = float(vx), float(vy)
        self.mass    = mass
        self.gm      = gm
        self.rpx     = rpx
        self.color   = color
        self.is_sun  = is_sun
        self.dist_sun = 0.0
        self.trail: list = []

    def _accel(self, x, y, others):
        ax = ay = 0.0
        for p in others:
            if p is self: continue
            dx = p.x-x; dy = p.y-y
            r2 = dx*dx+dy*dy; r = math.sqrt(r2)
            f  = p.gm/(r2*r)
            ax += f*dx; ay += f*dy
        return ax, ay

    def yoshida(self, others, dt):
        x, y   = self.x,  self.y
        vx, vy = self.vx, self.vy
        for ci, di in zip(_YC, _YD):
            x  += ci*vx*dt;  y  += ci*vy*dt
            if di:
                ax, ay = self._accel(x, y, others)
                vx += di*ax*dt;  vy += di*ay*dt
        self.x, self.y   = x,  y
        self.vx, self.vy = vx, vy

    def draw(self, win, view):
        sx, sy, dw = proj(self.x, self.y, view)
        dr = max(2, int(self.rpx * (dw if view==TILT else 1.0)))

        # glowing half-trail
        if len(self.trail) > 4:
            tw   = self.trail[-TRAIL_SHOW:]
            tpts = [proj(wx,wy,view) for wx,wy in tw]
            n    = len(tpts)
            gs   = pygame.Surface((W,H), pygame.SRCALPHA)
            for i in range(n-1):
                t  = i/max(1,n-2)
                x1,y1,_ = tpts[i];  x2,y2,_ = tpts[i+1]
                r,g,b = self.color
                for lw,af in ((7,0.08),(3,0.28),(1,0.86)):
                    pygame.draw.line(gs,(r,g,b,int(255*t*af)),
                                    (int(x1),int(y1)),(int(x2),int(y2)),lw)
            win.blit(gs,(0,0))

        # glow halo
        for i in range(3,0,-1):
            gr = dr+i*4
            gs = pygame.Surface((gr*2,gr*2),pygame.SRCALPHA)
            r,g,b = self.color
            pygame.draw.circle(gs,(r,g,b,int(255/(i*2.5+1))),(gr,gr),gr)
            win.blit(gs,(int(sx-gr),int(sy-gr)))

        pygame.draw.circle(win,self.color,(int(sx),int(sy)),dr)

        if not self.is_sun:
            hx=int(sx-dr*0.3); hy=int(sy-dr*0.3)
            pygame.draw.circle(win,WHITE,(hx,hy),max(1,int(dr*0.22)))
            dtxt = FONT_SM.render(f"{self.dist_sun/AU:.3f} AU",1,(155,155,155))
            win.blit(dtxt,(sx-dtxt.get_width()//2,sy+dr+18))

        nt = FONT.render(self.name,1,self.color)
        win.blit(nt,(sx-nt.get_width()//2,sy+dr+2))

# ── Solar system factory ──────────────────────────────────────────────────────
def make_system():
    """
    All planets start at PERIHELION on the +x axis.
    Correct real-space orbit is counter-clockwise (CCW) when viewed from
    the north ecliptic pole.  In pygame coordinates (+y downward) CCW
    real-space = clockwise on screen.
    For a planet at (r_peri, 0), the velocity that produces CCW real-space
    orbit is purely in the -y direction:  vx=0, vy = -v_perihelion.
    This is derived from the angular momentum condition:
      L_z = x * vy - y * vx  must be < 0 in pygame coords for CCW real orbit.
    All five planets are initialised identically (same axis, same sign) so
    they all orbit in the same direction, as observed.
    """
    def vp(a_m, e):
        # vis-viva at perihelion: v = sqrt(GM*(1+e) / (a*(1-e)))
        return math.sqrt(GM_SUN * (1 + e) / (a_m * (1 - e)))

    sun = Planet("Sun", 0, 0, 0, 0, M_SUN, GM_SUN, 16, (255,240,80), is_sun=True)

    #  name        a_AU         e           mass_kg     GM_m3s2   px  colour
    data = [
      ("Mercury", 0.38709893, 0.20563069, 3.3011e23, 2.2032e13,  5, (180,180,180)),
      ("Venus",   0.72333199, 0.00677323, 4.8675e24, 3.2486e14,  7, (230,200,130)),
      ("Earth",   1.00000011, 0.01671022, 5.9722e24, 3.9860e14,  8, (100,149,237)),
      ("Mars",    1.52366231, 0.09341233, 6.4171e23, 4.2828e13,  6, (188, 80, 60)),
      ("Jupiter", 5.20336301, 0.04839266, 1.8982e27, 1.2669e17, 13, (200,170,120)),
    ]
    bodies = [sun]
    for nm, a_au, e, mass, gm_p, rpx, col in data:
        a_m   = a_au * AU
        r_peri = a_m * (1 - e)          # start at perihelion on +x axis
        v_peri = vp(a_m, e)
        # vy = -v_peri  → CCW in real space (CW on pygame screen, y-axis flipped)
        bodies.append(Planet(nm, r_peri, 0, 0, -v_peri, mass, gm_p, rpx, col))
    return bodies

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    clock  = pygame.time.Clock()
    bodies = make_system()
    SUBS   = 4
    dt_sub = DAY / SUBS
    paused = False
    view   = TILT
    run    = True
    sun    = bodies[0]

    for _ in range(100):
        for _ in range(SUBS):
            for p in bodies: p.yoshida(bodies, dt_sub)
        for p in bodies[1:]:
            p.dist_sun = math.hypot(p.x-sun.x, p.y-sun.y)
            p.trail.append((p.x,p.y))
            if len(p.trail)>TRAIL_MAX: p.trail.pop(0)

    while run:
        clock.tick(60)
        WIN.fill(BG)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: run=False
            if ev.type == pygame.KEYDOWN:
                if ev.key==pygame.K_ESCAPE: run=False
                if ev.key==pygame.K_SPACE:  paused=not paused
                if ev.key==pygame.K_b:      view=BIRD
                if ev.key==pygame.K_t:      view=TILT

        if not paused:
            for _ in range(SUBS):
                for p in bodies: p.yoshida(bodies, dt_sub)
            for p in bodies[1:]:
                p.dist_sun = math.hypot(p.x-sun.x, p.y-sun.y)
                p.trail.append((p.x,p.y))
                if len(p.trail)>TRAIL_MAX: p.trail.pop(0)

        draw_spacetime(WIN, bodies, view)
        for p in bodies: p.draw(WIN, view)

        m = "BIRD'S EYE  [T]=3-D tilt" if view==BIRD else "3-D TILT   [B]=bird's eye"
        WIN.blit(FONT_LG.render(m,1,(80,140,210)),(12,10))
        WIN.blit(FONT.render(
            "SPACE=pause  ESC=quit",
            1,(50,85,135)),(12,34))

        pygame.display.update()

    pygame.quit(); sys.exit()

if __name__=="__main__":
    main()
