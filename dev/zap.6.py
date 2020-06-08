#!/usr/bin/env python

# Zap

import pygame
from math import sin, cos, pi
import random, time

RES = 160
RES2 = RES/2
CENTER = int(RES2), int(0.75 * RES2)
SRES = 640
SSIZ = 10
ENSIZ = 4
PSIZ = 2
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
			"start": pygame.mixer.Sound("fanfare.wav"),
			"fire": pygame.mixer.Sound("shot.wav"),
			"shiphit": pygame.mixer.Sound("enemy.wav"),
			"end": pygame.mixer.Sound("stationdest2.wav"),
			"pfire": pygame.mixer.Sound("photon.wav"),
			"pdest": pygame.mixer.Sound("photondest.wav"),
		}
		self.attractimg = pygame.image.load("zaplogo.png")
		self.audio["start"].play()
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
		if self.dir == self.shipdir and self.shipdist < 1000 and self.shipdist < self.phot[self.dir]:
			self.incscore(500)
			self.audio["shiphit"].play()
			self.shipdist = 100
			self.shipdir = random.randint(0, 3)
			return
		if self.phot[self.dir] < 1000:
			self.incscore(250)
			self.audio["pdest"].play()
			self.phot[self.dir] = 1000
			return

	def station(self, s):
		pygame.draw.rect(self.dazz, (255, 255, 0), ((CENTER[0] - s, CENTER[1] - s),
			(2 * s + 1, 2 * s + 1)))

	def enemy(self, s):
		x, y = (int(self.shipdist * sin(PI2 * self.shipdir)),
			int(self.shipdist * cos(PI2 * self.shipdir)))
		pygame.draw.rect(self.dazz, (0, 255, 0), ((CENTER[0] - s + x, CENTER[1] - s - y),
			(2 * s + 1, 2 * s + 1)))

	def photons(self, s):
		for n in range(4):
			x, y = (int(self.phot[n] * sin(PI2 * n)),
				int(self.phot[n] * cos(PI2 * n)))
			pygame.draw.rect(self.dazz, (255, 0, 0), ((CENTER[0] - s + x, CENTER[1] - s - y),
				(2 * s + 1, 2 * s + 1)))

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
		self.dazz.fill((0, 0, 0))
		self.laser()
		self.station(SSIZ)
		self.enemy(ENSIZ)
		self.photons(PSIZ)
		self.gun()
		out = pygame.transform.scale(self.dazz, (self.res))
		self.screen.blit(out, (0, 0))
		
		pygame.display.flip()

c = Zap()
c.run()

