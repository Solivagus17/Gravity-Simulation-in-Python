# Gravity-Simulation-in-Python
Physically accurate Solar System simulation with real-time spacetime fabric visualization. Features J2000 orbital elements, 4th-order Yoshida integrator, Lorentzian gravity wells &amp; glowing orbit trails. Inspired by Kavan's C++/OpenGL sim. Built with Python, Pygame &amp; NumPy.
# 🌌 Solar System Gravity Simulator

> Physically accurate Solar System simulation with real-time spacetime fabric visualization — built with Python, Pygame & NumPy.

Inspired by [Kavan's C++/OpenGL gravity simulation](https://youtu.be/_YbGWoUaZg0) — rebuilt from scratch in Python with significantly expanded physics, a real-time spacetime fabric, and correct orbital mechanics.

---

## ✨ Demo
#3-D View (TILT VIEW)
![image alt](https://github.com/Solivagus17/Gravity-Simulation-in-Python/blob/ac637aafc5c44015f9c686a009036f37d2ce5758/Gravity%20Simulation%20in%20Python-%20TILT%20view.png)

#BIRD'S EYE View(2-D View)
![image alt](https://github.com/Solivagus17/Gravity-Simulation-in-Python/blob/2a2daf16f158acefee2f8b4f7c57c33d2d6deb59/Gravity%20Simulation%20in%20Python-%20BIRD'S%20EYE%20view.png)


---

## 🚀 Features

- **Correct orbital mechanics** — J2000 epoch elements sourced from NASA JPL Horizons
- **4th-order Yoshida symplectic integrator** — far superior energy conservation vs naive Euler integration
- **Physically sourced constants** — G (NIST CODATA 2018), AU (IAU 2012 exact), GM☉ (IAU 2015 nominal)
- **Real-time spacetime fabric** — Lorentzian gravity wells per body (`z(d) = peak / √(1 + (d/w)²)`), computed via NumPy
- **Glowing half-orbit trails** — trailing arc follows each planet in real time
- **Two views** — Bird's-eye and 3D tilted perspective with full perspective projection
- **All planets orbit correctly** — counter-clockwise in real space, consistent across all bodies
- **60 fps** — spacetime grid fully vectorised with NumPy

---

## 🔭 Physics

### Integrator
Uses the **4th-order Yoshida symplectic integrator** with 4 sub-steps per frame (1 simulated day per frame). Symplectic integrators preserve the Hamiltonian structure of the equations of motion, meaning energy and angular momentum don't drift over long simulations.

### Orbital Elements (J2000 Epoch)
| Planet | a (AU) | e |
|--------|--------|---|
| Mercury | 0.38709893 | 0.20563069 |
| Venus | 0.72333199 | 0.00677323 |
| Earth | 1.00000011 | 0.01671022 |
| Mars | 1.52366231 | 0.09341233 |
| Jupiter | 5.20336301 | 0.04839266 |

Each planet starts at **perihelion** with the correct perihelion speed from the vis-viva equation:

```
v_peri = √( GM☉ × (1 + e) / (a × (1 - e)) )
```

### Spacetime Fabric
The spacetime curvature grid uses a **Lorentzian well profile**:

```
z(d) = peak / √(1 + (d/w)²)
```

This is smooth at the centre (no singularity), falls off as `1/d` at large distances (matching Newtonian potential shape), and is superposed across all bodies in the weak-field limit — valid throughout the Solar System since `Φ/c² ≪ 1` everywhere.

---

## 🛠️ Stack

| Library | Purpose |
|---------|---------|
| `pygame` | Window, rendering, event loop |
| `numpy` | Vectorised spacetime grid computation |
| `math` | Orbital mechanics, projection |

---

## ⚙️ Installation

```bash
git clone https://github.com/Solivagus17/Gravity-Simulation-in-Python
cd Gravity-Simulation-in-Python
pip install pygame numpy
python gravity_sim.py
```

---

## 🎮 Controls

| Key | Action |
|-----|--------|
| `B` | Bird's-eye view (top-down) |
| `T` | 3D tilt view (spacetime fabric visible) |
| `SPACE` | Pause / Resume |
| `ESC` | Quit |

---

## 🗺️ Roadmap

- [x] N-body Yoshida symplectic integrator
- [x] Real-time spacetime fabric with per-body gravity wells
- [x] Glowing half-orbit trails
- [x] Bird's-eye + 3D perspective views
- [ ] Black hole simulation with Schwarzschild geodesics
- [ ] Saturn's rings
- [ ] Gravitational lensing effect

---

## 🙏 Credits

- Inspired by **Kavan's** C++/OpenGL gravity simulation on YouTube.
- Orbital elements: [NASA JPL Horizons](https://ssd.jpl.nasa.gov/horizons/)
- Physical constants: [NIST CODATA 2018](https://physics.nist.gov/cuu/Constants/), [IAU 2015](https://www.iau.org/)

---

## 📄 License

MIT License — feel free to use, modify, and build on this.
