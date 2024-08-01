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
density         ρ               mu/lu^2
acceleration    a               lu/s^2
force           f               mu·lu/s^2
'''



# classes
## body
class Body:
    RHO = 0.1 # common density of all bodies
    def __init__(self, pos=np.array([0,0]), vel=np.array([0,0]),mass=0, is_contacted=True, is_attracted=True, is_attractor=False, is_player=False):
        # position and velocity are represented by numpy 2-dimention vectors
        self.p=np.array(pos, dtype=float)              # position
        self.v=np.array(vel, dtype=float)              # velocity
        self.m=float(mass)             # mass
        self.isContacted=is_contacted         # influenced by contact forces?
        self.isAttracted=is_attracted # influenced by attractive forces?
        self.isAttractor=is_attractor
        self.isPlayer=is_player
        self.updateRadius()

    def updateRadius(self):     # update radius
        self.r=np.sqrt(self.m/(np.pi*Body.RHO))
    
    def setMass(self, m):
        self.m=m
        self.updateRadius()

    def next(self, dt):             # simply 
        self.p = self.p+self.v*dt

    def __lt__(self, b): # less than magic function, compare regarding mass
        return self.m < b.m

    def __gt__(self, b):
        return self.m > b.m

## simulation environment
class Environment:
    def __init__(self, settings=None):
        self.bodies = []
        self.attractors = []
        self.player = None
        self.settings = {
                'border': True,
                'size': np.array([1000, 800]),# np.array([1500, 1000]),              # width and height
                'gravity': True,
                'gravitation-g': 100, # gravitation coefficient
                'absorb': True,
                'absorption-epsilon': 3, # if the smaller body has a new radius less than ε, then it'll be merged
                'ejection-velocity': 25,
                'dt': 0.08,                     # simulation time step, that is 50 fps
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
        if body.isAttractor: self.attractors.append(body)
        if body.isPlayer: self.player = body
    def addBodies(self, bodies):
        self.bodies.extend(bodies)
        for body in bodies:
            if body.isAttractor: self.attractors.append(body)
            if body.isPlayer: self.player = body
    # important methods

    def start(self):
        cnt = 0
        while(cnt < self.settings['time']):
            # render
            if self.settings['render']:
                res = self.renderer.render(self.bodies, player=self.player)
                if res['quit']: break
                if res['mouse-down-pos'] != None and self.player in self.bodies: # the player still survives and ejects a mote
                    # eject 5% of the total mass
                    pos = np.array(res['mouse-down-pos'])
                    if np.linalg.norm(pos-self.player.p)>self.player.r:
                        pm = self.player.m # old mass of the player
                        dm = self.player.m*0.05 # ejected mass
                        print("new mote")
                        vec = (pos-self.player.p)/np.linalg.norm(pos-self.player.p)
                        print(vec)
                        self.player.setMass(self.player.m-dm)
                        ejectedMote = Body(self.player.p+vec*(self.player.r+np.sqrt(dm/(np.pi*Body.RHO))), self.player.v+vec*self.settings['ejection-velocity'], dm)
                        self.bodies.append(ejectedMote)
                        self.player.v = (pm*self.player.v-dm*ejectedMote.v)/self.player.m
            # normal frame update
            self.updateFrame()
        self.renderer.close()


    def updateFrame(self):  # update one frame
        for body in self.bodies:
            body.next(self.settings['dt'])
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
        
        if self.settings['absorb']: # big bodies absorb small ones
            removed = []
            for i in range(0, len(self.bodies)):
                for j in range(i+1,len(self.bodies)):
                    if self.bodies[i] in removed or self.bodies[j] in removed: continue # needs further improvements
                    a, b = i, j
                    M, m = self.bodies[a], self.bodies[b]
                    if M<m:
                        M, m = m, M
                        a, b = b, a
                    d = np.linalg.norm(M.p-m.p)+1      # distance
                    if M.r+m.r>d: # absorption occurs
                        rM = (d+np.sqrt(2*(M.r**2+m.r**2)-d**2))/2
                        rm = (d-np.sqrt(2*(M.r**2+m.r**2)-d**2))/2
                        Mm, mm = M.m, m.m # old mass values
                        if rm >= self.settings['absorption-epsilon']:
                            M.setMass(Body.RHO*np.pi*rM**2)
                            m.setMass(Body.RHO*np.pi*rm**2)
                            if M.isContacted: M.v = (Mm*M.v+(mm-m.m)*m.v)/M.m
                        else:
                            M.setMass(M.m+m.m)
                            if M.isContacted: M.v = (Mm*M.v+mm*m.v)/(Mm+mm)
                            removed.append(m)
            
            for body in removed:
                self.bodies.remove(body)
                if body.isAttractor: self.attractors.remove(body)

        if self.settings['gravity']:
            for attractor in self.attractors:
                for body in self.bodies:
                    if body.isAttractor: continue# currently do not implement the interaction between two attractors
                    # note that attractors are also members of self.bodies
                    if not body.isAttracted and not attractor.isAttracted: continue
                    d = np.linalg.norm(attractor.p-body.p)
                    F = self.settings['gravitation-g']*attractor.m*body.m/d**2
                    if body.isAttracted:
                        ax = F*(attractor.p[0]-body.p[0])/d/body.m
                        ay = F*(attractor.p[1]-body.p[1])/d/body.m
                        body.v += np.array([ax, ay]) * self.settings['dt']
                    if attractor.isAttracted:
                        ax = -F*(attractor.p[0]-body.p[0])/d/attractor.m
                        ay = -F*(attractor.p[1]-body.p[1])/d/attractor.m
                        attractor.v += np.array([ax, ay]) * self.settings['dt']
                    
                    
                    
if __name__ == "__main__":
    env = Environment()
    bodies = []
    """
    for i in range(30):
        bodies.append(Body(np.array([np.random.randint(0, env.settings['size'][0]), np.random.randint(0, env.settings['size'][1])]),
                                    np.random.randint(-5, 5, (2,)), np.random.randint(20,60)))
    '''for i in range(3):
        bodies.append(Body(np.array([np.random.randint(0, env.settings['size'][0]), np.random.randint(0, env.settings['size'][1])]),
                       (0,0), 100, is_attractor=True))'''

    # bodies.append(Body(env.settings['size']/2,
    #                    (0,0), 100, is_attractor=True, is_attracted=False, is_contacted=False))

    bodies.append(Body(np.array([np.random.randint(0, env.settings['size'][0]), np.random.randint(0, env.settings['size'][1])]), np.zeros(2), 70, is_player=True))
    """
    sun = Body(env.settings['size']/2, (0,0), 100, is_attractor=True, is_attracted=False, is_contacted=False)
    bodies.append(sun)
    R = sun.r+10
    total = 15
    for i in range(total):
        theta = np.random.rand()*2*np.pi
        thetap = theta+np.pi/2
        m = np.random.randint(20,60) if i != total//2 else 50 
        r = np.sqrt(m/(np.pi*Body.RHO))
        v = np.sqrt(env.settings['gravitation-g']*sun.m/R)
        body = Body(sun.p+(R+r)*np.array([np.cos(theta), np.sin(theta)]),
                                    v*np.array([np.cos(thetap), np.sin(thetap)]), m, is_player = (i == total//2))
        R += body.r+10
        bodies.append(body)
    
    env.addBodies(bodies)
    env.start()
