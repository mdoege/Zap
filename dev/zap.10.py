#!/usr/bin/env python

# Zap

import pygame
from math import sin, cos, pi
import random, time

RES = 160
RES2 = RES/2
CENTER = int(RES2), int(0.75 * RES2)
SRES = 800
SSIZ = 10
ENSIZ = 4
PSIZ = 2
SATSIZ = 3
PI2 = pi / 2
BASES = 3
NEWBASE = 75000

class Zap:
	def __init__(self):
		pygame.init()
		self.res = SRES, int(0.75 * SRES)
		self.screen = pygame.display.set_mode(self.res, pygame.RESIZABLE)
		pygame.display.set_caption('Zap')
		self.clock = pygame.time.Clock()
		self.dazz = pygame.Surface((RES, int(0.75 * RES)))
		self.paused = False
		self.step = False
		self.dir = 0
		self.hiscore = 0
		self.phot = [1000, 1000, 1000, 1000]
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
		}
		self.img["fighter1"] = pygame.transform.rotate(self.img["fighter2"], 90)
		self.img["fighter0"] = pygame.transform.rotate(self.img["fighter2"], 180)
		self.img["fighter3"] = pygame.transform.rotate(self.img["fighter2"], 270)
		self.attractimg = pygame.image.load("img/title.png")
		self.audio["fanfare"].play()
		self.attract = True

	def newgame(self):
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
		self.starfield = pygame.Surface((RES, int(0.75 * RES)))
		self.starfield.fill((0, 0, 0))
		for n in range(200):
			x, y = random.randint(0, RES-1), random.randint(0, int(0.75 * RES-1))
			pygame.draw.line(self.starfield, (120, 120, 120), (x, y), (x, y))

	def events(self):
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
		self.score += x
		self.hiscore = max(self.score, self.hiscore)
		print("S/HS", self.score, self.hiscore)
		self.bonus = self.score // NEWBASE
		print(self.bases + self.bonus, "BASES")

	def fire(self):
		self.audio["fire"].play()
		self.lasertime = time.time()
		if self.satstage:
			if abs(self.dir - (self.satdir % 4)) < .25:
				self.incscore(2000)
				self.audio["satdest"].play()
				self.satstage = False
				self.satdir, self.satdist = 0, 1000
				return
			else:
				return

		if self.dir == self.shipdir and self.shipdist < 1000 and self.shipdist < self.phot[self.dir]:
			self.incscore(500)
			self.audio["shiphit"].play()
			if random.random() < .1:
				self.satstage = True
				self.satdist = 100
				self.satdir = random.uniform(0, 4)
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
		self.dazz.blit(self.img["station"], (CENTER[0] - s, CENTER[1] - s))

	def enemy(self, s):
		x, y = (int(self.shipdist * sin(PI2 * self.shipdir)),
			int(self.shipdist * cos(PI2 * self.shipdir)))
		self.dazz.blit(self.img["fighter%u" % self.shipdir], (CENTER[0] - s + x, CENTER[1] - s - y))

	def photons(self, s):
		for n in range(4):
			x, y = (int(self.phot[n] * sin(PI2 * n)),
				int(self.phot[n] * cos(PI2 * n)))
			self.dazz.blit(self.img["photon"], (CENTER[0] - s + x, CENTER[1] - s - y))

	def sat(self, s):
		x, y = (int(self.satdist * sin(PI2 * self.satdir)),
			int(self.satdist * cos(PI2 * self.satdir)))
		self.dazz.blit(self.img["sat"], (CENTER[0] - s + x, CENTER[1] - s - y))

	def gun(self):
		pygame.draw.line(self.dazz, (255, 255, 0), (CENTER[0], CENTER[1]),
			(int(CENTER[0] + 1.5 * SSIZ * sin(PI2 * self.dir)),
			int(CENTER[1] - 1.5 * SSIZ * cos(PI2 * self.dir))))

	def laser(self):
		dist = min(100, self.shipdist, self.phot[self.dir])
		if time.time() - self.lasertime < .1:
			pygame.draw.line(self.dazz, (255, 255, 255), (CENTER[0], CENTER[1]),
				(int(CENTER[0] + dist * sin(PI2 * self.dir)),
				int(CENTER[1] - dist * cos(PI2 * self.dir))))

	def endgame(self):
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
		if self.paused and not self.step:
			return
		self.step = False

		if self.attract:
			out = pygame.transform.scale(self.attractimg, (self.res))
			self.screen.blit(out, (0, 0))
			pygame.display.flip()
			return

		if self.satstage:
			self.satdir += .02
			self.satdist -= .2
			if self.satdist < SSIZ:
				self.endgame()
		else:
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
		if self.satstage:
			self.sat(SATSIZ)
		else:
			self.enemy(ENSIZ)
			self.photons(PSIZ)
		self.gun()
		out = pygame.transform.scale(self.dazz, (self.res))
		self.screen.blit(out, (0, 0))
		
		pygame.display.flip()

c = Zap()
c.run()

