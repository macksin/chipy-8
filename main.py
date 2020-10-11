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
        lines = [hex(line) for line in lines] # read in hex

    # game title
    print(lines[:10])
    for i in range(10):
        print(lines[i])

    # CPU
    cpu = CPU()
    
    for i, rom_byte in enumerate(lines):
        cpu.memory[512+i] = rom_byte

    ## Print unique opcodes
    u_opcodes = []

    for i in range(len(lines)//2):
        cpu.fetch_opcode()    
        u_opcodes.append(cpu.decode_opcode())
        cpu.pc += 2
    u_opcodes = set(u_opcodes)
    print(u_opcodes)
    print(sorted(u_opcodes))
    print(len(u_opcodes))

    #print(cpu.memory)
    #print(cpu.fetch_opcode())
    #print(cpu.decode_opcode())
    #cpu.pc += 2
    #print(cpu.fetch_opcode())
    #print(cpu.decode_opcode())


if __name__ == '__main__':
    main()