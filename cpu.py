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
			0x1: 'JUMP',
			0x2: 'CALL',
			0x3: 'SKE',
			0x4: 'SKNE',
			0x5: 'SKE',
			0x6: 'LOAD',
			0x7: 'ADD',
			0x8: 'LOGIC',
			0x9: 'SKNE',
			0xA: 'LOAD I',
			0xB: 'JUMP',
			0xC: 'RAND',
			0xD: 'DRAW',
			0xE: 'KEYS',
			0xF: 'OTHERS'
		}

		# implemented operations
		self.implemented = ['JUMP', 'LOAD', 'DRAW', 'LOAD I', 'LOGIC', 'ADD', 'SKNE', 'SKE', 'CALL', 'SYS', 'OTHERS']
		

	def fetch_opcode(self):
		curr = self.memory[self.pc] << 8 | self.memory[self.pc+1]
		self.opcode = curr
		return self.opcode

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

	def operation_search(self):
		pass

	def clear(self):
		"""Auxiliary functions"""
		if (self.opcode == 0x00EE):
			self.pc = self.sp
			self.stack.pop()
			try:
				self.pc = self.stack[-1]
			except:
				pass
		else:
			pass

	def jmp_addr(self):
		self.pc = (self.opcode & 0x0fff) - 2

	def jmp_sub(self):
		"""2NNN - Execute subroutine starting at address NNN"""
		address = self.opcode & 0x0fff
		self.stack.append(self.pc)
		self.sp = self.pc
		self.pc = address - 2
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
		mem_location = (self.opcode & 0x0f00) >> 8
		value = self.opcode & 0x00ff
		self.registers[mem_location] = value
		if self.verbose > 0:
			print("LOAD {} TO {}".format(hex(value), hex(mem_location)))

	def add_vlr_to_reg(self):
		"""7XNN - Add the value NN to register VX"""
		value = self.opcode & 0xff
		register = (self.opcode & 0x0f00) >> 8
		if self.registers[register] == None:
			self.registers[register] = value
		else:
			self.registers[register] = (self.registers[register] + value) & 0xff

	def logical(self):
		mini_operator = self.opcode & 0x000f

		# to X from Y
		if mini_operator == 0x0:
			y = self.opcode >> 4 & 0xf
			x = self.opcode >> 8 & 0xf
			self.registers[x] = self.registers[y]

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
			y = self.opcode >> 4 & 0xf
			x = self.opcode >> 8 & 0xf
			_ = self.registers[x] + self.registers[y]
			if _ > 255:
				self.registers[x] = 256 - _
				self.registers[0xF] = 1
			else:
				self.registers[x] = _
				self.registers[0xF] = 0

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
		self.i = self.opcode & 0x0fff

	def jmp_to_nnn_plus_v0(self):
		"""BNNN - Jump to address NNN + V0"""
		jumpto = self.opcode & 0x0fff
		self.pc = (jumpto + self.registers[0])
		

	def random_number():
		pass

	# DXYN - Draw a sprite at position VX, VY with N bytes 
	# of sprite data starting at the address stored in I 
	# Set VF to 01 if any set pixels are changed to unset, and 00 otherwise
	def draw_spr(self):
		length = self.opcode & 0x000f
		x_location = (self.opcode & 0x0f00) >> 8
		y_location = (self.opcode & 0x00f0) >> 4
		for b in range(length):
			_byte = self.memory[self.i+b]
			for bit in [int(i) for i in bin(0xf)[2:]]:
				if bit == 1:
					self.drawobj.draw.rect(self.screen, self.white, (x_location, y_location, 1, 1))
				else:
					self.drawobj.draw.rect(self.screen, self.black, (x_location, y_location, 1, 1))
				x_location += 1
			x_location = (self.opcode & 0x0f00) >> 8
			y_location += 1
		
	def keys_entry():
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