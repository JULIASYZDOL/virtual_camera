import pygame
import math
import numpy as np

class Camera:
    def __init__(self, x=100, y=100, z=800, fov=60):
        self.x = x
        self.y = y
        self.z = z
        self.fov = fov
        self.rotation = [0, 0, 0]
        self.move_speed = 10
        self.rotation_speed = 2
        self.translation_matrix = np.array([
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ])

    def move_forward(self):
        dx = math.sin(math.radians(self.rotation[1])) * self.move_speed
        dy = -math.sin(math.radians(self.rotation[0])) * self.move_speed
        dz = -math.cos(math.radians(self.rotation[1])) * self.move_speed

        self.x += dx
        self.y += dy
        self.z += dz

    def move_backward(self):
        dx = -math.sin(math.radians(self.rotation[1])) * self.move_speed
        dy = math.sin(math.radians(self.rotation[0])) * self.move_speed
        dz = math.cos(math.radians(self.rotation[1])) * self.move_speed

        self.x += dx
        self.y += dy
        self.z += dz

    def move_left(self):
        dx = math.sin(math.radians(self.rotation[1] + 90)) * self.move_speed
        dy = 0
        dz = -math.cos(math.radians(self.rotation[1] + 90)) * self.move_speed

        self.x += dx
        self.y += dy
        self.z += dz

    def move_right(self):
        dx = math.sin(math.radians(self.rotation[1] - 90)) * self.move_speed
        dy = 0
        dz = -math.cos(math.radians(self.rotation[1] - 90)) * self.move_speed

        self.x += dx
        self.y += dy
        self.z += dz

    def move_up(self):
        translation_vector = np.array([0, self.move_speed, 0, 1])
        translated_vector = np.dot(self.translation_matrix, translation_vector)
        self.x += translated_vector[0]
        self.y += translated_vector[1]
        self.z += translated_vector[2]

    def move_down(self):
        translation_vector = np.array([0, -self.move_speed, 0, 1])
        translated_vector = np.dot(self.translation_matrix, translation_vector)
        self.x += translated_vector[0]
        self.y += translated_vector[1]
        self.z += translated_vector[2]

    def rotate(self, axis, angle):
        if axis == 'x':
            self.rotation[0] += angle
        elif axis == 'y':
            self.rotation[1] += angle
        elif axis == 'z':
            self.rotation[2] += angle

    def fov_matrix(self, fov):
        aspect_ratio = 1 
        near = 10
        far = 1000

        f = 1 / math.tan(fov / 2 * math.pi/180)

        return np.array([
            [f / aspect_ratio, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, -far / (far - near) , -1],
            [0, 0, -far*near/(far-near), 0]
        ])

    def rotation_matrix_x(self, angle):
        c = math.cos(math.radians(angle))
        s = math.sin(math.radians(angle))
        return np.array([
            [1, 0, 0, 0],
            [0, c, -s, 0],
            [0, s, c, 0],
            [0, 0, 0, 1]
        ])

    def rotation_matrix_y(self, angle):
        c = math.cos(math.radians(angle))
        s = math.sin(math.radians(angle))
        return np.array([
            [c, 0, s, 0],
            [0, 1, 0, 0],
            [-s, 0, c, 0],
            [0, 0, 0, 1]
        ])

    def rotation_matrix_z(self, angle):
        c = math.cos(math.radians(angle))
        s = math.sin(math.radians(angle))
        return np.array([
            [c, -s, 0, 0],
            [s, c, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

    def projection_matrix(self):
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 1/800, 1]
        ])

class Scene:
    def __init__(self, filename):
        self.camera = Camera()
        self.cubes = []  
        self.load_scene_from_file(filename)

    def load_scene_from_file(self, filename):
        with open(filename, 'r') as file:
            current_cube = [] 
            for line in file:
                if line.strip().startswith('#'): 
                    if current_cube:  
                        self.cubes.append(current_cube)
                        current_cube = [] 
                else:
                    coords = list(map(float, line.strip().split()))
                    if len(coords) == 3:
                        current_cube.append(coords) 
            if current_cube:
                self.cubes.append(current_cube)

    def draw(self, screen):
        for cube in self.cubes:
            for i in range(len(cube) - 1):
                self.draw_3d_line(screen, cube[i], cube[i+1])


    def draw_3d_line(self, screen, start, end):
        start_x, start_y, start_z = start
        end_x, end_y, end_z = end

        start_x += self.camera.x
        start_y += self.camera.y
        start_z += self.camera.z

        end_x += self.camera.x
        end_y += self.camera.y
        end_z += self.camera.z

        rotated_start = self.rotate_point(start_x, start_y, start_z)
        rotated_end = self.rotate_point(end_x, end_y, end_z)

        rotated_start_array = np.array([rotated_start[0], rotated_start[1], rotated_start[2], 1])
        rotated_end_array = np.array([rotated_end[0], rotated_end[1], rotated_end[2], 1])

        fov_matrix = self.camera.fov_matrix(self.camera.fov)
        transformed_start = np.dot(fov_matrix, rotated_start_array)
        transformed_end = np.dot(fov_matrix, rotated_end_array)

        start_screen_x, start_screen_y = self.transform_to_screen(transformed_start)
        end_screen_x, end_screen_y = self.transform_to_screen(transformed_end)

        pygame.draw.line(screen, (255, 105, 180), (start_screen_x, start_screen_y), (end_screen_x, end_screen_y), 2)


    def transform_to_screen(self, point):
        screen_x = int((point[0] * 400 / -point[2] + 400))
        screen_y = int((point[1] * 400 / -point[2] + 400))
        return screen_x, screen_y

    def rotate_point(self, x, y, z):
        rotation_matrix_x = self.camera.rotation_matrix_x(self.camera.rotation[0])
        rotation_matrix_y = self.camera.rotation_matrix_y(self.camera.rotation[1])
        rotation_matrix_z = self.camera.rotation_matrix_z(self.camera.rotation[2])

        point = np.array([x, y, z, 1])

        rotated_point = np.dot(rotation_matrix_z, np.dot(rotation_matrix_y, np.dot(rotation_matrix_x, point)))

        return rotated_point[:3]

def main():
    pygame.init()
    screen_width, screen_height = 800, 800
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    filename = 'objects.txt'
    scene = Scene(filename)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            scene.camera.move_forward()
        if keys[pygame.K_s]:
            scene.camera.move_backward()
        if keys[pygame.K_a]:
            scene.camera.move_left()
        if keys[pygame.K_d]:
            scene.camera.move_right()
        if keys[pygame.K_SPACE]:
            scene.camera.move_up()
        if keys[pygame.K_LSHIFT]:
            scene.camera.move_down()
        if keys[pygame.K_UP]:
            scene.camera.rotate('x', scene.camera.rotation_speed)
        if keys[pygame.K_DOWN]:
            scene.camera.rotate('x', -scene.camera.rotation_speed)
        if keys[pygame.K_LEFT]:
            scene.camera.rotate('y', scene.camera.rotation_speed)
        if keys[pygame.K_RIGHT]:
            scene.camera.rotate('y', -scene.camera.rotation_speed)
        if keys[pygame.K_z]:
            scene.camera.fov -= 1  
        if keys[pygame.K_x]:
            scene.camera.fov += 1

        screen.fill((0, 0, 0))
        scene.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()