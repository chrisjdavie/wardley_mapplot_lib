* Very simplified - make rectangle a node for lines
* * zorder rect above lines
* * one line for power
* * no lines for other nodes
* * Squash very simplified, don't need all that y space
* * stop calling it the weird rectangle
* Make "Node Graph" object, functions to add 
* * 2 bottom of nodes.py
* * `for node in node_list if node.subcat == subcat`?
* decouple NodeList to a builder
# Blog post idea
* 2 posts - one justification, one "Wardley Maps in scientific research"
* Problem statement, ish, - A way of having a conversation about the problem - going "this is a problem", "this might be a solution" for each point, while I'm trying to communicate something about the agregate challenge that Wardley Maps do very well, overall picture
* Wardley maps doesn't, in this form, distinguish between scale of difficulties of evolving nodes
* * Tritium Market - established markets for selling radioactive materials, if Ti can be produced, replicating the patterns may (MAY) not be too hard?
* * 10/s vs 2/day, for days
* * * Lasers doing this
* * * Injection - middle of sphere, hitting tiny pellet each time perfectly
* * * Structure - fully evcuating a sphere of X m**3 10Hz
* * Could be represented by further expanding nodes (but more and more sci-fi like)
* start out super simplified, very simplified plot
* * this entire thing is imaginary ("envisaged"), but mostly not my imagination
* explain how I'm butchering the maps
* * emphasising the "unique" to fusion, leaving off electrical grid feedback (disservice? feedback loop in the electrical grid is important)
* * stretching it out, leaving off the rhs (links to above - the novel is the undiscovered)
* weirdness - "isn't steel, laser systems, Plasma Physics, etc much more evolved?" - it is, but this is specific for this application, neutron resistant etc (as covered below). A weakness of pairing down on "unique to IFE" as each of those has a link to much more evolved points (perhaps more specifically a weakness of these maps? )
* The goal of both major Fusion research projects is "will the fuel ignite?"
* * Not a question asked of any other power project
* Simplified
* Wardley Maps for the uninitiated
* * resturant as an example, perhaps - BK, genesis in someone's kitchen, a single resturant as custom built, a chain as a product. The burger itself evolves faster - for a custom built it's product, for product it's a commodity
* * Maybe just link to somewhere else? Just state "R&D to the first point it delivers value", a couple of examples there
* * "Value chain" this relationship with that - laser hitting targets, laser goes through walls, optics sit in wall, targets injected
* "Visibility" in this context
* * what people will think of when they think of plasma physics, broadly
* Why I'm being so uncharitable
* * Ephasise position is based on *towards an IFE power plant*
* * * "Building laser physics experiments" should be more evolved
* "Value Chain" in this context? (I'm def using these lines as "this won't work without this, dependencies, but tied to value chain - "this allowing that to work" is def a value add)
* Detailed
* highlight the major radiation issues (rep rate, cooling, debris, partial burn, energetic neutrons)
* * show the examples these hurts (first wall, optics, targets (speed), steel, Tritium market) with difficulties
* highlight that the Physics doesn't "matter" - if a powerplant works, is predictable and safe, then the Physics is less of an issue
* * theory led, vs "experiment" led ("experimental"/practice led is much more usual, it's also not always "experiment" - planes and engines were full products as hydro evolved to understand them)
* * * both theory and experiment contribute to R&D in practice
* * IFE is driven by Plasma Physics thou
* radioactive coating from partial burn
* quick references
* "Expertise" - the body of knowledge itself, how to run a fusion powerplant, does not exist
* NIF is primarily about developing the plasma physics
* Target design is evolving, but DD vs IDD (many think DD will be the way to go, energy efficiency but laser incident directly on the surface of the target has many different design requirements than IDD. Also, massssssssss production)
* Tritium market (kinda exists, Defense on govt side has stockpiles, precursor)
* not talked about the heat exchanger; how hard can it be, dual purpose facility, to extract the heat and the newly minted tritium. How hard can it be?
# Make code better
* CLI for this (dicking around with main is not happy)
* KeyError for missing node dependency is unclear
