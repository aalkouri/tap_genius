from ..common import *

META = {"id": "fruits_veg", "name": "Fruits & Veggies", "icon": "🍎"}

# (emoji, name) tables --------------------------------------------------------------------------
FRUIT = [("🍎", "apple"), ("🍌", "banana"), ("🍇", "grapes"), ("🍓", "strawberry"), ("🍊", "orange"), ("🍋", "lemon"), ("🍉", "watermelon"),
         ("🍍", "pineapple"), ("🥭", "mango"), ("🍑", "peach"), ("🍒", "cherries"), ("🥝", "kiwi"), ("🍐", "pear"), ("🫐", "blueberries"), ("🍈", "melon")]
VEG = [("🥕", "carrot"), ("🥦", "broccoli"), ("🥔", "potato"), ("🧅", "onion"), ("🧄", "garlic"), ("🥬", "lettuce"), ("🍠", "sweet potato")]
OTHER = [("🍅", "tomato"), ("🥒", "cucumber"), ("🍆", "eggplant"), ("🥑", "avocado"), ("🌽", "corn"), ("🫑", "bell pepper"), ("🌶️", "chili pepper"), ("🥥", "coconut"), ("🫒", "olive")]
ALL = FRUIT + VEG + OTHER
E2N = {e: n for e, n in ALL}
CAT_NAMES = [n for _, n in ALL]


MASS = {"spinach", "kale", "broccoli", "asparagus", "garlic", "celery", "corn", "ginger", "lettuce", "rhubarb"}


def art(n):
    if n in MASS: return n
    return ("an " if n[0] in "aeiou" else "a ") + n


def build(band):
    r = rng_for("fruits_veg", band)
    out = []
    if band == "2-5":
        TV = VEG[:6] + [("🌽", "corn")]
        for e, n in FRUIT:
            for t in ["What fruit is this?", "Name this fruit.", "What is this yummy fruit?"]:
                out.append(mc(r, t, n, [x for _, x in FRUIT], v=emoji(e)))
        for e, n in TV:
            for t in ["What veggie is this?", "Name this veggie.", "What is this yummy veggie?"]:
                out.append(mc(r, t, n, [x for _, x in TV + [("", "pea")]], v=emoji(e)))
        for e, n in ALL:
            for t in ["Tap the {n}!", "Show me the {n}!", "Find the {n}!"]:
                out.append(mc(r, t.format(n=n), e, [x for x, _ in ALL if x != e], ct="emoji"))
            out.append(mc(r, "What food is this?", n, CAT_NAMES, v=emoji(e)))
        TC = {"apple": "red", "strawberry": "red", "cherries": "red", "tomato": "red", "banana": "yellow", "lemon": "yellow", "corn": "yellow",
              "orange": "orange", "carrot": "orange", "grapes": "purple", "eggplant": "purple", "broccoli": "green", "cucumber": "green",
              "pear": "green", "lettuce": "green", "potato": "brown", "blueberries": "blue"}
        FC = {n: c for n, c in TC.items() if n in [x for _, x in FRUIT]}
        VC = {n: c for n, c in TC.items() if n in ["carrot", "broccoli", "potato", "corn", "lettuce"]}
        N2E = {n: e for e, n in ALL}
        for tbl, kind, tmpl in [(FC, "fruit", ["Which fruit is {c}?", "Find a {c} fruit!", "Tap the {c} fruit."]),
                                (VC, "veggie", ["Which veggie is {c}?", "Find a {c} veggie!", "Tap the {c} veggie."]),
                                (TC, "food", ["Which food is {c}?", "Find a {c} food!", "Tap the {c} food."])]:
            for c in sorted(set(tbl.values())):
                right = [n for n, x in tbl.items() if x == c]
                wrong = [N2E[n] for n, x in tbl.items() if x != c]
                if len(set(wrong)) < 3: continue
                for t in tmpl:
                    out.append(mc(r, t.format(c=c), N2E[r.choice(right)], wrong, ct="emoji"))
        for e, n in ALL:
            for k in range(1, 6):
                out.append(num_choices(r, "How many do you see?", k, v=emoji(e * k), spread=2, lo=1))
        for _ in range(45):
            fs = r.sample(FRUIT, 3)
            vv = r.choice(VEG)
            out.append(mc(r, "Which one does not belong?", vv[0], [f[0] for f in fs], v=emoji("".join(f[0] for f in fs)), ct="emoji"))
        for _ in range(20):
            vs = r.sample(VEG, 3)
            ff = r.choice(FRUIT)
            out.append(mc(r, "Which one does not belong?", ff[0], [v[0] for v in vs], v=emoji("".join(v[0] for v in vs)), ct="emoji"))
        for t in ["Which one is a fruit?", "Find the fruit!", "Tap the fruit.", "Which is a yummy fruit?", "Which one is a sweet fruit?"]:
            out.append(mc(r, t, r.choice(FRUIT)[0], [e for e, _ in VEG], ct="emoji"))
        for t in ["Which one is a veggie?", "Find the veggie!", "Tap the veggie.", "Which is a veggie?", "Which one is a healthy veggie?"]:
            out.append(mc(r, t, r.choice(VEG)[0], [e for e, _ in FRUIT], ct="emoji"))
        for t in ["What does a rabbit like?", "Which food do bunnies love?"]:
            out.append(mc(r, t, "🥕", ["🍕", "🍔", "🍟", "🍪"], ct="emoji", v=emoji("🐰")))
        for t in ["What does a monkey like?", "Which food do monkeys love?"]:
            out.append(mc(r, t, "🍌", ["🍕", "🍔", "🍟", "🍪"], ct="emoji", v=emoji("🐒")))
        for t in ["What does a horse like?", "Which food do horses love?"]:
            out.append(mc(r, t, "🍎", ["🍕", "🍔", "🍟", "🍪"], ct="emoji", v=emoji("🐴")))
    elif band == "6-10":
        FRU = ["apple", "banana", "grape", "strawberry", "orange", "lemon", "watermelon", "pineapple", "mango", "peach", "cherry", "kiwi", "pear",
               "blueberry", "plum", "raspberry", "apricot", "lime", "grapefruit", "blackberry"]
        VGN = ["carrot", "broccoli", "spinach", "lettuce", "potato", "onion", "cabbage", "garlic", "radish", "beet", "cauliflower", "asparagus", "kale",
               "turnip", "celery", "sweet potato", "parsnip", "leek"]
        for n in FRU:
            out.append(mc(r, f"Is {art(n)} a fruit or a vegetable?", "Fruit", ["Fruit", "Vegetable", "Grain", "Dairy"]))
            out.append(mc(r, f"{n.title()} is a kind of what?", "Fruit", ["Vegetable", "Grain", "Dairy", "Meat"]))
        for n in VGN:
            out.append(mc(r, f"Is {art(n)} a fruit or a vegetable?", "Vegetable", ["Fruit", "Vegetable", "Grain", "Dairy"]))
            out.append(mc(r, f"{n.title()} is a kind of what?", "Vegetable", ["Fruit", "Grain", "Dairy", "Meat"]))
        for e, n in FRUIT + VEG + OTHER:
            out.append(mc(r, "What food is this?", n, CAT_NAMES, v=emoji(e)))
        for _ in range(55):
            fs = r.sample(FRUIT, 3); vv = r.choice(VEG)
            out.append(mc(r, "Which one is NOT a fruit?", vv[1], [f[1] for f in fs], v=emoji("".join(f[0] for f in fs) + vv[0])))
        for _ in range(35):
            vs = r.sample(VEG, 3); ff = r.choice(FRUIT)
            out.append(mc(r, "Which one is NOT a vegetable?", ff[1], [v[1] for v in vs], v=emoji("".join(v[0] for v in vs) + ff[0])))
        PARTS = {"carrot": "Root", "beet": "Root", "radish": "Root", "turnip": "Root", "parsnip": "Root", "sweet potato": "Root", "lettuce": "Leaf",
                 "spinach": "Leaf", "cabbage": "Leaf", "kale": "Leaf", "broccoli": "Flower", "cauliflower": "Flower", "artichoke": "Flower",
                 "asparagus": "Stem", "pea": "Seed", "lentil": "Seed", "kidney bean": "Seed"}
        PP = ["Root", "Leaf", "Flower", "Stem", "Seed"]
        for n, p in PARTS.items():
            out.append(mc(r, f"Which plant part is {art(n)}?", p, PP))
            out.append(mc(r, f"When we eat {art(n)}, we eat the plant's...", p, PP))
        for e, n in [("🥕", "carrot"), ("🥦", "broccoli"), ("🥬", "lettuce"), ("🍠", "sweet potato")]:
            out.append(mc(r, "Which part of the plant do we eat here?", PARTS[n], PP, v=emoji(e)))
        for p, ts in [("Root", ["Which of these is a root vegetable?", "Which one do we eat as a plant root?"]), ("Leaf", ["Which of these is a leafy vegetable?", "Which of these is the leaf of a plant?"]),
                      ("Flower", ["Which of these is a flower we eat?", "Which of these vegetables is a flower bud?"])]:
            for t in ts:
                ans = r.choice([n for n, x in PARTS.items() if x == p])
                out.append(mc(r, t, ans, [n for n, x in PARTS.items() if x != p]))
        WH = {"apple": "On a tree", "orange": "On a tree", "lemon": "On a tree", "peach": "On a tree", "cherry": "On a tree", "pear": "On a tree", "mango": "On a tree",
              "plum": "On a tree", "apricot": "On a tree", "lime": "On a tree", "grapefruit": "On a tree", "coconut": "On a tree", "avocado": "On a tree",
              "carrot": "Underground", "potato": "Underground", "radish": "Underground", "beet": "Underground", "turnip": "Underground", "onion": "Underground",
              "garlic": "Underground", "sweet potato": "Underground", "parsnip": "Underground", "peanut": "Underground",
              "grape": "On a vine", "watermelon": "On a vine", "pumpkin": "On a vine", "kiwi": "On a vine", "cantaloupe": "On a vine",
              "blueberry": "On a bush", "raspberry": "On a bush", "blackberry": "On a bush"}
        WP = ["On a tree", "Underground", "On a vine", "On a bush"]
        for n, w in WH.items():
            out.append(mc(r, f"Where does {art(n)} grow?", w, WP))
            out.append(mc(r, f"Where would you find {art(n)} growing?", w, WP))
        COL = ["red", "yellow", "orange", "green", "purple", "blue", "brown", "white"]
        RIPE = {"banana": "yellow", "lemon": "yellow", "strawberry": "red", "cherry": "red", "blueberry": "blue", "carrot": "orange", "orange": "orange", "tomato": "red",
                "pumpkin": "orange", "eggplant": "purple", "raspberry": "red", "cauliflower": "white", "lime": "green", "spinach": "green",
                "broccoli": "green", "watermelon": "green"}
        for n, c in RIPE.items():
            if n == "watermelon": continue
            out.append(mc(r, f"What color is a ripe {n}?" if n not in ("carrot", "spinach", "broccoli", "cauliflower") else f"What color is {n}, usually?", c, COL))
            out.append(mc(r, f"The outside of {art(n)} is usually which color?", c, COL))
        PROD = [("raisins", "grapes", ["apples", "plums", "cherries"]), ("prunes", "plums", ["grapes", "apples", "pears"]), ("dill pickles", "cucumbers", ["carrots", "potatoes", "onions"]),
                ("ketchup", "tomatoes", ["apples", "carrots", "beets"]), ("guacamole", "avocados", ["bananas", "pears", "kiwis"]),
                ("popcorn", "corn", ["rice", "potatoes", "peas"]), ("french fries", "potatoes", ["carrots", "apples", "onions"]),
                ("applesauce", "apples", ["pears", "oranges", "plums"]), ("lemonade", "lemons", ["limes", "oranges", "grapes"]),
                ("sauerkraut", "cabbage", ["carrots", "potatoes", "turnips"]), ("orange juice", "oranges", ["lemons", "mangoes", "peaches"]),
                ("jam on toast, made with berries, often uses", "strawberries", ["potatoes", "onions", "carrots"]), ("peanut butter", "peanuts", ["almonds", "potatoes", "carrots"])]
        for p, a, w in PROD:
            out.append(mc(r, f"What is {p} made from?" if not p.startswith("jam") else "Strawberry jam is mostly made from what?", a, w + ["onions", "beans"]))
        NUT = [("Which vitamin do oranges and other citrus fruits have a lot of?", "Vitamin C", ["Vitamin D", "Vitamin B12", "Vitamin K"]),
               ("Which vitamin in carrots helps keep your eyes healthy?", "Vitamin A", ["Vitamin D", "Vitamin B12", "Vitamin C"]),
               ("Which mineral are bananas famous for?", "Potassium", ["Iron", "Zinc", "Salt"]),
               ("Fruits and vegetables give us plenty of this, which helps our tummies digest food.", "Fiber", ["Cholesterol", "Caffeine", "Lactose"]),
               ("Why do doctors say to eat many colors of fruits and vegetables?", "Different colors give different vitamins", ["Colors make you taller overnight", "Colors can replace sleep", "Colors are just for decoration"]),
               ("Which fruit has its seeds on the outside?", "Strawberry", ["Apple", "Banana", "Grape"]),
               ("Which fruit is more than 90% water?", "Watermelon", ["Banana", "Avocado", "Apple"]),
               ("What do we call a group of bananas growing together?", "A hand", ["A herd", "A flock", "A pack"]),
               ("Which vegetable can make your eyes water when you cut it?", "Onion", ["Carrot", "Potato", "Lettuce"]),
               ("Which vegetable did the cartoon sailor Popeye eat for strength?", "Spinach", ["Broccoli", "Carrot", "Corn"]),
               ("Which fruit has a crown of leaves on top?", "Pineapple", ["Apple", "Banana", "Orange"]),
               ("Which fruit has a hard shell with milky water inside?", "Coconut", ["Apple", "Banana", "Grape"]),
               ("Which one is a citrus fruit?", "Orange", ["Apple", "Banana", "Strawberry"]),
               ("Lemons, limes and ___ are all citrus fruits.", "Grapefruit", ["Pears", "Plums", "Bananas"]),
               ("A fruit grows from which part of a plant?", "The flower", ["The root", "The leaf", "The soil"]),
               ("What are the tiny things inside many fruits that can grow into new plants?", "Seeds", ["Roots", "Petals", "Stems"]),
               ("Which insect helps flowers turn into fruit by carrying pollen?", "Bee", ["Spider", "Snail", "Earthworm"]),
               ("Which fruit has one big hard pit (stone) inside?", "Peach", ["Apple", "Banana", "Watermelon"]),
               ("Which small red fruit has a hard pit inside?", "Cherry", ["Strawberry", "Raspberry", "Watermelon"]),
               ("What do people carve into Jack-o'-lanterns at Halloween?", "Pumpkin", ["Banana", "Grapes", "Pear"]),
               ("Which of these vegetables is orange?", "Carrot", ["Broccoli", "Cabbage", "Lettuce"]),
               ("A sweet potato is a kind of what part of a plant?", "Root", ["Leaf", "Flower", "Seed"]),
               ("Which is a berry that is blue?", "Blueberry", ["Strawberry", "Raspberry", "Blackberry"]),
               ("Cherries, plums and peaches all have a hard what in the middle?", "Pit (stone)", ["Shell", "Skin", "Leaf"]),
               ("Dried grapes are called what?", "Raisins", ["Prunes", "Dates", "Figs"]),
               ("Dried plums are called what?", "Prunes", ["Raisins", "Dates", "Figs"]),
               ("What gas do plants take in to make food?", "Carbon dioxide", ["Helium", "Laughing gas", "Smoke"]),
               ]
        for q, a, w in NUT:
            out.append(mc(r, q, a, w))
    else:  # 11+
        BOT = {"tomato": "Fruit", "cucumber": "Fruit", "pumpkin": "Fruit", "avocado": "Fruit", "eggplant": "Fruit", "zucchini": "Fruit", "olive": "Fruit",
               "bell pepper": "Fruit", "carrot": "Root", "beet": "Root", "radish": "Root", "parsnip": "Root", "sweet potato": "Root", "spinach": "Leaf",
               "lettuce": "Leaf", "kale": "Leaf", "cabbage": "Leaf", "broccoli": "Flower", "cauliflower": "Flower", "artichoke": "Flower",
               "asparagus": "Stem", "potato": "Stem (a tuber)", "ginger": "Stem (a rhizome)"}
        BP = ["Fruit", "Root", "Leaf", "Flower", "Stem"]
        for n, p in BOT.items():
            pool = ["Root", "Leaf", "Flower", "Stem"] if p == "Fruit" else [x for x in BP if x != p]
            if p.startswith("Stem"): pool = ["Fruit", "Root", "Leaf", "Flower"]
            if p == "Flower": pool = ["Fruit", "Root", "Leaf"]
            out.append(mc(r, f"Botanically speaking, what part of the plant is {art(n)}?", p, pool))
            out.append(mc(r, f"In botany, {n} is best classified as which plant part?", p, pool))
        TYPE = {"banana": "Berry", "grape": "Berry", "tomato": "Berry", "avocado": "Berry", "kiwi": "Berry", "eggplant": "Berry", "blueberry": "Berry",
                "peach": "Drupe", "cherry": "Drupe", "plum": "Drupe", "mango": "Drupe", "olive": "Drupe", "apricot": "Drupe", "apple": "Pome", "pear": "Pome",
                "raspberry": "Aggregate fruit", "blackberry": "Aggregate fruit", "strawberry": "Aggregate fruit", "pineapple": "Multiple fruit"}
        TP = ["Berry", "Drupe", "Pome", "Aggregate fruit", "Multiple fruit"]
        for n, t in TYPE.items():
            pool = [x for x in TP if x != "Drupe"] if t == "Aggregate fruit" else [x for x in TP if x != "Aggregate fruit"] if t == "Multiple fruit" else TP
            out.append(mc(r, f"Which type of fruit is {art(n)} in botanical terms?", t, pool))
            out.append(mc(r, f"What is the botanical fruit type of the {n}?", t, pool))
        FAM = {"tomato": "Nightshade", "potato": "Nightshade", "eggplant": "Nightshade", "bell pepper": "Nightshade", "broccoli": "Cabbage (mustard)",
               "cabbage": "Cabbage (mustard)", "cauliflower": "Cabbage (mustard)", "kale": "Cabbage (mustard)", "radish": "Cabbage (mustard)", "turnip": "Cabbage (mustard)",
               "cucumber": "Gourd", "pumpkin": "Gourd", "zucchini": "Gourd", "watermelon": "Gourd", "cantaloupe": "Gourd", "pea": "Pea (legume)",
               "lentil": "Pea (legume)", "peanut": "Pea (legume)", "chickpea": "Pea (legume)", "green bean": "Pea (legume)", "apple": "Rose", "pear": "Rose",
               "strawberry": "Rose", "cherry": "Rose", "peach": "Rose", "plum": "Rose", "raspberry": "Rose", "almond": "Rose", "lemon": "Citrus", "orange": "Citrus",
               "lime": "Citrus", "grapefruit": "Citrus", "onion": "Onion (allium)", "garlic": "Onion (allium)", "leek": "Onion (allium)", "carrot": "Carrot (parsley)",
               "celery": "Carrot (parsley)", "parsnip": "Carrot (parsley)", "lettuce": "Daisy"}
        FP = sorted(set(FAM.values()))
        for n, f in FAM.items():
            out.append(mc(r, f"To which plant family does {art(n)} belong?", f, FP))
            out.append(mc(r, f"{n.title()} is a member of which family?", f, FP))
        ORI = {"potato": "South America", "tomato": "South America", "pineapple": "South America", "corn": "North America", "avocado": "North America",
               "orange": "Asia", "mango": "Asia", "peach": "Asia", "apple": "Asia", "carrot": "Asia", "eggplant": "Asia", "cucumber": "Asia",
               "watermelon": "Africa", "macadamia nut": "Australia", "kiwifruit": "Asia"}
        CT = ["Asia", "Africa", "Europe", "North America", "South America", "Australia"]
        for n, c in ORI.items():
            out.append(mc(r, f"Which continent is the original home of {n}?", c, CT))
            out.append(mc(r, f"{n.title()} originally comes from which continent?", c, CT))
        LAT = {"potato": "Solanum tuberosum", "tomato": "Solanum lycopersicum", "carrot": "Daucus carota", "cucumber": "Cucumis sativus", "lemon": "Citrus limon",
               "pineapple": "Ananas comosus", "mango": "Mangifera indica", "avocado": "Persea americana", "peach": "Prunus persica", "onion": "Allium cepa",
               "garlic": "Allium sativum", "eggplant": "Solanum melongena", "corn": "Zea mays", "apple": "Malus domestica", "pea": "Pisum sativum", "strawberry": "Fragaria × ananassa"}
        for n, l in LAT.items():
            out.append(mc(r, f"What is the scientific name of the {n}?", l, [x for x in LAT.values()]))
            out.append(mc(r, f"Which food has the scientific name {l}?", n, [x for x in LAT]))
        F = [
            ("A lack of which vitamin causes scurvy?", "Vitamin C", ["Vitamin A", "Vitamin D", "Vitamin K"]),
            ("Sailors on long voyages often got scurvy because they lacked...", "Vitamin C", ["Protein", "Vitamin D", "Iron"]),
            ("Which vitamin do leafy greens like kale supply that is needed for blood clotting?", "Vitamin K", ["Vitamin C", "Vitamin D", "Vitamin B12"]),
            ("A shortage of vitamin A can cause what?", "Night blindness", ["Scurvy", "Rickets", "Anemia"]),
            ("Which pigment makes tomatoes red and is an antioxidant?", "Lycopene", ["Chlorophyll", "Anthocyanin", "Melanin"]),
            ("Which pigment gives carrots their orange color?", "Beta-carotene", ["Lycopene", "Chlorophyll", "Anthocyanin"]),
            ("Which pigments make blueberries and red cabbage blue or purple?", "Anthocyanins", ["Chlorophyll", "Carotenoids", "Lycopene"]),
            ("Which pigment makes leaves green?", "Chlorophyll", ["Lycopene", "Melanin", "Carotene"]),
            ("Which compound gives chili peppers their heat?", "Capsaicin", ["Allicin", "Pectin", "Lycopene"]),
            ("Which compound gives crushed garlic its sharp flavor and smell?", "Allicin", ["Capsaicin", "Pectin", "Lycopene"]),
            ("Which fiber found in apples is used to make jam set?", "Pectin", ["Allicin", "Capsaicin", "Glucose"]),
            ("Which acid gives lemons their sour taste?", "Citric acid", ["Acetic acid", "Hydrochloric acid", "Lactic acid"]),
            ("What plant hormone gas makes fruit ripen faster?", "Ethylene", ["Helium", "Neon", "Argon"]),
            ("Which part of the flower develops into the fruit?", "The ovary", ["The petal", "The stamen", "The sepal"]),
            ("Which part of the flower becomes the seeds?", "The ovules", ["The petals", "The anthers", "The sepals"]),
            ("What is the transfer of pollen to the female part of a flower called?", "Pollination", ["Germination", "Fermentation", "Respiration"]),
            ("Vegetables like broccoli and cabbage are called what, because their four petals form a cross?", "Cruciferous", ["Leguminous", "Solanaceous", "Cucurbit"]),
            ("Is a banana plant a tree?", "No, it is a giant herb", ["Yes, it is a palm tree", "Yes, it is an oak", "No, it is a vine"]),
            ("Which of these is NOT a cultivar of the species Brassica oleracea?", "Carrot", ["Broccoli", "Cabbage", "Kale"]),
            ("In 1893, a US Supreme Court case ruled tomatoes are vegetables for tariff purposes. What was it called?", "Nix v. Hedden", ["Brown v. Board", "Marbury v. Madison", "Plessy v. Ferguson"]),
            ("Botanically, is the tomato a fruit?", "Yes, it is a berry", ["No, it is a root", "No, it is a leaf", "No, it is a seed only"]),
            ("Which vegetable caused famine in Ireland in the 1840s when its crop failed from blight?", "Potato", ["Carrot", "Cabbage", "Turnip"]),
            ("Which part of rhubarb is poisonous?", "The leaves", ["The stalks", "Both are fine", "Neither"]),
            ("Green or sprouting potatoes contain which toxin?", "Solanine", ["Capsaicin", "Pectin", "Allicin"]),
            ("What does the Scoville scale measure?", "Heat (pungency) of chili peppers", ["Sweetness of fruit", "Ripeness of fruit", "Acidity of lemons"]),
            ("Which of these chili peppers is the hottest?", "Carolina Reaper", ["Jalapeno", "Habanero", "Cayenne"]),
            ("Which fruit is known as the \"king of fruits\" in Southeast Asia?", "Durian", ["Pineapple", "Banana", "Lychee"]),
            ("Which is the largest tree-borne fruit?", "Jackfruit", ["Coconut", "Breadfruit", "Mango"]),
            ("Which country is the world's largest producer of bananas?", "India", ["Ecuador", "Brazil", "Mexico"]),
            ("Which country is the world's largest producer of potatoes?", "China", ["Ireland", "Peru", "Canada"]),
            ("Which fruit floats in water because about 25% of it is air?", "Apple", ["Grape", "Potato", "Carrot"]),
            ("Which banana variety is the most widely exported?", "Cavendish", ["Granny Smith", "Fuji", "Hass"]),
            ("Which avocado variety is the most commonly grown worldwide?", "Hass", ["Cavendish", "Gala", "Valencia"]),
            ("Which of these is a variety of apple?", "Granny Smith", ["Cavendish", "Hass", "Valencia"]),
            ("Which of these is, like the banana, a true botanical berry?", "Tomato", ["Strawberry", "Raspberry", "Cherry"]),
            ("An almond is the seed of a fruit closely related to which fruit?", "Peach", ["Apple", "Banana", "Grape"]),
            ("Peanuts are botanically members of which plant family?", "Legumes", ["Nuts", "Grasses", "Nightshades"]),
            ("Corn on the cob: each kernel is botanically a...", "Fruit (grain)", ["Root", "Leaf", "Stem"]),
            ("Which gives beets their deep red color?", "Betalains", ["Lycopene", "Chlorophyll", "Capsaicin"]),
            ("Which mineral important for muscles and nerves is plentiful in bananas, potatoes and avocados?", "Potassium", ["Iodine", "Fluoride", "Silicon"]),
            ("Which B vitamin found in leafy greens is vital during pregnancy?", "Folate", ["Thiamine", "Biotin", "Niacin"]),
            ("Which of these fruits does NOT keep ripening much after being picked?", "Strawberry", ["Banana", "Avocado", "Pear"]),
            ("Which of these is a climacteric fruit that continues to ripen after picking?", "Banana", ["Strawberry", "Grape", "Cherry"]),
            ("Which type of fruit is a pineapple, formed from many fused flowers?", "Multiple fruit", ["Berry", "Drupe", "Pome"]),
            ("The juicy red part of a strawberry is actually which structure?", "An enlarged flower base (receptacle)", ["The seed coat", "A root", "A leaf stem"]),
            ("What do we call a vegetable such as a potato that is an underground stem?", "A tuber", ["A taproot", "A bulb", "A pod"]),
            ("Which onion-family vegetable grows as a bulb?", "Garlic", ["Carrot", "Beet", "Potato"]),
        ]
        for q, a, w in F:
            out.append(mc(r, q, a, w))
    return out
