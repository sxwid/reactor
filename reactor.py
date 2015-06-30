#!/usr/bin/python
# -*- encoding: utf-8 -*-

__version__ = "1.0"
# $Source$

from time import sleep
import pygame
from pygame.locals import *
import datetime
import time
import os
import sys
import traceback
import fnmatch
import random
import signal
import threading 
from enocean.consolelogger import init_logging
from enocean.communicators.serialcommunicator import SerialCommunicator
from enocean.protocol.packet import Packet
from enocean.protocol.constants import PACKET, RORG
try:
    import queue
except ImportError:
    import Queue as queue

# Generell
TITEL               = 'reactor'
LIZENZ              = u'free'

SW_MAX              = 8
SW_MIN              = 2
DEF_MIN_WAITTIME    = 2.0
DEF_MAX_WAITTIME    = 4.5
DEF_DIST_L          = 6.0
DEF_DIST_S          = 4.0
DEF_OFFSET_M        = 0.1
DEF_OFFSET_S        = 0.1
DEF_SCORE_OFFSET    = 1
DEF_SCORE           = 20
DEF_TIME_OFFSET     = 5
DEF_TIME            = 60
SCR_SETTINGS        = 4
SCR_GAME            = 5

SCR_SET1            = 0
SCR_SET2            = 1
SCR_SET3            = 2
SCR_SET4            = 3
SCR_SETUP           = SCR_SETTINGS
SCR_INIT            = SCR_SETTINGS+1
SCR_GMSEL           = SCR_SETTINGS+2
SCR_GMSTART         = SCR_SETTINGS+3
SCR_GMRUN           = SCR_SETTINGS+4
SCR_RESULTS         = SCR_SETTINGS+5
SCR_ABORT           = SCR_SETTINGS+6

# Pygame Events
EV_SERIAL_INPUT = pygame.USEREVENT + 1
EV_TIMEREVENT = pygame.USEREVENT + 2
EV_GAMESTARTED = pygame.USEREVENT + 3
EV_ABORT = pygame.USEREVENT + 4
EV_MOUSEBUTTON = pygame.USEREVENT + 5
PYGAME_FPS = 20
MOUSEDELAY = 250
if os.path.exists('/home/pi/icons'):
    on_raspi = True
    with_thread = True
else:
    on_raspi = False
    with_thread = False
sys_init = False
id_list = []

# UI related
if on_raspi == True:
    iconPath    = '/home/pi/icons' # Subdirectory containing UI bitmaps (PNG format)
else:
    pass
SCREEN_WIDTH	= 800
SCREEN_HEIGHT	= 480
BAR_HEIGHT      = 50
DEFAULT_OFFSET  = 15
BT_HEIGHT       = 75
BT_WIDTH        = 130
BT_OFFSET       = 10
BT_SETTINGS     = SCREEN_WIDTH - DEFAULT_OFFSET - BT_WIDTH
BT_1            = DEFAULT_OFFSET
BT_2            = DEFAULT_OFFSET + 1*BT_OFFSET+1*BT_WIDTH
BT_3            = DEFAULT_OFFSET + 2*BT_OFFSET+2*BT_WIDTH
BT_4            = DEFAULT_OFFSET + 3*BT_OFFSET+3*BT_WIDTH
BT_CORN         = 5

VIS_HEIGHT      = SCREEN_HEIGHT-2*BAR_HEIGHT-2*DEFAULT_OFFSET
VIS_WIDTH       = VIS_HEIGHT
VIS_OFF_X       = DEFAULT_OFFSET
VIS_OFF_Y       = BAR_HEIGHT+DEFAULT_OFFSET

INFO_HEIGHT     = SCREEN_HEIGHT-2*BAR_HEIGHT-2*DEFAULT_OFFSET
INFO_WIDTH      = SCREEN_WIDTH-3*DEFAULT_OFFSET-VIS_WIDTH
INFO_OFF_X      = VIS_WIDTH + 2*DEFAULT_OFFSET
INFO_OFF_Y      = BAR_HEIGHT+DEFAULT_OFFSET

LN_OFFSET       = 5
LN_1            = INFO_OFF_Y + LN_OFFSET
LN_2            = LN_1 + BT_HEIGHT + LN_OFFSET
LN_3            = LN_2 + BT_HEIGHT + LN_OFFSET
LN_4            = LN_3 + BT_HEIGHT + LN_OFFSET
LN_5            = LN_4 + BT_HEIGHT + LN_OFFSET
LN_START        = INFO_OFF_X + DEFAULT_OFFSET
LN_END          = INFO_OFF_X + INFO_WIDTH - DEFAULT_OFFSET

SW_XSZ          = 75
SW_YSZ          = 75

SW_X = [
((VIS_WIDTH-3*SW_XSZ)/4)*1 + 0*SW_XSZ + VIS_OFF_X,
((VIS_WIDTH-3*SW_XSZ)/4)*2 + 1*SW_XSZ + VIS_OFF_X,
((VIS_WIDTH-3*SW_XSZ)/4)*3 + 2*SW_XSZ + VIS_OFF_X,
((VIS_WIDTH-3*SW_XSZ)/4)*1 + 0*SW_XSZ + VIS_OFF_X,
((VIS_WIDTH-3*SW_XSZ)/4)*2 + 1*SW_XSZ + VIS_OFF_X,
((VIS_WIDTH-3*SW_XSZ)/4)*3 + 2*SW_XSZ + VIS_OFF_X,
((VIS_WIDTH-3*SW_XSZ)/4)*1 + 0*SW_XSZ + VIS_OFF_X,
((VIS_WIDTH-3*SW_XSZ)/4)*2 + 1*SW_XSZ + VIS_OFF_X,
((VIS_WIDTH-3*SW_XSZ)/4)*3 + 2*SW_XSZ + VIS_OFF_X
]

SW_Y = [
((VIS_HEIGHT-3*SW_YSZ)/4)*1 + 0*SW_YSZ + VIS_OFF_Y,
((VIS_HEIGHT-3*SW_YSZ)/4)*1 + 0*SW_YSZ + VIS_OFF_Y,
((VIS_HEIGHT-3*SW_YSZ)/4)*1 + 0*SW_YSZ + VIS_OFF_Y,
((VIS_HEIGHT-3*SW_YSZ)/4)*2 + 1*SW_YSZ + VIS_OFF_Y,
((VIS_HEIGHT-3*SW_YSZ)/4)*2 + 1*SW_YSZ + VIS_OFF_Y,
((VIS_HEIGHT-3*SW_YSZ)/4)*2 + 1*SW_YSZ + VIS_OFF_Y,
((VIS_HEIGHT-3*SW_YSZ)/4)*3 + 2*SW_YSZ + VIS_OFF_Y,
((VIS_HEIGHT-3*SW_YSZ)/4)*3 + 2*SW_YSZ + VIS_OFF_Y,
((VIS_HEIGHT-3*SW_YSZ)/4)*3 + 2*SW_YSZ + VIS_OFF_Y
]

# Farben
COLOR_BLACK     =   (  0,   0,   0)
COLOR_WHITE     =   (255, 255, 255)
COLOR_RED       =   (255,   0,   0)
COLOR_LGREEN    =   (  0, 140,   0)
COLOR_DGREEN    =   (  0, 153,   0)
COLOR_DDGREEN   =   (  0, 100,   0)
COLOR_GREEN     =   (  0, 255,   0)
COLOR_BLUE      =   (  0,   0, 255)
COLOR_BT        =   COLOR_DDGREEN
COLOR_BG        =   COLOR_DGREEN
COLOR_FG        =   COLOR_LGREEN
COLOR_FONT      =   COLOR_WHITE
COLOR_FONT_HL   =   COLOR_RED
COLOR_PASSIVE   =   COLOR_DDGREEN
COLOR_ACTIVE    =   COLOR_RED

#---Klassen---#FFFFFF#0000FF----------------------------------------------------

class Icon:
    def __init__(self, name):
        self.name = name
        try:
            self.bitmap = pygame.image.load(iconPath + '/' + name + '.png')
        except:
            pass


# Button erstellen mit Text oder Icon
class Button:
    def __init__(self, rect, **kwargs):
        self.rect       = rect # Bounds
        self.color      = None # Background fill color, if any
        self.iconBg     = None # Background Icon (atop color fill)
        self.iconFg     = None # Foreground Icon (atop background)
        self.bg         = None # Background Icon name
        self.fg         = None # Foreground Icon name
        self.callback   = None # Callback function
        self.value      = None # Value passed to callback
        self.corner     = None # Round corners
        self.text	    = None # Text
        self.cord_x 	= self.rect[0]
        self.cord_y 	= self.rect[1]
        self.size_x 	= self.rect[2]
        self.size_y 	= self.rect[3]
        pygame.font.init()
        self.font	= pygame.font.SysFont("Arial", 25)
        for key, value in kwargs.iteritems():
            if   key == 'color' : self.color    = value
            elif key == 'bg'    : self.bg       = value
            elif key == 'fg'    : self.fg       = value
            elif key == 'cb'    : self.callback = value
            elif key == 'val'   : self.value    = value
            elif key == 'corner': self.corner   = value
            elif key == 'text'	: self.text   	= value

    def selected(self, pos):
        x1 = self.rect[0]
        y1 = self.rect[1]
        x2 = x1 + self.rect[2] - 1
        y2 = y1 + self.rect[3] - 1
        if ((pos[0] >= x1) and (pos[0] <= x2) and (pos[1] >= y1) and (pos[1] <= y2)):
            if self.callback:
                if self.value is None: 
                    self.callback()
                else:
                    self.callback(self.value)
            return True
        return False

    def draw(self, screen):
        if self.color and not self.corner:
            screen.fill(self.color, self.rect)
        if self.color and self.corner:
            if self.cord_y+self.size_y == SCREEN_HEIGHT:
                pygame.draw.rect(screen, self.color, (self.cord_x,self.cord_y+2*self.corner,self.size_x,self.size_y-2*self.corner))
                pygame.draw.rect(screen, self.color, (self.cord_x+2*self.corner,self.cord_y,self.size_x-4*self.corner,2*self.corner))
                pygame.draw.circle(screen, self.color, (self.cord_x+2*self.corner,self.cord_y+2*self.corner), 2*self.corner, 0)
                pygame.draw.circle(screen, self.color, (self.cord_x+self.size_x-2*self.corner,self.cord_y+2*self.corner), 2*self.corner, 0)
            else:
                pygame.draw.rect(screen, self.color, (self.cord_x,self.cord_y+2*self.corner,self.size_x,self.size_y-4*self.corner))
                pygame.draw.rect(screen, self.color, (self.cord_x+2*self.corner,self.cord_y,self.size_x-4*self.corner,2*self.corner))
                pygame.draw.rect(screen, self.color, (self.cord_x+2*self.corner,self.cord_y+self.size_y-2*self.corner,self.size_x-4*self.corner,2*self.corner))
                pygame.draw.circle(screen, self.color, (self.cord_x+2*self.corner,self.cord_y+2*self.corner), 2*self.corner, 0)
                pygame.draw.circle(screen, self.color, (self.cord_x+self.size_x-2*self.corner,self.cord_y+2*self.corner), 2*self.corner, 0)
                pygame.draw.circle(screen, self.color, (self.cord_x+2*self.corner,self.cord_y+self.size_y-2*self.corner), 2*self.corner, 0)
                pygame.draw.circle(screen, self.color, (self.cord_x+self.size_x-2*self.corner,self.cord_y+self.size_y-2*self.corner), 2*self.corner, 0)
        if self.iconFg:
            screen.blit(self.iconFg.bitmap,(self.rect[0]+(self.rect[2]-self.iconFg.bitmap.get_width())/2,self.rect[1]+(self.rect[3]-self.iconFg.bitmap.get_height())/2))
        if self.text:
            lb = self.font.render(self.text, 1, COLOR_FONT)
            lb_x = self.cord_x+self.size_x/2-self.font.size(self.text)[0]/2
            lb_y = self.cord_y+self.size_y/2-self.font.size(self.text)[1]/2
            screen.blit(lb, (lb_x,lb_y))
        if self.iconBg:
            screen.blit(self.iconBg.bitmap,(self.rect[0]+(self.rect[2]-self.iconBg.bitmap.get_width())/2,self.rect[1]+(self.rect[3]-self.iconBg.bitmap.get_height())/2))

    def setBg(self, name):
        if name is None:
            self.iconBg = None
        else:
            for i in icons:
                if name == i.name:
                    self.iconBg = i
                    break

# Grundeinstellungen des Spiels (Delays, Konstanten, Setup vom Spielfeld
class GameSettings:
    def __init__(self):
        self.init = False
        self.min_waittime = DEF_MIN_WAITTIME
        self.max_waittime = DEF_MAX_WAITTIME
        self.distance_l = DEF_DIST_L
        self.distance_s = DEF_DIST_S
        self.switch = SW_MIN
        self.sw_active = None
        self.offset_m = DEF_OFFSET_M
        self.offset_s = DEF_OFFSET_S
        self.state = ""
        self.used = None
        self.nr = []
        self.id = []
        # Erstelle erste Liste mit Konfiguration
        self.set_sw(self.switch)

    # Allgemeine Einstellungen
    def set_state(self,text):
        self.state = text
        
    def set_min_waittime_up(self):
        if self.min_waittime < self.max_waittime:
            self.min_waittime += DEF_OFFSET_S

    def set_max_waittime_up(self):
        self.max_waittime += 0.1

    def set_min_waittime_down(self):
        if self.min_waittime > DEF_OFFSET_S:
            self.min_waittime -= DEF_OFFSET_S

    def set_max_waittime_down(self):
        if self.max_waittime > self.min_waittime:
            self.max_waittime -= DEF_OFFSET_S
        
    def set_init(self):
        self.init = True

    def set_distance_l_up(self):
        self.distance_l += DEF_OFFSET_M
        
    def set_distance_s_up(self):
        if self.distance_s < self.distance_l-DEF_OFFSET_M:
            self.distance_s += DEF_OFFSET_M
        
    def set_distance_l_down(self):
        if self.distance_l > 10*DEF_OFFSET_M and self.distance_l-DEF_OFFSET_M > self.distance_s:
            self.distance_l -= DEF_OFFSET_M
        
    def set_distance_s_down(self):
        if self.distance_s > 10*DEF_OFFSET_M:
            self.distance_s -= DEF_OFFSET_M

    def set_sw_up(self):
        if self.switch < SW_MAX:
            self.init_ids = False
            self.switch += 1
            self.set_sw(self.switch)
            
    def set_sw_down(self):
        if self.switch > SW_MIN:
            self.init_ids = False
            self.switch -= 1
            self.set_sw(self.switch)

    # Erhalte Anzahl gebrauchter Switches (int)
    def get_sw(self):
        return self.used

    # Erhalte Momentanen Spielmodus (str)
    def get_state(self):
        return self.state
    
    def get_min_waittime(self):
        return self.min_waittime

    def get_max_waittime(self):
        return self.max_waittime

    # Erhalte ein Zufallsdelay zwischen den zwei Zeit Thresholds in ms
    def get_wait_delay(self):
        delay_s = random.uniform(self.min_waittime,self.max_waittime)
        delay_ms = int(delay_s*1000)
        return delay_ms

    def get_init(self):
        return self.init

    # Erhalte Distanz weit
    def get_distance_l(self):
        return self.distance_l

    # Erhalte Distanz nah
    def get_distance_s(self):
        return self.distance_s
    
    # Update Liste mit Switches
    def set_sw(self, switch):
        self.used = switch
        # Lösche alte Liste
        for i in range(0,len(self.nr)): 
            del self.nr[-1]
        # Erstelle neue Liste
        if self.used == 2:
            self.nr.append(0)
            self.nr.append(2)    
        elif self.used == 3:
            self.nr.append(0)
            self.nr.append(1)
            self.nr.append(2)    
        elif self.used == 4:
            self.nr.append(0)
            self.nr.append(2)    
            self.nr.append(6)
            self.nr.append(8)    
        elif self.used == 5:
            self.nr.append(0)
            self.nr.append(1)
            self.nr.append(2)    
            self.nr.append(6)
            self.nr.append(8)    
        elif self.used == 6:
            self.nr.append(0)
            self.nr.append(1)
            self.nr.append(2)    
            self.nr.append(6)
            self.nr.append(7)
            self.nr.append(8)    
        elif self.used == 7:
            self.nr.append(0)
            self.nr.append(1)
            self.nr.append(2)
            self.nr.append(3)
            self.nr.append(5)    
            self.nr.append(6)
            self.nr.append(8)    
        elif self.used == 8:
            self.nr.append(0)
            self.nr.append(1)
            self.nr.append(2)
            self.nr.append(3)
            self.nr.append(5)    
            self.nr.append(6)
            self.nr.append(7)
            self.nr.append(8) 

    # Initialisiere Switches für korrekte IDs    
    def set_id(self, senderid):
        valid = True
        # Stelle sicher, dass Switch noch nicht in Liste
        for i in range(0,len(self.id)):
            if self.id[i] == senderid:
                valid = False
        # Bei gültiger Eingabe ID registrieren
        if valid == True:
            self.id.append(senderid)
            self.sw_active = None
            if self.get_sw() == len(self.id):
                self.init = True
     
    # Erhalte Liste mit benutzten Switchs ([])
    def get_sw_list(self):
        return self.nr
  
    # Erhalte Liste mit benutzten IDs ([])
    def get_id_list(self):
        return self.id

    # Erhalte die ID von einem Switch (Array-Index)
    def get_id(self, switch):
        if switch >= len(self.id):
            return None
        elif switch <= self.used and bool(self.id) is True:
            if bool(self.id[switch]) is True:
                return self.id[switch]
            else:
                return None
        else:
            return None
        
    # Erhalte den Array-Index zu einer ID
    def get_nr(self, ID):
        for i in range(0,len(self.id)):
            if self.id[i] == ID:
                return i
        else:
            return None

    # Initialisieren der Switches
    def sw_init(self):
        # Wenn kein Switch am initialisieren ist, gehe einen Schritt weiter
        if self.sw_active == None and self.init == False:
            # Suche ersten nicht initialisierten Switch
            i=0
            while i <= self.get_sw()-1:
                if self.get_id(i) is not None:
                    i+=1
                else:
                    self.sw_active = self.nr[i]
                    break
        # Wenn alle Switches initialisiert sind oder Initialisierung laueft mache nichts
        else:
            pass

    # Erhalte aktive Switch-Nummer
    def get_active(self):
        return self.sw_active            

    # Setze aktive Switch-Nummer
    def set_active(self,sw):
        self.sw_active = sw
        
    def reset_sw(self):
        self.sw_active = None
        self.init = False
        for i in range(0,len(self.id)): 
            del self.id[-1]
            
# Spielablauf während dem Spiel
class Game:
    def __init__(self, settings):
        self.obj_set = settings
        self.score = 0
        self.tm_start_game = None
        self.tm_stop_game = None
        self.tm_start_run = None
        self.tm_stop_run = None
        self.avg_speed = 0
        self.distance = 0
        self.fastest_time = None
        self.slowest_time = None
        self.def_score = DEF_SCORE
        self.def_time = DEF_TIME        
        self.game_started = False
        self.run_started = False
        self.mode_time = False
        self.mode_score = False
        self.mode_random = False
        self.mode_speed = False
        self.last_sw = -1

    def reset_values(self):
        self.score = 0
        self.tm_start_game = None
        self.tm_stop_game = None
        self.tm_start_run = None
        self.tm_stop_run = None
        self.avg_speed = 0
        self.distance = 0
        self.fastest_time = None
        self.slowest_time = None
        self.def_score = DEF_SCORE
        self.def_time = DEF_TIME        
        self.game_started = False
        self.run_started = False
        self.mode_time = False
        self.mode_score = False 
        self.mode_random = False
        self.mode_speed = False
        self.last_sw = -1 
        self.obj_set.set_active(None)      
    
    def start_game(self):
        self.game_started = True
        self.tm_start_game = datetime.datetime.now()
        startevent = pygame.event.Event(EV_GAMESTARTED, mode=0)
        pygame.event.post(startevent)
        print self.tm_start_game
        
    def stop_game(self, time):
        self.game_started = False
        self.tm_stop_game = time
        startevent = pygame.event.Event(EV_GAMESTARTED, mode=1)
        pygame.event.post(startevent)
        print self.tm_stop_game
        
    def start_run(self, switch):
        list = self.obj_set.get_sw_list()
        self.obj_set.set_active(list[switch]) 
        self.tm_start_run = datetime.datetime.now()
        print "Starte Run", switch, list[switch]

    def stop_run(self, time):
        self.tm_stop_run = time
        self.last_sw = self.obj_set.get_active()
        # Score +1
        self.score += 1
        delta = self.tm_stop_run-self.tm_start_run
        if (self.obj_set.get_active()%2):
            speed = self.obj_set.get_distance_s()/delta.total_seconds()
            self.distance += self.obj_set.get_distance_s()
        else:
            speed = self.obj_set.get_distance_l()/delta.total_seconds()
            self.distance += self.obj_set.get_distance_l()
        if self.avg_speed == 0:
            self.avg_speed = speed
        else:
            tmp = self.avg_speed*(self.score-1) + speed
            self.avg_speed = tmp/self.score
        # Setze aktiven sw auf None 
        self.obj_set.set_active(None)
        print speed, "m/s"
    
    def reset_run(self):
        self.game_started = False

    def get_def_score(self):
        return self.def_score
    
    def get_score(self):
        return self.score
  
    def get_def_time(self):
        return self.def_time

    def get_mode_time(self):
        return self.mode_time
    
    def get_mode_score(self):
        return self.mode_score
    
    def get_start_time(self):
        return self.tm_start_game
    
    def get_stop_time(self):
        return self.tm_stop_game
    
    def set_def_score_up(self):
        self.set_def_score(1)

    def set_def_score_down(self):
        self.set_def_score(-1)

    def set_def_score(self, direction):
        if direction is 1:
            self.def_score += DEF_SCORE_OFFSET
        elif direction is -1:
            if self.def_score >= 2*DEF_SCORE_OFFSET:
                self.def_score -= DEF_SCORE_OFFSET
        elif direction is 0:
            self.def_score = DEF_SCORE
 
    def set_def_time_up(self):
        self.set_def_time(1)

    def set_def_time_down(self):
        self.set_def_time(-1)

    def set_def_time(self, direction):
        if direction is 1:
            self.def_time += DEF_TIME_OFFSET
        elif direction is -1:
            if self.def_time >= 2*DEF_TIME_OFFSET:
                self.def_time -= DEF_TIME_OFFSET
        elif direction is 0:
            self.def_time = DEF_TIME
   
    def start_time_random(self):
        self.mode_time = True
        self.mode_random = True
        self.mode_speed = False
        self.start_game()
        
    def start_score_random(self):
        self.mode_score = True
        self.mode_random = True
        self.mode_speed = False
        self.start_game()

    def start_time_speed(self):
        self.mode_time = True
        self.mode_random = False
        self.mode_speed = True
        self.start_game()
        
    def start_score_speed(self):
        self.mode_score = True
        self.mode_random = False
        self.mode_speed = True
        self.start_game()

    def get_remaining_time(self):
        time_rem = self.get_def_time()-(datetime.datetime.now()-self.get_start_time()).total_seconds()
        if time_rem < 0:
            # Stop Run workaround
            pygame.time.set_timer(EV_TIMEREVENT, 0)
            self.obj_set.set_active(None)
            self.stop_game(datetime.datetime.now())
        return time_rem

    def get_av_speed(self):
        return format(self.avg_speed,'.2f')

    def get_distance(self):
        return format(self.distance,'.0f')

    def sw_input_handler(self, id, tm):
        # Initialisieren
        if self.obj_set.get_init() is False:
            self.obj_set.set_id(id)
            self.obj_set.sw_init()

        # Zeige gedrückte Switches an
        elif self.obj_set.get_init() is True and self.game_started is False: 
            list = self.obj_set.get_sw_list()
            self.obj_set.set_active(list[self.obj_set.get_nr(id)])

        # Spiel
        elif self.game_started == True and self.obj_set.get_active() != None:
            # Prüfe ob korrekter Switch gedrückt wurde
            list = self.obj_set.get_sw_list()
            if list[self.obj_set.get_nr(id)] == self.obj_set.get_active():
                # Stoppe Run und werte aus
                self.stop_run(tm)
                # Werte aus ob Game weitergeht?
                if self.mode_score is True:
                    if self.score < self.def_score:
                        # Starte neue Runde zu random Switch
                        if self.mode_random is True:
                            pygame.time.set_timer(EV_TIMEREVENT, self.obj_set.get_wait_delay())
                        elif self.mode_speed is True:
                            pygame.time.set_timer(EV_TIMEREVENT, 0)
                            time.sleep(0.001)
                            if self.last_sw < len(self.obj_set.get_sw_list()):
                                self.start_run(self.last_sw+1)
                            else:
                                self.start_run(0)
                    else:
                        self.stop_game(tm)
                elif self.mode_time is True:
                    if (datetime.datetime.now() - self.tm_start_game) < datetime.timedelta(seconds=self.def_time):
                        # Starte Timer für nächsten Run
                        if self.mode_random is True:
                            pygame.time.set_timer(EV_TIMEREVENT, self.obj_set.get_wait_delay())
                        elif self.mode_speed is True:
                            pygame.time.set_timer(EV_TIMEREVENT, 0)
                            time.sleep(0.001)
                            if self.last_sw < len(self.obj_set.get_sw_list()):
                                self.start_run(self.last_sw+1)
                            else:
                                self.start_run(0)
                    else:
                        self.stop_game(tm)

        
    def abort_game(self):
        abortevent = pygame.event.Event(EV_ABORT)
        pygame.event.post(abortevent)
        

# Klasse für Grafisches
class UI:
    def __init__(self, settings, game):
        global sys_init
        self._running = True
        self._display_surf = None
        self.obj_set = settings
        self.obj_gm = game
        self.screen = SCR_SETTINGS
        self.last_screen = self.screen
        self.buttons = []
        self.icons = []
        self.font = None
        self.size = self.weight, self.height = SCREEN_WIDTH, SCREEN_HEIGHT
        self.states = ["Einstellungen Zeit","Einstellungen Distanzen","Einstellungen Spiel","Einstellungen Programm","Setup waehlen","Initialisiere Bodenplatten",u'Spielmodus waehlen',u'Spiel laeuft',"Resultat","Abbrechen"]
        self.clock = None
        self.button_cnt = 0

    def on_init(self):
        # Clock initialisieren
        print "Starte Pygame"
        self.clock = pygame.time.Clock()
        # Fonts initialisieren
        print "Initialisiere Schrifte"
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 25)
        print "Mauszeiger ausblenden"
        #pygame.mouse.set_visible(False)
        print "Initialisiere Bildschirm"
        if on_raspi is True:
            self._display_surf = pygame.display.set_mode(self.size,pygame.FULLSCREEN)
        else:
            self._display_surf = pygame.display.set_mode(self.size)           
        self._display_surf.fill(COLOR_BG)
        pygame.display.update()
         
        # Buttons erstellen
        self.create_buttons()
        self._running = True
 
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self.end_program()
        elif(event.type is KEYDOWN):
            key = pygame.key.get_pressed()
            if key[pygame.K_ESCAPE]:
                self.end_program()
        elif(event.type is MOUSEBUTTONDOWN):
            self.call_fct() 
            pygame.time.set_timer(EV_MOUSEBUTTON, MOUSEDELAY)
        elif(event.type is MOUSEBUTTONUP):
            pygame.time.set_timer(EV_MOUSEBUTTON, 0)
            self.button_cnt = 0
        elif(event.type is EV_SERIAL_INPUT):
            if self.screen == SCR_INIT or self.screen == SCR_GMSTART:
                self.obj_gm.sw_input_handler(event.id, event.tm)
        elif(event.type is EV_TIMEREVENT):
            pygame.time.set_timer(EV_TIMEREVENT, 0)
            self.obj_gm.start_run(random.randint(0,self.obj_set.get_sw()-1))
        elif(event.type is EV_MOUSEBUTTON):
            if self.button_cnt >= 5 and self.button_cnt < 10:
                pygame.time.set_timer(EV_MOUSEBUTTON, MOUSEDELAY/2)
            elif self.button_cnt >= 10 and self.button_cnt < 20:
                pygame.time.set_timer(EV_MOUSEBUTTON, MOUSEDELAY/4)
            elif self.button_cnt >= 20:
                pygame.time.set_timer(EV_MOUSEBUTTON, MOUSEDELAY/10)
            self.button_cnt += 1
            self.call_fct()	
        elif(event.type is EV_GAMESTARTED):
            if event.mode == 0:
                self.obj_gm.start_run(random.randint(0,self.obj_set.get_sw()-1))
                self.screen = SCR_GMSTART
            elif event.mode == 1:
                self.screen = SCR_GMRUN
        elif(event.type is EV_ABORT):
            self.scr_set(SCR_SETTINGS+SCR_GAME)

    def on_loop(self):
        self.dynamic_content()
        self.clock.tick(PYGAME_FPS)

    def on_render(self):
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()
 
    def on_execute(self):
        if self.on_init() == False:
            self._running = False
        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()

    # Navigierfunktionen im Menu
    def scr_back(self):
        self.last_screen = self.screen
        if self.screen > SCR_SETTINGS:
            self.screen -= 1
        self.obj_set.set_active(None)

    def scr_next(self):
        self.last_screen = self.screen
        if self.screen < SCR_ABORT:
            self.screen += 1
        self.obj_set.set_active(None)

    def start_init_sw(self):
        self.scr_next()
        self.obj_set.sw_init()

    def choose_game(self):
        if self.obj_set.get_init() == True:
            self.obj_set.set_active(None)
            self.scr_next()
        
    def scr_set(self, scr):
        if self.screen > SCR_SETTINGS:
            self.last_screen = self.screen
        self.screen = scr

    def call_fct(self):
        if pygame.mouse.get_pressed()[0]:
            pos = pygame.mouse.get_pos()
            for b in self.buttons[self.screen]:
                if b.selected(pos): break   

    def reset_everything(self):
        self.obj_set.reset_sw()
        self.obj_gm.reset_values()
        self.scr_set(SCR_SETTINGS+0)
        
    def end_program(self):
        sys_init = False
        time.sleep(1)
        self._running = False

    def shutdown(self):
        self.end_program()
        os.system("shutdown now -h")      
        
    def restart_game(self):
        self.obj_gm.reset_values()
        self.scr_set(SCR_GMSEL)
        
    def scr_last(self):
        tmp = self.screen
        self.screen = self.last_screen
        if tmp > SCR_SETTINGS:
            self.last_screen = tmp

    # Zeichenfunktionen für Buttons, Labels, Switches und Visualisierungen
    def draw_vis(self):
        initialized_switches = self.obj_set.get_sw_list()
        for i in range(0,len(initialized_switches)): 
            if self.obj_set.get_active() == initialized_switches[i]:
                self.draw_switch_coord(self._display_surf,SW_X[initialized_switches[i]], SW_Y[initialized_switches[i]], SW_XSZ, SW_YSZ,COLOR_ACTIVE, 2)
            else:
                self.draw_switch_coord(self._display_surf,SW_X[initialized_switches[i]], SW_Y[initialized_switches[i]], SW_XSZ, SW_YSZ,COLOR_PASSIVE, 2)

    def draw_switch_coord(self,screen,cord_x, cord_y, size_x, size_y, color, corner):
        pygame.draw.rect(screen, color, (cord_x,cord_y+2*corner,size_x,size_y-4*corner))
        pygame.draw.rect(screen, color, (cord_x+2*corner,cord_y,size_x-4*corner,2*corner))
        pygame.draw.rect(screen, color, (cord_x+2*corner,cord_y+size_y-2*corner,size_x-4*corner,2*corner))
        pygame.draw.circle(screen, color, (cord_x+2*corner,cord_y+2*corner), 2*corner, 0)
        pygame.draw.circle(screen, color, (cord_x+size_x-2*corner,cord_y+2*corner), 2*corner, 0)
        pygame.draw.circle(screen, color, (cord_x+2*corner,cord_y+size_y-2*corner), 2*corner, 0)
        pygame.draw.circle(screen, color, (cord_x+size_x-2*corner,cord_y+size_y-2*corner), 2*corner, 0)

    def create_buttons(self):
        print "Erstelle Buttons"
        self.buttons = [
            # Screen 0 settings
            [Button((  BT_1,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg="bt_time", cb=self.scr_set, val=SCR_SET1, color= COLOR_BT, corner=BT_CORN),
             Button((  BT_2,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg="bt_dist", cb=self.scr_set, val=SCR_SET2, color= COLOR_BT, corner=BT_CORN),
             Button((  BT_3,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg="bt_game", cb=self.scr_set, val=SCR_SET3, color= COLOR_BT, corner=BT_CORN),
             Button((  BT_4,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg="bt_general", cb=self.scr_set, val=SCR_SET4, color= COLOR_BT, corner=BT_CORN),
             Button((  BT_SETTINGS,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg='bt_retour', cb=self.scr_last, color= COLOR_BT, corner=BT_CORN),
             Button((  LN_START,LN_2,BT_HEIGHT,BT_HEIGHT), cb=self.obj_set.set_min_waittime_down, color=COLOR_BT, corner=BT_CORN, text="<"),
             Button((  LN_START+200,LN_2,BT_HEIGHT,BT_HEIGHT), cb=self.obj_set.set_min_waittime_up, color=COLOR_BT, corner=BT_CORN, text=">"),
             Button((  LN_START,LN_4,BT_HEIGHT,BT_HEIGHT), cb=self.obj_set.set_max_waittime_down, color=COLOR_BT, corner=BT_CORN, text="<"),
             Button((  LN_START+200,LN_4,BT_HEIGHT,BT_HEIGHT), cb=self.obj_set.set_max_waittime_up, color=COLOR_BT, corner=BT_CORN, text=">")],

            # Screen 1 settings
            [Button((  BT_1,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg="bt_time", cb=self.scr_set, val=SCR_SET1, color= COLOR_BT, corner=BT_CORN),
             Button((  BT_2,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg="bt_dist", cb=self.scr_set, val=SCR_SET2, color= COLOR_BT, corner=BT_CORN),
             Button((  BT_3,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg="bt_game", cb=self.scr_set, val=SCR_SET3, color= COLOR_BT, corner=BT_CORN),
             Button((  BT_4,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg="bt_general", cb=self.scr_set, val=SCR_SET4, color= COLOR_BT, corner=BT_CORN),
             Button((  BT_SETTINGS,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg='bt_retour', cb=self.scr_last, color= COLOR_BT, corner=BT_CORN),
             Button((  LN_START,LN_2,BT_HEIGHT,BT_HEIGHT), cb=self.obj_set.set_distance_s_down, color=COLOR_BT, corner=BT_CORN, text="<"),
             Button((  LN_START+200,LN_2,BT_HEIGHT,BT_HEIGHT), cb=self.obj_set.set_distance_s_up, color=COLOR_BT, corner=BT_CORN, text=">"),
             Button((  LN_START,LN_4,BT_HEIGHT,BT_HEIGHT), cb=self.obj_set.set_distance_l_down, color=COLOR_BT, corner=BT_CORN, text="<"),
             Button((  LN_START+200,LN_4,BT_HEIGHT,BT_HEIGHT), cb=self.obj_set.set_distance_l_up, color=COLOR_BT, corner=BT_CORN, text=">")],

            # Screen 2 settings
            [Button((  BT_1,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg="bt_time", cb=self.scr_set, val=SCR_SET1, color= COLOR_BT, corner=BT_CORN),
             Button((  BT_2,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg="bt_dist", cb=self.scr_set, val=SCR_SET2, color= COLOR_BT, corner=BT_CORN),
             Button((  BT_3,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg="bt_game", cb=self.scr_set, val=SCR_SET3, color= COLOR_BT, corner=BT_CORN),
             Button((  BT_4,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg="bt_general", cb=self.scr_set, val=SCR_SET4, color= COLOR_BT, corner=BT_CORN),
             Button((  LN_START,LN_2,BT_HEIGHT,BT_HEIGHT), cb=self.obj_gm.set_def_time_down,  color=COLOR_BT, corner=BT_CORN, text="<"),
             Button((  LN_START+200,LN_2,BT_HEIGHT,BT_HEIGHT), cb=self.obj_gm.set_def_time_up, color=COLOR_BT, corner=BT_CORN, text=">"),
             Button((  LN_START,LN_4,BT_HEIGHT,BT_HEIGHT), cb=self.obj_gm.set_def_score_down, color=COLOR_BT, corner=BT_CORN, text="<"),
             Button((  LN_START+200,LN_4,BT_HEIGHT,BT_HEIGHT), cb=self.obj_gm.set_def_score_up, color=COLOR_BT, corner=BT_CORN, text=">"),
             Button((  BT_SETTINGS,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg='bt_retour',cb=self.scr_last, color= COLOR_BT, corner=BT_CORN)],

            # Screen 3 settings
            [Button((  BT_1,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg="bt_time", cb=self.scr_set, val=SCR_SET1, color= COLOR_BT, corner=BT_CORN),
             Button((  BT_2,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg="bt_dist", cb=self.scr_set, val=SCR_SET2, color= COLOR_BT, corner=BT_CORN),
             Button((  BT_3,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg="bt_game", cb=self.scr_set, val=SCR_SET3, color= COLOR_BT, corner=BT_CORN),
             Button((  BT_4,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg="bt_general", cb=self.scr_set, val=SCR_SET4, color= COLOR_BT, corner=BT_CORN),
             Button((  LN_START,LN_2,BT_WIDTH,BT_HEIGHT), bg='bt_shutdown', cb=self.shutdown, color= COLOR_BT, corner=BT_CORN),
             Button((  LN_END-BT_WIDTH,LN_2,BT_WIDTH,BT_HEIGHT), cb=self.end_program, bg='bt_exit', color= COLOR_BT, corner=BT_CORN),
             Button((  LN_START,LN_4,BT_WIDTH,BT_HEIGHT), bg='bt_reset',cb=self.reset_everything, color= COLOR_BT, corner=BT_CORN),
             Button((  BT_SETTINGS,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg='bt_retour',cb=self.scr_last, color= COLOR_BT, corner=BT_CORN)],

          # Screen 3 init_setup
            [Button((  BT_2,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg='bt_next', cb=self.start_init_sw, color= COLOR_BT, corner=BT_CORN),
             Button((  BT_SETTINGS,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg='bt_settings', val=SCR_SET1, cb=self.scr_set, color= COLOR_BT, corner=BT_CORN),
             Button((  LN_START,LN_2,BT_HEIGHT,BT_HEIGHT), cb=self.obj_set.set_sw_down, color=COLOR_BT, corner=BT_CORN, text="<"),
             Button((  LN_START+175,LN_2,BT_HEIGHT,BT_HEIGHT), cb=self.obj_set.set_sw_up, color=COLOR_BT, corner=BT_CORN, text=">")],

          # Screen 4 init_switches
            [Button((  BT_2,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg='bt_next', cb=self.choose_game, color= COLOR_BT, corner=BT_CORN),
             Button((  BT_SETTINGS,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg='bt_settings', val=SCR_SET1, cb=self.scr_set, color= COLOR_BT, corner=BT_CORN),],

          # Screen 5 game_ready
            [Button((  BT_1,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg='bt_back', cb=self.scr_back, color= COLOR_BT, corner=BT_CORN),
             Button((  LN_START,LN_2,150,BT_HEIGHT), bg='bt_speed', cb=self.obj_gm.start_time_speed, color=COLOR_BT, corner=BT_CORN),
             Button((  LN_START,LN_4,150,BT_HEIGHT), bg='bt_speed', cb=self.obj_gm.start_score_speed, color=COLOR_BT, corner=BT_CORN),
             Button((  LN_END-150,LN_2,150,BT_HEIGHT), bg='bt_random', cb=self.obj_gm.start_time_random, color=COLOR_BT, corner=BT_CORN),
             Button((  LN_END-150,LN_4,150,BT_HEIGHT), bg='bt_random', cb=self.obj_gm.start_score_random, color=COLOR_BT, corner=BT_CORN),
             Button((  BT_SETTINGS,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg='bt_settings', val=SCR_SET1, cb=self.scr_set, color= COLOR_BT, corner=BT_CORN)],

          # Screen 6 game_running
            [Button((  BT_2,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg='bt_no', cb=self.obj_gm.abort_game, color= COLOR_BT, corner=BT_CORN)],

          # Screen 7 game_results
            [Button((  BT_1,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg='bt_reset', cb=self.restart_game, color= COLOR_BT, corner=BT_CORN),
             Button((  BT_SETTINGS,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg='bt_settings', val=SCR_SET1, cb=self.scr_set, color= COLOR_BT, corner=BT_CORN)],

          # Screen 8 game_results            
            [Button((  LN_START,LN_3,100,BT_HEIGHT), bg='bt_no', cb=self.scr_set, val=SCR_GMSTART,color=COLOR_BT, corner=BT_CORN),
             Button((  LN_START+200,LN_3,100,BT_HEIGHT), bg='bt_yes', cb=self.restart_game, color=COLOR_BT, corner=BT_CORN),
             Button((  BT_SETTINGS,SCREEN_HEIGHT-BAR_HEIGHT,BT_WIDTH,BAR_HEIGHT), bg='bt_settings', val=SCR_SET1, cb=self.scr_set, color= COLOR_BT, corner=BT_CORN)]
        ]
        
        print "Lade Icons"
        # Load all icons at startup.
        for file in os.listdir(iconPath):
            if fnmatch.fnmatch(file, '*.png'):
                self.icons.append(Icon(file.split('.')[0]))

        # Assign Icons to Buttons, now that they're loaded
        print"Ordne Buttons zu"
        for s in self.buttons:        # For each screenful of buttons...
            for b in s:            #  For each button on screen...
                for i in self.icons:      #   For each icon...
                    if b.bg == i.name: #    Compare names; match?
                        b.iconBg = i     #     Assign Icon to Button
                        b.bg     = None  #     Name no longer used; allow garbage collection
                    if b.fg == i.name:
                        b.iconFg = i
                        b.fg     = None 
    
    def create_text(self):
        if self.screen == SCR_SET1:
            self.create_lb(u'Verzoegerung MIN [s]',LN_1,LN_START)
            self.create_lb(str(self.obj_set.get_min_waittime()),LN_2,(2*LN_START+200)/2) 
            self.create_lb(u'Verzoegerung MAX [s]',LN_3,LN_START)
            self.create_lb(str(self.obj_set.get_max_waittime()),LN_4,(2*LN_START+200)/2) 
        if self.screen == SCR_SET2:
            self.create_lb(u'Distanz Platten kurz [m]',LN_1,LN_START)
            self.create_lb(str(self.obj_set.get_distance_s()),LN_2,(2*LN_START+200)/2) 
            self.create_lb(u'Distanz Platten lang [m]',LN_3,LN_START)
            self.create_lb(str(self.obj_set.get_distance_l()),LN_4,(2*LN_START+200)/2) 
        if self.screen == SCR_SET3:
            self.create_lb(u'Zeit Spiel [s]',LN_1,LN_START)
            self.create_lb(str(self.obj_gm.get_def_time()),LN_2,(2*LN_START+200)/2) 
            self.create_lb(u'Score Spiel []',LN_3,LN_START)
            self.create_lb(str(self.obj_gm.get_def_score()),LN_4,(2*LN_START+200)/2) 
        if self.screen == SCR_SET4:
            self.create_lb(u'Version:',LN_1,LN_START) 
            self.create_lb(__version__,LN_1,LN_START+100)
        elif self.screen == SCR_SETUP:
            self.create_lb(u'Anzahl Platten waehlen',LN_1,LN_START)
            self.create_lb(str(self.obj_set.get_sw()),LN_2,LN_START+100)            
        elif self.screen == SCR_INIT:
            if self.obj_set.get_init() is False:
                self.create_lb(u'Initialisieren...',LN_1,LN_START)
            else:
                self.create_lb(u'Initialisierung erfolgreich!',LN_1,LN_START)
        elif self.screen == SCR_GMSEL:
            self.create_lb(u'Zeitmodus',LN_1,LN_START)
            self.create_lb(u'Scoremodus',LN_3,LN_START)
        elif self.screen == SCR_GMSTART:
            if self.obj_gm.get_mode_time():
                self.create_lb(u'Score:',LN_1,LN_START)
                self.create_lb(str(self.obj_gm.get_score()),LN_1,LN_START+200) 
                self.create_lb_highlight(u'Zeit',LN_2,LN_START)
                self.create_lb_highlight(str("{0:.2f}".format(self.obj_gm.get_remaining_time())),LN_2,LN_START+200) 
                self.create_lb_highlight(u's',LN_2,LN_START+300) 
                self.create_lb(u'Geschwindigkeit',LN_3,LN_START)
                self.create_lb(str(self.obj_gm.get_av_speed()),LN_3,LN_START+200)
                self.create_lb(u'm/s',LN_3,LN_START+300)
                self.create_lb(u'Distanz',LN_4,LN_START)
                self.create_lb(str(self.obj_gm.get_distance()),LN_4,LN_START+200)
                self.create_lb(u'm',LN_4,LN_START+300)
            if self.obj_gm.get_mode_score():
                self.create_lb_highlight(u'Score:',LN_1,LN_START)
                self.create_lb_highlight(str(self.obj_gm.get_def_score()-self.obj_gm.get_score()),LN_1,LN_START+200) 
                self.create_lb(u'Zeit',LN_2,LN_START)
                self.create_lb(str("{0:.2f}".format((datetime.datetime.now()-self.obj_gm.get_start_time()).total_seconds())),LN_2,LN_START+200) 
                self.create_lb(u's',LN_2,LN_START+300)
                self.create_lb(u'Geschwindigkeit',LN_3,LN_START)
                self.create_lb(str(self.obj_gm.get_av_speed()),LN_3,LN_START+200)
                self.create_lb(u'm/s',LN_3,LN_START+300)
                self.create_lb(u'Distanz',LN_4,LN_START)
                self.create_lb(str(self.obj_gm.get_distance()),LN_4,LN_START+200)
                self.create_lb(u'm',LN_4,LN_START+300)
        elif self.screen == SCR_GMRUN:
            self.create_lb(u'Score:',LN_1,LN_START)
            self.create_lb(str(self.obj_gm.get_score()),LN_1,LN_START+200) 
            self.create_lb(u'Zeit',LN_2,LN_START)
            self.create_lb(str("{0:.2f}".format((self.obj_gm.get_stop_time()-self.obj_gm.get_start_time()).total_seconds())),LN_2,LN_START+200)
            self.create_lb(u's',LN_2,LN_START+300) 
            self.create_lb(u'Geschwindigkeit',LN_3,LN_START)
            self.create_lb(str(self.obj_gm.get_av_speed()),LN_3,LN_START+200)
            self.create_lb(u'm/s',LN_3,LN_START+300)
            self.create_lb(u'Distanz',LN_4,LN_START)
            self.create_lb(str(self.obj_gm.get_distance()),LN_4,LN_START+200)
            self.create_lb(u'm',LN_4,LN_START+300)
        elif self.screen == SCR_RESULTS:
            self.create_lb(u'Wirklich abbrechen?',LN_1,LN_START)


    def dynamic_content(self):
        self._display_surf.fill(COLOR_BG)
        # Statuszeile
        pygame.draw.rect(self._display_surf, COLOR_FG, (0,0,SCREEN_WIDTH,BAR_HEIGHT))

        # Menuzeile
        #pygame.draw.rect(screen, COLOR_FG, (0,SCREEN_HEIGHT-BAR_HEIGHT,SCREEN_WIDTH,BAR_HEIGHT))

        # Visualisierung
        pygame.draw.rect(self._display_surf, COLOR_FG, (VIS_OFF_X,VIS_OFF_Y,VIS_WIDTH,VIS_HEIGHT))
        #self._display_surf.blit(img_logo, (VIS_WIDTH/2-img_logo.get_width()/2+DEFAULT_OFFSET,VIS_HEIGHT/2-img_logo.get_height()/2+BAR_HEIGHT+DEFAULT_OFFSET))

        # Infobereich
        pygame.draw.rect(self._display_surf, COLOR_FG, (INFO_OFF_X,INFO_OFF_Y,INFO_WIDTH,INFO_HEIGHT))
        
        # Update Status
        self.obj_set.set_state(self.states[self.screen])

        # Statuszeile Inhalt
        d = datetime.datetime.now()
        label = self.font.render(d.strftime("%d.%m.%y - %H:%M:%S") , 1, COLOR_FONT)
        lb_y = BAR_HEIGHT/2 - self.font.size(d.strftime("%d.%m.%y - %H:%M:%S"))[1]/2
        self._display_surf.blit(label, (SCREEN_WIDTH-250, lb_y))

        label = self.font.render(self.obj_set.get_state(), 1, COLOR_FONT)
        lb_y = BAR_HEIGHT/2 - self.font.size(self.obj_set.get_state())[1]/2
        self._display_surf.blit(label, (DEFAULT_OFFSET, lb_y))
        
        #Labels
        self.create_text()
        
        #Visuals
        self.draw_vis()


        for i,b in enumerate(self.buttons[self.screen]):
            b.draw(self._display_surf)
            
    def create_lb(self, text, line, inset):
        label = self.font.render(text, 1, COLOR_FONT)
        lb_y = line + BT_HEIGHT/2 - self.font.size(str(text))[1]/2
        self._display_surf.blit(label, (inset,lb_y))

    def create_lb_highlight(self, text, line, inset):
        label = self.font.render(text, 1, COLOR_FONT_HL)
        lb_y = line + BT_HEIGHT/2 - self.font.size(str(text))[1]/2
        self._display_surf.blit(label, (inset,lb_y))


# Thread, generiert einen Event mit Attribut id=X und tm=Y bei einem enocean Input
def seriallistener():
    global on_raspi, sys_init, id_list
    senderID = None
    fire_event = False
    if(on_raspi is True):
        p = Packet(PACKET.COMMON_COMMAND, [0x08])
        c = SerialCommunicator()
        c.start()
        c.send(p)
        while sys_init is True:
            try:
                p = c.receive.get(block=True, timeout=1)
                if(p.type == PACKET.RADIO and p.rorg == RORG.BS4):
                    timestamp = datetime.datetime.now()
                    senderID =  p.data[5]*1677216+p.data[6]*65536+p.data[7]*256+p.data[8]
                    if len(id_list) == 0:
                        id_list.append(senderID)
                        fire_event = True
                    else:
                        i=0
                        for i in range(0,len(id_list)):
                            if id_list[i] == senderID:
                                id_list.remove(senderID)
                                fire_event = False
                                break
                            elif id_list[i] != senderID and i == (len(id_list)-1):
                                id_list.append(senderID)
                                fire_event = True
                                break
                    if fire_event is True:
                        serialevent = pygame.event.Event(EV_SERIAL_INPUT, id=senderID, tm=timestamp)
                        pygame.event.post(serialevent)
                        fire_event = False
            except queue.Empty:
                continue
            except KeyboardInterrupt:
                break
            except Exception:
                traceback.print_exc(file=sys.stdout)
                break
        c.stop()
    else:
        while pygame.display.get_init() is True:
            pygame.event.post(serialevent)
            time.sleep(random.uniform(1,5))


# Mainloop
if __name__ == "__main__" :
    print "Initialisiere Logger"
    init_logging()
    print "Initialisiere Pygame"
    pygame.init()
    sys_init = True
    if (with_thread is True):
        print "Initialisiere Thread"
        t = threading.Thread(target=seriallistener)
        t.start()
    print "Initialisiere Einstellungen"
    set = GameSettings()
    print "Erstelle Spiel"
    gm = Game(set)
    print "Initialisiere UI"
    ui = UI(set, gm)
    ui.on_execute()
    if (with_thread is True):
        t.join()
