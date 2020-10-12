import argparse
from cpu import CPU
import pygame

def main():

    # command line argument for ROM reading
    parser = argparse.ArgumentParser(description="CHIP-8 Emulator ROM")
    parser.add_argument('path_rom', metavar='R', type=str, help='Path to rom')
    args = parser.parse_args()
    print("ROM = '{}'".format(args.path_rom))

    # read the rom
    with open(args.path_rom, 'rb') as file:
        lines = file.read()
        lines = [(line) for line in lines] # read in hex

    # CPU
    cpu = CPU()
    
    for i, rom_byte in enumerate(lines):
        cpu.memory[512+i] = rom_byte

    ## Print unique opcodes
    u_opcodes = []

    for i in range(20):
        cpu.fetch_opcode()    
        u_opcodes.append(cpu.decode_opcode())
        print(cpu.print_status())
        print(cpu.registers)
        print("\n")
        cpu.pc += 2

# define a main function
def display():
     
    # initialize the pygame module
    pygame.init()
    # load and set the logo
    #logo = pygame.image.load("logo32x32.png")
    #pygame.display.set_icon(logo)
    pygame.display.set_caption("Emulador")
     
    black = (0, 0, 0)
    white = (255, 255, 255)

    # create a surface on screen that has the size of 240 x 180
    screen_width, screen_height = 64, 32
    scaling_factor = 10
    win = pygame.display.set_mode((screen_width*scaling_factor, screen_height*scaling_factor))
    screen = pygame.Surface((screen_width, screen_height))
     
    # define a variable to control the main loop
    running = True
     
    # main loop
    while running:
        pygame.time.delay(100)
        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False
        # events

        # draw test
        pygame.draw.rect(screen, white, (0, 0, 1, 1))
        
        win.blit(pygame.transform.scale(screen, win.get_rect().size), (0, 0))
        pygame.display.update()

if __name__ == '__main__':
    main()
    #display()