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
from crc import UpdateCRC

with open('mk64.json', 'r') as jfile:
    j = json.loads(jfile.read())

romout = open(j['rebuiltrom'], 'wb+')
with open(j['strippedrom'], 'rb') as romin:
    romout.write(romin.read())

def align16():
    while (romout.tell() & 0xF) != 0:
        romout.write(b'\x00')

def build_index(type, override_count, name, fileext):
    start_addr = romout.tell()
    realcount = 0
    for file in os.listdir('{}/{}'.format(j['audiofilesdir'], name)):
        if file.endswith('.' + fileext) and file[:-len(fileext)-1].isdigit():
            realcount += 1
    fullcount = override_count if override_count else realcount
    romout.write(struct.pack('>hh', type, fullcount))
    for i in range(fullcount):
        romout.write(b'\0' * 8)
    align16()
    for i in range(realcount):
        with open('{}/{}/{}.{}'.format(j['audiofilesdir'], name, i, fileext), 'rb') as f:
            data = f.read()
        size = len(data)
        if size == 1:
            # "Pointer" to another entry in the index
            offset = data[0]
            size = 0
        else:
            offset = romout.tell() - start_addr
            romout.write(data)
        romout.seek(start_addr + 4 + 8 * i)
        romout.write(struct.pack('>II', offset, size))
        romout.seek(0, 2) # 0 relative to 2 = eof
        align16()
    if override_count:
        romout.seek(start_addr + 4)
        for i in range(override_count):
            romout.write(struct.pack('>II', offset, size))
        romout.seek(0, 2) # 0 relative to 2 = eof
    return start_addr, realcount

audiobank_rom, nbanks = build_index(1, None, 'bank', 'bin')
audiotable_rom, _     = build_index(2, int(j['audiotable_duplicateentries'], 0), 'table', 'bin')
audioseq_rom, nseq    = build_index(3, None, 'seq', 'aseq')

seqbanksmap_rom = romout.tell()
for i in range(nseq):
    romout.write(b'\0\0')
for i in range(nseq):
    with open('{}/seq/{}.json'.format(j['audiofilesdir'], i), 'r') as jfile:
        banks = json.loads(jfile.read())
    assert len(banks) >= 1 and len(banks) <= 5
    offset = romout.tell() - seqbanksmap_rom
    romout.seek(seqbanksmap_rom+2*i)
    romout.write(struct.pack('>H', offset))
    romout.seek(seqbanksmap_rom + offset)
    romout.write(struct.pack('b', len(banks)))
    for b in banks:
        assert b < nbanks
        romout.write(struct.pack('b', b))
align16()

def addr_to_instrs(luiaddr, addiuaddr, addr):
    luiaddr, addiuaddr = int(luiaddr, 0), int(addiuaddr, 0)
    assert (luiaddr & 3) == 2 and (addiuaddr & 3) == 2
    upper = addr >> 16
    lower = addr & 0xFFFF
    if lower >= 0x8000:
        lower -= 0x10000
        upper += 1
    romout.seek(luiaddr)
    romout.write(struct.pack('>h', upper))
    romout.seek(addiuaddr)
    romout.write(struct.pack('>h', lower))

addr_to_instrs(j['audioseq_lui'],    j['audioseq_addiu'],    audioseq_rom)
addr_to_instrs(j['audiobank_lui'],   j['audiobank_addiu'],   audiobank_rom)
addr_to_instrs(j['audiotable_lui'],  j['audiotable_addiu'],  audiotable_rom)
addr_to_instrs(j['seqbanksmap_lui'], j['seqbanksmap_addiu'], seqbanksmap_rom)

UpdateCRC(romout, 6102)

romout.close()
