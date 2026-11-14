"""'Guess which altered princess this is!' questions for the 9 cut-out images public/img/disney/altered-01..09.png.
These are ALWAYS included in the Disney pool (the build reserves room for them).
>>> IMAGE_TO_PRINCESS is the one place to fix if an image is matched to the wrong princess. <<<"""
from ..common import *
from .. import svgkit as K

IMAGE_TO_PRINCESS = {1: "Cinderella", 2: "Ariel", 3: "Rapunzel", 4: "Mulan", 5: "Pocahontas", 6: "Aurora", 7: "Tiana", 8: "Belle", 9: "Merida"}
# dress colour of the artwork (None = skip colour question): fixed by what is visible in each image
DRESS = {1: "blue", 2: "green", 3: "purple", 4: "red", 5: "orange", 6: "pink", 7: "mint"}
HEX = {**K.COLORS, "mint": "#8CD1B0"}
COLOR_POOL = ["red", "blue", "yellow", "orange", "purple", "pink", "brown", "black", "white", "gray"]

ALL = ["Snow White", "Cinderella", "Aurora", "Ariel", "Belle", "Jasmine", "Pocahontas", "Mulan", "Tiana", "Rapunzel", "Merida", "Moana", "Raya", "Anna", "Elsa"]
INFO = {  # movie, year, studio, villain, sidekick(s)
    "Cinderella": ("Cinderella", 1950, "Walt Disney Animation Studios", "Lady Tremaine", "Gus and Jaq"),
    "Ariel": ("The Little Mermaid", 1989, "Walt Disney Animation Studios", "Ursula", "Flounder"),
    "Rapunzel": ("Tangled", 2010, "Walt Disney Animation Studios", "Mother Gothel", "Pascal"),
    "Mulan": ("Mulan", 1998, "Walt Disney Animation Studios", "Shan Yu", "Mushu"),
    "Pocahontas": ("Pocahontas", 1995, "Walt Disney Animation Studios", "Governor Ratcliffe", "Meeko"),
    "Aurora": ("Sleeping Beauty", 1959, "Walt Disney Animation Studios", "Maleficent", "Flora, Fauna and Merryweather"),
    "Tiana": ("The Princess and the Frog", 2009, "Walt Disney Animation Studios", "Dr. Facilier", "Louis"),
    "Belle": ("Beauty and the Beast", 1991, "Walt Disney Animation Studios", "Gaston", "Lumière"),
    "Merida": ("Brave", 2012, "Pixar Animation Studios", "Mor'du", "Angus"),
}
SOURCE = {"Cinderella": "Charles Perrault's fairy tale", "Ariel": "Hans Christian Andersen's fairy tale", "Rapunzel": "A Brothers Grimm fairy tale",
          "Mulan": "A Chinese legend, the Ballad of Mulan", "Belle": "A French fairy tale by Jeanne-Marie Leprince de Beaumont"}
SOURCE_POOL = ["A Greek myth", "An Arabian Nights story", "A Norse saga", "Aesop's fables", "A Roman legend", "An English nursery rhyme"]
STUDIOS = ["Walt Disney Animation Studios", "Pixar Animation Studios", "DreamWorks Animation", "Illumination"]
ALL_MOVIES = [v[0] for v in INFO.values()] + ["Aladdin", "Snow White and the Seven Dwarfs", "Moana", "Frozen", "Raya and the Last Dragon"]
ALL_VILLAINS = [v[3] for v in INFO.values()] + ["Jafar", "The Evil Queen", "Hades", "Scar", "Captain Hook", "Cruella de Vil"]
ALL_SIDEKICKS = [v[4] for v in INFO.values()] + ["Abu", "Olaf", "Pua", "Sisu", "Genie"]


def build(band):
    r = rng_for("disney-altered", band)
    out = []
    for i, who in IMAGE_TO_PRINCESS.items():
        v = img(f"disney/altered-{i:02d}.png")
        movie, year, studio, villain, side = INFO[who]
        others = [n for n in ALL if n != who]
        if band == "2-5":
            out += [mc(r, "Guess which altered princess this is!", who, others, v=v),
                    mc(r, "Which princess is this?", who, others, v=v),
                    mc(r, "Who is dressed up here?", who, others, v=v)]
            if i in DRESS:
                out.append(mc(r, "What color is her dress?", K.swatch(HEX[DRESS[i]]), [K.swatch(HEX[c]) for c in COLOR_POOL if c != DRESS[i]], v=v, ct="svg"))
        elif band == "6-10":
            out += [mc(r, "Guess which altered princess this is!", who, others, v=v),
                    mc(r, "This princess got a makeover! Who is she?", who, others, v=v),
                    mc(r, "Which movie is this altered princess from?", movie, [m for m in ALL_MOVIES if m != movie], v=v),
                    mc(r, "Which sidekick goes with this altered princess?", side, [s for s in ALL_SIDEKICKS if s != side], v=v),
                    mc(r, "Who is the villain in her story?", villain, [x for x in ALL_VILLAINS if x != villain], v=v)]
            if i in DRESS:
                out.append(mc(r, "What color is this princess's new dress?", DRESS[i] if DRESS[i] != "mint" else "mint green", [c for c in COLOR_POOL], v=v))
        else:
            out += [mc(r, "Guess which altered princess this is!", who, others, v=v),
                    mc(r, "Even with a new look, you should know her. Who is she?", who, others, v=v),
                    mc(r, "Which movie is this altered princess from?", movie, [m for m in ALL_MOVIES if m != movie], v=v),
                    num_choices(r, "In what year did her movie come out?", year, v=v, spread=12, lo=1937),
                    mc(r, "Who is the villain in her story?", villain, [x for x in ALL_VILLAINS if x != villain], v=v),
                    mc(r, "Which studio made her movie?", studio, [s for s in STUDIOS if s != studio], v=v)]
            if who in SOURCE:
                out.append(mc(r, "Her story was inspired by…", SOURCE[who], [x for k, x in SOURCE.items() if k != who] + SOURCE_POOL, v=v))
    return out
