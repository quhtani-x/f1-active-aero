# F1 Active Aero (AI wing controller)

An AI that controls an F1 car's rear wing angle in real time, shown in a live
visual simulation. The idea is exactly how DRS / active aero works:

- on a **straight** the AI drops the wing flat → less drag → higher top speed
- in a **corner** the AI raises the wing → more downforce → more grip → faster cornering

The controller looks *ahead* at the track curvature (like a driver does) and
moves the wing **before** the corner arrives. The window shows the car going
round the track, the live wing angle, the current mode (STRAIGHT/CORNER), the
speed, and a little side-view of the wing tilting.

## the controller

```
look ahead at track curvature
  curvature low  (straight) -> wing ≈ 5%   (DRS open, top speed ~334 km/h)
  curvature high (corner)   -> wing up to 100% (downforce, way more grip)
actuator moves the wing smoothly toward that target
```

## run

```bash
pip install pygame
python sim.py
```

tags: ai, control, simulation, pygame, aviation, motorsport

wanted to actually visualise active aero instead of just reading about DRS.
