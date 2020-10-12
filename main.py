import argparse
from cpu import CPU

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

    # game title
    print([hex(lin) for lin in lines[:10]])

    # CPU
    cpu = CPU()
    
    for i, rom_byte in enumerate(lines):
        cpu.memory[512+i] = rom_byte

    ## Print unique opcodes
    u_opcodes = []

    for i in range(40):
        cpu.fetch_opcode()    
        u_opcodes.append(cpu.decode_opcode())
        print(cpu.print_status())
        cpu.pc += 2

if __name__ == '__main__':
    main()
