#!/usr/bin/env python3
"""
gfx_png.py - editable PNG/.pal sources for the binaries of graphic_extract.yml.

graphic_extract.yml stays the description of every extracted binary (address, size,
path, type). graphic_png.yml adds, per entry name, how a binary is turned into a
source. The sources are written to graphics_png/, mirroring graphics/:

    graphics/unsorted/X.4bpp.lz   <-  graphics_png/unsorted/X.png
    data/banim/Y.bin              <-  graphics_png/data/banim/Y.png

  sources  [--overwrite] [--only SUBSTR]
      Reads the two ymls and baserom.gba, writes the sources to graphics_png/ and
      the make rules to gfx_png_rules.mk. Existing sources are kept unless --overwrite.

  prune    [--kept-mk gfx_kept.mk]
      Deletes the extracted binaries that have a source in graphics_png/ (or that the
      repo's own makefiles build from a tracked source), so that make -f Makefile.png
      builds them again. --kept-mk lists the binaries used as extracted.

  verify   [--only SUBSTR]
      Rebuilds every source with gbagfx / build-tsa and compares with the ROM.

  extract  [--missing] PATH...
      Extracts these paths of graphic_extract.yml from baserom.gba (used by
      gfx_kept.mk after a `make clean`).

  highbits FILE MASK / lz --min-disp N IN OUT
      Used by the make rules (bit 15 of palette colours; LZ77 like the ROM).

graphic_png.yml fields (all optional):
  data_type    gfx4bpp | palette | tilemap | map_layout | banim_oam | ... | data
  compression  lz77 | fk | none (only when it differs from the extension)
  lz_exact     false when gbagfx's LZ77 output differs from the ROM (keep the binary)
  lz_min_disp  N: compressed with a greedy LZ77 that never copies from closer than N
  tail_size    bytes after the compressed stream (an unsplit neighbour)
  rebuild      binary (keep the file) | repo (built by the repo's Makefile from `source`)
  source       (rebuild: repo) the tracked file it is built from
  png:         (gfx4bpp) width, num_tiles, palette (entry name | greyscale), palette_row,
               palette_colors, pad, tile_banks + banks, output: none, picture
  pal:         (palette) parts, expand, high_bits
  screen:      (tilemap) format, width, mirror, layers, banks, bank_colors, prefer_tiles,
               prefer_flip, blank_tile, overrides, trailing, output, builder, method
"""
import argparse, json, os, re, subprocess, sys
from collections import Counter
import numpy as np
import yaml
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classify_dump import lz77_decompress
import fe8gfx_rebuild as RB

BASE_YML = 'graphic_extract.yml'
PNG_YML = 'graphic_png.yml'
SRC_ROOT = 'graphics_png'
RULES_MK = 'gfx_png_rules.mk'
LOADER = getattr(yaml, 'CSafeLoader', yaml.SafeLoader)


def path_of(e):
    """the binary the sources incbin"""
    return os.path.join(e['location'], e['file_name'] + '.' + e['type'])


def src_stem(e):
    """graphics_png/<location without graphics/>/<file_name>: where the sources go"""
    loc = e['location']
    if loc == 'graphics' or loc.startswith('graphics/'):
        loc = loc[len('graphics/'):]
    return os.path.join(SRC_ROOT, loc, e['file_name'])


DATA_TYPE_OF_EXT = {'4bpp': 'gfx4bpp', '4bpp.lz': 'gfx4bpp', '4bpp.fk': 'gfx4bpp',
                    'gbapal': 'palette', 'gbapal.lz': 'palette', 'agbpal': 'palette',
                    'agbpal.lz': 'palette', 'tsa': 'tilemap', 'tsa.lz': 'tilemap',
                    'o.bin.lz': 'banim_script'}


def default_fields(e):
    typ = e['type']
    d = {'compression': 'lz77' if typ.endswith('.lz') else 'fk' if typ.endswith('.fk') else 'none'}
    m = re.fullmatch(r'fe(img|tsa)\d+\.bin(\.lz)?', typ)
    dt = DATA_TYPE_OF_EXT.get(typ) or (m and ('gfx4bpp' if m.group(1) == 'img' else 'tilemap'))
    if dt:
        d['data_type'] = dt
    return d


def load(repo):
    """the entries of the base yml, each with the fields graphic_png.yml gives it"""
    base = yaml.load(open(os.path.join(repo, BASE_YML), encoding='utf-8'), Loader=LOADER)['files']
    extra = {}
    p = os.path.join(repo, PNG_YML)
    if os.path.exists(p):
        extra = {e['name']: e for e in yaml.load(open(p, encoding='utf-8'), Loader=LOADER)['files']}
    files = []
    for b in base:
        e = dict(b)
        e.setdefault('file_name', e['name'])
        for k, v in default_fields(e).items():
            e[k] = v
        e.update({k: v for k, v in extra.get(b['name'], {}).items() if k != 'name'})
        files.append(e)
    return files


def high_bits_cmd(e, f):
    """shell command (for a make rule) that sets bit 15 back in the built palette f"""
    hb = (e.get('pal') or {}).get('high_bits')
    return ' && $(PYTHON) scripts/gfx_png.py highbits %s %s' % (f, hb) if hb else ''


def apply_high_bits(data, mask):
    w = np.frombuffer(data, '<u2').copy()
    bits = np.unpackbits(np.frombuffer(bytes.fromhex(mask), np.uint8), bitorder='little')[:len(w)]
    w[:len(bits)] |= bits.astype(np.uint16) << 15
    return w.tobytes()


def lz77_encode(data, min_disp=1):
    """greedy GBA LZ77 (type 0x10): longest match, nearest first, distance >= min_disp"""
    out = bytearray([0x10, len(data) & 0xFF, (len(data) >> 8) & 0xFF, (len(data) >> 16) & 0xFF])
    i = 0
    while i < len(data):
        flag_pos = len(out)
        out.append(0)
        for bit in range(8):
            if i >= len(data):
                break
            best_len, best_disp = 0, 0
            for disp in range(min_disp, min(4096, i) + 1):
                j, n = i - disp, 0
                while n < 18 and i + n < len(data) and data[j + n] == data[i + n]:
                    n += 1
                if n > best_len:
                    best_len, best_disp = n, disp
                    if n == 18:
                        break
            if best_len >= 3:
                out[flag_pos] |= 0x80 >> bit
                v = ((best_len - 3) << 12) | (best_disp - 1)
                out += bytes([v >> 8, v & 0xFF])
                i += best_len
            else:
                out.append(data[i])
                i += 1
    out += bytes(-len(out) % 4)
    return bytes(out)


def built_path(e):
    """the uncompressed binary a source builds (the .lz is made from it)"""
    target = path_of(e)
    if e.get('compression') in ('lz77', 'fk') and target.endswith(('.lz', '.fk')):
        return target[:-3]
    return target


class Ctx:
    def __init__(self, a):
        self.a = a
        self.files = load(a.repo)
        self.by_name = {e['name']: e for e in self.files}
        self.rom = open(os.path.join(a.repo, 'baserom.gba'), 'rb').read()
        self.cache = {}
        self.dry = False

    def raw(self, e):
        a = int(e['address'], 16) - 0x08000000
        return self.rom[a:a + e['size']]

    def data(self, e):
        n = e['name']
        if n not in self.cache:
            raw = self.raw(e)
            c = e.get('compression', 'none')
            if c == 'fk':
                self.cache[n] = raw[4:]
            elif c == 'lz77':
                d = lz77_decompress(raw)
                self.cache[n] = d[0] if d else raw
            else:
                self.cache[n] = raw
        return self.cache[n]

    def colors(self, name, row=0):
        banks = RB.palette_banks(self.data(self.by_name[name]))
        return banks[row % len(banks)]

    def out(self, e, suffix):
        p = os.path.join(self.a.repo, src_stem(e) + suffix)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        return p


def hex_colors(s):
    return RB.palette_banks(np.array([int(x, 16) for x in s.split()], '<u2').tobytes())[0]


def png_colors(ctx, png):
    if png.get('palette_colors'):
        return hex_colors(png['palette_colors'])
    if png.get('palette') not in (None, 'greyscale') and png['palette'] in ctx.by_name:
        return ctx.colors(png['palette'], png.get('palette_row', 0))
    return RB.GREY[0]


def screen_spec(ctx, e):
    """(entries as drawn, layers [(tiles, offset)], spec dict for build-tsa)"""
    s = e['screen']
    E, trailing = RB.tilemap_entries(ctx.data(e), s['format'], s.get('width'))
    if s.get('mirror'):
        E = RB.mirror_entries(E)
    layers, Lspec = [], []
    for L in s['layers']:
        g = ctx.by_name.get(L['image'])
        if not g:
            continue
        T = RB.tiles_of(ctx.data(g))
        layers.append((T, L['offset']))
        if (g.get('png') or {}).get('output') == 'none':
            # tiles of a feimg: no sheet PNG, use the binary the repo builds from the full picture
            Lspec.append(dict(bin=built_path(g), offset=L['offset'], num_tiles=len(T)))
        else:
            Lspec.append(dict(png=src_stem(g) + '.png', offset=L['offset'], num_tiles=len(T)))
    ov = dict(item.split('=') for item in (s.get('overrides') or '').split())
    name = s.get('output', e['file_name'] + '.screen.png')
    pic = s.get('builder') == 'picture' and ctx.by_name.get(s['layers'][0]['image'])
    spec = dict(screen=src_stem(pic) + '.png' if pic else os.path.join(os.path.dirname(src_stem(e)), name),
                format=s['format'], mirror=bool(s.get('mirror')), layers=Lspec,
                prefer_tiles=s.get('prefer_tiles', []), prefer_flip=s.get('prefer_flip', 0),
                blank_tile=s.get('blank_tile'), overrides=ov, trailing=s.get('trailing', ''))
    return E, layers, spec


def needs_custom_pack(e):
    """compressed data the generic '%.lz: %' rule cannot produce: no .lz in the
    file name, or extra bytes after the compressed stream"""
    return e.get('compression') == 'lz77' and (not e['type'].endswith('.lz') or e.get('tail_size'))


def pack_rule(ctx, e, deps, make_raw):
    """rule for needs_custom_pack(): build the raw data, compress, add the tail"""
    tail = ''
    if e.get('tail_size'):
        if not ctx.dry:
            raw = ctx.raw(e)
            open(ctx.out(e, '.tail.bin'), 'wb').write(raw[len(raw) - e['tail_size']:])
        tail = src_stem(e) + '.tail.bin'
    return '%s: %s %s\n\t%s\n\t$(GBAGFX) $@.raw.bin $@.raw.bin.lz\n\tcat $@.raw.bin.lz %s > $@\n\trm -f $@.raw.bin $@.raw.bin.lz\n' % (
        path_of(e), deps, tail, make_raw, tail)


def picture_paths(ctx, e):
    """builder: picture -> (screen png, image entry, built image, built tilemap)"""
    g = ctx.by_name[e['screen']['layers'][0]['image']]
    return (src_stem(g) + '.png', g, built_path(g), built_path(e))


def picture_build(scr, method, num_tiles, trailing, tmp):
    """run tsa_generator on a full picture -> (image bytes, tilemap bytes)"""
    oi, ot = '%s.feimg%d.bin' % (tmp, method), '%s.fetsa%d.bin' % (tmp, method)
    subprocess.run([sys.executable, 'scripts/gfxtools/tsa_generator.py', scr, oi, ot,
                    '--num_tiles', str(num_tiles)], check=True, capture_output=True)
    img, tsa = open(oi, 'rb').read(), open(ot, 'rb').read() + bytes.fromhex(trailing or '')
    os.remove(oi); os.remove(ot)
    return img, tsa


def write_sources(ctx, e, rules, overwrite, repo_targets):
    """writes the source(s) of one entry and appends its make rules; returns what it did"""
    can = lambda p: not ctx.dry and (overwrite or not os.path.exists(p))
    t = e.get('data_type')
    if e.get('rebuild') == 'binary' or e.get('lz_exact') is False:
        return None          # kept as a binary (gbagfx cannot reproduce its LZ77 data)
    built = built_path(e)
    if os.path.normpath(built) in repo_targets or os.path.normpath(path_of(e)) in repo_targets:
        return 'built by the repo makefiles'
    custom = needs_custom_pack(e)
    if e.get('lz_min_disp') and not custom:
        rules.append('%s: %s\n\t$(PYTHON) scripts/gfx_png.py lz --min-disp %d $< $@\n'
                     % (path_of(e), built, e['lz_min_disp']))
    if t == 'palette':
        data = ctx.data(e)
        n = (e.get('pal') or {}).get('parts', 1)
        expand = (e.get('pal') or {}).get('expand', 'round')
        if n == 1:
            p = ctx.out(e, '.pal')
            if can(p):
                RB.write_pal(p, data, expand)
            if custom:
                rules.append(pack_rule(ctx, e, src_stem(e) + '.pal', '$(GBAGFX) $< $@.raw.gbapal%s && mv $@.raw.gbapal $@.raw.bin'
                                       % high_bits_cmd(e, '$@.raw.gbapal')))
            else:
                rules.append('%s: %s\n\t$(GBAGFX) $< $@.tmp.gbapal%s && mv $@.tmp.gbapal $@\n'
                             % (built, src_stem(e) + '.pal', high_bits_cmd(e, '$@.tmp.gbapal')))
        else:
            parts = []
            for i in range(n):
                p = ctx.out(e, '.part%d.pal' % i)
                if can(p):
                    RB.write_pal(p, data[i * 512:(i + 1) * 512], expand)
                parts.append(src_stem(e) + '.part%d.pal' % i)
            rules.append('%s: %s\n\tfor p in $^; do $(GBAGFX) $$p $$p.gbapal || exit 1; done; '
                         'cat $(addsuffix .gbapal,$^) > $@; rm -f $(addsuffix .gbapal,$^)%s\n'
                         % (built, ' '.join(parts), high_bits_cmd(e, '$@')))
        return 'pal'
    if t == 'gfx4bpp' and 'png' in e:
        png = e['png']
        if png.get('output') == 'none':
            return 'sheet in the fetsa picture (repo rule)'
        if png.get('picture'):
            return None      # written with its tilemap (builder: picture)
        T = RB.tiles_of(ctx.data(e))
        p = ctx.out(e, '.png')
        if png.get('tile_banks'):
            tb = []
            for run in png['tile_banks'].split():
                b, n = run.split('x')
                tb += [int(b)] * int(n)
            T2 = T + (np.array(tb[:len(T)] + [0] * (len(T) - len(tb)), np.uint8)[:, None, None] << 4)
            img, _ = RB.arrange(T2, png['width'])
            pal = np.zeros((16, 16, 3), np.uint8)
            for b, ref in (png.get('banks') or {}).items():
                if isinstance(ref, list) and ref[0] in ctx.by_name:
                    pal[int(b)] = ctx.colors(ref[0], ref[1])
                elif isinstance(ref, str):
                    pal[int(b)] = hex_colors(ref)
            if can(p):
                im = Image.fromarray(img.astype(np.uint8), 'P')
                im.putpalette(pal.reshape(-1).tolist())
                im.save(p)
        else:
            img, _ = RB.arrange(T, png['width'])
            if png.get('pad'):
                n = len(T)
                filled = np.ones((((n + png['width'] - 1) // png['width']) * png['width'], 8, 8), np.uint8) * png['pad']
                filled[:n] = T
                img, _ = RB.arrange(filled, png['width'])
            if can(p):
                if png.get('palette') == 'greyscale' and not png.get('palette_colors'):
                    Image.fromarray(((15 - img) * 17).astype(np.uint8), 'L').save(p)
                else:
                    RB.save_png(p, img, png_colors(ctx, png))
        n = png['num_tiles']
        if custom:
            rules.append(pack_rule(ctx, e, src_stem(e) + '.png',
                                   '$(GBAGFX) $< $@.raw.4bpp -num_tiles %d && mv $@.raw.4bpp $@.raw.bin' % n))
        else:
            rules.append('%s: %s\n\t$(GBAGFX) $< $@.tmp.4bpp -num_tiles %d && mv $@.tmp.4bpp $@\n'
                         % (built, src_stem(e) + '.png', n))
        return 'png'
    if t == 'tilemap' and 'screen' in e and e['screen'].get('builder') in ('tsa_generator', 'tsa_png'):
        return 'screen (repo rule)'
    if t == 'tilemap' and 'screen' in e and e['screen'].get('builder') == 'picture':
        s = e['screen']
        E, layers, spec = screen_spec(ctx, e)
        scr = RB.draw_screen(E, layers, None)
        pal = np.zeros((16, 16, 3), np.uint8)
        banks = s.get('banks') or {}
        bcol = s.get('bank_colors') or {}
        for sb in range(16):
            b = banks.get(sb) or banks.get(str(sb))
            hx = bcol.get(sb) or bcol.get(str(sb))
            if hx:
                pal[sb] = hex_colors(hx)
            else:
                pal[sb] = ctx.colors(b[0], b[1]) if b and b[0] in ctx.by_name else RB.GREY[0]
        p = os.path.join(ctx.a.repo, spec['screen'])
        os.makedirs(os.path.dirname(p), exist_ok=True)
        if can(p):
            im = Image.fromarray(scr, 'P')
            im.putpalette(pal.reshape(-1).tolist())
            im.save(p)
        scr_png, g, img, tsa = picture_paths(ctx, e)
        m, tmp = s['method'], tsa + '.tmp'
        cmd = ('$(PYTHON) scripts/gfxtools/tsa_generator.py $< %s.feimg%d.bin %s.fetsa%d.bin --num_tiles %d'
               ' && mv %s.feimg%d.bin %s && mv %s.fetsa%d.bin %s'
               % (tmp, m, tmp, m, g['png']['num_tiles'], tmp, m, img, tmp, m, tsa))
        if s.get('trailing'):
            cmd += (" && $(PYTHON) -c \"import sys; open(sys.argv[1], 'ab').write(bytes.fromhex(sys.argv[2]))\" %s %s"
                    % (tsa, s['trailing']))
        # grouped target (GNU make 4.3): one run writes both
        rules.append('%s %s &: %s\n\t%s\n' % (tsa, img, scr_png, cmd))
        return 'screen (picture: image + tilemap)'
    return None              # tilemaps and data stay binary


def existing_targets(repo):
    """targets that the repo's own makefiles already build explicitly"""
    import glob
    found, unresolved = set(), set()
    files = ['Makefile', 'graphics_file_rules.mk'] + glob.glob(os.path.join(repo, 'graphics', '**', '*.mk'), recursive=True)
    for f in files:
        p = f if os.path.isabs(f) else os.path.join(repo, f)
        if not os.path.exists(p):
            continue
        text = open(p, encoding='utf-8', errors='replace').read().split('\n')
        var = {}
        for line in text:
            m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s*:?=\s*(.*)$', line)
            if m:
                var[m.group(1)] = m.group(2).strip()

        def expand(t):
            for _ in range(5):
                t2 = re.sub(r'\$\(([A-Za-z_][A-Za-z0-9_]*)\)', lambda m: var.get(m.group(1), m.group(0)), t)
                if t2 == t:
                    break
                t = t2
            return t
        for line in text:
            if line[:1] in ' \t#' or ':' not in line or line.startswith('%') or re.match(r'^[A-Za-z_][A-Za-z0-9_]*\s*:?=', line):
                continue
            head = expand(line.split(':', 1)[0])
            if '$(' in head:
                unresolved.add(head.strip())
                continue
            for t in head.split():
                if '%' not in t:
                    found.add(os.path.normpath(t))
    # targets written with make functions ($(addsuffix ...)): let make expand them
    for head in unresolved:
        r = subprocess.run(['make', '-s', '--no-print-directory', '-f', 'Makefile',
                            '--eval', '_gfx_png_targets: ; @echo %s' % head, '_gfx_png_targets'],
                           cwd=repo, capture_output=True, text=True)
        found.update(os.path.normpath(t) for t in r.stdout.split() if '%' not in t)
    return found


def sources(a):
    ctx = Ctx(a)
    repo_targets = existing_targets(a.repo)
    rules, c = [], Counter()
    for e in ctx.files:
        if a.only and a.only not in e['name'] and a.only not in e['location']:
            continue
        try:
            c[write_sources(ctx, e, rules, a.overwrite, repo_targets) or 'kept binary'] += 1
        except Exception as ex:
            c['error'] += 1
            print('error', e['name'], repr(ex)[:150])
    if not a.only:
        with open(os.path.join(a.repo, RULES_MK), 'w') as f:
            f.write('# generated by scripts/gfx_png.py from graphic_extract.yml + graphic_png.yml:\n'
                    '# graphics_png/ sources -> the binaries the sources incbin\n\n')
            f.writelines(x + '\n' for x in rules)
    for k, v in sorted(c.items()):
        print('  %-40s %d' % (k, v))


def source_files(ctx, e, repo_targets):
    """the source files a binary is built from, or None when it is used as extracted"""
    if e.get('rebuild') == 'binary' or e.get('lz_exact') is False:
        return None
    t = e.get('data_type')
    if e.get('rebuild') == 'repo':
        return [e['source']]
    if os.path.normpath(built_path(e)) in repo_targets or os.path.normpath(path_of(e)) in repo_targets:
        return []            # the repo's makefiles build it from their own sources
    if t == 'palette':
        n = (e.get('pal') or {}).get('parts', 1)
        return [src_stem(e) + '.pal'] if n == 1 else [src_stem(e) + '.part%d.pal' % i for i in range(n)]
    if t == 'gfx4bpp' and 'png' in e and e['png'].get('picture'):
        return [picture_paths(ctx, ctx.by_name[e['png']['picture']])[0]]
    if t == 'gfx4bpp' and 'png' in e and e['png'].get('output') != 'none':
        return [src_stem(e) + '.png']
    if t == 'tilemap' and (e.get('screen') or {}).get('builder') == 'picture':
        return [picture_paths(ctx, e)[0]]
    return None


def prune(a):
    """delete the extracted binaries that make can build from a source"""
    ctx = Ctx(a)
    ctx.dry = True
    repo_targets = existing_targets(a.repo)
    removed, kept, missing = 0, [], []
    for e in ctx.files:
        src = source_files(ctx, e, repo_targets)
        if src is None:
            kept.append(e)
            continue
        if not all(os.path.exists(os.path.join(a.repo, x)) for x in src):
            missing.append(e['name'])
            kept.append(e)
            continue
        for p in {path_of(e), built_path(e)}:
            fp = os.path.join(a.repo, p)
            if os.path.exists(fp):
                os.remove(fp)
                removed += 1
    print('removed %d binaries that will be built from their sources' % removed)
    if a.kept_mk:
        tracked = set(subprocess.run(['git', 'ls-files'], cwd=a.repo, capture_output=True,
                                     text=True).stdout.split())
        ps = sorted({path_of(e) for e in kept} - tracked - repo_targets)
        with open(os.path.join(a.repo, a.kept_mk), 'w') as fh:
            fh.write('# generated by scripts/gfx_png.py prune --kept-mk: binaries used as extracted\n'
                     'GFX_KEPT := %s\n\n'
                     '# missing (e.g. after make clean): extract them again from baserom.gba\n'
                     '$(GFX_KEPT) &:\n\t$(PYTHON) scripts/gfx_png.py extract --missing $(GFX_KEPT)\n' % ' '.join(ps))
        print('%s: %d binaries used as extracted' % (a.kept_mk, len(ps)))
    if missing:
        print('kept %d binaries whose source is missing: %s' % (len(missing), ', '.join(missing[:10])))


def extract(a):
    ctx = Ctx(a)
    want = {os.path.normpath(p) for p in a.paths}
    for e in ctx.files:
        p = os.path.normpath(path_of(e))
        if p not in want or (a.missing and os.path.exists(p)):
            continue
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'wb').write(ctx.raw(e))


def verify(a):
    ctx = Ctx(a)
    gfx = RB.Gfx(a.repo)
    repo_targets = existing_targets(a.repo)
    res, bad = Counter(), []
    for e in ctx.files:
        if a.only and a.only not in e['name'] and a.only not in e['location']:
            continue
        t = e.get('data_type')
        stem = os.path.join(a.repo, src_stem(e))
        try:
            src = source_files(ctx, e, repo_targets)
            if src is None or e.get('rebuild') == 'repo' or src == []:
                res['not from graphics_png'] += 1
                continue
            data = ctx.data(e)
            if t == 'palette':
                n = (e.get('pal') or {}).get('parts', 1)
                back = gfx.pal_to_gbapal(stem + '.pal') if n == 1 else \
                    b''.join(gfx.pal_to_gbapal(stem + '.part%d.pal' % i) or b'' for i in range(n))
                if back and (e.get('pal') or {}).get('high_bits'):
                    back = apply_high_bits(back, e['pal']['high_bits'])
            elif t == 'gfx4bpp':
                if e['png'].get('picture'):
                    pk = ctx.by_name[e['png']['picture']]
                    back = picture_build(os.path.join(a.repo, picture_paths(ctx, pk)[0]), pk['screen']['method'],
                                         e['png']['num_tiles'], pk['screen'].get('trailing'),
                                         os.path.join(a.repo, SRC_ROOT, 'verify_tmp'))[0]
                else:
                    back = gfx.png_to_4bpp(stem + '.png', e['png']['num_tiles'])
            else:
                _, g, _, _ = picture_paths(ctx, e)
                back = picture_build(os.path.join(a.repo, picture_paths(ctx, e)[0]), e['screen']['method'],
                                     g['png']['num_tiles'], e['screen'].get('trailing'),
                                     os.path.join(a.repo, SRC_ROOT, 'verify_tmp'))[1]
            ok = back == data
            res['%s %s' % (t, 'exact' if ok else 'MISMATCH')] += 1
            if not ok:
                bad.append(e['name'])
            if ok and e.get('compression') == 'lz77':
                raw = ctx.raw(e)
                body = raw[:len(raw) - e.get('tail_size', 0)]
                c = lz77_encode(data, e['lz_min_disp']) if e.get('lz_min_disp') else gfx.lz(data)
                ok_lz = c is not None and (c == body or (body[:len(c)] == c and not any(body[len(c):])))
                res['lz77 ' + ('reproduced' if ok_lz else 'DIFFERS')] += 1
                if not ok_lz:
                    bad.append(e['name'] + ' (lz)')
        except Exception as ex:
            res['%s error' % t] += 1
            bad.append('%s %s' % (e['name'], repr(ex)[:80]))
    for k, v in sorted(res.items()):
        print('  %-45s %d' % (k, v))
    if bad:
        print('not exact (%d): %s' % (len(bad), ', '.join(bad[:20])))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('highbits')
    p.add_argument('file')
    p.add_argument('mask')
    p = sub.add_parser('lz')
    p.add_argument('--min-disp', type=int, default=1)
    p.add_argument('input')
    p.add_argument('output')
    for n in ('sources', 'prune', 'verify', 'extract'):
        p = sub.add_parser(n)
        p.add_argument('--repo', default='.')
        if n in ('sources', 'verify'):
            p.add_argument('--only', default='')
        if n == 'sources':
            p.add_argument('--overwrite', action='store_true')
        if n == 'prune':
            p.add_argument('--kept-mk', default='')
        if n == 'extract':
            p.add_argument('--missing', action='store_true')
            p.add_argument('paths', nargs='+')
    a = ap.parse_args()
    if a.cmd == 'highbits':
        open(a.file, 'r+b').write(apply_high_bits(open(a.file, 'rb').read(), a.mask))
    elif a.cmd == 'lz':
        open(a.output, 'wb').write(lz77_encode(open(a.input, 'rb').read(), a.min_disp))
    else:
        {'sources': sources, 'prune': prune, 'verify': verify, 'extract': extract}[a.cmd](a)


if __name__ == '__main__':
    main()
