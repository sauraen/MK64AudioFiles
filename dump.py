'''
MK64AudioFiles - Audio file dump / build tools for Mario Kart 64
Copyright (C) 2022 Sauraen <my name at Google's email service>

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <https://www.gnu.org/licenses/>.
'''

import sys

if sys.version_info.major < 3:
    print('This is a python3 script')
    sys.exit(-1)

import json, struct, os

with open('mk64.json', 'r') as jfile:
    j = json.loads(jfile.read())

with open(j['rom'], 'rb') as romfile:
    rom = romfile.read()
assert rom[0:4] == b'\x80\x37\x12\x40', 'ROM is byte swapped or heavily modded'

def instrs_to_addr(luiaddr, addiuaddr):
    luiaddr, addiuaddr = int(luiaddr, 0), int(addiuaddr, 0)
    assert (luiaddr & 3) == 2 and (addiuaddr & 3) == 2
    upper = struct.unpack('>h', rom[luiaddr:luiaddr+2])[0]
    lower = struct.unpack('>h', rom[addiuaddr:addiuaddr+2])[0]
    addr = (upper << 16) + lower
    assert addr > 0 and addr < len(rom)
    assert (addr & 0xF) == 0
    return addr

audioseq_rom    = instrs_to_addr(j['audioseq_lui'],    j['audioseq_addiu'])
audiobank_rom   = instrs_to_addr(j['audiobank_lui'],   j['audiobank_addiu'])
audiotable_rom  = instrs_to_addr(j['audiotable_lui'],  j['audiotable_addiu'])
seqbanksmap_rom = instrs_to_addr(j['seqbanksmap_lui'], j['seqbanksmap_addiu'])

def extract_index(addr, type, override_count, name, fileext):
    os.makedirs('{}/{}'.format(j['audiofilesdir'], name))
    actual_type = struct.unpack('>h', rom[addr:addr+2])[0]
    assert type == actual_type
    count = struct.unpack('>h', rom[addr+2:addr+4])[0]
    if override_count: count = override_count
    a = addr + 4
    for i in range(count):
        offset, size = struct.unpack('>II', rom[a:a+8])
        a += 8
        with open('{}/{}/{}.{}'.format(j['audiofilesdir'], name, i, fileext), 'wb') as f:
            if size == 0:
                # "Pointer" to another entry in the index
                assert offset < count and offset != i
                f.write(struct.pack('b', offset))
            else:
                assert addr + offset + size <= len(rom)
                f.write(rom[addr+offset:addr+offset+size])
    return count

nbanks = extract_index(audiobank_rom, 1, None, 'bank', 'bin')
extract_index(audiotable_rom, 2, 1, 'table', 'bin')
nseqs  = extract_index(audioseq_rom,  3, None, 'seq', 'aseq')

for i in range(nseqs):
    offset = struct.unpack('>H', rom[seqbanksmap_rom+2*i:seqbanksmap_rom+2*i+2])[0]
    count = rom[seqbanksmap_rom + offset]
    assert count >= 1 and count <= 5 # no actual limit, but unlikely to be correct if > 5
    banks = []
    for k in range(count):
        b = rom[seqbanksmap_rom+offset+1+k]
        assert b < nbanks
        banks.append(b)
    with open('{}/seq/{}.json'.format(j['audiofilesdir'], i), 'w') as jfile:
        jfile.write(json.dumps(banks))

firstaudiorom = min(audioseq_rom, audiobank_rom, audiotable_rom, seqbanksmap_rom)
with open(j['strippedrom'], 'wb') as srom:
    srom.write(rom[0:firstaudiorom])
