#!/usr/bin/env python

# SnakeZap

import pygame
from math import sin, cos, pi
import random, time

RES = 160
RES2 = RES/2
CENTER = int(RES2), int(0.75 * RES2)
SRES = 640
SSIZ = 10
ENSIZ = 4
PI2 = pi / 2
BASES = 3

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
		self.newgame()
		pygame.mixer.init()
		self.audio = {
			"start": pygame.mixer.Sound("fanfare.wav"),
			"fire": pygame.mixer.Sound("shot.wav"),
			"shiphit": pygame.mixer.Sound("enemy.wav"),
			"end": pygame.mixer.Sound("stationdest2.wav"),
		}
		self.attractimg = pygame.image.load("zaplogo.png")
		self.audio["start"].play()
		self.attract = True

	def newgame(self):
		self.shipdir = random.randint(0, 3)
		self.shipdist = 100
		self.score = 0
		self.bases = BASES

	def events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT: self.running = False
			if event.type == pygame.VIDEORESIZE:
				self.res = event.w, event.h
				#print(s.res)
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
		if self.score / 75000 == self.score // 75000:
			self.bases += 1
			print(self.bases, "BASES")

	def fire(self):
		self.audio["fire"].play()
		if self.dir == self.shipdir and self.shipdist < 1000:
			self.incscore(500)
			self.audio["shiphit"].play()
			self.shipdist = 100
			self.shipdir = random.randint(0, 3)

	def station(self, s):
		pygame.draw.rect(self.dazz, (255, 255, 0), ((CENTER[0] - s, CENTER[1] - s),
			(2 * s + 1, 2 * s + 1)))

	def enemy(self, s):
		x, y = (int(self.shipdist * sin(PI2 * self.shipdir)),
			int(self.shipdist * cos(PI2 * self.shipdir)))
		pygame.draw.rect(self.dazz, (0, 255, 0), ((CENTER[0] - s + x, CENTER[1] - s - y),
			(2 * s + 1, 2 * s + 1)))

	def gun(self):
		pygame.draw.line(self.dazz, (255, 255, 0), (CENTER[0], CENTER[1]),
			(int(CENTER[0] + 1.5 * SSIZ * sin(PI2 * self.dir)),
			int(CENTER[1] - 1.5 * SSIZ * cos(PI2 * self.dir))))

	def endgame(self):
		self.bases -= 1
		print(self.bases, "BASES")
		if self.bases > 0:
			self.audio["shiphit"].play(loops = 5)
			time.sleep(4)
			self.shipdist = 100
			self.shipdir = random.randint(0, 3)
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

		#c = [85 * self.dir for q in range(3)]
		self.shipdist -= .5
		if self.shipdist < SSIZ + ENSIZ:
			self.endgame()
		self.dazz.fill((0, 0, 0))
		self.station(SSIZ)
		self.enemy(ENSIZ)
		self.gun()
		out = pygame.transform.scale(self.dazz, (self.res))
		self.screen.blit(out, (0, 0))
		
		pygame.display.flip()

c = Zap()
c.run()

