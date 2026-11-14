from ..common import *
import itertools

META = {"id": "disney", "name": "Disney Princess", "icon": "👑"}


def P(s): return s.split("|")


NAMES = ["Snow White", "Cinderella", "Aurora", "Ariel", "Belle", "Jasmine", "Pocahontas", "Mulan", "Tiana", "Rapunzel", "Merida", "Moana", "Raya", "Anna", "Elsa"]
SLUG = {n: n.lower().replace(" ", "-") for n in NAMES}
MOVIE = {"Snow White": "Snow White and the Seven Dwarfs", "Cinderella": "Cinderella", "Aurora": "Sleeping Beauty", "Ariel": "The Little Mermaid",
         "Belle": "Beauty and the Beast", "Jasmine": "Aladdin", "Pocahontas": "Pocahontas", "Mulan": "Mulan", "Tiana": "The Princess and the Frog",
         "Rapunzel": "Tangled", "Merida": "Brave", "Moana": "Moana", "Raya": "Raya and the Last Dragon", "Anna": "Frozen", "Elsa": "Frozen"}
YEAR = {"Snow White and the Seven Dwarfs": 1937, "Cinderella": 1950, "Sleeping Beauty": 1959, "The Little Mermaid": 1989, "Beauty and the Beast": 1991,
        "Aladdin": 1992, "Pocahontas": 1995, "Mulan": 1998, "The Princess and the Frog": 2009, "Tangled": 2010, "Brave": 2012, "Frozen": 2013,
        "Moana": 2016, "Raya and the Last Dragon": 2021}
MOVIES = list(YEAR)
PRINCESS_OF = {}
for _p, _m in MOVIE.items():
    PRINCESS_OF.setdefault(_m, []).append(_p)


def pimg(p): return img(f"disney/{SLUG[p]}.png")


def names_wo(*ex): return [n for n in NAMES if n not in ex]


def movies_wo(*ex): return [m for m in MOVIES if m not in ex]


# ---- emoji clues: emoji -> set of princesses it truly fits (first = main)
CL = [("👠", "Cinderella"), ("🎃", "Cinderella"), ("🐭", "Cinderella"), ("🍎", "Snow White", "Jasmine"), ("🧚", "Aurora", "Cinderella"),
      ("😴", "Aurora", "Snow White"), ("🧜‍♀️", "Ariel"), ("🐚", "Ariel", "Moana"), ("🦀", "Ariel", "Moana"), ("🌹", "Belle", "Aurora"), ("📚", "Belle"),
      ("🫖", "Belle"), ("🕯️", "Belle"), ("🪔", "Jasmine"), ("🐯", "Jasmine"), ("🧞", "Jasmine"), ("🐒", "Jasmine"), ("🦝", "Pocahontas"),
      ("🍂", "Pocahontas"), ("🦗", "Mulan"), ("🐲", "Raya", "Mulan"), ("🗡️", "Raya", "Mulan"), ("💎", "Raya"), ("🐸", "Tiana"), ("🐊", "Tiana"),
      ("🍳", "Tiana", "Rapunzel"), ("🎺", "Tiana"), ("🦎", "Rapunzel"), ("🏮", "Rapunzel"), ("🌼", "Rapunzel"), ("🏹", "Merida"), ("🐻", "Merida"),
      ("🐓", "Moana"), ("🐖", "Moana"), ("🏝️", "Moana"), ("🛶", "Moana", "Pocahontas"), ("🌊", "Moana", "Ariel"), ("❄️", "Elsa", "Anna"),
      ("⛄", "Elsa", "Anna"), ("🧊", "Elsa", "Anna"), ("🦌", "Anna", "Elsa"), ("🥕", "Anna", "Elsa")]
FIT = {c[0]: set(c[1:]) for c in CL}
UNIQ = [(c[0], c[1]) for c in CL if len(c) == 2]

# ---- characters: (name, movie, princess or "", friendly?)
CH = [
    ("Doc", "Snow White and the Seven Dwarfs", "Snow White", 1), ("Grumpy", "Snow White and the Seven Dwarfs", "Snow White", 1),
    ("Happy", "Snow White and the Seven Dwarfs", "Snow White", 1), ("Sleepy", "Snow White and the Seven Dwarfs", "Snow White", 1),
    ("Bashful", "Snow White and the Seven Dwarfs", "Snow White", 1), ("Sneezy", "Snow White and the Seven Dwarfs", "Snow White", 1),
    ("Dopey", "Snow White and the Seven Dwarfs", "Snow White", 1), ("The Evil Queen", "Snow White and the Seven Dwarfs", "Snow White", 0),
    ("Gus", "Cinderella", "Cinderella", 1), ("Jaq", "Cinderella", "Cinderella", 1), ("Bruno", "Cinderella", "Cinderella", 1),
    ("Anastasia", "Cinderella", "Cinderella", 0), ("Drizella", "Cinderella", "Cinderella", 0), ("Lady Tremaine", "Cinderella", "Cinderella", 0),
    ("Lucifer", "Cinderella", "Cinderella", 0), ("The Fairy Godmother", "Cinderella", "Cinderella", 1),
    ("Flora", "Sleeping Beauty", "Aurora", 1), ("Fauna", "Sleeping Beauty", "Aurora", 1), ("Merryweather", "Sleeping Beauty", "Aurora", 1),
    ("Maleficent", "Sleeping Beauty", "Aurora", 0), ("Prince Phillip", "Sleeping Beauty", "Aurora", 1), ("Diablo", "Sleeping Beauty", "Aurora", 0),
    ("Flounder", "The Little Mermaid", "Ariel", 1), ("Sebastian", "The Little Mermaid", "Ariel", 1), ("Scuttle", "The Little Mermaid", "Ariel", 1),
    ("Ursula", "The Little Mermaid", "Ariel", 0), ("King Triton", "The Little Mermaid", "Ariel", 1), ("Prince Eric", "The Little Mermaid", "Ariel", 1),
    ("Max", "The Little Mermaid", "Ariel", 1),
    ("Lumière", "Beauty and the Beast", "Belle", 1), ("Cogsworth", "Beauty and the Beast", "Belle", 1), ("Mrs. Potts", "Beauty and the Beast", "Belle", 1),
    ("Chip", "Beauty and the Beast", "Belle", 1), ("Gaston", "Beauty and the Beast", "Belle", 0), ("LeFou", "Beauty and the Beast", "Belle", 0),
    ("Maurice", "Beauty and the Beast", "Belle", 1), ("Philippe", "Beauty and the Beast", "Belle", 1),
    ("Aladdin", "Aladdin", "Jasmine", 1), ("The Genie", "Aladdin", "Jasmine", 0), ("Abu", "Aladdin", "Jasmine", 0), ("Rajah", "Aladdin", "Jasmine", 1),
    ("Iago", "Aladdin", "Jasmine", 0), ("Jafar", "Aladdin", "Jasmine", 0), ("The Sultan", "Aladdin", "Jasmine", 1),
    ("Meeko", "Pocahontas", "Pocahontas", 1), ("Flit", "Pocahontas", "Pocahontas", 1), ("Percy", "Pocahontas", "Pocahontas", 0),
    ("John Smith", "Pocahontas", "Pocahontas", 1), ("Governor Ratcliffe", "Pocahontas", "Pocahontas", 0), ("Grandmother Willow", "Pocahontas", "Pocahontas", 1),
    ("Nakoma", "Pocahontas", "Pocahontas", 1), ("Kocoum", "Pocahontas", "Pocahontas", 0), ("Chief Powhatan", "Pocahontas", "Pocahontas", 1),
    ("Mushu", "Mulan", "Mulan", 1), ("Cri-Kee", "Mulan", "Mulan", 1), ("Khan", "Mulan", "Mulan", 1), ("Li Shang", "Mulan", "Mulan", 1),
    ("Shan Yu", "Mulan", "Mulan", 0), ("Fa Zhou", "Mulan", "Mulan", 1), ("Yao", "Mulan", "Mulan", 1), ("Ling", "Mulan", "Mulan", 1),
    ("Chien-Po", "Mulan", "Mulan", 1), ("Chi-Fu", "Mulan", "Mulan", 0),
    ("Prince Naveen", "The Princess and the Frog", "Tiana", 1), ("Louis", "The Princess and the Frog", "Tiana", 1), ("Ray", "The Princess and the Frog", "Tiana", 1),
    ("Dr. Facilier", "The Princess and the Frog", "Tiana", 0), ("Charlotte", "The Princess and the Frog", "Tiana", 1), ("Mama Odie", "The Princess and the Frog", "Tiana", 1),
    ("Flynn Rider", "Tangled", "Rapunzel", 1), ("Pascal", "Tangled", "Rapunzel", 1), ("Maximus", "Tangled", "Rapunzel", 1),
    ("Mother Gothel", "Tangled", "Rapunzel", 0),
    ("King Fergus", "Brave", "Merida", 1), ("Queen Elinor", "Brave", "Merida", 1), ("Angus", "Brave", "Merida", 1), ("Mor'du", "Brave", "Merida", 0),
    ("Maui", "Moana", "Moana", 1), ("Heihei", "Moana", "Moana", 1), ("Pua", "Moana", "Moana", 1), ("Tamatoa", "Moana", "Moana", 0),
    ("Te Fiti", "Moana", "Moana", 0), ("Gramma Tala", "Moana", "Moana", 1), ("Chief Tui", "Moana", "Moana", 1), ("The Kakamora", "Moana", "Moana", 0),
    ("Sisu", "Raya and the Last Dragon", "Raya", 1), ("Tuk Tuk", "Raya and the Last Dragon", "Raya", 1), ("Namaari", "Raya and the Last Dragon", "Raya", 0),
    ("Chief Benja", "Raya and the Last Dragon", "Raya", 1), ("Boun", "Raya and the Last Dragon", "Raya", 1), ("Tong", "Raya and the Last Dragon", "Raya", 1),
    ("Olaf", "Frozen", "", 1), ("Sven", "Frozen", "", 1), ("Kristoff", "Frozen", "", 1), ("Hans", "Frozen", "", 0), ("Marshmallow", "Frozen", "", 0),
    ("Oaken", "Frozen", "", 1), ("Grand Pabbie", "Frozen", "", 1), ("The Duke of Weselton", "Frozen", "", 0),
]
CH = [(c.replace("Lumière", "Lumière").replace("Mama Odie", "Mama Odie"), m, p, f) for c, m, p, f in CH]

# kinds of characters  (name, kind, forbidden kinds in the choice list)
ANIM = [("Flounder", "Fish", ()), ("Sebastian", "Crab", ()), ("Scuttle", "Seagull", ()), ("Max", "Sheepdog", ("Dog", "Pug")), ("Pascal", "Chameleon", ()),
        ("Maximus", "Horse", ()), ("Abu", "Monkey", ()), ("Rajah", "Tiger", ()), ("Iago", "Parrot", ()), ("Meeko", "Raccoon", ()),
        ("Flit", "Hummingbird", ()), ("Percy", "Pug", ("Dog", "Sheepdog")), ("Mushu", "Dragon", ()), ("Cri-Kee", "Cricket", ()), ("Khan", "Horse", ()),
        ("Louis", "Alligator", ()), ("Ray", "Firefly", ()), ("Heihei", "Rooster", ()), ("Pua", "Pig", ()), ("Tamatoa", "Crab", ()),
        ("Sven", "Reindeer", ()), ("Olaf", "Snowman", ()), ("Gus", "Mouse", ()), ("Jaq", "Mouse", ()), ("Lucifer", "Cat", ()),
        ("Bruno", "Dog", ("Pug", "Sheepdog")), ("Diablo", "Raven", ()), ("Angus", "Horse", ()), ("Philippe", "Horse", ()), ("Sisu", "Dragon", ())]
KINDS = ["Fish", "Crab", "Seagull", "Sheepdog", "Chameleon", "Horse", "Monkey", "Tiger", "Parrot", "Raccoon", "Hummingbird", "Pug", "Dragon", "Cricket",
         "Alligator", "Firefly", "Rooster", "Pig", "Reindeer", "Snowman", "Mouse", "Cat", "Dog", "Raven", "Bear", "Owl", "Elephant"]
OBJ = [("Lumière", "A candelabra"), ("Cogsworth", "A mantel clock"), ("Mrs. Potts", "A teapot"), ("Chip", "A teacup")]
OBJK = ["A candelabra", "A mantel clock", "A teapot", "A teacup", "A feather duster", "A wardrobe", "A broom", "A lamp"]

VIL = [("The Evil Queen", "Snow White and the Seven Dwarfs", "Snow White"), ("Lady Tremaine", "Cinderella", "Cinderella"), ("Maleficent", "Sleeping Beauty", "Aurora"),
       ("Ursula", "The Little Mermaid", "Ariel"), ("Gaston", "Beauty and the Beast", "Belle"), ("Jafar", "Aladdin", "Jasmine"),
       ("Governor Ratcliffe", "Pocahontas", "Pocahontas"), ("Shan Yu", "Mulan", "Mulan"), ("Dr. Facilier", "The Princess and the Frog", "Tiana"),
       ("Mother Gothel", "Tangled", "Rapunzel"), ("Mor'du", "Brave", "Merida"), ("Hans", "Frozen", "Anna"), ("Namaari", "Raya and the Last Dragon", "Raya")]
VDESC = [("Which villain is a sea witch?", "Ursula"), ("Which villain is an evil fairy who curses a princess at her christening?", "Maleficent"),
         ("Which villain raised Rapunzel to keep her hair's magic?", "Mother Gothel"), ("Which villain is a sorcerer who wants the Genie's lamp?", "Jafar"),
         ("Which villain is a vain hunter who wants to marry Belle?", "Gaston"), ("Which villain is the greedy governor of Jamestown?", "Governor Ratcliffe"),
         ("Which villain leads the Huns?", "Shan Yu"), ("Which villain is called the Shadow Man?", "Dr. Facilier"),
         ("Which villain is a giant bear who attacks Merida's family?", "Mor'du"), ("Which villain is the prince who betrays Anna?", "Hans"),
         ("Which villain asks a magic mirror who is the fairest?", "The Evil Queen"), ("Which villain locks Cinderella in her room?", "Lady Tremaine")]

SONGS = [("Let It Go", "Frozen", "Elsa"), ("Part of Your World", "The Little Mermaid", "Ariel"), ("Under the Sea", "The Little Mermaid", ""),
         ("Kiss the Girl", "The Little Mermaid", ""), ("Poor Unfortunate Souls", "The Little Mermaid", ""), ("Colors of the Wind", "Pocahontas", "Pocahontas"),
         ("Just Around the Riverbend", "Pocahontas", "Pocahontas"), ("Reflection", "Mulan", "Mulan"), ("I'll Make a Man Out of You", "Mulan", ""),
         ("A Girl Worth Fighting For", "Mulan", ""), ("How Far I'll Go", "Moana", "Moana"), ("You're Welcome", "Moana", ""), ("Shiny", "Moana", ""),
         ("We Know the Way", "Moana", ""), ("Where You Are", "Moana", ""), ("A Whole New World", "Aladdin", ""), ("Friend Like Me", "Aladdin", ""),
         ("Prince Ali", "Aladdin", ""), ("Arabian Nights", "Aladdin", ""), ("Almost There", "The Princess and the Frog", "Tiana"),
         ("Friends on the Other Side", "The Princess and the Frog", ""), ("Down in New Orleans", "The Princess and the Frog", ""),
         ("When Will My Life Begin", "Tangled", "Rapunzel"), ("I See the Light", "Tangled", ""), ("Mother Knows Best", "Tangled", ""),
         ("Once Upon a Dream", "Sleeping Beauty", "Aurora"), ("Someday My Prince Will Come", "Snow White and the Seven Dwarfs", "Snow White"),
         ("Heigh-Ho", "Snow White and the Seven Dwarfs", ""), ("Whistle While You Work", "Snow White and the Seven Dwarfs", ""),
         ("A Dream Is a Wish Your Heart Makes", "Cinderella", "Cinderella"), ("Bibbidi-Bobbidi-Boo", "Cinderella", ""),
         ("So This Is Love", "Cinderella", ""), ("Be Our Guest", "Beauty and the Beast", ""), ("Tale as Old as Time", "Beauty and the Beast", ""),
         ("Gaston", "Beauty and the Beast", ""), ("Belle", "Beauty and the Beast", "Belle"), ("Touch the Sky", "Brave", ""),
         ("Do You Want to Build a Snowman?", "Frozen", ""), ("For the First Time in Forever", "Frozen", ""), ("Love Is an Open Door", "Frozen", ""),
         ("Into the Unknown", "Frozen II", ""), ("Show Yourself", "Frozen II", "")]

PLACE = {"Ariel": "Under the sea", "Belle": "France", "Jasmine": "Agrabah", "Pocahontas": "Virginia", "Mulan": "China", "Tiana": "New Orleans",
         "Rapunzel": "Corona", "Merida": "Scotland", "Moana": "Motunui", "Raya": "Kumandra", "Anna": "Arendelle", "Elsa": "Arendelle"}
PLACES = ["Under the sea", "France", "Agrabah", "Virginia", "China", "New Orleans", "Corona", "Scotland", "Motunui", "Kumandra", "Arendelle"]
LOVE = {"Aurora": "Prince Phillip", "Ariel": "Prince Eric", "Belle": "The Beast", "Jasmine": "Aladdin", "Pocahontas": "John Smith", "Mulan": "Li Shang",
        "Tiana": "Prince Naveen", "Rapunzel": "Flynn Rider (Eugene)", "Anna": "Kristoff"}
FRIEND = {"Snow White": ["Doc", "Grumpy", "Happy", "Sleepy", "Bashful", "Sneezy", "Dopey"], "Cinderella": ["Gus", "Jaq", "Bruno", "The Fairy Godmother"],
          "Aurora": ["Flora", "Fauna", "Merryweather", "Prince Phillip"], "Ariel": ["Flounder", "Sebastian", "Scuttle", "Prince Eric", "Max"],
          "Belle": ["Lumière", "Cogsworth", "Mrs. Potts", "Chip", "Maurice", "Philippe"], "Jasmine": ["Rajah", "Aladdin", "The Genie", "Abu"],
          "Pocahontas": ["Meeko", "Flit", "Grandmother Willow", "Nakoma", "John Smith"], "Mulan": ["Mushu", "Cri-Kee", "Khan", "Li Shang", "Yao", "Ling", "Chien-Po"],
          "Tiana": ["Louis", "Ray", "Prince Naveen", "Charlotte", "Mama Odie"], "Rapunzel": ["Pascal", "Maximus", "Flynn Rider"], "Merida": ["Angus"],
          "Moana": ["Maui", "Heihei", "Pua", "Gramma Tala"], "Raya": ["Sisu", "Tuk Tuk", "Boun", "Tong"], "Anna": ["Olaf", "Sven", "Kristoff"],
          "Elsa": ["Olaf", "Sven", "Kristoff"]}
PICK = {"Snow White": "Doc", "Cinderella": "Jaq", "Aurora": "Flora", "Ariel": "Flounder", "Belle": "Lumière", "Jasmine": "Rajah", "Pocahontas": "Meeko",
        "Mulan": "Mushu", "Tiana": "Louis", "Rapunzel": "Pascal", "Merida": "Angus", "Moana": "Heihei", "Raya": "Sisu", "Anna": "Kristoff", "Elsa": "Olaf"}
ALLFR = sorted({x for v in FRIEND.values() for x in v})


def friend_pool(p):
    own = set(FRIEND[p]) | ({"Olaf", "Sven", "Kristoff"} if p in ("Anna", "Elsa") else set())
    return [x for x in ALLFR if x not in own]


FQ = {"Flounder", "Sebastian", "Scuttle", "Pascal", "Maximus", "Rajah", "Meeko", "Flit", "Mushu", "Cri-Kee", "Khan", "Louis", "Ray", "Heihei", "Pua",
      "Gus", "Jaq", "Bruno", "Angus", "Philippe", "Sisu", "Tuk Tuk", "Lumière", "Cogsworth", "Mrs. Potts", "Chip", "Doc", "Grumpy", "Happy", "Sleepy",
      "Bashful", "Sneezy", "Dopey", "Maui"}


def pn(r, q, ans, *ex, v=None):
    return mc(r, q, ans, names_wo(ans, *ex), v=v)


# ---------------------------------------------------------------- 2-5
def kids():
    r = rng_for("disney", "2-5")
    out = []
    # --- image questions
    for p in NAMES:
        for q in ["Who is this princess?", "Which princess is this?", "What is her name?", "Can you name her?"]:
            out.append(mc(r, q, p, names_wo(p), v=pimg(p)))
    # --- emoji clue -> princess
    for e, p in UNIQ:
        for q in ["Which princess goes with this?", "Who goes with this?", "Whose story has this?", "Find the princess for this!"]:
            out.append(mc(r, q, p, names_wo(p, *[x for x in NAMES if p in FIT[e] and False]), v=emoji(e)))
    out.append(mc(r, "Who ate the poisoned apple?", "Snow White", names_wo("Snow White"), v=emoji("🍎")))
    out.append(mc(r, "Who fell asleep from a spindle?", "Aurora", names_wo("Aurora", "Snow White"), v=emoji("😴")))
    # --- princess -> emoji
    for p in NAMES:
        ans = [c[0] for c in CL if c[1] == p]
        bad = [e for e in FIT if p not in FIT[e]]
        if not ans: continue
        qs = ["Which one goes with {}?", "Find something for {}!", "Tap the one for {}!", "Which one is from {}'s story?", "Which is {}'s?"]
        for q in qs:
            out.append(mc(r, q.format(p), r.choice(ans), bad, ct="emoji"))
    # --- character -> princess
    for c, m, p, f in CH:
        if not p: continue
        out.append(mc(r, f"Whose story has {c}?", p, names_wo(p)))
        if c in FQ:
            out.append(mc(r, f"Who is {c}'s friend?", p, names_wo(p)))
    # --- simple text
    t = lambda q, a, ex=(): out.append(mc(r, q, a, names_wo(a, *ex)))
    for q, a, ex in [("Who lost a glass slipper?", "Cinderella", ()), ("Who lives with seven dwarfs?", "Snow White", ()), ("Who sings Let It Go?", "Elsa", ()),
                     ("Who sings Part of Your World?", "Ariel", ()), ("Who sings How Far I'll Go?", "Moana", ()), ("Who sings Colors of the Wind?", "Pocahontas", ()),
                     ("Who sings Reflection?", "Mulan", ()), ("Who has long, magic hair?", "Rapunzel", ()), ("Who has ice magic?", "Elsa", ()),
                     ("Who has a pet tiger?", "Jasmine", ()), ("Who has a fish friend?", "Ariel", ("Moana",)), ("Who has a chameleon friend?", "Rapunzel", ()),
                     ("Who has a rooster friend?", "Moana", ()), ("Who has a raccoon friend?", "Pocahontas", ()), ("Who kisses a frog?", "Tiana", ()),
                     ("Who works in a restaurant?", "Tiana", ()), ("Whose mom turns into a bear?", "Merida", ()), ("Who joins the army?", "Mulan", ()),
                     ("Who loves the Beast?", "Belle", ()), ("Who sleeps from a spinning wheel?", "Aurora", ("Snow White",)),
                     ("Who rides a magic carpet?", "Jasmine", ()), ("Who lives in a tower?", "Rapunzel", ()), ("Who is a mermaid?", "Ariel", ()),
                     ("Who builds a snowman with Anna?", "Elsa", ())]:
        t(q, a, ex)
    out += [
        mc(r, "Who is the snowman?", "Olaf", ["Sven", "Hans", "Flynn", "Maui"]),
        mc(r, "Who is the snowman in Frozen?", "Olaf", ["Sven", "Hans", "Pascal", "Louis"]),
        mc(r, "Cinderella lost a what?", "👠", ["👒", "🧤", "💍", "🧦"], ct="emoji"),
        mc(r, "Snow White ate a what?", "🍎", ["🍌", "🍇", "🥕", "🍪"], ct="emoji"),
        mc(r, "Elsa makes what?", "❄️", ["🔥", "🌳", "🌵", "☀️"], ct="emoji"),
        mc(r, "Rapunzel lives in a what?", "Tower", ["Boat", "Cave", "Tent", "Submarine"]),
        mc(r, "Ariel is a what?", "Mermaid", ["Fairy", "Dragon", "Witch", "Bird"]),
        mc(r, "Where does Ariel live?", "In the sea", ["In a tower", "In a forest", "On the moon", "In a desert"]),
        mc(r, "What does Moana sail across?", "The ocean", ["A desert", "A mountain", "A field", "A snowy hill"]),
        mc(r, "What color is Belle's rose?", "Red", ["Blue", "Green", "Black", "Orange"]),
        mc(r, "What does Rapunzel have?", "Long hair", ["A tail", "Wings", "A crown of ice", "Fins"]),
        mc(r, "How many dwarfs are there?", "7", ["3", "5", "9", "12"]),
        mc(r, "Cinderella has how many stepsisters?", "2", ["1", "3", "4", "5"]),
        mc(r, "How many wishes does the Genie give?", "3", ["1", "2", "4", "5"]),
        mc(r, "How many good fairies help Aurora?", "3", ["1", "2", "4", "5"]),
        mc(r, "Merida has how many little brothers?", "3", ["1", "2", "4", "5"]),
    ]
    return out


# ---------------------------------------------------------------- 6-10
EASY = [
    ("Snow White", "lives with seven dwarfs in the woods"), ("Snow White", "bites a poisoned apple"),
    ("Snow White", "is chased by a jealous queen with a magic mirror"),
    ("Cinderella", "loses a glass slipper at the royal ball"), ("Cinderella", "has a fairy godmother who sings 'Bibbidi-Bobbidi-Boo'"),
    ("Cinderella", "has two stepsisters named Anastasia and Drizella"), ("Cinderella", "has mouse friends named Gus and Jaq"),
    ("Cinderella", "must leave the ball before midnight"),
    ("Aurora", "is cursed to prick her finger on a spinning wheel"), ("Aurora", "is raised in the woods by three good fairies"),
    ("Aurora", "is known as Briar Rose while she hides in the forest"), ("Aurora", "is cursed by the fairy Maleficent"),
    ("Ariel", "is a mermaid who wants to live on land"), ("Ariel", "trades her voice to a sea witch"), ("Ariel", "has a friend named Flounder"),
    ("Ariel", "collects human objects like forks and pipes"), ("Ariel", "lives in the kingdom of Atlantica"), ("Ariel", "is the youngest daughter of King Triton"),
    ("Belle", "loves to read books"), ("Belle", "lives in an enchanted castle with talking objects"), ("Belle", "is given a giant library by the Beast"),
    ("Belle", "has an inventor father named Maurice"), ("Belle", "is chased by the vain hunter Gaston"),
    ("Jasmine", "lives in the city of Agrabah"), ("Jasmine", "has a pet tiger named Rajah"), ("Jasmine", "rides a magic carpet with Aladdin"),
    ("Jasmine", "is the daughter of the Sultan"),
    ("Pocahontas", "is the daughter of Chief Powhatan"), ("Pocahontas", "has a raccoon friend named Meeko"), ("Pocahontas", "talks to Grandmother Willow"),
    ("Pocahontas", "meets the English settler John Smith"),
    ("Mulan", "takes her father's place in the army"), ("Mulan", "pretends to be a soldier named Ping"), ("Mulan", "has a small dragon guardian named Mushu"),
    ("Mulan", "defeats the Hun leader Shan Yu"),
    ("Tiana", "dreams of opening her own restaurant"), ("Tiana", "is turned into a frog"), ("Tiana", "lives in New Orleans"),
    ("Tiana", "meets a prince named Naveen"), ("Tiana", "is friends with a trumpet-playing alligator named Louis"),
    ("Rapunzel", "has magic golden hair that glows"), ("Rapunzel", "is locked in a tower by Mother Gothel"), ("Rapunzel", "has a chameleon friend named Pascal"),
    ("Rapunzel", "dreams of seeing the floating lanterns"), ("Rapunzel", "meets a thief named Flynn Rider"),
    ("Merida", "is a Scottish princess with wild red curls"), ("Merida", "is a skilled archer"), ("Merida", "turns her mother into a bear"),
    ("Merida", "has a horse named Angus"),
    ("Moana", "sails across the ocean to save her island"), ("Moana", "is helped by the demigod Maui"), ("Moana", "has a pet rooster named Heihei"),
    ("Moana", "returns the heart of Te Fiti"),
    ("Raya", "searches for the last dragon"), ("Raya", "comes from the land of Heart"), ("Raya", "has a pet named Tuk Tuk"),
    ("Raya", "wants to bring Kumandra back together"),
    ("Anna", "sets out to find her sister Elsa"), ("Anna", "is helped by the ice harvester Kristoff"), ("Anna", "has a heart that is frozen"),
    ("Anna", "is the younger sister of Elsa"),
    ("Elsa", "has magic powers over ice and snow"), ("Elsa", "builds an ice palace after singing 'Let It Go'"), ("Elsa", "becomes the queen of Arendelle"),
    ("Elsa", "is the older sister of Anna"), ("Elsa", "wears gloves to hide her powers"),
]
DWARF = [("Which dwarf is always grumpy?", "Grumpy"), ("Which dwarf never says a word?", "Dopey"), ("Which dwarf is the leader?", "Doc"),
         ("Which dwarf is always shy?", "Bashful"), ("Which dwarf keeps sneezing?", "Sneezy"), ("Which dwarf is always tired?", "Sleepy"),
         ("Which dwarf is always cheerful?", "Happy")]
DW = ["Doc", "Grumpy", "Happy", "Sleepy", "Bashful", "Sneezy", "Dopey"]


def mid():
    r = rng_for("disney", "6-10")
    out = []
    # --- image questions
    for p in NAMES:
        out.append(mc(r, "Which princess is this?", p, names_wo(p), v=pimg(p)))
        out.append(mc(r, "What is this princess's name?", p, names_wo(p), v=pimg(p)))
        pool = movies_wo(MOVIE[p]) if p not in ("Anna", "Elsa") else movies_wo("Frozen")
        out.append(mc(r, "Which movie is she from?", MOVIE[p], pool, v=pimg(p)))
        out.append(mc(r, "Which of these is her friend?", PICK[p], friend_pool(p), v=pimg(p)))
    for vname, vm, p in VIL:
        out.append(mc(r, "Who is the villain in her movie?", vname, [x[0] for x in VIL if x[0] != vname], v=pimg(p)))
    for p, lv in LOVE.items():
        out.append(mc(r, "Who is her prince or love interest?", lv, [x for x in LOVE.values() if x != lv], v=pimg(p)))
    # --- emoji clues
    for e, p in UNIQ:
        out.append(mc(r, "Which princess matches this clue?", p, names_wo(p), v=emoji(e)))
    # --- clues
    for p, c in EASY:
        out.append(mc(r, f"Which princess {c}?", p, names_wo(p)))
    # --- characters
    for c, m, p, f in CH:
        out.append(mc(r, f"Which movie has {c} in it?", m, movies_wo(m)))
        out.append(mc(r, f"{c} is from which movie?", m, movies_wo(m)))
        if p:
            out.append(mc(r, f"Which princess's story has {c}?", p, names_wo(p)))
    for c, k, ban in ANIM:
        out.append(mc(r, f"What kind of animal is {c}?", k, [x for x in KINDS if x != k and x not in ban]))
    for c, k in OBJ:
        out.append(mc(r, f"What is {c}?", k, [x for x in OBJK if x != k]))
    # --- villains
    for vname, vm, p in VIL:
        out.append(mc(r, f"Who is the villain in {vm}?", vname, [x[0] for x in VIL if x[0] != vname]))
        out.append(mc(r, f"{vname} is the villain in which movie?", vm, movies_wo(vm)))
    for q, a in VDESC:
        out.append(mc(r, q, a, [x[0] for x in VIL if x[0] != a]))
    # --- songs
    for s, m, p in SONGS:
        poolm = [x for x in MOVIES + ["Frozen II"] if x != m and not (m in ("Frozen", "Frozen II") and x in ("Frozen", "Frozen II"))]
        out.append(mc(r, f"Which movie has the song '{s}'?", m, poolm))
        if p:
            out.append(mc(r, f"Which princess sings '{s}'?", p, names_wo(p)))
    # --- settings
    for p, pl in PLACE.items():
        out.append(mc(r, f"Where does {p} live?" if p not in ("Anna", "Elsa") else f"Where does {p} live as a princess?", pl, [x for x in PLACES if x != pl]))
    for m, pl in [("Aladdin", "Agrabah"), ("The Princess and the Frog", "New Orleans"), ("Brave", "Scotland"), ("Mulan", "China"), ("Tangled", "Corona"),
                  ("Frozen", "Arendelle"), ("Raya and the Last Dragon", "Kumandra"), ("Pocahontas", "Virginia"), ("The Little Mermaid", "Under the sea")]:
        pools = movies_wo(m) if m != "Frozen" else movies_wo("Frozen")
        out.append(mc(r, f"Which movie takes place {pl.lower()}?" if pl == "Under the sea" else f"Which movie takes place in {pl}?", m, pools))
    for q, a in DWARF:
        out.append(mc(r, q, a, [x for x in DW if x != a]))
    out += [
        mc(r, "How many dwarfs live with Snow White?", "7", ["3", "5", "6", "9"]), mc(r, "How many stepsisters does Cinderella have?", "2", ["1", "3", "4", "5"]),
        mc(r, "How many wishes does the Genie grant?", "3", ["1", "2", "4", "5"]), mc(r, "How many good fairies raise Aurora?", "3", ["1", "2", "4", "5"]),
        mc(r, "How many brothers does Merida have?", "3", ["1", "2", "4", "5"]), mc(r, "How many days does Ariel get to win Eric's kiss?", "3", ["1", "2", "5", "7"]),
        mc(r, "How many sisters does Ariel have?", "6", ["2", "3", "4", "8"]), mc(r, "How long is Rapunzel's hair?", "70 feet", ["7 feet", "20 feet", "120 feet", "300 feet"]),
        mc(r, "What color is Cinderella's ball gown?", "Blue", ["Red", "Yellow", "Green", "Black"]),
        mc(r, "What color is Belle's ball gown?", "Yellow", ["Red", "Blue", "Green", "Black"]),
        mc(r, "What is Ariel's hair color?", "Red", ["Blonde", "Black", "Brown", "Silver"]),
        mc(r, "What kind of hair does Merida have?", "Curly red hair", ["Long straight black hair", "Short blonde hair", "Silver braids", "A tall bun of white hair"]),
        mc(r, "What did Cinderella's Fairy Godmother turn a pumpkin into?", "A coach", ["A castle", "A boat", "A horse", "A ball gown"]),
        mc(r, "What did Cinderella lose at the ball?", "A glass slipper", ["A ring", "A crown", "A necklace", "A glove"]),
        mc(r, "What did Ariel give up to get legs?", "Her voice", ["Her tail's color", "Her hair", "Her shell necklace", "Her crown"]),
        mc(r, "What does the Beast give Belle as a gift?", "A library", ["A crown", "A horse", "A pet bird", "A boat"]),
        mc(r, "What is Elsa's snowman called?", "Olaf", ["Sven", "Pascal", "Hans", "Maui"]),
        mc(r, "Who is Kristoff's reindeer?", "Sven", ["Olaf", "Maximus", "Angus", "Khan"]),
        mc(r, "What is Maui's tool?", "A magic fish hook", ["A trident", "A staff", "A boomerang", "A canoe paddle"]),
        mc(r, "What lights up the sky in Tangled?", "Floating lanterns", ["Fireworks", "Balloons", "Kites", "Comets"]),
        mc(r, "What kind of animal is Mushu?", "A dragon", ["A cricket", "A horse", "A bear", "A monkey"]),
        mc(r, "What flies over Aladdin and Jasmine?", "A magic carpet", ["A broom", "A kite", "A cloud", "A rocket"]),
    ]
    return out


# ---------------------------------------------------------------- 11+
SRC = [
    ("Snow White and the Seven Dwarfs", "Brothers Grimm", "Hans Christian Andersen|Charles Perrault|Aesop|Lewis Carroll"),
    ("Cinderella", "Charles Perrault", "Hans Christian Andersen|Aesop|Lewis Carroll|Carlo Collodi"),
    ("Sleeping Beauty", "Charles Perrault", "Hans Christian Andersen|Aesop|Lewis Carroll|Carlo Collodi"),
    ("The Little Mermaid", "Hans Christian Andersen", "Brothers Grimm|Charles Perrault|Aesop|Lewis Carroll"),
    ("Beauty and the Beast", "Gabrielle-Suzanne de Villeneuve", "Hans Christian Andersen|Brothers Grimm|Aesop|Lewis Carroll"),
    ("Aladdin", "One Thousand and One Nights (Arabian Nights)", "Brothers Grimm|Hans Christian Andersen|Aesop's Fables|The Jungle Book"),
    ("Mulan", "The Ballad of Hua Mulan", "Journey to the West|Aesop's Fables|The Tale of Genji|The Arabian Nights"),
    ("The Princess and the Frog", "The Frog Prince (Brothers Grimm)", "The Snow Queen|Rapunzel|Puss in Boots|Peter Pan"),
    ("Tangled", "Rapunzel (Brothers Grimm)", "The Snow Queen|The Frog Prince|Puss in Boots|Peter Pan"),
    ("Frozen", "The Snow Queen by Hans Christian Andersen", "Rapunzel by the Brothers Grimm|Cinderella by Charles Perrault|The Frog Prince|Peter Pan"),
    ("Moana", "Polynesian mythology and legends", "Arabian folk tales|Norse sagas|Greek myths|Chinese poetry"),
    ("Pocahontas", "The life of a real Powhatan woman", "A Brothers Grimm tale|An Andersen tale|A Greek myth|A Perrault tale"),
]
HARD = [
    ("Which princess is the daughter of Chief Powhatan?", "Pocahontas", ()), ("Which princess is the daughter of King Triton?", "Ariel", ()),
    ("Which princess's father is named Maurice?", "Belle", ()), ("Which princess's father is named Fa Zhou?", "Mulan", ()),
    ("Which princess's father is the Sultan?", "Jasmine", ()), ("Which princess's father is Chief Tui?", "Moana", ()),
    ("Which princess's father is Chief Benja?", "Raya", ()), ("Which princess's mother is Queen Elinor?", "Merida", ()),
    ("Which princess's father is King Fergus?", "Merida", ()), ("Which princess's father is King Stefan?", "Aurora", ()),
    ("Which princess's stepmother is Lady Tremaine?", "Cinderella", ()), ("Which princess's stepmother is the Evil Queen?", "Snow White", ()),
    ("Which princess is raised by Mother Gothel?", "Rapunzel", ()), ("Which princess is the younger daughter of King Agnarr and Queen Iduna?", "Anna", ()),
    ("Which princess is the lost princess of Corona?", "Rapunzel", ()), ("Which princess grew up in the kingdom of Atlantica?", "Ariel", ()),
    ("Which princess is from Clan DunBroch?", "Merida", ()), ("Which princess comes from the land of Heart?", "Raya", ()),
    ("Which princess has a grandmother named Tala?", "Moana", ()), ("Which princess has a best friend named Charlotte La Bouff?", "Tiana", ()),
    ("Which princess has a friend named Nakoma?", "Pocahontas", ()), ("Which princess is called Briar Rose?", "Aurora", ()),
    ("Which princess is disguised as 'Ping'?", "Mulan", ()), ("Which princess is the youngest of King Triton's seven daughters?", "Ariel", ()),
    ("Which princess's love interest is Li Shang?", "Mulan", ()), ("Which princess's love interest is Kristoff?", "Anna", ()),
    ("Which princess falls for the thief Flynn Rider?", "Rapunzel", ()), ("Which princess falls for the street thief Aladdin?", "Jasmine", ()),
    ("Which princess marries Prince Naveen?", "Tiana", ()),
    ("Which princess falls for the human Prince Eric?", "Ariel", ()), ("Which princess falls for the English captain John Smith?", "Pocahontas", ()),
    ("Which princess falls for Prince Phillip?", "Aurora", ()),
]
PLOT = [
    ("What was Disney's first full-length animated feature film (1937)?", "Snow White and the Seven Dwarfs", "Cinderella|Pinocchio|Fantasia|Bambi"),
    ("What do the seven dwarfs do for a living?", "Mine for jewels", "Bake bread|Fish at sea|Farm wheat|Weave cloth"),
    ("What does the Evil Queen disguise herself as to trick Snow White?", "An old peddler woman", "A traveling fairy|A kitchen maid|A royal guard|A talking mirror"),
    ("What does the Evil Queen order the Huntsman to bring back?", "Snow White's heart", "Her crown|Her ring|Her shoes|Her mirror"),
    ("Which song do the dwarfs sing as they march to work?", "Heigh-Ho", "Whistle While You Work|Someday My Prince Will Come|I'm Wishing|With a Smile and a Song"),
    ("What breaks the spell on Snow White?", "Love's first kiss", "A magic potion|A wizard's spell|A magic song|A glass of water"),
    ("What time does the Fairy Godmother's magic wear off?", "Midnight", "Noon|Sunset|Dawn|Six o'clock"),
    ("What does the Fairy Godmother turn into a coach?", "A pumpkin", "A cabbage|A melon|A barrel|A basket"),
    ("What are the names of Cinderella's stepsisters?", "Anastasia and Drizella", "Flora and Fauna|Charlotte and Louise|Marian and Doris|Alice and Grace"),
    ("What is the name of Lady Tremaine's cat?", "Lucifer", "Figaro|Dinah|Duchess|Oliver"),
    ("Which mice are Cinderella's friends?", "Gus and Jaq", "Chip and Dale|Mickey and Minnie|Tom and Jerry|Bernard and Bianca"),
    ("Who locks Cinderella in her room?", "Lady Tremaine", "Anastasia|Drizella|Lucifer|The Grand Duke"),
    ("Who carries the glass slipper around the kingdom?", "The Grand Duke", "Prince Charming|The Huntsman|Lady Tremaine|The King's cook"),
    ("Who casts the sleeping curse on Aurora?", "Maleficent", "Flora|Merryweather|Lady Tremaine|The Evil Queen"),
    ("How old is Aurora when the curse is meant to strike?", "Sixteen", "Twelve|Eighteen|Twenty-one|Fourteen"),
    ("Which three fairies raise Aurora?", "Flora, Fauna and Merryweather", "Flora, Fauna and Tinker Bell|Fauna, Luna and Ivy|Rose, Lily and Daisy|Merry, Pippa and Flora"),
    ("What is the name of Maleficent's raven?", "Diablo", "Iago|Zazu|Flit|Scuttle"),
    ("What does Maleficent turn into in the final battle?", "A fire-breathing dragon", "A giant spider|A raven|A wolf|A stone statue"),
    ("What helps Prince Phillip defeat Maleficent?", "The Sword of Truth", "The Sword of Light|The Sword of Fire|A magic wand|A silver shield"),
    ("Whose music does Sleeping Beauty adapt?", "Tchaikovsky", "Mozart|Beethoven|Bach|Chopin"),
    ("Which song do Aurora and Phillip dance to in the forest?", "Once Upon a Dream", "A Whole New World|Part of Your World|Colors of the Wind|Someday My Prince Will Come"),
    ("What does Ariel give Ursula in exchange for legs?", "Her voice", "Her tail's color|Her crown|Her shell necklace|Her hair"),
    ("How many days does Ariel have to win Eric's kiss?", "Three", "One|Five|Seven|Ten"),
    ("What are Ursula's two eels called?", "Flotsam and Jetsam", "Ebb and Flow|Snap and Crackle|Slick and Slime|Tide and Reef"),
    ("What does Scuttle call a fork?", "A dinglehopper", "A snarfblatt|A thingamabob|A whatsit|A doohickey"),
    ("What does Scuttle call a pipe?", "A snarfblatt", "A dinglehopper|A thingamabob|A whatsit|A doohickey"),
    ("What is the name of Ariel's underwater kingdom?", "Atlantica", "Atlantis|Aquaria|Marinova|Coralia"),
    ("How does Eric defeat Ursula in the end?", "He rams her with a ship's bow", "He sings her a song|He locks her in a cage|He freezes her|He tricks her with a mirror"),
    ("Which song does Sebastian sing to keep Ariel in the sea?", "Under the Sea", "Part of Your World|Kiss the Girl|Poor Unfortunate Souls|Les Poissons"),
    ("Which song does Ursula sing to offer Ariel a deal?", "Poor Unfortunate Souls", "Under the Sea|Part of Your World|Kiss the Girl|Be Our Guest"),
    ("What is the name of Eric's dog?", "Max", "Pluto|Bruno|Rex|Marley"),
    ("What kind of flower is enchanted in the Beast's castle?", "A rose", "A tulip|A lily|A daisy|An orchid"),
    ("What is Cogsworth?", "A mantel clock", "A candelabra|A teapot|A teacup|A feather duster"),
    ("What is Belle's father's job?", "Inventor", "Baker|Blacksmith|Farmer|Doctor"),
    ("What is the name of Belle's horse?", "Philippe", "Maximus|Khan|Angus|Samson"),
    ("How does Gaston meet his end?", "He falls from the castle tower", "He is turned into a rose|He is frozen|He is locked in a dungeon|He sails away"),
    ("Who sings 'Be Our Guest'?", "Lumière", "Cogsworth|Gaston|Mrs. Potts|LeFou"),
    ("Who sings the title song 'Beauty and the Beast'?", "Mrs. Potts", "Belle|Lumière|Gaston|Chip"),
    ("What is the name of Gaston's sidekick?", "LeFou", "Lumière|Philippe|Maurice|Cogsworth"),
    ("What happens if the last rose petal falls?", "The Beast stays a beast forever", "The castle disappears|Belle goes home|Gaston wins the town|The Beast becomes a prince"),
    ("Beauty and the Beast was the first animated film nominated for which Oscar?", "Best Picture", "Best Director|Best Actress|Best Costume|Best Writing"),
    ("What does Aladdin use his third wish for?", "To free the Genie", "To become a prince|To marry Jasmine|To be rich|To defeat Jafar"),
    ("What is Jafar's job at the start of Aladdin?", "Royal vizier", "Palace cook|Royal guard|Court jester|Stable keeper"),
    ("What is the name of the place where the lamp is found?", "The Cave of Wonders", "The Cave of Treasures|The Sultan's Cave|The Magic Grotto|The Lamp Cave"),
    ("Who voiced the Genie in the 1992 film?", "Robin Williams", "Eddie Murphy|Jim Carrey|Mike Myers|Tim Allen"),
    ("How does Jafar end up at the film's end?", "Trapped in a lamp as a genie", "Turned to stone|Sent to prison|Banished to the desert|Eaten by Rajah"),
    ("Which English settlement appears in Pocahontas?", "Jamestown", "Plymouth|Boston|Salem|Philadelphia"),
    ("Who is the greedy leader of the settlers in Pocahontas?", "Governor Ratcliffe", "John Smith|Kocoum|Chief Powhatan|Thomas"),
    ("What is the name of Governor Ratcliffe's pug?", "Percy", "Meeko|Max|Pongo|Bolt"),
    ("Which warrior is promised to Pocahontas?", "Kocoum", "John Smith|Thomas|Ratcliffe|Powhatan"),
    ("Which Oscar did 'Colors of the Wind' win?", "Best Original Song", "Best Picture|Best Director|Best Costume|Best Sound"),
    ("What does Mulan do to stop the Huns on the mountain?", "Fires a cannon to cause an avalanche", "Builds a wall|Talks them down|Floods the valley|Calls the Emperor"),
    ("Who is Mulan's captain and love interest?", "Li Shang", "Chi-Fu|Yao|Shan Yu|Ling"),
    ("Which song teaches the recruits to be soldiers?", "I'll Make a Man Out of You", "Reflection|A Girl Worth Fighting For|Honor to Us All|True to Your Heart"),
    ("What is Mulan's lucky cricket called?", "Cri-Kee", "Jiminy|Jaq|Zazu|Flit"),
    ("Who is Mulan's father?", "Fa Zhou", "Chi-Fu|Li Shang|Shan Yu|Yao"),
    ("What is Tiana's dream?", "To open her own restaurant", "To become a queen|To sail the world|To be a singer|To fly a plane"),
    ("What instrument does Louis the alligator play?", "Trumpet", "Trombone|Clarinet|Saxophone|Violin"),
    ("What kind of insect is Ray?", "A firefly", "A ladybug|A bee|A dragonfly|A cricket"),
    ("Who does Ray the firefly love?", "Evangeline, a star", "Charlotte|Mama Odie|Louis|The Moon"),
    ("What country is Prince Naveen from?", "Maldonia", "Genovia|Agrabah|Corona|Arendelle"),
    ("Who is Tiana's rich best friend?", "Charlotte La Bouff", "Mama Odie|Eudora|Lawrence|Georgie"),
    ("Which sweet New Orleans pastry is Tiana famous for?", "Beignets", "Churros|Waffles|Croissants|Macarons"),
    ("Which princess was Disney's first Black princess?", "Tiana", "Jasmine|Mulan|Moana|Pocahontas"),
    ("What kind of animation is The Princess and the Frog?", "Traditional hand-drawn", "Stop-motion|Fully 3D computer animation|Claymation|Live action"),
    ("How long is Rapunzel's hair?", "About 70 feet", "About 7 feet|About 20 feet|About 120 feet|About 300 feet"),
    ("What is Flynn Rider's real name?", "Eugene Fitzherbert", "Edward Fitzwilliam|Eric Fitzgerald|Evan Fitzpatrick|Ethan Fitzhugh"),
    ("What is the name of the pub where the thugs sing 'I've Got a Dream'?", "The Snuggly Duckling", "The Salty Dog|The Golden Goose|The Drunken Duck|The Happy Hound"),
    ("What weapon does Rapunzel use?", "A frying pan", "A sword|A bow|A broom|A rolling pin"),
    ("What color does Rapunzel's hair become after it is cut?", "Brown", "Black|Red|White|Gray"),
    ("What does Mother Gothel use to stay young?", "A magic golden flower", "A silver rose|A blue lily|A magic mushroom|A red tulip"),
    ("What does Rapunzel see floating every year on her birthday?", "Lanterns", "Balloons|Fireflies|Kites|Fireworks"),
    ("Which kingdom is Rapunzel the lost princess of?", "Corona", "Arendelle|Agrabah|Atlantica|Maldonia"),
    ("What heals Eugene at the end of Tangled?", "Rapunzel's tear", "A kiss|A song|Her hair|A flower"),
    ("What does Merida's mother turn into?", "A bear", "A wolf|A deer|An eagle|A horse"),
    ("What is the name of the bear that attacked King Fergus?", "Mor'du", "Mor'ven|Fergus|Dingwall|MacGuffin"),
    ("What skill does Merida compete in for her own hand?", "Archery", "Sword fighting|Horse racing|Wrestling|Chess"),
    ("What are the names of Merida's brothers?", "Harris, Hubert and Hamish", "Hamish, Hugh and Harry|Hector, Hugo and Hal|Harold, Hank and Hubert|Henry, Hubert and Hector"),
    ("Which studio made Brave?", "Pixar", "DreamWorks|Illumination|Sony Pictures Animation|Aardman"),
    ("What leads Merida to the witch's cottage?", "Will-o'-the-wisps", "Fireflies|Wolves|Ravens|A map"),
    ("What deadline does Merida face to break the spell?", "The second sunrise", "Midnight|The next full moon|Sunset|Her birthday"),
    ("What is the name of Merida's mother?", "Elinor", "Fiona|Isla|Moira|Eilidh"),
    ("What is the name of Moana's island?", "Motunui", "Te Fiti|Lalotai|Kakamora|Hawaiki"),
    ("What does Moana return to Te Fiti?", "Her heart", "Her crown|Her sword|Her shell|Her staff"),
    ("What is Maui's magical tool?", "A fish hook", "A trident|A staff|A boomerang|A canoe paddle"),
    ("What animal does Gramma Tala become?", "A manta ray", "A turtle|A whale|A dolphin|A shark"),
    ("Who is the giant crab who loves shiny things?", "Tamatoa", "Kakamora|Te Kā|Maui|Heihei"),
    ("What is the lava monster in Moana called?", "Te Kā", "Te Fiti|Tamatoa|Kakamora|Maui"),
    ("What are the tiny coconut-armored pirates called?", "The Kakamora", "The Druun|The Huns|The Pirates of Corona|The Shadow Men"),
    ("What is the name of the dragon in Raya and the Last Dragon?", "Sisu", "Mushu|Elliott|Toothless|Drogon"),
    ("Which five lands make up Kumandra?", "Heart, Fang, Talon, Spine and Tail", "Heart, Fang, Claw, Back and Tail|Sun, Moon, Star, Sea and Sky|North, South, East, West and Center|Fire, Water, Earth, Air and Spirit"),
    ("What is the evil force in Raya called?", "The Druun", "The Dark|The Shadow Mist|The Void|The Gloom"),
    ("What do the Druun do to people?", "Turn them to stone", "Freeze them in ice|Make them invisible|Put them to sleep|Turn them into animals"),
    ("What magical item holds the dragons' power?", "The Dragon Gem", "The Dragon Crown|The Dragon Pearl|The Dragon Staff|The Dragon Sword"),
    ("Which land is Namaari the princess of?", "Fang", "Heart|Talon|Spine|Tail"),
    ("What is the name of Arendelle's villainous prince?", "Hans", "Kristoff|Olaf|Oaken|Sven"),
    ("What does Olaf dream about?", "Summer", "Winter|Spring|Autumn|Skiing"),
    ("What heals Anna's frozen heart?", "An act of true love", "A kiss from Hans|A magic potion|Warm sunlight|A troll's spell"),
    ("Who is the leader of the trolls in Frozen?", "Grand Pabbie", "Bulda|Oaken|Kristoff|Cliff"),
    ("Where does Elsa build her ice palace?", "On the North Mountain", "In the Enchanted Forest|On the Southern Isles|At the fjord|In Arendelle's harbor"),
    ("What is the name of Hans's home?", "The Southern Isles", "The North Mountain|Weselton|Corona|Atlantica"),
    ("In Frozen II, what water spirit does Elsa tame?", "The Nokk", "Bruni|Gale|The Earth Giants|Marshmallow"),
    ("In Frozen II, what is the name of the river of memory Elsa seeks?", "Ahtohallan", "Northuldra|Arendelle|The Dark Sea|The Enchanted Forest"),
    ("In Frozen II, which people live in the Enchanted Forest?", "The Northuldra", "The Southern Islanders|The Trolls|The Giants|The Weseltonians"),
    ("Who becomes queen of Arendelle at the end of Frozen II?", "Anna", "Elsa|Honeymaren|Mattias|Kristoff"),
]
VOICE = [("Elsa", "Frozen", "Idina Menzel"), ("Anna", "Frozen", "Kristen Bell"), ("Olaf", "Frozen", "Josh Gad"), ("Kristoff", "Frozen", "Jonathan Groff"),
         ("Hans", "Frozen", "Santino Fontana"), ("Moana", "Moana", "Auli'i Cravalho"), ("Maui", "Moana", "Dwayne Johnson"), ("Tamatoa", "Moana", "Jemaine Clement"),
         ("Heihei", "Moana", "Alan Tudyk"), ("Tiana", "The Princess and the Frog", "Anika Noni Rose"), ("Dr. Facilier", "The Princess and the Frog", "Keith David"),
         ("Rapunzel", "Tangled", "Mandy Moore"), ("Flynn Rider", "Tangled", "Zachary Levi"), ("Mother Gothel", "Tangled", "Donna Murphy"),
         ("Merida", "Brave", "Kelly Macdonald"), ("Mulan", "Mulan", "Ming-Na Wen"), ("Mushu", "Mulan", "Eddie Murphy"), ("Belle", "Beauty and the Beast", "Paige O'Hara"),
         ("the Beast", "Beauty and the Beast", "Robby Benson"), ("Lumière", "Beauty and the Beast", "Jerry Orbach"), ("Mrs. Potts", "Beauty and the Beast", "Angela Lansbury"),
         ("Gaston", "Beauty and the Beast", "Richard White"), ("Ariel", "The Little Mermaid", "Jodi Benson"), ("Ursula", "The Little Mermaid", "Pat Carroll"),
         ("Sebastian", "The Little Mermaid", "Samuel E. Wright"), ("Jasmine (speaking voice)", "Aladdin", "Linda Larkin"), ("the Genie", "Aladdin", "Robin Williams"),
         ("Aladdin", "Aladdin", "Scott Weinger"), ("Jafar", "Aladdin", "Jonathan Freeman"), ("Pocahontas", "Pocahontas", "Irene Bedard"),
         ("John Smith", "Pocahontas", "Mel Gibson"), ("Raya", "Raya and the Last Dragon", "Kelly Marie Tran"), ("Sisu", "Raya and the Last Dragon", "Awkwafina"),
         ("Namaari", "Raya and the Last Dragon", "Gemma Chan"), ("Cinderella", "Cinderella", "Ilene Woods"),
         ("Snow White", "Snow White and the Seven Dwarfs", "Adriana Caselotti"), ("Aurora", "Sleeping Beauty", "Mary Costa")]
MUSIC = [
    ("Who composed the music for The Little Mermaid, Aladdin and Pocahontas?", "Alan Menken", "Randy Newman|Hans Zimmer|Lin-Manuel Miranda|Robert Lopez"),
    ("Who wrote the lyrics for The Little Mermaid and Beauty and the Beast?", "Howard Ashman", "Stephen Schwartz|Lin-Manuel Miranda|David Zippel|Randy Newman"),
    ("Who wrote the lyrics for 'Colors of the Wind'?", "Stephen Schwartz", "Howard Ashman|Tim Rice|Lin-Manuel Miranda|David Zippel"),
    ("Who wrote the songs for Frozen?", "Kristen Anderson-Lopez and Robert Lopez", "Alan Menken and Howard Ashman|Lin-Manuel Miranda|Randy Newman|Phil Collins"),
    ("Which Broadway star co-wrote the songs for Moana?", "Lin-Manuel Miranda", "Robert Lopez|Alan Menken|Randy Newman|Stephen Schwartz"),
    ("Who wrote the songs for The Princess and the Frog?", "Randy Newman", "Alan Menken|Lin-Manuel Miranda|Phil Collins|Elton John"),
    ("Who wrote the songs for Mulan?", "Matthew Wilder and David Zippel", "Alan Menken and Stephen Schwartz|Randy Newman|Phil Collins|Elton John"),
    ("Who composed the music for Tangled?", "Alan Menken", "Randy Newman|Hans Zimmer|Lin-Manuel Miranda|Robert Lopez"),
    ("Who composed the score for Brave?", "Patrick Doyle", "Alan Menken|Hans Zimmer|Danny Elfman|John Williams"),
    ("Who composed the score for Raya and the Last Dragon?", "James Newton Howard", "Alan Menken|Hans Zimmer|Danny Elfman|John Williams"),
    ("Which Aladdin song won the Oscar for Best Original Song?", "A Whole New World", "Friend Like Me|Prince Ali|Arabian Nights|One Jump Ahead"),
    ("Which Little Mermaid song won the Oscar for Best Original Song?", "Under the Sea", "Part of Your World|Kiss the Girl|Poor Unfortunate Souls|Les Poissons"),
    ("Which Pocahontas song won the Oscar for Best Original Song?", "Colors of the Wind", "Just Around the Riverbend|Savages|Mine, Mine, Mine|Steady as the Beating Drum"),
    ("Which Frozen song won the Oscar for Best Original Song?", "Let It Go", "For the First Time in Forever|Love Is an Open Door|Do You Want to Build a Snowman?|Fixer Upper"),
    ("Which Beauty and the Beast song won the Oscar for Best Original Song?", "Beauty and the Beast", "Be Our Guest|Belle|Gaston|Something There"),
    ("Which Moana song was nominated for the Oscar for Best Original Song?", "How Far I'll Go", "You're Welcome|Shiny|We Know the Way|Where You Are"),
    ("Who wrote the songs for Snow White and the Seven Dwarfs (1937)?", "Frank Churchill and Larry Morey", "Alan Menken and Howard Ashman|Randy Newman|Richard and Robert Sherman|Phil Collins"),
    ("Which singer provided the singing voice for both Jasmine and Mulan?", "Lea Salonga", "Idina Menzel|Jodi Benson|Auli'i Cravalho|Anika Noni Rose"),
]
SETT = [
    ("Which fictional kingdom does Elsa rule?", "Arendelle", "Corona|Agrabah|Atlantica|Kumandra"),
    ("Which fictional kingdom is Rapunzel's home?", "Corona", "Arendelle|Agrabah|Atlantica|Maldonia"),
    ("Which fictional city is Aladdin set in?", "Agrabah", "Arendelle|Corona|Atlantica|Kumandra"),
    ("Which fictional land is the setting of Raya and the Last Dragon?", "Kumandra", "Agrabah|Arendelle|Corona|Motunui"),
    ("In which US city does The Princess and the Frog take place?", "New Orleans", "Savannah|Houston|Miami|Charleston"),
    ("Which country is Brave set in?", "Scotland", "Ireland|England|Wales|Norway"),
    ("Which country does Mulan's story take place in?", "China", "Japan|Korea|Mongolia|Thailand"),
    ("Which region of the world is Moana set in?", "The Pacific Islands (Polynesia)", "The Caribbean|The Mediterranean|Southeast Asia|The Arctic"),
    ("Which present-day US state is Pocahontas's story set in?", "Virginia", "Massachusetts|Florida|New York|Maryland"),
    ("Which year was Jamestown founded, the setting of Pocahontas?", "1607", "1492|1620|1776|1587"),
    ("Which real-world country inspires Belle's village?", "France", "Germany|Italy|England|Switzerland"),
    ("What is the name of Ariel's kingdom?", "Atlantica", "Atlantis|Aquaria|Marinova|Coralia"),
    ("Which of Kumandra's lands is Raya from?", "Heart", "Fang|Talon|Spine|Tail"),
    ("What is the name of the Pacific island home of Moana?", "Motunui", "Te Fiti|Lalotai|Kakamora|Hawaiki"),
    ("What is the Southern Isles in Frozen?", "Hans's homeland", "Elsa's ice palace|Anna's village|Olaf's land|Oaken's trading post"),
]


def mk_year(r, m):
    return mc(r, f"In which year was {m} released?" if m != "Frozen" else "In which year was the first Frozen movie released?", str(YEAR[m]),
              [str(YEAR[m] + d) for d in (-12, -7, -4, -2, 2, 3, 5, 8, 12) if 1930 < YEAR[m] + d < 2026])


def late():
    r = rng_for("disney", "11+")
    out = []
    # --- image questions
    for p in NAMES:
        out.append(mc(r, "Which Disney princess is shown here?", p, names_wo(p), v=pimg(p)))
        m = MOVIE[p]
        out.append(mc(r, "In which year was her first movie released?", str(YEAR[m]), [str(YEAR[m] + d) for d in (-12, -7, -4, 3, 5, 9, 12) if 1930 < YEAR[m] + d < 2026], v=pimg(p)))
    for vname, vm, p in VIL:
        out.append(mc(r, "Which villain appears in her movie?", vname, [x[0] for x in VIL if x[0] != vname], v=pimg(p)))
    for p, lv in LOVE.items():
        out.append(mc(r, "Who is her love interest in the movie?", lv, [x for x in LOVE.values() if x != lv], v=pimg(p)))
    for p, pl in PLACE.items():
        out.append(mc(r, "Where does her story take place?", pl, [x for x in PLACES if x != pl], v=pimg(p)))
    sm = {m: (s, w) for m, s, w in SRC}
    for p in NAMES:
        m = MOVIE[p]
        if m in sm:
            out.append(mc(r, "What inspired her movie?", sm[m][0], P(sm[m][1]), v=pimg(p)))
    # --- years
    for m in MOVIES:
        out.append(mk_year(r, m))
        out.append(mc(r, f"Which Disney film came out in {YEAR[m]}?" if m != "Frozen" else "Which film came out in 2013?", m, movies_wo(m)))
    out.append(mc(r, "In which year was Frozen II released?", "2019", ["2014", "2016", "2018", "2021"]))
    out.append(mc(r, "In which year was Moana 2 released?", "2024", ["2018", "2020", "2022", "2026"]))
    pairs = list(itertools.combinations(MOVIES, 4))
    r.shuffle(pairs)
    for combo in pairs[:70]:
        first = min(combo, key=lambda m: YEAR[m]); last = max(combo, key=lambda m: YEAR[m])
        names = ", ".join(combo[:-1]) + " or " + combo[-1]
        if r.random() < 0.5:
            out.append(mc(r, f"Which came out FIRST: {names}?", first, [m for m in combo if m != first]))
        else:
            out.append(mc(r, f"Which came out LAST: {names}?", last, [m for m in combo if m != last]))
    # --- sources
    for m, a, w in SRC:
        out.append(mc(r, f"What inspired the movie {m}?" if m != "Pocahontas" else "What inspired the movie Pocahontas?", a, P(w)))
    out += [
        mc(r, "Who published the shortened 1756 version of Beauty and the Beast?", "Jeanne-Marie Leprince de Beaumont", ["Hans Christian Andersen", "Charles Perrault", "The Brothers Grimm", "Aesop"]),
        mc(r, "Which author wrote 'The Snow Queen' (1844)?", "Hans Christian Andersen", ["The Brothers Grimm", "Charles Perrault", "Lewis Carroll", "Carlo Collodi"]),
        mc(r, "Which author wrote the 1697 'Cendrillon' tale?", "Charles Perrault", ["The Brothers Grimm", "Hans Christian Andersen", "Aesop", "Lewis Carroll"]),
        mc(r, "Which author wrote 'The Little Mermaid' (1837)?", "Hans Christian Andersen", ["The Brothers Grimm", "Charles Perrault", "Lewis Carroll", "Carlo Collodi"]),
        mc(r, "Which siblings collected 'Snow White' and 'Rapunzel'?", "The Brothers Grimm", ["The Brothers Andersen", "The Brothers Perrault", "The Marx Brothers", "The Brothers Aesop"]),
        mc(r, "Which Chinese heroine's ballad inspired Mulan?", "Hua Mulan", ["Mulan Li", "Lady Fu Hao", "Empress Wu", "Mulan Fa Zhou"]),
        mc(r, "The real Pocahontas married which Englishman in 1614?", "John Rolfe", ["John Smith", "Walter Raleigh", "Thomas Dale", "Henry Hudson"]),
        mc(r, "The real Pocahontas was the daughter of which leader?", "Chief Powhatan", ["Chief Seattle", "Chief Sitting Bull", "Chief Tecumseh", "Chief Joseph"]),
        mc(r, "The real Pocahontas died in which country?", "England", ["Virginia, USA", "France", "Spain", "Canada"]),
        mc(r, "Which Pixar film features Disney's first Pixar princess, Merida?", "Brave", ["Coco", "Up", "Inside Out", "Cars"]),
    ]
    # --- voices
    D = lambda c: c[0].upper() + c[1:]
    for c, m, a in VOICE:
        if "speaking" in c:
            out.append(mc(r, "Who was the speaking voice of Jasmine in Aladdin?", a, [x[2] for x in VOICE if x[2] != a]))
            continue
        out.append(mc(r, f"Who voiced {c} in {m}?", a, [x[2] for x in VOICE if x[2] != a]))
        out.append(mc(r, f"Which character did {a} voice in {m}?", D(c), [D(x[0]) for x in VOICE if x[0] != c and "speaking" not in x[0]]))
    # --- relationships / hard clues
    for q, a, ex in HARD:
        out.append(mc(r, q, a, names_wo(a, *ex)))
    for p, lv in LOVE.items():
        out.append(mc(r, f"Who is {p}'s love interest in her movie?", lv, [x for x in LOVE.values() if x != lv]))
    for vname, vm, p in VIL:
        out.append(mc(r, f"Who is the main villain in {vm}?", vname, [x[0] for x in VIL if x[0] != vname]))
    for q, a, w in PLOT + MUSIC + SETT:
        out.append(mc(r, q, a, P(w)))
    return out


def build(band):
    if band == "2-5": return kids()
    if band == "6-10": return mid()
    return late()
