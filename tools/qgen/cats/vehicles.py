from ..common import *
import itertools

META = {"id": "vehicles", "name": "Vehicles", "icon": "🚗"}


def P(s): return s.split("|")


def rows(r, rs):
    return [mc(r, q, a, P(w)) for q, a, w in rs]


# ---------------------------------------------------------------- 2-5
# (emoji, name, group, where)   group = names that must not appear together in one question
KV = [("🚗", "Car", "car", "road"), ("🚓", "Police car", "car", "road"), ("🏎️", "Race car", "car", "road"), ("🚌", "Bus", "", "road"),
      ("🚑", "Ambulance", "", "road"), ("🚒", "Fire truck", "truck", "road"), ("🚚", "Truck", "truck", "road"),
      ("🚜", "Tractor", "", "road"), ("🏍️", "Motorcycle", "bike", "road"), ("🚲", "Bike", "bike", "road"), ("🛴", "Kick scooter", "", "road"),
      ("🛹", "Skateboard", "", "road"), ("🚂", "Steam train", "", "rail"), ("✈️", "Airplane", "", "sky"), ("🚁", "Helicopter", "", "sky"),
      ("🚀", "Rocket", "", "space"), ("⛵", "Sailboat", "boat", "water"), ("🚤", "Speedboat", "boat", "water"),
      ("🚢", "Ship", "boat", "water"), ("🛶", "Canoe", "boat", "water")]
WHERE = {"road": "On the road", "sky": "In the sky", "water": "On the water", "rail": "On train tracks"}


def the(n): return n.lower()


def art(n): return "an" if n[0] in "AEIO" else "a"


def kids():
    r = rng_for("vehicles", "2-5")
    out = []
    for e, n, g, w in KV:
        names = [x[1] for x in KV if x[1] != n and not (g and x[2] == g)]
        emos = [x[0] for x in KV if x[1] != n and not (g and x[2] == g)]
        a = "an" if n[0] in "AEIOU" else "a"
        for q in ["What is this?", "Can you name this?", "What do you see?"]:
            out.append(mc(r, q, n, names, v=emoji(e)))
        for q in ["Find the {}!", "Tap the {}!", "Where is the {}?", "Which one is the {}?", "Show me the {}!"]:
            out.append(mc(r, q.format(the(n)), e, emos, ct="emoji"))
        if w != "space":
            out.append(mc(r, "Where does it go?", WHERE[w], [v for k, v in WHERE.items() if k != w], v=emoji(e)))
            out.append(mc(r, f"Where does {a} {the(n)} go?", WHERE[w], [v for k, v in WHERE.items() if k != w]))
    for e in ["🚗", "🚌", "🚲", "✈️", "🚀", "🚢", "🚂", "🚜", "🚁", "⛵", "🚓", "🚒"]:
        for n in range(1, 6):
            for q in ["How many do you see?", "Count them!"]:
                out.append(num_choices(r, q, n, v=emoji(" ".join([e] * n)), spread=2, lo=1))
    for w, k in [("a bike", 2), ("a car", 4), ("a tricycle", 3), ("a motorcycle", 2), ("a kick scooter", 2), ("a skateboard", 4)]:
        out.append(num_choices(r, f"How many wheels does {w} have?", k, spread=2, lo=1))
    E = lambda q, a, w: mc(r, q, a, P(w), ct="emoji")
    out += [
        E("Which one can fly?", "✈️", "🚗|🚲|🚢|🚂|🚜"), E("Which one flies in the sky?", "🚁", "🚗|🚲|🚢|🚂|🚜"),
        E("What goes up in the sky?", "✈️", "🚌|🚲|🚢|🚂|🚜"), E("Which one floats on water?", "🚢", "🚗|🚲|🚌|🚜|🚂"),
        E("What sails on the sea?", "⛵", "🚗|🚲|🚌|🚜|🚂"), E("Which one goes on the sea?", "🚤", "🚗|🚲|🚌|🚜|🚂"),
        E("Which one has two wheels?", "🚲", "🚗|🚌|🚜|🚚|🚂"), E("Which one goes on train tracks?", "🚂", "🚗|🚲|🚢|✈️|🚜"),
        E("What says choo choo?", "🚂", "🚗|🚲|✈️|🚢|🚜"), E("Which one puts out fires?", "🚒", "🚗|🚲|🚌|🚜|🚂"),
        E("Which one helps sick people?", "🚑", "🚲|🚜|🚂|🚢|🚤"), E("Which one goes to space?", "🚀", "🚗|🚲|🚌|🚜|🚂"),
        E("What do kids ride to school?", "🚌", "🚀|✈️|🚢|🚂|🚁"), E("Which one is super fast?", "🏎️", "🚲|🚜|🛴|🛹|⛵"),
        E("Which one pedals?", "🚲", "🚗|🚌|🚜|🚂|🚢"),
        E("Which one has wings?", "✈️", "🚗|🚲|🚌|🚜|🚂"), E("Which one has a sail?", "⛵", "🚗|🚲|🚌|🚜|🚂"),
        E("Which one works on a farm?", "🚜", "🚀|✈️|🚢|🚂|🚁"),
        mc(r, "Red means...", "Stop", ["Go", "Fly", "Swim", "Jump"]),
        mc(r, "Green means...", "Go", ["Stop", "Sleep", "Swim", "Hide"]),
        mc(r, "What do we wear on a bike?", "A helmet", ["Swim goggles", "Flippers", "A crown", "A backpack of rocks"]),
        mc(r, "What do we buckle in a car?", "Seat belt", ["Shoe", "Toy", "Hat", "Spoon"]),
        mc(r, "What color is a fire truck?", "Red", ["Pink", "Purple", "Brown", "Green"]),
        mc(r, "What color is a school bus?", "Yellow", ["Pink", "Purple", "Brown", "Black"]),
        mc(r, "What goes round on a car?", "Wheels", ["Wings", "Sails", "Legs", "Fins"]),
        mc(r, "What does a plane have?", "Wings", ["Sails", "Legs", "Fins", "Horns"]),
        mc(r, "What does a boat float on?", "Water", ["Grass", "Sand", "Snow", "Clouds"]),
        mc(r, "A bike needs...", "Pedaling", ["Sails", "Wings", "Fuel from a pump", "Rails"]),
    ]
    return out


# ---------------------------------------------------------------- 6-10
LAND = ["Car", "Bus", "Truck", "Bicycle", "Motorcycle", "Tractor", "Train", "Tram", "Skateboard", "Bulldozer", "Fire engine", "Ambulance",
        "Taxi", "Garbage truck", "Dump truck", "Snowplow", "School bus", "Unicycle"]
AIR = ["Airplane", "Helicopter", "Hot air balloon", "Glider", "Jumbo jet", "Blimp", "Hang glider", "Jet fighter"]
WATER = ["Sailboat", "Canoe", "Ferry", "Speedboat", "Rowboat", "Cruise ship", "Kayak", "Tugboat", "Lifeboat", "Cargo ship", "Fishing boat", "Submarine"]
SPACE = ["Rocket", "Space shuttle", "Space capsule"]

# (vehicle, what it does, emoji or "", group)
JOBS = [
    ("Fire engine", "Puts out fires", "🚒", ""), ("Ambulance", "Takes sick or hurt people to hospital", "🚑", ""),
    ("Garbage truck", "Collects trash", "", "road"), ("Bulldozer", "Pushes dirt with a big blade", "", "earth"),
    ("Excavator", "Digs holes with a bucket on an arm", "", "earth"), ("Crane", "Lifts heavy things high up", "", "lift"),
    ("Cement mixer", "Mixes and carries concrete", "", ""), ("Tow truck", "Pulls away broken-down cars", "", ""),
    ("School bus", "Takes children to school", "🚌", ""), ("Dump truck", "Tips out sand and gravel", "", "earth"),
    ("Tractor", "Pulls machines on a farm", "🚜", "farm"), ("Forklift", "Lifts boxes on pallets", "", "lift"),
    ("Snowplow", "Clears snow from roads", "", "road"), ("Tugboat", "Pulls and pushes big ships", "", ""),
    ("Lifeboat", "Rescues people at sea", "", ""), ("Icebreaker", "Breaks a path through sea ice", "", ""),
    ("Combine harvester", "Harvests crops like wheat", "", "farm"), ("Ferry", "Carries people and cars across water", "⛴️", "ship"),
    ("Submarine", "Travels underwater", "", ""), ("Police car", "Helps officers patrol and respond fast", "🚓", ""),
    ("Cargo ship", "Carries goods across the sea", "", "ship"), 
    ("Street sweeper", "Cleans dirt off the road", "", "road"),
]

PARTS = [
    ("Which part steers a ship or boat?", "Rudder", "Anchor|Mast|Hull|Propeller"), ("Which part of a bicycle do you hold to steer?", "Handlebars", "Pedals|Chain|Saddle|Spokes"),
    ("What do brakes do?", "Slow down or stop the vehicle", "Make it louder|Steer it|Make it float|Light the road"),
    ("Where does a pilot sit in a plane?", "The cockpit", "The hull|The trunk|The deck|The hold"),
    ("What do wings help a plane do?", "Lift up into the air", "Float on water|Dig into the ground|Roll on rails|Stay cool"),
    ("What holds a ship in place when it stops?", "An anchor", "A rudder|A sail|A propeller|A mast"),
    ("What are the spinning blades on top of a helicopter called?", "Rotors", "Wings|Sails|Fins|Pedals"),
    ("What part of a car lights the road at night?", "Headlights", "Horn|Mirrors|Brakes|Wipers"),
    ("What part of a car makes a warning sound?", "The horn", "The wipers|The seat belt|The mirror|The trunk"),
    ("What clears rain from a car's windshield?", "Wipers", "Mirrors|Brakes|Horn|Bumpers"),
    ("What does a seat belt do?", "Keeps you safe in a crash", "Makes the car faster|Cools the engine|Steers the car|Plays music"),
    ("What catches the wind on a sailboat?", "The sail", "The anchor|The rudder|The hull|The deck"),
    ("What is the main body of a boat called?", "The hull", "The sail|The anchor|The propeller|The mast"),
    ("What spins to push a ship through the water?", "A propeller", "An anchor|A sail only|A wheel|A wing"),
    ("What do the pedals on a bicycle turn?", "The chain", "The sail|The wing|The rotor|The horn"),
    ("What do we call the place where a ship's captain steers?", "The bridge", "The cellar|The attic|The garage|The porch"),
    ("What do a train's wheels run on?", "Rails", "Roads|Wires|Ice|Sand"),
    ("What is the soft, air-filled part around a car wheel?", "The tire", "The bumper|The grille|The engine|The mirror"),
    ("What helps a plane land safely on the ground?", "Landing gear", "Rotors|Sails|Anchors|Pedals"),
    ("Which part of a plane helps it turn and stay balanced?", "The tail", "The wheels|The windows|The cockpit door|The seats"),
    ("What makes a car's engine work?", "Fuel", "Water only|Sand|Snow|Paint"),
    ("What do we call the front of a ship?", "The bow", "The stern|The keel|The deck|The hull"),
    ("What do we call the back of a ship?", "The stern", "The bow|The mast|The bridge|The anchor"),
    ("What do we call the left side of a ship?", "Port", "Starboard|Bow|Stern|Keel"),
    ("What do we call the right side of a ship?", "Starboard", "Port|Bow|Stern|Keel"),
    ("What is the long pole that holds up the sails?", "The mast", "The hull|The rudder|The anchor|The keel"),
]

POWER = [
    ("What powers an electric car?", "A battery", "Wind|Coal|Steam from a boiler|Pedaling"),
    ("What did old steam trains burn to make steam?", "Coal or wood", "Batteries|Sunlight|Hydrogen|Wind"),
    ("What makes a sailboat move?", "The wind", "A battery|Steam|Gasoline|Pedals"),
    ("What do you use to move a bicycle?", "Pedaling with your legs", "A battery|Steam|Gasoline|Wind"),
    ("What moves a rowboat?", "Oars", "A sail|A battery|A jet engine|Steam"),
    ("What do gasoline cars burn?", "Gasoline", "Coal|Wood|Sunshine|Water"),
    ("What makes a hot air balloon rise?", "Hot air", "A big engine|Magnets|Steam|Wings"),
    ("What does a rocket burn to blast off?", "Fuel", "Wood|Water|Air only|Sunlight"),
    ("What do many city trams use for power?", "Electricity from overhead wires", "Coal|Gasoline|Sails|Wind"),
    ("What gives a plane's wings 'lift'?", "Air flowing over the wings", "A big magnet|The wheels|The tail|The seats"),
    ("What powers a solar-powered car?", "Sunlight", "Coal|Steam|Wind|Pedals"),
    ("What does a diesel truck burn?", "Diesel fuel", "Coal|Batteries|Sunlight|Hydrogen only"),
    ("What does a glider use to stay up?", "Rising air", "A jet engine|A big motor|Steam|Batteries"),
    ("What do hybrid cars use?", "An engine and an electric motor", "Only sails|Only pedals|Only steam|Only wind"),
    ("What do we call the part that makes a car go?", "The engine", "The horn|The mirror|The seat|The wiper"),
    ("What do electric trains get power from?", "Overhead wires or a third rail", "Coal fires|Wind sails|Pedals|Gasoline tanks"),
    ("Which of these uses no fuel at all?", "A bicycle", "A bus|A tractor|A jet|A cruise ship"),
]

FAMOUS = [
    ("Which famous ship sank after hitting an iceberg in 1912?", "Titanic", "Mayflower|Santa Maria|Cutty Sark|Queen Mary"),
    ("Which brothers built and flew the first powered airplane in 1903?", "The Wright brothers", "The Mario brothers|The Marx brothers|The Montgolfier brothers|The Grimm brothers"),
    ("Which ship carried the Pilgrims to America in 1620?", "The Mayflower", "The Titanic|The Santa Maria|The Beagle|The Victory"),
    ("What are the fast trains of Japan called?", "Shinkansen (bullet trains)", "Eurostar|Orient Express|Flying Scotsman|Maglev express"),
    ("Which fictional train takes students to Hogwarts?", "The Hogwarts Express", "The Polar Express|Thomas the Tank Engine|The Orient Express|The Rocket"),
    ("What is a hot air balloon's basket called?", "The gondola", "The hull|The cockpit|The bridge|The trunk"),
    ("Which famous passenger jet is called the 'Jumbo Jet'?", "Boeing 747", "Concorde|Airbus A380|Boeing 737|Cessna"),
    ("Which famous passenger plane could fly faster than sound?", "Concorde", "Boeing 747|Airbus A380|Boeing 737|Cessna"),
    ("What color are the famous London buses?", "Red", "Yellow|Blue|Green|Purple"),
    ("What color are the famous New York taxis?", "Yellow", "Red|Blue|Green|Purple"),
    ("What color are school buses in the USA?", "Yellow", "Red|Blue|Green|Purple"),
    ("What do we call a bus with two floors?", "A double-decker", "A jumbo|A tandem|A convertible|A hatchback"),
    ("What is the president of the USA's plane called?", "Air Force One", "Marine One|Space One|Sky King|Eagle One"),
    ("Which famous ship did Christopher Columbus sail in 1492?", "Santa Maria", "Titanic|Mayflower|Cutty Sark|Victory"),
    ("In the Beatles song, what color is the submarine?", "Yellow", "Red|Blue|Green|Purple"),
    ("Which Chinese city has a famous fast maglev train to its airport?", "Shanghai", "Beijing|Hong Kong|Tokyo|Seoul"),
    ("What is the name of the famous train from Paris to Istanbul?", "Orient Express", "Polar Express|Flying Scotsman|Eurostar|Bullet Train"),
    ("What is the Eurostar train famous for?", "Going through the Channel Tunnel", "Climbing mountains|Flying|Swimming|Driving on sand"),
    ("What do we call a tall ship with big white sails?", "A clipper or sailing ship", "A submarine|A tugboat|A ferry|A speedboat"),
    ("Which vehicle did Neil Armstrong travel to the Moon in?", "Apollo 11 spacecraft", "Space Shuttle|Soyuz|A Mars rover|The Hubble"),
]

BRANDS = [("Toyota", "Japan"), ("Honda", "Japan"), ("Nissan", "Japan"), ("Mazda", "Japan"), ("Subaru", "Japan"), ("Ford", "USA"), ("Chevrolet", "USA"),
          ("Tesla", "USA"), ("Volkswagen", "Germany"), ("BMW", "Germany"), ("Mercedes-Benz", "Germany"), ("Audi", "Germany"), ("Porsche", "Germany"),
          ("Ferrari", "Italy"), ("Lamborghini", "Italy"), ("Fiat", "Italy"), ("Volvo", "Sweden"), ("Renault", "France"), ("Peugeot", "France"),
          ("Citroen", "France"), ("Kia", "South Korea"), ("Hyundai", "South Korea"), ("Rolls-Royce", "United Kingdom"), ("Land Rover", "United Kingdom"),
          ("Skoda", "Czech Republic"), ("Tata", "India")]
LOGOS = [("Which car brand's logo is a prancing horse?", "Ferrari", "Ford|Toyota|Volvo|Audi"),
         ("Which car brand's logo is a charging bull?", "Lamborghini", "Ferrari|Ford|Audi|Honda"),
         ("Which car brand's logo is a three-pointed star in a circle?", "Mercedes-Benz", "Audi|Toyota|Ford|Volvo"),
         ("Which car brand's logo is four linked rings?", "Audi", "Mercedes-Benz|Toyota|Ford|Honda"),
         ("Which car brand's logo is a blue oval?", "Ford", "Audi|Mercedes-Benz|Ferrari|Volvo"),
         ("Which car brand's logo is a lion standing on its legs?", "Peugeot", "Ferrari|Ford|Audi|Honda"),
         ("Which car brand's logo is a gold bowtie?", "Chevrolet", "Ford|Audi|Mercedes-Benz|Honda"),
         ("Which car company makes the Model S, Model 3 and Model Y?", "Tesla", "Ford|Toyota|Honda|Volvo"),
         ("Which company makes the Mustang?", "Ford", "Toyota|Tesla|Honda|Audi"),
         ("Which company makes the Beetle and the Golf?", "Volkswagen", "Ford|Toyota|Honda|Tesla"),
         ("Which company makes the Boeing 747?", "Boeing", "Airbus|Tesla|Ford|Cessna"),
         ("Which company makes the Airbus A380?", "Airbus", "Boeing|Ford|Tesla|Cessna")]

SIGNS = [
    ("What shape is a stop sign?", "Octagon", "Circle|Square|Triangle|Hexagon"),
    ("What does a yellow traffic light mean?", "Get ready to stop", "Go faster|Park here|Turn around|Honk your horn"),
    ("What does a green traffic light mean?", "Go", "Stop|Turn off the engine|Fly|Park"),
    ("What does a red traffic light mean?", "Stop", "Go faster|Turn left only|Honk|Slow down a little"),
    ("What is a zebra crossing for?", "People crossing the road", "Parking cars|Fast driving|Racing|Animals only"),
    ("Which side of the road do cars drive on in the USA?", "Right", "Left|Middle|Either|Alternating"),
    ("Which side of the road do cars drive on in the UK?", "Left", "Right|Middle|Either|Alternating"),
    ("What do you wear on a bicycle to protect your head?", "A helmet", "A scarf|A crown|A mask|Sunglasses"),
    ("What do you wear in a car to stay safe?", "A seat belt", "Swimming goggles|A life jacket|Gloves|A scarf"),
    ("What do you wear on a boat to stay safe?", "A life jacket", "A seat belt|A helmet|Gloves|A scarf"),
    ("What does a railway signal tell a train driver?", "When to stop or go", "Which radio station to play|What the weather is|How many seats are free|When it is lunch"),
    ("What do we call a road that cars can drive on very fast, with several lanes?", "A highway", "A footpath|A tunnel|A cycle path|A canal"),
    ("What do we call the place where planes take off and land?", "An airport", "A harbor|A station|A garage|A depot"),
    ("What do we call the place where ships stop?", "A port or harbor", "An airport|A station|A garage|A depot"),
    ("What do we call the place where trains stop?", "A station", "A harbor|An airport|A garage|A hangar"),
    ("Where do airplanes park?", "In a hangar or at a gate", "In a harbor|On a railway track|In a parking lot only|In a stable"),
]

WHEELS = [("a bicycle", 2), ("a tricycle", 3), ("a car", 4), ("a motorcycle", 2), ("a unicycle", 1), ("a skateboard", 4), ("a kick scooter", 2),
          ("a tractor", 4), ("a large semi-truck (18-wheeler)", 18)]
RANKS = [("🚶", "Walking", 5), ("🚲", "Bicycle", 20), ("🚗", "Car", 100), ("🚄", "Bullet train", 300), ("✈️", "Jet plane", 900), ("🚀", "Rocket", 28000)]


def mid():
    r = rng_for("vehicles", "6-10")
    out = []
    med = [("Land", LAND), ("Air", AIR), ("Water", WATER), ("Space", SPACE)]
    for m, lst in med:
        for n in lst:
            out.append(mc(r, f"Where does {art(n)} {n.lower()} travel?", m if n != "Submarine" else "Water", [x for x, _ in med if x != m]))
    for e, n, g, w in KV:
        if w == "space": continue
        names = [x[1] for x in KV if x[1] != n and not (g and x[2] == g)]
        out.append(mc(r, "Which vehicle is this?", n, names, v=emoji(e)))
        out.append(mc(r, f"Which picture shows {art(n)} {n.lower()}?", e, [x[0] for x in KV if x[1] != n and not (g and x[2] == g)], ct="emoji"))
    for n, d, e, g in JOBS:
        other = [x for x in JOBS if x[0] != n and not (g and x[3] == g)]
        out.append(mc(r, f"What does {art(n)} {n.lower()} do?", d, [x[1] for x in other]))
        out.append(mc(r, f"Which vehicle {d[0].lower() + d[1:]}?", n, [x[0] for x in other]))
        if e:
            out.append(mc(r, "What does this vehicle do?", d, [x[1] for x in other], v=emoji(e)))
    out += rows(r, PARTS)
    out += rows(r, POWER)
    out += rows(r, FAMOUS)
    out += rows(r, SIGNS)
    out += rows(r, LOGOS)
    for b, c in BRANDS:
        if c in ("Czech Republic", "India", "Sweden", "South Korea", "United Kingdom"):
            pool = ["Japan", "USA", "Germany", "Italy", "France", "China", "Brazil", "Spain", "Australia"]
        else:
            pool = ["Japan", "USA", "Germany", "Italy", "France", "China", "Brazil", "Spain", "Australia", "Sweden", "India"]
        out.append(mc(r, f"In which country is the car brand {b} from?", c, pool))
    for n, k in WHEELS:
        out.append(num_choices(r, f"How many wheels does {n} usually have?", k, spread=3 if k < 10 else 8, lo=1 if k < 10 else 6))
    # speed ranking: four vehicles are shown, pick fastest / slowest
    for combo in itertools.combinations(RANKS, 4):
        show = emoji(" ".join(c[0] for c in combo))
        fast = max(combo, key=lambda c: c[2]); slow = min(combo, key=lambda c: c[2])
        out.append(mc(r, "Which of these is the fastest?", fast[1], [c[1] for c in combo], v=show))
        out.append(mc(r, "Which of these is the slowest?", slow[1], [c[1] for c in combo], v=show))
    return out


# ---------------------------------------------------------------- 11+
FACT = [
    ("Who is credited with building the first practical gasoline-powered automobile (1885)?", "Karl Benz", "Henry Ford|Rudolf Diesel|Gottlieb Daimler|Ferdinand Porsche"),
    ("Which car, launched in 1908, made car ownership affordable for ordinary Americans?", "Ford Model T", "Chevrolet Corvette|Volkswagen Beetle|Cadillac Eldorado|Jeep Willys"),
    ("What manufacturing method did Henry Ford introduce at scale in 1913?", "The moving assembly line", "Robotic welding|Just-in-time delivery|3D printing|Interchangeable parts"),
    ("Who designed the original Volkswagen Beetle?", "Ferdinand Porsche", "Henry Ford|Enzo Ferrari|Karl Benz|Alec Issigonis"),
    ("Who designed the original Mini, launched in 1959?", "Alec Issigonis", "Ferdinand Porsche|Colin Chapman|Enzo Ferrari|Ettore Bugatti"),
    ("Which engineer invented the compression-ignition engine that bears his name?", "Rudolf Diesel", "Nikolaus Otto|Karl Benz|James Watt|Felix Wankel"),
    ("Who built the first practical four-stroke engine in 1876?", "Nikolaus Otto", "Rudolf Diesel|Karl Benz|James Watt|Felix Wankel"),
    ("Which engineer developed the rotary engine used in Mazda sports cars?", "Felix Wankel", "Rudolf Diesel|Nikolaus Otto|Karl Benz|James Watt"),
    ("Who introduced the 'horsepower' as a unit of power?", "James Watt", "Isaac Newton|Rudolf Diesel|Henry Ford|Nikola Tesla"),
    ("What are the four strokes of a gasoline engine in order?", "Intake, compression, power, exhaust", "Power, intake, exhaust, compression|Compression, intake, exhaust, power|Intake, power, compression, exhaust|Exhaust, power, intake, compression"),
    ("What ignites the fuel in a diesel engine?", "Heat from compressed air", "A spark plug|A glow of the battery|A pilot flame|A magnet"),
    ("What ignites the fuel-air mixture in a gasoline engine?", "A spark plug", "Compressed air heat|A catalytic converter|A radiator|An alternator"),
    ("What converts a piston's up-and-down motion into rotation?", "The crankshaft", "The camshaft|The radiator|The alternator|The differential"),
    ("What does a car's alternator do?", "Generates electricity to charge the battery", "Cools the engine|Changes gears|Filters exhaust|Pumps fuel"),
    ("What does a radiator do in a car?", "Cools the engine", "Charges the battery|Changes gears|Filters air|Pumps fuel"),
    ("What does a catalytic converter do?", "Reduces harmful exhaust gases", "Boosts power|Cools the engine|Charges the battery|Steers the car"),
    ("What does a turbocharger use to boost an engine?", "Exhaust gases spinning a turbine", "Battery power|Sunlight|Extra fuel only|Magnets"),
    ("What does a differential allow?", "Drive wheels to turn at different speeds in corners", "The engine to start|Brakes to cool|Fuel to mix|The car to float"),
    ("What does ABS stand for in cars?", "Anti-lock braking system", "Automatic balance system|All-wheel brake setup|Advanced battery source|Air bag sensor"),
    ("What does regenerative braking do in an electric vehicle?", "Recovers energy into the battery", "Cools the tires|Spins the wheels faster|Makes the brakes louder|Burns extra fuel"),
    ("What does RPM measure on a car's tachometer?", "Engine revolutions per minute", "Road pressure|Rear power meter|Radiator pressure|Rolling pace"),
    ("What is a V8 engine?", "An engine with eight cylinders", "An engine with eight valves only|A hybrid engine|An engine with eight wheels|A jet engine"),
    ("What does a hybrid car combine?", "A combustion engine and an electric motor", "Two gasoline engines|A sail and an engine|A battery and a sail|Steam and diesel"),
    ("Which car was the first mass-produced hybrid, launched in Japan in 1997?", "Toyota Prius", "Honda Civic|Nissan Leaf|Tesla Roadster|Ford Fiesta"),
    ("Which car, launched in 2010, became a mass-market electric hatchback from Nissan?", "Nissan Leaf", "Toyota Prius|Tesla Model S|Chevrolet Corvette|Honda Accord"),
    ("What unit is battery capacity usually measured in?", "Kilowatt-hours", "Kilograms|Newtons|Litres|Kilopascals"),
    ("What does a hydrogen fuel-cell car emit from its tailpipe?", "Water vapour", "Carbon monoxide|Soot|Methane|Smoke"),
    ("How many levels of driving automation (0 to 5) are in the SAE scale?", "6", "4|5|8|3"),
    ("Which was the first production car to exceed 400 km/h, in 2005?", "Bugatti Veyron", "Ferrari Enzo|McLaren F1|Porsche 911|Lamborghini Countach"),
    ("What was the first supersonic land vehicle, which set a record in 1997?", "ThrustSSC", "Bloodhound|Spirit of America|Blue Flame|Bluebird"),
    ("In what year did the first Formula One World Championship season take place?", "1950", "1930|1946|1962|1975"),
    ("Which famous 24-hour endurance race is held in France?", "24 Hours of Le Mans", "Indianapolis 500|Monaco Grand Prix|Daytona 500|Dakar Rally"),
    ("In motor racing, what does 'pole position' mean?", "Starting at the front of the grid", "Finishing last|The fastest pit stop|Winning the championship|The slowest lap"),
    ("Who made the first powered, controlled airplane flight in 1903?", "Orville and Wilbur Wright", "Louis Bleriot|Charles Lindbergh|Alberto Santos-Dumont|Amelia Earhart"),
    ("Where did the Wright brothers make their first flight?", "Kitty Hawk, North Carolina", "Dayton, Ohio|Paris, France|San Diego, California|Cape Canaveral, Florida"),
    ("Who made the first flight across the English Channel in 1909?", "Louis Bleriot", "Charles Lindbergh|Orville Wright|Amelia Earhart|Alberto Santos-Dumont"),
    ("Who made the first solo nonstop flight across the Atlantic in 1927?", "Charles Lindbergh", "Amelia Earhart|Louis Bleriot|Howard Hughes|Chuck Yeager"),
    ("What was the name of Lindbergh's plane?", "Spirit of St. Louis", "Winnie Mae|Flyer|Enola Gay|Memphis Belle"),
    ("Who was the first woman to fly solo across the Atlantic (1932)?", "Amelia Earhart", "Bessie Coleman|Jacqueline Cochran|Harriet Quimby|Amy Johnson"),
    ("Who first broke the sound barrier in level flight in 1947?", "Chuck Yeager", "Neil Armstrong|Charles Lindbergh|Howard Hughes|John Glenn"),
    ("In which aircraft did Chuck Yeager break the sound barrier?", "Bell X-1", "SR-71|Concorde|X-15|Spitfire"),
    ("Which two engineers independently developed the jet engine in the 1930s?", "Frank Whittle and Hans von Ohain", "Wilbur Wright and Orville Wright|Igor Sikorsky and Henri Giffard|Louis Bleriot and Glenn Curtiss|Anthony Fokker and Claude Dornier"),
    ("Who built the first practical single-rotor helicopter in the US (1939-40)?", "Igor Sikorsky", "Frank Whittle|Henri Giffard|Louis Bleriot|Anthony Fokker"),
    ("What is Mach 1?", "The speed of sound", "The speed of light|Twice the speed of sound|Half the speed of sound|The speed of a bullet"),
    ("About how fast is the speed of sound at sea level?", "About 1,200 km/h", "About 300 km/h|About 12,000 km/h|About 120 km/h|About 300,000 km/h"),
    ("What are the four forces acting on an airplane?", "Lift, weight, thrust and drag", "Lift, mass, push and spin|Speed, gravity, wind and flap|Thrust, pitch, yaw and roll|Weight, torque, lift and fuel"),
    ("What control surfaces on the wings make an aircraft roll?", "Ailerons", "Rudder|Elevator|Flaps only|Trim tabs only"),
    ("Which control surface makes an aircraft pitch up or down?", "Elevator", "Aileron|Rudder|Spoiler|Flap"),
    ("Which control surface makes an aircraft yaw left or right?", "Rudder", "Aileron|Elevator|Flap|Spoiler"),
    ("What do flaps do during takeoff and landing?", "Increase lift at low speeds", "Reduce engine noise|Steer the plane on the ground|Release fuel|Cool the engine"),
    ("What is a stall in aviation?", "Loss of lift when the wing's angle of attack is too high", "Engine failure|A runway delay|Running out of fuel|Landing gear failure"),
    ("What instrument is used to measure an aircraft's airspeed?", "Pitot tube", "Barometer|Gyroscope|Radar|Altimeter"),
    ("What are the main parts of a jet engine in order of airflow?", "Compressor, combustor, turbine", "Combustor, compressor, turbine|Turbine, compressor, combustor|Compressor, turbine, combustor|Turbine, combustor, compressor"),
    ("What engine type powers most modern airliners?", "Turbofan", "Piston|Ramjet|Rocket|Turboprop"),
    ("What does a turboprop engine do?", "Uses a gas turbine to spin a propeller", "Burns steam in a piston|Uses only electricity|Pushes air with a fan only|Runs on solid fuel"),
    ("What color are aircraft 'black boxes' actually?", "Bright orange", "Black|Gray|Blue|White"),
    ("What does a flight recorder (black box) record?", "Flight data and cockpit voices", "Passenger tickets|Weather forecasts|Fuel prices|Seat bookings"),
    ("What is the usual cruising altitude of a jet airliner?", "About 10,000 m (35,000 ft)", "About 1,000 m|About 500 m|About 100,000 m|About 100 m"),
    ("Which airliner first flew in 1969 and was known as the 'Queen of the Skies'?", "Boeing 747", "Airbus A380|Concorde|Boeing 737|Lockheed Tristar"),
    ("What is notable about the Airbus A380?", "Largest passenger airliner with two full decks", "Fastest airliner|First jet airliner|Only seaplane airliner|Smallest airliner"),
    ("At what speed did Concorde cruise?", "About Mach 2", "About Mach 0.5|About Mach 5|About Mach 1 exactly|About Mach 10"),
    ("When did Concorde retire from service?", "2003", "1989|1999|2010|2020"),
    ("Which spy plane flew at over Mach 3 and is the fastest air-breathing crewed aircraft?", "SR-71 Blackbird", "Concorde|F-16|MiG-25|U-2"),
    ("Which rocket plane reached about Mach 6.7?", "X-15", "Bell X-1|SR-71|Concorde|Space Shuttle"),
    ("Which airline is the oldest still operating under its original name (founded 1919)?", "KLM", "Pan Am|Lufthansa|Qantas|British Airways"),
    ("What does the radio call 'Mayday' signal?", "A life-threatening emergency", "A weather warning|A landing request|A fuel stop|A routine check"),
    ("Who made the first crewed hot-air balloon flight in 1783?", "The Montgolfier brothers", "The Wright brothers|The Lumiere brothers|The Grimm brothers|The Marx brothers"),
    ("Which German airship burned at Lakehurst, New Jersey, in 1937?", "Hindenburg", "Graf Zeppelin|Titanic|Akron|Macon"),
    ("What gas was used in the Hindenburg that made it so dangerous?", "Hydrogen", "Helium|Methane|Oxygen|Propane"),
    ("Which gas do modern blimps use instead because it does not burn?", "Helium", "Hydrogen|Methane|Oxygen|Propane"),
    ("What gauge is 'standard gauge' for railways?", "1,435 mm", "1,000 mm|1,676 mm|1,067 mm|2,000 mm"),
    ("Which engineer built the locomotive 'Rocket' in 1829?", "George and Robert Stephenson", "Isambard Brunel|Richard Trevithick|James Watt|Thomas Newcomen"),
    ("Who built the first steam railway locomotive to run on rails in 1804?", "Richard Trevithick", "George Stephenson|James Watt|Isambard Brunel|Thomas Newcomen"),
    ("Which railway, opened in 1825, was the first public railway to use steam locomotives?", "Stockton and Darlington Railway", "Liverpool and Manchester Railway|Orient Express|Trans-Siberian Railway|Union Pacific"),
    ("Which was the first steam locomotive to officially reach 100 mph (1934)?", "Flying Scotsman", "Mallard|Rocket|Evening Star|Duchess of Hamilton"),
    ("Which steam locomotive set the speed record of 126 mph in 1938?", "Mallard", "Flying Scotsman|Rocket|Evening Star|City of Truro"),
    ("What is the longest railway line in the world, running from Moscow to Vladivostok?", "Trans-Siberian Railway", "Orient Express|Canadian Pacific|Union Pacific|Ghan"),
    ("When did Japan's first Shinkansen line open?", "1964", "1945|1975|1984|1954"),
    ("What does a maglev train use to float and move?", "Magnetic levitation", "Compressed air only|Steam jets|Large wheels|Propellers"),
    ("What is the speed of the French TGV wheeled-train record from 2007?", "574.8 km/h", "320 km/h|430 km/h|603 km/h|250 km/h"),
    ("What is a pantograph on an electric train?", "A device that collects power from overhead wires", "A type of brake|A cab window|A kind of coupling|A rail switch"),
    ("What is the longest railway tunnel in the world, opened in 2016 in Switzerland?", "Gotthard Base Tunnel", "Channel Tunnel|Seikan Tunnel|Simplon Tunnel|Mont Blanc Tunnel"),
    ("When did the Channel Tunnel open?", "1994", "1974|1984|2004|1964"),
    ("Which was the world's first underground passenger railway (1863)?", "London Underground", "Paris Metro|New York Subway|Moscow Metro|Berlin U-Bahn"),
    ("Who built the steamboat Clermont in 1807?", "Robert Fulton", "James Watt|George Stephenson|Isambard Brunel|Henry Ford"),
    ("Which was the first nuclear-powered submarine (1954)?", "USS Nautilus", "USS Enterprise|HMS Dreadnought|USS Turtle|HMS Victory"),
    ("Where was the Titanic built?", "Belfast", "Southampton|Liverpool|Glasgow|New York"),
    ("From which port did the Titanic begin her only voyage in April 1912?", "Southampton", "Liverpool|Plymouth|Belfast|New York"),
    ("What is a knot as a unit of speed?", "One nautical mile per hour", "One kilometre per hour|One mile per hour|One metre per second|One league per hour"),
    ("How many kilometers is one nautical mile?", "1.852 km", "1.609 km|1.0 km|2.0 km|1.5 km"),
    ("What does the Plimsoll line on a ship's hull show?", "The safe loading limit", "The ship's speed|The captain's rank|The ship's age|The port of origin"),
    ("Which canal opened in 1869, linking the Mediterranean and Red Seas?", "Suez Canal", "Panama Canal|Kiel Canal|Erie Canal|Corinth Canal"),
    ("Which canal opened in 1914, linking the Atlantic and Pacific Oceans?", "Panama Canal", "Suez Canal|Kiel Canal|Erie Canal|Corinth Canal"),
    ("Which Swedish warship sank on her maiden voyage in 1628 and was raised in 1961?", "Vasa", "Victory|Mary Rose|Bismarck|Cutty Sark"),
    ("Which ship was Admiral Nelson's flagship at Trafalgar?", "HMS Victory", "HMS Dreadnought|Mary Rose|Cutty Sark|Vasa"),
    ("Which tea clipper, built in 1869, is preserved in Greenwich, London?", "Cutty Sark", "HMS Victory|Mary Rose|Vasa|Titanic"),
    ("Which expedition completed the first circumnavigation of the world in 1522?", "The Magellan-Elcano expedition", "Columbus's first voyage|Cook's first voyage|Drake's raid|Vasco da Gama's voyage"),
    ("What device uses sound waves to detect objects underwater?", "Sonar", "Radar|Lidar|GPS|Compass"),
    ("What do submarines fill and empty to dive and surface?", "Ballast tanks", "Fuel tanks|Propellers|Torpedo tubes|Periscopes"),
    ("What did the first bicycle-like 'draisine' of 1817 lack?", "Pedals", "Wheels|A frame|Handlebars|A seat"),
    ("Who invented the practical pneumatic tire in 1888?", "John Boyd Dunlop", "Charles Goodyear|Louis Michelin|Henry Ford|Karl Benz"),
    ("What was the large-front-wheeled bicycle of the 1870s called?", "Penny-farthing", "Draisine|Safety bicycle|Boneshaker|Tandem"),
    ("Which company made the first reusable orbital-class rocket booster landing in 2015?", "SpaceX", "NASA|Boeing|Blue Origin|Lockheed Martin"),
    ("Which rocket launched the Apollo Moon missions?", "Saturn V", "Falcon 9|Atlas V|Space Shuttle|Soyuz"),
    ("How many Space Shuttle orbiters flew in space (not counting Enterprise)?", "5", "3|4|6|7"),
    ("Which Soviet spacecraft carried Yuri Gagarin?", "Vostok 1", "Soyuz 1|Apollo 11|Mercury 3|Sputnik 2"),
    ("In what decade did Tesla, Inc. deliver its first Roadster?", "2000s", "1980s|1990s|2010s|1970s"),
    ("What does EV stand for?", "Electric vehicle", "Efficient velocity|Engine valve|Exhaust vent|Express vehicle"),
    ("Which car brand's logo is a trident?", "Maserati", "Ferrari|Peugeot|Lamborghini|Alfa Romeo"),
    ("Which car brand's logo is a cluster of six stars?", "Subaru", "Mercedes-Benz|Mazda|Toyota|Nissan"),
    ("Which car brand's emblem is a winged 'B'?", "Bentley", "Aston Martin|Bugatti|Rolls-Royce|Ford"),
    ("What is the Rolls-Royce hood ornament called?", "Spirit of Ecstasy", "Flying Lady of Speed|Golden Eagle|Silver Ghost|Winged Victory"),
    ("Which firm built the Spitfire fighter in WWII?", "Supermarine", "Boeing|Messerschmitt|Hawker|Lockheed"),
    ("Which country is home to the car maker Skoda?", "Czech Republic", "Poland|Slovakia|Hungary|Germany"),
]
AIRPORTS = [("LHR", "London Heathrow"), ("JFK", "New York John F. Kennedy"), ("CDG", "Paris Charles de Gaulle"), ("LAX", "Los Angeles"),
            ("SIN", "Singapore Changi"), ("DXB", "Dubai"), ("HND", "Tokyo Haneda"), ("SFO", "San Francisco"), ("AMS", "Amsterdam Schiphol"),
            ("FRA", "Frankfurt"), ("SYD", "Sydney"), ("ORD", "Chicago O'Hare")]
FIRSTS = [("The Wright brothers' first powered flight", 1903), ("The Benz Patent-Motorwagen's patent (first practical car)", 1886),
          ("The introduction of Ford's Model T", 1908), ("Louis Bleriot's flight across the English Channel", 1909),
          ("Lindbergh's solo flight across the Atlantic", 1927), ("Chuck Yeager breaking the sound barrier", 1947),
          ("The first flight of the Boeing 747", 1969), ("The first Concorde supersonic test flight", 1969),
          ("The opening of the Panama Canal", 1914), ("The opening of the Suez Canal", 1869), ("The Titanic disaster", 1912),
          ("The Hindenburg disaster", 1937), ("The first launch of the Toyota Prius in Japan", 1997),
          ("The Stockton and Darlington Railway opening", 1825), ("The Rainhill Trials won by Rocket", 1829),
          ("The Shinkansen's opening", 1964), ("The Channel Tunnel's opening", 1994), ("The launch of the USS Nautilus", 1954),
          ("The first Montgolfier balloon flight with people", 1783), ("The first Formula One World Championship", 1950),
          ("The first Space Shuttle launch", 1981), ("The first Nissan Leaf sales", 2010)]


def yrs(y):
    return [str(y + d) for d in (-14, -8, -4, 3, 6, 11) if 1700 < y + d < 2026]


def late():
    r = rng_for("vehicles", "11+")
    out = rows(r, FACT)
    out += rows(r, LOGOS)
    for code, name in AIRPORTS:
        out.append(mc(r, f"Which airport has the IATA code {code}?", name, [n for c, n in AIRPORTS if c != code]))
        out.append(mc(r, f"What is the IATA code for {name} airport?", code, [c for c, n in AIRPORTS if c != code]))
    for t, y in FIRSTS:
        out.append(mc(r, f"In which year did this happen: {t}?", str(y), yrs(y)))
    for b, c in BRANDS:
        pool = ["Japan", "USA", "Germany", "Italy", "France", "China", "Spain", "Australia", "Brazil", "Russia"]
        out.append(mc(r, f"The car maker {b} is based in which country?", c, [x for x in pool if x != c]))
    spd = [("How fast could the SR-71 Blackbird fly?", "Over Mach 3", "About Mach 1|About Mach 2|About Mach 6|About Mach 10"),
           ("What is the Shanghai Maglev's top operating speed?", "About 431 km/h", "About 200 km/h|About 320 km/h|About 600 km/h|About 150 km/h"),
           ("What speed did the JR Central maglev reach in a 2015 test, a rail record?", "603 km/h", "431 km/h|574 km/h|350 km/h|700 km/h"),
           ("ThrustSSC set the land speed record of about what speed in 1997?", "About 1,228 km/h", "About 600 km/h|About 800 km/h|About 400 km/h|About 2,000 km/h"),
           ("How long did the Wright Flyer's first flight last?", "About 12 seconds", "About 12 minutes|About 2 hours|About 1 second|About 1 minute")]
    out += rows(r, spd)
    # who built which
    mk = [("Ford", "Model T"), ("Volkswagen", "Beetle"), ("Toyota", "Prius"), ("Jaguar", "E-Type"), ("Porsche", "911"), ("Nissan", "Leaf"),
          ("Chevrolet", "Corvette"), ("Mini", "Cooper"), ("Tesla", "Model S"), ("Bugatti", "Veyron"), ("Mazda", "MX-5 Miata"), ("Ferrari", "Testarossa"),
          ("Lamborghini", "Countach"), ("Jeep", "Wrangler"), ("Land Rover", "Defender")]
    cars = [m for m, _ in mk]
    for m, mod in mk:
        out.append(mc(r, f"Which brand built the {mod}?", m, [c for c in cars if c != m]))
    return out


def build(band):
    if band == "2-5": return kids()
    if band == "6-10": return mid()
    return late()
