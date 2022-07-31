#!/usr/bin/env python

# Zap

import pygame
from math import sin, cos, pi
import random, time

RES = 160        # horizontal resolution
RESY = int(0.75 * RES)
RES2 = RES/2
CENTER = int(RES2), int(0.75 * RES2)
SRES = 800       # initial upscaled horizontal resolution (window can be resized)
SSIZ = 10        # station size
ENSIZ = 4        # enemy size
PSIZ = 2         # photon torpedo size
SATSIZ = 3       # attack satellite size
EXSIZ = 5        # explosion size
PI2 = pi / 2
BASES = 3        # initial numbers of bases
NEWBASE = 75000  # score for a bonus base
EXPLO_DUR = 10   # explosion duration

class Zap:
	def __init__(self):
		pygame.init()
		self.res = SRES, int(0.75 * SRES)
		self.screen = pygame.display.set_mode(self.res, pygame.RESIZABLE)
		pygame.display.set_caption('Zap')
		self.clock = pygame.time.Clock()
		self.dazz = pygame.Surface((RES, RESY))
		self.paused = False
		self.step = False
		self.dir = 0
		self.hiscore = 0
		self.phot = [1000, 1000, 1000, 1000]
		self.explo = []
		self.newgame()
		pygame.mixer.init()
		self.audio = {
			"fanfare": pygame.mixer.Sound("snd/fanfare.ogg"),
			"start":   pygame.mixer.Sound("snd/start.ogg"),
			"fire":    pygame.mixer.Sound("snd/shot.ogg"),
			"shiphit": pygame.mixer.Sound("snd/enemy.ogg"),
			"end":     pygame.mixer.Sound("snd/stationdest.ogg"),
			"pfire":   pygame.mixer.Sound("snd/photon.ogg"),
			"pdest":   pygame.mixer.Sound("snd/photondest.ogg"),
			"satdest": pygame.mixer.Sound("snd/sat.ogg"),
		}
		self.img = {
			"station":  pygame.image.load("img/station.png"),
			"photon":   pygame.image.load("img/photon.png"),
			"fighter2": pygame.image.load("img/fighter.png"),
			"sat":      pygame.image.load("img/satellite.png"),
			"explode":  pygame.image.load("img/explosion.png"),
			"num":      pygame.image.load("img/numbers.png"),
			"text":     pygame.image.load("img/text.png"),
		}
		self.img["fighter1"] = pygame.transform.rotate(self.img["fighter2"], 90)
		self.img["fighter0"] = pygame.transform.rotate(self.img["fighter2"], 180)
		self.img["fighter3"] = pygame.transform.rotate(self.img["fighter2"], 270)
		self.attractimg = pygame.image.load("img/title.png")
		self.audio["fanfare"].play()
		self.attract = True

	def newgame(self):
		"Set up a new game, reset everthing"
		self.shipdir = random.randint(0, 3)
		self.shipdist = 100
		self.score = 0
		self.bonus = 0
		self.phot = [1000, 1000, 1000, 1000]
		self.lastshot = time.time()
		self.bases = BASES
		self.lasertime = 0
		self.satstage = False
		self.satdir, self.satdist = 0, 1000
		self.starfield = pygame.Surface((RES, RESY))
		self.starfield.fill((0, 0, 0))
		for n in range(200):
			x, y = random.randint(0, RES-1), random.randint(0, RESY-1)
			pygame.draw.line(self.starfield, (120, 120, 120), (x, y), (x, y))

	def events(self):
		"Handle player input"
		for event in pygame.event.get():
			if event.type == pygame.QUIT: self.running = False
			if event.type == pygame.VIDEORESIZE:
				self.res = event.w, event.h
				self.screen = pygame.display.set_mode(self.res, pygame.RESIZABLE)
			if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
				self.paused = not self.paused
			if event.type == pygame.KEYDOWN and event.key == pygame.K_PERIOD:
				self.step = True
			if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
				if self.attract:
					self.attract = False
					self.audio["start"].play()
					time.sleep(1)
				else:
					self.fire()
			if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
				self.dir = 0
			if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
				self.dir = 1
			if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
				self.dir = 2
			if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
				self.dir = 3

	def run(self):
		self.running = True
		while self.running:
			self.clock.tick(60)
			self.events()
			self.update()
		pygame.quit()

	def incscore(self, x):
		"Increase score and highscore"
		self.score += x
		self.hiscore = max(self.score, self.hiscore)
		print("S/HS", self.score, self.hiscore)
		self.bonus = self.score // NEWBASE
		print(self.bases + self.bonus, "BASES")

	def add_explosion(self, xdir, xdist):
		"Add exlosion effect"
		x, y = (int(xdist * sin(PI2 * xdir)), int(xdist * cos(PI2 * xdir)))
		self.explo.append([x, y, EXPLO_DUR])

	def fire(self):
		"Trigger has been pulled, check if anything has been hit"
		self.audio["fire"].play()
		self.lasertime = time.time()
		if self.satstage:
			if abs(self.dir - (self.satdir % 4)) < .25:
				self.incscore(2000)
				self.audio["satdest"].play()
				self.add_explosion(self.satdir, self.satdist)
				self.satstage = False
				self.satdir, self.satdist = 0, 1000
				return
			else:
				return

		if self.dir == self.shipdir and self.shipdist < 1000 and self.shipdist < self.phot[self.dir]:
			self.incscore(500)
			self.audio["shiphit"].play()
			self.add_explosion(self.shipdir, self.shipdist)
			if random.random() < .1:
				self.satstage = True
				self.satdist = 100
				self.satdir = random.uniform(0, 4)
				self.shipdist = 100
				print("ATTACK SATELLITE!")
			else:
				self.shipdist = 100
				self.shipdir = random.randint(0, 3)
			return
		if self.phot[self.dir] < 1000:
			self.incscore(250)
			self.audio["pdest"].play()
			self.phot[self.dir] = 1000
			return

	def station(self, s):
		"Draw the station"
		self.dazz.blit(self.img["station"], (CENTER[0] - s, CENTER[1] - s))

	def enemy(self, s):
		"Draw enemy fighters"
		x, y = (int(self.shipdist * sin(PI2 * self.shipdir)),
			int(self.shipdist * cos(PI2 * self.shipdir)))
		self.dazz.blit(self.img["fighter%u" % self.shipdir], (CENTER[0] - s + x, CENTER[1] - s - y))

	def explo_draw(self, s):
		"Draw explosions"
		for n, x in enumerate(self.explo):
			if x[2] > 0:
				x[2] -= 1
				self.dazz.blit(self.img["explode"], (CENTER[0] - s + x[0], CENTER[1] - s - x[1]))
		for n, x in enumerate(self.explo):
			if x[2] <= 0:
				del(self.explo[n])

	def photons(self, s):
		"Draw photon torpedoes"
		for n in range(4):
			x, y = (int(self.phot[n] * sin(PI2 * n)),
				int(self.phot[n] * cos(PI2 * n)))
			self.dazz.blit(self.img["photon"], (CENTER[0] - s + x, CENTER[1] - s - y))

	def sat(self, s):
		"Draw attack satellite"
		x, y = (int(self.satdist * sin(PI2 * self.satdir)),
			int(self.satdist * cos(PI2 * self.satdir)))
		self.dazz.blit(self.img["sat"], (CENTER[0] - s + x, CENTER[1] - s - y))

	def gun(self):
		"Draw the station's gun"
		pygame.draw.line(self.dazz, (255, 255, 0), (CENTER[0], CENTER[1]),
			(int(CENTER[0] + 1.5 * SSIZ * sin(PI2 * self.dir)),
			int(CENTER[1] - 1.5 * SSIZ * cos(PI2 * self.dir))))

	def laser(self):
		"Draw a laser shot from the station"
		dist = min(100, self.shipdist, self.phot[self.dir])
		if time.time() - self.lasertime < .1:
			pygame.draw.line(self.dazz, (255, 255, 255), (CENTER[0], CENTER[1]),
				(int(CENTER[0] + dist * sin(PI2 * self.dir)),
				int(CENTER[1] - dist * cos(PI2 * self.dir))))

	def scores(self):
		"Draw score and highscore display"
		for n, c in enumerate("%u" % self.score):
			i = int(c)
			self.dazz.blit(self.img["num"], (5 * n, 6),
				area = (5 * i, 0, 5, 5))
		dx = RES - 5 * len("%u" % self.hiscore) + 1
		for n, c in enumerate("%u" % self.hiscore):
			i = int(c)
			self.dazz.blit(self.img["num"], (5 * n + dx, 6),
				area = (5 * i, 0, 5, 5))
		for n, c in enumerate("%u" % (self.bases + self.bonus)):
			i = int(c)
			self.dazz.blit(self.img["num"], (5 * n, RESY - 11),
				area = (5 * i, 0, 5, 5))

		self.dazz.blit(self.img["text"], (RES - 28, 0),
				area = (0, 0, 28, 5))
		self.dazz.blit(self.img["text"], (0, 0),
				area = (7, 0, 28, 5))
		self.dazz.blit(self.img["text"], (0, RESY - 5),
				area = (0, 6, 28, 5))


	def endgame(self):
		"The station has been destroyed"
		self.bases -= 1
		print(self.bases + self.bonus, "BASES")
		if self.bases + self.bonus > 0:
			self.audio["shiphit"].play(loops = 5)
			time.sleep(4)
			self.shipdist = 100
			self.shipdir = random.randint(0, 3)
			self.phot = [1000, 1000, 1000, 1000]
			self.lastshot = time.time()
			self.satstage = False
			self.lasertime = 0
		else:
			self.audio["shiphit"].play(loops = 8)
			time.sleep(6)
			self.newgame()
			self.attract = True

	def update(self):
		"Main loop"
		if self.paused and not self.step:
			return
		self.step = False

		if self.attract:    # title screen
			out = pygame.transform.scale(self.attractimg, (self.res))
			self.screen.blit(out, (0, 0))
			pygame.display.flip()
			return

		if self.satstage:   # killer satellite active?
			self.satdir += .02
			self.satdist -= .2
			if self.satdist < SSIZ:
				self.endgame()
		else:               # normal play
			self.shipdist -= .5
			for n in range(4):
				if self.phot[n] < 1000:
					self.phot[n] -= 1
				if self.phot[n] == 1000 and self.shipdir == n:
					if  time.time() - self.lastshot > 1:
						self.phot[n] = self.shipdist - 1
						self.lastshot = time.time()
						self.audio["pfire"].play()
						if random.random() < .3:
							self.shipdist = 100
							self.shipdir = random.randint(0, 3)
			if (self.shipdist < SSIZ + ENSIZ) or (min(self.phot) < SSIZ + PSIZ):
				self.endgame()
		self.dazz.blit(self.starfield, (0, 0))
		self.laser()
		self.station(SSIZ)
		self.explo_draw(EXSIZ)
		if self.satstage:
			self.sat(SATSIZ)
		else:
			self.enemy(ENSIZ)
			self.photons(PSIZ)
		self.gun()
		self.scores()
		out = pygame.transform.scale(self.dazz, (self.res))
		self.screen.blit(out, (0, 0))
		
		pygame.display.flip()

c = Zap()
c.run()

