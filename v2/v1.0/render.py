import pygame, numpy as np
from pygame import gfxdraw
pygame.init()

class Renderer:
    BLACK = (0,0,0)
    WHITE = (255,255,255)
    BODY_BLUE = (39,130,215)
    def __init__(self, size, dt):
        self.size = list(size)
        self.screen = pygame.display.set_mode(size)
        self.dt = dt*1000
        self.clock = pygame.time.Clock()
    def render(self, bodies):
        self.screen.fill(Renderer.WHITE)
        for body in bodies:
            gfxdraw.aacircle(self.screen,int(body.p[0]),int(body.p[1]),int(body.r),Renderer.BODY_BLUE)
            gfxdraw.filled_circle(self.screen,int(body.p[0]),int(body.p[1]),int(body.r),Renderer.BODY_BLUE)
        pygame.display.flip()
        self.clock.tick(self.dt)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return 0
    def close(self):
        pygame.quit()
