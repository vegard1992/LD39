import pygame
from pygame.locals import *

import math
import time
import glob
import os
import random
import mido
import numpy



class Text:
    def __init__(self):
        self.fonts = {}
        self.init_fonts()
        #Outrun future, diskoteque, 6809, husky, karmatic, true lies
        self.selection = ""

    def parse_type_entry(self, t):
        #print(t)
        t = t.rstrip("\n")
        p = "", "", ""
        w = "UNIQUEWORD123456789VEGARDISANUNCOMMONNAMESECRETPASSWORD99"
        if '"' in t:
            p = t.split('"')
            #print(p)
            t = p[0] + w + p[-1]
            #print(t)
        s = t.split(" ")
        #print(s)
        name, fname, size = s[0], s[1].replace(w, p[1]), int(s[2])
        return name, fname, size

    def init_fonts(self):
        print("== %LOADING FONTS% ==")
        with open("fonts/types.txt", "r") as f:
            for line in f.readlines():
                name, fname, size = self.parse_type_entry(line)
                path = "fonts/"+fname
                print(path)
                F = pygame.font.Font(path, size)
                self.fonts[name] = [name, fname, size, F, []]

    def get(self, abc, color):
        return self.fonts[self.selection][3].render(abc, 1, color)


class MIDI:
    def __init__(self):
        self.tracks = []
        self.collect()

    def collect(self):
        print("== %LOADING MIDI% ==")
        os.chdir("midi")
        for F in glob.glob("*.mid"):
            print(F)
            self.tracks.append(F)
        os.chdir("..")


class Background:
    # Patterns! l systems like in pong game
    def __init__(self):
        pass

def load_art():
    L = ["art/pac/animation.txt", "art/cratepop/animation.txt", "art/ghost/static.txt", \
            "art/pups/static.txt", "art/dk/static.txt", "art/crate/static.txt"]
    print("== %LOADING ART% ==")
    anim, banim = Animation(L[0]), Animation(L[1])
    stat = Static(L[2])
    stat.grayscale()
    pstat = Static(L[3], treatn=3)
    dkstat = Static(L[4], treatn=1)
    cstat = Static(L[5])
    return anim, banim, stat, pstat, dkstat, cstat


class Animation:
    def __init__(self, path):
        self.path = path
        self.images = []
        self.load()
        for i in range(2): self.treat()

        self.frame = 0
        self.total = 0
        self.current = 0
        self.timer = 0
        self.dt = 0

    def load(self):
        prepath = "/".join(self.path.split("/")[:-1])+"/"
        with open(self.path, "r") as F:
            data = F.read().rstrip("\n").split(" ")

        # name, fps, format, frames, frame1, frame2, ..., hold_frame_1, hold_frame_2, ...
        name = self.name = data[0]
        fps = self.fps = int(data[1])
        fmat = self.fmat = data[2]
        frames = self.frames = int(data[3])
        fnames = self.fnames = []
        fholds = self.fholds = []

        for entry in data[4:4+frames]:
            fnames.append(entry)
            self.images.append(pygame.image.load(prepath+entry+"."+fmat).convert_alpha())
        for entry in data[4+frames:]:
            fholds.append(int(entry))

        self.dt = 1/self.fps

        print("animation")
        print("  {0} - {1}".format(name, " ".join(fnames)))
        print("    loaded - {0} fps, {1} frames".format(fps, frames))

    def treat(self):
        n = []
        for i in self.images:
            sx, sy = i.get_width(), i.get_height()
            ns = (sx*2, sy*2)
            i1 = pygame.transform.scale(i, ns)
            #self.color_surface(i1, (0, 255, 0))
            n.append(i1)

        self.images = n

    def update(self):
        if time.clock() - self.timer > self.dt:
            self.timer = time.clock()
            self.frame += 1

        if self.frame-self.total >= self.fholds[self.current]:
            self.current += 1
            self.total += self.frame

        if self.current >= self.frames:
            self.current = 0
            self.total = 0
            self.frame = 0

    def get_frame(self):
        return self.images[self.current]


def grayscale(img):
    arr = pygame.surfarray.array3d(img)
    #luminosity filter
    avgs = [[(r*0.298 + g*0.587 + b*0.114) for (r,g,b) in col] for col in arr]
    arr = numpy.array([[[avg,avg,avg] for avg in col] for col in avgs])
    return pygame.surfarray.make_surface(arr)


class Static:
    def __init__(self, path, treatn=2):
        self.path = path
        self.images = []
        self.load()
        for i in range(treatn):
            self.treat()
        self.grays = []
        #self.grayscale()

    def grayscale(self):
        for g in (0, 5, 6, 7):
            i = self.images[g]
            key = i.get_at((0,0))[:3]
            #print(key)
            i.set_colorkey(key)
            self.grays.append(grayscale(i))

    def load(self):
        prepath = "/".join(self.path.split("/")[:-1])+"/"
        with open(self.path, "r") as F:
            data = F.read().rstrip("\n").split(" ")

        name = data[0]
        fmat = data[1]
        print("static")
        print("  "+name)
        print("  "+fmat+" format")
        print("    " + " ".join(data[2:]))
        fnames = []
        for entry in data[2:]:
            fnames.append(entry)
            self.images.append(pygame.image.load(prepath+entry+"."+fmat).convert_alpha())

    def treat(self):
        n = []
        for i in self.images:
            sx, sy = i.get_width(), i.get_height()
            ns = (sx*2, sy*2)
            i1 = pygame.transform.scale(i, ns)
            #self.color_surface(i1, (0, 150, 0))
            #S = pygame.Surface((sx*2, sy*2))
            #S.set_alpha(100)
            #i1.blit(S, (0,0))
            n.append(i1)

        self.images = n

    def color_surface(self, surface, new_color):
        c = pygame.surfarray.pixels3d(surface)
        a = pygame.surfarray.array3d(surface)
        r, g, b = new_color
        #arr[:,:,0] = b & arr[:,:,0]
        a[:,:,1] = g & c[:,:,2] & ~c[:,:,1]  #& ~(arr[:,:,1] & arr[:,:,0])) + (arr[:,:,1] & (arr[:,:,1] & arr[:,:,0]))
        #arr[:,:,2] = r & arr[:,:,0]
        return pygame.surfarray.make_surface(a)


class Sound:
    def __init__(self):
        self.sounds = {}
        bounces = "Jump4.wav", "Laser_Shoot5.wav", "Pickup_Coin2.wav", "Powerup17.wav", "Pickup_Coin3.wav", "Jump13.wav", "Powerup33.wav", "Powerup48.wav"
        path = "sounds/"
        # playing, sound_data
        self.sounds["bounce"] = [False, pygame.mixer.Sound(path+bounces[7])] # 2, 5, 4, 7
        self.sounds["bounce"][1].set_volume(0.2)

        booms = "Powerup47.wav", "Powerup40.wav"
        self.sounds["ready"] = [False, pygame.mixer.Sound(path+booms[1])]
        self.sounds["ready"][1].set_volume(0.2)
        self.sounds["boom"] = [False, pygame.mixer.Sound(path+booms[0])]

        hurts = "Hit_Hurt32.wav"
        self.sounds["ow"] = [False, pygame.mixer.Sound(path+hurts)]
        self.sounds["ow"][1].set_volume(0.2)

        wall = "Hit_Hurt41.wav"
        self.sounds["wall"] = [False, pygame.mixer.Sound(path+wall)]
        self.sounds["wall"][1].set_volume(0.2)

        controls = "Powerup45.wav"
        self.sounds["control"] = [False, pygame.mixer.Sound(path+controls)]
        self.sounds["control"][1].set_volume(0.2)

        danger = "Jump17.wav"
        self.sounds["warning"] = [False, pygame.mixer.Sound(path+danger)]
        self.sounds["warning"][1].set_volume(0.3)

        throw = "Jump22.wav"
        self.sounds["throw"] = [False, pygame.mixer.Sound(path+throw)]
        self.sounds["throw"][1].set_volume(0.2)

        crate = "Hit_Hurt47.wav", "Hit_Hurt52.wav", "Hit_Hurt70.wav"
        self.sounds["crate"] = [False, pygame.mixer.Sound(path+crate[2])]
        self.sounds["crate"][1].set_volume(0.2)

    def play(self, snd):
        self.sounds[snd][1].play()

class Ghost:
    def __init__(self, spawn_area, w, h):
        self.w, self.h = w, h
        a = spawn_area
        self.pos = random.randint(a.x, a.x+a.w), random.randint(a.y, a.y+a.h)
        self.held_frame = 0
        #self.held_frame_dt = 0.5
        self.held_frame_dt = random.random() / 2 + 0.25
        self.held_frame_timer = time.clock()
        self.held_frame_f = False

        self.frame = 0
        self.derps = 1, 2, 3, 4
        self.spinny = False

        self.dx, self.dy = 0, 0

        self.colliding = False

        self.killedby = ""

    def update(self):
        dx, dy = self.dx, self.dy
        self.pos = self.pos[0] + dx, self.pos[1] + dy

        if not self.held_frame_f:
            if abs(dx) > abs(dy):
                if dx > 0:
                    F = 0
                else:
                    F = 6
            else:
                if dy > 0:
                    F = 5
                else:
                    F = 7
        elif self.spinny == True:
            F = random.choice((0, 6, 5, 7))
        else:
            F = self.held_frame

        self.frame = F

        if time.clock() - self.held_frame_timer > self.held_frame_dt:
            self.held_frame_dt = random.random() / 2 + 0.25
            self.held_frame_timer = time.clock()
            self.held_frame_f = False

            if not random.randint(0, 3):
                self.held_frame_f = True
                self.held_frame = random.choice(self.derps)
            elif not random.randint(0, 3):
                self.spinny = True
            if not random.randint(0, 1):
                Q = random.random()*10
                self.dx = random.random() * Q - Q/2
                self.dy = random.random() * Q - Q/2

    def collision(self, line):
        x0, y0 = self.pos
        x0 += self.w/2
        y0 += self.h/2
        x1, y1 = line[0]
        x2, y2 = line[1]

        if (x2-x0)**2 + (y2-y0)**2 < 20**2: return True # within reach of pac

        maxd = 70**0.5
        over = abs((y2-y1)*x0 - (x2-x1)*y0 + x2*y1 - y2*x1)
        under = ((y2-y1)**2+(x2-x1)**2)**0.5
        distance = over/under

        if maxd ** 2 > distance:
            self.colliding = True
            if (y1 < y2 and y1 < y0 < y2) or (y2 < y1 and y2 < y0 < y1):
                return True
        self.colliding = False
        return False



class Ghosts:
    def __init__(self, R, s, e):
        self.safe_rect = R
        self.static = s
        self.ghosts = []
        self.death_anims = []
        self.death_anim_dt = 0.5

        self.spawn_timer = time.clock()
        self.spawn_timer_dt = random.random() / 2 + 0.25

        self.effects = e

        self.snd = None

        self.player = ""
        self.p1kills = 0
        self.p2kills = 0

        self.exploding = False

        self.spawn_mode = 1

    def spawn(self):
        if self.spawn_mode == 0: return
        if random.randint(0, 9): return
        im = self.static.images[0]
        w, h = im.get_width(), im.get_height()
        g = Ghost(self.safe_rect, w, h)
        self.ghosts.append(g)
        self.effects.add_crate(g.pos)

    def set_explode(self, p):
        self.player = p
        self.exploding = True

    def update(self, line, p):
        i = 0
        kill = []
        for g in self.ghosts:
            g.update()
            try: c = g.collision(line)
            except ZeroDivisionError: c = False
            if not self.safe_rect.collidepoint(g.pos) or c:
                kill.append(i)
                if not self.exploding:
                    if p == "player1":
                        self.p1kills += 1
                        g.killedby = "player1"
                    else:
                        self.p2kills += 1
                        g.killedby = "player2"
                else:
                    if self.player == "player1":
                        self.p1kills += 1
                        g.killedby = "player1"
                    else:
                        self.p2kills += 1
                        g.killedby = "player2"

            i += 1

        for i in reversed(kill):
            g = self.ghosts[i]
            self.ghosts.pop(i)
            danim = [g.pos, time.clock(), 255]
            #da = self.death_anims[i]
            px, py = g.pos
            px += g.w/2
            py += g.h/2
            pkill = g.killedby
            self.effects.add_death((px, py), pkill)
            self.death_anims.append(danim)
            #self.snd.play("ow")


        kill = []
        i = 0
        for d in self.death_anims:
            d[2] = int(255*(time.clock()-self.death_anim_dt))
            if time.clock() - d[1] > self.death_anim_dt:
                kill.append(i)
            i += 1

        for i in reversed(kill):
            self.death_anims.pop(i)

        if time.clock() - self.spawn_timer > self.spawn_timer_dt and self.spawn_mode == 0:
            self.spawn_timer = time.clock()
            self.spawn_timer_dt = random.random() / 4 + 0.1
            im = self.static.images[0]
            w, h = im.get_width(), im.get_height()
            g = Ghost(self.safe_rect, w, h)
            self.ghosts.append(g)
            self.effects.add_crate(g.pos)



    def draw(self, surf, b):
        for g in self.ghosts:
            surf.blit(self.static.images[g.frame], g.pos)
            #if g.colliding: col = 255, 0, 0
            #else: col = 0, 255, 255
            #A = g.pos[0] + g.w/2, g.pos[1] + g.h/2
            #B = b
            #pygame.draw.line(surf, col, A, B, 5)
        for d in self.death_anims:
            A = random.choice(self.static.grays)
            #A.set_alpha(d[2])
            surf.blit(A, d[0])
            #A.set_alpha(0)

class BouncingBall:
    # 40 updates per sec
    def __init__(self):
        self.pos = 100, 300
        self.ppos = 99, 299
        self.vel = 20, -20
        self.rad = 20

        self.impact = False
        self.polyfirst = False
        self.polynomial = False
        self.speedup = 1.1
        self.region = "", ""
        self.supersonic = False
        self.MAXV = 1000
        self.supersonicspeed = (60)**2
        self.pause_momentum = False
        self.pause_length = 0.3
        self.pause_timer = time.clock()

        self.update_yet = False
        self.upd_per_sec = 40
        self.upd_timer = 1/self.upd_per_sec
        self.n_upd = 0
        self.first_update = True
        self.last_timer = time.clock()

        self.combo = 0
        self.consecutive_misses = 0

        self.disable_controls = False

        self.explode = False
        self.explode_dt = 3
        self.explode_timer = time.clock()

        self.tug = 0
        self.tug_size = 100

        self.walled = False

    def set_explode(self):
        self.explode = True
        self.explode_timer = time.clock()

    def set_world(self, rect):
        self.world_rect = rect
        B = self.rad * 3 / 4
        self.safe_rect = pygame.Rect(rect.x+B, rect.y+B, rect.w-B*2, rect.h-B*2)
        self.center = rect.center

        self.x1 = self.safe_rect.x
        self.x2 = self.safe_rect.x + self.safe_rect.w
        self.y1 = self.safe_rect.y
        self.y2 = self.safe_rect.y + self.safe_rect.h

    def dsq(self, v):
        return v[0]**2+v[1]**2

    def move(self):

        if self.polynomial:
            Z = 1.04 #* 2
            if self.polytype == "y": self.vel = self.vel[0], self.vel[1] * Z
            if self.polytype == "x": self.vel = self.vel[0] * Z, self.vel[1]

            #print("hi")
            #else: self.vel = self.vel[0] * 1.02, self.vel[1]
        #else:
            #print("poop")

        MAXV = self.MAXV
        if self.vel[0] > MAXV:
            self.vel = MAXV, self.vel[1]
        elif self.vel[0] < -MAXV:
            self.vel = -MAXV, self.vel[1]
        if self.vel[1] > MAXV:
            self.vel = self.vel[0], MAXV
        elif self.vel[1] < -MAXV:
            self.vel = self.vel[0], -MAXV

        self.impact = False
        self.ppos = self.pos
        dx, dy = new_pos = self.pos[0] + self.vel[0], self.pos[1] + self.vel[1]

        # as long as we are inside the "safe rect" we will not be colliding with the walls
        #print(new_pos)
        if self.safe_rect.collidepoint(new_pos):
            self.pos = new_pos
            return

        if self.polynomial == True:
            self.polynomial = False
            Q = 0
            D = 0.9
            #self.vel = self.vel[0] * D + random.random()*Q-Q/2, self.vel[1] * D + random.random()*Q-Q/2

        # figure out which wall it collides with
        #print(self.vel)
        vel = self.vel
        px, py = self.pos
        yX, yY = 0, 0
        xX, xY = 0, 0
        if vel[1] < 0: # top
            ya = self.y1
            dsy = vel[1]
            dsx = vel[0]
            yb = (dsy)/(dsx)
            B = py - yb * px
            #print(B)
            xa = (ya-B)/yb
            yX = xa# + self.pos[0]
            yY = xa * yb + 1 + B # + self.pos[1]
            #print(self.pos)
            #print(new_pos)
            #print(yX, yY)
            if self.safe_rect.collidepoint((yX, yY)):
                self.pos = yX, yY
                self.vel = self.vel[0], -self.vel[1]#*2
                self.impact = True
                if yX < self.safe_rect.centerx:
                    self.region = "top", "left"
                else:
                    self.region = "top", "right"
                return
        elif vel[1] > 0: # bot
            ya = self.y2
            #print(ya)
            dsy = vel[1]
            dsx = vel[0]
            yb = (dsy)/(dsx)
            B = py - yb * px
            #print(B)
            xa = (ya-B)/yb
            #print(xa)
            yX = xa# + self.pos[0]
            yY = xa * yb-1 + B# + self.pos[1]
            #print(self.pos)
            #print(new_pos)
            #print(yX, yY)
            if self.safe_rect.collidepoint((yX, yY)):
                self.pos = yX, yY
                self.vel = self.vel[0], -self.vel[1]#*2
                self.impact = True
                if yX < self.safe_rect.centerx:
                    self.region = "bot", "left"
                else:
                    self.region = "bot", "right"
                return
        if vel[0] < 0: # left
            xa = self.x1
            dsy = vel[1]
            dsx = vel[0]
            yb = (dsy)/(dsx)
            B = py - yb * px
            #print(B)
            #xa = (ya-B)/yb
            #yX = xa# + self.pos[0]
            xX = xa + 1
            xY = xa * yb + B# + self.pos[1]
            if self.safe_rect.collidepoint((xX, xY)):
                self.pos = xX, xY
                self.vel = -self.vel[0], self.vel[1]#*2
                self.impact = True
                if xY < self.safe_rect.centery:
                    self.region = "left", "top"
                else:
                    self.region = "left", "bot"
                return
        elif vel[0] > 0: # right
            xa = self.x2
            dsy = vel[1]
            dsx = vel[0]
            yb = (dsy)/(dsx)
            B = py - yb * px
            #print(self.pos, new_pos)
            #print(xa)
            #print(yb, B)
            #print(B)
            #xa = (ya-B)/yb
            #yX = xa# + self.pos[0]
            xX = xa - 1
            xY = xa * yb + B# + self.pos[1]
            if self.safe_rect.collidepoint((xX, xY)):
                self.pos = xX, xY
                self.vel = -self.vel[0], self.vel[1]#*2
                self.impact = True
                if xY < self.safe_rect.centery:
                    self.region = "right", "top"
                else:
                    self.region = "right", "bot"
                #print(self.pos, self.vel)
                return

        #print("Slope", yb)
        #print("Intersection at", xa)
        #print(X, Y)


    def update(self):
        if time.clock() - self.last_timer > self.upd_timer:
            self.tug_size -= 1 / self.upd_per_sec
            self.update_yet = True
            self.last_timer = time.clock()

            if self.first_update:
                self.first_update = False
                self.first_timer = time.clock()

        if not self.update_yet: return
        self.update_yet = False
        self.n_upd += 1
        if self.n_upd%40 == 0:
            upd_correct = 1/40*self.n_upd/(time.clock()-self.first_timer)
            self.upd_timer *= upd_correct

        if self.impact == True:
            self.combo += 1
            self.ppos = self.pos
            self.pause_momentum = True
            self.pause_timer = time.clock()

        if time.clock() - self.explode_timer > self.explode_dt:
            self.explode = False

        if self.explode:
            self.consecutive_misses = 0
            self.polyfirst = False
            self.polynomial = False
            self.pause_momentum = False
            self.vel = self.vel[0] * 1.05, self.vel[1] * 1.05
            self.combo = 0

        self.supersonic = False
        if self.dsq(self.vel) > self.supersonicspeed:
            self.supersonic = True

        if self.polyfirst:
            #print("Yo")
            self.consecutive_misses += 1
            self.combo -= 2
            #self.combo = int(self.combo / 2)
            if self.combo < 1: self.combo = 0
            B = 0.75
            self.vel = self.vel[0] * B, self.vel[1] * B
            self.polynomial = True
            self.polyfirst = False
            if abs(self.vel[0]) > abs(self.vel[1]): self.polytype = "y"
            else: self.polytype = "x"
        #elif self.impact and not self.polynomial:
            #self.consecutive_misses = 0

        if self.consecutive_misses >= 5:
            self.combo = 0
            self.consecutive_misses = 0
            self.disable_controls = True

        if self.polynomial:
            self.pause_momentum = False


        if not self.pause_momentum:
            self.move()
        else:
            #print("hi")
            #print("a")
            #print("hey")
            self.impact = False
            PF = (self.dsq(self.vel)/5000)
            if PF > 2: PF = 1
            #print(PF)
            if time.clock() - self.pause_timer > self.pause_length * PF:
                self.pause_momentum = False

            self.consecutive_misses = 0


        #print(self.consecutive_misses)


class Controls:
    def __init__(self):
        self.region1 = "", ""
        self.region2 = "", ""
        self.disabled = False
        self.disabled_timer = time.clock()
        self.disabled_dt = 3
        self.undisabled = False

        self.space_pressed = False
        self.space_dt = 0.2
        self.space_timer = time.clock()
        self.powerup = "player1"

        self.shuffled = False

        self.controls_inverted = ""

    def set_disabled(self):
        if self.disabled: return
        #print("hey")
        self.region1 = "", ""
        self.region2 = "", ""
        self.disabled = True
        self.disabled_timer = time.clock()

    def update(self):
        if self.disabled:
            if time.clock() - self.disabled_timer > self.disabled_dt:
                self.disabled = False
                self.undisabled = True
            return

        #print("self.controls_inverted)
        P = pygame.key.get_pressed()
        if not self.controls_inverted == "player1":
            KL = K_a
            KU1 = K_w
            KD1 = K_s
            K_P1 = K_d
        elif not self.shuffled:
            self.L = L = [K_a, K_w, K_s, K_d]
            random.shuffle(L)
            self.shuffled = True
            KL, KU1, KD1, K_P1 = self.L
        else:
            KL, KU1, KD1, K_P1 = self.L

        # player1

        if not self.controls_inverted == "player2":
            KR = K_RIGHT
            KU2 = K_UP
            KD2 = K_DOWN
            K_P2 = K_LEFT
        elif not self.shuffled:
            self.L = L = [K_RIGHT, K_UP, K_DOWN, K_LEFT]
            random.shuffle(L)
            self.shuffled = True
            KR, KU2, KD2, K_P2 = self.L
        else:
            KR, KU2, KD2, K_P2 = self.L


        #player2

        self.region1 = "", ""
        if P[KL]: self.region1 = "left", ""
        elif P[KU1]: self.region1 = "top", "left"
        elif P[KD1]: self.region1 = "bot", "left"

        self.region2 = "", ""
        if P[KR]: self.region2 = "right", ""
        elif P[KU2]: self.region2 = "top", "right"
        elif P[KD2]: self.region2 = "bot", "right"

        self.space_pressed = False
        if (time.clock() - self.space_timer > self.space_dt):
            if (P[K_P1]):
                self.space_pressed = True
                self.powerup = "player1"
            elif (P[K_P2]):
                self.space_pressed = True
                self.powerup = "player2"


        """
        if self.region1[0] == "":
            if P[KL]: self.region1 = "left", KL; return
            elif P[KR]: self.region1 = "right", KR; return
            elif P[KU]: self.region1 = "top", KU; return
            elif P[KD]: self.region1 = "bot", KD; return
        elif self.region2[0] == "":
            if P[KL] and self.region1[0] not in ("left", "right"): self.region2 = "left", KL; return
            elif P[KR] and self.region1[0] not in ("left", "right"): self.region2 = "right", KR; return
            elif P[KU] and self.region1[0] not in ("top", "bot"): self.region2 = "top", KU; return
            elif P[KD] and self.region1[0] not in ("top", "bot"): self.region2 = "bot", KD; return
            elif not (P[self.region1[1]]):
                self.region1 = "", 0
        else:
            if not (P[self.region1[1]] and P[self.region2[1]]):
                self.region1 = "", 0
                self.region2 = "", 0
        """

def check_region(r1, r2, r):
    #print(r1, r2, r)
    if r1 == r or r2 == r: return True, True
    if r1[1] == "" and r1[0] == "left" and r[0] == "left": return True, True
    if r2[1] == "" and r2[0] == "right" and r[0] == "right": return True, True

    #if R[0] == r[0]: return True, False
    return False, None


def draw_selected_regions(r1, r2, rect, surf, wmode, pl):
    R = r1, r2
    color = (240,240,240)
    T = 20
    if wmode:
        if pl == "player1":
            A1, B1 = rect.topleft, rect.midtop
            A2, B2 = rect.bottomleft, rect.midbottom
            A3, B3 = rect.topleft, rect.bottomleft
        else:
            A1, B1 = rect.midtop, rect.topright
            A2, B2 = rect.midbottom, rect.bottomright
            A3, B3 = rect.topright, rect.bottomright
        pygame.draw.line(surf, color, A1, B1, T)
        pygame.draw.line(surf, color, A2, B2, T)
        pygame.draw.line(surf, color, A3, B3, T)

        return


    if R[0] == "top":
        A, B = rect.topleft, rect.topright
    elif R[0] == "bot":
        A, B = rect.bottomleft, rect.bottomright
    elif R[0] == "left":
        A, B = rect.topleft, rect.bottomleft
    elif R[0] == "right":
        A, B = rect.topright, rect.bottomright
    else: return
    if R[1] == "":
        pygame.draw.line(surf, color, A, B, T)
        return

    if R[0] == "top" and R[1] == "right":
        A, B = rect.midtop, rect.topright
    elif R[0] == "top" and R[1] == "left":
        A, B = rect.topleft, rect.midtop
    if R[0] == "bot" and R[1] == "left":
        A, B = rect.bottomleft, rect.midbottom
    elif R[0] == "bot" and R[1] == "right":
        A, B = rect.midbottom, rect.bottomright
    if R[0] == "left" and R[1] == "top":
        A, B = rect.topleft, rect.midleft
    elif R[0] == "left" and R[1] == "bot":
        A, B = rect.midleft, rect.bottomleft
    if R[0] == "right" and R[1] == "top":
        A, B = rect.topright, rect.midright
    elif R[0] == "right" and R[1] == "bot":
        A, B = rect.midright, rect.bottomright

    pygame.draw.line(surf, color, A, B, T)


def get_slope(p1, p2):
    x1, y1 = p1
    x2, y2 = p2

    dx = x2-x1
    dy = y2-y1

    try: a = dy/dx
    except ZeroDivisionError: return 0, 0
    b = y1/(a*x1)

    return a, b


class Blip:
    def __init__(self, pos, m, t):
        self.pos = pos
        rx = random.random()-0.5
        ry = random.random()-0.5
        self.vel = rx * m, ry * m
        self.target = t

        self.first_entry = False
        self.explode = False
        self.crazymode = False

    def update(self):
        if self.explode == True and self.crazymode == False:
            self.crazymode = True
            self.explode = False
            Q = 50
            r1, r2 = random.random()*Q-Q/2, random.random()*Q-Q/2
            self.vel = r1, r2
        if self.crazymode:
            self.pos = self.pos[0] + self.vel[0], self.pos[1] + self.vel[1]
            return
        R = (random.random()+0.5)*0.01
        self.vel = (self.target[0]-self.pos[0])*0.01*R + self.vel[0], (self.target[1]-self.pos[1])*0.01*R + self.vel[1]
        d = (self.target[0]-self.pos[0])**2+(self.target[1]-self.pos[1])**2
        if d < 35**2:
            if self.first_entry:
                self.first_entry = False
                velx, vely = self.vel
                self.vel = velx*0.15, vely*0.15
        else:
            self.first_entry = True
        dx = self.vel[0]
        dy = self.vel[1]
        self.pos = self.pos[0] + dx, self.pos[1] + dy

    def draw(self, surf):
        pos = list(map(int, self.pos))
        col = 255, 255, 255
        rad = 7
        pygame.draw.circle(surf, col, pos, rad)

class Death:
    def __init__(self, pos, magnitude, t, p):
        self.p = p
        self.blips = []
        for i in range(magnitude):
            b = Blip(pos, magnitude, t)
            self.blips.append(b)

        self.explode = False
        self.die = False

    def update(self):
        for b in self.blips:
            b.explode = self.explode
            b.update()

        if self.explode == True:
             self.die = True

    def draw(self, surf):
        for b in self.blips:
            b.draw(surf)


class Crate:
    def __init__(self, pos):
        self.pos = pos
        self.timer = time.clock()
        self.dt = 0.25
        self.kill = False
        self.scale = 1

    def update(self):
        pt = time.clock() - self.timer
        self.scale = 10 * (self.dt-pt) + 1

        if pt > self.dt:
            self.kill = True


class Effects:
    def __init__(self):
        self.screen_shake = False
        self.sx, self.sy = 0, 0
        self.shake_timer = time.clock()
        self.shake_dt = 0.15
        self.shake_impact = 10
        self.slope = 1, 1
        self.slope_mode = True

        self.fader_timer = time.clock()
        self.fader_dt = 0.2
        self.fade = False
        self.fadeside = ""
        self.fadevel = 0, 0
        self.fadep = 0, 0
        self.fadespeed = 4
        self.fadeR = pygame.Rect(0,0,0,0)
        self.fadecoloro = 240
        self.fadecolor = 0

        self.deaths = []
        self.target = None
        self.target2 = None
        self.mag = None

        self.explode = False
        self.explode_timer = time.clock()
        self.explode_dt = 1

        self.snd = None

        self.pupasstimer = time.clock()
        self.padt = 2.25

        self.static = None

        self.crates = []
        self.cstatic = None

    def add_crate(self, pos):
        self.crates.append(Crate(pos))

    def set_explode(self):
        self.explode = True
        self.explode_timer = time.clock()

    def add_powerup(self, pup, to):
        self.assignedto = to
        self.pup = pup
        self.pupasstimer = time.clock()
        self.displaypup = True

    def add_death(self, pos, player):
        mag = int(self.mag)
        if mag == 0 or player not in ("player1", "player2"): return
        target = self.target
        if player == "player1":
            target = self.target
        else:
            target = self.target2
        d = Death(pos, mag, target, player)
        self.deaths.append(d)

    def set_fade(self):
        self.fade = True
        self.fader_timer = time.clock()

    def set_fadeside(self, s, r):
        self.safe_rect = r
        self.fade_w = r.w

        if s == "top":
            self.fadevel = 0, -1
            self.fadep = r.x, self.safe_rect.top
            self.fadeR = pygame.Rect(self.fadep, (r.w, 10))
        elif s == "bot":
            self.fadevel = 0, 1
            self.fadep = r.x, self.safe_rect.bottom
            self.fadeR = pygame.Rect(self.fadep, (r.w, 10))
        elif s == "left":
            self.fadevel = -1, 0
            self.fadep = r.left, r.y
            self.fadeR = pygame.Rect(self.fadep, (10, r.h))
        elif s == "right":
            self.fadevel = 1, 0
            self.fadep = r.right, r.y
            self.fadeR = pygame.Rect(self.fadep, (10, r.h))

        #print(s)
        #print(self.fadeR)

    def set_shake(self):
        self.shake_timer = time.clock()
        self.screen_shake = True

    def get_shake(self):
        SI = self.shake_impact
        if self.slope_mode:
            A = self.slope[0]
            if A < 0: pass
            s1 = random.random() * SI - SI/2
            s2 = A * s1
            return s1, s2
        return random.random() * SI - SI/2, random.random() * SI - SI/2

    def set_impact(self, vel, maxv):
        self.shake_impact = 500*(vel[0]**2+vel[1]**2)/maxv**2
        if self.shake_impact > 20:
            self.shake_impact = 20

    def set_slope(self, p1, p2):
        self.slope = get_slope(p1, p2)

    def update(self):
        if time.clock() - self.pupasstimer > self.padt:
            self.displaypup = False

        if time.clock() - self.shake_timer > self.shake_dt:
            self.screen_shake = False

        dt = time.clock() - self.fader_timer
        if dt > self.fader_dt:
            self.fade = False
        else:
            self.fadeR.move_ip(self.fadevel[0] * self.fadespeed, self.fadevel[1] * self.fadespeed)
            self.fadecolor = int(self.fadecoloro * (dt)/self.fader_dt)

        self.total_blips = 0
        if self.explode and time.clock() - self.explode_timer > self.explode_dt:
            i = 0
            kill = []
            for d in self.deaths:
                if d.die:
                    kill.append(i)
                i += 1
            for i in reversed(kill):
                self.deaths.pop(i)
            self.explode_timer = time.clock()
            self.explode = False

        for d in self.deaths:
            d.explode = self.explode
            d.update()
            self.total_blips += len(d.blips)

        if self.total_blips > 180:
            self.deaths.pop()
        #self.explode = False

        kill = []
        i = 0
        for c in self.crates:
            c.update()
            if c.kill:
                kill.append(i)
            i += 1

        for i in reversed(kill):
            self.crates.pop(i)


def dot_product(a, b):
    return a[0]*b[0]+a[1]*b[1]

def normalize(v):
    l = (v[0]**2+v[1]**2)**0.5
    if l == 0: return 0, 0
    return v[0]/l, v[1]/l


class DonkeyKong:
    def __init__(self, hw, h, static):
        self.pos = hw, h
        self.static = static
        self.display = 0

    def update(self):
        if not random.randint(0, 9):
            self.display = 1-self.display


    def draw(self, surf):
        blitme = self.static.images[self.display]
        off = -3
        pos = int(self.pos[0]), int(self.pos[1]-blitme.get_height()-off)
        surf.blit(blitme, pos)


class Firework:
    def __init__(self, s):
        self.pos = s
        self.vel = random.random() * 15 - 7.5, 10+random.random() * 15
        self.a = random.random()/20
        self.kill = False

    def update(self):
        self.vel = self.vel[0], self.vel[1] - self.a
        self.pos = self.pos[0] + self.vel[0], self.pos[1] - self.vel[1]
        if self.pos[1] < -100:
            self.kill = True

    def draw(self, surf):
        surf.blit(self.static, (0,0))

class Fireworks:
    def __init__(self, static, spawnp):
        self.works = []
        self.static = static
        self.spawnp = spawnp

    def update(self):
        i = 0
        kill = []
        for w in self.works:
            w.update()
            if w.kill:
                kill.append(i)
            i += 1

        for i in reversed(kill):
            self.works.pop(i)

        if not random.randint(0, 29):
            n = Firework(self.spawnp)
            self.works.append(n)

    def draw(self, surf):
        for w in self.works:
            if w.vel[0] > 0:
                img = self.static.images[0]
            else:
                img = self.static.images[1]
            surf.blit(img, w.pos)

class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        with open("resolution.txt", "r") as F:
            w, h = list(map(int, F.read().rstrip("\n").split(" ")))
        #w, h = 1700, 900
        self.actual_surf = pygame.display.set_mode((w, h))
        self.surf = pygame.Surface((w, h))
        self.fade_surf = pygame.Surface((w, h))
        self.fade_surf.set_alpha(200)
        self.w, self.h = w, h
        pygame.display.set_caption("bla bla")

        self.clock = pygame.time.Clock()
        self.fps = 144

        self.load_assets()
        self.init_game()

    def load_assets(self):
        self.text = Text()
        self.text.selection = "future"
        self.music = MIDI()
        pygame.mixer.music.set_volume(0.75)
        self.animation, self.banim, self.static, self.pupstatic, self.dkstatic, self.cratestatic = load_art()
        self.sound = Sound()

    def init_game(self):

        b = 50
        self.world_rect = pygame.Rect(b, b, self.w - b*2, self.h - b*2)
        self.bb = BouncingBall()
        self.bb.set_world(self.world_rect)

        self.controls = Controls()

        self.effects = Effects()
        self.effects.target = 70, 70
        self.effects.target2 = self.surf.get_width()-70, self.surf.get_height()-70
        self.effects.snd = self.sound
        self.effects.static = self.pupstatic
        self.effects.cstatic = self.cratestatic

        self.ghosts = Ghosts(self.bb.safe_rect, self.static, self.effects)
        self.ghosts.snd = self.sound

        self.combo = 0

        self.ready = False

        self.whohititlast = ""

        self.kong = DonkeyKong(self.w/2, self.h, self.dkstatic)

        self.first = True
        self.assign_powerup()
        self.powerup_assigned = False
        self.powerup_used = False
        self.effects.displaypup = False
        self.powerup_timer = time.clock()
        self.powerup_dt = 1

        self.warned = False
        self.warned2 = False

        self.barcolor = (200, 200, 200)

        self.fireworks = Fireworks(self.cratestatic, (self.w/2, self.h-110))

    def assign_powerup(self):
        assignedto = random.choice(("player1", "player2"))
        self.powerup_type = random.choice(("boom", "control", "wall"))
        self.effects.add_powerup(self.powerup_type, assignedto)
        self.assignedto = assignedto
        if not self.first: self.sound.play("ready")
        self.first = False
        self.powerup_assigned = True

    def update(self):
        if not pygame.mixer.music.get_busy():
            track = self.playing = random.choice(self.music.tracks)
            pygame.mixer.music.load("midi/"+track)
            pygame.mixer.music.play()

            self.song_timer = time.clock()
            mid = self.song_file = mido.MidiFile("midi/"+track)

            self.tracks = {}
            for i, track in enumerate(mid.tracks):
                #print('Track {}: {}'.format(i, track.name))
                self.tracks[track.name] = [i, track, 0, True]

            self.maintrack = None
            self.tiers = "main", "drums", "guitar"
            for t in self.tiers:
                try:
                    self.maintrack = [t, self.tracks[t]]
                    
                except KeyError:
                    pass
            if self.maintrack == None:
                K = list(self.tracks.keys())[0]
                self.maintrack = [K, self.tracks[K]]

            self.ticks_per_beat = mid.ticks_per_beat
            #print(self.ticks_per_beat)
            self.tempo = 120
            #print(mid.tempo)
            #print(self.maintrack)
            #self.track_index = 0
        #self.port.send(self.L[i])
        #self.n+=1
        #msg = self.track[self.track_index]
        #print(msg)
        #self.track_index += 1

        if self.maintrack[1][3]: # if next message
            self.maintrack[1][3] = False
            mt = self.maintrack[1][1]
            self.msg = mt[self.maintrack[1][2]]

            self.first = True

            self.maintrack[1][2] += 1 # index
        else:
            # process midi until next message
            msg = self.msg
            #print(msg, msg.time)
            if msg.time == 0:
                #print("ho")
                self.msgtimer = time.clock()
                self.msgdt = 0
                self.maintrack[1][3] = True
                self.first = False
            elif self.first == True:
                self.ghosts.spawn()
                self.first = False
                #print("hi")
                self.msgtimer = time.clock()
                self.msgdt = mido.tick2second(msg.time, self.ticks_per_beat, self.tempo)
                #mido.ti

            if time.clock() - self.msgtimer > self.msgdt:
                self.maintrack[1][3] = True

        self.fireworks.update()

        self.bb.update()
        if self.bb.impact:
            self.sound.play("bounce")

        self.controls.update()
        #print(self.controls.region1, self.controls.region2)
        if self.bb.impact:
            chk = check_region(self.controls.region1, self.controls.region2, self.bb.region)
            if chk[0] and chk[1] or self.powerup_used and self.powerup_type == "wall" and ((self.bb.pos[0] < self.bb.safe_rect.centerx and self.assignedto == "player1") \
             or (self.bb.pos[0] > self.bb.safe_rect.centerx and self.assignedto == "player2")):
                if self.bb.pos[0] < self.bb.safe_rect.centerx:
                    self.whohititlast = "player1"
                else:
                    self.whohititlast = "player2"
                self.bb.vel = self.bb.vel[0] * self.bb.speedup, self.bb.vel[1] * self.bb.speedup
            else:
                self.bb.polyfirst = True
                if self.bb.pos[0] < self.bb.safe_rect.centerx:
                    self.bb.tug += 1 # player 1 is hurt
                    if self.whohititlast == "player1": self.whohititlast = ""
                else:
                    self.bb.tug -= 1 # player 2 is hurt
                    if self.whohititlast == "player2": self.whohititlast = ""

        if self.bb.impact:
            self.effects.set_shake()
            self.effects.set_impact(self.bb.vel, self.bb.MAXV)
            self.effects.set_slope(self.bb.ppos, self.bb.pos)

            self.effects.set_fade()
            self.effects.set_fadeside(self.bb.region[0], self.bb.safe_rect)

        self.effects.mag = self.bb.combo/4 #+ 1+9*(self.bb.dsq(self.bb.vel) / self.bb.MAXV**2) +
        #self.effects.mag = 10
        self.effects.update()

        self.animation.update()

        line = self.bb.ppos, self.bb.pos
        self.ghosts.update(line, self.whohititlast)

        self.combo = self.bb.combo


        if self.bb.disable_controls:
            self.bb.disable_controls = False
            self.bb.consecutive_misses = 0
            #self.controls.set_disabled()
        #if self.controls.undisabled:
            #self.controls.undisabled = False
            #self.bb.consecutive_misses = 0
        #if self.bb.explode:
            #self.controls.set_disabled()

        #print(self.controls.space_pressed, self.powerup_assigned)
        if self.controls.space_pressed and self.effects.total_blips >= 60 and self.powerup_assigned and not self.powerup_used:
            self.ghosts.set_explode(self.controls.powerup)
            self.effects.set_explode()
            if self.powerup_type == "boom":
                self.bb.set_explode()
                self.controls.set_disabled()
                self.sound.play("boom")
            elif self.powerup_type == "control":
                self.sound.play("control")
                invertme = {"player1":"player2", "player2":"player1"}[self.assignedto]
                self.controls.controls_inverted = invertme
            elif self.powerup_type == "wall":
                self.sound.play("wall")
                self.bb.walled = True
            self.controls.space_timer = time.clock()
            self.controls.space_pressed = False
            #self.sound.play()
            self.powerup_used = True
            #self.ready = False
            self.powerup_timer = time.clock()
            if self.powerup_type == "boom":
                self.powerup_dt = 3
            elif self.powerup_type == "wall":
                self.powerup_dt = 5
            else:
                self.powerup_dt = 4


        #print(self.controls.controls_inverted)
        if time.clock() - self.powerup_timer > self.powerup_dt and self.powerup_used:
            self.powerup_used = False
            self.controls.controls_inverted = ""
            self.bb.walled = False
            self.bb.explode = False
            self.powerup_assigned = False
            self.controls.shuffled = False

        if self.effects.total_blips >= 60 and not self.powerup_assigned:
            self.assign_powerup()
            self.ready = True
            #self.powerup_used = False
        elif self.effects.total_blips < 60:
            #self.powerup_used = False
            self.ready = False
            self.controls.undisabled = False
            #self.powerup_assigned = False

        if self.bb.tug - self.bb.tug_size >= 0:
            self.init_game()
        elif self.bb.tug + self.bb.tug_size <= 0:
            self.init_game()

        if self.bb.tug - self.bb.tug_size >= -30:
            if not self.warned:
                self.sound.play("warning")
                self.warned = True
                self.barcolor = 255,0,0
        else:
            self.warned = False
            if not self.warned2: self.barcolor=(200, 200, 200)

        if self.bb.tug + self.bb.tug_size <= 30:
            if not self.warned2:
                self.sound.play("warning")
                self.warned2 = True
                self.barcolor = 255,0,0
        else:
            self.warned2 = False
            if not self.warned: self.barcolor=(200, 200, 200)

        self.g1 = self.ghosts.p1kills
        self.ghosts.p1kills = 0
        self.g2 = self.ghosts.p2kills
        self.ghosts.p2kills = 0
        self.bb.tug -= self.g1 * 0.2
        self.bb.tug += self.g2 * 0.2

        self.kong.update()

        #print(self.ghosts.p1kills, self.ghosts.p2kills)

    def draw(self):
        #self.surf.blit(self.static.images[0], (0, 0))
        #pygame.draw.rect(self.surf, (50, 50, 50), self.world_rect, 0)
        self.surf.blit(self.text.get(self.playing, (0, 200, 0)), (150, 80))
        #self.surf.blit(self.text.get(self.playing, (0, 200, 0)), (self.surf.get_width()-150-500, self.surf.get_height()-80-140))
        for d in self.effects.deaths:
            d.draw(self.surf)
        self.ghosts.draw(self.surf, self.bb.pos)
        self.surf.blit(self.fade_surf, (0,0))
        col1 = 0, 0, 80
        pygame.draw.rect(self.surf, col1, self.bb.safe_rect, 2)
        r2 = pygame.Rect(self.bb.safe_rect)
        r2.move_ip(-2,-2)
        col2 = 0, 0, 220
        pygame.draw.rect(self.surf, col2, self.bb.safe_rect, 1)
        if self.powerup_type == "wall" and self.powerup_used:
            wall_mode = True
        else:
            wall_mode = False
        player = self.assignedto
        for z in (self.controls.region1, self.controls.region2):
            draw_selected_regions(z[0], z[1], self.bb.safe_rect, self.surf, wall_mode, player)
        if self.effects.fade:
            R = self.effects.fadeR
            C = self.effects.fadecolor
            pygame.draw.rect(self.surf, (C,C,C), R)
            self.text.selection = "future"
            fadetext = self.text.get("x"+str(self.combo), (C, C, C))
            mid = self.actual_surf.get_width()/2 - 40, self.actual_surf.get_height()/2 - 70
            self.surf.blit(fadetext, mid)

        S, B = get_slope(self.bb.ppos, self.bb.pos)

        if self.bb.supersonic and not self.bb.pause_momentum:
            bp = self.bb.pos
            bpp = self.bb.ppos
            Q1 = bp[0], bp[1]+15
            Q2 = bpp[0], bpp[1]+15
            pygame.draw.line(self.surf, (200, 200, 0), list(map(int, Q2)), list(map(int, Q1)), 20)

            v = Q1[0]-Q2[0], Q1[1]-Q2[1]
            perp = normalize((v[1], -v[0]))
            n = perp
            #d = v1
            #t = 2*dot_product(d, n)
            #q1, q2 = n[0]*t, n[1]*t
            #r = d[0] - q1, d[1] - q2
            F = 25
            c1 = Q1[0] + perp[0] * F, Q1[1] + perp[1] * F
            c2 = Q1[0] - perp[0] * F, Q1[1] - perp[1] * F
            plist = c1, c2, Q2
            pygame.draw.polygon(self.surf, (200, 200, 0), plist)
        #pygame.draw.circle(self.surf, (0,200,200), list(map(int, self.bb.pos)) , self.bb.rad)
        ox = self.animation.images[0].get_width()/2
        oy = self.animation.images[0].get_height()/2
        bbx, bby = self.bb.pos
        pacx = int(bbx - ox)
        pacy = int(bby - oy)
        paccy = pacx, pacy

        try: angle = math.degrees(math.atan(S)) - 90
        except ZeroDivisionError: angle = 0
        angle = -angle - 90
        if self.bb.vel[0] < 0:
            angle = angle + 180
        #print(angle, S)
        rotated = pygame.transform.rotate(self.animation.get_frame(), angle)
        self.surf.blit(rotated, paccy)

        tugo = self.bb.tug
        B = 0
        P1 = self.surf.get_width()/2-self.bb.tug_size+tugo, 30
        P2 = self.surf.get_width()/2+self.bb.tug_size+tugo, 30
        hp = P1[0] + (P2[0]-P1[0])/2
        hp1 = hp-B, 30
        hp2 = hp+B, 30
        pygame.draw.line(self.surf, self.barcolor, list(map(int,P1)), list(map(int,hp1)), 20)
        pygame.draw.line(self.surf, self.barcolor, list(map(int,hp2)), list(map(int,P2)), 20)
        hw = int(self.surf.get_width()/2)
        A = hw, 0
        Z = hw, 60
        pygame.draw.line(self.surf, (0, 0, 0), A, Z, 6)

        self.kong.draw(self.surf)

        if int((time.clock() - self.effects.pupasstimer) * 24) % 4 != 0:
            displayit = True
        else:
            displayit = False

        if (self.effects.displaypup and displayit):
            hw = self.effects.static.images[0].get_width()
            hh = self.effects.static.images[0].get_height()
            if self.effects.assignedto == "player1":
                pos = self.w/4-hw, 110-hh
            else:
                pos = self.w*3/4-hw, 110-hh
            if self.effects.pup == "wall":
                pup = self.effects.static.images[0]
            if self.effects.pup == "control":
                pup = self.effects.static.images[1]
            if self.effects.pup == "boom":
                pup = self.effects.static.images[2]
            self.surf.blit(pup, list(map(int, pos)))

        if (self.powerup_assigned and self.powerup_used == False) and self.effects.displaypup == False:
            hw = self.effects.static.images[0].get_width()
            hh = self.effects.static.images[0].get_height()
            if self.effects.assignedto == "player1":
                pos = self.w/4-hw, 110-hh
            else:
                pos = self.w*3/4-hw, 110-hh
            if self.effects.pup == "wall":
                pup = self.effects.static.images[0]
            if self.effects.pup == "control":
                pup = self.effects.static.images[1]
            if self.effects.pup == "boom":
                pup = self.effects.static.images[2]
            self.surf.blit(pup, list(map(int, pos)))

        self.fireworks.draw(self.surf)

#############################
        q2i = [0, 1, 2, 3]
        for c in self.effects.crates:
            cx, cy = c.pos
            if cx > self.w/2:
                if cy > self.h/2:
                    quadrant = 3
                else:
                    quadrant = 0
            else:
                if cy > self.h/2:
                    quadrant = 2
                else:
                    quadrant = 1
            ind = q2i[quadrant]
            img = self.effects.cstatic.images[ind]
            for i in range(int(c.scale**0.75)):
                img = pygame.transform.scale2x(img)
            bx = cx - img.get_width()/2 + 50
            by = cy - img.get_height()/2 + 50
            self.surf.blit(img, (bx, by))
        #if self.controls.disabled:
            #self.fade_surf.set_alpha(200)
            #self.surf.blit(self.fade_surf, (0, 0))
            #self.fade_surf.set_alpha(100)


    def loop(self):
        while True:
            self.update()

            self.surf.fill((0,0,0))
            self.draw()
            #self.actual_surf.fill((0,0,0))
            if self.effects.screen_shake:
                sx, sy = self.effects.get_shake()
            else:
                sx, sy = 0, 0
            self.actual_surf.blit(self.surf, (sx, sy))
            pygame.display.update()

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    return

            self.clock.tick(self.fps)




if __name__ == "__main__":
    g = Game()
    g.loop()




# DO:
"""
midi spawning
"""
