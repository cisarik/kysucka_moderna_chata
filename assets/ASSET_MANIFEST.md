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

## Prostredie v04

Pracovný vizualizačný kandidát: 7 normalizovaných knižníc. Pôvodné archívy ostávajú v dočasnom úložisku; offline zostavenie používa iba nižšie uvedené súbory.

### Pôvod a úpravy

| Identifikátor | Autor | Zdroj | Licencia | Zachované siete / trojuholníky |
|---|---|---|---|---|
| `sketchfab_bf500546e2874f9ea086ba6abb11357e` | PlantCatalog | [Realistic HD Norway spruce (3/43)](https://sketchfab.com/3d-models/realistic-hd-norway-spruce-343-bf500546e2874f9ea086ba6abb11357e) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | ABIES_LOD0: 84240; ABIES_LOD1: 21000; ABIES_YOUNG: 84240 |
| `sketchfab_3232c3022f2947b7999de0941ede5653` | PlantCatalog | [Realistic HD Black spruce (19/38)](https://sketchfab.com/3d-models/realistic-hd-black-spruce-1938-3232c3022f2947b7999de0941ede5653) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | MARIANA_LOD0: 69701; MARIANA_LOD1: 18000 |
| `sketchfab_7df0631398f443379fa4541e9efc2343` | Lassi Kaukonen (thesidekick) | [Blossoming apple tree](https://sketchfab.com/3d-models/blossoming-apple-tree-7df0631398f443379fa4541e9efc2343) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | ORCHARD: 80000 |
| `food_apple_01` | Oliver Harries | [Food Apple 01](https://polyhaven.com/a/food_apple_01) | [CC0](https://polyhaven.com/license) | FOOD_APPLE_01_0: 7012 |
| `grass_medium_01` | Rob Tuytel, Rico Cilliers | [Grass Medium 01](https://polyhaven.com/a/grass_medium_01) | [CC0](https://polyhaven.com/license) | GRASS_MEDIUM_01_0: 2301; GRASS_MEDIUM_01_1: 290; GRASS_MEDIUM_01_2: 662 |
| `shrub_01` | Rico Cilliers | [Shrub 01](https://polyhaven.com/a/shrub_01) | [CC0](https://polyhaven.com/license) | SHRUB_01_0: 2276; SHRUB_01_1: 1544; SHRUB_01_2: 1374 |
| `periwinkle_plant` | Amal Kumar | [Periwinkle Plant](https://polyhaven.com/a/periwinkle_plant) | [CC0](https://polyhaven.com/license) | PERIWINKLE_PLANT_0: 5480; PERIWINKLE_PLANT_1: 2606; PERIWINKLE_PLANT_2: 1508 |

Čierny smrek (`Picea mariana`) je Michalom vybraný podklad pre hustý les; nejde o tvrdenie o jeho pôvodnosti na Kysuciach. Nórsky smrek je `Picea abies`. Jabloň je normalizovaný fotogrametrický podklad Blossoming apple tree.

Úpravy: statické siete bez rigov, animácie a demonstračných scén; metre a os Z nahor; odstránený zemný lem jablone, výška približne 4,15 m a zníženie na 80 000 trojuholníkov; jej 8K mapy zmenšené na 2K. Smreky používajú zdrojové LOD2 ako detailný master a odvodené LOD1 (21 000 / 18 000 trojuholníkov); mladý nórsky smrek má vodorovnú šírku koruny násobenú 0,72. Sivé ihličie čierneho smreka je v shaderi tónované na zelenú; alfa má bielu nepriehľadnú a čiernu vyrezanú časť. Použité sú OpenGL normály a jemná translucencia. Byliny používajú vybrané jednotlivé siete/LOD, zoskupené zdieľanými inštanciami. Bez geometrického displacementu.

### Prijaté archívy a pôvodné súbory

| Vstup | Bajty | MD5, ak publikované | SHA-256 |
|---|---:|---|---|
| [work/downloads/food_apple_01/food_apple_01_1k.blend](https://dl.polyhaven.org/file/ph-assets/Models/blend/1k/food_apple_01/food_apple_01_1k.blend) | 445545 | `d319fcdce53e2c88946ae7079c219a0e` | `c933242181c204f07b55afee1105c576dcd9430cbd3f0fcac947e834197f03f0` |
| [work/downloads/food_apple_01/textures/food_apple_01_diff_1k.jpg](https://dl.polyhaven.org/file/ph-assets/Models/jpg/1k/food_apple_01/food_apple_01_diff_1k.jpg) | 183791 | `3ddf2b8313f20c95f3e04fb057b32d7b` | `b7fc17cfb5013958167bbc089ea4d1c193fb1c61ea4f3c974a9894ed9ba82e8a` |
| [work/downloads/food_apple_01/textures/food_apple_01_nor_gl_1k.jpg](https://dl.polyhaven.org/file/ph-assets/Models/jpg/1k/food_apple_01/food_apple_01_nor_gl_1k.jpg) | 63513 | `e456cb63d6a4c298c826b63be0adfaf7` | `c81b1e51ce7e789b65bfde2f046dcb5ba5773b5c6be3e572313be0600c51721b` |
| [work/downloads/food_apple_01/textures/food_apple_01_rough_1k.jpg](https://dl.polyhaven.org/file/ph-assets/Models/jpg/1k/food_apple_01/food_apple_01_rough_1k.jpg) | 53123 | `e46e242f52a3c2138a1e8c6ce0d82438` | `2e5a503af38df7b570b0e81cc9563125f0913b466e01140d4e24ea5ebdbec587` |
| [work/downloads/grass_medium_01/grass_medium_01_1k.blend](https://dl.polyhaven.org/file/ph-assets/Models/blend/1k/grass_medium_01/grass_medium_01_1k.blend) | 1832028 | `e37f4fa4c90ddeb807ce6b4c09e3033d` | `5bbeaf7161508c1de66f137e7fcaec6fdea9c4ac0faa134c384c89c97271bec2` |
| [work/downloads/grass_medium_01/textures/grass_medium_01_diff_1k.jpg](https://dl.polyhaven.org/file/ph-assets/Models/jpg/1k/grass_medium_01/grass_medium_01_diff_1k.jpg) | 395673 | `6b18ed50d776fd20c1304d9994bd764e` | `71495bd6a11fddcab0aaff38246fea1a7b802a705483f1c7cbca53955daa8050` |
| [work/downloads/grass_medium_01/textures/grass_medium_01_nor_gl_1k.jpg](https://dl.polyhaven.org/file/ph-assets/Models/jpg/1k/grass_medium_01/grass_medium_01_nor_gl_1k.jpg) | 956166 | `fcf43dd1253f56e4c361079f34155c37` | `cae298d3d1d7ff7c7e210ad8ac772b96706e356f9315a6b04fde373ce01ccf1e` |
| [work/downloads/grass_medium_01/textures/grass_medium_01_rough_1k.jpg](https://dl.polyhaven.org/file/ph-assets/Models/jpg/1k/grass_medium_01/grass_medium_01_rough_1k.jpg) | 541262 | `f60c4663fb5b1f08c7c7178db9f8b684` | `e9a7c5b3cd4c4a3e4eeb016fed248c51796262ee412624e4b9e5b9cc862bd203` |
| [work/downloads/grass_medium_01/textures/grass_medium_01_alpha_1k.png](https://dl.polyhaven.org/file/ph-assets/Models/png/1k/grass_medium_01/grass_medium_01_alpha_1k.png) | 648718 | `6b5b251ef1ca9a69ab9f49def66d758a` | `711a8e49af758d6a6ce1f610db858899a27be19da6d1866bd35c13bc7b8ffeff` |
| [work/downloads/shrub_01/shrub_01_1k.blend](https://dl.polyhaven.org/file/ph-assets/Models/blend/1k/shrub_01/shrub_01_1k.blend) | 6535174 | `dfbacf2c8c64823862ec8b9747d7687e` | `a6ba7e56937853891eae84dc875fcc653d1ac38d50364b32a250025d7d4a80b0` |
| [work/downloads/shrub_01/textures/shrub_01_diff_2k.jpg](https://dl.polyhaven.org/file/ph-assets/Models/jpg/2k/shrub_01/shrub_01_diff_2k.jpg) | 1651989 | `cd89f941ba9e5c60cbeee50e0b269e2c` | `d464a823982b28832a92d3edacc62461adfb3f99117829127e79eb253051e940` |
| [work/downloads/shrub_01/textures/shrub_01_nor_gl_2k.jpg](https://dl.polyhaven.org/file/ph-assets/Models/jpg/2k/shrub_01/shrub_01_nor_gl_2k.jpg) | 2628947 | `ba76e790f9346ad2366585b57095c214` | `1b2f8631a66ef35c876238d6269f2cd2d1603102b7422f2cc57e3ec9ab209b62` |
| [work/downloads/shrub_01/textures/shrub_01_rough_2k.jpg](https://dl.polyhaven.org/file/ph-assets/Models/jpg/2k/shrub_01/shrub_01_rough_2k.jpg) | 906913 | `1661adf4a08af76b338468d28a04f95f` | `f1c08a9c3598dcf1cfb42bf6edd07b4f8a71a19f6c418ddc8f447d76245ba985` |
| [work/downloads/shrub_01/textures/shrub_01_alpha_2k.png](https://dl.polyhaven.org/file/ph-assets/Models/png/2k/shrub_01/shrub_01_alpha_2k.png) | 297762 | `dabea4c2ea5710c231d58cf94b85e6b3` | `238e65642075a5317d5a68b509dfef4f369fd6e76b84528bc37eac95587edd24` |
| [work/downloads/periwinkle_plant/periwinkle_plant_1k.blend](https://dl.polyhaven.org/file/ph-assets/Models/blend/1k/periwinkle_plant/periwinkle_plant_1k.blend) | 1680482 | `6920bf78874cc7b966c63e73f1a14ddb` | `91dc069a8824244c3e16f0fd207295946a4d7e17e8efccfa34a1a5c5c94d987f` |
| [work/downloads/periwinkle_plant/textures/periwinkle_plant_diff_1k.jpg](https://dl.polyhaven.org/file/ph-assets/Models/jpg/1k/periwinkle_plant/periwinkle_plant_diff_1k.jpg) | 349879 | `32b2cba340cf12c976f0fb4c26cc5721` | `32d61084e6c07fa3ca8e03b35b347a12717f971efc90e8fe1185931ee2298c56` |
| [work/downloads/periwinkle_plant/textures/periwinkle_plant_nor_gl_1k.jpg](https://dl.polyhaven.org/file/ph-assets/Models/jpg/1k/periwinkle_plant/periwinkle_plant_nor_gl_1k.jpg) | 418428 | `10e7ee6a4ccf292564237c2b31a5a4be` | `36d2464e7500f741500228b955c1fb0f26d954e869bd26f93dd25c0fafc5087d` |
| [work/downloads/periwinkle_plant/textures/periwinkle_plant_rough_1k.jpg](https://dl.polyhaven.org/file/ph-assets/Models/jpg/1k/periwinkle_plant/periwinkle_plant_rough_1k.jpg) | 201230 | `0cf77d5da32d2051e2f8f39d4090f8b3` | `59b6289ed4a3f1ccdf091a1e3d73502bf4a6d1704a68ed8468adae34eef30b50` |
| [work/downloads/periwinkle_plant/textures/periwinkle_plant_opacity_1k.png](https://dl.polyhaven.org/file/ph-assets/Models/png/1k/periwinkle_plant/periwinkle_plant_opacity_1k.png) | 86094 | `4386b4cf7a9cc7d79ad1db812b1d8e50` | `e1dc2746b641606ae2772667c719e2b593b548759a51d86ce093322c22e903de` |
| [work/downloads/periwinkle_plant/textures/periwinkle_plant_translucency_1k.jpg](https://dl.polyhaven.org/file/ph-assets/Models/jpg/1k/periwinkle_plant/periwinkle_plant_translucency_1k.jpg) | 359204 | `237d4538e9656b4af61dba3c97ef8fb3` | `388abd2765a351c98625cf6f1f76a483aad8590c7ccecf46f9d8ec02fc2d02cf` |
| `blossoming-apple-tree.zip` | 88293821 | `—` | `32ec7eeacfaa985a4f335fe34dc916158d1e4793582496ed7db5a85db260ed0b` |
| `realistic-hd-norway-spruce.zip` | 168364749 | `—` | `4f634d5172a3a4b662c2faef666bca7e6234a92724306ab7a4e4802a03a25e95` |
| `realistic-hd-black-spruce-1938.zip` | 165134556 | `—` | `714b68f1a205b8686c29b1b42a43198a2f8a5be8deeca315bce7a41fe3fd643d` |

### Zachované súbory a kontrolné súčty

Mapy farby používajú sRGB, alfa/drsnosť/OpenGL normála/oklúzia Non-Color. Mapy sa zdieľajú medzi inštanciami. Knižnice aj v04 obsahujú zabalené použité mapy; samostatné textúry sú zachované kvôli prenosnosti a kontrole pôvodu.

| Cesta | Bajty | SHA-256 | Pôvodný SHA-256 textúry pred prípadným zmenšením |
|---|---:|---|---|
| `assets/models/sketchfab_bf500546e2874f9ea086ba6abb11357e/LICENSE.txt` | 550 | `3a215da9766a78d7d3258800143740e71f00c20434cb8bdd885dd71c573d3780` | `—` |
| `assets/models/sketchfab_bf500546e2874f9ea086ba6abb11357e/master.blend` | 15682885 | `62223577cbfb1a451edf45645cbe10b2ea789dac8d5c4b0a3b189a97f981f8cb` | `—` |
| `assets/models/sketchfab_bf500546e2874f9ea086ba6abb11357e/textures/Picea_abies_HD_Picea_abies_bark_2_Picea_abies_bark_02_LOD2_Color.png` | 439300 | `d5f0f0838ca2873bb6528fae745867f69d8191de6235d39fbf83a69992a3e65c` | `d5f0f0838ca2873bb6528fae745867f69d8191de6235d39fbf83a69992a3e65c` |
| `assets/models/sketchfab_bf500546e2874f9ea086ba6abb11357e/textures/Picea_abies_HD_Picea_abies_bark_2_Picea_abies_bark_02_n_LOD2_Normal.png` | 506816 | `36f723d7a9af6fcd47e6c1fb24a814736ccfa2b7b68821adde82c3f2ee8f7a43` | `36f723d7a9af6fcd47e6c1fb24a814736ccfa2b7b68821adde82c3f2ee8f7a43` |
| `assets/models/sketchfab_bf500546e2874f9ea086ba6abb11357e/textures/Picea_abies_HD_Picea_abies_brch_dead_Picea_ab_branch_01_dead_LOD2_Color.png` | 253724 | `f0e637c4732919a6283f2be82ce469fadf6c3fef70421ae3c89c8f682834e9e8` | `f0e637c4732919a6283f2be82ce469fadf6c3fef70421ae3c89c8f682834e9e8` |
| `assets/models/sketchfab_bf500546e2874f9ea086ba6abb11357e/textures/Picea_abies_HD_Picea_abies_brch_dead_Picea_ab_branch_01_dead_n_LOD2_Normal.png` | 284283 | `3ad6ef111157e9ca0b5a934eb112f9f6ec984d898161fc00c28dba267473e174` | `3ad6ef111157e9ca0b5a934eb112f9f6ec984d898161fc00c28dba267473e174` |
| `assets/models/sketchfab_bf500546e2874f9ea086ba6abb11357e/textures/Picea_abies_HD_Picea_branch_Picea_abies_bark_01_LOD2_Color.png` | 584283 | `69bcc0da7037219add4317bb7d78b914fa22630f4ab423d5892a4b92722edfad` | `69bcc0da7037219add4317bb7d78b914fa22630f4ab423d5892a4b92722edfad` |
| `assets/models/sketchfab_bf500546e2874f9ea086ba6abb11357e/textures/Picea_abies_HD_Picea_branch_Picea_abies_branch_01_n_LOD2_Normal.png` | 306144 | `7cbfb5fe55569c7677373f4454ce3d91ae3ae2ddf91733763c14250925177166` | `7cbfb5fe55569c7677373f4454ce3d91ae3ae2ddf91733763c14250925177166` |
| `assets/models/sketchfab_bf500546e2874f9ea086ba6abb11357e/textures/Picea_abies_HD_Picea_brch_cut_02_Picea_branch_cut_01_n_LOD2_Normal.png` | 35347 | `fad4f3790a43d6fd583d10ec3acd8a54265fa6c7540f89bdb0766c71c7ced251` | `fad4f3790a43d6fd583d10ec3acd8a54265fa6c7540f89bdb0766c71c7ced251` |
| `assets/models/sketchfab_bf500546e2874f9ea086ba6abb11357e/textures/Picea_abies_HD_Picea_brch_cut_02_Picea_branch_cut_01b_LOD2_Color.png` | 31915 | `277b01ec0ebca5574e6885321087e1cf6ec8d987ef89138cc08db99bc87f99b7` | `277b01ec0ebca5574e6885321087e1cf6ec8d987ef89138cc08db99bc87f99b7` |
| `assets/models/sketchfab_bf500546e2874f9ea086ba6abb11357e/textures/Picea_abies_HD_Picea_fol_1_Picea_fol_01_LOD2_Color.png` | 209205 | `8ae920f91091126cca9925913b6da01d8c3ab83e314962cac578a231191d2559` | `8ae920f91091126cca9925913b6da01d8c3ab83e314962cac578a231191d2559` |
| `assets/models/sketchfab_bf500546e2874f9ea086ba6abb11357e/textures/Picea_abies_HD_Picea_fol_1_Picea_fol_01_a_LOD2_Transparency.png` | 55844 | `9c4390137a028479d0c5a1d311b58c7216422e00143f4d053d8959e96fb59d92` | `9c4390137a028479d0c5a1d311b58c7216422e00143f4d053d8959e96fb59d92` |
| `assets/models/sketchfab_bf500546e2874f9ea086ba6abb11357e/textures/Picea_abies_HD_Picea_fol_1_Picea_fol_01_n_LOD2_Normal.png` | 326482 | `66e8907eeb578ed993187b40366b7bc7a9f01fd66ec41ee7cb7fc5edbf09498c` | `66e8907eeb578ed993187b40366b7bc7a9f01fd66ec41ee7cb7fc5edbf09498c` |
| `assets/models/sketchfab_bf500546e2874f9ea086ba6abb11357e/textures/Picea_abies_HD_Picea_fol_1_dying_Picea_fol_01_dying_LOD2_Color.png` | 248474 | `d37f2f36f78287882ebd9da1f8fd338b68fc9692b78e518e6add8223eec2654c` | `d37f2f36f78287882ebd9da1f8fd338b68fc9692b78e518e6add8223eec2654c` |
| `assets/models/sketchfab_bf500546e2874f9ea086ba6abb11357e/textures/Picea_abies_HD_Picea_fol_1_dying_Picea_fol_01_dying_a_LOD2_Transparency.png` | 29546 | `c21b7890c58ca83d6681ef91de2357fc83487e78b6d90837e93154dc2031f9c7` | `c21b7890c58ca83d6681ef91de2357fc83487e78b6d90837e93154dc2031f9c7` |
| `assets/models/sketchfab_bf500546e2874f9ea086ba6abb11357e/textures/Picea_abies_HD_Picea_fol_1_dying_Picea_fol_01_dying_n_LOD2_Normal.png` | 289648 | `d19396536e5332c17de0cf50ef044d42eb3458e7d562dd2641ead9cc85357c9e` | `d19396536e5332c17de0cf50ef044d42eb3458e7d562dd2641ead9cc85357c9e` |
| `assets/models/sketchfab_bf500546e2874f9ea086ba6abb11357e/textures/Picea_abies_HD_Picea_fol_2_Picea_fol_02_LOD2_Color.png` | 45353 | `eed254b4a373c4a35ab4344bc5d9ac4da45f93ef3fdf30499c87c712e40c18d8` | `eed254b4a373c4a35ab4344bc5d9ac4da45f93ef3fdf30499c87c712e40c18d8` |
| `assets/models/sketchfab_bf500546e2874f9ea086ba6abb11357e/textures/Picea_abies_HD_Picea_fol_2_Picea_fol_02_a_LOD2_Transparency.png` | 17411 | `b686b86bc49ccf7348b2ae6422d9e30e6a1fd1d9804f514132a6f6e2b17761c2` | `b686b86bc49ccf7348b2ae6422d9e30e6a1fd1d9804f514132a6f6e2b17761c2` |
| `assets/models/sketchfab_bf500546e2874f9ea086ba6abb11357e/textures/Picea_abies_HD_Picea_fol_2_Picea_fol_02_n_LOD2_Normal.png` | 82538 | `61dc3a112e7552fea12ce3bc4d889c23da7c9644ed1a00f6072d9d4b36133d34` | `61dc3a112e7552fea12ce3bc4d889c23da7c9644ed1a00f6072d9d4b36133d34` |
| `assets/models/sketchfab_bf500546e2874f9ea086ba6abb11357e/textures/Picea_abies_HD_Picea_fol_2_long_Picea_fol_02_long_LOD2_Color.png` | 90306 | `099bd1bdc95141ffcd07da2474151eb11227a5a08e1a623474212da9ff83bbb0` | `099bd1bdc95141ffcd07da2474151eb11227a5a08e1a623474212da9ff83bbb0` |
| `assets/models/sketchfab_bf500546e2874f9ea086ba6abb11357e/textures/Picea_abies_HD_Picea_fol_2_long_Picea_fol_02_long_a_LOD2_Transparency.png` | 33926 | `3d03efee25353fef7b995258b41311617725137263e53a4fc5469e9e3d8e0fa9` | `3d03efee25353fef7b995258b41311617725137263e53a4fc5469e9e3d8e0fa9` |
| `assets/models/sketchfab_bf500546e2874f9ea086ba6abb11357e/textures/Picea_abies_HD_Picea_fol_2_long_Picea_fol_02_long_n_LOD2_Normal.png` | 163940 | `39311e03666575c279c709983315f3f76059c94f76f5645ca00cb1d1b3da1d65` | `39311e03666575c279c709983315f3f76059c94f76f5645ca00cb1d1b3da1d65` |
| `assets/models/sketchfab_bf500546e2874f9ea086ba6abb11357e/textures/Picea_abies_HD_Picea_fol_2_short_Picea_fol_02_short_LOD2_Color.png` | 23613 | `96f9bf87ede01b6fff84ae9d2b4ce62febe60b17cecb1188e94e3f85170742fc` | `96f9bf87ede01b6fff84ae9d2b4ce62febe60b17cecb1188e94e3f85170742fc` |
| `assets/models/sketchfab_bf500546e2874f9ea086ba6abb11357e/textures/Picea_abies_HD_Picea_fol_2_short_Picea_fol_02_short_a_LOD2_Transparency.png` | 8790 | `155b5da9ff3dfe21442c534bd22442685a982b28608d36996a445b6fd67c6e2a` | `155b5da9ff3dfe21442c534bd22442685a982b28608d36996a445b6fd67c6e2a` |
| `assets/models/sketchfab_bf500546e2874f9ea086ba6abb11357e/textures/Picea_abies_HD_Picea_fol_2_short_Picea_fol_02_short_n_LOD2_Normal.png` | 41930 | `38a51454afa30aee3b677c25b0c3de741779859dc7f4f32e227dad1923131cad` | `38a51454afa30aee3b677c25b0c3de741779859dc7f4f32e227dad1923131cad` |
| `assets/models/sketchfab_bf500546e2874f9ea086ba6abb11357e/textures/Picea_abies_HD_Picea_trunk_cut_01_LOD2_Color.png` | 122427 | `838510f58bc92525b159aee4999714a19680a65ed5036d948e0a27f1dce3bf6a` | `838510f58bc92525b159aee4999714a19680a65ed5036d948e0a27f1dce3bf6a` |
| `assets/models/sketchfab_bf500546e2874f9ea086ba6abb11357e/textures/Picea_abies_HD_Picea_trunk_cut_01_n_LOD2_Normal.png` | 117713 | `a493c70463dc5603b763a3d2c8f40b6e6317dea66cf0f5e4ad7d220f18ccca44` | `a493c70463dc5603b763a3d2c8f40b6e6317dea66cf0f5e4ad7d220f18ccca44` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/LICENSE.txt` | 550 | `b247ccf22123817a0699dd9ba45fc53ee1cffdd9d33aedfebeb5bd83d349f581` | `—` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/master.blend` | 9555701 | `de86b51b4e8f922cd52587ddd4ce6fe408afa0720d62ab5a1cce2a6e7c33ad20` | `—` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_bark_2_Picea_mariana_bark_02_LOD2_Color.png` | 378305 | `de614132505cad7ab201e573b810975bc9e9bdda28c5a9d72ec304f26a1f840e` | `de614132505cad7ab201e573b810975bc9e9bdda28c5a9d72ec304f26a1f840e` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_bark_2_Picea_mariana_bark_02_n_LOD2_Normal.png` | 506816 | `36f723d7a9af6fcd47e6c1fb24a814736ccfa2b7b68821adde82c3f2ee8f7a43` | `36f723d7a9af6fcd47e6c1fb24a814736ccfa2b7b68821adde82c3f2ee8f7a43` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_branch_01_LOD2_Color.png` | 236219 | `df251eadef1c6048df81ff4d5cf91beb9addb00ede5f8e15b0cc2c4a8e86f69c` | `df251eadef1c6048df81ff4d5cf91beb9addb00ede5f8e15b0cc2c4a8e86f69c` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_branch_01_n_LOD2_Normal.png` | 306144 | `7cbfb5fe55569c7677373f4454ce3d91ae3ae2ddf91733763c14250925177166` | `7cbfb5fe55569c7677373f4454ce3d91ae3ae2ddf91733763c14250925177166` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_brch_cut_02_Picea_branch_cut_01_n_LOD2_Normal.png` | 35347 | `fad4f3790a43d6fd583d10ec3acd8a54265fa6c7540f89bdb0766c71c7ced251` | `fad4f3790a43d6fd583d10ec3acd8a54265fa6c7540f89bdb0766c71c7ced251` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_brch_cut_02_Picea_branch_cut_01b_LOD2_Color.png` | 31915 | `277b01ec0ebca5574e6885321087e1cf6ec8d987ef89138cc08db99bc87f99b7` | `277b01ec0ebca5574e6885321087e1cf6ec8d987ef89138cc08db99bc87f99b7` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_brch_dead_Picea_mariana_branch_01_dead_LOD2_Color.png` | 250091 | `a38160259b50d158ccd279142c8bb08ea4b5d5b117cffe0cb78caadcb50c9683` | `a38160259b50d158ccd279142c8bb08ea4b5d5b117cffe0cb78caadcb50c9683` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_brch_dead_Picea_mariana_branch_01_dead_n_LOD2_Normal.png` | 284283 | `3ad6ef111157e9ca0b5a934eb112f9f6ec984d898161fc00c28dba267473e174` | `3ad6ef111157e9ca0b5a934eb112f9f6ec984d898161fc00c28dba267473e174` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_fol_1_Picea_mariana_fol_01_a_LOD2_Transparency.png` | 46168 | `d0031f8a1be72263915f351906f5dfc42cf959fd0bc106a71020164261bf0d73` | `d0031f8a1be72263915f351906f5dfc42cf959fd0bc106a71020164261bf0d73` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_fol_1_Picea_mariana_fol_01_gray_LOD2_Color.png` | 216957 | `76b0e7c6ea31f768001a10b00bc8aa3269a6594c4c6ced993b5e8f63b1d3e2c2` | `76b0e7c6ea31f768001a10b00bc8aa3269a6594c4c6ced993b5e8f63b1d3e2c2` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_fol_1_Picea_mariana_fol_01_n_LOD2_Normal.png` | 316223 | `5fc18f544239e71a5808724031c57fac83754a3c51323e2552a711db9ebe244a` | `5fc18f544239e71a5808724031c57fac83754a3c51323e2552a711db9ebe244a` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_fol_1_dead_Picea_mariana_fol_01_dead_LOD2_Color.png` | 206071 | `77b258a2f68a16681ad326674649490912acb189f0e4cc0cd2b668949cc8db0b` | `77b258a2f68a16681ad326674649490912acb189f0e4cc0cd2b668949cc8db0b` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_fol_1_dead_Picea_mariana_fol_01_dead_a_LOD2_Transparency.png` | 15046 | `10addcf1ccd46b5cf64bf54c04b6a16cd7daa1ae7f4300aa0d859e652c2ceca6` | `10addcf1ccd46b5cf64bf54c04b6a16cd7daa1ae7f4300aa0d859e652c2ceca6` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_fol_1_dead_Picea_mariana_fol_01_dead_n_LOD2_Normal.png` | 241384 | `ecf465236edb1f3bc40e225f7f641459dc2846d1cc682c61e6f44eb31bd2ed96` | `ecf465236edb1f3bc40e225f7f641459dc2846d1cc682c61e6f44eb31bd2ed96` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_fol_1_dying_Picea_mariana_fol_01_dying_LOD2_Color.png` | 222213 | `ad399f1c9faf87350700d2f4cedeb82c04294bfb1e03d36ea2a580190db87a3f` | `ad399f1c9faf87350700d2f4cedeb82c04294bfb1e03d36ea2a580190db87a3f` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_fol_1_dying_Picea_mariana_fol_01_dying_a_LOD2_Transparency.png` | 22833 | `adcaeac635248ad65d2628417394d4dbeadd0c2bbdb8c97ad73008d3404baa1c` | `adcaeac635248ad65d2628417394d4dbeadd0c2bbdb8c97ad73008d3404baa1c` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_fol_1_dying_Picea_mariana_fol_01_dying_n_LOD2_Normal.png` | 302283 | `3ef4047ada4bf3d5e35b1d106ad71c413fb2d04350734233f8b789c3dd43e054` | `3ef4047ada4bf3d5e35b1d106ad71c413fb2d04350734233f8b789c3dd43e054` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_fol_2_long_Picea_mariana_fol_02_long_a_LOD2_Transparency.png` | 15384 | `268491c88873f508a0ddc29b43456a5f7e372fb22f5755eb95c7d594e2928fa5` | `268491c88873f508a0ddc29b43456a5f7e372fb22f5755eb95c7d594e2928fa5` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_fol_2_long_Picea_mariana_fol_02_long_gray_LOD2_Color.png` | 56717 | `950a600d43bfcb6efbbf5891303239c932d63a9f1408c13ab42ec52a69cd1679` | `950a600d43bfcb6efbbf5891303239c932d63a9f1408c13ab42ec52a69cd1679` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_fol_2_long_Picea_mariana_fol_02_long_n_LOD2_Normal.png` | 84653 | `067cf48ee451ec255816ec57bb4028084ce4eb0fe13fd6f60b3ad7885e71e330` | `067cf48ee451ec255816ec57bb4028084ce4eb0fe13fd6f60b3ad7885e71e330` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_fol_2_short_Picea_mariana_fol_02_short_a_LOD2_Transparency.png` | 7800 | `537f2b05b60ba61f120c31f780b09d0b70ce1e3b26fcb58556434c145ba40452` | `537f2b05b60ba61f120c31f780b09d0b70ce1e3b26fcb58556434c145ba40452` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_fol_2_short_Picea_mariana_fol_02_short_gray_LOD2_Color.png` | 26970 | `21ee7624650fc34bc5ecd4fdf86309348442fcb574dc0e5eaa472af33cdbadb6` | `21ee7624650fc34bc5ecd4fdf86309348442fcb574dc0e5eaa472af33cdbadb6` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_fol_2_short_Picea_mariana_fol_02_short_n_LOD2_Normal.png` | 106361 | `8d001d66b7b062906da1000171728ed52f64aff9bd86277ec056d46fdb9ee684` | `8d001d66b7b062906da1000171728ed52f64aff9bd86277ec056d46fdb9ee684` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_fol_2_short_dead_Picea_mariana_fol_02_short_dead_LOD2_Color.png` | 9812 | `9574d29b26f4479a8c760a7f4a1a317b88944b75942b50a51a4b9774e85e51f0` | `9574d29b26f4479a8c760a7f4a1a317b88944b75942b50a51a4b9774e85e51f0` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_fol_2_short_dead_Picea_mariana_fol_02_short_dead_a_LOD2_Transparency.png` | 2001 | `24317ef1abdc02bae40f59a9740fec95f147aaaf47759ffac998e87011caf7f8` | `24317ef1abdc02bae40f59a9740fec95f147aaaf47759ffac998e87011caf7f8` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_fol_2_short_dead_Picea_mariana_fol_02_short_dead_n_LOD2_Normal.png` | 6460 | `7c67173a18fd7da566f00ef068d25b1f0f9916389c43d5452ef9fadf7eb5807c` | `7c67173a18fd7da566f00ef068d25b1f0f9916389c43d5452ef9fadf7eb5807c` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_fol_2_short_dying_Picea_mariana_fol_02_short_dying_LOD2_Color.png` | 31967 | `fb0f12bc89cd9cb3f88557f3892ee5f09da301c8a905914300e81a54439284fb` | `fb0f12bc89cd9cb3f88557f3892ee5f09da301c8a905914300e81a54439284fb` |
| `assets/models/sketchfab_3232c3022f2947b7999de0941ede5653/textures/Picea_mariana_HD_Picea_mariana_trunk_cut_01_n_LOD2_Normal.png` | 132993 | `5bc90ffa0a867a4d5a4b6f02482ae814cc26c3e9caa0cdb8aa610594cd9a2559` | `5bc90ffa0a867a4d5a4b6f02482ae814cc26c3e9caa0cdb8aa610594cd9a2559` |
| `assets/models/sketchfab_7df0631398f443379fa4541e9efc2343/LICENSE.txt` | 547 | `bc5ca8926c15b4c23bab1b21f3d5eb68c89d157555e9c0d86330685742df1eef` | `—` |
| `assets/models/sketchfab_7df0631398f443379fa4541e9efc2343/master.blend` | 7716265 | `5d168bdb69d7afaf168f4f7ce062932633f2a0ad5edefb625316d17ea133a0ef` | `—` |
| `assets/models/sketchfab_7df0631398f443379fa4541e9efc2343/textures/Apple_tree.jpg` | 1386607 | `7506413a061a51fea1ca2474179584c54527a6f246aaf2479b5dfbb410e42715` | `e651799a0b650902fb4fe49808feb332ac709829e3caa1a3b6ee1a6460efa383` |
| `assets/models/sketchfab_7df0631398f443379fa4541e9efc2343/textures/Apple_tree_normal.jpg` | 1537892 | `bdb65b5f3dd5f98cdf73288b4d6b240cc77f4eecbb2c10401bca7af5fe4093ce` | `d783220b1124d753bc04167c373379c29a7228d89c692d32f8d178bbb8499422` |
| `assets/models/sketchfab_7df0631398f443379fa4541e9efc2343/textures/Apple_tree_occlusion.jpg` | 1257413 | `5b949bc60b73ab494ea31ed61007000a13502d7c6b8ab4f45884ced6f93233a1` | `94bcf81b293e2d1b1f2df350484954268679474aefedd2fd1eb648371fb9c9ad` |
| `assets/models/food_apple_01/LICENSE.txt` | 402 | `3097e1bb6dd1952db4a31ef005189d503c2a27a77a871ceca9718baf9fc77daf` | `—` |
| `assets/models/food_apple_01/master.blend` | 584470 | `f90221c14c8d206381f0a448c4ac800e0c845cfe85b21d3efa93f41f44195451` | `—` |
| `assets/models/food_apple_01/textures/food_apple_01_diff_1k.jpg` | 183791 | `b7fc17cfb5013958167bbc089ea4d1c193fb1c61ea4f3c974a9894ed9ba82e8a` | `b7fc17cfb5013958167bbc089ea4d1c193fb1c61ea4f3c974a9894ed9ba82e8a` |
| `assets/models/food_apple_01/textures/food_apple_01_nor_gl_1k.jpg` | 63513 | `c81b1e51ce7e789b65bfde2f046dcb5ba5773b5c6be3e572313be0600c51721b` | `c81b1e51ce7e789b65bfde2f046dcb5ba5773b5c6be3e572313be0600c51721b` |
| `assets/models/food_apple_01/textures/food_apple_01_rough_1k.jpg` | 53123 | `2e5a503af38df7b570b0e81cc9563125f0913b466e01140d4e24ea5ebdbec587` | `2e5a503af38df7b570b0e81cc9563125f0913b466e01140d4e24ea5ebdbec587` |
| `assets/models/grass_medium_01/LICENSE.txt` | 417 | `75e7bb33ccb7b009000723332d8ad1da4b2d0481eac3ae3aa2ac98771659218f` | `—` |
| `assets/models/grass_medium_01/master.blend` | 2690207 | `678b963826ce33e7ec23b0fba6ebf6cb5f82d64e84db6921ea1a504dc83021d4` | `—` |
| `assets/models/grass_medium_01/textures/grass_medium_01_alpha_1k.png` | 648718 | `711a8e49af758d6a6ce1f610db858899a27be19da6d1866bd35c13bc7b8ffeff` | `711a8e49af758d6a6ce1f610db858899a27be19da6d1866bd35c13bc7b8ffeff` |
| `assets/models/grass_medium_01/textures/grass_medium_01_diff_1k.jpg` | 395673 | `71495bd6a11fddcab0aaff38246fea1a7b802a705483f1c7cbca53955daa8050` | `71495bd6a11fddcab0aaff38246fea1a7b802a705483f1c7cbca53955daa8050` |
| `assets/models/grass_medium_01/textures/grass_medium_01_nor_gl_1k.jpg` | 956166 | `cae298d3d1d7ff7c7e210ad8ac772b96706e356f9315a6b04fde373ce01ccf1e` | `cae298d3d1d7ff7c7e210ad8ac772b96706e356f9315a6b04fde373ce01ccf1e` |
| `assets/models/grass_medium_01/textures/grass_medium_01_rough_1k.jpg` | 541262 | `e9a7c5b3cd4c4a3e4eeb016fed248c51796262ee412624e4b9e5b9cc862bd203` | `e9a7c5b3cd4c4a3e4eeb016fed248c51796262ee412624e4b9e5b9cc862bd203` |
| `assets/models/shrub_01/LICENSE.txt` | 391 | `7c865f35d2f1a66727d36cedb07cdb7fb4a02fda74310ae2f94943934ad247f6` | `—` |
| `assets/models/shrub_01/master.blend` | 5522865 | `0897abcbea6aa0389f9e50d86cb217bb3e646bada01eff589ef272964cf69126` | `—` |
| `assets/models/shrub_01/textures/shrub_01_alpha_2k.png` | 297762 | `238e65642075a5317d5a68b509dfef4f369fd6e76b84528bc37eac95587edd24` | `238e65642075a5317d5a68b509dfef4f369fd6e76b84528bc37eac95587edd24` |
| `assets/models/shrub_01/textures/shrub_01_diff_2k.jpg` | 1651989 | `d464a823982b28832a92d3edacc62461adfb3f99117829127e79eb253051e940` | `d464a823982b28832a92d3edacc62461adfb3f99117829127e79eb253051e940` |
| `assets/models/shrub_01/textures/shrub_01_nor_gl_2k.jpg` | 2628947 | `1b2f8631a66ef35c876238d6269f2cd2d1603102b7422f2cc57e3ec9ab209b62` | `1b2f8631a66ef35c876238d6269f2cd2d1603102b7422f2cc57e3ec9ab209b62` |
| `assets/models/shrub_01/textures/shrub_01_rough_2k.jpg` | 906913 | `f1c08a9c3598dcf1cfb42bf6edd07b4f8a71a19f6c418ddc8f447d76245ba985` | `f1c08a9c3598dcf1cfb42bf6edd07b4f8a71a19f6c418ddc8f447d76245ba985` |
| `assets/models/periwinkle_plant/LICENSE.txt` | 404 | `cdbf25121983d9be89a98f60ae50943af3746c9cadc61312936e94f87ce349ab` | `—` |
| `assets/models/periwinkle_plant/master.blend` | 1676952 | `98d499c18bf9108b0205b94e0143895b50f471388972597f299bdb170a3b5409` | `—` |
| `assets/models/periwinkle_plant/textures/periwinkle_plant_diff_1k.jpg` | 349879 | `32d61084e6c07fa3ca8e03b35b347a12717f971efc90e8fe1185931ee2298c56` | `32d61084e6c07fa3ca8e03b35b347a12717f971efc90e8fe1185931ee2298c56` |
| `assets/models/periwinkle_plant/textures/periwinkle_plant_nor_gl_1k.jpg` | 418428 | `36d2464e7500f741500228b955c1fb0f26d954e869bd26f93dd25c0fafc5087d` | `36d2464e7500f741500228b955c1fb0f26d954e869bd26f93dd25c0fafc5087d` |
| `assets/models/periwinkle_plant/textures/periwinkle_plant_opacity_1k.png` | 86094 | `e1dc2746b641606ae2772667c719e2b593b548759a51d86ce093322c22e903de` | `e1dc2746b641606ae2772667c719e2b593b548759a51d86ce093322c22e903de` |
| `assets/models/periwinkle_plant/textures/periwinkle_plant_rough_1k.jpg` | 201230 | `59b6289ed4a3f1ccdf091a1e3d73502bf4a6d1704a68ed8468adae34eef30b50` | `59b6289ed4a3f1ccdf091a1e3d73502bf4a6d1704a68ed8468adae34eef30b50` |
| `assets/models/periwinkle_plant/textures/periwinkle_plant_translucency_1k.jpg` | 359204 | `388abd2765a351c98625cf6f1f76a483aad8590c7ccecf46f9d8ec02fc2d02cf` | `388abd2765a351c98625cf6f1f76a483aad8590c7ccecf46f9d8ec02fc2d02cf` |

### Rozmery masterov

| Kolekcia | Rozsah X / Y / Z v metroch |
|---|---|
| `V04_MASTER_ABIES_LOD0` | -1.97944..2.06908 / -2.08270..1.97816 / 0.00000..9.58616 |
| `V04_MASTER_ABIES_LOD1` | -1.97944..2.06010 / -2.08270..1.97816 / -0.02119..9.58616 |
| `V04_MASTER_ABIES_YOUNG` | -1.42520..1.48974 / -1.49955..1.42428 / 0.00000..9.58616 |
| `V04_MASTER_MARIANA_LOD0` | -0.75686..0.95847 / -0.80107..0.79605 / 0.00000..11.22350 |
| `V04_MASTER_MARIANA_LOD1` | -0.75643..0.95961 / -0.80107..0.79605 / -0.00960..11.22350 |
| `V04_MASTER_ORCHARD` | -3.34087..3.40306 / -3.09943..1.79356 / -0.00006..4.14524 |
| `V04_MASTER_FOOD_APPLE_01_0` | -0.04878..0.04878 / -0.04795..0.04795 / 0.00000..0.08539 |
| `V04_MASTER_GRASS_MEDIUM_01_0` | -0.16348..0.16348 / -0.16583..0.16583 / 0.00000..0.14489 |
| `V04_MASTER_GRASS_MEDIUM_01_1` | -0.08048..0.08048 / -0.07927..0.07927 / 0.00000..0.32255 |
| `V04_MASTER_GRASS_MEDIUM_01_2` | -0.09389..0.09389 / -0.09143..0.09143 / 0.00000..0.17772 |
| `V04_MASTER_SHRUB_01_0` | -0.11540..0.11540 / -0.10287..0.10287 / 0.00000..0.37191 |
| `V04_MASTER_SHRUB_01_1` | -0.09091..0.09091 / -0.08752..0.08752 / 0.00000..0.33233 |
| `V04_MASTER_SHRUB_01_2` | -0.08029..0.08029 / -0.08754..0.08754 / 0.00000..0.29395 |
| `V04_MASTER_PERIWINKLE_PLANT_0` | -0.13038..0.13038 / -0.16037..0.16037 / 0.00000..0.39726 |
| `V04_MASTER_PERIWINKLE_PLANT_1` | -0.08373..0.08373 / -0.07328..0.07328 / 0.00000..0.29996 |
| `V04_MASTER_PERIWINKLE_PLANT_2` | -0.05555..0.05555 / -0.07045..0.07045 / 0.00000..0.20589 |

## Trávnik a lúka v05

Doplnené 16. 11. 2026: [ambientCG Grass005](https://ambientcg.com/view?id=Grass005),
[CC0](https://docs.ambientcg.com/license/). Oficiálne [API](https://ambientcg.com/api/v2/full_json?id=Grass005&include=downloadData) uvádza `creationMethod: PBRProcedural`; nejde o tvrdenie o overenom fotoskene.

Finálna voľba je **1K-JPG**: samostatný 2K render prekročil cieľ pamäte.
Zachováva rovnakú geometriu listov, mapové kanály, UV mierku a shaderové nastavenia.
[1K ZIP](https://ambientcg.com/get?file=Grass005_1K-JPG.zip) má 10 442 657 B; overili sa ZIP CRC a serverový SHA-1 `88dd838d26fddf31925ccb8c0ddf873e6c71f227`.
SHA-256 archívu je `58a7fb7f32c44a86879483325b62781d04e0ab8f70b0f70ede36c8f1726f8a22`.

| Súbor | Úloha / farebný priestor | Rozlíšenie | Bajty | SHA-256 |
|---|---|---|---:|---|
| `assets/textures/grass/Grass005/Grass005_1K-JPG_Color.jpg` | farba / sRGB | 1024 × 1024 | 1875015 | `5fd8edc1a04e2b9b093229dd0ec41f29668dda9fc698f6610b12cdd83b7690cb` |
| `assets/textures/grass/Grass005/Grass005_1K-JPG_Roughness.jpg` | drsnosť / Non-Color | 1024 × 1024 | 851896 | `04ca3a66eee6105cac9754ac773ffd4ee63ca2222984554c4c04b0cdca80da26` |
| `assets/textures/grass/Grass005/Grass005_1K-JPG_NormalGL.jpg` | OpenGL normála / Non-Color | 1024 × 1024 | 2137845 | `f89e3a1701511d379a9772774ec6b9d7b7ccf3e944fdcc2b98c09dee4cfd804f` |

Zdrojové JPG sú neupravené, zabalené a majú relatívne cesty `//../assets/textures/grass/Grass005/...`.
Mierka 1 × 1 m je vizuálny predpoklad; API neuvádza merané fyzické rozmery.
Oba nové podkladové materiály používajú svetové XY UV, spoločné miešanie fáz
(0,317; 0,419), pomalú masku, drsnosť 0,80–0,98 a OpenGL normálu s intenzitou 0,35.
Geometrický displacement sa nepoužíva.

Pôvodne overený [2K ZIP](https://ambientcg.com/get?file=Grass005_2K-JPG.zip) má
39 523 019 B a SHA-256 `89183d8dceabc3c23a26978f426e1662143dd2f84f1dc3586a1592d101e5234b`.
Jeho mapy, archív a 2K kandidáti zostávajú v gitignored `work/` ako meracia evidencia.
Do projektu patria iba tri finálne 1K mapy. Modely, USD a ďalšie súbory archívov
sa neimportovali.

Krátke 4–10 cm listy trávnika sú nová procedurálna geometria. Lúčne 25–65 cm
skupiny vychádzajú z kópií `grass_medium_01` od Rob Tuytel a Rico Cilliers
(Poly Haven CC0), s jemnými procedurálnymi steblami/hlávkami a vlastnými
zelenými/suchými materiálmi. Na nerovnom podklade sa samostatne usádzajú
zdieľané časti trsov; žiadna normalizovaná v04 knižnica sa nemení.
Pôvodné CC BY 4.0 kredity PlantCatalog a Lassi Kaukonen uvedené vyššie zostávajú
platné a patria aj k šíreným renderom. Čierny smrek je zvolené vizuálne aktívum.


## Chodník v07 — štrkový povrch

Pridané 17. 11. 2026. [Gravel Ground 01](https://polyhaven.com/a/gravel_ground_01), autor Rob Tuytel, [CC0](https://polyhaven.com/license). Oficiálna stránka uvádza šírku opakovania 3 m; vybrané JPG majú 2048 × 2048 px. Súbory zostávajú neupravené.

| Súbor | Úloha / farebný priestor | Bajty | SHA-256 | Zdroj |
|---|---|---:|---|---|
| `assets/textures/gravel/gravel_ground_01/gravel_ground_01_diff_2k.jpg` | diffuse / sRGB | 3823037 | `b626c16301208b67eba976ad71860d98fd6fe82ae1c87d9d27692e70c1089cd2` | [JPG](https://dl.polyhaven.org/file/ph-assets/Textures/jpg/2k/gravel_ground_01/gravel_ground_01_diff_2k.jpg) |
| `assets/textures/gravel/gravel_ground_01/gravel_ground_01_rough_2k.jpg` | roughness / Non-Color | 1582667 | `18d0214f0b5b916d2439a24eef32ac82574f3fc34d1bef02fc92abfbf3d69fce` | [JPG](https://dl.polyhaven.org/file/ph-assets/Textures/jpg/2k/gravel_ground_01/gravel_ground_01_rough_2k.jpg) |
| `assets/textures/gravel/gravel_ground_01/gravel_ground_01_nor_gl_2k.jpg` | NormalGL / Non-Color | 5481185 | `571eb16b158eb8581ab5348579a26f42c3c711536941f347074795e79afe6329` | [JPG](https://dl.polyhaven.org/file/ph-assets/Textures/jpg/2k/gravel_ground_01/gravel_ground_01_nor_gl_2k.jpg) |

Spolu 10 886 889 bajtov. Použité mapy sa balia do v07 s relatívnymi cestami. UV opakovanie je 3 × 3 m; farba má saturáciu 0,62 a hodnotu 0,82, drsnosť 0,78–0,94, OpenGL normála intenzitu 0,28. Dve rovnako mierkované fázy majú posun (0,317; 0,419) a pomalé miešanie. Geometrický displacement sa nepoužíva. Pôvodné kredity a knižnice ostávajú platné. Lokálny pôdny lem používa vlastnú kópiu shaderu lúky; pôvodný materiál sa nemení. Tri drobné predlohy kamienkov a tri predlohy ihličia sú procedurálna geometria v07, bez ďalšieho stiahnutého aktíva.
