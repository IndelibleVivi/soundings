"""Build renamed, content-specific WOFF subsets from the two licensed source OTFs.

Usage: python scripts/subset-brand-fonts.py /path/to/original-font-directory
Download the originals from the URLs in public/fonts/SOURCES.json.
Requires fontTools. The output uses WOFF with zlib, without a Brotli dependency.

The glyph set is derived from the actual site source: the React components in
app/ plus index.html. Re-run it whenever new Chinese text is added, then commit
the regenerated public/fonts/jiandi-song-*.woff.
"""
from pathlib import Path
import sys
from fontTools import subset
from fontTools.ttLib import TTFont

root = Path(__file__).resolve().parents[1]
originals = Path(sys.argv[1])
source_files = list((root / 'app').rglob('*.tsx')) + [root / 'index.html']
text = ''.join(p.read_text() for p in source_files)
charset = set(map(ord, text)) | set(range(0x20, 0x100)) | set(range(0x2000, 0x2070))

for weight in ('Regular', 'Medium'):
    source = originals / f'SourceHanSerifSC-{weight}.otf'
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
        1: 'Jiandi Song', 2: weight, 3: f'JiandiSong-{weight}-2.003-subset',
        4: f'Jiandi Song {weight}', 6: f'JiandiSong-{weight}',
        16: 'Jiandi Song', 17: weight,
    }
    for record in font['name'].names:
        if record.nameID in replacements:
            record.string = replacements[record.nameID].encode(record.getEncoding())
    if 'CFF ' in font:
        cff = font['CFF '].cff
        cff.fontNames = [f'JiandiSong-{weight}']
        for top in cff.topDictIndex:
            top.FamilyName = 'Jiandi Song'
            top.FullName = f'Jiandi Song {weight}'
    font.flavor = 'woff'
    output = root / 'public/fonts' / f'jiandi-song-{weight.lower()}.woff'
    font.save(output)
    print(f'{output.name}: {output.stat().st_size} bytes; Chinese glyph coverage complete')
