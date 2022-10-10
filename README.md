# MK64AudioFiles

Audio file dump / build tools for Mario Kart 64 \
Copyright (C) 2022 Sauraen <my name at Google's email service> \
GPL3 licensed

### How to Use

1. Edit `mk64.json` to specify the paths and ROM files for your project. `"rom"`
should point to the original unmodified ROM.
2. `python3 dump.py` will remove all the audio files from the ROM, placing them
into directories within your specified `"audiofilesdir"`, and the ROM with the
audio files cut out into `"strippedrom"`.
3. Modify `"strippedrom"` and edit the audio files with other tools.
4. `python3 build.py` will produce `"rebuiltrom"`.

### Assumptions / Warnings

The audio files (Audiobank incl. Audiobank Index, Audiotable incl. Audiotable
Index, Audioseq incl. Audioseq Index, and Sequence Banks Map) must be at the end
of the original ROM. Or rather, there must not be any useful / non-padding data
after the first one of these files starts. Any such data will be destroyed.

There may be other tables in `code` with data for each bank or sequence (this is
true in SM64 and OoT), which will not get expanded if you add more banks or
sequences, possibly leading to undesired results. Also, there may be a hard-
coded maximum number of sequences and banks (0x80 and 0x30 respectively in OoT,
unknown for MK64).

There is a hardcoded maximum size of seq0, and a hardcoded maximum size for all
other sequences. Both of these sizes are currently unknown for MK64. There is
probably also a hardcoded maximum bank size.

### Index "Pointers"

An index entry with a size of zero is a "pointer" to another entry in the index,
with the target index represented by the offset. For example, if sequence 3 has
offset 2 and size 0, the game will load sequence 2 instead of sequence 3. This
is represented by a one byte long file, where the one byte is the target index.

### Sequence Banks Map

The list of banks usable for each sequence is represented as a JSON file next to
each sequence file, containing a list of bank numbers. In MK64 vanilla, each
sequence only has one bank.
