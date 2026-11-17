from ti_draw import *
from ti_system import *
from math import *
from random import *

# --- TI-84 PLUS CE KEY CODES ---
K_UP = 25
K_DOWN = 34
K_LEFT = 24
K_RIGHT = 26
K_2ND = 21
K_ALPHA = 31
K_ENTER = 105
K_CLEAR = 45

# --- RETRO SOCCER PLAYER SPRITE (12x16 pixels) ---
# 0 = Transparent, 1 = Skin, 2 = Jersey (Team Color), 3 = Shorts, 4 = Cleats, 5 = Hair
S_SPRITE = [
    [0,0,0,5,5,5,5,5,0,0,0,0],
    [0,0,5,5,5,5,5,5,5,0,0,0],
    [0,0,1,1,1,1,1,1,1,0,0,0], # Face
    [0,0,0,1,1,1,1,1,0,0,0,0],
    [0,2,2,2,2,2,2,2,2,2,0,0], # Jersey
    [2,2,2,3,2,2,2,3,2,2,2,0],
    [2,2,2,2,2,2,2,2,2,2,2,0],
    [0,2,2,2,2,2,2,2,2,2,0,0],
    [0,3,3,3,3,3,3,3,3,3,0,0], # Shorts
    [0,3,3,0,0,0,0,3,3,0,0,0],
    [0,0,1,1,0,0,1,1,0,0,0,0], # Legs
    [0,0,1,1,0,0,1,1,0,0,0,0],
    [0,0,1,1,0,0,1,1,0,0,0,0],
    [0,0,4,4,0,0,4,4,0,0,0], # Cleats
    [0,4,4,4,0,0,4,4,4,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0]
]

# --- GAME STATE ---
px, py = 80, 135
gx, gy = 200, 135
score = 0
cpu = 0
match_time = 45.0
half = 1
dribble = 0
tackle_cd = 0
aiming = False
aim_ang = 45.0
aim_dir = 1
aim_pwr = 0.0
pwr_dir = 1
phase = 0  # 0=dribble, 1=angle, 2=power, 3=flight
bx, by, bvx, bvy = 0.0, 0.0, 0.0, 0.0
msg = ""
msg_t = 0
goal_x, goal_y1, goal_y2 = 300, 85, 135

def draw_pitch():
  # Stadium Sky / Stands backdrop
  set_color(20, 36, 54)
  fill_rect(0, 0, 320, 55)
  for cx in range(6, 320, 16):
    for cy in range(16, 48, 10):
      set_color(50 + (cx * 2) % 90, 70 + (cy * 4) % 100, 90 + (cx + cy) % 110)
      fill_circle(cx, cy, 3)

  # Green turf pitch + stripe patterns
  set_color(45, 148, 62)
  fill_rect(0, 55, 320, 155)
  set_color(38, 130, 52)
  for x in range(0, 320, 40):
    fill_rect(x, 55, 20, 155)

  # Pitch lines (White)
  set_color(245, 245, 245)
  set_pen("medium", "solid")
  draw_rect(12, 58, 296, 149) # Outer boundary
  draw_line(160, 58, 160, 207) # Halfway line
  draw_circle(160, 132, 36) # Center circle
  
  # Penalty boxes & Goal area
  draw_rect(230, 95, 78, 74)
  draw_rect(275, 114, 33, 36)
  set_pen("thin", "solid")

  # Goal Net & Posts
  set_color(30, 30, 30)
  fill_rect(301, 84, 6, 98)
  set_color(220, 225, 235)
  draw_rect(300, 84, 12, 53)
  # Net crosshatch pattern
  for ny in range(88, 133, 6):
    draw_line(301, ny, 311, ny)
  for nx in range(303, 311, 3):
    draw_line(nx, 85, nx, 136)

def draw_pixel_player(x, y, is_cpu, step, has_ball):
  ix, iy = int(x) - 6, int(y) - 8
  # Drop shadow
  set_color(20, 80, 30)
  fill_rect(ix + 1, iy + 14, 10, 3)

  for r in range(16):
    for c in range(12):
      val = S_SPRITE[r][c]
      if val == 0:
        continue
      elif val == 1:
        set_color(145, 92, 56) if not is_cpu else set_color(228, 178, 134)
      elif val == 2: # Jerseys: Blue (Player) vs Red (CPU)
        set_color(32, 110, 225) if not is_cpu else set_color(215, 35, 45)
      elif val == 3: # Shorts: White vs Black
        set_color(250, 250, 250) if not is_cpu else set_color(35, 35, 35)
      elif val == 4:
        set_color(20, 20, 20)
      elif val == 5:
        set_color(25, 25, 30)

      bo = 1 if (step % 4 < 2 and r > 9) else 0
      set_pixel(ix + c, iy + r + bo)

  # Dribbling Soccer Ball
  if has_ball:
    bounce = abs((step % 6) - 3)
    draw_ball(int(x) + 8, int(y) + 4 + bounce)

def draw_ball(x, y):
  ix, iy = int(x), int(y)
  set_color(250, 250, 250)
  fill_circle(ix, iy, 4)
  set_color(20, 20, 20)
  draw_circle(ix, iy, 4)
  set_pixel(ix, iy)

def draw_hud():
  set_color(15, 18, 28)
  fill_rect(0, 0, 320, 16)
  set_color(100, 225, 250)
  draw_text(6, 2, "HOME:" + str(score))
  set_color(240, 95, 95)
  draw_text(98, 2, "AWAY:" + str(cpu))
  set_color(255, 255, 255)
  draw_text(192, 2, "H" + str(half) + " " + str(int(match_time)) + "'")
  if tackle_cd == 0:
    set_color(80, 235, 130)
    draw_text(260, 2, "[SKILL]")

def draw_arc_guide():
  rad = aim_ang * 3.14159 / 180.0
  spd = 8.0 + (aim_pwr / 100.0) * 8.0 if phase == 2 else 11.5
  vx = cos(rad) * spd
  vy = -sin(rad) * spd
  tx, ty = float(px + 4), float(py - 6)
  for i in range(1, 16):
    tx += vx * 1.3
    ty += vy * 1.3
    if i % 2 == 0:
      set_color(255, 255, 255) if phase == 1 else set_color(80, 250, 120)
      fill_circle(int(tx), int(ty), 2)

  if phase == 2:
    set_color(20, 20, 20)
    fill_rect(int(px) - 18, int(py) - 32, 36, 6)
    set_color(60, 235, 100) if 60 <= aim_pwr <= 80 else set_color(250, 190, 40)
    fill_rect(int(px) - 17, int(py) - 31, int(aim_pwr * 0.34), 4)

def reset_possession(scored):
  global px, py, gx, gy, phase, match_time, cpu, half, msg, msg_t
  if scored:
    globals()['score'] += 1
    msg = "GOAL! HOME SCORES!"
  else:
    msg = "SAVED! CPU COUNTERS!"
    cpu += 1
  msg_t = 20
  px, py = 80, 135
  gx, gy = 200, 135
  phase = 0
  match_time = max(0.0, match_time - 5.0)

# --- TITLE SCREEN ---
clear()
draw_pitch()
set_color(15, 18, 28)
fill_rect(35, 55, 250, 95)
set_color(100, 225, 250)
draw_rect(35, 55, 250, 95)
draw_text(65, 66, "CE SOCCER: STRIKER")
set_color(255, 255, 255)
draw_text(52, 88, "ARROWS: Move   ALPHA: Skill")
draw_text(52, 106, "2ND / ENTER: Aim & Shoot")
set_color(80, 235, 130)
draw_text(68, 128, "PRESS ANY KEY TO PLAY")
show_draw()
wait_key()

# --- MAIN GAME LOOP ---
while half <= 2:
  k = get_key(0)
  if k == K_CLEAR:
    break

  if phase == 0:
    moved = False
    if k == K_UP and py > 68:
      py -= 4
      moved = True
    elif k == K_DOWN and py < 196:
      py += 4
      moved = True
    elif k == K_LEFT and px > 20:
      px -= 4
      moved = True
    elif k == K_RIGHT and px < 275:
      px += 4
      moved = True

    if k == K_ALPHA and tackle_cd == 0:
      px = min(280, px + 18)
      py += randint(-12, 12)
      tackle_cd = 25
      moved = True

    if moved:
      dribble += 1
    if tackle_cd > 0:
      tackle_cd -= 1

    # CPU Defender AI
    if gx > px + 18:
      gx -= 2
    elif gx < px + 14:
      gx += 2
    if gy < py:
      gy += 2
    elif gy > py:
      gy -= 2

    if abs(px - gx) < 12 and abs(py - gy) < 10 and tackle_cd < 18:
      msg = "TACKLED! CPU BALL"
      msg_t = 16
      px, py = 70, 135

    if k == K_2ND or k == K_ENTER:
      phase = 1
      aim_ang = 40.0
      aim_dir = 1

  elif phase == 1:
    aim_ang += aim_dir * 3.5
    if aim_ang > 68:
      aim_dir = -1
    elif aim_ang < 25:
      aim_dir = 1
    if k == K_2ND or k == K_ENTER:
      phase = 2
      aim_pwr = 10.0
      pwr_dir = 1

  elif phase == 2:
    aim_pwr += pwr_dir * 6.0
    if aim_pwr >= 100:
      pwr_dir = -1
    elif aim_pwr <= 5:
      pwr_dir = 1
    if k == K_2ND or k == K_ENTER:
      phase = 3
      rad = aim_ang * 3.14159 / 180.0
      spd = 8.0 + (aim_pwr / 100.0) * 8.0
      bx, by = float(px + 4), float(py - 6)
      bvx = cos(rad) * spd
      bvy = -sin(rad) * spd

  elif phase == 3:
    bx += bvx
    by += bvy
    # Goal check
    if bx >= 298 and 85 <= by <= 135:
      reset_possession(True)
    elif bx > 310 or by < 60 or by > 200:
      reset_possession(False)

  if phase < 3:
    match_time -= 0.12
    if match_time <= 0:
      if half == 1:
        half = 2
        match_time = 45.0
        msg = "HALF TIME!"
        msg_t = 25
      else:
        half = 3

  # --- RENDER FRAME ---
  draw_pitch()
  draw_hud()

  if py < gy:
    draw_pixel_player(px, py, False, dribble, phase < 3)
    draw_pixel_player(gx, gy, True, dribble, False)
  else:
    draw_pixel_player(gx, gy, True, dribble, False)
    draw_pixel_player(px, py, False, dribble, phase < 3)

  if phase in (1, 2):
    draw_arc_guide()
  elif phase == 3:
    draw_ball(bx, by)

  if msg_t > 0:
    set_color(15, 18, 28)
    fill_rect(80, 24, 160, 18)
    set_color(100, 225, 250)
    draw_rect(80, 24, 160, 18)
    draw_text(92, 27, msg)
    msg_t -= 1

  show_draw()

# --- FULL TIME / GAME OVER SCREEN ---
set_color(15, 18, 28)
fill_rect(50, 68, 220, 72)
set_color(100, 225, 250)
draw_rect(50, 68, 220, 72)
res = "FULL TIME: YOU WIN!" if score > cpu else "FULL TIME: YOU LOSE" if score < cpu else "FULL TIME: DRAW"
draw_text(85, 78, res)
set_color(255, 255, 255)
draw_text(102, 100, "FINAL: " + str(score) + " - " + str(cpu))
draw_text(74, 120, "PRESS CLEAR TO EXIT")
show_draw()
wait_key()
