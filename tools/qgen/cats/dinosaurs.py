from ..common import *

META = {"id": "dinosaurs", "name": "Dinosaurs", "icon": "🦖"}

# name, period, diet, length_m, legs walked on, group, continent, meaning of the name
# (None = unknown / disputed / not used)
ROWS = [
    ("Tyrannosaurus rex", "Cretaceous", "carnivore", 12, 2, "theropod", "North America", "tyrant lizard"),
    ("Triceratops", "Cretaceous", "herbivore", 9, 4, "ceratopsian", "North America", "three-horned face"),
    ("Stegosaurus", "Jurassic", "herbivore", 9, 4, "stegosaur", "North America", "roof lizard"),
    ("Velociraptor", "Cretaceous", "carnivore", 2, 2, "theropod", "Asia", "swift thief"),
    ("Brachiosaurus", "Jurassic", "herbivore", 22, 4, "sauropod", "North America", "arm lizard"),
    ("Diplodocus", "Jurassic", "herbivore", 25, 4, "sauropod", "North America", "double beam"),
    ("Allosaurus", "Jurassic", "carnivore", 9, 2, "theropod", "North America", "different lizard"),
    ("Spinosaurus", "Cretaceous", "carnivore", 14, None, "theropod", "Africa", "spine lizard"),
    ("Ankylosaurus", "Cretaceous", "herbivore", 7, 4, "ankylosaur", "North America", "fused lizard"),
    ("Parasaurolophus", "Cretaceous", "herbivore", 10, None, "hadrosaur", "North America", "near crested lizard"),
    ("Iguanodon", "Cretaceous", "herbivore", 10, None, None, "Europe", "iguana tooth"),
    ("Apatosaurus", "Jurassic", "herbivore", 22, 4, "sauropod", "North America", "deceptive lizard"),
    ("Compsognathus", "Jurassic", "carnivore", 1, 2, "theropod", "Europe", None),
    ("Carnotaurus", "Cretaceous", "carnivore", 8, 2, "theropod", "South America", "meat-eating bull"),
    ("Gallimimus", "Cretaceous", None, 6, 2, "theropod", "Asia", "chicken mimic"),
    ("Pachycephalosaurus", "Cretaceous", None, 4.5, 2, "pachycephalosaur", "North America", "thick-headed lizard"),
    ("Archaeopteryx", "Jurassic", None, 0.5, 2, "theropod", "Europe", "ancient wing"),
    ("Giganotosaurus", "Cretaceous", "carnivore", 12, 2, "theropod", "South America", "giant southern lizard"),
    ("Argentinosaurus", "Cretaceous", "herbivore", 30, 4, "sauropod", "South America", "Argentina lizard"),
    ("Deinonychus", "Cretaceous", "carnivore", 3, 2, "theropod", "North America", "terrible claw"),
    ("Oviraptor", "Cretaceous", None, 2, 2, "theropod", "Asia", "egg thief"),
    ("Protoceratops", "Cretaceous", "herbivore", 2, 4, "ceratopsian", "Asia", "first horned face"),
    ("Dilophosaurus", "Jurassic", "carnivore", 7, 2, "theropod", "North America", "two-crested lizard"),
    ("Megalosaurus", "Jurassic", "carnivore", 9, 2, "theropod", "Europe", "great lizard"),
    ("Microraptor", "Cretaceous", "carnivore", 0.8, None, "theropod", "Asia", "small thief"),
    ("Coelophysis", "Triassic", "carnivore", 3, 2, "theropod", "North America", "hollow form"),
    ("Plateosaurus", "Triassic", None, 8, None, None, "Europe", "flat lizard"),
    ("Brontosaurus", "Jurassic", "herbivore", 22, 4, "sauropod", "North America", "thunder lizard"),
    ("Edmontosaurus", "Cretaceous", "herbivore", 12, None, "hadrosaur", "North America", "lizard from Edmonton"),
    ("Maiasaura", "Cretaceous", "herbivore", 9, None, "hadrosaur", "North America", "good mother lizard"),
    ("Troodon", "Cretaceous", None, 2.5, 2, "theropod", "North America", "wounding tooth"),
    ("Therizinosaurus", "Cretaceous", None, 10, 2, "theropod", "Asia", "scythe lizard"),
    ("Utahraptor", "Cretaceous", "carnivore", 6, 2, "theropod", "North America", "Utah thief"),
    ("Baryonyx", "Cretaceous", "carnivore", 9, None, "theropod", "Europe", "heavy claw"),
    ("Ceratosaurus", "Jurassic", "carnivore", 6, 2, "theropod", "North America", "horned lizard"),
    ("Camarasaurus", "Jurassic", "herbivore", 15, 4, "sauropod", "North America", "chambered lizard"),
    ("Styracosaurus", "Cretaceous", "herbivore", 5.5, 4, "ceratopsian", "North America", "spiked lizard"),
    ("Corythosaurus", "Cretaceous", "herbivore", 9, None, "hadrosaur", "North America", "helmet lizard"),
    ("Mamenchisaurus", "Jurassic", "herbivore", 22, 4, "sauropod", "Asia", None),
    ("Kentrosaurus", "Jurassic", "herbivore", 4.5, 4, "stegosaur", "Africa", None),
    ("Albertosaurus", "Cretaceous", "carnivore", 9, 2, "theropod", "North America", "Alberta lizard"),
    ("Dreadnoughtus", "Cretaceous", "herbivore", 26, 4, "sauropod", "South America", "fears nothing"),
    ("Patagotitan", "Cretaceous", "herbivore", 31, 4, "sauropod", "South America", "Patagonian giant"),
    ("Psittacosaurus", "Cretaceous", "herbivore", 2, None, "ceratopsian", "Asia", "parrot lizard"),
    ("Herrerasaurus", "Triassic", "carnivore", 4, 2, None, "South America", None),
    ("Eoraptor", "Triassic", None, 1, 2, None, "South America", "dawn thief"),
    ("Tarbosaurus", "Cretaceous", "carnivore", 10, 2, "theropod", "Asia", "alarming lizard"),
    ("Suchomimus", "Cretaceous", "carnivore", 11, None, "theropod", "Africa", "crocodile mimic"),
    ("Pachyrhinosaurus", "Cretaceous", "herbivore", 6, 4, "ceratopsian", "North America", "thick-nosed lizard"),
    ("Saltasaurus", "Cretaceous", "herbivore", 9, 4, "sauropod", "South America", None),
    ("Nigersaurus", "Cretaceous", "herbivore", 9, 4, "sauropod", "Africa", None),
    ("Giraffatitan", "Jurassic", "herbivore", 22, 4, "sauropod", "Africa", "giant giraffe"),
    ("Euoplocephalus", "Cretaceous", "herbivore", 6, 4, "ankylosaur", "North America", "well-armored head"),
    ("Minmi", "Cretaceous", "herbivore", 3, 4, "ankylosaur", "Australia", None),
    ("Muttaburrasaurus", "Cretaceous", "herbivore", 8, None, None, "Australia", None),
    ("Sinosauropteryx", "Cretaceous", "carnivore", 1, 2, "theropod", "Asia", None),
    ("Amargasaurus", "Cretaceous", "herbivore", 10, 4, "sauropod", "South America", None),
]
D = {r[0]: dict(name=r[0], period=r[1], diet=r[2], len=r[3], legs=r[4], group=r[5], cont=r[6], mean=r[7]) for r in ROWS}
NAMES = list(D)
SHORT = {"Tyrannosaurus rex": "T. rex"}
PERIODS = ["Triassic", "Jurassic", "Cretaceous"]
FAMOUS = ["Tyrannosaurus rex", "Triceratops", "Stegosaurus", "Velociraptor", "Brachiosaurus", "Diplodocus", "Allosaurus", "Spinosaurus",
          "Ankylosaurus", "Iguanodon", "Apatosaurus", "Carnotaurus", "Gallimimus", "Pachycephalosaurus", "Archaeopteryx", "Deinonychus",
          "Oviraptor", "Protoceratops", "Maiasaura", "Parasaurolophus", "Megalosaurus", "Brontosaurus", "Coelophysis", "Plateosaurus",
          "Giganotosaurus", "Argentinosaurus", "Dilophosaurus", "Troodon", "Therizinosaurus", "Utahraptor"]
KID2 = ["Tyrannosaurus rex", "Triceratops", "Stegosaurus", "Velociraptor", "Brachiosaurus", "Diplodocus", "Allosaurus", "Ankylosaurus",
        "Apatosaurus", "Brontosaurus", "Spinosaurus", "Parasaurolophus", "Giganotosaurus", "Argentinosaurus", "Carnotaurus", "Dilophosaurus",
        "Deinonychus", "Protoceratops", "Iguanodon", "Compsognathus", "Utahraptor", "Pachycephalosaurus", "Coelophysis", "Maiasaura"]
KID6 = FAMOUS + ["Styracosaurus", "Corythosaurus", "Edmontosaurus", "Baryonyx", "Camarasaurus", "Dreadnoughtus", "Patagotitan",
                 "Ceratosaurus", "Albertosaurus", "Kentrosaurus", "Psittacosaurus", "Tarbosaurus", "Microraptor", "Mamenchisaurus"]
SAUROPODS = {n for n in D if D[n]["group"] == "sauropod"}


def vis(n):
    if n == "Tyrannosaurus rex": return emoji("🦖")
    if n in SAUROPODS: return emoji("🦕")
    return None


def fmt_m(x): return f"{x:g} m"


def lineups(r, want, ratio, direction, key, pred=lambda n: True, tries=5000):
    names = [n for n in D if D[n][key] is not None and pred(n)]
    seen, out = set(), []
    for _ in range(tries):
        s = r.sample(names, 4)
        s.sort(key=lambda n: D[n][key], reverse=(direction == "max"))
        a, b = D[s[0]][key], D[s[1]][key]
        if direction == "max" and a < b * ratio: continue
        if direction == "min" and b < a * ratio: continue
        if frozenset(s) in seen: continue
        seen.add(frozenset(s)); out.append(s)
        if len(out) >= want: break
    return out


FACT6 = [
    ("What does the word dinosaur mean?", "terrible lizard", ["giant bird", "big tooth", "old dragon"]),
    ("What do we call a scientist who studies dinosaur fossils?", "paleontologist", ["astronomer", "chemist", "meteorologist"]),
    ("What are fossils?", "remains or prints of ancient living things in rock", ["toys made of stone", "bones of animals alive today", "rocks that fell from space"]),
    ("Dinosaurs lived about how long ago?", "millions of years ago", ["100 years ago", "last week", "1,000 years ago"]),
    ("Which dinosaur had three horns on its face?", "Triceratops", ["Tyrannosaurus rex", "Stegosaurus", "Velociraptor"]),
    ("Which dinosaur had big plates on its back?", "Stegosaurus", ["Triceratops", "Tyrannosaurus rex", "Diplodocus"]),
    ("Which dinosaur had a bony club on its tail?", "Ankylosaurus", ["Triceratops", "Velociraptor", "Tyrannosaurus rex"]),
    ("Which dinosaur had a very long neck and ate leaves from tall trees?", "Brachiosaurus", ["Tyrannosaurus rex", "Triceratops", "Velociraptor"]),
    ("Which dinosaur's name means 'tyrant lizard king'?", "Tyrannosaurus rex", ["Triceratops", "Stegosaurus", "Diplodocus"]),
    ("Which fast hunter was about as big as a turkey?", "Velociraptor", ["Tyrannosaurus rex", "Brachiosaurus", "Stegosaurus"]),
    ("Pterodactyls could fly. Were they dinosaurs?", "No, they were flying reptiles", ["Yes, they were dinosaurs", "Yes, they were birds", "No, they were bats"]),
    ("Which of these was NOT a dinosaur?", "woolly mammoth", ["Triceratops", "Stegosaurus", "Brachiosaurus"]),
    ("Which one was NOT a dinosaur?", "saber-toothed cat", ["Tyrannosaurus rex", "Diplodocus", "Allosaurus"]),
    ("Which of these animals was NOT a dinosaur?", "Pteranodon", ["Velociraptor", "Ankylosaurus", "Iguanodon"]),
    ("Which one lived in the sea and was NOT a dinosaur?", "Mosasaurus", ["Triceratops", "Spinosaurus", "Apatosaurus"]),
    ("Today's birds are relatives of which ancient animals?", "dinosaurs", ["fish", "frogs", "mammoths"]),
    ("What do we call dinosaurs that ate only plants?", "herbivores", ["carnivores", "omnivores", "insectivores"]),
    ("What do we call dinosaurs that ate only meat?", "carnivores", ["herbivores", "omnivores", "vegetarians"]),
    ("How were baby dinosaurs born?", "they hatched from eggs", ["they were born live like puppies", "they grew from seeds", "they came out of pouches"]),
    ("How do we know about dinosaurs today?", "from fossils", ["from photographs", "from old videos", "from diaries"]),
    ("What do we call dinosaur footprints that were turned to stone?", "fossil tracks", ["fossil eggs", "fossil teeth", "fossil leaves"]),
    ("The age of the dinosaurs is called the ...", "Mesozoic Era", ["Cenozoic Era", "Paleozoic Era", "Stone Age"]),
    ("What is a coprolite?", "fossil dinosaur poop", ["a fossil egg", "a fossil tooth", "a fossil bone"]),
    ("How many fingers did a T. rex have on each hand?", "2", ["1", "3", "5"]),
    ("How many horns did a Triceratops have?", "3", ["1", "2", "5"]),
    ("Which dinosaur had a big sail on its back and loved to eat fish?", "Spinosaurus", ["Triceratops", "Ankylosaurus", "Velociraptor"]),
    ("Which dinosaur had a crest on its head like a long trumpet?", "Parasaurolophus", ["Triceratops", "Stegosaurus", "Allosaurus"]),
    ("Which dinosaur had a thick, bony dome on its head?", "Pachycephalosaurus", ["Stegosaurus", "Diplodocus", "Spinosaurus"]),
    ("Which dinosaur is named 'good mother lizard' because it cared for its nest?", "Maiasaura", ["Velociraptor", "Allosaurus", "Spinosaurus"]),
    ("Which dinosaur had a sharp spike on each thumb?", "Iguanodon", ["Triceratops", "Stegosaurus", "Brachiosaurus"]),
    ("Which dinosaur had a 'terrible claw' on each foot?", "Deinonychus", ["Triceratops", "Diplodocus", "Ankylosaurus"]),
    ("What did the biggest dinosaurs eat?", "plants", ["other dinosaurs", "fish only", "ice cream"]),
    ("How many legs did a T. rex walk on?", "2", ["4", "6", "8"]),
    ("Which dinosaur walked on four legs and had a big bony frill?", "Triceratops", ["Tyrannosaurus rex", "Velociraptor", "Allosaurus"]),
    ("Which was longer: a Diplodocus or a school bus?", "Diplodocus", ["a school bus", "they were the same", "a bicycle"]),
    ("Which came first on Earth?", "dinosaurs", ["people", "cars", "castles"]),
    ("What probably caused the dinosaurs to die out?", "a giant space rock hit Earth", ["people hunted them", "the Moon got too close", "all the water dried up"]),
    ("Which two dinosaurs lived at the same time?", "Tyrannosaurus rex and Triceratops", ["Tyrannosaurus rex and Stegosaurus", "Stegosaurus and Velociraptor", "Allosaurus and Triceratops"]),
]

FACT11 = [
    ("The Mesozoic Era is made up of which three periods?", "Triassic, Jurassic, Cretaceous", ["Permian, Triassic, Jurassic", "Jurassic, Cretaceous, Tertiary", "Devonian, Permian, Triassic"]),
    ("Which period came right after the Triassic?", "Jurassic", ["Cretaceous", "Permian", "Devonian"]),
    ("Which was the last period of the Mesozoic Era?", "Cretaceous", ["Jurassic", "Triassic", "Permian"]),
    ("Which was the first period in which dinosaurs appeared?", "Triassic", ["Jurassic", "Cretaceous", "Permian"]),
    ("About how long ago did the non-bird dinosaurs go extinct?", "66 million years ago", ["6 million years ago", "250 million years ago", "10,000 years ago"]),
    ("Where is the Chicxulub impact crater, linked to the dinosaur extinction?", "Yucatan Peninsula, Mexico", ["Siberia, Russia", "Antarctica", "Western Australia"]),
    ("A thin layer of which rare element at the end of the Cretaceous supports the asteroid-impact idea?", "iridium", ["gold", "uranium", "carbon"]),
    ("Birds evolved from which group of dinosaurs?", "theropods", ["sauropods", "ceratopsians", "stegosaurs"]),
    ("Which means 'bird-hipped'?", "Ornithischia", ["Saurischia", "Theropoda", "Sauropoda"]),
    ("Which means 'lizard-hipped'?", "Saurischia", ["Ornithischia", "Ceratopsia", "Hadrosauridae"]),
    ("Plesiosaurs, ichthyosaurs and mosasaurs were ...", "marine reptiles, not dinosaurs", ["the biggest dinosaurs", "early birds", "dinosaur eggs"]),
    ("Dimetrodon, with its big sail, lived before the dinosaurs in which period?", "Permian", ["Jurassic", "Cretaceous", "Triassic"]),
    ("The largest mass extinction ever, about 252 million years ago, ended which period?", "Permian", ["Triassic", "Jurassic", "Cretaceous"]),
    ("What are stones swallowed by some dinosaurs to help grind food called?", "gastroliths", ["coprolites", "geodes", "stalactites"]),
    ("What is fossilized dinosaur dung called?", "coprolite", ["gastrolith", "amber", "trilobite"]),
    ("What do we call a line of fossil footprints?", "a trackway", ["a coprolite", "a gastrolith", "a trilobite"]),
    ("Most fossils are found in which type of rock?", "sedimentary rock", ["igneous rock", "metamorphic rock", "crystal"]),
    ("Which scientist invented the word 'Dinosauria' in 1842?", "Richard Owen", ["Charles Darwin", "Mary Anning", "Gregor Mendel"]),
    ("Which fossil, found in Germany in 1861, links dinosaurs and birds?", "Archaeopteryx", ["Velociraptor", "Triceratops", "Stegosaurus"]),
    ("The famous T. rex skeleton named 'Sue' is displayed in which city?", "Chicago", ["London", "Paris", "Sydney"]),
    ("Microraptor had feathers on how many limbs, making it 'four-winged'?", "four", ["two", "three", "six"]),
    ("The first birds like Archaeopteryx lived in which period?", "Jurassic", ["Triassic", "Cretaceous", "Permian"]),
    ("Which is true about T. rex and Stegosaurus?", "T. rex lived closer in time to us than to Stegosaurus", ["They lived at the same time", "Stegosaurus lived closer in time to us than T. rex", "T. rex hunted Stegosaurus"]),
    ("Which dinosaur lived at the same time as T. rex?", "Triceratops", ["Stegosaurus", "Brachiosaurus", "Allosaurus"]),
    ("Which dinosaur lived at the same time as Stegosaurus?", "Allosaurus", ["Tyrannosaurus rex", "Triceratops", "Velociraptor"]),
    ("Which group of dinosaurs includes Triceratops and Styracosaurus?", "ceratopsians", ["sauropods", "theropods", "stegosaurs"]),
    ("Which group of dinosaurs includes the duck-billed Edmontosaurus?", "hadrosaurs", ["ceratopsians", "sauropods", "theropods"]),
    ("Which two-legged dinosaur group included T. rex and Velociraptor?", "theropods", ["sauropods", "ankylosaurs", "hadrosaurs"]),
    ("The 'dome-headed' dinosaurs belong to which group?", "pachycephalosaurs", ["ceratopsians", "stegosaurs", "ankylosaurs"]),
    ("The giant long-necked dinosaurs belong to which group?", "sauropods", ["theropods", "ceratopsians", "hadrosaurs"]),
    ("Which group of armored dinosaurs had tail clubs?", "ankylosaurs", ["stegosaurs", "sauropods", "theropods"]),
    ("A thagomizer is the name for the spikes on the tail of a ...", "Stegosaurus", ["Triceratops", "Brachiosaurus", "Velociraptor"]),
    ("Fossils of Maiasaura nests suggest that it ...", "cared for its young", ["ate its eggs", "flew to new nests", "buried its eggs in the sea"]),
    ("Which pair of dinosaurs lived in different periods?", "Stegosaurus and Tyrannosaurus rex", ["Tyrannosaurus rex and Triceratops", "Brachiosaurus and Stegosaurus", "Triceratops and Edmontosaurus"]),
    ("Which dinosaur is thought to have eaten mainly fish and had a sail?", "Spinosaurus", ["Allosaurus", "Triceratops", "Diplodocus"]),
    ("In which country were Velociraptor fossils found?", "Mongolia", ["Argentina", "Canada", "Australia"]),
]

GROUPS = ["theropod", "sauropod", "ceratopsian", "stegosaur", "ankylosaur", "hadrosaur", "pachycephalosaur"]
CONTS = ["North America", "South America", "Europe", "Asia", "Africa", "Australia"]


def build(band):
    r = rng_for("dinosaurs", band)
    out = []
    add = out.append

    # =============================================================== 2-5
    if band == "2-5":
        def spread(a, b):
            items = ["🦖"] * a + ["🦕"] * b
            r.shuffle(items)
            return emoji(" ".join(items))
        for a in range(0, 6):
            for b in range(0, 6):
                if a + b == 0: continue
                if a >= 1:
                    add(num_choices(r, "How many 🦖 can you see?", a, v=spread(a, b), spread=2, lo=1))
                if b >= 1:
                    add(num_choices(r, "How many 🦕 can you see?", b, v=spread(a, b), spread=2, lo=1))
                add(num_choices(r, "How many dinosaurs are there?", a + b, v=spread(a, b), spread=2, lo=1))
        for sym, nm in (("🥚", "eggs"), ("🦴", "bones"), ("🌿", "leaves"), ("🐾", "footprints"), ("🌋", "volcanoes"), ("🌴", "palm trees")):
            for k in range(1, 8 if sym in ("🥚", "🦴", "🌿", "🐾") else 6):
                add(num_choices(r, f"How many {nm}?", k, v=emoji(" ".join([sym] * k)), spread=2, lo=1))
        FOOD = ["Plants", "Meat", "Pizza", "Toys"]
        for n in KID2:
            d = D[n]
            if d["diet"]:
                ans = "Plants" if d["diet"] == "herbivore" else "Meat"
                add(mc(r, f"Did {SHORT.get(n, n)} eat plants or meat?", ans, [x for x in FOOD if x != ans], v=vis(n)))
                add(mc(r, f"What did {SHORT.get(n, n)} like to eat?", ans, [x for x in ("Cake", "Pizza", "Toys", "Ice cream")], v=vis(n)))
            if d["legs"]:
                add(mc(r, f"How many legs did {SHORT.get(n, n)} walk on?", str(d["legs"]), list("2468"), v=vis(n)))
                add(mc(r, f"{SHORT.get(n, n)} walked on how many legs?", str(d["legs"]), list("2468"), v=vis(n)))
        add(mc(r, "How many legs does it walk on?", "2", list("468"), v=emoji("🦖")))
        add(mc(r, "How many legs does this one have?", "4", list("268"), v=emoji("🦕")))
        non = ["🐶", "🐱", "🐮", "🐷", "🐴", "🐑", "🦆", "🐸", "🐘", "🦁", "🐻", "🐰"]
        add(mc(r, "Which one is a dinosaur?", "🦖", r.sample(non, 4), ct="emoji"))
        add(mc(r, "Find the dinosaur!", "🦕", r.sample(non, 4), ct="emoji"))
        add(mc(r, "Which one is a T. rex?", "🦖", ["🦕", "🐊", "🐍"], ct="emoji"))
        add(mc(r, "Which dinosaur has a long neck?", "🦕", ["🦖", "🐊", "🐍", "🐢"], ct="emoji"))
        add(mc(r, "Which dinosaur has big teeth?", "🦖", ["🦕", "🐮", "🐑", "🐴"], ct="emoji"))
        add(mc(r, "Which dinosaur is the T. rex?", "🦖", ["🦕", "🦎", "🐢", "🐊"], ct="emoji"))
        add(mc(r, "Which one is a long-neck dinosaur?", "🦕", ["🦖", "🦎", "🐸", "🐍"], ct="emoji"))
        add(mc(r, "What does a dinosaur say?", "Roar!", ["Moo!", "Quack!", "Meow!"]))
        add(mc(r, "What did baby dinosaurs hatch from?", "🥚", ["🍎", "🎈", "🌽"], ct="emoji"))
        add(mc(r, "What came out of a dinosaur egg?", "🦖", ["🐥", "🐸", "🐍"], ct="emoji"))

    # =============================================================== 6-10
    elif band == "6-10":
        PER6 = PERIODS + ["Ice Age"]
        for n in KID6:
            d = D[n]
            nm = SHORT.get(n, n)
            add(mc(r, f"When did {nm} live?", d["period"], [p for p in PER6 if p != d["period"]], v=vis(n)))
            if d["diet"]:
                add(mc(r, f"Was {nm} a herbivore, carnivore or omnivore?", d["diet"], ["herbivore", "carnivore", "omnivore", "insectivore"], v=vis(n)))
            if d["legs"]:
                add(mc(r, f"How many legs did {nm} walk on?", str(d["legs"]), list("2468"), v=vis(n)))
            if d["mean"] and n in FAMOUS:
                means = [x["mean"] for x in D.values() if x["mean"] and x["mean"] != d["mean"]]
                add(mc(r, f"What does the name {n} mean?", d["mean"], means, v=vis(n)))
        for n in FAMOUS:
            d = D[n]
            if d["mean"] and sum(1 for x in D.values() if x["mean"] == d["mean"]) == 1:
                add(mc(r, f"Which dinosaur's name means '{d['mean']}'?", n, [x for x in FAMOUS if x != n]))
        for s in lineups(r, 45, 2.0, "max", "len", lambda n: n in KID6):
            add(_longest(r, s, "longest"))
        for s in lineups(r, 35, 2.0, "min", "len", lambda n: n in KID6):
            add(_longest(r, s, "shortest"))
        herb = [n for n in KID6 if D[n]["diet"] == "herbivore"]
        carn = [n for n in KID6 if D[n]["diet"] == "carnivore"]
        seen = set()
        for _ in range(60):
            a = r.choice(herb); bs = r.sample(carn, 3)
            names = r.sample([a] + bs, 4)
            qq = "Which of these dinosaurs ate only plants: " + ", ".join(SHORT.get(x, x) for x in names[:-1]) + " or " + SHORT.get(names[-1], names[-1]) + "?"
            if qq in seen: continue
            seen.add(qq); add(mc(r, qq, SHORT.get(a, a), [SHORT.get(x, x) for x in bs]))
        for _ in range(60):
            a = r.choice(carn); bs = r.sample(herb, 3)
            names = r.sample([a] + bs, 4)
            qq = "Which of these dinosaurs ate meat: " + ", ".join(SHORT.get(x, x) for x in names[:-1]) + " or " + SHORT.get(names[-1], names[-1]) + "?"
            if qq in seen: continue
            seen.add(qq); add(mc(r, qq, SHORT.get(a, a), [SHORT.get(x, x) for x in bs]))
        for q, a, w in FACT6:
            add(mc(r, q, a, w))

    # =============================================================== 11+
    else:
        PER11 = PERIODS + ["Permian"]
        for n, d in D.items():
            nm = SHORT.get(n, n)
            add(mc(r, f"In which period did {nm} live?", d["period"], [p for p in PER11 if p != d["period"]], v=vis(n)))
            add(mc(r, f"On which continent were {nm} fossils first found?", d["cont"], [c for c in CONTS if c != d["cont"]]))
            if d["group"]:
                add(mc(r, f"Which dinosaur group did {nm} belong to?", d["group"], [g for g in GROUPS if g != d["group"]], v=vis(n)))
            if d["mean"]:
                means = [x["mean"] for x in D.values() if x["mean"] and x["mean"] != d["mean"]]
                add(mc(r, f"What does the name {n} mean?", d["mean"], means))
                if sum(1 for x in D.values() if x["mean"] == d["mean"]) == 1:
                    add(mc(r, f"Which dinosaur's name means '{d['mean']}'?", n, [x for x in NAMES if x != n and D[x]["mean"]]))
            near = [fmt_m(x) for x in sorted({v["len"] for k, v in D.items() if k != n}) if x / d["len"] >= 1.6 or d["len"] / x >= 1.6]
            if len(near) >= 3:
                add(mc(r, f"About how long was {nm}?", fmt_m(d["len"]), near))
        for s in lineups(r, 70, 1.5, "max", "len"):
            add(_longest(r, s, "longest"))
        for s in lineups(r, 50, 1.5, "min", "len"):
            add(_longest(r, s, "shortest"))
        for per in PERIODS:
            inp = [n for n in D if D[n]["period"] == per]
            outp = [n for n in D if D[n]["period"] != per]
            seen = set()
            for _ in range(60):
                a = r.choice(inp); bs = r.sample(outp, 3)
                names = r.sample([a] + bs, 4)
                qq = f"Which of these dinosaurs lived in the {per}: " + ", ".join(SHORT.get(x, x) for x in names[:-1]) + " or " + SHORT.get(names[-1], names[-1]) + "?"
                if qq in seen: continue
                seen.add(qq); add(mc(r, qq, SHORT.get(a, a), [SHORT.get(x, x) for x in bs]))
        for q, a, w in FACT11:
            add(mc(r, q, a, w))
    return out


def _longest(r, s, phr):
    names = r.sample(s, 4)
    qq = f"Which of these dinosaurs was the {phr}: " + ", ".join(SHORT.get(x, x) for x in names[:-1]) + " or " + SHORT.get(names[-1], names[-1]) + "?"
    return mc(r, qq, SHORT.get(s[0], s[0]), [SHORT.get(x, x) for x in s[1:]])
