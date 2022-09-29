from scene import *
from math import pi
from random import uniform as rnd, choice, randint
import sys
import random
from math import *
A = Action
sys.setrecursionlimit(1000000)

colors = ['pzl:Green5', "pzl:Red5", "pzl:Blue5"] + ["pzl:Purple5", "pzl:Button2"] + ["plf:Item_CoinGold"]
global inited
inited = False
class Explosion (Node):
    def __init__(self, brick, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)
        self.position = brick.position
        for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            p = SpriteNode(brick.texture, scale=0.5, parent=self)
            p.position = brick.size.w/4 * dx, brick.size.h/4 * dy
            p.size = brick.size
            d = 0.6
            r = 30
            p.run_action(A.move_to(rnd(-r, r), rnd(-r, r), d))
            p.run_action(A.scale_to(0, d))
            p.run_action(A.rotate_to(rnd(-pi/2, pi/2), d))
        self.run_action(A.sequence(A.wait(d), A.remove()))

class Brick (SpriteNode):
    def __init__(self, brick_type, *args, **kwargs):
        img = colors[brick_type]
        SpriteNode.__init__(self, img, *args, **kwargs)
        self.brick_type = brick_type
        self.is_on = True
        self.lf = True
        self.enabled = True
    
    def destroy(self):
        self.remove_from_parent()
        self.is_on = False
    
    def mark(self):
        self.lf = False
    
    def demark(self):
        self.lf = True

class Game(Scene):
    def brickgetpos(self, i, j):
        return (self.Woff + j * self.W, self.Hoff + i * self.H)
    
    def brick(self, ty, i, j):
        b = Brick(ty, size=(self.W, self.H), position=self.brickgetpos(i, j), parent=self.game_node)
        b.rotation = random.random()
        return b

    def random_brick_type(self):
        if random.random() < 0.992:
            return random.randint(0, 3)
        else:
            if random.random() < 0.8:
                return 5
            else:
                return 4
    def setup(self):
        FONT = ('Chalkduster', 20)
        self.score_label = LabelNode('Score: 0', font=FONT, position=(self.size.w/2-100, self.size.h-40), parent=self)
        self.score = 0
        self.last_score_label = LabelNode('Delta: +0', font=FONT, position=(self.size.w/2-300, self.size.h-40), parent=self)
        self.last_score = 0
        #self.avg_label = LabelNode('Speed: +0/s', font=FONT, position=(self.size.w/2+100, self.size.h-40), parent=self)
        #self.max_label = LabelNode('Peak: +0/s', font=FONT, position=(self.size.w/2+300, self.size.h-40), parent=self)
        #self.max_speed = 0
        self.game_time = 120
        self.timel = LabelNode('Time: ' + str(self.game_time) + "s", font=FONT, position=(self.size.w/2+300, self.size.h-40), parent=self)
        self.gems = [0 for i in colors]
        self.effect_node = EffectNode(parent=self)
        self.game_node = Node(parent=self.effect_node)
        self.l = [0 for i in colors]
        self.lt = [0 for i in colors]
        for i in range(len(colors)):
            R = 50 if i == 6 else 35
            self.l[i] = Brick(i, size=(R, R), position=(40, self.size.h-100-i*40), parent=self.game_node)
            self.lt[i] = LabelNode(": 0", font=FONT, position=(self.l[i].position[0] + 40, self.l[i].position[1]), parent=self)
        self.WB = 30
        self.HB = 30
        self.W = 900 // self.WB
        self.H = 900 // self.HB
        self.colcount = 4
        self.Woff = (int(self.size.w) - self.W * self.WB + self.W) // 2
        self.Hoff = self.H + 10

        self.net = [[self.brick(self.random_brick_type(), i, j) for i in range(self.HB)] for j in range(self.WB)]
        
        #self.touch_moved = self.touch_began
        self.start_time = self.t
        self.game_on = True
        
        global inited
        inited = True
    
    def demark(self):
        for bricks in self.net:
            for brick in bricks:
                brick.demark()
    
    def howfar(self, x, y):
        alt = 0
        for i in range(y):
            if not self.net[x][i].is_on:
                alt += 1
        return alt
    
    def update(self):
        global inited
        if not inited:
            return
        self.game_on = self.t - self.start_time < self.game_time
        if self.game_on:
            self.timel.text = "Time: " + str(round(self.game_time - (self.t - self.start_time))) + "s"
        else:
            self.timel.text = "Game over"
        #if speed > self.max_speed:
        #    self.max_speed = speed
        #    self.max_label.text = "Peak: +" + str(round(self.max_speed)) + "/s"
    
    def gravity(self, x, y):
        alt = self.howfar(x, y)
        if alt == 0:
            return
        
        self.net[x][y].destroy()
        self.net[x][y - alt] = self.brick(self.net[x][y].brick_type, y, x)
        self.net[x][y - alt].position = self.net[x][y].position
        self.net[x][y - alt].rotation = self.net[x][y].rotation
        self.net[x][y - alt].enabled = False
        self.net[x][y - alt].run_action(A.sequence(A.move_to(*self.brickgetpos(y - alt, x), 0.2 * alt ** 0.5, TIMING_EASE_IN_2), A.call(lambda: self.enable_cell(x, y - alt))))
    
    def enable_cell(self, x, y):
        self.net[x][y].enabled = True
    
    def fall(self):
        for x in range(self.WB):
            for y in range(self.HB):
                if self.net[x][y].is_on:
                    self.gravity(x, y)
    
    def update_scores(self):
        self.score += self.last_score
        self.score_label.text = "Score: " + str(self.score)
        self.last_score_label.text = "Delta: +" + str(self.last_score)
        self.last_score = 0
    
    def update_cells(self):
        for i in range(self.WB):
            for j in range(self.HB):
                if not self.net[i][j].is_on:
                    self.net[i][j] = self.brick(self.random_brick_type(), j + self.HB, i)
                    self.net[i][j].enabled = True
                    self.net[i][j].run_action(A.sequence(A.move_to(*self.brickgetpos(j, i), 0.2 * self.HB ** 0.5, TIMING_EASE_IN_2), A.call(lambda: self.enable_cell(i, j))))
    
    def inbounds(self, x, y):
        return (x >= 0) and (y >= 0) and (x < self.WB) and (y < self.HB)
    
    def bomb(self, x, y, radius):
        score = 0
        bc = 0
        for i in range(round(4 * radius ** 2)):
            rad = random.random() * radius
            ang = random.random() * 2 * pi
            xp, yp = x + sin(ang) * rad, y + cos(ang) * rad
            xp, yp = int(xp), int(yp)
            if self.inbounds(xp, yp):
                score += self.explode(xp, yp)
        self.fall()
        self.give_score(round(score / 1.7), self.brickgetpos(y, x))
    
    def laser(self, x, y):
        score = 0
        coords = []
        for i in range(self.HB):
            for j in range(-1, 1 + 1, 1):
                coords.append((x + j, i))
        for i in range(self.WB):
            coords.append((i, y))
        for i in range(-self.HB, self.HB):
            coords.append((x + i, y + i))
        for i in range(-self.WB, self.WB):
            coords.append((x - i, y + i))
        bc = 0
        for x, y in coords:
            if not self.inbounds(x, y):
                continue
            score += self.explode(x, y)
        self.fall()
        self.give_score(score, self.brickgetpos(y, x))
    
    def getty(self, x, y):
        if not self.inbounds(x, y) or not self.net[x][y].is_on:
            return -1
        else:
            return self.net[x][y].brick_type
    
    def popupt(self, text, position_, font_=("Arial", 30), color_="white"):
        label = LabelNode(text, font=font_, color=color_, parent=self, position=position_)
        label.run_action(A.sequence(A.wait(1), A.call(label.remove_from_parent)))
    
    def give_score(self, count, xy):
        self.last_score = int(count ** 2.5)
        size = 10
        if self.last_score > 50000:
            size = 60
        elif self.last_score > 20000:
            size = 40
        elif self.last_score > 10000:
            size = 30
        elif self.last_score > 5000:
            size = 25
        elif self.last_score > 2000:
            size = 20
        elif self.last_score > 1000:
            size = 15
        if self.last_score > 0:
            self.popupt("+" + str(self.last_score), xy, font_=("Chalkduster", int(size * 1.5)))
        self.update_scores()
    
    def touch_began(self, touch):
        if not self.game_on:
            return
        x, y = touch.location
        x, y = x + self.W / 2, y + self.H / 2
        W, H = get_screen_size()
        x, y = x, y
        x, y = int(x), int(y)
        x, y = x - self.Woff, y - self.Hoff
        x, y = x // self.W, y // self.H
        if not self.inbounds(x, y):
            return
        
        count = self.react(self.net[x][y].brick_type, x, y, True)
        self.demark()
        if self.getty(x, y) in [0, 1, 2, 3]:
            if count >= 2:
                self.react(self.net[x][y].brick_type, x, y)
                self.fall()
                self.give_score(count, touch.location)
        elif self.getty(x, y) == 4:
            self.bomb(x, y, 5 * count)
        elif self.getty(x, y) == 5:
            self.explode(x, y)
            self.fall()
        self.update_cells()
    
    def explode(self, x, y):
        if self.net[x][y].is_on:
            self.net[x][y].destroy()
            self.gems[self.net[x][y].brick_type] += 1
            s = str(self.gems[self.net[x][y].brick_type])
            self.lt[self.net[x][y].brick_type].text = " " * len(s) +  ": " + s
            self.game_node.add_child(Explosion(self.net[x][y]))
            return True
        else:
            return False
    
    def react(self, col, x, y, ignore=False):
        if self.inbounds(x, y) and self.net[x][y].brick_type == col and self.net[x][y].is_on and self.net[x][y].lf and self.net[x][y].enabled:
            if not ignore:   
                self.explode(x, y)
            else:
                self.net[x][y].mark()
            r = 1
            r += self.react(col, x + 1, y + 0, ignore)
            r += self.react(col, x - 1, y - 0, ignore)
            r += self.react(col, x + 0, y + 1, ignore)
            r += self.react(col, x - 0, y - 1, ignore)
            return r
        else:
            return 0
    
    def destroy_brick(self, x, y):
        self.net[x][y].destroy()
        
run(Game(), LANDSCAPE, show_fps=True)
