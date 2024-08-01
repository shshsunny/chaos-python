import pygame, numpy as np
from pygame import gfxdraw
pygame.init()

class Renderer:
    BLACK = (0,0,0)
    WHITE = (255,255,255)
    BODY_BLUE = (39,130,215)
    BODY_RED = (255, 0, 0)
    ATTRACTOR_ORANGE = (255, 87, 51)
    PLAYER_GREEN = (23, 119, 65)
    def __init__(self, size, dt):
        self.size = list(size)
        self.screen = pygame.display.set_mode(size)
        self.dt = dt*1000 # miliseconds
        self.clock = pygame.time.Clock()
    def render(self, bodies, player=None):
        self.screen.fill(Renderer.BLACK)
        for body in bodies:
            if body.isPlayer:
                color = Renderer.PLAYER_GREEN
            else:
                color = (Renderer.BODY_RED if player==None else (Renderer.BODY_BLUE if body.m<player.m else Renderer.BODY_RED)) if not body.isAttractor else Renderer.ATTRACTOR_ORANGE
            gfxdraw.aacircle(self.screen,int(body.p[0]),int(body.p[1]),int(body.r),color)
            gfxdraw.filled_circle(self.screen,int(body.p[0]),int(body.p[1]),int(body.r),color)
            #pygame.draw.circle(self.screen, Renderer.BODY_BLUE, (int(body.p[0]), int(body.p[1])), int(body.r), 0)
        pygame.display.flip()
        self.clock.tick(self.dt)

        res = {"quit": False, "mouse-down-pos": None}
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                res["quit"] = True
            if e.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]: # the left mouse button is pressed 
                res["mouse-down-pos"] = pygame.mouse.get_pos()
        return res
    def close(self):
        pygame.quit()
