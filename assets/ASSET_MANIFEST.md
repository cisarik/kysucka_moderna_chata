# PBR drevo pre pracovnú scénu v03

Stav: dve overené sady Poly Haven; zdrojové JPG sa neupravovali. Dátum: 14. 11. 2026.
Licencia všetkých šiestich súborov: [CC0](https://polyhaven.com/license).

- [coated_pine_02](https://polyhaven.com/a/coated_pine_02): 2048 × 2048 px, fyzická opakovacia plocha 1,05 × 1,05 m. Vlákna vedú po U, teda vodorovne v obrázku; UV sa nezamieňajú. Určené len pre 89 exteriérových drevených objektov.
- [rough_wood](https://polyhaven.com/a/rough_wood): 2048 × 2048 px, plocha 0,50 × 0,50 m. Vlákna vedú po V, teda zvisle v obrázku; logické metrické UV sa zamieňajú `(u,v) → (v,u)`. Určené len pre stĺpiky a priečky plota.

Smer vlákien potvrdila vizuálna kontrola oboch základných máp cez Blender MCP. Veľkosti a MD5 sa zhodujú s konkrétnym realizačným grantom. Zdrojová URL každého súboru je `https://dl.polyhaven.org/file/ph-assets/Textures/jpg/2k/<sada>/<názov-súboru>`.

| Súbor | Úloha | Farebný priestor | Bajty | MD5 | SHA-256 | Zdrojový súbor |
|---|---|---|---:|---|---|---|
| `assets/textures/wood/coated_pine_02/coated_pine_02_diff_2k.jpg` | základná farba | sRGB | 2985006 | `9d2bb5797918490d00743efe737c1471` | `7a74bd4b58da02aab73a53f3b307524a6d79c0c10fd4fa94ccc9f9b04839c59a` | [JPG](https://dl.polyhaven.org/file/ph-assets/Textures/jpg/2k/coated_pine_02/coated_pine_02_diff_2k.jpg) |
| `assets/textures/wood/coated_pine_02/coated_pine_02_rough_2k.jpg` | drsnosť | Non-Color | 620683 | `44dd138d932b3f966e4be7ae21f81030` | `f59af2c9b15a0c3637a7911bed8a859ca075b37cc26517cf0f4f5ad804cc1606` | [JPG](https://dl.polyhaven.org/file/ph-assets/Textures/jpg/2k/coated_pine_02/coated_pine_02_rough_2k.jpg) |
| `assets/textures/wood/coated_pine_02/coated_pine_02_nor_gl_2k.jpg` | OpenGL normála | Non-Color | 1418403 | `e4ca3043d18d35aee836fc26cfc3ac1e` | `72f2f07712d554fc2df1758cea158a75aa438cf5548bae3d99b30405b150b7b3` | [JPG](https://dl.polyhaven.org/file/ph-assets/Textures/jpg/2k/coated_pine_02/coated_pine_02_nor_gl_2k.jpg) |
| `assets/textures/wood/rough_wood/rough_wood_diff_2k.jpg` | základná farba | sRGB | 2223327 | `f5f9c55696f047ceaa49dc97c5aa5526` | `0bd2b3195db9b54d55aa0f842801220ec5e1d389f5fc1e670b378bdaca3f8e7b` | [JPG](https://dl.polyhaven.org/file/ph-assets/Textures/jpg/2k/rough_wood/rough_wood_diff_2k.jpg) |
| `assets/textures/wood/rough_wood/rough_wood_rough_2k.jpg` | drsnosť | Non-Color | 810338 | `832d6d549a8e76c16b9af2586f429d6c` | `38343cb062e7fadcda513ded0b17271c9d7f1da56765d03508dc84c8ff1bd475` | [JPG](https://dl.polyhaven.org/file/ph-assets/Textures/jpg/2k/rough_wood/rough_wood_rough_2k.jpg) |
| `assets/textures/wood/rough_wood/rough_wood_nor_gl_2k.jpg` | OpenGL normála | Non-Color | 2520021 | `62594f2d00eb246581b9d4fde30209f1` | `b75cb1e989407e442c3255f3e05ea8c40162c0e5dc2efc9ef2515fce61319194` | [JPG](https://dl.polyhaven.org/file/ph-assets/Textures/jpg/2k/rough_wood/rough_wood_nor_gl_2k.jpg) |

Spolu: 10 577 778 bajtov. Použité mapy sú zabalené do v03 a zachovávajú relatívne cesty `//../assets/textures/wood/...`.

## Použitie a úpravy

Originálne JPG ostávajú byte-identické so stiahnutými súbormi. Úpravy farby, drsnosti a intenzity normály sú iba v shaderoch. Exteriér používa jemnú medovohnedú povrchovú úpravu, drsnosť 0,42–0,58; plot menej sýte sivohnedé drevo s drsnosťou 0,72–0,88. Metrické UV a posuny odvodené zo SHA-256 mena objektu vytvára `scripts/timber_fence_v03.py`; normály používajú ten istý UVMap vrátane zámeny osí. Nepoužíva sa geometrický displacement ani subdivision.

Jedna vizuálna korekcia po prvom rendri: exteriér má saturáciu 0,85 a hodnotu 0,68. Pomalá neperiodická maska mieša dve rovnako veľké, iba posunuté fázy tých istých troch máp; posun UV je (0,317; 0,419), mierka masky 0,38. Farba, drsnosť aj normála používajú tú istú masku. Toto potláča pravidelné opakovanie sukov bez nových aktív, otočenia vlákien alebo zmeny geometrie.
