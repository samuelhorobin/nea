import pygame
import random
import settings

class RectParticleCache:
    '''
    Cache class to store generated particle images based on width and color.

    Attributes:
    - cache: Dictionary to store cached particle images.
    '''

    def __init__(self):
        self.cache = {}

    def get_cached_particle(self, *key):
        '''
        Get a cached particle image or create and cache a new one if not present.

        Parameters:
        - key: Tuple representing the particle properties (width, color).

        Returns:
        - Cached or newly created particle image.
        '''
        if key in self.cache:
            return self.cache[key]
        else:
            image = self.create_particle(key)
            self.cache[key] = image
            return image

    def create_particle(self, key):
        '''
        Create a new particle image based on the specified properties.

        Parameters:
        - key: Tuple representing the particle properties (width, color).

        Returns:
        - Newly created particle image.
        '''
        width = height = key[0]
        rgb = key[1]

        # Create a new particle image with specified width and color
        image = pygame.Surface((width, height))
        image.fill(rgb)

        return image

class RectParticle_Manager:
    '''
    Manager class for rectangular particles.

    Attributes:
    - particles: Pygame sprite group to manage particles.
    - cache: Instance of RectParticleCache for caching particle images.
    '''

    particles = pygame.sprite.Group()
    cache = RectParticleCache()

    @staticmethod
    def update(dt):
        '''
        Update method to handle particle updates over time.

        Parameters:
        - dt: Time elapsed since the last update.
        '''
        for rp in RectParticle_Manager.particles:
            rp.time += dt
            if rp.time >= rp.lifespan:
                rp.kill()

            if not rp.settled:
                rp.vector.y += rp.yGrav
                rp.vector.x *= (1 - rp.xRes)
                if abs(rp.vector.x) < 0.5:
                    rp.vector.x = 0

                rp.rect.move_ip(rp.vector)

                if rp.rect.bottom > rp.floor:
                    rp.vector.y = 0
                    rp.yGrav = 0
                    rp.rect.bottom = rp.floor

                if rp.vector.x == 0 and rp.vector.y == 0:
                    rp.settled = True

class Rectparticle(pygame.sprite.Sprite):
    '''
    Class representing a rectangular particle.

    Attributes:
    - pos: Position of the particle.
    - width, height: Dimensions of the particle.
    - rgb: Color of the particle.
    - lifespanB: Base lifespan of the particle.
    - lifespanV: Variance in the lifespan of the particle.
    - angle: Angle of movement for the particle.
    - strength: Strength of the particle's movement.
    - xRes: Resistance to movement along the x-axis.
    - yGrav: Gravity affecting the particle along the y-axis.
    '''

    def __init__(self, pos):
        super().__init__()
        self.pos = pos

        # Particle attributes
        self.width = self.height = random.randint(1, 2) * 5
        self.rgb = (random.randint(150, 200), 61, 61)

        self.lifespanB = 2  # Base lifespan
        self.lifespanV = random.uniform(-1, 1)  # Variance in lifespan

        self.angle = random.randint(10, 170)
        self.strength = random.randint(5, 10)

        self.xRes = 0.1
        self.yGrav = 1

    def load(self):
        '''
        Load method to initialize particle attributes and set up the particle.

        Sets up attributes such as time, settled status, movement vector, lifespan, image, rect, and floor.
        '''
        self.time = 0
        self.settled = False

        self.vector = pygame.Vector2(self.strength, self.strength * -1)
        self.vector.rotate_ip(self.angle)

        self.lifespan = (self.lifespanB + self.lifespanV)

        # Get the particle image from the cache
        self.image = RectParticle_Manager.cache.get_cached_particle(self.width, self.rgb)

        self.rect = self.image.get_frect(topleft=self.pos)

        self.floor = self.rect.bottom + random.randint(4, 11) * settings.UPSCALE

    def draw(self, screen):
        '''
        Draw method to blit the particle image onto the screen.

        Parameters:
        - screen: Pygame display surface.
        '''
        screen.blit(self.image, self.rect.topleft)

class ElixirParticle(Rectparticle):
    '''
    Class representing an elixir particle, a specific type of rectangular particle.

    Attributes:
    Inherits attributes from Rectparticle.
    '''

    def __init__(self, pos):
        super().__init__(pos)
        self.width = self.height = random.randint(2, 3) * 5
        self.rgb = (66, random.randint(0, 70), 144)
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.rgb)
        self.rect = self.image.get_frect(topleft=pos)

class FleshParticle(Rectparticle):
    '''
    Class representing a flesh particle, a specific type of rectangular particle.

    Attributes:
    Inherits attributes from Rectparticle.
    '''

    def __init__(self, pos):
        super().__init__(pos)
        self.width = self.height = random.randint(3, 4) * 5
        self.rgb = (random.randint(125, 225), 40, 61)
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.rgb)
        self.rect = self.image.get_frect(topleft=pos)
