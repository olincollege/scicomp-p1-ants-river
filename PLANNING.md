# Rough data plan
The data structures I plan to use, in typed pseudocode. This is nonbinding, just a snapshot of what I was thinking at the start of the project.

I'm going to go somewhat object-oriented here.
```rust
type LatticePos (uint, uint); // some type to represent a position on the lattice

enum LatticeDir {
    0 = NORTH;
    45 = NORTHEAST;
    90 = EAST;
    135 = SOUTHEAST;
    180 = SOUTH;
    225 = SOUTHWEST;
    270 = WEST;
    315 = NORTHWEST;
} // note: doesn't generalize well to non-rectangular lattices

// LatticeNode: a graph node representing a possible location
struct LatticeNode {
    Map<LatticeDir, Option<LatticeNode>> neighbors; // a None option is a place ants can go, but not return from
    uint pher_quantity; // analogous to C(x, t). Units: pu (pheromone units)
    LatticePos pos; // represent the global position of this node
}

struct Lattice {
    Vector<LatticeNode> nodes;
}

enum AntStatus {LOST; FOLLOWING}

struct Ant {
    LatticeNode current_node;
    AntStatus status; // analogous to L(x,t) and F(x,t)
}

struct WorldParams {
    // Enumerated parameters from the paper:
    uint tau; // "rate of pheromone deposition per ant per time step." Units: pu/ts
    Map<uint, float> B; // turning kernel, maps a difference in angles to a probability
    float phi_low; // minimum probability of staying on trail. Units: unitless (probability)
    uint C_s; // concentration of pheromone at antennae saturation. Units: pu
    float delta_phi; // rise in phi between phi_low and C_s. Units: unitless (probability)
    // Enumerated parameters not defined here:
    // C(x, t), L(x, t), and F(x, t) are derived from lattice and ants
    // \phi(C) is constructed from phi_low, C_s, and delta_phi
    // r-bar is derived from 1/(1-\phi(C)) and isn't directly used by the model

    // Implied parameters from the paper:
    uint evaporation_rate // paper defines as 1
    uint world_size; // paper defines as 256
    Fn<WorldParams -> Lattice> generate_lattice; // paper defines as square graph with diagonal adjacencies

}

struct AntWorld {
    WorldParams params;
    Lattice lattice;
    LatticeNode nest_node;
    Vector<Ant> ants;
    uint timestep;
}
```
Notes:
* LatticePos is needed for direction-biased turning, but I'm going to try to use LatticeNode refs where possible
* Direction-biased turning is actually pretty annoying in this data model, it forces me to translate at least once between abstract graph adjacencies and physical relative location, and to bake in some assumptions about grid shape in LatticeDir
* I wish I'd found a better way to represent the turning kernel and how it relates to LatticeDir, I don't like how weakly typed using "the difference between LatticeDir angles" is
* There's an argument for not having an Ant object and just tracking them via uint params on LatticeNodes, but this way will be a bit easier to reason about and iterate over imo
* To match the paper, I've used ints for pheromone units, when I would usually use floats.

That means that some core functions will be:
```rust
impl AntWorld {
    void step(); // step time forward. update timestep, move ants, create new ants, etc.
}

impl Ant {
    void move(WorldParams params, Lattice lattice); // pick a direction to move and go there, updating self.status if needed
    LatticeNode pick_fork(WorldParams params, Map<LatticeDir, LatticeNode> options); // the Fork Algorithm
}

impl Lattice {
    LatticeNode getNodeAtPos(LatticePos pos); // get a node by global position
    Map<LatticeDir, LatticeNode> get_neighbors(LatticeNode node); // helper to get the neighbors and directions of a node
    void evaporate_all_pheromone(WorldParams params); // evaporate pheromone at all nodes
}

impl LatticeNode {
    void add_pheromone(uint amount); // add amount pus of pheromone to this node, due to an ant being there.
    void remove_pheromone(uint amount); // remove amount pus of pheromone to this node, due to evaporation
}
```