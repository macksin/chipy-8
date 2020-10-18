import argparse
from cpu import CPU
import pygame


def init():
	# command line argument for ROM reading
	parser = argparse.ArgumentParser(description="CHIP-8 Emulator ROM")
	parser.add_argument('path_rom', metavar='R', type=str, help='Path to rom')
	args = parser.parse_args()
	print("ROM = '{}'".format(args.path_rom))

	# read the rom
	with open(args.path_rom, 'rb') as file:
		lines = file.read()
		lines = [(line) for line in lines]  # read in hex

	# CPU
	cpu = CPU()

	for i, rom_byte in enumerate(lines):
		cpu.memory[0x200 + i] = rom_byte

	## Print unique opcodes
	u_opcodes = []


# define a main function
def display():
	# command line argument for ROM reading
	parser = argparse.ArgumentParser(description="CHIP-8 Emulator ROM")
	parser.add_argument('path_rom', metavar='R', type=str, help='Path to rom')
	args = parser.parse_args()
	print("ROM = '{}'".format(args.path_rom))

	# read the rom
	with open(args.path_rom, 'rb') as file:
		lines = file.read()
		lines = [(line) for line in lines]  # read in hex
	#lines = [0xD5, 0x55]

	# CPU
	pygame.init()

	# create a surface on screen that has the size of 240 x 180
	screen_width, screen_height = 64, 32
	scaling_factor = 10
	win = pygame.display.set_mode((screen_width * scaling_factor, screen_height * scaling_factor))
	screen = pygame.Surface((screen_width, screen_height))

	cpu = CPU(pygame, screen, 1)
	#cpu.i = 5

	for i, rom_byte in enumerate(lines):
		cpu.memory[0x200 + i] = rom_byte

	## Print unique opcodes
	u_opcodes = []

	# initialize the pygame module

	# load and set the logo
	# logo = pygame.image.load("logo32x32.png")
	# pygame.display.set_icon(logo)
	pygame.display.set_caption("Emulador")

	black = (0, 0, 0)
	white = (255, 255, 255)

	# define a variable to control the main loop
	running = True

	loop = 0
	# main loop
	while running:
		# pygame.time.delay(1000)
		pygame.time.delay(10)
		# event handling, gets all event from the event queue
		for event in pygame.event.get():
			# only do something if the event is of type QUIT
			if event.type == pygame.QUIT:
				# change the value to False, to exit the main loop
				running = False
		# events
		cpu.fetch_opcode()
		u_opcodes.append(cpu.decode_opcode())
		print(cpu.print_status())
		print(cpu.registers)
		print("\n")
		cpu.pc += 2
		if loop == float('inf'):
			pygame.time.delay(100 * 100)

		# draw test
		pygame.draw.rect(screen, white, (0, 0, 1, 1))

		win.blit(pygame.transform.scale(screen, win.get_rect().size), (0, 0))
		pygame.display.update()

		if cpu.print_status() == -1:
			break

		loop += 1


if __name__ == '__main__':
	# init()
	display()
