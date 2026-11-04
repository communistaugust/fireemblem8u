#!/usr/bin/env python3
"""
classify_dump.py - assign a real data type to every file in dumping_file/

Usage (from the repo root):
    python3 scripts/classify_dump.py [--repo .] [--out reports/dumping_file_types.csv]

For each file it combines four independent sources of evidence:
  1. content   - decompress (GBA LZ77 0x10) if possible, then test the bytes
                 against palette / FE TSA / raw tilemap / 4bpp tile shapes
  2. usage     - how the incbin's label is used in src/*.c (Decompress,
                 ApplyPalette, CallARM_FillTileRect, APProc_Create, ...)
                 including the destination argument of Decompress
  3. name      - the prefix of the dumped name (Img/Tsa/Pal/Ap/AnimScr...)
  4. rom refs  - pointers to the file's address inside baserom.gba and the
                 symbol (from fireemblem8.map) that holds each pointer
It then picks a final type with a confidence, and proposes partners
(palette / tilemap for an image, image for a tilemap ...) for PNG rebuilding.
"""
import argparse, bisect, csv, os, re, struct, sys
from collections import defaultdict, Counter

# --------------------------------------------------------------- LZ77 -------
def lz77_decompress(data):
    """GBA BIOS LZ77 (type 0x10). Returns (out, consumed) or None if invalid."""
    if len(data) < 4 or data[0] != 0x10:
        return None
    size = data[1] | data[2] << 8 | data[3] << 16
    if size == 0 or size > 0x40000:
        return None
    out = bytearray()
    i = 4
    try:
        while len(out) < size:
            flags = data[i]; i += 1
            for bit in range(8):
                if len(out) >= size:
                    break
                if flags & (0x80 >> bit):
                    b1, b2 = data[i], data[i + 1]; i += 2
                    length = (b1 >> 4) + 3
                    disp = ((b1 & 0xF) << 8 | b2) + 1
                    if disp > len(out):
                        return None
                    for _ in range(length):
                        out.append(out[-disp])
                else:
                    out.append(data[i]); i += 1
    except IndexError:
        return None
    return bytes(out[:size]), i

def u16s(b):
    n = len(b) // 2
    return struct.unpack('<%dH' % n, b[:n * 2])

# ------------------------------------------------------------ content -------
def test_palette(b):
    if len(b) < 4 or len(b) % 2 or len(b) > 0x400:
        return 0, ''
    v = u16s(b)
    if any(x & 0x8000 for x in v):
        return 0, ''
    if len(b) % 32:
        return 0.35, '%d colors (partial bank)' % len(v)
    banks = len(b) // 32
    if banks > 16:
        return 0, ''
    score = 0.6 + (0.2 if banks <= 2 else 0) + (0.1 if len(set(v)) > 2 else -0.3)
    return score, '%d bank(s)' % banks

def tilemap_stats(v):
    tiles = [x & 0x3FF for x in v]
    pals = Counter(x >> 12 for x in v)
    top2 = sum(c for _, c in pals.most_common(2)) / len(v)
    small = sum(1 for t in tiles if t < 0x300) / len(v)
    # adjacent entries often increment by 1 or repeat in a tilemap
    steps = sum(1 for a, b in zip(tiles, tiles[1:]) if b - a in (0, 1)) / max(1, len(v) - 1)
    return top2, small, steps, len(pals)

def test_fe_tsa(b):
    """FE 'TSA': u8 w-1, u8 h-1, then w*h u16 screen entries (rows bottom-up)."""
    if len(b) < 4:
        return 0, ''
    w, h = b[0] + 1, b[1] + 1
    need = 2 + w * h * 2
    if not (need <= len(b) <= need + 3) or w > 64 or h > 64:
        return 0, ''
    top2, small, steps, _ = tilemap_stats(u16s(b[2:need]))
    score = 0.55 + 0.25 * top2 + 0.15 * steps
    return score, '%dx%d tiles' % (w, h)

def test_raw_tilemap(b):
    if len(b) < 64 or len(b) % 2:
        return 0, ''
    v = u16s(b)
    top2, small, steps, npal = tilemap_stats(v)
    if top2 < 0.9 or small < 0.95:
        return 0, ''
    score = 0.3 + 0.3 * steps + (0.15 if len(b) in (0x500, 0x600, 0x800, 0x1000, 0x2000) else 0)
    return score, '%d entries' % len(v)

def test_tiles4(b):
    if len(b) == 0 or len(b) % 32:
        return 0, ''
    n = len(b) // 32
    # 4bpp pixel data: nibbles spread across many values
    nib = Counter()
    for x in b[:4096]:
        nib[x & 15] += 1; nib[x >> 4] += 1
    score = 0.45 + (0.1 if len(nib) >= 4 else 0)
    return score, '%d tiles' % n

def content_guess(b):
    cands = []
    for name, fn in (('palette', test_palette), ('tsa', test_fe_tsa),
                     ('tilemap', test_raw_tilemap), ('gfx4bpp', test_tiles4)):
        s, d = fn(b)
        if s > 0:
            cands.append((s, name, d))
    cands.sort(reverse=True)
    if not cands:
        return 'data', 0.2, '%d bytes' % len(b), []
    return cands[0][1], cands[0][0], cands[0][2], cands

# --------------------------------------------------------------- names ------
NAME_HINTS = [
    (r'^(g?Pal|Pal\d|gUiFramePalette|gUiBarPalette|.*Palette)', 'palette'),
    (r'^(g?Img|g?Gfx|TileSet|gUiFrameImage|gUnkUiFrameImage|Obj|obj)', 'gfx4bpp'),
    (r'^(g?Tsa|g?TSA|TSA\d|Tsa\d|TsaConf)', 'tsa'),
    (r'^(Ap_|ApHandle|AP_)', 'ap_sprite'),
    (r'^ApConf', 'ap_conf'),
    (r'^AnimScr', 'anim_script'),
    (r'^(AnimSprite|SpriteAnim)', 'anim_sprite'),
    (r'RomHeader', 'rom_header'),
]
def name_hint(label):
    for rx, t in NAME_HINTS:
        if re.search(rx, label):
            return t
    return ''

def ext_hint(fn):
    f = os.path.basename(fn).lower()
    if '.gbapal' in f or '.agbpal' in f: return 'palette'
    if '.4bpp' in f or '.feimg' in f: return 'gfx4bpp'
    if '.tsa' in f or '.fetsa' in f: return 'tilemap'
    return ''

# --------------------------------------------------------------- usage ------
GFX_DEST = re.compile(r'CHR|VRAM|OBJ_VRAM|0x060|0x6010|OBJ_CHR|BG_CHR|TileDataOffset|gfx|Gfx', re.I)
BUF_DEST = re.compile(r'Buffer|gBuf|gGeneric|gEkrTsa|Tsa|tsa', re.I)
CALL_TYPES = {
    'ApplyPalette': 'palette', 'ApplyPalettes': 'palette', 'SpellFx_RegisterBgPal': 'palette',
    'SpellFx_RegisterObjPal': 'palette', 'CopyToPaletteBuffer': 'palette', 'StartPalFade': 'palette',
    'StartPaletteAnimatorReverse': 'palette', 'StartPaletteAnimatorNormal': 'palette',
    'SaveMenuCopyPalette': 'palette', 'CopyPalWithFade': 'palette', 'PAL_BUF_COLOR': 'palette',
    'SpellFx_RegisterBgGfx': 'gfx4bpp', 'SpellFx_RegisterObjGfx': 'gfx4bpp', 'EfxTmDecompress': 'tsa',
    'CallARM_FillTileRect': 'tsa', 'SpellFx_WriteBgMap': 'tsa', 'RegisterTsaWithOffset': 'tsa',
    'EfxTmCpyBG': 'tsa', 'EfxTmCpyExt': 'tsa', 'EfxTmCpyBgHFlip': 'tsa', 'EfxTmCpyExtHFlip': 'tsa',
    'APProc_Create': 'ap_sprite', 'AP_Create': 'ap_sprite', 'PutSpriteExt': 'oam_sprite',
    'SetMuSpecialSprite': 'ap_sprite',
}

def enclosing_call(text, pos):
    """Name and argument text of the innermost call containing text[pos]."""
    depth = 0
    i = pos
    while i > 0:
        i -= 1
        c = text[i]
        if c == ')': depth += 1
        elif c == '(':
            if depth == 0:
                m = re.search(r'([A-Za-z_]\w*)\s*$', text[max(0, i - 60):i])
                # find end of call
                j, d = i + 1, 1
                while j < len(text) and d:
                    if text[j] == '(': d += 1
                    elif text[j] == ')': d -= 1
                    j += 1
                return (m.group(1) if m else ''), text[i + 1:j - 1]
            depth -= 1
        elif c in ';{}':
            return '', ''
    return '', ''

def split_blocks(text):
    """Split C text into top-level blocks (functions / initializers)."""
    blocks, depth, start = [], 0, 0
    for i, c in enumerate(text):
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                blocks.append((start, i + 1)); start = i + 1
        elif c == ';' and depth == 0:
            start = i + 1
    return blocks

# ---------------------------------------------------------------- main ------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default='.')
    ap.add_argument('--out', default='reports/dumping_file_types.csv')
    ap.add_argument('--dirs', nargs='+', default=['dumping_file'],
                    help='dumping_file and/or graphics (graphics: every incbin\'d file under graphics/)')
    ap.add_argument('--yml', default='', help='also classify every file listed in this extraction yml')
    args = ap.parse_args()
    R = lambda *p: os.path.join(args.repo, *p)

    dump_dir = R('dumping_file')
    # dumping_file/ was moved into graphics/<category>/: use --dirs graphics for those files
    files = (['dumping_file/' + f for f in sorted(os.listdir(dump_dir))]
             if 'dumping_file' in args.dirs and os.path.isdir(dump_dir) else [])

    # --- hardcoded_incbin.txt : name,addr,size
    addr_of = {}
    if os.path.exists(R('hardcoded_incbin.txt')):
        for line in open(R('hardcoded_incbin.txt'), encoding='utf-8'):
            p = line.strip().split(',')
            if len(p) >= 3:
                addr_of[p[0]] = int(p[1], 16)

    # --- incbins in data/*.s with label, source file and order
    inc = {}       # filename -> dict
    order = defaultdict(list)   # s file -> [filename...]
    rx_inc = re.compile(r'\.incbin\s+"(?:\./)?((?:dumping_file|graphics)/[^"]+)"')
    rx_lab = re.compile(r'^\s*([A-Za-z_]\w*):')
    for root in ('data', 'asm', 'src'):
        for dp, _, fns in os.walk(R(root)):
            for fn in fns:
                if not fn.endswith('.s'):
                    continue
                path = os.path.join(dp, fn)
                last_label = None
                lines = open(path, encoding='utf-8', errors='replace').read().splitlines()
                for ln, line in enumerate(lines):
                    m = rx_lab.match(line)
                    if m:
                        last_label = (m.group(1), ln); continue
                    m = rx_inc.search(line)
                    if m:
                        f = m.group(1)
                        lab = last_label[0] if last_label and ln - last_label[1] <= 2 else ''
                        rel = os.path.relpath(path, args.repo)
                        inc[f] = {'s_file': rel, 'line': ln + 1, 'label': lab}
                        order[rel].append(f)
                        last_label = None
                    elif line.strip() and not line.strip().startswith(('.global', '@', '.align', '.section')):
                        pass

    if 'graphics' in args.dirs:
        files += sorted(f for f in inc if f.startswith('graphics/') and os.path.exists(R(f)))
    yml_entry = {}
    if args.yml:
        import yaml
        from gfx_yml import load_yml   # here: gfx_yml imports this module (lz77_decompress)
        for e in load_yml(R(args.yml))['files']:
            pth = os.path.join(e['location'], e['file_name'] + '.' + e['type'])
            yml_entry[pth] = e
            if pth not in files and os.path.exists(R(pth)) and not pth.startswith('dumping_file/'):
                files.append(pth)
            inc.setdefault(pth, {'s_file': '', 'line': 0, 'label': e['name']})
            if not inc[pth]['label']:
                inc[pth]['label'] = e['name']
            addr_of.setdefault(pth, int(e['adress'], 16))

    # --- map symbols (for rom pointer refs)
    syms = []
    if os.path.exists(R('fireemblem8.map')):
        for line in open(R('fireemblem8.map'), encoding='utf-8', errors='replace'):
            m = re.match(r'\s+0x(08[0-9a-fA-F]{6})\s+([A-Za-z_]\w*)\s*$', line)
            if m:
                syms.append((int(m.group(1), 16), m.group(2)))
    syms.sort()
    sym_addrs = [a for a, _ in syms]
    def sym_at(a):
        i = bisect.bisect_right(sym_addrs, a) - 1
        return '%s+0x%X' % (syms[i][1], a - syms[i][0]) if i >= 0 else '0x%08X' % a
    sym_addr = {n: a for a, n in syms}
    for f, d in inc.items():
        if d['label'] and d['label'] in sym_addr:
            addr_of.setdefault(f, sym_addr[d['label']])
    rom = open(R('baserom.gba'), 'rb').read() if os.path.exists(R('baserom.gba')) else b''
    ptr_index = defaultdict(list)
    if rom:
        for off in range(0, len(rom) - 3, 4):
            v = rom[off] | rom[off+1] << 8 | rom[off+2] << 16 | rom[off+3] << 24
            if 0x08000000 <= v < 0x08000000 + len(rom):
                ptr_index[v].append(0x08000000 + off)

    # --- C usage
    label_to_file = {}
    for f in files:
        lab = inc.get(f, {}).get('label') or os.path.basename(f).split('.')[0]
        label_to_file[lab] = f
    rx_ident = re.compile(r'[A-Za-z_]\w*')
    class _M:
        def __init__(s, m): s.m = m
        def group(s, i): return s.m.group(0)
        def start(s): return s.m.start()
    class _RX:
        def finditer(s, text):
            for m in rx_ident.finditer(text):
                if m.group(0) in label_to_file:
                    yield _M(m)
    rx_any = _RX()
    usage = defaultdict(list)          # file -> [(func, dest/args)]
    cooc = defaultdict(set)            # file -> files used in same C block
    block_of = defaultdict(set)
    for root in ('src', 'include', 'data', 'asm'):
        for dp, _, fns in os.walk(R(root)):
            for fn in fns:
                if not fn.endswith(('.c', '.h', '.s')):
                    continue
                path = os.path.join(dp, fn)
                text = open(path, encoding='utf-8', errors='replace').read()
                if '.incbin' in text and fn.endswith('.s'):
                    text = '\n'.join(l for l in text.splitlines() if '.incbin' not in l)
                if fn.endswith('.c'):
                    blocks = split_blocks(text)
                    starts = [s for s, _ in blocks]
                for m in rx_any.finditer(text):
                    f = label_to_file[m.group(1)]
                    rel = os.path.relpath(path, args.repo)
                    if fn.endswith('.c'):
                        func, argtxt = enclosing_call(text, m.start())
                        usage[f].append((func, argtxt.strip().replace('\n', ' ')[:80], rel))
                        bi = bisect.bisect_right(starts, m.start()) - 1
                        if bi >= 0 and blocks[bi][0] <= m.start() < blocks[bi][1]:
                            block_of[(rel, bi)].add(f)
                    elif fn.endswith('.s') and re.search(r'\.word\s', text[max(0, m.start()-40):m.start()]):
                        usage[f].append(('.word', '', rel))
                    elif fn.endswith('.h'):
                        usage[f].append(('decl', text[max(0, m.start()-60):m.start()].splitlines()[-1].strip()[:60], rel))
    for fs in block_of.values():
        for f in fs:
            cooc[f] |= fs - {f}

    # ranges occupied by dumped files: words inside them are data, not pointers
    def addr_for(f):
        b = os.path.basename(f).split('.')[0]
        a = addr_of.get(f) or addr_of.get(b)
        if a is None and f.startswith('dumping_file/'):
            m = re.search(r'(?:0x)?(08[0-9A-Fa-f]{6})', b)
            a = int(m.group(1), 16) if m else None
        return a
    ranges = sorted((a, a + os.path.getsize(R(f))) for f in files for a in [addr_for(f)] if a)
    rstarts = [a for a, _ in ranges]
    def in_dump(p):
        i = bisect.bisect_right(rstarts, p) - 1
        return i >= 0 and ranges[i][0] <= p < ranges[i][1]

    # --- per-file analysis
    rows, info = [], {}
    for f in files:
        raw = open(R(f), 'rb').read()
        base = os.path.basename(f).split('.')[0]
        lab = inc.get(f, {}).get('label', '')
        addr = addr_for(f)
        dec = lz77_decompress(raw)
        compressed = bool(dec) and len(raw) - dec[1] <= 3
        lz_tail = 0
        if dec and not compressed and dec[1] >= len(raw) // 2:
            compressed, lz_tail = True, len(raw) - ((dec[1] + 3) & ~3)
        data = dec[0] if compressed else raw
        if f.endswith('.fk') and len(raw) >= 4:
            compressed, data = 'fk', raw[4:]
        ctype, cscore, cdetail, cands = content_guess(data)
        eh0 = ext_hint(f)
        for sc, nm, dt in cands:
            if nm == eh0 and nm != ctype and cscore - sc < 0.3:
                ctype, cscore, cdetail = nm, sc, dt
                break

        # usage-based type
        votes = Counter()
        weak_votes = set()      # types that only come from a 'copy into VRAM' (could be a screen block)
        callers = Counter()
        for func, argtxt, _ in usage.get(f, []):
            if func:
                callers[func] += 1
            t = CALL_TYPES.get(func)
            if t:
                votes[t] += 2
            elif func in ('Decompress', 'LZ77UnCompVram', 'LZ77UnCompWram', 'CpuFastCopy', 'CpuCopy16', 'CpuFastCopy'):
                dest = argtxt.split(',', 1)[1] if ',' in argtxt else ''
                if GFX_DEST.search(dest): votes['gfx4bpp'] += 2; weak_votes.add('gfx4bpp')
                elif re.search(r'PAL|Palette|pal', dest): votes['palette'] += 2
                elif BUF_DEST.search(dest): votes['tsa_or_buffer'] += 1
        utype = votes.most_common(1)[0][0] if votes else ''
        if utype == 'tsa_or_buffer':
            utype = 'tsa' if ctype in ('tsa', 'tilemap') else ''

        ntype = name_hint(lab or base) or ext_hint(f)
        # repo folders whose content is known from the build rules
        for rx_, t_ in ((r'/map/layout/', 'map_layout'), (r'Changes\w*_change_\d+', 'map_change'), (r'TileConfiguration', 'map_tileconfig'), (r'data/banim/.*_oam_[lr]\.', 'banim_oam'),
                        (r'data/banim/.*_motion\.', 'banim_script'), (r'data/banim/.*_modes\.', 'banim_modes')):
            if re.search(rx_, f):
                ntype = t_

        # rom pointer refs
        refs = [p for p in ptr_index.get(addr, []) if not in_dump(p)] if addr else []
        ref_syms = [sym_at(r) for r in refs[:6]]

        # holder symbols (tables in ROM that point at this file)
        holders = [x.split('+')[0] for x in ref_syms]
        htype = ''
        for h in holders:
            if re.search(r'Tsa|TSA', h): htype = 'tilemap'
            elif re.search(r'Pal', h): htype = 'palette'
            elif re.search(r'Img|Gfx', h): htype = 'gfx4bpp'
            elif re.search(r'WMPath', h): htype = 'wm_path'
            if htype: break

        # interior pointers: is this an unsplit blob holding several items?
        interior = []
        if addr and rom and not compressed:   # nothing can point inside an LZ77 stream
            for t in range(addr + 4, addr + len(raw), 4):
                srcs = [p for p in ptr_index.get(t, []) if not in_dump(p)]
                if srcs:
                    interior.append('+0x%X' % (t - addr))

        # ---------- decide
        notes = []
        fam = lambda t: 'tilemap' if t in ('tsa', 'tilemap') else t
        ctype_f = fam(ctype); cand_f = [fam(c[1]) for c in cands]
        ntype = fam(ntype); utype = fam(utype)
        final, conf = ctype_f, 'low'
        if not compressed and len(raw) >= 4 and raw[0] == 0x10:
            notes.append('starts with 0x10 but is not a clean LZ77 stream')
        if utype in weak_votes and ntype and fam(ntype) != utype and (fam(ntype) in [fam(c[1]) for c in cands] or name_hint(lab)):
            utype = ''          # a name saying otherwise wins over a plain copy into VRAM
        if ntype in ('map_layout', 'map_change', 'map_tileconfig', 'banim_oam', 'banim_script', 'banim_modes'):
            final, conf = ntype, 'high'
        elif utype:
            final = utype
            agree = utype == ctype_f or utype in cand_f or utype.startswith(('ap_', 'oam_', 'anim'))
            conf = 'high' if agree else 'medium'
            if not agree:
                notes.append('usage says %s, content says %s' % (utype, ctype))
        elif ntype and not base.startswith('gUnknown'):
            agree = ntype == ctype_f or ntype in cand_f or ntype.startswith(('ap_', 'anim', 'rom_', 'map_'))
            final = ntype
            conf = 'high' if (ntype == ctype_f or ntype.startswith(('ap_', 'anim', 'rom_', 'map_'))) else ('medium' if agree else 'low')
            if not agree:
                notes.append('name says %s, content says %s' % (ntype, ctype))
        elif htype:
            final = htype
            conf = 'high' if htype == ctype_f else ('medium' if htype in cand_f or htype == 'wm_path' else 'low')
            if htype not in cand_f and htype != ctype_f and htype != 'wm_path':
                notes.append('table %s suggests %s, content says %s' % (holders[0], htype, ctype))
        else:
            conf = 'medium' if cscore >= 0.75 else 'low'
        eh = ext_hint(f)
        if eh and eh != final:
            notes.append('extension implies %s' % eh)
        if not compressed and f.endswith('.lz'):
            notes.append('.lz extension but data is not LZ77')
        if compressed and not f.endswith('.lz'):
            notes.append('LZ77 compressed but extension lacks .lz')
        if not refs and not usage.get(f) and not lab:
            notes.append('unlabeled and unreferenced: padding or unsplit data')
        if lz_tail:
            notes.append('%d bytes after the LZ77 data: probably the next item, split it' % lz_tail)
        if interior:
            notes.append('pointers into it at %s -> probably several items, split it' % ','.join(interior[:6]))
        fmt = ''
        if final == 'tilemap':
            fmt = 'fe_tsa' if ctype == 'tsa' or 'tsa' in [c[1] for c in cands] else 'raw_screen'
            r_detail = cdetail
        hoff = {}
        for x in ref_syms:
            h, _, o = x.partition('+')
            hoff[h] = int(o, 16) if o else 0
        info[f] = dict(final=final, base=base, s=inc.get(f, {}).get('s_file', ''), holders=set(holders),
                       addr=addr or 0, hoff=hoff)
        rows.append(dict(
            file=f, label=lab, rom_addr='0x%08X' % addr if addr else '',
            s_file=inc.get(f, {}).get('s_file', ''), size=len(raw),
            compressed=('lz77' if compressed is True else compressed) if compressed else '', data_size=len(data),
            content_type=ctype, content_detail=cdetail, tilemap_format=fmt,
            usage_type=utype, callers=';'.join('%s x%d' % kv for kv in callers.most_common(4)),
            name_type=ntype, final_type=final, confidence=conf,
            rom_ptr_refs=len(refs), ref_by=';'.join(ref_syms),
            notes='; '.join(notes)))

    # --- partners
    def stem(b):
        b = re.sub(r'^(g?Img|g?Gfx|g?Pal|g?Tsa|g?TSA|TSA|Tsa|Pal|Img|TileSet)\d*_?', '', b)
        return re.sub(r'(_[A-Z]|\d+)$', '', b).lower()
    by_stem = defaultdict(list)
    for f, d in info.items():
        if not d['base'].startswith('gUnknown'):
            by_stem[stem(d['base'])].append(f)
    by_holder = defaultdict(set)
    for f, d in info.items():
        for h in d['holders']:
            by_holder[h].add(f)
    for fs in by_holder.values():
        if len(fs) <= 40:
            for f in fs:
                cooc[f] |= fs - {f}
    for r in rows:
        f, t = r['file'], r['final_type']
        want = {'gfx4bpp': ('palette', 'tilemap'),
                'tilemap': ('gfx4bpp', 'palette'), 'palette': ('gfx4bpp',)}.get(t)
        if not want:
            r['partners'] = ''; r['partner_source'] = ''; continue
        found, src = [], ''
        c = [g for g in cooc.get(f, ()) if info[g]['final'] in want]
        if c:
            def dist(g):
                common = set(info[f]['hoff']) & set(info[g]['hoff'])
                if common:
                    h = min(common)
                    return (0, abs(info[f]['hoff'][h] - info[g]['hoff'][h]), g)
                return (1, abs(info[f]['addr'] - info[g]['addr']), g)
            found, src = sorted(c, key=dist), 'same C function or ROM table'
        elif not info[f]['base'].startswith('gUnknown'):
            c = [g for g in by_stem.get(stem(info[f]['base']), []) if g != f and info[g]['final'] in want]
            if c: found, src = sorted(c, key=lambda g: abs(info[f]['addr'] - info[g]['addr'])), 'same name stem'
        if not found and info[f]['s']:
            seq = order[info[f]['s']]
            i = seq.index(f)
            near = [g for g in seq[max(0, i-4):i+5] if g != f and g in info and info[g]['final'] in want]
            if near: found, src = near, 'neighbours in ' + info[f]['s']
        r['partners'] = ';'.join(found[:16]); r['partner_source'] = src

    out = R(args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cols = ['file', 'final_type', 'confidence', 'tilemap_format', 'content_type', 'content_detail', 'usage_type',
            'name_type', 'compressed', 'size', 'data_size', 'label', 'rom_addr', 's_file',
            'callers', 'rom_ptr_refs', 'ref_by', 'partners', 'partner_source', 'notes']
    with open(out, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, cols); w.writeheader(); w.writerows(rows)
    tc = Counter(r['final_type'] for r in rows)
    cc = Counter(r['confidence'] for r in rows)
    print('wrote', out, len(rows), 'rows')
    print('types:', dict(tc.most_common()))
    print('confidence:', dict(cc))

if __name__ == '__main__':
    main()
