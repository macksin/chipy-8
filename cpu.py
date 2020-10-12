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
    """
    docstring
    """
    
    def __init__(self):
        self.opcode = 0
        self.memory = [None] * 4096 # 4096 locations
        self.registers = [None] * 16 # 16 registers
        self.i = 0
        self.pc = 0x200 # program counter starts
        self.gfs = [None] * (64 * 32) # 64 * 32
        self.stack = [None] * 16
        self.sp = 0 # reset stack ppinter
        self.key = [None] * 16 # 16 hex

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
            0xA: 'LOAD I,',
            0xB: 'JUMP',
            0xC: 'RAND',
            0xD: 'DRAW',
            0xE: 'KEYS',
            0xF: 'OTHERS'
        }

        # implemented operations
        self.implemented = ['JUMP', 'LOAD']
        

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
        pp = "instr: {} \tcode: {} \tpc: {}/{}\tsp={}".format(\
            hex(self.opcode),
            self.operations_names[self.decode_opcode()],
            self.pc,
            hex(self.pc),
            self.sp)
        if self.operations_names[self.decode_opcode()] in self.implemented:
            self.operations_search[self.decode_opcode()]()
            
        return pp

    def operation_search(self):
        pass

    def clear():
        pass

    def jmp_addr(self):
        self.pc = self.opcode & 0x0fff

    def jmp_sub():
        pass

    def skp_if_reg_eq_var():
        pass

    def skp_if_reg_neq_var():
        pass

    def skp_if_reg_e_reg():
        pass

    def load_value(self):
        memory_location = self.opcode >> 8 & 0x000f
        value_to_store = self.opcode & 0x00ff
        self.registers[memory_location] = value_to_store

    def add_vlr_to_reg():
        pass

    def logical():
        pass

    def skp_reg_ne_reg():
        pass

    def store_in_reg_i():
        pass

    def jmp_to_nnn_plus_v0():
        pass

    def random_number():
        pass

    def draw_spr():
        pass

    def keys_entry():
        pass

    def other_routines():
        pass