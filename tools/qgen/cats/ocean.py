from ..common import *

META = {"id": "ocean", "name": "Ocean Life", "icon": "🐠"}

# (name, emoji or None, group)
SEA = [
    ("fish", "🐟", "fish"), ("tropical fish", "🐠", "fish"), ("pufferfish", "🐡", "fish"), ("shark", "🦈", "fish"),
    ("great white shark", None, "fish"), ("hammerhead shark", None, "fish"), ("whale shark", None, "fish"), ("manta ray", None, "fish"),
    ("stingray", None, "fish"), ("seahorse", None, "fish"), ("clownfish", None, "fish"), ("angelfish", None, "fish"),
    ("tuna", None, "fish"), ("swordfish", None, "fish"), ("sailfish", None, "fish"), ("anglerfish", None, "fish"),
    ("ocean sunfish", None, "fish"), ("moray eel", None, "fish"), ("barracuda", None, "fish"), ("lionfish", None, "fish"),
    ("flying fish", None, "fish"), ("cod", None, "fish"), ("parrotfish", None, "fish"), ("oarfish", None, "fish"),
    ("dolphin", "🐬", "mammal"), ("whale", "🐳", "mammal"), ("seal", "🦭", "mammal"), ("sea otter", "🦦", "mammal"),
    ("blue whale", None, "mammal"), ("orca", None, "mammal"), ("humpback whale", None, "mammal"), ("sperm whale", None, "mammal"),
    ("narwhal", None, "mammal"), ("beluga", None, "mammal"), ("walrus", None, "mammal"), ("sea lion", None, "mammal"),
    ("manatee", None, "mammal"), ("porpoise", None, "mammal"), ("elephant seal", None, "mammal"),
    ("sea turtle", "🐢", "reptile"), ("leatherback turtle", None, "reptile"), ("green sea turtle", None, "reptile"),
    ("sea snake", None, "reptile"), ("marine iguana", None, "reptile"),
    ("penguin", "🐧", "bird"), ("pelican", None, "bird"), ("albatross", None, "bird"), ("puffin", None, "bird"),
    ("seagull", None, "bird"), ("emperor penguin", None, "bird"), ("cormorant", None, "bird"),
    ("octopus", "🐙", "mollusk"), ("squid", "🦑", "mollusk"), ("oyster", "🦪", "mollusk"), ("giant squid", None, "mollusk"),
    ("clam", None, "mollusk"), ("nautilus", None, "mollusk"), ("cuttlefish", None, "mollusk"), ("mussel", None, "mollusk"),
    ("sea snail", None, "mollusk"), ("scallop", None, "mollusk"),
    ("crab", "🦀", "crustacean"), ("lobster", "🦞", "crustacean"), ("shrimp", "🦐", "crustacean"), ("hermit crab", None, "crustacean"),
    ("barnacle", None, "crustacean"), ("krill", None, "crustacean"),
    ("jellyfish", None, "cnidarian"), ("coral", None, "cnidarian"), ("sea anemone", None, "cnidarian"),
    ("Portuguese man o' war", None, "cnidarian"), ("box jellyfish", None, "cnidarian"),
    ("starfish", None, "echinoderm"), ("sea urchin", None, "echinoderm"), ("sand dollar", None, "echinoderm"),
    ("sea cucumber", None, "echinoderm"), ("brittle star", None, "echinoderm"),
    ("sea sponge", None, "sponge"),
]
S = {n: dict(name=n, e=e, g=g) for n, e, g in SEA}
EM = [n for n in S if S[n]["e"]]
KID6 = {"fish", "tropical fish", "pufferfish", "shark", "great white shark", "hammerhead shark", "whale shark", "manta ray", "stingray",
        "seahorse", "clownfish", "tuna", "swordfish", "dolphin", "whale", "seal", "sea otter", "blue whale", "orca", "humpback whale",
        "narwhal", "beluga", "walrus", "sea lion", "manatee", "sea turtle", "sea snake", "penguin", "pelican", "puffin", "seagull",
        "octopus", "squid", "oyster", "clam", "crab", "lobster", "shrimp", "hermit crab", "jellyfish", "starfish", "sea urchin", "coral"}
CONF = [{"fish", "tropical fish", "pufferfish", "shark"}, {"octopus", "squid"}, {"crab", "lobster", "shrimp"},
        {"whale", "dolphin", "blue whale"}, {"seal", "sea otter"}]


def ok(a, b):
    return a != b and not any(a in g and b in g for g in CONF)


def wr(ans, pool): return [x for x in pool if ok(ans, x)]
def art(n): return ("an " if n[0].lower() in "aeiou" else "a ") + n
def E(n): return S[n]["e"]


# approximate adult values
LEN = {"blue whale": 30, "humpback whale": 15, "sperm whale": 16, "whale shark": 12, "giant squid": 12, "orca": 8,
       "great white shark": 5, "narwhal": 4.5, "walrus": 3, "bottlenose dolphin": 3, "ocean sunfish": 3, "sailfish": 3,
       "leatherback turtle": 2, "sea otter": 1.2, "emperor penguin": 1.1, "lobster": 0.4, "clownfish": 0.1}
MASS = {"blue whale": 150000, "sperm whale": 40000, "whale shark": 20000, "orca": 5000, "walrus": 1200,
        "great white shark": 1000, "bottlenose dolphin": 250, "emperor penguin": 30, "sea otter": 25, "clownfish": 0.01}
SPEED = {"orca": 50, "great white shark": 40, "bottlenose dolphin": 35, "leatherback turtle": 35, "sea otter": 10, "manatee": 8,
         "moon jellyfish": 2}
LIFE = {"Greenland shark": 250, "bowhead whale": 200, "blue whale": 85, "great white shark": 70, "green sea turtle": 70,
        "sea otter": 15, "giant Pacific octopus": 4, "moon jellyfish": 1}
LEN_EM = {"whale": 30, "shark": 5, "dolphin": 3, "seal": 1.8, "penguin": 1.1, "sea turtle": 1, "tropical fish": 0.1, "crab": 0.2, "shrimp": 0.05}
EMOJI_OF = {"fish": "🐟", "crab": "🦀", "shrimp": "🦐", "whale": "🐳", "shark": "🦈", "dolphin": "🐬", "seal": "🦭", "penguin": "🐧",
            "sea turtle": "🐢", "octopus": "🐙", "tropical fish": "🐠"}


def f_m(x): return f"{x:g} m"
def f_kg(x):
    if x >= 1000: return f"{x:,.0f} kg"
    if x >= 1: return f"{x:g} kg"
    return f"{x * 1000:g} g"
def f_kmh(x): return f"{x:g} km/h"
def f_yr(x): return "1 year" if x == 1 else f"{x:g} years"


def lineups(r, table, want, ratio, direction, tries=5000):
    """4-name lists whose extreme (max/min) is separated from the runner-up by >= ratio."""
    names = list(table)
    seen, out = set(), []
    for _ in range(tries):
        s = r.sample(names, 4)
        s.sort(key=lambda n: table[n], reverse=(direction == "max"))
        a, b = table[s[0]], table[s[1]]
        if direction == "max" and a < b * ratio: continue
        if direction == "min" and b < a * ratio: continue
        if frozenset(s) in seen: continue
        seen.add(frozenset(s)); out.append(s)
        if len(out) >= want: break
    return out


BABY = [("whale", "calf"), ("blue whale", "calf"), ("dolphin", "calf"), ("orca", "calf"), ("manatee", "calf"), ("walrus", "calf"),
        ("seal", "pup"), ("sea lion", "pup"), ("sea otter", "pup"), ("shark", "pup"), ("manta ray", "pup"), ("stingray", "pup"),
        ("sea turtle", "hatchling"), ("fish", "fry"), ("penguin", "chick"), ("puffin", "chick")]
BABY_POOL = ["calf", "pup", "hatchling", "fry", "chick", "kitten", "puppy", "joey"]

# animal, main food, wrong foods
FOOD6 = [("blue whale", "krill", ["seagrass", "clams", "seals", "sea urchins"]),
         ("manatee", "seagrass", ["krill", "jellyfish", "seals", "crabs"]),
         ("leatherback turtle", "jellyfish", ["seagrass", "krill", "clams", "seaweed only"]),
         ("green sea turtle", "seagrass", ["krill", "seals", "clams", "sea urchins"]),
         ("sea otter", "sea urchins", ["krill", "seagrass", "jellyfish", "seals"]),
         ("walrus", "clams", ["krill", "seagrass", "jellyfish", "coral"]),
         ("great white shark", "seals", ["seagrass", "krill", "jellyfish", "coral"]),
         ("octopus", "crabs", ["seagrass", "coral", "krill", "seaweed"]),
         ("parrotfish", "algae growing on coral", ["seals", "krill", "jellyfish", "crabs"]),
         ("starfish", "clams and mussels", ["seagrass", "krill", "seals", "jellyfish"]),
         ("ocean sunfish", "jellyfish", ["seagrass", "seals", "clams", "crabs"]),
         ("whale shark", "tiny plankton", ["seals", "crabs", "sea turtles", "dolphins"]),
         ("penguin", "fish and krill", ["seagrass", "coral", "jellyfish only", "algae"]),
         ("pelican", "fish", ["seagrass", "coral", "krill", "algae"])]

REEF = "on a coral reef"; DEEP = "in the deep, dark ocean"; POLAR = "in icy polar waters"; TIDE = "in tide pools near the shore"
HAB = [("clownfish", REEF), ("parrotfish", REEF), ("angelfish", REEF), ("butterflyfish", REEF), ("anglerfish", DEEP), ("vampire squid", DEEP),
       ("giant squid", DEEP), ("narwhal", POLAR), ("beluga", POLAR), ("walrus", POLAR), ("emperor penguin", POLAR), ("leopard seal", POLAR),
       ("harp seal", POLAR)]

FACT6 = [
    ("How many oceans are there on Earth?", "5", ["3", "6", "7", "8"]),
    ("Which is the largest ocean?", "Pacific Ocean", ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean"]),
    ("Which is the smallest ocean?", "Arctic Ocean", ["Pacific Ocean", "Atlantic Ocean", "Indian Ocean"]),
    ("Which ocean is around the North Pole?", "Arctic Ocean", ["Pacific Ocean", "Atlantic Ocean", "Indian Ocean"]),
    ("Which ocean are the Hawaiian Islands in?", "Pacific Ocean", ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean"]),
    ("Which ocean is between Europe and North America?", "Atlantic Ocean", ["Pacific Ocean", "Indian Ocean", "Arctic Ocean"]),
    ("Which ocean is between Africa and Australia?", "Indian Ocean", ["Atlantic Ocean", "Arctic Ocean", "Pacific Ocean"]),
    ("Which cold ocean surrounds Antarctica?", "Southern Ocean", ["Indian Ocean", "Atlantic Ocean", "Arctic Ocean"]),
    ("What does ocean water taste like?", "salty", ["sweet", "sour", "spicy"]),
    ("About how much of Earth's surface is covered by ocean?", "about 70 percent", ["about 10 percent", "about 30 percent", "about 50 percent"]),
    ("What is the biggest animal in the ocean?", "blue whale", ["great white shark", "giant squid", "orca"]),
    ("What is the biggest fish in the ocean?", "whale shark", ["great white shark", "blue whale", "manta ray"]),
    ("Which sea animal has eight arms?", "octopus", ["crab", "starfish", "dolphin", "shark"]),
    ("How many arms do most starfish have?", "5", ["3", "4", "8", "10"]),
    ("Which sea animal is called the 'unicorn of the sea' because of its long tusk?", "narwhal", ["walrus", "dolphin", "manatee"]),
    ("Which of these sea animals is a mammal?", "dolphin", ["shark", "octopus", "jellyfish", "tuna"]),
    ("Which of these is NOT a fish?", "dolphin", ["shark", "tuna", "seahorse"]),
    ("Which one is NOT a fish?", "whale", ["clownfish", "swordfish", "stingray"]),
    ("Which of these animals is not a fish?", "seal", ["shark", "sailfish", "manta ray"]),
    ("What do clownfish live in?", "sea anemones", ["sponges", "seashells", "kelp"]),
    ("Which sea animal makes pearls?", "oyster", ["crab", "shark", "jellyfish"]),
    ("Which sea animal squirts ink to escape?", "octopus", ["shark", "crab", "dolphin", "whale"]),
    ("What are coral reefs built by?", "tiny animals called corals", ["tiny plants", "big fish", "sand and wind"]),
    ("The Great Barrier Reef is off the coast of which country?", "Australia", ["Brazil", "Japan", "Canada"]),
    ("What causes the tides?", "the pull of the Moon", ["fish swimming", "boats", "underwater volcanoes"]),
    ("In most places, high tide happens about how many times a day?", "2", ["1", "4", "10"]),
    ("At high tide, the water is ...", "high up on the beach", ["far away from the beach", "frozen", "gone"]),
    ("At low tide, the water is ...", "far down the beach", ["high up on the beach", "frozen", "salt-free"]),
    ("What do we call a giant wave caused by an undersea earthquake?", "tsunami", ["tide", "whirlpool", "hurricane"]),
    ("What mostly makes ocean waves?", "wind", ["fish", "boats", "rain"]),
    ("Which sea animal can regrow a lost arm?", "starfish", ["dolphin", "shark", "whale"]),
    ("Which of these does a jellyfish NOT have?", "a brain", ["tentacles", "a mouth", "stinging cells"]),
    ("Which sea animal walks sideways and has two big claws?", "crab", ["octopus", "dolphin", "jellyfish"]),
    ("Which seahorse parent carries the babies?", "the dad", ["the mom", "a big fish", "a crab"]),
    ("Why do sea otters hold hands when they sleep?", "so they don't drift apart", ["to play games", "to say hello", "to catch fish"]),
    ("Which seabird cannot fly but swims very well?", "penguin", ["pelican", "seagull", "albatross"]),
    ("A group of fish swimming together is called a ...", "school", ["pride", "herd", "pack"]),
    ("A group of dolphins is called a ...", "pod", ["pride", "herd", "pack"]),
    ("What do whales and dolphins breathe through?", "blowholes", ["gills", "fins", "scales"]),
    ("What do fish use to breathe underwater?", "gills", ["lungs", "blowholes", "fins"]),
    ("Which sea animal is nicknamed the 'sea cow'?", "manatee", ["walrus", "seal", "whale"]),
    ("Which sea mammal has long tusks and whiskers and lives in the Arctic?", "walrus", ["dolphin", "seal", "manatee", "sea otter"]),
    ("Where do sea turtles lay their eggs?", "on sandy beaches", ["on coral reefs", "on the deep sea floor", "on ice"]),
    ("Hermit crabs live inside ...", "empty shells", ["coral", "sponges", "rocks only"]),
    ("How do dolphins talk to each other?", "clicks and whistles", ["roars", "tweets", "quacks"]),
    ("What is the part of the ocean where sunlight reaches called?", "the sunlight zone", ["the midnight zone", "the twilight zone", "the trench"]),
    ("Which fish has a glowing light to lure its food in the dark deep sea?", "anglerfish", ["clownfish", "tuna", "cod"]),
    ("What kind of animal is a sea turtle?", "reptile", ["fish", "mammal", "bird"]),
    ("What is the deepest part of the ocean called?", "Mariana Trench", ["Great Barrier Reef", "Bermuda Triangle", "Sargasso Sea"]),
    ("Which sea animal has three hearts and blue blood?", "octopus", ["dolphin", "crab", "starfish"]),
    ("What do blue whales eat?", "tiny krill", ["big sharks", "seals", "seaweed"]),
    ("Which sea animal looks like a star?", "starfish", ["seahorse", "octopus", "clam"]),
    ("What are tiny floating sea plants and animals called?", "plankton", ["coral", "kelp", "sponges"]),
    ("What are giant underwater 'forests' of tall seaweed called?", "kelp forests", ["coral reefs", "tide pools", "mangroves"]),
]

FACT11 = [
    ("What is the name of the ocean zone from about 200 to 1,000 m deep, where only dim light reaches?", "twilight zone", ["sunlight zone", "midnight zone", "abyssal zone"]),
    ("Which ocean zone, from about 1,000 to 4,000 m, has no sunlight at all?", "midnight zone", ["sunlight zone", "twilight zone", "intertidal zone"]),
    ("The hadal zone refers to ...", "the deepest ocean trenches", ["the sunlit surface", "the shoreline", "coral reefs"]),
    ("What is the deepest known point in the ocean called?", "Challenger Deep", ["Puerto Rico Trench", "Great Blue Hole", "Sargasso Basin"]),
    ("About how deep is the Challenger Deep in the Mariana Trench?", "about 11,000 m", ["about 4,000 m", "about 2,000 m", "about 25,000 m"]),
    ("About how deep is the ocean on average?", "about 3,700 m", ["about 300 m", "about 10,000 m", "about 800 m"]),
    ("What percent of Earth's water is in the oceans?", "about 97%", ["about 50%", "about 75%", "about 85%"]),
    ("About how much of seawater's weight is dissolved salt?", "about 3.5%", ["about 0.35%", "about 10%", "about 25%"]),
    ("Spring tides, the biggest tides, happen when ...", "the Sun, Earth and Moon line up", ["the Moon is at first or last quarter", "a storm arrives", "it is the spring season"]),
    ("Neap tides, the smallest tides, happen around which Moon phase?", "first or last quarter", ["full moon", "new moon", "both new and full moon"]),
    ("Which bay in Canada has some of the highest tides in the world?", "Bay of Fundy", ["Hudson Bay", "Bay of Biscay", "Monterey Bay"]),
    ("About how long is it between two high tides in the same place?", "about 12 hours", ["about 6 hours", "about 24 hours", "about 3 hours"]),
    ("Which warm current carries heat from the Caribbean toward Western Europe?", "Gulf Stream", ["Humboldt Current", "Labrador Current", "California Current"]),
    ("El Nino is a warming of surface waters in which ocean?", "Pacific Ocean", ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean"]),
    ("Coral bleaching happens when corals lose the tiny ... living in them.", "algae", ["fish", "sand grains", "crabs"]),
    ("Coral polyps belong to which animal group?", "cnidarians", ["mollusks", "crustaceans", "echinoderms"]),
    ("The Great Barrier Reef lies off which Australian state?", "Queensland", ["Western Australia", "Tasmania", "Victoria"]),
    ("Clownfish and sea anemones help each other. This is called ...", "mutualism", ["parasitism", "predation", "competition"]),
    ("Cleaner wrasses eat parasites off larger fish. This relationship is called ...", "mutualism", ["parasitism", "predation", "competition"]),
    ("Blue whales feed using plates of ... in their mouths.", "baleen", ["teeth", "tusks", "gills"]),
    ("Which pair are both toothed whales?", "sperm whale and orca", ["blue whale and humpback", "gray whale and bowhead", "right whale and minke"]),
    ("Dolphins sleep by resting how much of their brain at a time?", "one half", ["all of it", "none of it", "a quarter"]),
    ("Which is the largest dolphin species?", "orca", ["bottlenose dolphin", "common dolphin", "river dolphin"]),
    ("Orcas, or killer whales, are actually the largest members of which family?", "dolphins", ["sharks", "seals", "porpoises"]),
    ("A narwhal's tusk is actually a ...", "long tooth", ["horn", "antler", "fin spine"]),
    ("The Portuguese man o' war is actually ...", "a colony of tiny animals working together", ["a true jellyfish", "a type of fish", "a seaweed"]),
    ("Which tiny jellyfish can return to an earlier life stage and is called 'immortal'?", "Turritopsis dohrnii", ["moon jelly", "box jellyfish", "lion's mane jellyfish"]),
    ("What color is octopus blood?", "blue", ["red", "green", "yellow"]),
    ("How many hearts does an octopus have?", "3", ["1", "2", "8"]),
    ("How many limbs in total does a squid have (arms plus tentacles)?", "10", ["8", "6", "12"]),
    ("Which cephalopod has an outer spiral shell and is a 'living fossil'?", "nautilus", ["octopus", "squid", "cuttlefish"]),
    ("Starfish belong to which group of animals?", "echinoderms", ["cnidarians", "mollusks", "crustaceans"]),
    ("Starfish move using hundreds of tiny ...", "tube feet", ["fins", "jets", "tails"]),
    ("Which of these animals is a crustacean?", "lobster", ["clam", "squid", "starfish"]),
    ("Which of these animals is a mollusk?", "squid", ["lobster", "starfish", "jellyfish"]),
    ("The glowing lure of an anglerfish gets its light from ...", "bacteria", ["algae", "electricity", "sunlight"]),
    ("Which is the heaviest bony fish in the world?", "ocean sunfish", ["great white shark", "whale shark", "manta ray"]),
    ("A shark's skeleton is made of ...", "cartilage", ["bone", "shell", "coral"]),
    ("A shark's lost teeth are ...", "replaced throughout its life", ["never replaced", "replaced only once", "replaced only in winter"]),
    ("What is the largest predatory fish in the ocean?", "great white shark", ["tiger shark", "hammerhead shark", "bull shark"]),
    ("Which marine mammal has the thickest fur of any animal?", "sea otter", ["seal", "walrus", "dolphin"]),
    ("Sea otters use ... as tools to crack open shellfish.", "rocks", ["fishing nets", "seaweed ropes", "coral"]),
    ("Which animal protects kelp forests by eating sea urchins?", "sea otter", ["dolphin", "great white shark", "blue whale"]),
    ("Kelp is a kind of ...", "brown algae", ["coral", "sponge", "jellyfish"]),
    ("Tiny ocean plankton called phytoplankton make a large share of Earth's ...", "oxygen", ["gold", "salt", "oil"]),
    ("Blue whales mainly eat which tiny shrimp-like animals?", "krill", ["herring", "squid", "sardines"]),
    ("The only lizard that feeds in the sea lives on the ...", "Galapagos Islands", ["Hawaiian Islands", "Canary Islands", "Maldives"]),
    ("Sea turtles and sea snakes must come to the surface to ...", "breathe air", ["drink fresh water", "lay eggs only", "find salt"]),
    ("Which is the largest sea turtle?", "leatherback", ["green turtle", "hawksbill", "loggerhead"]),
    ("In sea turtle nests, warmer sand produces more ...", "females", ["males", "twins", "pink shells"]),
    ("Salmon are born in rivers, live in the sea, and return to ... to lay eggs.", "the river where they were born", ["a coral reef", "the deepest trench", "the Arctic"]),
    ("Which sea, known for floating seaweed, is where freshwater eels go to spawn?", "Sargasso Sea", ["Red Sea", "Black Sea", "Coral Sea"]),
    ("What is the world's longest mountain chain, mostly underwater?", "mid-ocean ridge", ["Himalayas", "Andes", "Rocky Mountains"]),
    ("Life near deep-sea hydrothermal vents gets energy from ...", "chemicals", ["sunlight", "waves", "ice"]),
    ("Most tsunamis are caused by ...", "undersea earthquakes", ["strong winds", "high tides", "whales"]),
    ("Giant circular systems of ocean currents are called ...", "gyres", ["tides", "fjords", "atolls"]),
    ("A ring-shaped coral island is called an ...", "atoll", ["fjord", "delta", "isthmus"]),
    ("Fringing, barrier and atoll are types of ...", "coral reefs", ["tides", "waves", "currents"]),
    ("Mangroves are trees that grow in ...", "salty coastal water", ["deep ocean trenches", "polar ice", "open sea"]),
    ("The shore area between high tide and low tide is called the ...", "intertidal zone", ["abyssal zone", "twilight zone", "hadal zone"]),
    ("What is the longest-living vertebrate known, possibly over 250 years?", "Greenland shark", ["blue whale", "great white shark", "sea otter"]),
    ("What is the largest species of seal?", "southern elephant seal", ["harbor seal", "leopard seal", "monk seal"]),
    ("Which of these has visible outer ear flaps?", "sea lion", ["seal", "walrus", "elephant seal"]),
    ("Sharks and rays belong to which group of fish with skeletons of cartilage?", "cartilaginous fish", ["bony fish", "lobe-finned fish", "ray-finned fish"]),
    ("Which ocean is the 'Ring of Fire' of volcanoes and earthquakes around?", "Pacific Ocean", ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean"]),
]

SCI = {"great white shark": "Carcharodon carcharias", "blue whale": "Balaenoptera musculus", "orca": "Orcinus orca",
       "bottlenose dolphin": "Tursiops truncatus", "green sea turtle": "Chelonia mydas", "giant squid": "Architeuthis dux",
       "common octopus": "Octopus vulgaris", "sea otter": "Enhydra lutris", "emperor penguin": "Aptenodytes forsteri",
       "sperm whale": "Physeter macrocephalus", "humpback whale": "Megaptera novaeangliae", "narwhal": "Monodon monoceros",
       "beluga": "Delphinapterus leucas", "walrus": "Odobenus rosmarus", "whale shark": "Rhincodon typus",
       "ocean sunfish": "Mola mola", "leatherback turtle": "Dermochelys coriacea", "chambered nautilus": "Nautilus pompilius",
       "Atlantic bluefin tuna": "Thunnus thynnus"}

GROUP_NAMES = [("sea otters", "raft", ["pod", "school", "pack"]), ("sharks", "shiver", ["pod", "raft", "parliament"]),
               ("jellyfish", "smack", ["pod", "raft", "herd"]), ("dolphins", "pod", ["raft", "shiver", "smack"]),
               ("orcas", "pod", ["raft", "shiver", "smack"]), ("penguins", "colony", ["raft", "shiver", "smack"]),
               ("fish", "school", ["raft", "shiver", "smack"])]


def _em(x):
    return EMOJI_OF[x]


def build(band):
    r = rng_for("ocean", band)
    out = []
    add = out.append

    # =============================================================== 2-5
    if band == "2-5":
        TOD = {"fish": "🐟", "tropical fish": "🐠", "pufferfish": "🐡", "shark": "🦈", "octopus": "🐙", "squid": "🦑", "shrimp": "🦐",
               "lobster": "🦞", "crab": "🦀", "dolphin": "🐬", "whale": "🐳", "seal": "🦭", "penguin": "🐧", "turtle": "🐢", "otter": "🦦"}
        T = list(TOD)
        CT = [{"fish", "tropical fish", "pufferfish", "shark"}, {"octopus", "squid"}, {"crab", "lobster", "shrimp"}, {"whale", "dolphin"}, {"seal", "otter"}]
        tok = lambda a, b: a != b and not any(a in g and b in g for g in CT)
        for n in T:
            e = TOD[n]
            wrong = [x for x in T if tok(n, x)]
            add(mc(r, "What sea animal is this?", n, wrong, v=emoji(e)))
            for qq in (f"Find the {n}!", f"Which one is the {n}?", f"Where is the {n}?", f"Tap the {n}!"):
                add(mc(r, qq, e, [TOD[x] for x in wrong], ct="emoji"))
            for k in range(1, 6):
                add(num_choices(r, "How many?", k, v=emoji(" ".join([e] * k)), spread=2, lo=1))
        for _ in range(60):
            k = r.randint(2, 8)
            items = [TOD[r.choice(T)] for _ in range(k)]
            add(num_choices(r, "How many sea animals?", k, v=emoji(" ".join(items)), spread=2, lo=1))
        for n in ["fish", "tropical fish", "pufferfish", "shark", "octopus", "squid", "shrimp", "lobster", "crab", "dolphin", "whale"]:
            add(mc(r, "Where does it live?", "🌊", ["🌲", "🌵", "🌋"], v=emoji(TOD[n]), ct="emoji"))
        BIG, SMALL = ["whale", "shark", "dolphin"], ["shrimp", "crab", "tropical fish", "pufferfish", "lobster"]
        for b in BIG:
            for s in SMALL:
                vis = emoji(" ".join(r.sample([TOD[b], TOD[s]], 2)))
                add(mc(r, "Which one is bigger?", TOD[b], [TOD[s]] + r.sample([TOD[x] for x in SMALL if x != s], 2), v=vis, ct="emoji"))
                add(mc(r, "Which one is smaller?", TOD[s], [TOD[b]] + r.sample([TOD[x] for x in BIG if x != b], 2), v=vis, ct="emoji"))
        add(mc(r, "Which one has eight arms?", "🐙", ["🦈", "🐬", "🦀", "🐟"], ct="emoji"))
        add(mc(r, "Which one has big claws?", "🦀", ["🐙", "🐬", "🐟", "🐢"], ct="emoji"))
        add(mc(r, "Which one has a shell?", "🐢", ["🐬", "🐟", "🐧", "🦈"], ct="emoji"))
        add(mc(r, "Which one is black and white?", "🐧", ["🐠", "🦀", "🐙", "🐡"], ct="emoji"))
        add(mc(r, "Which one puffs up like a ball?", "🐡", ["🐬", "🦈", "🐢", "🦀"], ct="emoji"))
        add(mc(r, "Which one squirts ink?", "🐙", ["🦈", "🐬", "🦀", "🐟"], ct="emoji"))
        add(mc(r, "Which one is a big whale?", "🐳", ["🐟", "🦀", "🦐", "🐠"], ct="emoji"))
        add(mc(r, "Which one lives in the sea?", "🐬", ["🐶", "🐱", "🐮", "🐷"], ct="emoji"))
        add(mc(r, "Which one is NOT a sea animal?", "🐶", ["🐙", "🐬", "🦀", "🐠"], ct="emoji"))
        add(mc(r, "What color is the sea?", "🔵", ["🔴", "🟡", "🟢"], ct="emoji"))
        add(mc(r, "Which one waddles on the ice?", "🐧", ["🐬", "🐟", "🦈", "🐠"], ct="emoji"))

    # =============================================================== 6-10
    elif band == "6-10":
        K6 = ["fish", "mammal", "reptile", "bird", "mollusk", "crustacean"]
        for n, d in S.items():
            if n not in KID6: continue
            v = emoji(d["e"]) if d["e"] else None
            if d["e"]:
                add(mc(r, "What sea animal is this?", n, wr(n, EM), v=v))
            if d["g"] in K6:
                add(mc(r, f"What kind of animal is {art(n)}?", d["g"], K6, v=v))
        for n, b in BABY:
            e = E(n) if n in S else None
            add(mc(r, f"What is a baby {n} called?", b, [x for x in BABY_POOL if x != b], v=emoji(e) if e else None))
        for n, f, w in FOOD6:
            e = E(n) if n in S else None
            add(mc(r, f"What does {art(n)} mainly eat?", f, w, v=emoji(e) if e else None))
        allhab = [REEF, DEEP, POLAR, TIDE]
        for n, h in HAB:
            e = E(n) if n in S else None
            add(mc(r, f"Where does {art(n)} live?", h, [x for x in allhab if x != h], v=emoji(e) if e else None))
        for c, qs in (("fish", ("Which of these is a fish?", "Which one is a fish?")), ("mammal", ("Which of these is a mammal?", "Find the mammal!")),
                      ("reptile", ("Which of these is a reptile?",)), ("bird", ("Which of these is a bird?", "Find the bird!")),
                      ("mollusk", ("Which of these is a mollusk?",)), ("crustacean", ("Which of these is a crustacean?",))):
            for qq in qs:
                a = r.choice([n for n in EM if S[n]["g"] == c])
                add(mc(r, qq, E(a), [E(x) for x in EM if S[x]["g"] != c], ct="emoji"))
        add(mc(r, "Which shellfish has big claws?", E("crab"), [E(x) for x in EM if S[x]["g"] != "crustacean"], ct="emoji"))
        for s in lineups(r, LEN_EM, 50, 2.0, "max"):
            add(mc(r, "Which sea animal is the biggest?", s[0], s[1:], v=emoji(" ".join(_em(x) for x in r.sample(s, 4)))))
        for s in lineups(r, LEN_EM, 40, 2.0, "min"):
            add(mc(r, "Which sea animal is the smallest?", s[0], s[1:], v=emoji(" ".join(_em(x) for x in r.sample(s, 4)))))
        for table, phr, d, want, ratio in ((MASS, "heaviest", "max", 30, 3.0), (LEN, "longest", "max", 30, 2.0), (SPEED, "fastest swimmer", "max", 25, 1.8)):
            for s in lineups(r, table, want, ratio, d):
                names = r.sample(s, 4)
                add(mc(r, f"Which of these sea animals is the {phr}: " + ", ".join(names[:-1]) + " or " + names[-1] + "?", s[0], s[1:]))
        for g, a, w in GROUP_NAMES[3:]:
            add(mc(r, f"A group of {g} is called a ...", a, w))
        for q, a, w in FACT6:
            add(mc(r, q, a, w))

    # =============================================================== 11+
    else:
        VERT = ["fish", "mammal", "reptile", "bird"]
        INV = ["mollusk", "crustacean", "cnidarian", "echinoderm", "sponge"]
        for n, d in S.items():
            if n == "fish": continue
            side = VERT if d["g"] in VERT else INV
            add(mc(r, f"Which group does the {n} belong to?", d["g"], [x for x in side if x != d["g"]]))
        pool = list(SCI.values())
        for c, s in SCI.items():
            add(mc(r, f"What is the scientific name of the {c}?", s, pool))
            add(mc(r, f"Which sea animal has the scientific name {s}?", c, list(SCI)))
        for table, f, qmax, qmin, ratio in ((LEN, f_m, "is the longest", "is the shortest", 1.5), (MASS, f_kg, "weighs the most", "weighs the least", 2.0),
                                            (SPEED, f_kmh, "swims the fastest", "is the slowest", 1.5), (LIFE, f_yr, "lives the longest", "has the shortest lifespan", 1.5)):
            for d, phr, want in (("max", qmax, 40), ("min", qmin, 25)):
                for s in lineups(r, table, want, ratio, d):
                    names = r.sample(s, 4)
                    add(mc(r, f"Which of these sea animals {phr}: " + ", ".join(names[:-1]) + " or " + names[-1] + "?", s[0], s[1:]))
        for table, f, kind in ((LEN, f_m, "len"), (MASS, f_kg, "mass"), (LIFE, f_yr, "life")):
            for n, right in table.items():
                near = [f(v) for v in sorted({v for k, v in table.items() if k != n}) if v / right >= 1.8 or right / v >= 1.8]
                if len(near) < 3: continue
                qq = {"len": f"About how long is an adult {n}?", "mass": f"About how much does an adult {n} weigh?", "life": f"About how long can {art(n)} live?"}[kind]
                add(mc(r, qq, f(right), near))
        for q, a, w in FACT11:
            add(mc(r, q, a, w))
        for g, a, w in GROUP_NAMES:
            add(mc(r, f"What is a group of {g} called?", a, w))
    return out
