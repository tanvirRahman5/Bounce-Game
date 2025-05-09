from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
from OpenGL.GLU import *
import math, time, sys, random


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
ASPECT = WINDOW_WIDTH / WINDOW_HEIGHT

gravity = -500.0
jump_strength = 250.0
max_jump_duration = 0.35

ball_radius = 10.0
ball_pos = [0.0, 0.0, 10.0]
ball_vel = [0.0, 0.0, 0.0]
jumping = False
jump_start_time = 0.0

score = 0
lives = 3
game_over = False
game_won = False
last_tile = None
time_on_tile = 0.0
max_tile_time = 5
show_timer = False
time_last = time.time()
move_keys = {"a": False, "d": False, "w": False, "s": False}
space_pressed = False

camera_distance = 500.0
camera_angle = 0
camera_height = 500.0
wall_height = 80.0
max_x = 1000
grid_size_x = 30
grid_size_y = 13
tile_size = 80
half_size_x = grid_size_x * tile_size / 2
half_size_y = grid_size_y * tile_size / 2

obstacles = [
    {'pos': [100, 0, 30], 'base_size': 15, 'current_size': 15, 'vel': 100, 
     'shrink_speed': 0.8, 'min_size': 5, 'float_height': 30, 'float_speed': 1.5, 
     'float_offset': random.random()*6.28, 'pulse': 0},
    {'pos': [-150, 100, 40], 'base_size': 20, 'current_size': 20, 'vel': -120,
     'shrink_speed': 1.0, 'min_size': 8, 'float_height': 40, 'float_speed': 2.0,
     'float_offset': random.random()*6.28, 'pulse': 0},
    {'pos': [300, -50, 35], 'base_size': 20, 'current_size': 20, 'vel': 90,
     'shrink_speed': 1.2, 'min_size': 7, 'float_height': 35, 'float_speed': 1.8,
     'float_offset': random.random()*6.28, 'pulse': 0},
    {'pos': [-400, 70, 45], 'base_size': 18, 'current_size': 18, 'vel': -80,
     'shrink_speed': 0.9, 'min_size': 6, 'float_height': 45, 'float_speed': 1.3,
     'float_offset': random.random()*6.28, 'pulse': 0},
    {'pos': [600, 0, 25], 'base_size': 20, 'current_size': 20, 'vel': 110,
     'shrink_speed': 1.1, 'min_size': 5, 'float_height': 25, 'float_speed': 2.2,
     'float_offset': random.random()*6.28, 'pulse': 0},
    {'pos': [200, -150, 50], 'base_size': 16, 'current_size': 16, 'vel': 70,
     'shrink_speed': 1.3, 'min_size': 4, 'float_height': 50, 'float_speed': 1.7,
     'float_offset': random.random()*6.28, 'pulse': 0},
    {'pos': [-300, -100, 20], 'base_size': 17, 'current_size': 17, 'vel': -90,
     'shrink_speed': 0.7, 'min_size': 6, 'float_height': 20, 'float_speed': 2.5,
     'float_offset': random.random()*6.28, 'pulse': 0},
    {'pos': [500, 120, 55], 'base_size': 19, 'current_size': 19, 'vel': 80,
     'shrink_speed': 1.4, 'min_size': 5, 'float_height': 55, 'float_speed': 1.2,
     'float_offset': random.random()*6.28, 'pulse': 0},
    {'pos': [-200, -80, 30], 'base_size': 14, 'current_size': 14, 'vel': -70,
     'shrink_speed': 0.6, 'min_size': 5, 'float_height': 30, 'float_speed': 1.9,
     'float_offset': random.random()*6.28, 'pulse': 0},
    {'pos': [400, -120, 40], 'base_size': 15, 'current_size': 15, 'vel': 100,
     'shrink_speed': 1.5, 'min_size': 4, 'float_height': 40, 'float_speed': 2.1,
     'float_offset': random.random()*6.28, 'pulse': 0},
]

collectibles = []
special_point = {'type': 'star', 'pos': (0, 0, 10), 'collected': False}
holes = set()

def generate_holes():
    global holes
    holes = set()
    while len(holes) < 100:
        i = random.randint(0, grid_size_x - 1)
        j = random.randint(0, grid_size_y - 1)
        holes.add((i, j))

def find_safe_tile():
    while True:
        i = random.randint(0, grid_size_x - 1)
        j = random.randint(0, grid_size_y - 1)
        if (i, j) not in holes:
            x = i * tile_size - half_size_x + tile_size / 2
            y = j * tile_size - half_size_y + tile_size / 2
            return (x, y)

def reset_game(reset_score=True, reset_lives=True):
    global ball_pos, ball_vel, jumping, jump_start_time, score, lives, game_over, game_won
    global collectibles, time_last, obstacles, last_tile, time_on_tile, show_timer, special_point
    
    ball_pos[:] = find_safe_start_tile()
    ball_vel[:] = [0.0, 0.0, 0.0]
    jumping = False
    jump_start_time = 0.0
    
    if reset_score:
        score = 0
        generate_holes()
        collectibles = []
        for _ in range(5):
            x, y = find_safe_tile()
            collectibles.append({
                'type': random.choice(['cube', 'torus', 'pyramid']),
                'pos': (x, y, 10)
            })
        x, y = find_safe_tile()
        special_point['pos'] = (x, y, 10)
        special_point['collected'] = False
    
    if reset_lives:
        lives = 3
    
    game_over = False
    game_won = False
    time_last = time.time()
    last_tile = None
    time_on_tile = 0.0
    show_timer = False
    
    for o in obstacles:
        o['current_size'] = o['base_size']
        o['pos'][2] = o['float_height']
        o['float_offset'] = random.random()*6.28
        o['pulse'] = 0

def find_safe_start_tile():
    for i in range(grid_size_x):
        for j in range(grid_size_y):
            if (i, j) not in holes:
                x = i * tile_size - half_size_x + tile_size / 2
                y = j * tile_size - half_size_y + tile_size / 2
                return [x, y, 10.0]
    return [0.0, 0.0, 10.0]

def setup_projection():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, ASPECT, 1.0, 3000.0)
    glMatrixMode(GL_MODELVIEW)

def reshape(w, h):
    global WINDOW_WIDTH, WINDOW_HEIGHT, ASPECT
    WINDOW_WIDTH = w
    WINDOW_HEIGHT = h
    ASPECT = w / h
    glViewport(0, 0, w, h)
    setup_projection()

def setup_scene():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glLoadIdentity()
    angle_rad = math.radians(camera_angle)
    eye_x = ball_pos[0] - camera_distance * math.cos(angle_rad)
    eye_y = ball_pos[1] + camera_distance * math.sin(angle_rad)
    eye_z = ball_pos[2] + camera_height
    gluLookAt(eye_x, eye_y, eye_z,
              ball_pos[0], ball_pos[1], ball_pos[2],
              0.0, 0.0, 1.0)
    glClearColor(0.5, 0.8, 1.0, 1.0)

def draw_floor():
    green_r, green_g, green_b = 0.302, 0.471, 0.388
    for i in range(grid_size_x):
        for j in range(grid_size_y):
            x = i * tile_size - half_size_x
            y = j * tile_size - half_size_y
            if (i, j) in holes:
                glColor3f(0.0, 0.0, 0.0)
            else:
                if (i + j) % 2 == 0:
                    glColor3f(1.0, 1.0, 1.0)
                else:
                    glColor3f(green_r, green_g, green_b)
            glBegin(GL_QUADS)
            glVertex3f(x, y, 0.0)
            glVertex3f(x + tile_size, y, 0.0)
            glVertex3f(x + tile_size, y + tile_size, 0.0)
            glVertex3f(x, y + tile_size, 0.0)
            glEnd()

def draw_walls():
    glColor3f(0.2, 0.2, 0.8)
    for sx, sy in [(-half_size_x,0),(half_size_x,0),(0,half_size_y),(0,-half_size_y)]:
        glBegin(GL_QUADS)
        if sx != 0:
            x = sx
            glVertex3f(x, -half_size_y, 0)
            glVertex3f(x,  half_size_y, 0)
            glVertex3f(x,  half_size_y, wall_height)
            glVertex3f(x, -half_size_y, wall_height)
        else:
            y = sy
            glVertex3f(-half_size_x, y, 0)
            glVertex3f( half_size_x, y, 0)
            glVertex3f( half_size_x, y, wall_height)
            glVertex3f(-half_size_x, y, wall_height)
        glEnd()

def draw_tree(x, y):
    glColor3f(0.55, 0.27, 0.07)
    glPushMatrix()
    glTranslatef(x, y, 0)
    glScalef(5, 5, 30)
    glutSolidCube(1)
    glPopMatrix()
    glColor3f(0.0, 0.5, 0.0)
    glPushMatrix()
    glTranslatef(x, y, 30)
    glutSolidCone(15, 40, 12, 12)
    glPopMatrix()

def draw_trees():
    spacing = tile_size 
    tree_offset = tile_size // 2
    x = -half_size_x + spacing // 2
    while x <= half_size_x:
        draw_tree(x, -half_size_y + tree_offset)
        draw_tree(x, half_size_y - tree_offset)
        x += spacing

def draw_special_point():
    if not special_point['collected']:
        glPushMatrix()
        x, y, z = special_point['pos']
        glTranslatef(x, y, z)
        glColor3f(1.0, 1.0, 0.0)
        
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0)
        for i in range(11):
            angle = i * 2 * math.pi / 10
            radius = 10 if i % 2 == 0 else 5
            glVertex3f(math.cos(angle) * radius, math.sin(angle) * radius, 0)
        glEnd()
        
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 5)
        glVertex3f(0, 0, 15)
        glVertex3f(5, 0, 10)
        glVertex3f(-5, 0, 10)
        glVertex3f(0, 5, 10)
        glVertex3f(0, -5, 10)
        glEnd()
        
        glPopMatrix()

def draw_collectibles():
    for c in collectibles:
        glPushMatrix()
        x, y, z = c['pos']
        glTranslatef(x, y, z)
        if c['type'] == 'cube':
            glutSolidCube(15)
        elif c['type'] == 'torus':
            glutWireTorus(3, 10, 12, 12)
        elif c['type'] == 'pyramid':
            # Draw base
            glBegin(GL_QUADS)
            glVertex3f(-10, -10, 0)
            glVertex3f(10, -10, 0)
            glVertex3f(10, 10, 0)
            glVertex3f(-10, 10, 0)
            glEnd()
            # Draw sides
            glBegin(GL_TRIANGLES)
            # Front
            glVertex3f(0,0,20); glVertex3f(-10,-10,0); glVertex3f(10,-10,0)
            # Back
            glVertex3f(0,0,20); glVertex3f(10,10,0); glVertex3f(-10,10,0)
            # Right
            glVertex3f(0,0,20); glVertex3f(10,-10,0); glVertex3f(10,10,0)
            # Left
            glVertex3f(0,0,20); glVertex3f(-10,10,0); glVertex3f(-10,-10,0)
            glEnd()
        glPopMatrix()
    draw_special_point()

def draw_obstacles():
    for o in obstacles:
        glPushMatrix()
        x, y, z = o['pos']
        glTranslatef(x, y, z)
        
        o['pulse'] += 0.1
        pulse_factor = 0.5 + 0.5 * math.sin(o['pulse'])
        
        size_ratio = (o['current_size'] - o['min_size']) / (o['base_size'] - o['min_size'])
        red_intensity = 0.8 + (1.0 - size_ratio) * 0.2 * pulse_factor
        green_blue = 0.1 * size_ratio
        
        glColor3f(red_intensity, green_blue, green_blue)
        glutSolidSphere(o['current_size'], 32, 32)
        
        if o['current_size'] < o['base_size']:
            glPushMatrix()
            glow_size = o['current_size'] * (1.0 + 0.2 * pulse_factor)
            glColor4f(1.0, 0.3, 0.3, 0.3 + 0.2 * pulse_factor)
            glutWireSphere(glow_size, 16, 16)
            glPopMatrix()
        
        glPushMatrix()
        float_offset = 5 * math.sin(time.time() * 2 + o['float_offset'])
        glTranslatef(0, 0, -float_offset - o['current_size'])
        glColor4f(0.9, 0.9, 0.1, 0.2 + 0.1 * pulse_factor)
        glutSolidSphere(o['current_size'] * 0.7, 16, 16)
        glPopMatrix()
        
        glPopMatrix()

def draw_ball():
    glColor3f(1.0, 0, 0)
    glPushMatrix()
    glTranslatef(ball_pos[0], ball_pos[1], ball_pos[2])
    glutSolidSphere(ball_radius, 32, 32)
    glPopMatrix()

def draw_score():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    
    glColor3f(1,1,1)
    glRasterPos2f(10, WINDOW_HEIGHT - 30)
    for ch in f"Score: {score} Lives: {lives}": 
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    
    if show_timer:
        time_left = max(0, max_tile_time - time_on_tile)
        glColor3f(1, 0.5, 0)
        glRasterPos2f(10, WINDOW_HEIGHT - 60)
        for ch in f"Move in: {time_left:.1f}s": 
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    
    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_game_over():
    if game_over:
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glColor3f(1,0,0)
        glRasterPos2f(10, WINDOW_HEIGHT - 90)
        for ch in f"Game Over! Score: {score} (Press R to Restart)": 
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        glEnable(GL_DEPTH_TEST)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

def draw_win_message():
    if game_won:
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        
        glColor3f(0, 1, 0)
        win_text = "YOU WIN! (Press R to Restart)"
        text_width = glutBitmapLength(GLUT_BITMAP_HELVETICA_18, win_text.encode())
        glRasterPos2f((WINDOW_WIDTH - text_width) // 2, WINDOW_HEIGHT // 2)
        
        for ch in win_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        
        glEnable(GL_DEPTH_TEST)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

def update_obstacles(dt):
    for o in obstacles:
        o['current_size'] -= o['shrink_speed'] * dt
        
        if o['current_size'] <= o['min_size']:
            o['current_size'] = o['base_size']
        
        o['pos'][2] = o['float_height'] + 10 * math.sin(time.time() * o['float_speed'] + o['float_offset'])
        
        o['pos'][1] += o['vel'] * dt
        if o['pos'][1] > half_size_y - o['current_size'] or o['pos'][1] < -half_size_y + o['current_size']:
            o['vel'] *= -1

def update():
    global time_last, ball_pos, ball_vel, jumping, jump_start_time, score, lives, game_over, last_tile, time_on_tile, show_timer, game_won
    
    now = time.time()
    dt = now - time_last
    time_last = now
    if game_over or game_won:
        return

    # Adjusted movement directions
    move_dir = [(1 if move_keys['w'] else -1 if move_keys['s'] else 0),
                (-1 if move_keys['d'] else 1 if move_keys['a'] else 0)]
    
    if move_dir[0] and move_dir[1]:
        move_dir = [d/math.sqrt(2) for d in move_dir]
    
    speed = 200.0
    ball_vel[0] = move_dir[0] * speed
    ball_vel[1] = move_dir[1] * speed

    on_ground = ball_pos[2] <= ball_radius
    if space_pressed and on_ground and not jumping:
        jumping = True
        jump_start_time = now
        ball_vel[2] = jump_strength
    
    if jumping:
        ball_vel[2] = jump_strength if space_pressed and (now - jump_start_time) < max_jump_duration else ball_vel[2]
        if not space_pressed or (now - jump_start_time) >= max_jump_duration:
            jumping = False

    ball_vel[2] += gravity * dt
    for i in range(3): 
        ball_pos[i] += ball_vel[i] * dt

    if ball_pos[2] < ball_radius:
        ball_pos[2] = ball_radius
        ball_vel[2] = 0
        jumping = False

    ball_pos[0] = max(-half_size_x + ball_radius, min(half_size_x - ball_radius, ball_pos[0]))
    ball_pos[1] = max(-half_size_y + ball_radius, min(half_size_y - ball_radius, ball_pos[1]))

    i = int(math.floor((ball_pos[0] + half_size_x) / tile_size))
    j = int(math.floor((ball_pos[1] + half_size_y) / tile_size))
    current_tile = (i, j)

    if ball_pos[2] <= ball_radius + 1 and (current_tile not in holes):
        if current_tile == last_tile:
            time_on_tile += dt
            show_timer = True
            if time_on_tile >= max_tile_time:
                lives -= 1
                time_on_tile = 0.0
                last_tile = None
                show_timer = False
                if lives <= 0:
                    game_over = True
                else:
                    reset_game(reset_score=False, reset_lives=False)
        else:
            last_tile = current_tile
            time_on_tile = 0.0
            show_timer = True
    else:
        last_tile = None
        time_on_tile = 0.0
        show_timer = False

    if (i,j) in holes and ball_pos[2] <= ball_radius + 1:
        lives -= 1
        if lives <= 0:
            game_over = True
        else:
            reset_game(reset_score=False, reset_lives=False)

    update_obstacles(dt)

    for o in obstacles:
        dx = ball_pos[0] - o['pos'][0]
        dy = ball_pos[1] - o['pos'][1]
        dz = ball_pos[2] - o['pos'][2]
        distance = math.sqrt(dx**2 + dy**2 + dz**2)
        
        if distance < ball_radius + o['current_size']:
            lives -= 1
            if lives <= 0:
                game_over = True
            else:
                reset_game(reset_score=False, reset_lives=False)
            break

    # Check for collectibles with 3D collision
    remaining = []
    for c in collectibles:
        dx = ball_pos[0] - c['pos'][0]
        dy = ball_pos[1] - c['pos'][1]
        dz = ball_pos[2] - c['pos'][2]
        distance = math.sqrt(dx**2 + dy**2 + dz**2)
        
        if distance < ball_radius + 15:
            score += 1
        else:
            remaining.append(c)
    collectibles[:] = remaining

    # Check for special point with 3D collision
    if not special_point['collected']:
        sp_x, sp_y, sp_z = special_point['pos']
        dx = ball_pos[0] - sp_x
        dy = ball_pos[1] - sp_y
        dz = ball_pos[2] - sp_z
        distance = math.sqrt(dx**2 + dy**2 + dz**2)
        
        if distance < ball_radius + 15:
            score += 2
            special_point['collected'] = True
            if score >= 7:  # Fixed win condition
                game_won = True

def display():
    setup_scene()
    draw_floor()
    draw_walls()
    draw_trees()
    if not game_won:
        draw_collectibles()
    draw_obstacles()
    draw_ball()
    draw_score()
    draw_game_over()
    draw_win_message()
    glutSwapBuffers()

def idle():
    update()
    glutPostRedisplay()

def keyboard(k,x,y):
    global space_pressed
    if k == b'\x1b': sys.exit()
    if k == b' ': space_pressed = True
    if k in [b'a',b'd',b'w',b's']: move_keys[k.decode()] = True
    if k == b'r': 
        if game_over or game_won:
            reset_game()

def keyboard_up(k,x,y):
    global space_pressed
    if k == b' ': space_pressed = False
    if k in [b'a',b'd',b'w',b's']: move_keys[k.decode()] = False

def special(key,x,y):
    global camera_angle, camera_height
    if key == GLUT_KEY_LEFT: camera_angle += 5
    elif key == GLUT_KEY_RIGHT: camera_angle -= 5
    elif key == GLUT_KEY_UP: camera_height += 10
    elif key == GLUT_KEY_DOWN: camera_height -= 10
    camera_height = max(50, min(1000, camera_height))

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutCreateWindow(b"3D Ball Game - Fixed Version")
    glutReshapeFunc(reshape)
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special)
    reset_game()
    glutMainLoop()

if __name__ == '__main__':
    main()
