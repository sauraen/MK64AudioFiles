'''
 * N64 Checksum (CRC/CIC) Algorithm
 * All known versions of this code have been released under the GPL
 * 
 * Authors/editors in reverse chronological order (AKA rabbit hole):
 * Python port   (C) 2022 Sauraen, released in MK64AudioFiles
 * Modifications (C) 2014-2019 Sauraen, released in seq64
 *     (https://github.com/sauraen/seq64/)
 * Modifications (C) 2005 Parasyte, released in M64ROMExtender1.3b
 *     (http://qubedstudios.rustedlogic.net/Mario64Tools.htm)
 *     (http://www.smwcentral.net/?p=section&a=details&id=4812)
 * Modifications (C) 2002-2004 dbjh, released in ucon64-2.0.0
 *               (C) 1999-2001 NoisyB <noisyb@gmx.net> 
 *     (http://ucon64.sourceforge.net/)
 * Written/RE'd  (C) 1997 Andreas Sterbenz <stan@sbox.tu-graz.ac.at>,
 *     released as chksum64 V1.2 (retrieved from 
 *     https://github.com/DragonMinded/libdragon/blob/master/tools/chksum64.c )
 * Original Code (C) ???? "Nagra"
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * 
*************************************************************************
Copyright/Attribution Notice from n64sums.c in M64ROMExtender1.3b,
as downloaded from http://qubedstudios.rustedlogic.net/Mario64Tools.htm
or http://www.smwcentral.net/?p=section&a=details&id=4812 :
*************************************************************************
 * 
 * snesrc - SNES Recompiler
 *
 * Copyright notice for this file:
 *  Copyright (C) 2005 Parasyte
 *
 * Based on uCON64's N64 checksum algorithm by Andreas Sterbenz
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*************************************************************************
Copyright/Attribution Notice from n64.c in ucon64-2.0.0,
as downloaded from http://ucon64.sourceforge.net/ :
*************************************************************************
 * n64.c - Nintendo 64 support for uCON64
 * 
 * Copyright (c) 1999 - 2001 NoisyB <noisyb@gmx.net>
 * Copyright (c) 2002 - 2004 dbjh
 * 
 * 
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
*************************************************************************
Copyright/Attribution Notice from chksum64.c, as downloaded from
https://github.com/DragonMinded/libdragon/blob/master/tools/chksum64.c :
*************************************************************************
 * chksum64 V1.2, a program to calculate the ROM checksum of Nintendo64 ROMs.
 * Copyright (C) 1997  Andreas Sterbenz (stan@sbox.tu-graz.ac.at)
 * 
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*************************************************************************
Statements of original authorship from chksum64.c (same file):
*************************************************************************
  printf("CHKSUM64 V1.2   Copyright (C) 1997 Andreas Sterbenz (stan@sbox.tu-graz.ac.at)\n");
  printf("This program is released under the terms of the GNU public license. NO WARRANTY\n\n");
[...]
  fprintf(stderr, "Usage: %s [-r] [-o|-s] <File>\n\n", progname);
  fprintf(stderr, "This program calculates the ROM checksum for Nintendo64 ROM images.\n");
  fprintf(stderr, "Checksum code reverse engineered from Nagra's program.\n");
[...]
  Below is the actual checksum calculation algorithm, which was
  reverse engineered out of Nagra's program.

  As you can see, the algorithm is total crap. Obviously it was
  designed to be difficult to guess and reverse engineer, and not
  to give a good checksum. A simple XOR and ROL 13 would give a
  just as good checksum. The ifs and the data dependent ROL are really
  extreme nonsense.
*************************************************************************
Who this Nagra person is, or what code this originally appeared in, is
anyone's guess. My guess is that the algorithm was derived from an
analysis of some MIPS code (probably the actual checksum-verifying
routine in some ROM's boot code), due to the fact that there the
intermediate values are named t1-t6, which are temporary registers in the
R4300i CPU.
*************************************************************************
'''

import sys

if sys.version_info.major < 3:
    print('This is a python3 script')
    sys.exit(-1)

import struct

def UpdateCRC(rom, cic_name):
    '''
    rom must be a file object opened with 'wb+'.
    '''
    cic_seed_list = {
        6101: 0xF8CA4DDC,
        6102: 0xF8CA4DDC,
        6103: 0xA3886759,
        6105: 0xDF26F436,
        6106: 0x1FEA617A
    }
    def ROL(i, b):
        return ((i << b) & 0xFFFFFFFF) | (i >> (32 - b))
    N64_HEADER_SIZE = 0x40
    N64_BC_SIZE     = 0x1000 - N64_HEADER_SIZE
    N64_CRC1        = 0x10
    N64_CRC2        = 0x14
    CHECKSUM_START  = 0x00001000
    CHECKSUM_LENGTH = 0x00100000
    try:
        seed = cic_seed_list[cic_name]
    except KeyError:
        raise RuntimeError('CIC name must be integer chip part number!')
    t1 = t2 = t3 = t4 = t5 = t6 = seed
    rom.seek(CHECKSUM_START)
    for i in range(CHECKSUM_START, CHECKSUM_START + CHECKSUM_LENGTH, 4):
        d = struct.unpack('>I', rom.read(4))[0]
        if ((t6 + d) & 0xFFFFFFFF) < t6: t4 += 1
        t6 += d
        t6 &= 0xFFFFFFFF
        t3 ^= d
        r = ROL(d, d & 0x1F)
        t5 += r
        t5 &= 0xFFFFFFFF
        if t2 > d:
            t2 ^= r
        else:
            t2 ^= t6 ^ d
        if cic_name == 6105:
            rom.seek(N64_HEADER_SIZE + 0x0710 + (i & 0xFF))
            t1 += struct.unpack('>I', rom.read(4))[0] ^ d
            rom.seek(i+4)
        else:
            t1 += t5 ^ d
    t4 &= 0xFFFFFFFF
    t1 &= 0xFFFFFFFF
    if cic_name == 6103:
        crc1 = (t6 ^ t4) + t3
        crc2 = (t5 ^ t2) + t1
    elif cic_name == 6106:
        crc1 = (t6 * t4) + t3
        crc2 = (t5 * t2) + t1
    else:
        crc1 = t6 ^ t4 ^ t3
        crc2 = t5 ^ t2 ^ t1
    rom.seek(N64_CRC1)
    rom.write(struct.pack('>II', crc1, crc2))

if __name__ == '__main__':
    assert len(sys.argv) == 3
    with open(sys.argv[1], 'wb+') as rom:
        UpdateCRC(rom, int(sys.argv[2]))
