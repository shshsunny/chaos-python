import numpy as np
import render

'''
physical units
---------------------------------------------------------------------
name            form            measuring unit 
---------------------------------------------------------------------
position        p[x,y]          length unit [lu]
velocity        v[dx,dy]        lu/s
mass            m               mass unit [mu]
acceleration    a               lu/s^2
force           f               mu·lu/s^2
'''



# classes
## body
class Body:
    def __init__(self, dt, pos=np.array([0,0]), vel=np.array([0,0]),mass=0, external=True):
        # position and velocity are represented by numpy 2-dimention vectors
        self.p=pos              # position
        self.v=vel              # velocity
        self.m=mass             # mass
        self.e=external         # influenced by external forces?
        self.dt = dt
        self.updateRadius()

    def updateRadius(self):     # update radius
        self.r=np.sqrt(self.m)*2

    def influenced(self):
        return self.e
    
    def setMass(self, m):
        self.m=m
        self.updateRadius()

    def next(self):             # simply 
        self.p = self.p+self.v*self.dt

    def __lt__(self, b): # less than magic function, compare regarding mass
        return self.m < b.m

    def __gt__(self, b):
        return self.m > b.m
## simulation environment
class Environment:
    def __init__(self, settings=None):
        self.bodies = []
        self.settings = {
                'border': True,
                'size': np.array([1500, 1000]),              # width and height
                'gravity': False,
                'absorb': True,
                'dt': 0.04,                     # simulation time step, that is 25 fps
                'time': float('inf'),                      # total simulation time
                'render': True
            }
        if settings != None:
            for key in settings:
                self.settings[key]=settings[key]
        if self.settings['render']:
            self.renderer = render.Renderer(self.settings['size'], self.settings['dt'])
        else: self.renderer=None

    # basic interface
    def addBody(self, body):
        self.bodies.append(body)
    def addBodies(self, bodies):
        self.bodies.extend(bodies)
    
    # important methods

    def start(self):
        cnt = 0
        while(cnt < self.settings['time']):
            # render
            if self.settings['render']:
                res = self.renderer.render(self.bodies)
                if res == 0:
                    break
            # normal frame update
            self.updateFrame()
        self.renderer.close()


    def updateFrame(self):  # update one frame
        for body in self.bodies:
            body.next()
        if self.settings['border']:
            for body in self.bodies:
                if body.p[0]-body.r<0:
                    body.v[0]=abs(body.v[0])
                if body.p[0]+body.r>self.settings['size'][0]:
                    body.v[0]=-abs(body.v[0])
                if body.p[1]-body.r<0:
                    body.v[1]=abs(body.v[1])
                if body.p[1]+body.r>self.settings['size'][1]:
                    body.v[1]=-abs(body.v[1])
        
        if self.settings['absorb']:
            for i in range(0, len(self.bodies)):
                for j in range(i+1,len(self.bodies)):
                    a, b = i, j
                    if self.bodies[a]<self.bodies[b]: a, b = b, a
                    u, v = self.bodies[a], self.bodies[b]
                    dist = np.linalg.norm(u.p-v.p)      # distance


if __name__ == "__main__":
    env = Environment()
    bodies = []
    for i in range(10):
        bodies.append(Body(0.04,np.random.randint(0, 500, [2,1]),np.random.randint(0, 50, [2,1]),np.random.randint(10,50)))
    env.addBodies(bodies)
    env.start()
