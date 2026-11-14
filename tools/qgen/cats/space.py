from ..common import *

META = {"id": "space", "name": "Space", "icon": "🚀"}


def P(s): return s.split("|")


def rows(r, rs, **kw):
    return [mc(r, q, a, P(w), **kw) for q, a, w in rs]


PLANETS = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
ORD = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth"]
# diameter in thousand km
SIZE = {"Mercury": 4.9, "Venus": 12.1, "Earth": 12.7, "Mars": 6.8, "Jupiter": 139.8, "Saturn": 116.5, "Uranus": 50.7, "Neptune": 49.2}
PHASES = [("🌑", "New Moon"), ("🌒", "Waxing Crescent"), ("🌓", "First Quarter"), ("🌔", "Waxing Gibbous"),
          ("🌕", "Full Moon"), ("🌖", "Waning Gibbous"), ("🌗", "Last Quarter"), ("🌘", "Waning Crescent")]

# ---------------------------------------------------------------- 2-5
KIDS = [("🚀", "Rocket"), ("🛸", "Flying saucer"), ("🌞", "Sun"), ("🌙", "Moon"), ("⭐", "Star"), ("🌍", "Earth"),
        ("🪐", "Ringed planet"), ("☄️", "Comet"), ("🌌", "Galaxy"), ("🛰️", "Satellite"), ("👽", "Alien"),
        ("🔭", "Telescope"), ("🌠", "Shooting star"), ("🧑‍🚀", "Astronaut")]
STARLIKE = {"Sun", "Star", "Shooting star"}
PROPER = {"Sun", "Moon", "Earth"}


def nm(n): return "the " + (n if n in PROPER else n.lower())


def kids():
    r = rng_for("space", "2-5")
    out = []
    for e, n in KIDS:
        bad = STARLIKE if n in STARLIKE else set()
        names = [x for _, x in KIDS if x != n and x not in bad]
        emos = [x for x, y in KIDS if y != n and y not in bad]
        for q in ["What is this?", "Can you name this?", "What do you see?"]:
            out.append(mc(r, q, n, names, v=emoji(e)))
        for q in ["Find {}!", "Tap {}!", "Where is {}?", "Which one is {}?", "Show me {}!"]:
            out.append(mc(r, q.format(nm(n)), e, emos, ct="emoji"))
    cnt = ["⭐", "🚀", "🌙", "🪐", "🛸", "☄️", "👽", "🌞", "🌍", "🛰️", "🔭", "🌠"]
    for e in cnt:
        for n in range(1, 6):
            for q in ["How many do you see?", "Count them!"]:
                out.append(num_choices(r, q, n, v=emoji(" ".join([e] * n)), spread=2, lo=1))
    E = lambda q, a, w: mc(r, q, a, P(w), ct="emoji")
    out += [
        E("What do astronauts ride?", "🚀", "🚗|🚲|🚜|🚂|🚢"),
        E("Which one flies to space?", "🚀", "🚗|🚲|🚜|🚢|🚂"),
        E("What goes zoom up to space?", "🚀", "🚗|🚲|🚜|🚢|🐎"),
        E("What do we live on?", "🌍", "🌞|🌙|⭐|🪐|☄️"),
        E("Which one is hot?", "🌞", "🌙|❄️|🧊|☁️|⛄"),
        E("What is bright in the day?", "🌞", "🌠|🌌|👽|🛸|🔭"),
        E("What twinkles in the night?", "⭐", "🌍|🪐|🚀|🛸|🌈"),
        E("What has a long tail?", "☄️", "🌞|🌙|🪐|🌍|⭐"),
        E("Which planet has rings?", "🪐", "🌞|🌙|🌍|☄️|⭐"),
        E("What helps us see stars?", "🔭", "🧸|🍎|🔨|🚲|🎈"),
        E("What do aliens ride in?", "🛸", "🚗|🚲|🚜|🚂|🚢"),
        E("Who goes in a rocket?", "🧑‍🚀", "🐶|🐱|🐮|🐷|🐔"),
        E("What shines at night?", "🌙", "🌞|🌈|🚜|🚗|🍎"),
        E("What do you wish on?", "🌠", "🚗|🍎|🚲|🧸|🎈"),
        mc(r, "What color is the Sun?", "Yellow", ["Blue", "Green", "Purple", "Pink"]),
        mc(r, "What color is Earth's sky?", "Blue", ["Pink", "Green", "Purple", "Brown"]),
        mc(r, "Where do astronauts go?", "Space", ["The farm", "The zoo", "The beach", "The shop"]),
        mc(r, "Which way do rockets go?", "Up", ["Down", "Under", "Left", "Round"]),
        mc(r, "When can we see the stars?", "At night", ["At lunch", "At noon", "At breakfast", "In the bath"]),
        mc(r, "When does the Sun shine?", "In the day", ["At midnight", "At bedtime", "When it is dark", "At night"]),
    ]
    return out


# ---------------------------------------------------------------- 6-10
def clear_cmp(r):
    """Which planet is wider / narrower than X (clearly separated sizes)."""
    out = []
    for x in PLANETS:
        bigger = [p for p in PLANETS if SIZE[p] > SIZE[x] * 1.2]
        smaller = [p for p in PLANETS if SIZE[p] < SIZE[x]]
        larger_any = [p for p in PLANETS if SIZE[p] > SIZE[x]]
        narrow = [p for p in PLANETS if SIZE[p] < SIZE[x] / 1.2]
        if bigger and len(smaller) >= 3:
            out.append(mc(r, f"Which planet is wider than {x}?", r.choice(bigger), smaller))
        if narrow and len(larger_any) >= 3:
            out.append(mc(r, f"Which planet is narrower than {x}?", r.choice(narrow), larger_any))
    return out


def mid():
    r = rng_for("space", "6-10")
    out = []
    for i, p in enumerate(PLANETS):
        out.append(mc(r, f"Which planet is {ORD[i]} from the Sun?", p, PLANETS))
        out.append(mc(r, f"What number planet from the Sun is {p}?", str(i + 1), [str(k) for k in range(1, 9)]))
        out.append(mc(r, f"How many planets are closer to the Sun than {p}?", str(i), [str(k) for k in range(0, 8)]))
        out.append(mc(r, f"How many planets are farther from the Sun than {p}?", str(7 - i), [str(k) for k in range(0, 8)]))
        if i < 7:
            out.append(mc(r, f"Which planet comes right after {p}, going outward?", PLANETS[i + 1], PLANETS))
        if i > 0:
            out.append(mc(r, f"Which planet comes right before {p}, going outward?", PLANETS[i - 1], PLANETS))
        if 0 < i < 7:
            out.append(mc(r, f"Which planet is between {PLANETS[i - 1]} and {PLANETS[i + 1]}?", p, PLANETS))
        closer, farther = PLANETS[:i], PLANETS[i + 1:]
        if closer and len(farther) >= 3:
            out.append(mc(r, f"Which planet is closer to the Sun than {p}?", r.choice(closer), farther))
        if farther and len(closer) >= 3:
            out.append(mc(r, f"Which planet is farther from the Sun than {p}?", r.choice(farther), closer))
        pool = [x for x in ["Earth", "The Moon", "Jupiter", "Mars", "Venus"] if x != p]
        out.append(mc(r, f"What does {p} orbit?", "The Sun", pool))
    out += clear_cmp(r)
    clue = [
        ("Which planet is closest to the Sun?", "Mercury"), ("Which planet is the smallest?", "Mercury"),
        ("Which planet is the hottest?", "Venus"), ("Which planet is known as the Red Planet?", "Mars"),
        ("Which planet is the biggest?", "Jupiter"), ("Which planet is best known for its big, bright rings?", "Saturn"),
        ("Which planet is farthest from the Sun?", "Neptune"), ("Which planet do we live on?", "Earth"),
        ("Which planet is named after the Roman god of war?", "Mars"),
        ("Which planet is named after the messenger of the Roman gods?", "Mercury"),
        ("Which planet is named after the Roman goddess of love and beauty?", "Venus"),
        ("Which planet is named after the king of the Roman gods?", "Jupiter"),
        ("Which planet is named after the Roman god of farming?", "Saturn"),
        ("Which planet is named after the Roman god of the sea?", "Neptune"),
        ("Which planet is named after the Greek god of the sky?", "Uranus"),
        ("Which planet has a giant storm called the Great Red Spot?", "Jupiter"),
        ("Which planet is tilted so much that it spins on its side?", "Uranus"),
        ("Which planet has the fastest winds in the solar system?", "Neptune"),
        ("Which planet has oceans of liquid water on its surface?", "Earth"),
        ("Which planet is sometimes called Earth's sister planet?", "Venus"),
        ("Which planet has a giant volcano called Olympus Mons?", "Mars"),
        ("Which planet has the shortest day, about 10 hours?", "Jupiter"),
        ("Which planet is so light it would float in water?", "Saturn"),
        ("Which planet has two small moons, Phobos and Deimos?", "Mars"),
        ("Which planet do the rovers Curiosity and Perseverance explore?", "Mars"),
        ("Which planet takes about 165 Earth years to orbit the Sun?", "Neptune"),
    ]
    for q, a in clue:
        out.append(mc(r, q, a, PLANETS))
    # moon phases
    for e, n in PHASES:
        out.append(mc(r, "Which moon phase is this?", n, [x for _, x in PHASES], v=emoji(e)))
        out.append(mc(r, f"Which picture shows the {n}?", e, [x for x, _ in PHASES], ct="emoji"))
        out.append(mc(r, f"Tap the {n}!", e, [x for x, _ in PHASES], ct="emoji"))
    for i, (e, n) in enumerate(PHASES):
        nx, pv = PHASES[(i + 1) % 8][1], PHASES[i - 1][1]
        out.append(mc(r, f"Which moon phase comes right after the {n}?", nx, [x for _, x in PHASES]))
        out.append(mc(r, f"Which moon phase comes right before the {n}?", pv, [x for _, x in PHASES]))
    out += rows(r, [
        ("When the Moon is waxing, what is it doing?", "Showing more lit part each night", "Showing less lit part each night|Getting closer to Earth|Changing color|Standing still"),
        ("When the Moon is waning, what is it doing?", "Showing less lit part each night", "Showing more lit part each night|Getting farther from Earth|Changing color|Standing still"),
        ("Which moon phase looks completely dark?", "New Moon", "Full Moon|First Quarter|Waxing Gibbous|Last Quarter"),
        ("Which moon phase shows the whole face lit?", "Full Moon", "New Moon|First Quarter|Waning Crescent|Last Quarter"),
        ("About how long is the cycle of Moon phases?", "About one month", "About one day|About one week|About one year|About one hour"),
        ("What do we call a Moon that is lit on just a thin slice?", "A crescent", "A gibbous|A full Moon|A quarter|An eclipse"),
    ])
    # object types
    kinds = [("the Sun", "Star"), ("Sirius", "Star"), ("Polaris", "Star"), ("Earth's Moon", "Moon"), ("Titan", "Moon"), ("Europa", "Moon"),
             ("Mars", "Planet"), ("Jupiter", "Planet"), ("Saturn", "Planet"), ("Pluto", "Dwarf planet"), ("Ceres", "Dwarf planet"),
             ("Halley's Comet", "Comet"), ("The Milky Way", "Galaxy"), ("Andromeda", "Galaxy")]
    for o, k in kinds:
        bad = {k}
        if k == "Dwarf planet": bad |= {"Planet"}
        pool = [x for x in ["Star", "Planet", "Moon", "Comet", "Galaxy", "Dwarf planet"] if x not in bad]
        if k == "Planet": pool = [x for x in pool if x != "Dwarf planet"]
        out.append(mc(r, f"What kind of space object is {o}?", k, pool))
    out += rows(r, [
        ("What force keeps us on the ground?", "Gravity", "Magnetism|Friction|Wind|Sunlight"),
        ("What do we call a person who travels into space?", "Astronaut", "Pilot|Captain|Driver|Engineer"),
        ("What do astronauts wear outside their spacecraft?", "A spacesuit", "A swimsuit|A raincoat|A snowsuit|A uniform of feathers"),
        ("What is the ISS?", "A space station orbiting Earth", "A giant telescope on the Moon|A rocket launch pad|A moon of Jupiter|A kind of comet"),
        ("Who was the first person to walk on the Moon?", "Neil Armstrong", "Yuri Gagarin|John Glenn|Sally Ride|Valentina Tereshkova"),
        ("What is the name of our galaxy?", "The Milky Way", "Andromeda|The Big Dipper|Orion|The Sun"),
        ("What do we call a group of stars that makes a picture?", "A constellation", "A galaxy|A comet|A crater|An orbit"),
        ("What is a shooting star really?", "A meteor", "A comet|A tiny star|A planet|A satellite"),
        ("What is the Sun?", "A star", "A planet|A moon|A comet|A galaxy"),
        ("What do we call a bowl-shaped hole on the Moon?", "A crater", "A canyon|A valley|A volcano|A lake"),
        ("What do we call the path of an object around a planet or star?", "An orbit", "A tunnel|A bridge|A highway|A wave"),
        ("Which star is closest to Earth?", "The Sun", "Sirius|The North Star|Betelgeuse|Rigel"),
        ("What gives the Moon its glow?", "Reflected sunlight", "Its own fire|Lightning|Heat from Earth|Light bulbs"),
        ("How long does Earth take to go around the Sun?", "One year", "One day|One month|One week|One hour"),
        ("How long does Earth take to spin around once?", "One day", "One year|One month|One hour|One week"),
        ("About how long does the Moon take to orbit Earth?", "About one month", "One day|One year|One hour|One week"),
        ("What causes day and night on Earth?", "Earth spinning", "The Moon moving|Clouds|The Sun going round Earth|Wind"),
        ("On the Moon, you would weigh...", "Less than on Earth", "More than on Earth|The same as on Earth|Twice as much|A hundred times more"),
        ("Which of these is a dwarf planet?", "Pluto", "Mars|Titan|Sirius|Venus"),
        ("What do we call it when the Moon blocks the Sun?", "A solar eclipse", "A lunar eclipse|A comet|A sunrise|A meteor shower"),
        ("What do we call it when Earth's shadow falls on the Moon?", "A lunar eclipse", "A solar eclipse|A meteor shower|A sunset|A comet"),
        ("What does a telescope help us do?", "See faraway things", "Hear sounds|Fly|Measure weight|Taste food"),
        ("What was the first satellite sent to space?", "Sputnik 1", "Hubble|Voyager|Apollo 11|Curiosity"),
        ("Who was the first person in space?", "Yuri Gagarin", "Neil Armstrong|John Glenn|Buzz Aldrin|Sally Ride"),
        ("Which animal was the first to orbit Earth, in 1957?", "A dog named Laika", "A monkey|A cat|A rabbit|A mouse"),
        ("What does a rocket need to lift off?", "Powerful engines and fuel", "Wings and a tail|Wheels|Sails|Pedals"),
        ("What do we call a vehicle that explores a planet's surface?", "A rover", "A satellite|A telescope|A comet|A moon"),
        ("What is the Sun mostly made of?", "Hydrogen and helium", "Rock and metal|Ice|Liquid water|Sand"),
        ("Which is the biggest object in our solar system?", "The Sun", "Jupiter|Earth|The Moon|Saturn"),
        ("What is a comet mostly made of?", "Ice, dust and rock", "Pure iron|Liquid water|Solid gold|Fire"),
        ("Where is the main asteroid belt?", "Between Mars and Jupiter", "Between Venus and Earth|Between Saturn and Uranus|Around the Moon|Beyond Neptune"),
        ("How many planets are in our solar system?", "8", "6|7|9|10"),
        ("How many moons does Earth have?", "1", "0|2|3|4"),
        ("What is the Great Red Spot?", "A giant storm on Jupiter", "A volcano on Mars|A crater on the Moon|A sea on Earth|A star"),
        ("What is the name of NASA's first crewed Moon landing mission?", "Apollo 11", "Apollo 1|Voyager 1|Hubble|Sputnik"),
        ("Which direction does the Sun appear to rise from?", "East", "West|North|South|Up"),
        ("What do we call a spacecraft that circles a planet?", "An orbiter", "A submarine|A kite|A balloon|A train"),
        ("What is the Hubble telescope?", "A telescope that orbits Earth", "A moon of Saturn|A kind of rocket|A planet|A space suit"),
        ("What is a satellite?", "An object that orbits a bigger one", "A kind of star|A planet's ring|A space food|A type of storm"),
        ("Why do astronauts need spacesuits?", "There is no air in space", "To stay dry|To look cool|Space is windy|To hide from stars"),
        ("In which direction do we say the Sun sets?", "West", "East|North|South|Up"),
        ("What is the planet we see as a bright 'evening star'?", "Venus", "Pluto|The Sun|Sirius|Neptune"),
    ])
    ids = [("🚀", "Rocket"), ("🛰️", "Satellite"), ("🔭", "Telescope"), ("☄️", "Comet"), ("🌌", "Galaxy"), ("🪐", "Saturn"),
           ("🌍", "Earth"), ("🌞", "Sun"), ("🧑‍🚀", "Astronaut"), ("🌙", "Moon")]
    for e, n in ids:
        pool = [x for _, x in ids if x != n] + ["Meteor", "Asteroid", "Space station", "Black hole"]
        if n == "Saturn": pool = ["Jupiter", "Mars", "Venus", "Neptune", "Mercury"]
        q = "Which planet is this?" if n == "Saturn" else "What is this space picture?"
        out.append(mc(r, q, n, pool, v=emoji(e)))
        out.append(mc(r, f"Which picture shows {'a' if n not in ('Saturn','Earth','Sun','Moon') else ''} {n}?".replace("  ", " ").replace("shows  ", "shows "), e, [x for x, _ in ids], ct="emoji"))
        out.append(mc(r, f"Tap {n}!", e, [x for x, _ in ids], ct="emoji"))
    return out


# ---------------------------------------------------------------- 11+
EVENTS = [
    ("Sputnik 1, the first artificial satellite, launch", 1957), ("Yuri Gagarin's first human spaceflight", 1961),
    ("Valentina Tereshkova's flight as the first woman in space", 1963), ("The Apollo 11 Moon landing", 1969),
    ("The Apollo 13 accident", 1970), ("The Apollo 8 flight, the first crewed trip around the Moon,", 1968),
    ("The last crewed Moon landing, Apollo 17,", 1972), ("The first launch of the Space Shuttle (Columbia)", 1981),
    ("Sally Ride's flight as the first American woman in space", 1983), ("The Space Shuttle Challenger disaster", 1986),
    ("The launch of the Hubble Space Telescope", 1990), ("The Space Shuttle Columbia disaster", 2003),
    ("The launch of the first ISS module", 1998), ("The launch of Voyager 1 and Voyager 2", 1977),
    ("The Viking landers' arrival on Mars", 1976), ("Mars Pathfinder and its Sojourner rover landing", 1997),
    ("The landing of rovers Spirit and Opportunity on Mars", 2004), ("The Curiosity rover's landing on Mars", 2012),
    ("The Perseverance rover's landing on Mars", 2021), ("New Horizons' flyby of Pluto", 2015),
    ("The launch of the James Webb Space Telescope", 2021), ("The first image of a black hole (M87*) release", 2019),
    ("Pluto's reclassification as a dwarf planet", 2006), ("The discovery of Neptune", 1846), ("The discovery of Uranus", 1781),
    ("The discovery of Pluto", 1930), ("Galileo's discovery of Jupiter's four large moons", 1610),
    ("Edwin Hubble's evidence that the universe is expanding", 1929), ("The launch of the Mir space station", 1986),
    ("The launch of the space station Skylab", 1973), ("The first discovery of an exoplanet around a Sun-like star", 1995),
    ("Cassini's arrival at Saturn", 2004),
]


def yr(y):
    return [str(y + d) for d in (-12, -7, -3, 3, 7, 12) if y + d > 1500 and y + d <= 2025]


def late():
    r = rng_for("space", "11+")
    out = []
    for t, y in EVENTS:
        q = f"In which year did this happen: {t.strip().rstrip(',')}?" if len(t) < 90 else t
        out.append(mc(r, q, str(y), yr(y)))
    # planetary data
    year_len = {"Mercury": "88 Earth days", "Venus": "225 Earth days", "Mars": "687 Earth days", "Jupiter": "About 12 Earth years",
                "Saturn": "About 29 Earth years", "Uranus": "84 Earth years", "Neptune": "165 Earth years"}
    for p, v in year_len.items():
        out.append(mc(r, f"How long is one year (one orbit of the Sun) on {p}?", v, [x for x in year_len.values() if x != v]))
    au = {"Mercury": "0.4 AU", "Venus": "0.7 AU", "Mars": "1.5 AU", "Jupiter": "5.2 AU", "Saturn": "9.5 AU", "Uranus": "19 AU", "Neptune": "30 AU"}
    for p, v in au.items():
        out.append(mc(r, f"About how far is {p} from the Sun on average?", v, [x for x in au.values() if x != v] + ["1 AU"]))
    diam = {"Mercury": "About 4,900 km", "Venus": "About 12,100 km", "Mars": "About 6,800 km", "Jupiter": "About 140,000 km", "Saturn": "About 116,000 km", "Earth": "About 12,700 km"}
    for p, v in diam.items():
        out.append(mc(r, f"What is the approximate diameter of {p}?", v, [x for x in diam.values() if x != v] + ["About 51,000 km"]))
    for i in range(1, 9):
        order = sorted(PLANETS, key=lambda p: -SIZE[p])
        out.append(mc(r, f"Ranked by diameter, which planet is number {i} (1 = biggest)?", order[i - 1], PLANETS))
    # moon -> planet
    moons = [("Phobos", "Mars"), ("Deimos", "Mars"), ("Io", "Jupiter"), ("Europa", "Jupiter"), ("Ganymede", "Jupiter"), ("Callisto", "Jupiter"),
             ("Titan", "Saturn"), ("Enceladus", "Saturn"), ("Mimas", "Saturn"), ("Rhea", "Saturn"), ("Iapetus", "Saturn"),
             ("Miranda", "Uranus"), ("Titania", "Uranus"), ("Oberon", "Uranus"), ("Triton", "Neptune")]
    for m, p in moons:
        out.append(mc(r, f"Which planet does the moon {m} orbit?", p, [x for x in PLANETS if x != p]))
    NJ = ["Titan", "Triton", "Charon", "Phobos", "Rhea", "Enceladus"]
    NS = ["Io", "Triton", "Charon", "Phobos", "Europa", "Ganymede"]
    NN = ["Io", "Titan", "Charon", "Phobos", "Europa", "Rhea"]
    for q, a, pool in [("Which moon is the largest in the solar system?", "Ganymede", ["Io", "Europa", "Callisto", "Titan", "Triton", "Charon"]),
                       ("Which moon of Jupiter is the most volcanically active place known?", "Io", NJ),
                       ("Which moon of Jupiter likely hides an ocean beneath an icy shell and is a top target for life searches?", "Europa", NJ),
                       ("Which moon of Saturn has a thick nitrogen atmosphere?", "Titan", ["Enceladus", "Mimas", "Rhea", "Iapetus"]),
                       ("Which moon of Saturn shoots geysers of ice from its south pole?", "Enceladus", ["Titan", "Mimas", "Rhea", "Iapetus"]),
                       ("Which large moon of Neptune orbits backwards (retrograde)?", "Triton", NN),
                       ("What is the largest moon of Pluto called?", "Charon", ["Io", "Europa", "Titan", "Triton", "Phobos"])]:
        out.append(mc(r, q, a, pool))
    out += [mc(r, "Which of these is NOT one of Jupiter's four Galilean moons?", "Titan", ["Io", "Europa", "Ganymede", "Callisto"]),
            mc(r, "How many moons does Mars have?", "2", ["0", "1", "3", "4"]),
            mc(r, "How many moons does Mercury have?", "0", ["1", "2", "3", "4"]),
            mc(r, "How many moons does Venus have?", "0", ["1", "2", "3", "4"]),
            mc(r, "Which planet has the most known moons?", "Saturn", ["Jupiter", "Earth", "Mars", "Neptune"])]
    R = []
    R += [
        ("Which planets are called the ice giants?", "Uranus and Neptune", "Jupiter and Saturn|Mercury and Venus|Earth and Mars"),
        ("Which planets are the gas giants?", "Jupiter and Saturn", "Uranus and Neptune|Mercury and Venus|Earth and Mars"),
        ("Which planets are the rocky (terrestrial) planets?", "Mercury, Venus, Earth, Mars", "Jupiter, Saturn, Uranus, Neptune|Venus, Earth, Jupiter, Saturn|Mars, Jupiter, Uranus, Neptune"),
        ("What are Jupiter and Saturn mostly made of?", "Hydrogen and helium", "Iron and nickel|Water ice only|Carbon dioxide|Silicate rock"),
        ("Which gas in Uranus's and Neptune's atmospheres gives them a blue tint?", "Methane", "Oxygen|Neon|Chlorine|Ozone"),
        ("What is the main gas in Mars's thin atmosphere?", "Carbon dioxide", "Oxygen|Nitrogen|Methane|Hydrogen"),
        ("What is the main gas in Venus's thick atmosphere?", "Carbon dioxide", "Oxygen|Hydrogen|Methane|Helium"),
        ("What is the most abundant gas in Earth's atmosphere?", "Nitrogen", "Oxygen|Carbon dioxide|Hydrogen|Helium"),
        ("Why is Venus hotter than Mercury, though farther from the Sun?", "Thick CO2 atmosphere traps heat", "It is closer to Earth|It spins faster|It has no atmosphere|It has volcanoes only"),
        ("About how hot is the surface of Venus?", "About 465 degrees C", "About 15 degrees C|About 100 degrees C|About 1,000 degrees C|About 20 degrees below zero"),
        ("Why does Mars look red?", "Iron oxide (rust) in its dust", "Hot lava everywhere|Red oceans|Sunlight only|Red plants"),
        ("What is Olympus Mons?", "The tallest volcano in the solar system", "A crater on the Moon|A moon of Mars|A mountain on Venus|A canyon on Mercury"),
        ("Which huge canyon system is found on Mars?", "Valles Marineris", "Grand Canyon|Olympus Mons|Cassini Division|Tycho"),
        ("Which planet rotates in the opposite direction to most planets and has a day longer than its year?", "Venus", "Mars|Mercury|Jupiter|Neptune"),
        ("Which planet's axis is tilted about 98 degrees?", "Uranus", "Neptune|Saturn|Mars|Earth"),
        ("Which planet was found by mathematical prediction before being seen?", "Neptune", "Uranus|Saturn|Mars|Venus"),
        ("Who discovered Uranus in 1781?", "William Herschel", "Galileo Galilei|Isaac Newton|Edwin Hubble|Johannes Kepler"),
        ("Who discovered Pluto in 1930?", "Clyde Tombaugh", "Edwin Hubble|William Herschel|Carl Sagan|Percival Lowell"),
        ("What is the name of the gap in Saturn's rings seen from Earth?", "Cassini Division", "Kuiper Gap|Hubble Division|Roche Gap|Great Rift"),
        ("What is the name for the average distance from Earth to the Sun?", "An astronomical unit", "A light-year|A parsec|A lunar unit|A solar mile"),
        ("About how many kilometres is one astronomical unit?", "About 150 million", "About 15 million|About 1.5 billion|About 150 thousand|About 15 billion"),
        ("What is the main belt of rocky bodies between Mars and Jupiter?", "Asteroid belt", "Kuiper belt|Oort cloud|Van Allen belt|Heliosphere"),
        ("Which region of icy bodies lies beyond Neptune?", "Kuiper belt", "Asteroid belt|Van Allen belt|Inner solar system|Roche limit"),
        ("What is the distant spherical shell of icy bodies thought to surround the solar system?", "Oort cloud", "Kuiper belt|Asteroid belt|Local Group|Heliosphere"),
        ("The Moon's surface gravity is about what fraction of Earth's?", "One-sixth", "One-half|One-tenth|One-third|Twice"),
        ("About how far is the Moon from Earth?", "About 384,000 km", "About 38,000 km|About 3.8 million km|About 150 million km|About 3,800 km"),
        ("Why do we always see the same face of the Moon?", "It is tidally locked to Earth", "It does not rotate or orbit|It is a flat disc|Clouds hide the far side|It is too far to see"),
        ("What mainly causes ocean tides on Earth?", "The Moon's gravity", "Wind only|The Sun's heat|Earth's magnetism|Earthquakes"),
        ("What causes Earth's seasons?", "The tilt of Earth's axis", "Distance from the Sun only|The Moon|Solar flares|Earth's speed changing"),
        ("About how much is Earth's axial tilt?", "About 23.5 degrees", "About 5 degrees|About 45 degrees|About 90 degrees|About 0 degrees"),
        ("What is the outer atmosphere of the Sun, visible during a total eclipse?", "The corona", "The photosphere|The core|The mantle|The crust"),
        ("What are sunspots?", "Cooler, darker areas on the Sun", "Holes in the Sun|Planets crossing the Sun|Hot bright areas|Meteors"),
        ("What creates the aurora (northern and southern lights)?", "Charged particles hitting Earth's atmosphere", "Reflected moonlight|Volcanic ash|Cities' lights|Ice crystals only"),
        ("What stream of charged particles flows out from the Sun?", "The solar wind", "The jet stream|The Gulf Stream|Cosmic dust|Dark matter"),
        ("About how long does sunlight take to reach Earth?", "About 8 minutes", "About 8 seconds|About 8 hours|About 1 second|About 8 days"),
        ("About how long does moonlight (reflected light) take to reach Earth?", "About 1.3 seconds", "About 8 minutes|About 1 hour|About 13 minutes|About 1 day"),
        ("What is a light-year a unit of?", "Distance", "Time|Speed|Brightness|Mass"),
        ("About how fast does light travel?", "300,000 km per second", "3,000 km per second|30,000 km per second|3,000,000 km per second|300 km per second"),
        ("About how far is one light-year?", "About 9.5 trillion km", "About 9.5 million km|About 150 million km|About 95 billion km|About 950 trillion km"),
        ("What is the nearest star to the Sun?", "Proxima Centauri", "Sirius|Betelgeuse|Polaris|Vega"),
        ("About how far away is Proxima Centauri?", "About 4.2 light-years", "About 42 light-years|About 420 light-years|About 4.2 million light-years|About 0.4 light-years"),
        ("Which is the brightest star in Earth's night sky?", "Sirius", "Polaris|Betelgeuse|Vega|Rigel"),
        ("Which star is almost directly above Earth's north pole?", "Polaris", "Sirius|Vega|Rigel|Antares"),
        ("Betelgeuse is a red supergiant in which constellation?", "Orion", "Scorpius|Taurus|Leo|Cygnus"),
        ("Which colour of star is the hottest?", "Blue", "Red|Orange|Yellow|Brown"),
        ("Which colour of star is the coolest?", "Red", "Blue|White|Blue-white|Violet"),
        ("What type of star is the Sun?", "Yellow dwarf (G-type)", "Red giant|White dwarf|Neutron star|Blue supergiant"),
        ("What process powers the Sun?", "Nuclear fusion", "Burning coal|Nuclear fission|Chemical burning|Friction"),
        ("What will the Sun become in about 5 billion years?", "A red giant", "A black hole|A supernova|A neutron star|A comet"),
        ("What is left after a Sun-like star finishes its life?", "A white dwarf", "A black hole|A pulsar|A quasar|A nebula"),
        ("What can a massive star leave behind after a supernova?", "A neutron star or black hole", "A white dwarf only|A red giant|A planet|A comet"),
        ("What is a pulsar?", "A spinning neutron star", "A pulsing planet|A dying red giant|A comet's tail|A kind of galaxy"),
        ("What is a nebula?", "A cloud of gas and dust in space", "A cluster of planets|A kind of comet|A dead star|A black hole"),
        ("About how old is the Sun?", "About 4.6 billion years", "About 4.6 million years|About 13.8 billion years|About 460 million years|About 46 billion years"),
        ("About how old is the universe?", "About 13.8 billion years", "About 4.6 billion years|About 138 million years|About 1.38 trillion years|About 6,000 years"),
        ("What does the Big Bang theory describe?", "The expansion of the universe from a hot, dense state", "A star exploding|A planet forming|A black hole merging|The Moon forming"),
        ("Who showed in 1929 that galaxies are moving away from us?", "Edwin Hubble", "Albert Einstein|Carl Sagan|Stephen Hawking|Galileo Galilei"),
        ("What is the cosmic microwave background?", "Leftover glow from the early universe", "Light from the Sun|Radio from Mars|Starlight|Light from black holes"),
        ("Roughly how much of the universe is ordinary matter?", "About 5%", "About 50%|About 95%|About 27%|About 80%"),
        ("What makes up most of the universe's energy content?", "Dark energy", "Ordinary matter|Starlight|Black holes|Neutron stars"),
        ("What is the boundary around a black hole beyond which nothing can escape?", "The event horizon", "The corona|The photosphere|The heliopause|The ergosphere"),
        ("What is the supermassive black hole at the center of the Milky Way called?", "Sagittarius A*", "Cygnus X-1|M87*|Andromeda A|Orion Prime"),
        ("The first image of a black hole (2019) came from which network?", "Event Horizon Telescope", "Hubble Space Telescope|Kepler|Voyager|LIGO"),
        ("Which galaxy's black hole was shown in that first image?", "M87", "The Milky Way|Andromeda|The Large Magellanic Cloud|Triangulum"),
        ("Who proposed that black holes emit radiation?", "Stephen Hawking", "Albert Einstein|Isaac Newton|Carl Sagan|Edwin Hubble"),
        ("How does a stellar black hole usually form?", "A massive star collapses", "Two planets collide|A comet crashes|A galaxy cools|A nebula freezes"),
        ("What is the point of infinite density at a black hole's center called?", "A singularity", "A pulsar|A corona|An aphelion|A quasar"),
        ("What type of galaxy is the Milky Way?", "Barred spiral", "Elliptical|Irregular|Lenticular only|Ring"),
        ("What is the nearest large galaxy to the Milky Way?", "Andromeda", "Triangulum|Whirlpool|Sombrero|Pinwheel"),
        ("About how far away is the Andromeda Galaxy?", "About 2.5 million light-years", "About 25,000 light-years|About 250 light-years|About 2.5 billion light-years|About 25 light-years"),
        ("About how wide is the Milky Way?", "About 100,000 light-years", "About 1,000 light-years|About 10 million light-years|About 100 light-years|About 100 billion light-years"),
        ("Which galaxy shape is smooth with no spiral arms?", "Elliptical", "Spiral|Barred spiral|Ring|Pinwheel"),
        ("The Large Magellanic Cloud is a small companion galaxy of what?", "The Milky Way", "Andromeda|The Sun|Triangulum|The Pinwheel"),
        ("What is the group of galaxies that includes the Milky Way called?", "The Local Group", "The Virgo Cluster|The Coma Cluster|The Oort Cloud|The Great Wall"),
        ("Roughly how many stars are in the Milky Way?", "Hundreds of billions", "About a million|About ten thousand|Hundreds of trillions|About a billion"),
        ("Which constellation looks like a hunter with a belt of three stars?", "Orion", "Cassiopeia|Lyra|Scorpius|Cygnus"),
        ("Which constellation contains the Big Dipper?", "Ursa Major", "Ursa Minor|Orion|Cassiopeia|Leo"),
        ("Polaris is the tip of the handle of which constellation's 'dipper'?", "Ursa Minor", "Ursa Major|Orion|Scorpius|Draco"),
        ("Which constellation is shaped like a 'W' or 'M'?", "Cassiopeia", "Orion|Leo|Cygnus|Gemini"),
        ("Which constellation, seen from the southern hemisphere, includes the Southern Cross?", "Crux", "Orion|Cassiopeia|Ursa Major|Lyra"),
        ("Sirius, the brightest star, is in which constellation?", "Canis Major", "Orion|Taurus|Lyra|Leo"),
        ("Vega is the brightest star in which constellation?", "Lyra", "Cygnus|Orion|Canis Major|Taurus"),
        ("Antares is a red supergiant in which constellation?", "Scorpius", "Leo|Orion|Gemini|Lyra"),
        ("Which constellation contains the Pleiades star cluster?", "Taurus", "Orion|Leo|Gemini|Cygnus"),
        ("Castor and Pollux are the bright stars of which constellation?", "Gemini", "Orion|Taurus|Leo|Lyra"),
        ("Rigel, a blue supergiant, is in which constellation?", "Orion", "Scorpius|Lyra|Taurus|Leo"),
        ("Which Apollo 11 astronaut stayed in lunar orbit?", "Michael Collins", "Buzz Aldrin|Neil Armstrong|Alan Shepard|Jim Lovell"),
        ("Who was the second person to walk on the Moon?", "Buzz Aldrin", "Michael Collins|Alan Shepard|John Glenn|Pete Conrad"),
        ("What was the name of the Apollo 11 lunar module?", "Eagle", "Columbia|Odyssey|Falcon|Challenger"),
        ("What was the name of the Apollo 11 command module?", "Columbia", "Eagle|Aquarius|Discovery|Endeavour"),
        ("Which rocket launched the Apollo Moon missions?", "Saturn V", "Falcon 9|Atlas|Soyuz|Ariane 5"),
        ("Who was the first American woman in space?", "Sally Ride", "Mae Jemison|Christa McAuliffe|Valentina Tereshkova|Eileen Collins"),
        ("Who was the first woman in space?", "Valentina Tereshkova", "Sally Ride|Mae Jemison|Svetlana Savitskaya|Eileen Collins"),
        ("Who was the first American to orbit Earth (1962)?", "John Glenn", "Alan Shepard|Neil Armstrong|Buzz Aldrin|Gus Grissom"),
        ("Which country launched the first artificial satellite?", "Soviet Union", "United States|China|United Kingdom|France"),
        ("Which Voyager probe visited both Uranus and Neptune?", "Voyager 2", "Voyager 1|Pioneer 10|Cassini|Galileo"),
        ("Which spacecraft is the most distant human-made object from Earth?", "Voyager 1", "Voyager 2|Hubble|New Horizons|Cassini"),
        ("What is on the Voyager Golden Records?", "Sounds and images of Earth", "Rock samples|Seeds|Maps of Mars|Photos of the Moon only"),
        ("Which spacecraft orbited Saturn from 2004 to 2017?", "Cassini", "Galileo|Juno|Voyager 1|Pioneer 11"),
        ("Which NASA spacecraft orbits Jupiter and arrived in 2016?", "Juno", "Cassini|Galileo|New Horizons|Voyager 2"),
        ("Which probe flew past Pluto in 2015?", "New Horizons", "Cassini|Juno|Voyager 2|Dawn"),
        ("Which NASA probe is designed to 'touch' the Sun's atmosphere?", "Parker Solar Probe", "Juno|Cassini|Kepler|Dawn"),
        ("The James Webb Space Telescope mainly observes which kind of light?", "Infrared", "X-rays|Gamma rays|Radio only|Ultraviolet only"),
        ("The Hubble Space Telescope is named after which astronomer?", "Edwin Hubble", "Galileo Galilei|Carl Sagan|Nicolaus Copernicus|Johannes Kepler"),
        ("Which Space Shuttle was lost in January 1986?", "Challenger", "Columbia|Discovery|Atlantis|Endeavour"),
        ("Which Space Shuttle broke up on re-entry in 2003?", "Columbia", "Challenger|Discovery|Atlantis|Endeavour"),
        ("Which Space Shuttle carried Hubble into orbit in 1990?", "Discovery", "Columbia|Challenger|Atlantis|Endeavour"),
        ("Which agency operates the Soyuz spacecraft?", "Roscosmos", "NASA|ESA|JAXA|ISRO"),
        ("What does ESA stand for?", "European Space Agency", "Earth Satellite Alliance|European Solar Association|Equatorial Space Agency|Explorer Space Administration"),
        ("About how high above Earth does the ISS orbit?", "About 400 km", "About 40 km|About 4,000 km|About 36,000 km|About 400,000 km"),
        ("About how long does the ISS take to orbit Earth once?", "About 90 minutes", "About 9 minutes|About 24 hours|About 9 hours|About 90 days"),
        ("About how fast does the ISS travel?", "About 28,000 km/h", "About 2,800 km/h|About 280,000 km/h|About 280 km/h|About 28 km/h"),
        ("What is the Karman line, often used as the edge of space?", "100 km altitude", "10 km altitude|1,000 km altitude|400 km altitude|36,000 km altitude"),
        ("What is escape velocity from Earth, roughly?", "About 11 km/s", "About 1.1 km/s|About 110 km/s|About 0.11 km/s|About 300 km/s"),
        ("Which program aims to return humans to the Moon in the 2020s?", "Artemis", "Apollo|Gemini|Mercury|Vostok"),
        ("What does a solar eclipse require?", "The Moon between the Sun and Earth", "Earth between the Sun and Moon|The Sun between Earth and Moon|Mars passing the Sun|A comet in front of the Sun"),
        ("What does a lunar eclipse require?", "Earth between the Sun and Moon", "The Moon between the Sun and Earth|The Sun between Earth and Moon|A comet passing|A planet blocking the Moon"),
        ("What did the four Galilean moons help support in the 1600s?", "That not everything orbits Earth", "That the Moon is a planet|That Mars has water|That the Sun is a planet|That Earth is flat"),
        ("Who proposed that the planets orbit the Sun (heliocentric model) in 1543?", "Nicolaus Copernicus", "Isaac Newton|Galileo Galilei|Tycho Brahe|Ptolemy"),
        ("Who described the three laws of planetary motion?", "Johannes Kepler", "Isaac Newton|Nicolaus Copernicus|Albert Einstein|Galileo Galilei"),
        ("Who formulated the law of universal gravitation?", "Isaac Newton", "Albert Einstein|Galileo Galilei|Johannes Kepler|Edwin Hubble"),
        ("Whose theory of general relativity describes gravity as curved spacetime?", "Albert Einstein", "Isaac Newton|Stephen Hawking|Max Planck|Niels Bohr"),
        ("What did LIGO first detect in 2015?", "Gravitational waves", "Dark matter|A black hole's light|Neutrinos|Cosmic rays"),
        ("What does redshift in a galaxy's light tell us?", "It is moving away from us", "It is moving toward us|It is cooling|It is very small|It is made of dust"),
        ("What is an exoplanet?", "A planet orbiting a star other than the Sun", "A planet beyond Neptune in our system|A moon of a gas giant|A dwarf planet|A comet's core"),
        ("What does a spectrum from a star mainly reveal?", "Its chemical makeup", "Its exact age only|The number of its planets|Its colour name|Its distance only"),
        ("Which spectral class is the Sun?", "G", "A|K|M|O"),
        ("What is the Moon's dark plains called, formed by ancient lava?", "Maria", "Craters|Rilles|Highlands|Rays"),
    ]
    out += rows(r, R)
    return out


def build(band):
    if band == "2-5": return kids()
    if band == "6-10": return mid()
    return late()
