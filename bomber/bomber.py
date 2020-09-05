import numpy as np
import cv2
import math as m
from time import time
from random import randint
from ctypes import windll

WIN_NAME = "Bomber"
DISP_SIZE = (windll.user32.GetSystemMetrics(0),
			windll.user32.GetSystemMetrics(1))
del windll



class Mouse():
	"""docstring for mouse"""
	def __init__(self):
		self.pos = (0,0)
		self.lButtonDown = False
		self.rButtonDown = False
		self.lastLBClickPos = (0,0)
		self.lastRBClickPos = (0,0)
		self.lButtonClick = False
		self.rButtonClick = False
		self.lDoubleClick = False
		self.rDoubleClick = False
		self.wheel = False
mouse = Mouse()



def mouseHandler(event, x, y, flag, params):
	global mouse
	if event == cv2.EVENT_MOUSEMOVE: mouse.pos = (x,y)
	elif event == cv2.EVENT_LBUTTONDOWN:
		mouse.lButtonDown = True
		mouse.lastLBClickPos = mouse.pos
	elif event == cv2.EVENT_RBUTTONDOWN:
		mouse.rButtonDown = True
		mouse.rButtonClick = True
		mouse.lastRBClickPos = mouse.pos
	elif event == cv2.EVENT_LBUTTONUP:
		mouse.lButtonClick = True
		mouse.lButtonDown = False
	elif event == cv2.EVENT_RBUTTONUP:
		mouse.rButtonDown = False
	elif event == cv2.EVENT_LBUTTONDBLCLK: mouse.lDoubleClick = True
	elif event == cv2.EVENT_RBUTTONDBLCLK: mouse.rDoubleClick = True
	elif event == cv2.EVENT_MOUSEWHEEL:
		if flag > 0: mouse.wheel = "up"
		if flag < 0: mouse.wheel = "down"



class Button():
	"""docstring for Button"""
	def __init__(self):
		self.pos = None
		self.width = None
		self.height = None
		self.isPressed = False
		self.flag = False
		self.value = None
		self.btype = "default"
		self.posInFieldMap = None

	def hover(self):
		if self.pos[0] < mouse.pos[0] < self.pos[0] + self.width and \
				self.pos[1] < mouse.pos[1] < self.pos[1] + self.height:
			return True
		else: return False

	def action(self):
		self.isPressed = not self.isPressed

	def flagReversed(self):
		self.flag = not self.flag



class Game(object):
	"""docstring for Game"""
	def __init__(self):
		self.lastSetupTime = None
		self.pastTime = None

		self.isLost = None
		self.isWon = None

		self.buttonList = None
		self.bombList = None
		self.openCellList = None

		self.fieldSize = None
		self.bombNum = None
		self.fieldMap = None
		self.flagsNum = None

		self.windowSize = None
		self.emptyframe = None
		self.cellSize = None

	def windowSetup(self):
		cv2.namedWindow(WIN_NAME, cv2.WINDOW_NORMAL)
		cv2.resizeWindow(WIN_NAME, self.windowSize)
		cv2.setMouseCallback(WIN_NAME, mouseHandler)

		# game reset button
		gameResetButton = Button()
		gameResetButton.width = 131
		gameResetButton.height = 40
		gameResetButton.pos = (int(self.windowSize[0]/2-gameResetButton.width/2), 18)
		gameResetButton.value = "Restart"
		def gameResetButtonAction(): 
			self.setup((600,600), (10,10), 10)
			self.createField((0,0))
		gameResetButton.action = gameResetButtonAction
		self.buttonList.append(gameResetButton)

	def setup(self, windowSize, fieldSize, bombNum):
		"""setup(self, windowSize, fieldSize, bombNum)"""
		self.lastSetupTime = time()
		self.pastTime = 0

		self.isLost = False
		self.isWon = False

		self.buttonList = []
		self.bombList = []
		self.openCellList = []

		self.fieldSize = fieldSize
		self.bombNum = bombNum
		self.fieldMap = np.zeros(list(reversed(list(fieldSize))), np.dtype(str))
		self.flagsNum = 0

		self.windowSize = windowSize
		self.emptyframe = np.zeros(list(reversed(list(self.windowSize)))+[3], np.dtype("uint8"))
		# cv2.rectangle(self.emptyframe, (0,0), self.windowSize, (250,250,250), -1)
		self.cellSize = int((self.windowSize[0]-150)/fieldSize[0])

		self.windowSetup()

	def openEmptyCells(self, startPos):
		aroundCellList = [startPos]
		while aroundCellList != []:
			pos = aroundCellList[-1]
			del aroundCellList[-1]
			if not (pos in self.openCellList): self.openCellList.append(pos)

			if self.fieldMap[pos[1]][pos[0]] != ' ': continue

			if pos[1]+1 < self.fieldSize[1]:
				if not ((pos[0], pos[1]+1) in self.openCellList):
					aroundCellList.append((pos[0], pos[1]+1))
			if pos[0]+1 < self.fieldSize[0]:
				if not ((pos[0]+1, pos[1]) in self.openCellList):
					aroundCellList.append((pos[0]+1, pos[1]))
			if pos[0]+1 < self.fieldSize[0] and pos[1]+1 < self.fieldSize[1]:
				if not ((pos[0]+1, pos[1]+1) in self.openCellList):
					aroundCellList.append((pos[0]+1, pos[1]+1))
			if pos[1]-1 >= 0:
				if not ((pos[0], pos[1]-1) in self.openCellList):
					aroundCellList.append((pos[0], pos[1]-1))
			if pos[0]-1 >= 0:
				if not ((pos[0]-1, pos[1]) in self.openCellList):
					aroundCellList.append((pos[0]-1, pos[1]))
			if pos[0]-1 >= 0 and pos[1]-1 >= 0:
				if not ((pos[0]-1, pos[1]-1) in self.openCellList):
					aroundCellList.append((pos[0]-1, pos[1]-1))
			if pos[0]+1 < self.fieldSize[0] and pos[1]-1 >= 0:
				if not ((pos[0]+1, pos[1]-1) in self.openCellList):
					aroundCellList.append((pos[0]+1, pos[1]-1))
			if pos[0]-1 >= 0 and pos[1]+1 < self.fieldSize[1]:
				if not ((pos[0]-1, pos[1]+1) in self.openCellList):
					aroundCellList.append((pos[0]-1, pos[1]+1))
		# return self.openCellList

	def createField(self, startPoint):
		for i in range(self.bombNum):
			bombPos = (randint(0, self.fieldSize[0]-1), 
						randint(0, self.fieldSize[1]-1))
			i = 0
			while True:
				i += 1
				if i > 10000: exit()
				bombPos = (randint(0, self.fieldSize[0]-1), 
							randint(0, self.fieldSize[1]-1))
				if not bombPos in self.bombList and bombPos != startPoint and \
						(bombPos[0],   bombPos[1]+1) != startPoint and \
						(bombPos[0]+1, bombPos[1])   != startPoint and \
						(bombPos[0]+1, bombPos[1]+1) != startPoint and \
						(bombPos[0],   bombPos[1]-1) != startPoint and \
						(bombPos[0]-1, bombPos[1])   != startPoint and \
						(bombPos[0]-1, bombPos[1]-1) != startPoint and \
						(bombPos[0]+1, bombPos[1]-1) != startPoint and \
						(bombPos[0]-1, bombPos[1]+1) != startPoint:
					break

			self.bombList.append(bombPos)

		for y in range(self.fieldSize[1]):
			for x in range(self.fieldSize[0]):
				pos = (x * self.cellSize + int((self.windowSize[0] - self.cellSize * self.fieldSize[0])/2),
						y * self.cellSize + int((self.windowSize[1] - self.cellSize * self.fieldSize[1])/2))
				button = Button()
				if (x,y) in self.bombList:
					button.value = 'B'
					self.fieldMap[y][x] = 'B'
				else:
					surroundBombsNum = 0
					if (x,	y+1) in self.bombList: surroundBombsNum += 1
					if (x+1,y)	 in self.bombList: surroundBombsNum += 1
					if (x+1,y+1) in self.bombList: surroundBombsNum += 1
					if (x,	y-1) in self.bombList: surroundBombsNum += 1
					if (x-1,y)	 in self.bombList: surroundBombsNum += 1
					if (x-1,y-1) in self.bombList: surroundBombsNum += 1
					if (x+1,y-1) in self.bombList: surroundBombsNum += 1
					if (x-1,y+1) in self.bombList: surroundBombsNum += 1
					if surroundBombsNum != 0:
						button.value = str(surroundBombsNum)
						self.fieldMap[y][x] = str(surroundBombsNum)
					else:
						button.value = ' '
						self.fieldMap[y][x] = ' '

				button.pos = pos
				button.width = self.cellSize
				button.height = self.cellSize
				button.btype = "cell"
				button.posInFieldMap = (x,y)
				self.buttonList.append(button)
game = Game()
game.setup((600,600), (10,10), 10)
game.createField((0,0))

lastFpsShow = time()
framesTime = 0
framesCounter = 0
fps = 0

while True:
	# zeroing
	lastStartMainLoop = time()
	logList = []
	frame = np.array(game.emptyframe)
	mouse.wheel = False
	mouse.lButtonClick = False
	mouse.rButtonClick = False
	mouse.lDoubleClick = False
	mouse.rDoubleClick = False

	# key handling
	cvKey = cv2.waitKey(1)
	if cvKey == 27: break

	# button handling
	for button in game.buttonList:
		if button.btype == "default":
			if button.hover():
				color = (255,255,255)
				if mouse.lButtonClick:
					button.action()
			else:
				color = (128,128,128)
			cv2.rectangle(frame, button.pos,
				(button.pos[0] + button.width,
					button.pos[1] + button.height),
				color)
			cv2.putText(frame, button.value,
				(button.pos[0] + 10, 
					button.pos[1] - 10 + button.height),
				cv2.FONT_HERSHEY_DUPLEX, 1, color)

		elif button.btype == "cell":
			if button.posInFieldMap in game.openCellList:
				if button.value == 'B': color = (64,64,64)
				elif button.value == '1': color = (255,128,0)
				elif button.value == '2': color = (0,255,128)
				elif button.value == '3': color = (0,128,255)
				elif button.value == '4': color = (255,64,128)
				elif button.value == '5': color = (255,0,255)
				elif button.value == '6': color = (255,255,0)
				elif button.value == '7': color = (0,255,255)
				elif button.value == '8': color = (128,128,128)
				elif button.value == 'RB': color = (0,0,255)
				else:
					cv2.circle(frame,
						(button.pos[0] + int(button.width/2),
							button.pos[1] + int(button.width/2)),
						1, (64,64,64), 2)

				if button.value != 'B' and button.value != 'RB':
					cv2.putText(frame, button.value,
						(button.pos[0] + int(button.width/2) - 10, 
							button.pos[1] + int(button.width/2) + 10),
						cv2.FONT_HERSHEY_DUPLEX, 1, color)
				else:
					cv2.circle(frame,
						(button.pos[0] + int(button.width/2),
							button.pos[1] + int(button.width/2)),
						1, color, int(button.width/2))
					for i in range(8):
						ang = (m.pi * 2) / 8 * i
						cv2.line(frame, 
							(button.pos[0] + int(button.width/2),
								button.pos[1] + int(button.width/2)),
							(int(m.cos(ang) * button.width/3 + button.pos[0] + button.width/2),
								int(m.sin(ang) * button.width/3 + button.pos[1] + button.width/2)),
							color, int(button.width/16))
					if game.isLost and button.flag:
						cv2.putText(frame, 'B',
							(button.pos[0] + int(button.width/2) - 10, 
								button.pos[1] + int(button.width/2) + 10),
							cv2.FONT_HERSHEY_DUPLEX, 1, (0,0,255))
		
			else:
				color = (255,255,255)
				color = (128,128,128)
				if button.hover() and not game.isLost and not game.isWon:
					# color = (color[0] / 2,
					# 		color[1] / 2,
					# 		color[2] / 2)
					color = (color[0] * 2,
							color[1] * 2,
							color[2] * 2)
					if mouse.lButtonClick and button.flag == False: 
						if game.openCellList == []:
							game.setup(DISP_SIZE, (31,31), 128)
							game.setup((600,600), (10,10), 10)
							game.createField(button.posInFieldMap)
						else:
							if button.value == 'B':
								game.isLost = True
								button.value = 'RB'
								for bombPos in game.bombList:
									game.openCellList.append(bombPos)
						game.openEmptyCells(button.posInFieldMap)
						if len(game.openCellList) == game.fieldSize[0] * game.fieldSize[1] - game.bombNum:
							if not game.isLost:
								game.isWon = True
								game.flagsNum = game.bombNum
								for bombPos in game.bombList:
									game.openCellList.append(bombPos)
					if mouse.rButtonClick: 
						button.flagReversed()
						if button.flag == True:
							game.flagsNum += 1
						else:
							game.flagsNum -= 1

				if button.flag:
					if not game.isLost:
						cv2.putText(frame, 'F',
							(button.pos[0] + int(button.width/2) - 10, 
								button.pos[1] + int(button.width/2) + 10),
							cv2.FONT_HERSHEY_DUPLEX, 1, (0,0,255))
							# cv2.FONT_HERSHEY_DUPLEX, 1, (255,255,255))
					else:
						cv2.circle(frame,
							(button.pos[0] + int(button.width/2),
								button.pos[1] + int(button.width/2)),
							1, (64,64,64), int(button.width/2))
						for i in range(8):
							ang = (m.pi * 2) / 8 * i
							cv2.line(frame, 
								(button.pos[0] + int(button.width/2),
									button.pos[1] + int(button.width/2)),
								(int(m.cos(ang) * button.width/3 + button.pos[0] + button.width/2),
									int(m.sin(ang) * button.width/3 + button.pos[1] + button.width/2)),
								(64,64,64), int(button.width/16))
						if not button.posInFieldMap in game.bombList:
							color = (0,0,0)
							for i in range(4):
								ang = (2*m.pi*i+m.pi) / 4
								# ang = m.pi * i - m.pi / 4
								cv2.line(frame, 
									(button.pos[0] + int(button.width/2),
										button.pos[1] + int(button.width/2)),
									(int(m.cos(ang) * button.width/3 + button.pos[0] + button.width/2),
										int(m.sin(ang) * button.width/3 + button.pos[1] + button.width/2)),
									(0,0,200), 2)

				cv2.circle(frame,
					(button.pos[0] + int(button.width/2),
						button.pos[1] + int(button.width/2)),
					int(button.width/2)-1, color, 1)
				# cv2.rectangle(frame, button.pos,
				# 	(button.pos[0] + button.width - 1,
				# 		button.pos[1] + button.height - 1),
				# 	color)

	if game.isLost:
		cv2.putText(frame, 'The game is lost',
			(int(game.windowSize[0]/2) - 135, game.windowSize[1] - 10),
			cv2.FONT_HERSHEY_DUPLEX, 1, (0,0,255))
	if game.isWon:
		cv2.putText(frame, 'The game is won',
			(int(game.windowSize[0]/2) - 135, game.windowSize[1] - 10),
			cv2.FONT_HERSHEY_DUPLEX, 1, (0,255,0))

	# last bomv num
	color = (64,64,64)
	cv2.circle(frame, (120, 40), 1, color, int(button.width/2))
	for i in range(8):
		ang = (m.pi * 2) / 8 * i
		cv2.line(frame, (120, 40), 
			(int(m.cos(ang) * 15 + 120), int(m.sin(ang) * 15 + 40)),
			color, 2)
	cv2.putText(frame, str(game.bombNum - game.flagsNum),
		(145, 50),
		cv2.FONT_HERSHEY_DUPLEX, 1, (255,255,255))

	# time
	color = (128,128,128)
	cv2.circle(frame, (game.windowSize[1] - 180, 40), int(button.width/3), color, 2)
	cv2.line(frame, 
		(game.windowSize[1] - 180, 41), 
		(game.windowSize[1] - 180, 41 - int(button.width/5)),
		color, 2)
	cv2.line(frame, 
		(game.windowSize[1] - 180, 41), 
		(game.windowSize[1] - 180 + int(button.width/5), 41),
		color, 2)
	if game.openCellList == [] or game.isWon or game.isLost:
		game.pastTime = game.pastTime
	else: game.pastTime = int(time() - game.lastSetupTime)
	cv2.putText(frame, str(game.pastTime),
		(game.windowSize[1] - 150, 50),
		cv2.FONT_HERSHEY_DUPLEX, 1, (255,255,255))

	# logging
	# logList.append("LBDwn = " + str(mouse.lButtonDown))
	# logList.append("LBClk = " + str(mouse.lButtonClick))
	# logList.append("RBDwn = " + str(mouse.rButtonDown))
	# logList.append("RBClk = " + str(mouse.rButtonClick))
	# logList.append("LBDBLClk = " + str(mouse.lDoubleClick))
	# logList.append("RBDBLClk = " + str(mouse.rDoubleClick))
	# logList.append("wheel = " + str(mouse.wheel))
	for i in range(len(logList)):
		cv2.putText(frame, str(logList[i]), (0,i*40+40), cv2.FONT_HERSHEY_DUPLEX, 1, (255,255,0))

	# fps counting
	framesTime += time() - lastStartMainLoop
	framesCounter += 1
	if time() - lastFpsShow >= .5:
		lastFpsShow = time()
		fps = round(1/(framesTime/framesCounter), 1)
		framesCounter = 0
		framesTime = 0
	# cv2.putText(frame, str(fps), (game.windowSize[0]-100,50), cv2.FONT_HERSHEY_DUPLEX, 1, (255,255,0))

	cv2.imshow(WIN_NAME, frame)
