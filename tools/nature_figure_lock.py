"""Pinned source metadata for the upstream nature-figure Skill."""

from __future__ import annotations

PINNED_COMMIT = "1930963cbc004da9ac8e3af7944d4f0a3488d3e1"
SOURCE_REPOSITORY = "https://github.com/lth0/codexSkill"
ARCHIVE_URL = f"https://codeload.github.com/lth0/codexSkill/zip/{PINNED_COMMIT}"

_HASH_ITEMS = (
    (".gitignore", "cf237c7aff44efbe6e502e645c3e06da03a69d7bdeb43392108ef3348143417e"),
    (
        "assets/chart-atlas/atlas-01-bar-charts.png",
        "4a0e3040bbdbfe5ec48b66515f719f83ad7304fadb2e56432cd3e8f7ccbabd65",
    ),
    (
        "assets/chart-atlas/atlas-02-line-trends.png",
        "9a8189149180a68679738bc4be152ee40b17d71261d71b3759d315a7169da0d9",
    ),
    (
        "assets/chart-atlas/atlas-03-heatmaps.png",
        "40dd7c7c14c45b45cc22ee23e19f2dc1901f38b26a1fb4b0f26a30dbd10c0423",
    ),
    (
        "assets/chart-atlas/atlas-04-scatter-bubble.png",
        "1bbfbc38a3f246e4fd7c59b9ed1003ddbc7280ee160b7c38abf8d410b27fe6f8",
    ),
    (
        "assets/chart-atlas/atlas-05-radar-polar.png",
        "e7fa7d98cd4f5263f5550d7ac8824e60071c20b2927aef52ac6d18d62fd29ffa",
    ),
    (
        "assets/chart-atlas/atlas-06-distributions.png",
        "a1fe533d07dae36d11c997577ded61adb16bf5d4dd5c0dee2ff92ae570f0f01e",
    ),
    (
        "assets/chart-atlas/atlas-07-forest-interval.png",
        "dc61a5257eae4748348c72c51f2e70e59979c6892f52dadf7bb4ba6f8b98b00b",
    ),
    (
        "assets/chart-atlas/atlas-08-area-stacked.png",
        "350c25e427d945dee5fd98316eb6ebe307304b9d187d954a88c05852d664a60b",
    ),
    (
        "assets/chart-atlas/atlas-09-image-plates.png",
        "bbc8c0b8708d42465e57cb7c56b4d2ecfbaa63340a5a6dfefbcb51189cd1a995",
    ),
    (
        "assets/chart-atlas/atlas-10-network-matrix.png",
        "cd384abe10aa86bd310c1288a42f33735cb555c267bddae1ecd262905a7a1de5",
    ),
    (
        "assets/gallery/fig1-material-mechanism-rich.png",
        "2e0706fae3256e1de2388f8605f35b9b6ac23cfc397161a952f34cc5fa2f2192",
    ),
    (
        "assets/gallery/fig2-spatial-imaging-rich.png",
        "90081b3f778b9ede2dba41c60b6abf0c28a239060c69428344539529cd7f3257",
    ),
    (
        "assets/gallery/fig3-in-vivo-efficacy-rich.png",
        "25d6fc50f5808104a7cb19f4795cea4229fbc6159fa7509f716a94f7c160a033",
    ),
    (
        "assets/gallery/fig4-single-cell-systems-rich.png",
        "999edb06b942f988a51b11f947845e42e4c346b2f9e5d5a6425def9e43bb69d1",
    ),
    (
        "assets/gallery/fig5-validation-perturbation-rich.png",
        "245ad31f97b2054628987444e44d6a007f352f65ae6254189f5ed8ba9b0301c6",
    ),
    ("evals/evals.json", "c5d4c7b8c64ee251771262dff2a50d346054b4f871116f4b119bcf9c707c697c"),
    ("README.md", "249bfd26f4669587dce429ffbe03f1bc000de6736fa39a8eb2fa1b8da0d1c241"),
    ("references/api.md", "4d4f47ab46d082c4d1f2065058dd4756302a7d0770929845a635fab1fdddb71d"),
    (
        "references/backend-selection.md",
        "f30b3e5c9293e8732c6de27c2f695284d3267ac5f4ecf21d8d5209020eb2e052",
    ),
    (
        "references/chart-types.md",
        "585b5e59c0a528e020750df6b77914759eaa285f8a2a025d3810e40a8637c2ab",
    ),
    (
        "references/common-patterns.md",
        "a2f9d839d4284dc2a8dcac0e5682446db037ff197aa2b4b5e995128eeadf6a1e",
    ),
    (
        "references/design-theory.md",
        "0a7b3a8a964635fa1c7a59d82640e0adb31a6e9845beae77bc6e87503f8597c1",
    ),
    (
        "references/figure-contract.md",
        "d989b4ebdb3aeab14c09e261980756abe72a67bc5eb866e1b91cdaac9c5d5201",
    ),
    (
        "references/nature-2026-observations.md",
        "e4f7800316740297ae3573b2f1830a2d150e3e306546144f6c0547806431c307",
    ),
    (
        "references/qa-contract.md",
        "5323f234fa5319784ce4b06e4eba1d242ba39a72ce83198f9e2ba126eb500339",
    ),
    (
        "references/r-template-index.md",
        "0ebbbd4171896b61639d7969a010401d0aa257bafb99783026a1ba32c91ce19e",
    ),
    (
        "references/r-workflow.md",
        "67ca5126e54b22373a6646c7f7c23c892ef237174092a2b5c94edbd9b25ead5e",
    ),
    (
        "references/tutorials.md",
        "7f9232dab5f1b10dd5d5f93f4c9cde2fe70dd514a9c8cf490059366391b45670",
    ),
    ("SKILL.md", "b4fd8daf9b5b4fa8b048e89234c9afadcca25aa2ee696521380671b286bd5f5f"),
)

EXPECTED_HASHES: dict[str, str] = dict(_HASH_ITEMS)

EXPECTED_FILES = tuple(sorted(EXPECTED_HASHES))
DEFAULT_REFERENCES = (
    "SKILL.md",
    "references/figure-contract.md",
    "references/common-patterns.md",
    "references/qa-contract.md",
)
