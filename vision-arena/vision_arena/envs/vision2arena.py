import gym
from gym import error, spaces, utils
from gym.utils import seeding
import pybullet as p
import pybullet_data
import cv2
import numpy as np

class VisionArena(gym.Env):
	metadata = {'render.modes': ['human']}

	def __init__(self):
		np.random.seed(0)
		p.connect(p.GUI)
		p.setAdditionalSearchPath(pybullet_data.getDataPath())
		p.setGravity(0,0,-10)
		p.loadURDF('rsc/plane.urdf',[0,0,-0.1], useFixedBase=1)
		p.configureDebugVisualizer(p.COV_ENABLE_WIREFRAME, 0)
		p.configureDebugVisualizer(p.COV_ENABLE_SHADOWS, 0)
		
		self.load_arena()
		self.husky = p.loadURDF('husky/husky.urdf',[0,0,0.1],p.getQuaternionFromEuler([0,0,0]))

	def move_husky(self, leftFrontWheel, rightFrontWheel, leftRearWheel, RighRearWheel):
		self.move(self.husky, leftFrontWheel, rightFrontWheel, leftRearWheel, RighRearWheel)

	def reset(self):
		p.resetSimulation()
		p.setGravity(0,0,-10)
		
		#load arena
		self.husky = p.loadURDF('husky/husky.urdf',[0,0,0],p.getQuaternionFromEuler([0,0,0]))

	def load_arena(self, size = 9):
		'''
		Loading the Arena
		'''
		assert size % 2 == 1, 'Size must be an odd integer'
		
		self.arena = np.random.randint(low = 0, high = 6, size = (size, size))
		# After the arena is updated, the numbers will represent
		# Yellow Square : 6n + 1
		# Yellow Circle : 6n + 2
		# Yellow Triangle : 6n + 4
		# Red Square : 6n + 4
		# Red Circle : 6n + 5
		# Red Triangle : 6n + 6
		# where
		# n = 0 for white base
		# n = 1 for green base
		# n = 2 for blue base
		# n = 3 for cyan base
		# n = 4 for magenta base
		# 31 -> arrow with green base
		# 32 -> arrow with blue base
		# 33 -> arrow with cyan base
		# 34 -> arrow with magenta base
		# 0 -> black
		# -1 -> centre
		shape_colour_dict = {
			0: 'rsc/square/square yellow.urdf',
			1: 'rsc/circle/circle yellow.urdf',
			2: 'rsc/triangle/triangle yellow.urdf',
			3: 'rsc/square/square red.urdf',
			4: 'rsc/circle/circle red.urdf',
			5: 'rsc/triangle/triangle red.urdf',
		}
		base_plate_colours = np.random.choice(4, 4, replace = False)
		base_plate_dict = {
			0: 'rsc/base plate/base plate green.urdf',
			1: 'rsc/base plate/base plate blue.urdf',
			2: 'rsc/base plate/base plate cyan.urdf',
			3: 'rsc/base plate/base plate magenta.urdf',
		}
		def get_postion(i, j):
			if self.arena[i, j] % 3 == 2: # If the shape is a triangle
				return [3.2-i*0.75, 3.2-j*0.75, 0.03]
			return [3-i*0.75,3-j*0.75,0.03]

		for i in range(9):
			for j in range(9):
				if (i==0 or i==8) and j!=4:
						p.loadURDF('rsc/base plate/base plate white.urdf', [3-i*0.75,3-j*0.75,0], p.getQuaternionFromEuler([0,0,0]), useFixedBase=1)
						p.loadURDF(shape_colour_dict[self.arena[i, j]], get_postion(i, j), p.getQuaternionFromEuler([0,0,np.pi]), useFixedBase=1)
						self.arena[i, j] = self.arena[i, j] + 1
				elif (i==1 or i==7) and (j==0 or j==8):
						p.loadURDF('rsc/base plate/base plate white.urdf', [3-i*0.75,3-j*0.75,0], p.getQuaternionFromEuler([0,0,0]), useFixedBase=1)
						p.loadURDF(shape_colour_dict[self.arena[i, j]], get_postion(i, j), p.getQuaternionFromEuler([0,0,np.pi]), useFixedBase=1)
						self.arena[i, j] = self.arena[i, j] + 1
				elif (i==2 or i==6) and (j!=1 and j!=7 and j!=4):
						p.loadURDF('rsc/base plate/base plate white.urdf', [3-i*0.75,3-j*0.75,0], p.getQuaternionFromEuler([0,0,0]), useFixedBase=1)
						p.loadURDF(shape_colour_dict[self.arena[i, j]], get_postion(i, j), p.getQuaternionFromEuler([0,0,np.pi]), useFixedBase=1)
						self.arena[i, j] = self.arena[i, j] + 1
				elif (i==3 or i==5) and (j%2==0 and j!=4):
						p.loadURDF('rsc/base plate/base plate white.urdf', [3-i*0.75,3-j*0.75,0], p.getQuaternionFromEuler([0,0,0]), useFixedBase=1)
						p.loadURDF(shape_colour_dict[self.arena[i, j]], get_postion(i, j), p.getQuaternionFromEuler([0,0,np.pi]), useFixedBase=1)
						self.arena[i, j] = self.arena[i, j] + 1
				elif (i==4 and j!=4):
					if j<4:
						p.loadURDF(base_plate_dict[base_plate_colours[0]], [3-i*0.75,3-j*0.75,0], p.getQuaternionFromEuler([0,0,0]), useFixedBase=1)
						if j==0:
							p.loadURDF('rsc/arrow/arrow.urdf', [3-i*0.75,3-j*0.75,0.03], p.getQuaternionFromEuler([0,0,-np.pi/2]), useFixedBase=1)
							self.arena[i, j] = base_plate_colours[0] + 31
						else:
							p.loadURDF(shape_colour_dict[self.arena[i, j]], get_postion(i, j), p.getQuaternionFromEuler([0,0,np.pi]), useFixedBase=1)
							self.arena[i, j] = (base_plate_colours[0] + 1) * 6 + self.arena[i, j] + 1
					else:
						p.loadURDF(base_plate_dict[base_plate_colours[1]], [3-i*0.75,3-j*0.75,0], p.getQuaternionFromEuler([0,0,0]), useFixedBase=1)
						if j == 8:
							p.loadURDF('rsc/arrow/arrow.urdf', [3-i*0.75,3-j*0.75,0.03], p.getQuaternionFromEuler([0,0,np.pi/2]), useFixedBase=1)
							self.arena[i, j] = base_plate_colours[1] + 31
						else:
							p.loadURDF(shape_colour_dict[self.arena[i, j]], get_postion(i, j), p.getQuaternionFromEuler([0,0,np.pi]), useFixedBase=1)
							self.arena[i, j] = (base_plate_colours[1] + 1) * 6 + self.arena[i, j] + 1
				elif (j == 4 and i != 4):
					if i < 4:
						p.loadURDF(base_plate_dict[base_plate_colours[2]], [3-i*0.75,3-j*0.75,0], p.getQuaternionFromEuler([0,0,0]), useFixedBase=1)
						if i == 0:
							p.loadURDF('rsc/arrow/arrow.urdf', [3-i*0.75,3-j*0.75,0.03], p.getQuaternionFromEuler([0,0,np.pi]), useFixedBase=1)
							self.arena[i, j] = base_plate_colours[2] + 31
						else:
							p.loadURDF(shape_colour_dict[self.arena[i, j]], get_postion(i, j), p.getQuaternionFromEuler([0,0,np.pi]), useFixedBase=1)
							self.arena[i, j] = (base_plate_colours[2] + 1) * 6 + self.arena[i, j] + 1
					else:
						p.loadURDF(base_plate_dict[base_plate_colours[3]], [3-i*0.75,3-j*0.75,0], p.getQuaternionFromEuler([0,0,0]), useFixedBase=1)
						if i == 8:
							p.loadURDF('rsc/arrow/arrow.urdf', [3-i*0.75,3-j*0.75,0.03], p.getQuaternionFromEuler([0,0,0]), useFixedBase=1)
							self.arena[i, j] = base_plate_colours[3] + 31
						else:
							p.loadURDF(shape_colour_dict[self.arena[i, j]], get_postion(i, j), p.getQuaternionFromEuler([0,0,np.pi]), useFixedBase=1)
							self.arena[i, j] = (base_plate_colours[3] + 1) * 6 + self.arena[i, j] + 1
				elif i == 4 and j == 4:
					p.loadURDF('rsc/base plate/base plate white.urdf', [3-i*0.75,3-j*0.75,0], p.getQuaternionFromEuler([0,0,0]), useFixedBase=1)
					self.arena[i, j] = -1
				else:
					p.loadURDF('rsc/base plate/base plate black.urdf', [3-i*0.75,3-j*0.75,0], p.getQuaternionFromEuler([0,0,0]), useFixedBase=1)
					self.arena[i, j] = 0
		print(self.arena)

	def move(self, car, leftFrontWheel, rightFrontWheel, leftRearWheel, rightRearWheel):
		p.setJointMotorControl2(car,  2, p.VELOCITY_CONTROL, targetVelocity=leftFrontWheel, force=15)
		p.setJointMotorControl2(car,  3, p.VELOCITY_CONTROL, targetVelocity=rightFrontWheel, force=15)
		p.setJointMotorControl2(car,  4, p.VELOCITY_CONTROL, targetVelocity=leftRearWheel, force=15)
		p.setJointMotorControl2(car,  5, p.VELOCITY_CONTROL, targetVelocity=rightRearWheel, force=15)
