from ..common import *

META = {"id": "animals", "name": "Animals", "icon": "🐾"}

# name, emoji, class, legs (None = skip), diet (None = skip), baby, sound
ROWS = [
    ("dog", "🐶", "mammal", 4, None, "puppy", "woof"),
    ("cat", "🐱", "mammal", 4, "carnivore", "kitten", "meow"),
    ("cow", "🐮", "mammal", 4, "herbivore", "calf", "moo"),
    ("pig", "🐷", "mammal", 4, "omnivore", "piglet", "oink"),
    ("horse", "🐴", "mammal", 4, "herbivore", "foal", "neigh"),
    ("sheep", "🐑", "mammal", 4, "herbivore", "lamb", "baa"),
    ("goat", "🐐", "mammal", 4, "herbivore", "kid", None),
    ("chicken", "🐔", "bird", 2, "omnivore", "chick", "cluck"),
    ("rooster", "🐓", "bird", 2, "omnivore", None, "cock-a-doodle-doo"),
    ("duck", "🦆", "bird", 2, "omnivore", "duckling", "quack"),
    ("turkey", "🦃", "bird", 2, "omnivore", "poult", "gobble"),
    ("frog", "🐸", "amphibian", 4, None, "tadpole", "ribbit"),
    ("lion", "🦁", "mammal", 4, "carnivore", "cub", "roar"),
    ("tiger", "🐯", "mammal", 4, "carnivore", "cub", "roar"),
    ("leopard", "🐆", "mammal", 4, "carnivore", "cub", None),
    ("bear", "🐻", "mammal", 4, "omnivore", "cub", "growl"),
    ("elephant", "🐘", "mammal", 4, "herbivore", "calf", "trumpet"),
    ("monkey", "🐵", "mammal", None, None, None, None),
    ("gorilla", "🦍", "mammal", None, None, None, None),
    ("orangutan", "🦧", "mammal", None, None, None, None),
    ("giraffe", "🦒", "mammal", 4, "herbivore", "calf", None),
    ("zebra", "🦓", "mammal", 4, "herbivore", "foal", None),
    ("rhino", "🦏", "mammal", 4, "herbivore", "calf", None),
    ("hippo", "🦛", "mammal", 4, "herbivore", "calf", None),
    ("kangaroo", "🦘", "mammal", None, "herbivore", "joey", None),
    ("koala", "🐨", "mammal", 4, "herbivore", "joey", None),
    ("panda", "🐼", "mammal", 4, "herbivore", "cub", None),
    ("wolf", "🐺", "mammal", 4, "carnivore", None, "howl"),
    ("fox", "🦊", "mammal", 4, "omnivore", None, None),
    ("raccoon", "🦝", "mammal", 4, "omnivore", None, None),
    ("deer", "🦌", "mammal", 4, "herbivore", "fawn", None),
    ("rabbit", "🐰", "mammal", 4, "herbivore", "bunny", None),
    ("mouse", "🐭", "mammal", 4, "omnivore", None, "squeak"),
    ("hamster", "🐹", "mammal", 4, None, None, None),
    ("squirrel", "🐿️", "mammal", 4, None, None, None),
    ("hedgehog", "🦔", "mammal", 4, None, None, None),
    ("bat", "🦇", "mammal", 2, None, "pup", None),
    ("camel", "🐪", "mammal", 4, "herbivore", "calf", None),
    ("llama", "🦙", "mammal", 4, "herbivore", "cria", None),
    ("sloth", "🦥", "mammal", 4, "herbivore", None, None),
    ("otter", "🦦", "mammal", 4, "carnivore", "pup", None),
    ("skunk", "🦨", "mammal", 4, "omnivore", None, None),
    ("beaver", "🦫", "mammal", 4, "herbivore", "kit", None),
    ("bison", "🦬", "mammal", 4, "herbivore", "calf", None),
    ("seal", "🦭", "mammal", None, "carnivore", "pup", None),
    ("dolphin", "🐬", "mammal", None, "carnivore", "calf", None),
    ("whale", "🐳", "mammal", None, None, "calf", None),
    ("owl", "🦉", "bird", 2, "carnivore", "owlet", "hoot"),
    ("eagle", "🦅", "bird", 2, "carnivore", "eaglet", None),
    ("parrot", "🦜", "bird", 2, None, "chick", None),
    ("penguin", "🐧", "bird", 2, "carnivore", "chick", None),
    ("flamingo", "🦩", "bird", 2, None, "chick", None),
    ("swan", "🦢", "bird", 2, None, "cygnet", None),
    ("peacock", "🦚", "bird", 2, None, None, None),
    ("snake", "🐍", "reptile", 0, "carnivore", None, "hiss"),
    ("turtle", "🐢", "reptile", 4, None, "hatchling", None),
    ("crocodile", "🐊", "reptile", 4, "carnivore", "hatchling", None),
    ("lizard", "🦎", "reptile", 4, None, None, None),
    ("fish", "🐟", "fish", 0, None, "fry", None),
    ("shark", "🦈", "fish", 0, "carnivore", "pup", None),
    ("bee", "🐝", "insect", 6, None, "larva", "buzz"),
    ("butterfly", "🦋", "insect", 6, None, "caterpillar", None),
    ("ant", "🐜", "insect", 6, None, None, None),
    ("ladybug", "🐞", "insect", 6, None, None, None),
    ("beetle", "🪲", "insect", 6, None, None, None),
    ("cricket", "🦗", "insect", 6, None, None, "chirp"),
    ("mosquito", "🦟", "insect", 6, None, None, None),
    ("spider", "🕷️", "arachnid", 8, None, None, None),
    ("scorpion", "🦂", "arachnid", 8, None, None, None),
    ("snail", "🐌", "mollusk", 0, None, None, None),
    ("octopus", "🐙", "mollusk", None, None, None, None),
    ("crab", "🦀", "crustacean", None, None, None, None),
    # text-only animals (no emoji)
    ("polar bear", None, "mammal", 4, "carnivore", "cub", None),
    ("cheetah", None, "mammal", 4, "carnivore", "cub", None),
    ("goose", None, "bird", 2, None, "gosling", "honk"),
    ("ostrich", None, "bird", 2, None, "chick", None),
    ("alligator", None, "reptile", 4, "carnivore", "hatchling", None),
    ("hawk", None, "bird", 2, "carnivore", None, None),
    ("toucan", None, "bird", 2, None, None, None),
]
A = {r[0]: dict(name=r[0], e=r[1], cls=r[2], legs=r[3], diet=r[4], baby=r[5], sound=r[6]) for r in ROWS}
EM = [n for n in A if A[n]["e"]]            # animals that have an emoji
CONF = [{"bear", "panda", "polar bear"}, {"fish", "shark"}, {"cat", "lion", "tiger", "leopard", "cheetah"},
        {"dog", "wolf", "fox"}, {"monkey", "gorilla", "orangutan"}, {"duck", "swan", "goose"},
        {"chicken", "rooster", "turkey"}, {"mouse", "hamster"}, {"horse", "zebra"}, {"sheep", "goat"},
        {"cow", "bison"}, {"crocodile", "alligator"}, {"eagle", "hawk"}, {"whale", "dolphin"},
        {"octopus"}]


def ok(a, b):
    return a != b and not any(a in g and b in g for g in CONF)


def wr(ans, pool):
    return [x for x in pool if ok(ans, x)]


def cap(s): return s[0].upper() + s[1:]
def art(n): return ("an " if n[0].lower() in "aeiou" else "a ") + n
def E(n): return A[n]["e"]


# ------------------------------------------------------------------ numeric tables (approximate adult values)
MASS = {"blue whale": 150000, "sperm whale": 40000, "orca": 5000, "African elephant": 6000, "white rhino": 2300, "hippo": 1500,
        "giraffe": 1200, "walrus": 1200, "horse": 500, "cow": 650, "camel": 550, "polar bear": 450, "tiger": 220, "lion": 190,
        "gorilla": 160, "ostrich": 110, "giant panda": 100, "red kangaroo": 85, "sheep": 80, "wolf": 40, "emperor penguin": 30,
        "koala": 9, "red fox": 6, "bald eagle": 5, "house cat": 4, "rabbit": 2, "house mouse": 0.02, "bee hummingbird": 0.002}
MASS_EM = {"elephant": 6000, "whale": 100000, "rhino": 2300, "hippo": 1500, "giraffe": 1200, "horse": 500, "cow": 650, "bear": 300,
           "lion": 190, "tiger": 220, "panda": 100, "kangaroo": 85, "sheep": 80, "wolf": 40, "penguin": 30, "koala": 9, "eagle": 5,
           "cat": 4, "rabbit": 2, "mouse": 0.02, "bee": 0.0001, "dolphin": 200, "camel": 550}
SPEED = {"cheetah": 110, "pronghorn": 88, "lion": 80, "ostrich": 70, "horse": 70, "kangaroo": 70, "zebra": 65, "wolf": 60,
         "giraffe": 55, "rabbit": 55, "domestic cat": 48, "elephant": 40, "polar bear": 40, "squirrel": 30, "pig": 18,
         "chicken": 14, "house mouse": 13, "sloth": 0.2, "garden snail": 0.05}
SPEED_EM = {"lion": 80, "horse": 70, "kangaroo": 70, "zebra": 65, "wolf": 60, "giraffe": 55, "rabbit": 55, "cat": 48, "elephant": 40,
            "pig": 18, "chicken": 14, "mouse": 13, "sloth": 0.2, "snail": 0.05}
LIFE = {"Greenland shark": 250, "bowhead whale": 200, "giant tortoise": 150, "African elephant": 65, "blue whale": 80, "macaw": 50,
        "horse": 28, "cow": 20, "bald eagle": 25, "lion": 14, "dog": 12, "house cat": 15, "rabbit": 9, "chicken": 8,
        "hamster": 2.5, "house mouse": 2, "mayfly": 0.003}


def fmt_kg(x):
    if x >= 1000: return f"{x:,.0f} kg"
    if x >= 1: return f"{x:g} kg"
    return f"{x * 1000:g} g"


def fmt_kmh(x): return f"{x:g} km/h"


def fmt_yr(x):
    if x < 0.01: return "1 day"
    return f"{x:g} years"


def lineups(r, table, want, ratio, direction, tries=4000):
    """yield 4-name lists where the extreme (max/min) is separated from the runner-up by >= ratio."""
    names = list(table)
    seen, out = set(), []
    for _ in range(tries):
        s = r.sample(names, 4)
        s.sort(key=lambda n: table[n], reverse=(direction == "max"))
        a, b = table[s[0]], table[s[1]]
        if direction == "max" and a < b * ratio: continue
        if direction == "min" and b < a * ratio: continue
        key = frozenset(s)
        if key in seen: continue
        seen.add(key); out.append(s)
        if len(out) >= want: break
    return out


# ------------------------------------------------------------------ fact banks: (question, answer, [wrong answers])
GROUP_NAMES = [("lions", "pride", ["pack", "flock", "school"]), ("wolves", "pack", ["pride", "flock", "school"]),
               ("fish", "school", ["pride", "herd", "troop"]), ("cows", "herd", ["pride", "pack", "school"]),
               ("sheep", "flock", ["pride", "pack", "school"]), ("bees", "swarm", ["pride", "pack", "herd"]),
               ("ants", "colony", ["pride", "herd", "school"]), ("dolphins", "pod", ["pride", "pack", "flock"]),
               ("geese", "gaggle", ["pack", "school", "pride"]), ("crows", "murder", ["pack", "school", "pride"]),
               ("owls", "parliament", ["pack", "school", "pride"]), ("monkeys", "troop", ["school", "pride", "pod"]),
               ("elephants", "herd", ["pride", "pack", "school"]), ("penguins", "colony", ["pride", "pack", "school"]),
               ("whales", "pod", ["pride", "pack", "flock"]), ("puppies", "litter", ["pride", "flock", "school"])]

FACT6 = [
    ("Which animal is the tallest in the world?", "giraffe", ["elephant", "camel", "horse", "bear"]),
    ("What is the biggest animal on land?", "elephant", ["giraffe", "hippo", "rhino", "bear"]),
    ("What is the fastest land animal?", "cheetah", ["lion", "horse", "elephant", "bear", "zebra"]),
    ("What is the biggest animal in the whole world?", "blue whale", ["elephant", "giraffe", "hippo", "great white shark"]),
    ("A baby kangaroo rides in its mother's ...", "pouch", ["nest", "shell", "burrow", "cave"]),
    ("Animals that eat only plants are called ...", "herbivores", ["carnivores", "omnivores", "amphibians"]),
    ("Animals that eat only meat are called ...", "carnivores", ["herbivores", "omnivores", "amphibians"]),
    ("Animals that eat plants and meat are called ...", "omnivores", ["herbivores", "carnivores", "amphibians"]),
    ("How many legs does an insect have?", "6", ["4", "8", "2", "10"]),
    ("What do bees make?", "honey", ["milk", "wool", "sugar", "butter"]),
    ("Which animal sleeps hanging upside down?", "bat", ["eagle", "bear", "lion", "rabbit"]),
    ("Which bird cannot fly but swims very well?", "penguin", ["eagle", "owl", "parrot", "swan"]),
    ("What is the biggest bird in the world?", "ostrich", ["eagle", "penguin", "flamingo", "swan"]),
    ("Which animal has black and white stripes?", "zebra", ["lion", "giraffe", "elephant", "bear"]),
    ("Which animal carries its shell on its back and moves slowly?", "snail", ["rabbit", "owl", "cat", "bear"]),
    ("Which animal can change its color to hide?", "chameleon", ["lion", "elephant", "bear", "rabbit"]),
    ("Which sea animal has eight arms?", "octopus", ["shark", "dolphin", "whale", "seahorse"]),
    ("What do caterpillars turn into?", "butterflies or moths", ["bees", "beetles", "flies", "frogs"]),
    ("What do tadpoles grow up to be?", "frogs", ["fish", "snakes", "turtles", "birds"]),
    ("Which animal has a very long trunk?", "elephant", ["giraffe", "hippo", "camel", "bear"]),
    ("Which animal has a hump on its back and lives in the desert?", "camel", ["horse", "cow", "elephant", "bear"]),
    ("What animal gives us wool?", "sheep", ["cow", "pig", "chicken", "duck"]),
    ("Which animal says hoo-hoo at night?", "owl", ["duck", "cow", "eagle", "frog"]),
    ("A spider is not an insect. How many legs does it have?", "8", ["6", "4", "10", "2"]),
    ("Which animal builds dams in rivers?", "beaver", ["bear", "rabbit", "deer", "fox"]),
    ("Which animal is black and white and loves to eat bamboo?", "panda", ["zebra", "penguin", "skunk", "koala"]),
    ("Which animal sleeps most of the day in a eucalyptus tree?", "koala", ["lion", "owl", "zebra", "eagle"]),
    ("What do we call animals that are awake at night?", "nocturnal", ["hibernating", "migrating", "herbivores"]),
    ("When animals travel far to find warmer weather, it is called ...", "migration", ["hibernation", "camouflage", "pollination"]),
    ("When an animal sleeps through the winter, it is called ...", "hibernation", ["migration", "camouflage", "pollination"]),
    ("Which animal has a shell and can pull its head inside?", "turtle", ["frog", "snake", "lizard", "crocodile"]),
    ("Which of these animals lays eggs?", "chicken", ["cow", "dog", "horse", "pig"]),
    ("Which of these animals gives us milk?", "cow", ["chicken", "duck", "snake", "frog"]),
    ("What is a baby butterfly called before it grows wings?", "caterpillar", ["tadpole", "chick", "puppy"]),
    ("A skunk protects itself by ...", "spraying a bad smell", ["flying away", "digging for water", "changing color", "roaring"]),
    ("A hedgehog protects itself with ...", "sharp spines", ["a hard shell", "a long tail", "big horns", "bright feathers"]),
    ("Which part of a bird helps it to fly?", "wings", ["horns", "claws", "paws", "fins"]),
    ("Which animal builds its home in a hive?", "bee", ["ant", "beaver", "bear", "bird"]),
    ("What do fish use to breathe underwater?", "gills", ["lungs", "wings", "fur", "horns"]),
    ("What covers a bird's body?", "feathers", ["fur", "scales", "shells", "wool"]),
    ("What covers a fish's body?", "scales", ["feathers", "fur", "wool", "feet"]),
    ("Which animal is a mammal that can really fly?", "bat", ["eagle", "butterfly", "owl", "bee"]),
    ("Which of these animals is a mammal?", "dolphin", ["shark", "turtle", "octopus", "crab"]),
    ("Which of these is NOT a bird?", "bat", ["eagle", "owl", "penguin", "duck"]),
    ("Which of these animals is NOT an insect?", "spider", ["ant", "bee", "butterfly", "beetle"]),
    ("Which animal has a very long neck and spots?", "giraffe", ["zebra", "elephant", "camel", "horse"]),
    ("What is a very big group of bees living together called?", "a colony", ["a pride", "a flock", "a litter"]),
    ("Which animal lives in a nest high in a tree?", "bird", ["fish", "snake", "whale", "bear"]),
    ("Which animal lives in a burrow underground?", "rabbit", ["eagle", "dolphin", "giraffe", "monkey"]),
    ("Where does a bee live?", "in a hive", ["in a nest", "in a burrow", "in a pond"]),
    ("Which animal builds a web?", "spider", ["ant", "bee", "snail", "butterfly"]),
    ("Which one does NOT have bones inside its body?", "octopus", ["dog", "bird", "frog", "snake"]),
    ("A grass-eating animal that hops and has long ears is a ...", "rabbit", ["fox", "wolf", "bear", "lion"]),
    ("Which is the largest kind of bear, living in the icy Arctic?", "polar bear", ["panda", "sun bear", "sloth bear"]),
]

FACT11 = [
    ("Which is the only mammal that can truly fly?", "bat", ["flying squirrel", "sugar glider", "colugo"]),
    ("Which two mammals lay eggs?", "platypus and echidna", ["kangaroo and koala", "bat and sloth", "otter and beaver", "seal and walrus"]),
    ("Kangaroos, koalas and opossums are all ...", "marsupials", ["monotremes", "rodents", "primates"]),
    ("Which animal is the largest rodent?", "capybara", ["beaver", "porcupine", "guinea pig", "muskrat"]),
    ("Which bird dives fastest, over 300 km/h?", "peregrine falcon", ["bald eagle", "ostrich", "owl", "hummingbird"]),
    ("Which bird has the longest wingspan, about 3.5 m?", "wandering albatross", ["bald eagle", "ostrich", "great horned owl"]),
    ("What is the smallest bird in the world?", "bee hummingbird", ["sparrow", "wren", "finch", "kiwi"]),
    ("Which bird makes the longest yearly migration of any animal, pole to pole?", "Arctic tern", ["swan", "stork", "goose", "robin"]),
    ("What is the largest living reptile?", "saltwater crocodile", ["Komodo dragon", "green anaconda", "leatherback turtle"]),
    ("What is the largest living lizard?", "Komodo dragon", ["iguana", "gecko", "chameleon"]),
    ("Which cat is the fastest land animal?", "cheetah", ["lion", "leopard", "jaguar", "tiger"]),
    ("Which of these cats purrs but cannot roar?", "cheetah", ["lion", "tiger", "jaguar", "leopard"]),
    ("Which is the largest living cat?", "tiger", ["lion", "jaguar", "leopard", "cheetah"]),
    ("Which amphibian can regrow lost limbs and keeps its gills as an adult?", "axolotl", ["bullfrog", "tree frog", "toad"]),
    ("What is the largest frog in the world?", "goliath frog", ["bullfrog", "tree frog", "cane toad", "poison dart frog"]),
    ("Bright colors on a poison dart frog warn predators. This is called ...", "aposematism", ["camouflage", "mimicry", "hibernation", "echolocation"]),
    ("How many chambers does a bird's heart have?", "4", ["2", "3", "5", "6"]),
    ("How many hearts does an octopus have?", "3", ["1", "2", "4", "8"]),
    ("A giraffe's neck has how many neck bones (vertebrae)?", "7", ["3", "14", "20", "30"]),
    ("A cow's stomach has how many compartments?", "4", ["1", "2", "3", "8"]),
    ("How many body sections does an insect have?", "3", ["2", "4", "5", "8"]),
    ("How many toes does an ostrich have on each foot?", "2", ["1", "3", "4", "5"]),
    ("Which sense do bats use to find insects in the dark?", "echolocation", ["x-ray vision", "smell only", "heat vision", "magnetic sense"]),
    ("Which mammal is covered in true scales?", "pangolin", ["hedgehog", "porcupine", "anteater"]),
    ("An owl can turn its head about how far?", "270 degrees", ["90 degrees", "180 degrees", "360 degrees", "45 degrees"]),
    ("Which bird can fly backward?", "hummingbird", ["eagle", "owl", "pigeon", "swan"]),
    ("Male emperor penguins keep their egg warm by balancing it on their ...", "feet", ["wings", "beak", "back", "tail"]),
    ("Monarch butterflies migrate in winter to forests in which country?", "Mexico", ["Canada", "Brazil", "Egypt", "India"]),
    ("In a honeybee hive, all worker bees are ...", "female", ["male", "queens", "babies", "drones"]),
    ("How do honeybees tell each other where flowers are?", "waggle dance", ["singing", "ink clouds", "howling", "drumming"]),
    ("Which animal's fingerprints look very much like human ones?", "koala", ["bear", "cat", "lion", "dog"]),
    ("What does a camel's hump mainly store?", "fat", ["water", "air", "sand", "milk"]),
    ("Which animal has a trunk with no bones inside?", "elephant", ["anteater", "rhino", "hippo"]),
    ("Which is the largest living primate?", "gorilla", ["orangutan", "chimpanzee", "baboon"]),
    ("Which animal sleeps up to about 20 hours a day?", "koala", ["giraffe", "elephant", "horse", "cow"]),
    ("Which snake is the longest in the world?", "reticulated python", ["king cobra", "rattlesnake", "boa constrictor", "garter snake"]),
    ("What do you call an animal that hunts other animals for food?", "predator", ["prey", "scavenger", "producer", "herbivore"]),
    ("What do you call an animal that is hunted for food?", "prey", ["predator", "scavenger", "producer", "carnivore"]),
    ("Vultures and hyenas often eat animals that are already dead. They are ...", "scavengers", ["producers", "herbivores", "parasites", "pollinators"]),
    ("A tick that feeds on a dog's blood is a ...", "parasite", ["predator", "pollinator", "scavenger", "producer"]),
    ("Birds that carry pollen between flowers help the plant by ...", "pollinating it", ["eating it", "watering it", "burying it", "cutting it"]),
]

TERMS = [
    ("What is it called when an animal blends in with its surroundings?", "camouflage", ["migration", "hibernation", "echolocation", "metamorphosis"]),
    ("Animals that are active mostly at night are ...", "nocturnal", ["diurnal", "crepuscular", "aquatic", "solitary"]),
    ("Animals that are active during the day are ...", "diurnal", ["nocturnal", "crepuscular", "aquatic", "solitary"]),
    ("Animals that are most active at dawn and dusk are ...", "crepuscular", ["nocturnal", "diurnal", "aquatic", "arboreal"]),
    ("A big change in body shape, like caterpillar to butterfly, is ...", "metamorphosis", ["migration", "adaptation", "hibernation", "mimicry"]),
    ("When two species live together and both benefit, it is called ...", "mutualism", ["parasitism", "predation", "competition", "camouflage"]),
    ("A species at the top of a food chain with no natural predators is an ...", "apex predator", ["herbivore", "decomposer", "producer", "scavenger"]),
    ("A species that has a huge effect on its ecosystem is a ...", "keystone species", ["pest species", "invasive species", "extinct species", "domestic species"]),
    ("Warm-blooded animals make their own body heat. This is called ...", "endothermy", ["ectothermy", "hibernation", "metamorphosis", "migration"]),
    ("Animals that rely on the sun to warm their bodies are ...", "ectotherms", ["endotherms", "mammals", "herbivores", "predators"]),
    ("Animals without a backbone are called ...", "invertebrates", ["vertebrates", "mammals", "reptiles", "amphibians"]),
    ("Animals with a backbone are called ...", "vertebrates", ["invertebrates", "arthropods", "mollusks", "insects"]),
    ("Mammals whose babies develop in a pouch are called ...", "marsupials", ["monotremes", "rodents", "primates", "amphibians"]),
    ("An animal that copies the look of another animal for protection shows ...", "mimicry", ["migration", "hibernation", "metamorphosis", "pollination"]),
    ("A body part that no longer has a use, like a whale's tiny hip bones, is ...", "vestigial", ["venomous", "nocturnal", "invasive", "migratory"]),
    ("A species with no living members left is ...", "extinct", ["endangered", "invasive", "migratory", "nocturnal"]),
    ("A species at high risk of becoming extinct is ...", "endangered", ["extinct", "invasive", "domestic", "nocturnal"]),
    ("In a food chain, the producers are the ...", "plants", ["herbivores", "carnivores", "decomposers", "predators"]),
    ("An animal that eats only plants is a ...", "primary consumer", ["secondary consumer", "producer", "apex predator", "decomposer"]),
    ("Fungi and bacteria that break down dead matter are ...", "decomposers", ["producers", "predators", "herbivores", "scavengers"]),
    ("A summer sleep to survive hot, dry weather is called ...", "estivation", ["hibernation", "migration", "metamorphosis", "mimicry"]),
    ("The light made by living things such as some deep-sea fish is called ...", "bioluminescence", ["fluorescence", "camouflage", "echolocation", "photosynthesis"]),
    ("When a bird, snake or crab sheds its old outer layer, it is called ...", "molting", ["migrating", "hibernating", "mimicking", "estivating"]),
    ("A chemical signal animals release to communicate is a ...", "pheromone", ["vitamin", "venom", "enzyme"]),
    ("A tree-dwelling animal is described as ...", "arboreal", ["aquatic", "nocturnal", "burrowing", "terrestrial"]),
    ("An animal that lives mainly in water is ...", "aquatic", ["arboreal", "terrestrial", "nocturnal", "aerial"]),
    ("The role an organism plays in its ecosystem is its ...", "niche", ["habitat", "colony", "territory", "migration"]),
    ("A plant-eating animal with a four-part stomach that chews cud is a ...", "ruminant", ["predator", "omnivore", "scavenger", "marsupial"]),
    ("Animals that eat mostly insects are called ...", "insectivores", ["herbivores", "frugivores", "omnivores"]),
    ("Animals that eat mostly fruit are called ...", "frugivores", ["insectivores", "carnivores", "piscivores"]),
    ("Animals that eat mostly fish are called ...", "piscivores", ["frugivores", "insectivores", "herbivores"]),
]

BABY11 = [("hare", "leveret"), ("fish", "fry"), ("eel", "elver"), ("pigeon", "squab"), ("goose", "gosling"), ("swan", "cygnet"),
          ("llama", "cria"), ("hedgehog", "hoglet"), ("turkey", "poult"), ("kangaroo", "joey"), ("seal", "pup"),
          ("bat", "pup"), ("shark", "pup"), ("deer", "fawn"), ("owl", "owlet"), ("goat", "kid"), ("frog", "tadpole"),
          ("butterfly", "caterpillar"), ("beaver", "kit"), ("eagle", "eaglet"), ("sheep", "lamb"), ("horse", "foal")]
BABY_ALL = ["leveret", "fry", "elver", "squab", "gosling", "cygnet", "cria", "hoglet", "poult", "joey", "pup", "fawn", "owlet", "kid",
            "tadpole", "caterpillar", "kit", "eaglet", "lamb", "foal", "calf", "cub", "chick", "kitten", "puppy", "piglet"]
# babies that fit more than one animal in the list above (don't use them as the "wrong" side): pup, kit, calf, cub, chick, foal(horse/zebra)

CLASS11 = {
    "mammal": "dog cat cow pig horse sheep goat lion tiger leopard cheetah jaguar wolf fox bear polar_bear panda koala kangaroo elephant giraffe zebra rhino hippo gorilla chimpanzee orangutan monkey bat whale dolphin seal walrus otter beaver squirrel rabbit mouse rat hedgehog camel llama deer moose bison platypus echidna pangolin",
    "bird": "eagle owl parrot penguin ostrich emu flamingo swan duck chicken turkey peacock hummingbird pelican albatross woodpecker toucan crow sparrow kiwi",
    "reptile": "snake turtle tortoise crocodile alligator lizard gecko chameleon iguana Komodo_dragon cobra python",
    "amphibian": "frog toad salamander newt axolotl",
    "fish": "shark goldfish salmon tuna clownfish seahorse eel stingray swordfish sailfish",
    "insect": "bee ant butterfly beetle ladybug dragonfly grasshopper cricket mosquito fly wasp moth cockroach termite",
    "arachnid": "spider scorpion tick mite tarantula",
    "crustacean": "crab lobster shrimp barnacle pill_bug",
    "mollusk": "snail octopus squid clam oyster slug",
    "cnidarian": "jellyfish coral sea_anemone",
    "echinoderm": "starfish sea_urchin sea_cucumber",
    "annelid": "earthworm leech",
}
GROUP_LABEL = {"mammal": "mammal", "bird": "bird", "reptile": "reptile", "amphibian": "amphibian", "fish": "fish", "insect": "insect",
               "arachnid": "arachnid", "crustacean": "crustacean", "mollusk": "mollusk", "cnidarian": "cnidarian",
               "echinoderm": "echinoderm", "annelid": "annelid (segmented worm)"}

SCI = {"lion": "Panthera leo", "tiger": "Panthera tigris", "leopard": "Panthera pardus", "jaguar": "Panthera onca",
       "cheetah": "Acinonyx jubatus", "house cat": "Felis catus", "gray wolf": "Canis lupus", "red fox": "Vulpes vulpes",
       "brown bear": "Ursus arctos", "polar bear": "Ursus maritimus", "giant panda": "Ailuropoda melanoleuca",
       "African elephant": "Loxodonta africana", "Asian elephant": "Elephas maximus", "giraffe": "Giraffa camelopardalis",
       "hippopotamus": "Hippopotamus amphibius", "blue whale": "Balaenoptera musculus", "orca": "Orcinus orca",
       "bottlenose dolphin": "Tursiops truncatus", "humpback whale": "Megaptera novaeangliae", "sperm whale": "Physeter macrocephalus",
       "koala": "Phascolarctos cinereus", "human": "Homo sapiens", "horse": "Equus caballus", "cow": "Bos taurus",
       "sheep": "Ovis aries", "goat": "Capra hircus", "European rabbit": "Oryctolagus cuniculus", "house mouse": "Mus musculus",
       "bald eagle": "Haliaeetus leucocephalus", "emperor penguin": "Aptenodytes forsteri", "ostrich": "Struthio camelus",
       "mallard": "Anas platyrhynchos", "great horned owl": "Bubo virginianus", "peregrine falcon": "Falco peregrinus",
       "honey bee": "Apis mellifera", "monarch butterfly": "Danaus plexippus", "great white shark": "Carcharodon carcharias",
       "green sea turtle": "Chelonia mydas", "Nile crocodile": "Crocodylus niloticus", "king cobra": "Ophiophagus hannah",
       "Komodo dragon": "Varanus komodoensis", "common octopus": "Octopus vulgaris", "giant squid": "Architeuthis dux",
       "platypus": "Ornithorhynchus anatinus", "chimpanzee": "Pan troglodytes"}


SAFE_NOT_AUS = {"lion", "giraffe", "zebra", "tiger", "gorilla", "monkey", "sloth", "orangutan", "bear", "panda", "hippo", "polar bear", "wolf", "beaver", "otter"}
LAB = {"farm": "on a farm", "ocean": "in the ocean", "jungle": "in the jungle", "desert": "in the desert", "polar": "in the snowy polar lands",
       "savanna": "on the African grassland", "forest": "in the forest", "water": "in a pond or river", "australia": "in Australia"}
HAB = {"cow": ("farm", {"farm"}), "pig": ("farm", {"farm"}), "sheep": ("farm", {"farm"}), "chicken": ("farm", {"farm"}), "goat": ("farm", {"farm"}),
       "horse": ("farm", {"farm", "savanna", "forest"}), "duck": ("water", {"water", "farm"}), "lion": ("savanna", {"savanna", "desert", "forest"}),
       "giraffe": ("savanna", {"savanna", "desert"}), "zebra": ("savanna", {"savanna", "desert"}), "tiger": ("jungle", {"jungle", "forest", "polar"}),
       "gorilla": ("jungle", {"jungle", "forest"}), "monkey": ("jungle", {"jungle", "forest", "savanna"}), "parrot": ("jungle", {"jungle", "forest"}),
       "sloth": ("jungle", {"jungle", "forest"}), "orangutan": ("jungle", {"jungle", "forest"}),
       "bear": ("forest", {"forest", "jungle", "polar"}), "deer": ("forest", {"forest", "jungle", "polar", "savanna", "farm"}),
       "wolf": ("forest", {"forest", "polar", "savanna"}), "panda": ("forest", {"forest", "jungle"}), "camel": ("desert", {"desert"}),
       "kangaroo": ("australia", {"australia", "desert", "savanna"}), "koala": ("australia", {"australia", "forest"}),
       "polar bear": ("polar", {"polar"}), "penguin": ("polar", {"polar", "ocean"}), "seal": ("ocean", {"ocean", "polar", "water"}),
       "dolphin": ("ocean", {"ocean", "water"}), "whale": ("ocean", {"ocean", "polar"}), "shark": ("ocean", {"ocean"}),
       "octopus": ("ocean", {"ocean"}), "crab": ("ocean", {"ocean", "water"}), "frog": ("water", {"water", "jungle", "forest"}),
       "hippo": ("water", {"water", "savanna"}), "crocodile": ("water", {"water", "savanna", "jungle"}), "beaver": ("water", {"water", "forest"}),
       "swan": ("water", {"water"}), "flamingo": ("water", {"water"}), "otter": ("water", {"water", "ocean"})}
HAB = {n: (a, t | ({"australia"} if n not in SAFE_NOT_AUS else set())) for n, (a, t) in HAB.items()}
FOOD = [("panda", "bamboo", "P"), ("koala", "eucalyptus leaves", "P"), ("cow", "grass", "P"), ("horse", "grass", "P"), ("sheep", "grass", "P"),
        ("giraffe", "leaves from tall trees", "P"), ("butterfly", "nectar from flowers", "P"), ("lion", "meat", "A"),
        ("frog", "insects", "A"), ("penguin", "fish", "A"), ("anteater", "ants and termites", "A"), ("polar bear", "seals", "A"),
        ("blue whale", "tiny krill", "A"), ("owl", "mice and other small animals", "A"), ("spider", "insects", "A")]
PLANT = ["bamboo", "eucalyptus leaves", "grass", "leaves from tall trees", "nectar from flowers"]
BABY_POOL = ["puppy", "kitten", "calf", "foal", "lamb", "piglet", "duckling", "joey", "fawn", "cygnet", "tadpole", "gosling", "cria", "eaglet", "kid", "cub", "chick", "hatchling"]


def build(band):
    r = rng_for("animals", band)
    out = []
    add = out.append

    # =============================================================== 2-5
    if band == "2-5":
        TOD = [n for n in EM if n not in ("mosquito", "beetle", "skunk", "raccoon", "orangutan", "scorpion", "hamster", "leopard", "bison", "cricket")]
        for n in TOD:
            e = E(n)
            es = [E(x) for x in wr(n, TOD)]
            add(mc(r, "What animal is this?", n, wr(n, TOD), v=emoji(e)))
            add(mc(r, f"Find the {n}!", e, es, ct="emoji"))
            add(mc(r, f"Which one is the {n}?", e, es, ct="emoji"))
            add(mc(r, f"Where is the {n}?", e, es, ct="emoji"))
            if A[n]["legs"] in (2, 4, 6, 8):
                add(mc(r, "How many legs does it have?", str(A[n]["legs"]), list("2468"), v=emoji(e)))
        FAV = ["dog", "cat", "cow", "pig", "duck", "frog", "lion", "bear", "elephant", "monkey", "giraffe", "fish", "bee", "butterfly",
               "rabbit", "horse", "sheep", "penguin", "owl", "turtle", "ladybug", "snail", "crab", "octopus", "chicken", "panda"]
        for n in FAV:
            for k in range(1, 6):
                add(num_choices(r, "How many?", k, v=emoji(" ".join([E(n)] * k)), spread=2, lo=1))
        SND = [n for n in TOD if A[n]["sound"]]
        sound_pool = [A[n]["sound"] for n in SND]
        for n in SND:
            s = A[n]["sound"]
            loud = {"roar", "growl"}
            bad = [x for x in sound_pool if x != s and not ({x, s} <= loud)]
            add(mc(r, "What sound does it make?", s, bad, v=emoji(E(n))))
            others = [E(x) for x in wr(n, SND) if A[x]["sound"] != s and not (s in loud and A[x]["sound"] in loud) and not (s == "hiss" and x == "cat")]
            add(mc(r, f"Who says {s}?", E(n), others, ct="emoji"))
        HOME = {"🌊": ["fish", "shark", "dolphin", "whale", "octopus", "crab"], "🌲": ["bear", "deer", "wolf", "squirrel", "owl"],
                "🚜": ["cow", "pig", "sheep", "chicken", "horse"], "🌴": ["monkey", "tiger", "parrot", "sloth", "gorilla"], "🏜️": ["camel"]}
        for place, names in HOME.items():
            for n in names:
                others = [p for p in HOME if p != place and {p, place} != {"🌲", "🌴"}]
                add(mc(r, "Where does it live?", place, others, v=emoji(E(n)), ct="emoji"))
        BIG = ["elephant", "giraffe", "whale", "hippo", "rhino", "camel", "horse", "cow"]
        SMALL = ["ant", "bee", "ladybug", "butterfly", "snail", "mouse", "spider", "frog", "hedgehog", "bat", "chicken", "duck"]
        for b in BIG:
            for s in SMALL:
                vis = emoji(" ".join(r.sample([E(b), E(s)], 2)))
                add(mc(r, "Which one is bigger?", E(b), [E(s)] + r.sample([E(x) for x in SMALL if x != s], 2), v=vis, ct="emoji"))
                add(mc(r, "Which one is smaller?", E(s), [E(b)] + r.sample([E(x) for x in BIG if x != b], 2), v=vis, ct="emoji"))
        NON = ["dog", "cat", "cow", "pig", "horse", "sheep", "elephant", "lion", "bear", "frog", "turtle", "giraffe", "zebra", "rabbit", "monkey", "hippo"]
        TR = [
            (["Which one can fly?", "Which one has wings?", "Who can fly high in the sky?"], ["eagle", "owl", "parrot", "butterfly", "bee"], NON),
            (["Which one has a long trunk?", "Which one has a big trunk?"], ["elephant"], [x for x in NON if x != "elephant"]),
            (["Which one has a long neck?", "Which has the longest neck?"], ["giraffe"], [x for x in NON if x != "giraffe"]),
            (["Which one has a shell?", "Who carries a shell?"], ["turtle", "snail", "crab"], [x for x in NON if x != "turtle"]),
            (["Which one lives in the sea?", "Which one lives in the ocean?"], ["fish", "shark", "dolphin", "whale", "octopus", "crab"],
             ["dog", "cat", "cow", "pig", "horse", "sheep", "elephant", "lion", "bear", "giraffe", "zebra", "rabbit", "monkey"]),
            (["Which one hops?", "Who can hop and jump?"], ["frog", "rabbit", "kangaroo"], ["cow", "pig", "horse", "sheep", "elephant", "lion", "bear", "giraffe", "hippo", "turtle"]),
            (["Which one has no legs?", "Which one slithers?"], ["snake"], NON),
            (["Which one has stripes?", "Who wears stripes?"], ["zebra", "tiger"], ["cow", "pig", "horse", "sheep", "elephant", "lion", "bear", "giraffe", "rabbit", "hippo", "monkey", "turtle"]),
            (["Which one eats grass?", "Who munches grass?"], ["cow", "sheep", "horse", "zebra"], ["lion", "shark", "owl", "eagle", "snake", "crocodile", "tiger", "wolf", "fish"]),
            (["Which one loves bananas?", "Who eats bananas?"], ["monkey"], ["lion", "shark", "owl", "eagle", "snake", "crocodile", "tiger", "wolf", "fish", "turtle"]),
            (["Which one eats bamboo?", "Who loves bamboo?"], ["panda"], ["lion", "shark", "owl", "eagle", "snake", "tiger", "wolf", "fish", "dog", "cat"]),
            (["Which one has a pouch?", "Who carries a baby in a pouch?"], ["kangaroo"], [x for x in NON]),
            (["Which one makes honey?", "Who makes sweet honey?"], ["bee"], ["ant", "butterfly", "ladybug", "spider", "dog", "cat", "cow"]),
            (["Which one spins a web?", "Who makes a web?"], ["spider"], ["ant", "bee", "butterfly", "ladybug", "snail", "dog", "cat"]),
            (["Which one gives us milk?", "Who gives us milk?"], ["cow"], ["chicken", "duck", "frog", "fish", "snake", "owl", "bee"]),
            (["Which one has soft wool?", "Who has wool?"], ["sheep"], ["cow", "pig", "dog", "cat", "horse", "chicken", "duck", "elephant"]),
            (["Which one swings in trees?", "Who swings from tree to tree?"], ["monkey"], ["cow", "pig", "elephant", "snail", "fish", "turtle", "horse", "sheep"]),
            (["Which one is very slow?", "Who is super slow?"], ["snail", "turtle"], ["horse", "dog", "cat", "rabbit", "eagle", "lion", "bee"]),
            (["Which one is very fast?", "Who runs super fast?"], ["horse", "lion"], ["snail", "turtle", "sloth", "snake"]),
        ]
        for qs, ans, wrong in TR:
            for qq in qs:
                a = r.choice(ans)
                add(mc(r, qq, E(a), [E(x) for x in wrong if x != a], ct="emoji"))
        add(mc(r, "Which one is NOT an animal?", "🌳", ["🐶", "🐱", "🐻", "🦁"], ct="emoji"))
        add(mc(r, "Which one is not an animal?", "🍎", ["🐘", "🐒", "🐢", "🐸"], ct="emoji"))
        add(mc(r, "Which one is a baby chick?", "🐥", ["🐔", "🦆", "🦉", "🐓"], ct="emoji"))

    # =============================================================== 6-10
    elif band == "6-10":
        K6 = ["mammal", "bird", "reptile", "amphibian", "fish", "insect"]
        LEGLAB = {0: "none", 2: "2", 4: "4", 6: "6", 8: "8"}
        for n in A:
            d = A[n]
            vis = emoji(d["e"]) if d["e"] else None
            if d["e"]:
                add(mc(r, "What animal is this?", n, wr(n, EM), v=vis))
            if d["cls"] in K6:
                add(mc(r, f"What kind of animal is {art(n)}?", d["cls"], K6, v=vis))
            if d["legs"] is not None:
                add(mc(r, f"How many legs does {art(n)} have?", LEGLAB[d["legs"]], [LEGLAB[x] for x in (0, 2, 4, 6, 8)]))
            if d["baby"] and n != "bee":
                wrong = [b for b in BABY_POOL if b != d["baby"]]
                add(mc(r, f"What is a baby {n} called?", d["baby"], wrong, v=vis))
            if d["diet"] and n != "frog":
                add(mc(r, f"Is {art(n)} a herbivore, carnivore or omnivore?", d["diet"], ["herbivore", "carnivore", "omnivore", "insectivore"], v=vis))
        from collections import Counter
        cnt = Counter(A[n]["baby"] for n in EM if A[n]["baby"])
        for n in EM:
            b = A[n]["baby"]
            if b and cnt[b] == 1:
                bad = [x for x in EM if A[x]["baby"] and A[x]["baby"] != b and ok(n, x)]
                add(mc(r, f"A {b} is a baby ...", n, bad))
        for n, f, t in FOOD:
            e = E(n) if n in A else None
            if t == "P":
                bad = [x for x in PLANT + ["fish", "insects", "meat"] if x != f and not ({x, f} <= {"eucalyptus leaves", "leaves from tall trees"})]
                if n == "panda": bad = [x for x in bad if x != "leaves from tall trees"]
            else:
                bad = list(PLANT)
            add(mc(r, f"What does {art(n)} eat?", f, bad, v=emoji(e) if e else None))
        SNDS = [n for n in EM if A[n]["sound"]]
        allsnd = [A[n]["sound"] for n in SNDS]
        for n in SNDS:
            s = A[n]["sound"]
            add(mc(r, f"What sound does {art(n)} make?", s, [x for x in allsnd if x != s and not ({x, s} <= {"roar", "growl"})], v=emoji(E(n))))
        for n, (ans, tags) in HAB.items():
            bad = [LAB[c] for c in LAB if c not in tags]
            add(mc(r, f"Where does {art(n)} live?", LAB[ans], bad, v=emoji(E(n)) if E(n) else None))
        for c in ("farm", "ocean", "jungle", "desert", "savanna", "forest", "australia"):
            names = [n for n, (a, t) in HAB.items() if a == c and E(n)]
            for k, n in enumerate(r.sample(names, min(2, len(names)))):
                bad = [x for x, (a, t) in HAB.items() if c not in t and E(x) and ok(n, x)]
                qq = f"Which animal lives {LAB[c]}?" if k == 0 else f"Which of these lives {LAB[c]}?"
                add(mc(r, qq, E(n), [E(x) for x in bad], ct="emoji"))
        CLN = {"mammal": "a mammal", "bird": "a bird", "reptile": "a reptile", "amphibian": "an amphibian", "fish": "a fish", "insect": "an insect"}
        for c in K6:
            for qq in (f"Which of these is {CLN[c]}?", f"Which one is {CLN[c]}?", f"Find {CLN[c]}!"):
                a = r.choice([n for n in EM if A[n]["cls"] == c])
                add(mc(r, qq, E(a), [E(x) for x in EM if A[x]["cls"] != c], ct="emoji"))
        for table, phr, d, want, ratio in ((MASS_EM, "biggest", "max", 40, 2.0), (MASS_EM, "smallest", "min", 40, 2.0),
                                           (SPEED_EM, "fastest", "max", 30, 1.5), (SPEED_EM, "slowest", "min", 30, 1.5)):
            for s in lineups(r, table, want, ratio, d):
                qq = f"Which animal moves the {phr}?" if phr in ("fastest", "slowest") else f"Which animal is the {phr}?"
                add(mc(r, qq, s[0], s[1:], v=emoji(" ".join(E(x) for x in r.sample(s, 4)))))
        for g, a, w in GROUP_NAMES:
            add(mc(r, f"A group of {g} is called a ...", a, w))
        for q, a, w in FACT6:
            add(mc(r, q, a, w))

    # =============================================================== 11+
    else:
        VERT = ["mammal", "bird", "reptile", "amphibian", "fish"]
        INVERT = ["insect", "arachnid", "crustacean", "mollusk", "cnidarian", "echinoderm", "annelid"]
        for g, names in CLASS11.items():
            for n in names.split():
                nm = n.replace("_", " ")
                side = VERT if g in VERT else INVERT
                add(mc(r, f"Which group does the {nm} belong to?", GROUP_LABEL[g], [GROUP_LABEL[x] for x in side if x != g]))
        sci_pool = list(SCI.values())
        for common, s in SCI.items():
            add(mc(r, f"What is the scientific name of the {common}?", s, sci_pool))
            add(mc(r, f"Which animal has the scientific name {s}?", common, list(SCI)))
        for table, fmt, qmax, qmin, ratio in ((MASS, fmt_kg, "weighs the most", "weighs the least", 2.0),
                                              (SPEED, fmt_kmh, "is the fastest over a short distance", "is the slowest", 1.5),
                                              (LIFE, fmt_yr, "has the longest lifespan", "has the shortest lifespan", 1.5)):
            for dirn, phr, want in (("max", qmax, 45), ("min", qmin, 35)):
                for s in lineups(r, table, want, ratio, dirn):
                    names = r.sample(s, 4)
                    add(mc(r, f"Which of these animals {phr}: " + ", ".join(names[:-1]) + " or " + names[-1] + "?", s[0], s[1:]))
        for table, fmt, what in ((MASS, fmt_kg, "weigh"), (SPEED, fmt_kmh, "speed"), (LIFE, fmt_yr, "life")):
            for n, right in table.items():
                near = [fmt(v) for v in sorted({v for k, v in table.items() if k != n}) if v / right >= 1.8 or right / v >= 1.8]
                if len(near) < 3: continue
                qq = {"weigh": f"About how much does an adult {n} weigh?", "speed": f"About how fast can {art(n)} move at top speed?",
                      "life": f"About how long can {art(n)} live?"}[what]
                add(mc(r, qq, fmt(right), near))
        for q, a, w in FACT11 + TERMS:
            add(mc(r, q, a, w))
        pool = [x for x in BABY_ALL if x not in ("pup", "calf", "cub", "kit", "chick", "kid", "foal")]
        for n, b in BABY11:
            if n == "butterfly":
                add(mc(r, "What is the larva of a butterfly called?", b, pool))
            else:
                add(mc(r, f"What is a baby {n} called?", b, pool))
        for g, a, w in GROUP_NAMES:
            add(mc(r, f"What is the collective noun for a group of {g}?", a, w))
    return out
