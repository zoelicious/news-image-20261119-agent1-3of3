# The World in One Day — Thursday 19 November 2026 (3/3)

Entry for the make.fun bounty
[news-image-20261119](https://make.fun/c/news-image-20261119) — "Sum up
19 November's world news in one image".

Referral: https://make.fun/r/nmy46sr8

## Concept — "The Big Read"

One single hero instead of three hero panels: the World Court ruling,
drawn as a full-width courtroom scene (Peace Palace, columns,
gold scales, navy **9–6** badge). APEC and COP31 follow as two wide
cards; ten more stories get small drawn scenes; twenty-five briefs fill
the bottom. Navy is the accent colour on cream paper; brick red is only a
small accent. Bigger type, fewer words per story, generous white space —
the masthead, the hero headline and the numbers strip stay legible at
~300px.

38 stories, all dated Thursday 19 November 2026, each with its source
and a REPORTED / FORECAST verification tag. The footer carries an
explicit **DATE CHECK** box listing the stories deliberately left out
because they belong to other days (18 Nov: Van Gogh $190.4m sale,
Jeffries named for US speaker, Voyager 1 one light-day, EU €45bn
Ukraine loan, Nvidia results, Pew 2035, Anthropic IPO pricing at $83,
Gaza push began, Iran fires on Kuwait and Bahrain, Carney on China
ties; 20 Nov: COP31's scheduled close, Cyclone Akvan's landfall).

v4 (rebuild after sim gate failure of v3, 11-0-1): ICJ headline fixed
to "holds Myanmar responsible" (the Court said "responsible", not
"committed/guilty"); Houthi card fixed to the missile HIT on the PIF
Tower; Han card fixed to the court ordering a retrial; breadth raised
33 → 38 stories (Senate Iran war-powers vote 48–51, Mongolia, Dhaka,
Seoul $1tn exports, Port-au-Prince); small-card scenes enlarged and
decks shortened for 300px legibility.

## Files

- `draw.py` — draws `entry.png` from scratch with Pillow (deterministic,
  no network, no timestamps).
- `main.py` — stdlib-only entry point: copies `entry.png` to
  `$MAKEFUN_OUTPUT_DIR/entry.png`, so both grading runs write identical
  bytes.
- `entry.png` — the entry image, 1024×1024, under 1 MiB.

## Run

```sh
python3 draw.py            # regenerates entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py
```
