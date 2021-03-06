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
		pygame.mixer.init()
		self.audio = {
			"fire": pygame.mixer.Sound("shot.wav"),
		}

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

	def fire(self):
		self.audio["fire"].play()

	def station(self, s):
		pygame.draw.rect(self.dazz, (255, 255, 0), ((CENTER[0] - s, CENTER[1] - s),
			(2 * s, 2 * s)))

	def enemy(self, s, x, y):
		pygame.draw.rect(self.dazz, (0, 255, 0), ((CENTER[0] - s + x, CENTER[1] - s - y),
			(2 * s, 2 * s)))

	def gun(self):
		pygame.draw.line(self.dazz, (255, 255, 0), (CENTER[0], CENTER[1]),
			(int(CENTER[0] + 1.5 * SSIZ * sin(PI2 * self.dir)),
			int(CENTER[1] - 1.5 * SSIZ * cos(PI2 * self.dir))))

	def update(self):
		if self.paused and not self.step:
			return
		self.step = False

		#c = [85 * self.dir for q in range(3)]
		self.dazz.fill((0, 0, 0))
		self.station(SSIZ)
		self.enemy(ENSIZ, 0, 30)
		self.gun()
		out = pygame.transform.scale(self.dazz, (self.res))
		self.screen.blit(out, (0, 0))
		
		pygame.display.flip()

c = Zap()
c.run()

