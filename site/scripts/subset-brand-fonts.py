"""Build renamed, content-specific WOFF subsets from licensed source fonts.

Usage: python scripts/subset-brand-fonts.py /path/to/original-font-directory [--family song|kai]
Download the originals from the URLs in public/fonts/SOURCES.json (Song)
or public/fonts/KAI-SOURCES.json (Kai).
Requires fontTools. The output uses WOFF with zlib, without a Brotli dependency.

The glyph set is derived from the actual site source: the React components in
app/ plus index.html. Re-run it whenever new Chinese text is added, then commit
the regenerated public/fonts/jiandi-{song,kai}-*.woff.
"""
from pathlib import Path
import argparse
from fontTools import subset
from fontTools.ttLib import TTFont

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('originals', type=Path)
parser.add_argument('--family', choices=('song', 'kai'), default='song')
args = parser.parse_args()
originals = args.originals
family = 'Jiandi Song' if args.family == 'song' else 'Jiandi Kai'
prefix = 'JiandiSong' if args.family == 'song' else 'JiandiKai'
version = '2.003' if args.family == 'song' else '1.522'
source_files = list((root / 'app').rglob('*.tsx')) + [root / 'index.html']
text = ''.join(p.read_text() for p in source_files)
charset = set(map(ord, text)) | set(range(0x20, 0x100)) | set(range(0x2000, 0x2070))

for weight in ('Regular', 'Medium'):
    filename = f'SourceHanSerifSC-{weight}.otf' if args.family == 'song' else f'LXGWWenKai-{weight}.ttf'
    source = originals / filename
    font = TTFont(source)
    cmap = font.getBestCmap()
    missing = [chr(c) for c in charset if 0x3400 <= c <= 0x9fff and c not in cmap]
    if missing:
        raise ValueError(f'Chinese glyphs missing from source: {missing}')
    opts = subset.Options()
    opts.name_IDs = ['*']
    opts.name_languages = ['*']
    opts.name_legacy = True
    sub = subset.Subsetter(options=opts)
    sub.populate(unicodes=charset)
    sub.subset(font)
    replacements = {
        1: family, 2: weight, 3: f'{prefix}-{weight}-{version}-subset',
        4: f'{family} {weight}', 6: f'{prefix}-{weight}',
        16: family, 17: weight,
    }
    for record in font['name'].names:
        if record.nameID in replacements:
            record.string = replacements[record.nameID].encode(record.getEncoding())
    if 'CFF ' in font:
        cff = font['CFF '].cff
        cff.fontNames = [f'{prefix}-{weight}']
        for top in cff.topDictIndex:
            top.FamilyName = family
            top.FullName = f'{family} {weight}'
    font.flavor = 'woff'
    output = root / 'public/fonts' / f'jiandi-{args.family}-{weight.lower()}.woff'
    font.save(output)
    print(f'{output.name}: {output.stat().st_size} bytes; Chinese glyph coverage complete')
