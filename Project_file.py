from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

# Window and grid
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
GRID_SIZE = 10000
GRID_DIVISIONS = 100

# Ball position (treated as player position)
ball_x, ball_y, ball_z = 0, 0, 20
ball_speed = 5.0

# Add these variables for jump physics
ball_vertical_velocity = 0.0
gravity = -0.5
is_jumping = False

# Camera settings
camera_offset_z = 100  # Initial vertical offset
camera_offset_y = 80
field_of_view = 45
first_person = False
view_distance = 300
view_angle = 270  # camera angle in degrees (for third-person view)
player_rotation = 90  # assuming facing up
player_coordinates = (ball_x, ball_y)

# Camera control
camera_vertical_speed = 10  # Speed of vertical camera movement
camera_rotation_speed = 5  # Speed of camera rotation

def draw_grid():
    square_size = GRID_SIZE // GRID_DIVISIONS
    half = GRID_SIZE // 2
    for i in range(-half, half, square_size):
        for j in range(-half, half, square_size):
            if ((i // square_size) + (j // square_size)) % 2 == 0:
                glColor3f(1.0, 1.0, 1.0)
            else:
                glColor3f(0.85, 0.75, 0.95)
            glBegin(GL_QUADS)
            glVertex3f(i, j, 0)
            glVertex3f(i + square_size, j, 0)
            glVertex3f(i + square_size, j + square_size, 0)
            glVertex3f(i, j + square_size, 0)
            glEnd()

def draw_ball():
    glPushMatrix()
    glTranslatef(ball_x, ball_y, ball_z)
    glColor3f(0.0, 1.0, 0.0)
    quad = gluNewQuadric()
    gluSphere(quad, 10, 32, 32)
    gluDeleteQuadric(quad)
    glPopMatrix()

def configure_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(field_of_view, WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    px, py = player_coordinates
    pa = math.radians(player_rotation)

    if first_person:
        eye_x = px + 20 * math.cos(pa)
        eye_y = py + 20 * math.sin(pa)
        eye_z = 80
        look_x = px + 100 * math.cos(pa)
        look_y = py + 100 * math.sin(pa)
        look_z = 80
        gluLookAt(eye_x, eye_y, eye_z, look_x, look_y, look_z, 0, 0, 1)
    else:
        cam_x = px + view_distance * math.cos(math.radians(view_angle))
        cam_y = py + view_distance * math.sin(math.radians(view_angle))
        cam_z = camera_offset_z  # The camera's vertical position (z-axis)
        gluLookAt(cam_x, cam_y, cam_z, px, py, 0, 0, 0, 1)  # Add the missing `up_z` argument

def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)

def display():
    global player_coordinates
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    player_coordinates = (ball_x, ball_y)
    configure_camera()
    draw_grid()
    draw_ball()
    glutSwapBuffers()

def update_ball():
    global ball_z, ball_vertical_velocity, is_jumping

    # Apply gravity if the ball is in the air
    if ball_z > 20 or is_jumping:
        ball_vertical_velocity += gravity
        ball_z += ball_vertical_velocity

        # Stop the ball when it hits the ground
        if ball_z <= 20:
            ball_z = 20
            ball_vertical_velocity = 0
            is_jumping = False

    glutPostRedisplay()

def special_keys(key, x, y):
    global ball_x, ball_y
    if key == GLUT_KEY_UP:
        ball_y += ball_speed
    elif key == GLUT_KEY_DOWN:
        ball_y -= ball_speed
    elif key == GLUT_KEY_LEFT:
        ball_x -= ball_speed
    elif key == GLUT_KEY_RIGHT:
        ball_x += ball_speed
    glutPostRedisplay()

def normal_keys(key, x, y):
    global camera_offset_z, view_angle, ball_vertical_velocity, is_jumping

    if key == b'w':  # Move the camera up (on Z-axis)
        camera_offset_z += camera_vertical_speed
    elif key == b's':  # Move the camera down (on Z-axis)
        camera_offset_z -= camera_vertical_speed
    elif key == b'a':  # Rotate the camera left
        view_angle -= camera_rotation_speed
    elif key == b'd':  # Rotate the camera right
        view_angle += camera_rotation_speed
    elif key == b' ':  # Space bar for jump
        if not is_jumping:  # Only allow jumping if the ball is on the ground
            ball_vertical_velocity = 10.0
            is_jumping = True

    glutPostRedisplay()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutCreateWindow(b"3D Ball with Camera Control")
    init()
    glutDisplayFunc(display)
    glutSpecialFunc(special_keys)
    glutKeyboardFunc(normal_keys)  # Bind normal key controls (WASD) for camera
    glutIdleFunc(update_ball)  # Continuously update the ball's position
    glutMainLoop()

if __name__ == "__main__":
    main()
