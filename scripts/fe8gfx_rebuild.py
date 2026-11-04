#!/usr/bin/env python3
"""
fe8gfx_rebuild.py - turn binary graphics into editable sources that rebuild
to the exact original bytes, and check that they do.

  extract  [--types reports/all_types.csv] [--facts reports/gfx_code_facts.json]
           [--out rebuild] [--only SUBSTR]
      For every graphic file listed in the classification CSV, write:
        <stem>.png          4bpp tiles as an indexed PNG (gbagfx source)
        <stem>.pal          palette as JASC .pal (gbagfx source)
        <stem>.screen.png   tilemap drawn as a picture: pixel index =
                            stored palette bank * 16 + colour
        <stem>.screen.json  what build-tsa needs besides the picture:
                            format, the tile sheet PNG(s) and their tile
                            offsets, and per-cell overrides
      then rebuilds each one with gbagfx / build-tsa and compares with the
      original. Results go to <out>/rebuild_report.csv, Make rules to
      <out>/rules.mk.

  build-tsa <screen.json> <out.bin> [--root .]
      Build a tilemap from <stem>.screen.png + the tile sheet PNGs named in
      the JSON (used by the Make rules).

Where the image, palette and starting tile of a tilemap come from, in order:
the C code (reports/gfx_code_facts.json from gfx_code_facts.py), else a
search over the partner files from the classification CSV that keeps the
combination whose tiles join best at their edges.
"""
import argparse, csv, json, os, re, shutil, struct, subprocess, sys, tempfile
from collections import Counter, defaultdict
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classify_dump import lz77_decompress

GBAGFX = 'tools/gbagfx/gbagfx'
KNOWN_EXT = ('.4bpp', '.gbapal', '.agbpal', '.bin', '.tsa', '.lz', '.fk', '.feimg1', '.feimg2',
             '.feimg3', '.feimg4', '.fetsa1', '.fetsa2', '.fetsa3', '.fetsa4', '.gbapal', '.1bpp', '.8bpp')

# ------------------------------------------------------------------ io -----
def read_item(repo, f):
    raw = open(os.path.join(repo, f), 'rb').read()
    if f.endswith('.fk') and len(raw) >= 4:
        return raw, raw[4:], 'fk'
    d = lz77_decompress(raw)
    if d and len(raw) - d[1] <= 3:
        return raw, d[0], 'lz'
    if d and d[1] >= len(raw) // 2:
        # a compressed stream followed by unrelated bytes (an unsplit neighbour)
        cut = (d[1] + 3) & ~3
        tail_of[f] = raw[cut:]
        return raw[:cut], d[0], 'lz'
    return raw, raw, ''

tail_of = {}

def stem_of(f):
    d, b = os.path.split(f)
    return os.path.join(d, b.split('.')[0])

def palette_banks(data):
    v = np.frombuffer(data[:len(data) // 2 * 2], '<u2').astype(np.int32)
    v = np.concatenate([v, np.zeros(-len(v) % 16, np.int32)])
    rgb = np.stack([(v & 31), (v >> 5) & 31, (v >> 10) & 31], -1)
    return ((rgb << 3) | (rgb >> 2)).reshape(-1, 16, 3).astype(np.uint8)

GREY = np.repeat((np.arange(16) * 17).astype(np.uint8)[:, None], 3, 1)[None]

def tiles_of(gfx):
    n = len(gfx) // 32
    b = np.frombuffer(gfx[:n * 32], np.uint8).reshape(n, 8, 4)
    t = np.empty((n, 8, 8), np.uint8)
    t[:, :, 0::2] = b & 15
    t[:, :, 1::2] = b >> 4
    return t

def luma(rgb):
    return rgb.astype(np.float32) @ np.array([0.3, 0.59, 0.11], np.float32)

# ---------------------------------------------------------- seam scores ----
def seam_cost(L, busy, h, w):
    parts = []
    if w > 1:
        a, b = L[:, 7:-1:8], L[:, 8::8]
        m = np.repeat(busy[:, :-1] & busy[:, 1:], 8, 0)
        if m.sum() > 16: parts.append(np.abs(a - b)[m].mean())
    if h > 1:
        a, b = L[7:-1:8, :], L[8::8, :]
        m = np.repeat(busy[:-1, :] & busy[1:, :], 8, 1)
        if m.sum() > 16: parts.append(np.abs(a - b)[m].mean())
    return sum(parts) / len(parts) if parts else 1e9

def arrange(T, w):
    n = len(T); h = (n + w - 1) // w
    A = np.concatenate([T, np.zeros((h * w - n, 8, 8), np.uint8)]).reshape(h, w, 8, 8)
    return A.transpose(0, 2, 1, 3).reshape(h * 8, w * 8), h

WIDTHS = [4, 5, 6, 8, 10, 12, 15, 16, 20, 24, 30, 32]
def best_width(T, lum):
    n = len(T)
    if n < 8:
        return max(1, n)
    flat = T.reshape(n, -1).min(1) == T.reshape(n, -1).max(1)
    sc = {}
    for w in WIDTHS:
        if w > n or (n + w - 1) // w < 2: continue
        img, h = arrange(T, w)
        busy = np.concatenate([~flat, np.zeros(h * w - n, bool)]).reshape(h, w)
        sc[w] = seam_cost(lum[img], busy, h, w)
    if not sc:
        return min(32, n)
    best = min(sc, key=sc.get)
    for w in (32, 16):
        if w in sc and sc[w] <= sc[best] * 1.03:
            return w
    return best

# ------------------------------------------------------------ tilemaps -----
def tilemap_entries(data, fmt, width=None):
    """-> (entries HxW top-down, trailing bytes)"""
    if fmt == 'fe_tsa':
        w, h = data[0] + 1, data[1] + 1
        n = w * h * 2
        e = np.frombuffer(data[2:2 + n], '<u2').reshape(h, w)[::-1].astype(np.int32)
        return e, data[2 + n:]
    n = len(data) // 2
    if not width:
        width = 32 if n % 32 == 0 else (30 if n % 30 == 0 else 32)
    h = n // width
    e = np.frombuffer(data[:h * width * 2], '<u2').reshape(h, width).astype(np.int32)
    return e, data[h * width * 2:]

def bg_reachable(ctx, L):
    """can the map of this draw use the image of this load? An image loaded relative to
    BG n's character base only serves BG n; an absolute one (default BG config: BG0-2 at 0,
    BG3 at 0x8000) only the BGs whose 1024 tiles reach it"""
    bg, lb = ctx.get('bg'), L.get('bg')
    if L.get('space', 'bg') != 'bg':
        return False                  # OBJ tiles are never BG tiles
    if bg is None:
        return True
    if isinstance(lb, int):
        return lb == bg
    if lb == 'abs' and ctx.get('default_bg_cfg'):
        return (L['tile'] >= 1024) == (bg == 3)
    return True


def mirror_entries(E):
    """Picture as the game shows it when the map is copied with EfxTmCpy*HFlip."""
    return E[:, ::-1] ^ 0x400

def entries_bytes(E, fmt, trailing):
    h, w = E.shape
    if fmt == 'fe_tsa':
        return bytes([w - 1, h - 1]) + E[::-1].astype('<u2').tobytes() + trailing
    return E.astype('<u2').tobytes() + trailing

def draw_screen(E, layers, bank_colors):
    """E: stored entries; layers: [(tiles, offset)] stored tile = idx + offset.
    Returns indexed image (index = stored bank*16 + colour)."""
    h, w = E.shape
    img = np.zeros((h * 8, w * 8), np.uint8)
    for y in range(h):
        for x in range(w):
            e = int(E[y, x]); t = e & 0x3FF; bank = e >> 12
            tile = None
            for T, off in layers:
                if 0 <= t - off < len(T):
                    tile = T[t - off]; break
            if tile is None:
                tile = np.zeros((8, 8), np.uint8)
            if e & 0x400: tile = tile[:, ::-1]
            if e & 0x800: tile = tile[::-1, :]
            img[y * 8:y * 8 + 8, x * 8:x * 8 + 8] = tile + bank * 16
    return img

def build_entries(screen, layers, prefer=(), blank_tile=None, prefer_flip=0):
    """Inverse of draw_screen without overrides: canonical entry per cell.
    Among identical tiles the lowest number wins, unless one is in `prefer`."""
    h, w = screen.shape[0] // 8, screen.shape[1] // 8
    prefer = set(prefer)
    lookup = {}
    for T, off in layers:
        for i, tile in enumerate(T):
            for (hf, vf) in ((0, 0), (1, 0), (0, 1), (1, 1)):
                p = tile
                if hf: p = p[:, ::-1]
                if vf: p = p[::-1, :]
                key = p.tobytes()
                cand = (i + off, (hf | vf << 1) != prefer_flip, hf, vf)
                rank = lambda c: (c[0] not in prefer, c[1], c[0], c[2] + c[3])
                if key not in lookup or rank(cand) < rank(lookup[key]):
                    lookup[key] = cand
    E = np.zeros((h, w), np.int32)
    for y in range(h):
        for x in range(w):
            cell = screen[y * 8:y * 8 + 8, x * 8:x * 8 + 8]
            bank = int(cell.max() >> 4)
            if blank_tile is not None and not (cell & 15).any():
                E[y, x] = blank_tile | (bank << 12)
                continue
            m = lookup.get((cell & 15).astype(np.uint8).tobytes())
            if m:
                E[y, x] = (m[0] & 0x3FF) | (m[2] << 10) | (m[3] << 11) | (bank << 12)
            else:
                E[y, x] = bank << 12
    return E

def load_png_tiles(path):
    im = Image.open(path)
    a = np.array(im)
    if im.mode == 'L':
        a = 15 - a // 17          # greyscale PNG: gbagfx reads colour = 15 - grey/17
    h, w = a.shape[0] // 8, a.shape[1] // 8
    return a.reshape(h, 8, w, 8).transpose(0, 2, 1, 3).reshape(-1, 8, 8) & 15

def build_tsa(spec_path, root):
    spec = json.load(open(spec_path))
    screen = np.array(Image.open(os.path.join(root, spec['screen'])))
    layers = []
    for L in spec['layers']:
        if 'bin' in L:
            # a built binary (e.g. a .feimg4.bin made from a full picture by tsa_generator)
            cands = [os.path.join(root, L['bin']), L['bin']]
            p = next((c for c in cands if os.path.exists(c)), None)
            if p:
                T = tiles_of(open(p, 'rb').read())
            else:
                p = next(c + '.lz' for c in cands if os.path.exists(c + '.lz'))
                T = tiles_of(lz77_decompress(open(p, 'rb').read())[0])
            if L.get('num_tiles'): T = T[:L['num_tiles']]
            layers.append((T, L['offset']))
            continue
        T = load_png_tiles(os.path.join(root, L['png']))
        if L.get('num_tiles'): T = T[:L['num_tiles']]
        layers.append((T, L['offset']))
    E = build_entries(screen, layers, spec.get('prefer_tiles', []), spec.get('blank_tile'), spec.get('prefer_flip', 0))
    for k, v in spec.get('overrides', {}).items():
        x, y = map(int, k.split(','))
        E[y, x] = int(v, 16)
    if spec.get('mirror'):
        E = mirror_entries(E)
    return entries_bytes(E, spec['format'], bytes.fromhex(spec.get('trailing', '')))

# ------------------------------------------------------------- gbagfx ------
class Gfx:
    def __init__(self, repo):
        self.exe = os.path.join(repo, GBAGFX)
        if os.name == 'nt' and not os.path.exists(self.exe + '.exe'):
            sys.exit('tools/gbagfx/gbagfx is a Linux program: run this script from WSL '
                     '(cd ~/fireemblem8u && python3 scripts/...), not from Windows Python.')
        if os.name == 'nt':
            self.exe += '.exe'
        if not os.path.exists(self.exe):
            sys.exit('%s not found: build the tools first (./build_tools.sh or make -C tools/gbagfx)' % self.exe)
        self.tmp = tempfile.mkdtemp()
    def run(self, src, dst, *opts):
        r = subprocess.run([self.exe, src, dst, *map(str, opts)], capture_output=True, text=True)
        return r.returncode == 0
    def lz(self, data):
        p = os.path.join(self.tmp, 'x.bin')
        open(p, 'wb').write(data)
        return open(p + '.lz', 'rb').read() if self.run(p, p + '.lz') else None
    def png_to_4bpp(self, png, n):
        p = os.path.join(self.tmp, 'x.4bpp')
        if not self.run(png, p, '-num_tiles', n): return None
        return open(p, 'rb').read()
    def pal_to_gbapal(self, pal):
        p = os.path.join(self.tmp, 'x.gbapal')
        if not self.run(pal, p): return None
        return open(p, 'rb').read()

PAL_EXPAND = {
    'round': lambda c: np.floor(c * 255 / 31 + 0.5).astype(int),   # most .pal files in the repo
    'floor': lambda c: (c * 255) // 31,                             # graphics/op_anim
    'shift': lambda c: (c << 3) | (c >> 2),
    'x8':    lambda c: c << 3,
}

def pal_text(data, expand='round'):
    v = np.frombuffer(data[:len(data) // 2 * 2], '<u2').astype(np.int32)
    c5 = np.stack([(v & 31), (v >> 5) & 31, (v >> 10) & 31], -1)
    rows = PAL_EXPAND[expand](c5)
    return 'JASC-PAL\r\n0100\r\n%d\r\n' % len(rows) + ''.join('%d %d %d\r\n' % tuple(x) for x in rows)

def write_pal(path, data, expand='round'):
    open(path, 'w', newline='').write(pal_text(data, expand))

def _old_write_pal(path, data):
    v = np.frombuffer(data[:len(data) // 2 * 2], '<u2').astype(np.int32)
    c5 = np.stack([(v & 31), (v >> 5) & 31, (v >> 10) & 31], -1)
    banks = np.floor(c5 * 255 / 31 + 0.5).astype(int)
    with open(path, 'w', newline='') as f:
        f.write('JASC-PAL\r\n0100\r\n%d\r\n' % len(banks))
        for r, g, b in banks:
            f.write('%d %d %d\r\n' % (r, g, b))

def save_png(path, idx, colors):
    im = Image.fromarray(idx.astype(np.uint8), 'P')
    flat = colors.reshape(-1).tolist()
    im.putpalette(flat + [0] * (768 - len(flat)))
    im.save(path, bits=4 if idx.max() < 16 and len(flat) <= 48 else 8)

# ------------------------------------------------------------- extract -----
def extract(a):
    repo, outdir = a.repo, os.path.join(a.repo, a.out)
    rows = list(csv.DictReader(open(os.path.join(repo, a.types), encoding='utf-8')))
    facts = json.load(open(os.path.join(repo, a.facts))) if os.path.exists(os.path.join(repo, a.facts)) else {}
    by = {r['file']: r for r in rows}
    by_label = {}
    for r in rows:
        if r['label']: by_label.setdefault(r['label'], r['file'])
        by_label.setdefault(os.path.basename(r['file']).split('.')[0], r['file'])
    gfx = Gfx(repo)
    cache = {}
    def item(f):
        if f not in cache: cache[f] = read_item(repo, f)
        return cache[f]
    def partners(r, t):
        return [p for p in r['partners'].split(';') if p and by.get(p, {}).get('final_type') == t]
    def facts_for(f):
        r = by[f]
        return facts.get(r['label']) or facts.get(os.path.basename(f).split('.')[0]) or {}

    # palettes loaded by the same function that loads an image (lowest bank first,
    # BG banks for BG images, OBJ banks for OBJ images)
    func_pals = defaultdict(list)
    for lbl, v in facts.items():
        for pe in v.get('palettes', []):
            func_pals[(pe['file'], pe['func'])].append((pe['bank'], lbl))
    def code_palettes(f):
        res = []
        for ld in facts_for(f).get('loads', []):
            space_obj = ld['space'] == 'obj'
            for bank, lbl in sorted(func_pals.get((ld['file'], ld['func']), [])):
                if (bank >= 16) == space_obj:
                    pf = by_label.get(lbl)
                    if pf and by.get(pf, {}).get('final_type') == 'palette' and pf not in res:
                        res.append(pf)
        return res

    tm_by_holder, tm_by_stem = defaultdict(list), defaultdict(list)
    for r0 in rows:
        if r0['final_type'] == 'tilemap':
            for h in r0['ref_by'].split(';'):
                if h: tm_by_holder[h.split('+')[0]].append(r0['file'])
            tm_by_stem[re.sub(r'\d+$', '', os.path.basename(r0['file']).split('.')[0])].append(r0['file'])
    def siblings(f):
        r0 = by[f]
        res = []
        for h in r0['ref_by'].split(';'):
            if h: res += tm_by_holder.get(h.split('+')[0], [])
        res += tm_by_stem.get(re.sub(r'\d+$', '', os.path.basename(f).split('.')[0]), [])
        return [x for x in dict.fromkeys(res) if x != f]

    gfx_of_pal = defaultdict(list)
    for r0 in rows:
        if r0['final_type'] == 'gfx4bpp':
            for p0 in r0['partners'].split(';'):
                if by.get(p0, {}).get('final_type') == 'palette':
                    gfx_of_pal[p0].append(r0['file'])
    gfx_by_stem = defaultdict(list)
    for r0 in rows:
        if r0['final_type'] == 'gfx4bpp':
            gfx_by_stem[stem_of(r0['file'])].append(r0['file'])
    pal_by_stem, pal_by_dir = defaultdict(list), defaultdict(list)
    for r0 in rows:
        if r0['final_type'] == 'palette':
            pal_by_stem[stem_of(r0['file'])].append(r0['file'])
            pal_by_dir[os.path.dirname(r0['file'])].append(r0['file'])
    def same_stem_palettes(f):
        st = stem_of(f)
        res = list(pal_by_stem.get(st, []))
        # foo_sheet.4bpp -> foo.gbapal, portrait_X_mug -> portrait_X_palette ...
        d, b = os.path.split(st)
        for cand_stem, fs in pal_by_stem.items():
            cd, cb = os.path.split(cand_stem)
            if cd == d and cand_stem != st and (b.startswith(cb) or cb.startswith(b)) and min(len(b), len(cb)) >= 6:
                res += fs
        return res
    DUMP_DIRS = {'graphics/' + c for c in (
        'mapanim', 'efxdragon', 'world_map', 'efxbattle', 'sysutils', 'classchg', 'map_fx',
        'link_arena', 'lvup', 'prep_screen', 'main_menu', 'cg', 'event', 'op_anim',
        'player_interface', 'ending', 'chap_title', 'efxmagic', 'statscreen', 'misc',
        'op_subtitle', 'world_map/nations')}
    def dir_palettes(f):
        d = os.path.dirname(f)
        # dumping_file/ was a flat mix of everything; its entries now sit in these graphics/
        # dirs (notes/scripts/move_dump.py), which are just as mixed
        if d == 'dumping_file' or d in DUMP_DIRS:
            return []
        fs = pal_by_dir.get(d, [])
        return fs if len(fs) == 1 else []

    # gfx files near a given file in the same .s (fallback partners)
    by_s = defaultdict(list)
    for r0 in rows:
        if r0['s_file'] and r0['final_type'] == 'gfx4bpp':
            by_s[r0['s_file']].append(r0)
    def nearby_gfx(r, n=10):
        try:
            a0 = int(r['rom_addr'], 16)
        except ValueError:
            return []
        c = [x for x in by_s.get(r['s_file'], []) if x['rom_addr']]
        c.sort(key=lambda x: abs(int(x['rom_addr'], 16) - a0))
        return [x['file'] for x in c[:n]]

    report, rules = [], []
    def out_path(f, suffix):
        p = os.path.join(outdir, stem_of(f) + suffix)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        return p
    def rel(p):
        return os.path.relpath(p, outdir)

    # ---- palettes ------------------------------------------------------
    pal_cache = {}
    def pal_colors(f):
        if f not in pal_cache:
            pal_cache[f] = palette_banks(item(f)[1])
        return pal_cache[f]

    def lz_status(f, raw, data, comp):
        if comp == 'lz':
            c = gfx.lz(data)
            ok = c is not None and (c == raw or (raw[:len(c)] == c and not any(raw[len(c):])))
            return 'ok' if ok else 'MISMATCH'
        return ''

    gfx_png = {}       # gfx file -> (png path rel to out, num tiles, colors)
    todo = [r for r in rows if not a.only or re.search(a.only, r['file'])]
    # palettes first, then gfx (tilemaps need the gfx PNGs)
    order = {'palette': 0, 'gfx4bpp': 1, 'tilemap': 2}
    todo.sort(key=lambda r: order.get(r['final_type'], 3))
    for r in todo:
        f, t = r['file'], r['final_type']
        if t not in order:
            report.append(dict(file=f, type=t, status='not graphics: kept as binary'))
            continue
        try:
            raw, data, comp = item(f)
            lzs = lz_status(f, raw, data, comp)
            rec = dict(file=f, type=t, compression=comp, lz_rebuild=lzs)
            # ---------------- palette
            if t == 'palette':
                v = np.frombuffer(data[:len(data) // 2 * 2], '<u2')
                target = f[:-3] if comp == 'lz' else f
                if len(data) % 2 or (v & 0x8000).any():
                    rec.update(status='keep binary', note='odd size or colour with bit 15 set')
                elif len(v) <= 256:
                    p = out_path(f, '.pal')
                    write_pal(p, data)
                    ok = gfx.pal_to_gbapal(p) == data
                    rec.update(status='exact' if ok else 'MISMATCH', source=rel(p))
                    if ok and not target.endswith('.gbapal'):
                        rules.append('%s: %s\n\t$(GBAGFX) $< $@.gbapal && mv $@.gbapal $@\n' % (target, stem_of(f) + '.pal'))
                else:
                    # JASC .pal holds at most 256 colours: split, convert each, concatenate
                    parts, back = [], b''
                    for i in range(0, len(data), 512):
                        p = out_path(f, '.part%d.pal' % (i // 512))
                        write_pal(p, data[i:i + 512])
                        back += gfx.pal_to_gbapal(p) or b''
                        parts.append(stem_of(f) + '.part%d.pal' % (i // 512))
                    ok = back == data
                    rec.update(status='exact' if ok else 'MISMATCH', source=';'.join(parts), note='%d colours, split in %d .pal' % (len(v), len(parts)))
                    if ok:
                        rules.append('%s: %s\n\tfor p in $^; do $(GBAGFX) $$p $$p.gbapal || exit 1; done; cat $(addsuffix .gbapal,$^) > $@; rm -f $(addsuffix .gbapal,$^)\n' % (target, ' '.join(parts)))
            # ---------------- 4bpp tiles
            elif t == 'gfx4bpp':
                T = tiles_of(data)
                if not len(T):
                    report.append(dict(rec, status='keep binary', note='no whole tile')); continue
                # palette: code (bank used by the draws / loaded in the same function), then partners
                colors, psrc = None, ''
                pals = same_stem_palettes(f) + code_palettes(f) + [p for p in partners(r, 'palette')] + dir_palettes(f)
                if pals:
                    colors, psrc = pal_colors(pals[0])[0], pals[0]
                else:
                    colors, psrc = GREY[0], 'GREYSCALE'
                existing = os.path.join(repo, stem_of(f) + '.png')
                w_guess = best_width(T, luma(colors))
                w = w_guess
                if os.path.exists(existing):
                    try:
                        ew = Image.open(existing).size[0] // 8
                        if ew: w = ew
                    except Exception:
                        pass
                img, _ = arrange(T, w)
                p = out_path(f, '.png')
                save_png(p, img, colors)
                gfx_png[f] = (rel(p), len(T), colors)
                back = gfx.png_to_4bpp(p, len(T))
                trailing = data[len(T) * 32:]
                if back == data:
                    rec.update(status='exact', source=rel(p))
                elif back == data[:len(T) * 32]:
                    rec.update(status='keep binary', source=rel(p), note='%d bytes after the last tile' % len(trailing))
                else:
                    rec.update(status='MISMATCH', source=rel(p))
                rec.update(width_tiles=w, width_guess=w_guess, tiles=len(T), palette=psrc)
                if os.path.exists(existing):
                    eim = Image.open(existing); e = np.array(eim)
                    if eim.mode == 'L': e = 15 - e // 17
                    if '.feimg' in f: rec['existing_png'] = 'n/a: full picture (tsa_generator)'
                    else: rec['existing_png'] = 'same pixels' if e.shape == img.shape and ((e & 15) == img).all() else \
                        ('same tiles, other layout' if sorted(map(bytes, load_png_tiles(existing)[:len(T)])) == sorted(map(bytes, T)) else 'different')
                    if '.feimg' not in f: rec['width_guess_ok'] = int(w_guess == w)
                if rec['status'] == 'exact':
                    target = f[:-3] if comp == 'lz' else (f[:-3] if comp == 'fk' else f)
                    padded = (len(T) % w) != 0
                    if not target.endswith('.4bpp'):
                        rules.append('%s: %s\n\t$(GBAGFX) $< $@.4bpp -num_tiles %d && mv $@.4bpp $@\n' % (target, stem_of(f) + '.png', len(T)))
                    elif padded:
                        rules.append('%s: %s\n\t$(GBAGFX) $< $@ -num_tiles %d\n' % (target, stem_of(f) + '.png', len(T)))
            # ---------------- tilemaps
            elif t == 'tilemap':
                fmt = r['tilemap_format'] or ('fe_tsa' if data[:1] and len(data) >= 2 + (data[0] + 1) * (data[1] + 1) * 2 else 'raw')
                if fmt == 'raw_screen': fmt = 'raw'
                fx = facts_for(f)
                ctxs = [d for d in fx.get('draws', []) if d.get('add') is not None and d['layers']]
                borrowed = ''
                fe_pair = '.fetsa' in f and bool(gfx_by_stem.get(stem_of(f)))
                if fe_pair:
                    ctxs = []          # X.fetsaN always goes with X.feimgN (one picture in the repo)
                if not ctxs and not fe_pair:
                    # never drawn directly (reached through a table): borrow how a sibling
                    # in the same table, or with the same name apart from a number, is drawn
                    for sib in siblings(f):
                        sc_ = [d for d in facts_for(sib).get('draws', []) if d.get('add') is not None and d['layers']]
                        if sc_:
                            ctxs, borrowed = sc_, os.path.basename(sib).split('.')[0]
                            break
                width = next((d.get('width') for d in ctxs if d.get('width')), None)
                E, trailing = tilemap_entries(data, fmt, width)
                if E.size == 0:
                    report.append(dict(rec, status='keep binary', note='empty tilemap')); continue
                layers, bank_colors, how = [], {}, ''
                mirror = False
                # every draw of this tilemap found in the code is a candidate; a BG reads
                # tiles from its own character base, so the offset is known modulo 512
                best = None
                idx = E & 0x3FF
                for ctx in ctxs:
                    add = ctx['add']
                    Lc = []
                    for L in ctx['layers']:
                        if not bg_reachable(ctx, L):
                            continue
                        g = by_label.get(L['label'])
                        if g and by.get(g, {}).get('final_type') == 'gfx4bpp' and (g, L['tile']) not in [(x, y + (add & 0x3FF)) for x, y in Lc]:
                            Lc.append((g, L['tile'] - (add & 0x3FF)))
                    if not Lc: continue
                    # all loaded images together, or each one alone (a file-level guess
                    # mixes images from unrelated screens)
                    sets = [Lc] + ([[x] for x in Lc] if len(Lc) > 1 else [])
                    for Ls0 in sets:
                        for k in range(0, 3):
                            L2 = [(g, off - 512 * k) for g, off in Ls0]
                            inside = np.zeros(E.shape, bool)
                            for g, off in L2:
                                n = len(item(g)[1]) // 32
                                inside |= (idx - off >= 0) & (idx - off < n)
                            cover = inside.mean()
                            if cover < 0.2: continue
                            TL = [(tiles_of(item(g)[1]), off) for g, off in L2]
                            nov = int((build_entries(draw_screen(E, TL, None), TL) != E).sum()) / E.size
                            aligned = any(off % 512 == 0 for _, off in L2)
                            sc = (1 - cover) * 100 + nov * 100 + (0 if aligned else 3) + len(L2) * 0.5
                            if best is None or sc < best[0]:
                                best = (sc, L2, ctx, 512 * k)
                if best:
                    sc, layers, ctx, shift = best
                    add = ctx['add']
                    for b_, pl in ctx['pals'].items():
                        lbl, k = (pl, 0) if isinstance(pl, str) else (pl[0], pl[1])
                        pf = by_label.get(lbl)
                        if pf and by.get(pf, {}).get('final_type') == 'palette':
                            sb = int(b_) - (add >> 12)
                            cols = pal_colors(pf)
                            if 0 <= sb < 16 and k < len(cols):
                                bank_colors[sb] = (cols[k], pf, k)
                    how = 'code: %s() in %s' % (ctx['func'], ctx['file']) + (' (as %s)' % borrowed if borrowed else '')
                    if ctx.get('mirror'):
                        mirror = True
                        E = mirror_entries(E)
                if not layers:
                    # search over partners
                    gs = list(gfx_by_stem.get(stem_of(f), [])) + [g for g in partners(r, 'gfx4bpp')][:12]
                    # images that go with the palettes this screen uses (e.g. UI frame tiles)
                    ctx_pals = [by_label.get(pl if isinstance(pl, str) else pl[0]) for d0 in fx.get('draws', []) for pl in d0.get('pals', {}).values()]
                    for pf0 in [p0 for p0 in ctx_pals if p0] + partners(r, 'palette'):
                        gs += gfx_of_pal.get(pf0, [])[:4]
                    gs = list(dict.fromkeys(gs)) or nearby_gfx(r)
                    if fe_pair:
                        gs = list(gfx_by_stem[stem_of(f)])   # the repo builds X.feimgN/X.fetsaN from one picture
                    pals = partners(r, 'palette')
                    for g in gs:
                        if pals: break
                        pals = code_palettes(g) or partners(by[g], 'palette')
                    idx = E & 0x3FF; used = idx[idx > 0]
                    mn = int(used.min()) if used.size else 0
                    offs = sorted({0, mn, mn & ~0x1F, mn & ~0x7F, mn & ~0xFF, max(0, mn - 1)})
                    if fe_pair:
                        offs = [0]          # tsa_generator numbers the tiles of the picture from 0
                    cands = []                      # list of layer lists [(gfx, offset)]
                    for g in gs:
                        for off in offs:
                            cands.append([(g, off)])
                    # images split in numbered parts loaded one after the other
                    parts = sorted((g for st, fs in gfx_by_stem.items() for g in fs
                                    if re.match(re.escape(stem_of(f)) + r'_(part_)?\d+$', st)),
                                   key=lambda g: int(re.search(r'(\d+)$', stem_of(g)).group(1)))
                    if len(parts) >= 2:
                        o, L = 0, []
                        for g in parts:
                            L.append((g, o)); o += len(item(g)[1]) // 32
                        cands.append(L)
                    same = set(gfx_by_stem.get(stem_of(f), []))
                    best = None
                    for L in cands:
                        TL = [(tiles_of(item(g)[1]), off) for g, off in L]
                        if not any(len(T) for T, _ in TL): continue
                        inside = np.zeros(E.shape, bool)
                        for T, off in TL:
                            inside |= (idx - off >= 0) & (idx - off < len(T))
                        cover = inside.mean()
                        if cover < 0.5 and not (len(L) == 1 and L[0][0] in same): continue
                        scr = draw_screen(E, TL, None)
                        hh, ww = E.shape
                        G = scr.reshape(hh, 8, ww, 8).transpose(0, 2, 1, 3).reshape(hh, ww, -1) & 15
                        busy = G.min(-1) != G.max(-1)
                        nov = int((build_entries(scr, TL) != E).sum())
                        for pf in (pals[:3] or [None]):
                            cols = pal_colors(pf) if pf else GREY
                            for pb in sorted({0, int((E >> 12).min())}):
                                bank = ((scr >> 4).astype(int) - pb) % len(cols)
                                rgb = cols[bank, scr & 15]
                                c = seam_cost(luma(rgb), busy, hh, ww) * 0.5 + 100.0 * nov / E.size
                                if best is None or c < best[0]:
                                    best = (c, L, pf, pb)
                    if best:
                        c, L, pf, pb = best
                        layers = L
                        if pf:
                            cols = pal_colors(pf)
                            for sb in range(16):
                                bank_colors[sb] = (cols[(sb - pb) % len(cols)], pf, (sb - pb) % len(cols))
                        how = 'search (score %.1f)' % c
                if not layers:
                    report.append(dict(rec, status='keep binary', note='no tile sheet found for it')); continue
                Ls = []
                for g, off in layers:
                    if g not in gfx_png:
                        # gfx outside the processed set (e.g. --only): render it now
                        T = tiles_of(item(g)[1]); w = best_width(T, luma(GREY[0]))
                        img, _ = arrange(T, w)
                        p = out_path(g, '.png'); save_png(p, img, GREY[0])
                        gfx_png[g] = (rel(p), len(T), GREY[0])
                    Ls.append((load_png_tiles(os.path.join(outdir, gfx_png[g][0]))[:gfx_png[g][1]], off))
                scr = draw_screen(E, Ls, None)
                pal = np.zeros((16, 16, 3), np.uint8)
                for sb in range(16):
                    pal[sb] = bank_colors[sb][0] if sb in bank_colors else GREY[0]
                p = out_path(f, '.screen.png')
                Image.fromarray(scr, 'P').save(p) if False else None
                im = Image.fromarray(scr, 'P'); im.putpalette(pal.reshape(-1).tolist()); im.save(p)
                # among identical tiles, prefer the numbers the original uses most
                groups = defaultdict(Counter)
                for T, off in Ls:
                    for i, tile in enumerate(T):
                        groups[tile.tobytes()]  # register
                used = Counter(int(x) & 0x3FF for x in E.reshape(-1))
                prefer = []
                seen = defaultdict(list)
                for T, off in Ls:
                    for i, tile in enumerate(T):
                        seen[tile.tobytes()].append(i + off)
                for nums in seen.values():
                    if len(nums) > 1:
                        best = max(nums, key=lambda n: (used[n], -n))
                        if used[best] and best != min(nums):
                            prefer.append(best)
                # the flip the original favours, and the entry it uses for empty cells; all
                # four flips are tried (the most common one over the whole map can be the
                # filler rows', e.g. Tsa_08755610: mirrored picture above 12 rows of tile 1023)
                hh, ww = E.shape
                G = scr.reshape(hh, 8, ww, 8).transpose(0, 2, 1, 3).reshape(hh, ww, -1) & 15
                empty = ~G.any(-1)
                bts = [None]
                if empty.any():
                    bts.append(Counter(int(e) & 0xFFF for e in E[empty]).most_common(1)[0][0])
                best_n = None
                for pf_ in (0, 1, 2, 3):
                    for bt in bts:
                        n_ = int((build_entries(scr, Ls, prefer, bt, pf_) != E).sum())
                        if best_n is None or n_ < best_n:
                            best_n, prefer_flip, blank_tile = n_, pf_, bt
                rebuilt = build_entries(scr, Ls, prefer, blank_tile, prefer_flip)
                diff = np.argwhere(rebuilt != E)
                overrides = {'%d,%d' % (x, y): '%04X' % int(E[y, x]) for y, x in diff}
                spec = dict(screen=rel(p), format=fmt,
                            layers=[dict(png=gfx_png[g][0], offset=int(off), num_tiles=gfx_png[g][1]) for g, off in layers],
                            mirror=mirror, prefer_tiles=sorted(prefer), prefer_flip=prefer_flip, blank_tile=blank_tile, overrides=overrides, trailing=trailing.hex(), source=how,
                            palettes=sorted({v[1] for v in bank_colors.values()}),
                            banks={str(sb): [v[1], int(v[2])] for sb, v in sorted(bank_colors.items())})
                sp = out_path(f, '.screen.json')
                json.dump(spec, open(sp, 'w'), indent=1)
                back = build_tsa(sp, outdir)
                cells = E.size
                rec.update(source=rel(p), layers=';'.join(g for g, _ in layers), how=how,
                           overrides=len(overrides), cells=cells,
                           palette=';'.join(spec['palettes']) or 'GREYSCALE')
                if back != data:
                    rec['status'] = 'MISMATCH'
                else:
                    rec['status'] = 'exact' if len(overrides) <= max(2, cells // 50) else 'exact, many overrides'
                if rec['status'].startswith('exact'):
                    target = f[:-3] if comp == 'lz' else f
                    deps = ' '.join(sorted({stem_of(g) + '.png' for g, _ in layers}))
                    rules.append('%s: %s %s %s\n\t$(PYTHON) scripts/fe8gfx_rebuild.py build-tsa %s $@\n' % (
                        target, stem_of(f) + '.screen.png', stem_of(f) + '.screen.json', deps, stem_of(f) + '.screen.json'))
            if f in tail_of and rec.get('status', '').startswith('exact'):
                tp = out_path(f, '.tail.bin')
                open(tp, 'wb').write(tail_of[f])
                rec['note'] = (rec.get('note', '') + '; %d bytes after the compressed data saved as %s (probably the next item, not split yet)' % (len(tail_of[f]), stem_of(f) + '.tail.bin')).strip('; ')
                rules.append('# %s = compressed data + the bytes that follow it\n' % f)
            if lzs == 'MISMATCH':
                rec['status'] = rec.get('status', '') + '; keep original .lz (gbagfx compresses it differently)'
            report.append(rec)
        except Exception as e:
            report.append(dict(file=f, type=t, status='ERROR', note=repr(e)[:200]))

    cols = ['file', 'type', 'status', 'source', 'compression', 'lz_rebuild', 'tiles', 'width_tiles', 'width_guess',
            'palette', 'layers', 'how', 'overrides', 'cells', 'existing_png', 'width_guess_ok', 'note']
    tag = ('.' + a.tag) if a.tag else ''
    with open(os.path.join(outdir, 'rebuild_report%s.csv' % tag), 'w', newline='') as fh:
        w = csv.DictWriter(fh, cols, extrasaction='ignore'); w.writeheader(); w.writerows(report)
    with open(os.path.join(outdir, 'rules%s.mk' % tag), 'w') as fh:
        fh.write('# generated by fe8gfx_rebuild.py: rules the generic %.4bpp/%.gbapal/%.lz rules do not cover\n\n')
        fh.writelines(r + '\n' for r in rules)
    c = Counter((x['type'], x['status'].split(';')[0]) for x in report)
    for k, v in sorted(c.items()):
        print('%-10s %-28s %d' % (k[0], k[1], v))
    lzbad = sum(1 for x in report if x.get('lz_rebuild') == 'MISMATCH')
    print('lz not reproducible:', lzbad)

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('extract')
    p.add_argument('--repo', default='.')
    p.add_argument('--types', default='reports/all_types.csv')
    p.add_argument('--facts', default='reports/gfx_code_facts.json')
    p.add_argument('--out', default='rebuild')
    p.add_argument('--only', default='', help='regex on the file path')
    p.add_argument('--tag', default='', help='suffix for the report/rules names (to run in parts)')
    p = sub.add_parser('build-tsa')
    p.add_argument('spec'); p.add_argument('out'); p.add_argument('--root', default='.')
    a = ap.parse_args()
    if a.cmd == 'extract':
        extract(a)
    else:
        open(a.out, 'wb').write(build_tsa(a.spec, a.root))

if __name__ == '__main__':
    main()
