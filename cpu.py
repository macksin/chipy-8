import random
import pygame

chip8_fontset = [
  0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
  0x20, 0x60, 0x20, 0x20, 0x70, # 1
  0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
  0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
  0x90, 0x90, 0xF0, 0x10, 0x10, # 4
  0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
  0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
  0xF0, 0x10, 0x20, 0x40, 0x40, # 7
  0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
  0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
  0xF0, 0x90, 0xF0, 0x90, 0x90, # A
  0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
  0xF0, 0x80, 0x80, 0x80, 0xF0, # C
  0xE0, 0x90, 0x90, 0x90, 0xE0, # D
  0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
  0xF0, 0x80, 0xF0, 0x80, 0x80  # F
]

KEY_MAPPINGS = {
	0x0: pygame.K_g,
	0x1: pygame.K_4,
	0x2: pygame.K_5,
	0x3: pygame.K_6,
	0x4: pygame.K_7,
	0x5: pygame.K_r,
	0x6: pygame.K_t,
	0x7: pygame.K_y,
	0x8: pygame.K_u,
	0x9: pygame.K_f,
	0xA: pygame.K_h,
	0xB: pygame.K_j,
	0xC: pygame.K_v,
	0xD: pygame.K_b,
	0xE: pygame.K_n,
	0xF: pygame.K_m,
}

class CPU():

	def __init__(self, drawobj, screenobj, verbose):
		self.opcode = 0
		self.memory = [None] * 4096 # 4096 locations
		self.registers = [None] * 16 # 16 registers
		self.i = 0
		self.pc = 0x200 # program counter starts
		self.gfs = [None] * (64 * 32) # 64 * 32
		self.stack = []
		self.sp = 0 # reset stack ppinter
		self.key = [None] * 16 # 16 hex
		self.drawobj = drawobj
		self.screen = screenobj
		self.black = (0, 0, 0)
		self.white = (255, 255, 255)
		self.verbose = verbose

		# Init fontset
		for i, c in enumerate(chip8_fontset):
			self.memory[i] = c

		# operations
		self.operations_search = {
			0x0: self.clear,
			0x1: self.jmp_addr,
			0x2: self.jmp_sub,
			0x3: self.skp_if_reg_eq_var,
			0x4: self.skp_if_reg_neq_var,
			0x5: self.skp_if_reg_e_reg,
			0x6: self.load_value,
			0x7: self.add_vlr_to_reg,
			0x8: self.logical,
			0x9: self.skp_reg_ne_reg,
			0xA: self.store_in_reg_i,
			0xB: self.jmp_to_nnn_plus_v0,
			0xC: self.random_number,
			0xD: self.draw_spr,
			0xE: self.keys_entry,
			0xF: self.other_routines
		}

		# operations
		self.operations_names = {
			0x0: 'SYS',
			0x1: 'JUMP1',
			0x2: 'CALL',
			0x3: 'SKE1',
			0x4: 'SKNE1',
			0x5: 'SKE2',
			0x6: 'LOAD',
			0x7: 'ADD',
			0x8: 'LOGIC',
			0x9: 'SKNE2',
			0xA: 'LOAD I',
			0xB: 'JUMP2',
			0xC: 'RAND',
			0xD: 'DRAW',
			0xE: 'KEYS',
			0xF: 'OTHERS'
		}

		# implemented operations
		self.implemented = self.operations_names.values()


	def fetch_opcode(self):
		# curr = self.memory[self.pc] << 8 | self.memory[self.pc+1] 0xa2cd
		curr = self.memory[self.pc] << 8 | self.memory[self.pc+1]
		self.opcode = curr

	def decode_opcode(self):
		return (self.opcode & 0xf000) >> 12

	def print_oper(self):
		operation = self.operations_names[self.decode_opcode()]
		print("{}".format(operation))

	def print_status(self):
		pp = "instr: {} \tcode: {} \tpc: {}/{}\tsp={}\ti={}".format(\
			hex(self.opcode),
			self.operations_names[self.decode_opcode()],
			self.pc,
			hex(self.pc),
			self.sp,
			hex(self.i))
		if self.operations_names[self.decode_opcode()] in self.implemented:
			self.operations_search[self.decode_opcode()]()
		else:
			print("STOPPED {}".format(hex(self.opcode)))
			return -1
		return pp

	def clear(self):
		"""Auxiliary functions"""
		if (self.opcode == 0x00ee):
			self.pc = self.sp
			try:
				self.stack.pop()
				self.pc = self.stack[-1]
			except:
				pass
		elif (self.opcode == 0x00e0):
			pass
		else:
			pass

	def jmp_addr(self):
		"""1NNN - Jump to address NNN"""
		self.pc = (self.opcode & 0x0fff) - 2

	def jmp_sub(self):
		"""2NNN - Execute subroutine starting at address NNN"""
		address = self.opcode & 0x0fff
		self.stack.append(self.pc)
		self.sp = self.pc
		self.pc = address
		if self.verbose > 0:
			print("JUMP SUB {}".format(hex(address)))

	# 3XNN - Skip the following instruction if
	#  the value of register VX equals NN
	def skp_if_reg_eq_var(self):
		x = (self.opcode & 0x0f00) >> 8
		nn = (self.opcode & 0x00ff)
		if self.registers[x] == nn:
			self.pc += 2

		if self.verbose > 0:
			print("SKP {}, {} = {}".format(hex(x), hex(nn), self.registers[x] == nn))

	# 4XNN - Skip the following instruction if the
	# value of register VX is not equal to NN
	def skp_if_reg_neq_var(self):
		x = (self.opcode & 0x0f00) >> 8
		nn = self.opcode & 0x00ff
		if self.registers[x] != nn:
			self.pc += 2

	# 5XY0 - Skip the following instruction if the value
	#  of register VX is equal to the value of register VY
	def skp_if_reg_e_reg(self):
		x = (self.opcode & 0x0f00) >> 8
		y = (self.opcode & 0x00f0) >> 4
		if self.registers[x] == self.registers[y]:
			self.pc += 2

		if self.verbose > 0:
			print("SKPN {}, {} = {}".format(hex(x), hex(y), self.registers[x] != self.registers[y]))

	def load_value(self):
		"""6XNN - Store number NN in register VX"""
		register = (self.opcode & 0x0f00) >> 8
		value = self.opcode & 0x00ff
		self.registers[register] = value
		if self.verbose > 0:
			print("LOAD {} TO {}".format(hex(value), hex(register)))

	def add_vlr_to_reg(self):
		"""7XNN - Add the value NN to register VX"""
		value = self.opcode & 0xff
		register = (self.opcode & 0x0f00) >> 8
		if self.registers[register] == None:
			self.registers[register] = value
		else:
			self.registers[register] = (self.registers[register] + value) & 0xff
			if self.verbose > 0:
				print("ADD {} TO REG {}".format(hex(value), hex(register)))

	def logical(self):
		mini_operator = self.opcode & 0x000f

		# 8XY0 - Store the value of register VY in register VX
		if mini_operator == 0x0:
			y = (self.opcode & 0x00f0) >> 4
			x = (self.opcode & 0x0f00) >> 8
			self.registers[x] = self.registers[y]
			if self.verbose > 0:
				print("STORE REG {} TO REG {}".format(hex(y), hex(x)))

		# 8XY1 - Set VX to VX OR VY
		elif mini_operator == 0x1:
			x = (self.opcode & 0x0f00) >> 8
			y = (self.opcode & 0x00f0) >> 4
			or_operator = x | y
			self.registers[or_operator] = self.registers[x]

		# 8XY2 - Set VX to VX AND VY
		elif mini_operator == 0x2:
			x = (self.opcode & 0x0f00) >> 8
			y = (self.opcode & 0x00f0) >> 4
			and_operator = x & y
			self.registers[and_operator] = self.registers[x]

		# 8XY3 - Set VX to VX XOR VY
		elif mini_operator == 0x3:
			x = (self.opcode & 0x0f00) >> 8
			y = (self.opcode & 0x00f0) >> 4
			xor_operator = x ^ y
			self.registers[xor_operator] = self.registers[x]

		# 8XY4 - Add the value of register VY to VX
		# Set VF to 01 if a carry occurs
		# Set VF to 00 if a carry does not occur
		elif mini_operator == 0x4:
			y = (self.opcode >> 4) & 0xf
			x = (self.opcode >> 8) & 0xf
			_ = self.registers[x] + self.registers[y]
			if _ > 255:
				self.registers[x] = 256 - _
				self.registers[0xF] = 1
			else:
				self.registers[x] = _
				self.registers[0xF] = 0
			if self.verbose > 0:
				print("ADD REG {} TO REG {}".format(hex(y), hex(x)))

		# 8XY - Subtract the value of register VY from register VX
		# Set VF to 00 if a borrow occurs
		# Set VF to 01 if a borrow does not occur
		elif mini_operator == 0x5:
			y = (self.opcode >> 4) & 0xf
			x = (self.opcode >> 8) & 0xf
			if self.registers[x] > self.registers[y]:
				self.registers[x] -= self.registers[y]
				self.registers[0xF] = 1
			else:
				self.registers[x] = 256 + (self.registers[x] - self.registers[y])
				self.registers[0xF] = 0

		# 8XY6 - Store the value of register VY shifted right one bit in register VX
		# Set register VF to the least significant bit prior to the shift
		elif mini_operator == 0x6:
			x = (self.opcode & 0x0f00) >> 8
			y = (self.opcode & 0x00f0) >> 4
			self.registers[x] = y >> 1
			self.registers[0xF] = y & 1

		# 8XY7 - Set register VX to the value of VY minus VX
		# Set VF to 00 if a borrow occurs
		# Set VF to 01 if a borrow does not occur
		elif mini_operator == 0x7:
			y = self.opcode >> 4 & 0xf
			x = self.opcode >> 8 & 0xf
			if self.registers[y] > self.registers[x]:
				self.registers[x] = self.registers[y] - self.registers[x]
				self.registers[0xF] = 1
			else:
				self.registers[x] = 256 + (self.registers[y] - self.registers[x])
				self.registers[0xF] = 0

		# 8XYE - Store the value of register VY shifted left one bit in register VX
		# Set register VF to the most significant bit prior to the shift
		elif mini_operator == 0xE:
			x = (self.opcode & 0x0f00) >> 8
			y = (self.opcode & 0x00f0) >> 4
			self.registers[x] = (y << 1) & 0xf
			self.registers[0xF] = (y << 1) & int('10000', 2)

		else:
			pass

	def skp_reg_ne_reg(self):
		"""9XY0 - Skip the following instruction if the value
		 of register VX is not equal to the value of register VY"""
		x = (self.opcode & 0x0f00) >> 8
		y = (self.opcode & 0x00f0) >> 4
		if self.registers[x] != self.registers[y]:
			self.pc += 2

		if self.verbose > 0:
			print("SKPN {}, {} = {}".format(hex(x), hex(y), self.registers[x] != self.registers[y]))

	def store_in_reg_i(self):
		"""ANNN - Store memory address NNN in register I"""
		self.i = self.opcode & 0x0fff

	def jmp_to_nnn_plus_v0(self):
		"""BNNN - Jump to address NNN + V0"""
		jumpto = self.opcode & 0x0fff
		self.pc = (jumpto + self.registers[0])


	def random_number(self):
		"""CXNN - Set VX to a random number with a mask of NN"""
		number = random.randint(0, 255)
		x = (self.opcode & 0x0f00) >> 8
		self.registers[x] = number
		if self.verbose > 0:
			print("RANDOM {} TO REG {}".format(hex(number), hex(x)))

	# DXYN - Draw a sprite at position VX, VY with N bytes
	# of sprite data starting at the address stored in I
	# Set VF to 01 if any set pixels are changed to unset, and 00 otherwise
	def draw_spr(self):

		length = self.opcode & 0x000F
		x_loc = (self.opcode & 0x0f00) >> 8
		y_loc = (self.opcode & 0x00f0) >> 4

		for l in range(length):
			byte = format(self.memory[self.i+l], '08b')

			for bit in [int(i) for i in byte]:
				if bit == 1:
					self.drawobj.draw.rect(self.screen, self.white, (x_loc, y_loc, 1, 1))
				else:
					self.drawobj.draw.rect(self.screen, self.black, (x_loc, y_loc, 1, 1))
				x_loc += 1
			x_loc = (self.opcode & 0x0f00) >> 8
			y_loc += 1

	def keys_entry(self):
		pass

	def other_routines(self):
		subroutine = self.opcode & 0x00ff
		# FX29 - I to the memory address to the hexadecimal digit in VX
		if subroutine == 0x29:
			number = (self.opcode & 0x0f00) >> 8
			self.i = number * 5
		# FX33 Store binary coded decimal
		elif subroutine == 0x33:
			x = (self.opcode & 0x0f00) >> 8
			d1 = int(self.registers[x] / 100)
			d2 = int((d1*100 - self.registers[x])/10)
			d3 = self.registers[x] // 10
			self.memory[self.i] = d1
			self.memory[self.i+1] = d2
			self.memory[self.i+2] = d3
		else:
			pass

	def keyboard(self):
		key_addr = (self.opcode & 0x0f00) >> 8
		instruction =  (self.opcode & 0x00ff)
		if instruction == 0x9e:
			# Skip the following instruction if the key corresponding to the hex value currently stored in register VX is pressed
			if KEY_MAPPINGS[key_addr]:
				self.pc += 2
		elif instruction == 0xa1:
			if not KEY_MAPPINGS[key_addr]:
				self.registers['pc'] += 2
