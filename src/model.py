"""
model.py
This module defines the core ant model, including data structures and behavoir.
It doesn't include any interface or input/output code.
"""
from typing import Callable
from enum import Enum
import random

class LatticeBuilders:
    """
    Collection of helper methods to build different lattice structures.
    """
    @staticmethod
    def square_lattice(world_size: int) -> 'Lattice':
        """
        Generate a square lattice, with diagonal adjacencies.
        
        :param world_size: The size of the world (width of the square)
        :type world_size: int
        :return: The generated square lattice
        :rtype: Lattice
        """
        nodes = {(x, y): LatticeNode((x, y)) for x in range(world_size) for y in range(world_size)}
        for (x, y), node in nodes.items():
            directions = {
                LatticeDir.NORTH: (x, y - 1),
                LatticeDir.NORTHEAST: (x + 1, y - 1),
                LatticeDir.EAST: (x + 1, y),
                LatticeDir.SOUTHEAST: (x + 1, y + 1),
                LatticeDir.SOUTH: (x, y + 1),
                LatticeDir.SOUTHWEST: (x - 1, y + 1),
                LatticeDir.WEST: (x - 1, y),
                LatticeDir.NORTHWEST: (x - 1, y - 1),
            }
            for direction, (nx, ny) in directions.items():
                if 0 <= nx < world_size and 0 <= ny < world_size:
                    neighbor = nodes[(nx, ny)]
                    node.set_neighbor(direction, neighbor)
        lattice = Lattice(list(nodes.values()))
        return lattice                    


class WorldParams:
    tau: int # Units: pu/ant/ts. rate of pheromone deposition per ant per time step
    B: dict[int, float] # Units: probability. mapping from turning angle to probability of following trail
    phi_low: float # Units: probability. minimum probability of staying on trail
    C_s: int # Units: pu. pheromone level of antennae saturation
    delta_phi: float # Units: probability. increase in probability of staying on trail when pheromone level is saturated
    evaporation_rate: int # Units: pu/ts. rate of pheromone evaporation per time step
    world_size: int # Units: nodes. size of the world
    generate_lattice: Callable[[int], 'Lattice'] # Function to generate the lattice structure
    def __init__(
        self,
        tau: int,
        B: dict[int, float],
        phi_low: float,
        C_s: int,
        delta_phi: float,
        evaporation_rate: int = 1,
        world_size: int = 256,
        generate_lattice: Callable[[int], 'Lattice'] = LatticeBuilders.square_lattice,
    ):
        """
        Initialize the world parameters for the ant simulation.
        :param self: The WorldParams instance
        :param tau: Rate of pheromone deposition per ant per time step
        :type tau: int
        :param B: Mapping from turning angle to probability of following trail
        :type B: dict[int, float]
        :param phi_low: Minimum probability of staying on trail
        :type phi_low: float
        :param C_s: Pheromone level of antennae saturation
        :type C_s: int
        :param delta_phi: Increase in probability of staying on trail when pheromone level is saturated
        :type delta_phi: float
        :param evaporation_rate: Rate of pheromone evaporation per time step
        :type evaporation_rate: int
        :param world_size: Size of the world
        :type world_size: int
        :param generate_lattice: Function to generate the lattice structure
        :type generate_lattice: Callable[[int], 'Lattice']
        """
        self.tau = tau
        self.B = B
        self.phi_low = phi_low
        self.C_s = C_s
        self.delta_phi = delta_phi
        self.evaporation_rate = evaporation_rate
        self.world_size = world_size
        self.generate_lattice = generate_lattice
        assert abs(sum(B.values()) - 1.0) < 1e-6, "Turning kernel probabilities must sum to 1."
        assert len(B) == 8, "Turning kernel must have 8 entries for 8 directions."
        assert 0.0 <= phi_low <= 1.0, "phi_low must be between 0 and 1."
        assert 0.0 <= delta_phi <= 1.0, "delta_phi must be between 0 and 1."
    
    @classmethod
    def default(cls) -> 'WorldParams':
        return cls(evaporation_rate=1, tau=1, B={0: 0.44, 45: 0.1, -45: 0.1, 90: 0.08, -90: 0.08, 135: 0.05, -135: 0.05, 180: 0.1}, phi_low=0.1, C_s=16, delta_phi=0.8, world_size=4)

type LatticePos = tuple[int, int]
class LatticeDir(Enum):
    """
    Possible directions for neighboring nodes in the lattice.
    0 degrees is North, increasing clockwise.
    """
    NORTH = 0
    NORTHEAST = 45
    EAST = 90
    SOUTHEAST = 135
    SOUTH = 180
    SOUTHWEST = 225
    WEST = 270
    NORTHWEST = 315

    @staticmethod
    def opposite(direction: 'LatticeDir') -> 'LatticeDir':
        """
        Get the opposite direction of the given direction.
        
        :param direction: The original direction
        :type direction: LatticeDir
        :return: The opposite direction
        :rtype: LatticeDir
        """
        opposite_angle = (direction.value + 180) % 360
        for dir in LatticeDir:
            if dir.value == opposite_angle:
                return dir
        raise ValueError("Invalid direction provided.")

class LatticeNode:
    """
    A single node in the lattice.
    """
    neighbors: dict[LatticeDir, 'LatticeNode | None']
    pheromone_level: int
    position: LatticePos

    def __init__(self, position: LatticePos):
        """
        Initialize a LatticeNode at the given position.
        
        :param self: The LatticeNode instance
        :param position: The position of the node in the lattice
        :type position: LatticePos
        """
        self.position = position
        self.neighbors = {direction: None for direction in LatticeDir}
        self.pheromone_level = 0
    
    def set_neighbor(self, direction: LatticeDir, neighbor: 'LatticeNode'):
        """
        Set a reference to a neighboring node in the specified direction.

        :param self: The LatticeNode instance
        :param direction: The direction of the neighbor
        :type direction: LatticeDir
        :param neighbor: The neighboring LatticeNode
        :type neighbor: 'LatticeNode'
        """
        self.neighbors[direction] = neighbor
    
    def add_pheromone(self, amount: int):
        """
        Increase the pheromone level at this node by the specified amount.
                
        :param self: The LatticeNode instance
        :param amount: The amount of pheromone to add
        :type amount: int
        """
        self.pheromone_level += amount
    
    def remove_pheromone(self, amount: int):
        """
        Decrease the pheromone level at this node by the specified amount,
        checking to ensure it does not go below zero.

        :param self: The LatticeNode instance
        :param amount: The amount of pheromone to remove
        :type amount: int
        """
        self.pheromone_level = max(0, self.pheromone_level - amount)

class Lattice:
    """
    The lattice structure containing multiple LatticeNodes.
    """
    nodes: list[LatticeNode]

    def __init__(self, nodes: list[LatticeNode]):
        """
        Initialize a Lattice with the given list of nodes.
        Intended to only be called by a lattice builder function.

        :param self: The Lattice instance
        :param nodes: The list of LatticeNodes in the lattice
        :type nodes: list[LatticeNode]
        """
        self.nodes = nodes

    def get_node_at(self, position: LatticePos) -> LatticeNode | None:
        """
        Retrieve the node at the specified position, if it exists.
        :param self: The Lattice instance
        :param position: The position to look for
        :type position: LatticePos
        :return: The LatticeNode at the position, or None if not found
        :rtype: LatticeNode | None
        """
        for node in self.nodes:
            if node.position == position:
                return node
        return None
    
    def get_neighbors(self, node: LatticeNode) -> dict[LatticeDir, LatticeNode]:
        """
        Get the neighboring nodes of the given node.

        :param self: The Lattice instance
        :param node: The LatticeNode to get neighbors for
        :type node: LatticeNode
        :return: A dictionary mapping directions to neighboring nodes
        :rtype: dict[LatticeDir, LatticeNode]
        """
        return {direction: neighbor for direction, neighbor in node.neighbors.items() if neighbor is not None}
    
    def evaporate_all_pheromones(self, params: WorldParams):
        """
        Evaporate pheromones on all nodes in the lattice according to the world parameters.

        :param self: The Lattice instance
        :param params: The world parameters
        :type params: WorldParams
        """
        for node in self.nodes:
            node.remove_pheromone(params.evaporation_rate)
    
class AntStatus(Enum):
    LOST = 0
    FOLLOWING = 1

class Ant:
    """
    An ant agent in the lattice.
    """
    current_node: LatticeNode
    status: AntStatus
    velocity: LatticeDir

    def __init__(self, start_node: LatticeNode):
        """
        Initialize an Ant at the given starting node.
        
        :param self: The Ant instance
        :param start_node: The starting LatticeNode for the ant
        :type start_node: LatticeNode
        """
        self.current_node = start_node
        self.status = AntStatus.LOST
        self.velocity = random.choice(list(LatticeDir))
    
    def get_fidelity_probability(self, params: WorldParams) -> float:
        """
        Calculate the probability of the ant remaining on its current trail
        based on the pheromone level at its current node and world parameters.
        Follows the paper's fidelity probability function.
        
        :param self: The Ant instance
        :param params: The world parameters
        :type params: WorldParams
        :return: The probability of staying on the trail
        :rtype: float
        """
        current_pheromone = self.current_node.pheromone_level
        if current_pheromone >= params.C_s:
            return params.phi_low + params.delta_phi
        else:
            return params.phi_low + (params.delta_phi * (current_pheromone / params.C_s))
    
    def move(self, params: WorldParams, lattice: Lattice):
        """
        Pick a direction to move according to lattice state and behavior rules,
        and update lattice and ant state accordingly.
        
        :param self: The Ant instance
        :param params: The world parameters
        :type params: WorldParams
        :param lattice: The lattice structure
        :type lattice: Lattice
        """
        # steps:
        # 1. deposit pheromone at current node
        # 2. if following or on node with nonzero pheromone, run fidelity check
        # 3. if lost, use pick_lost alg. if following and one option, go that way, else use pick_fork alg.

        self.current_node.add_pheromone(params.tau)

        if self.status == AntStatus.FOLLOWING or self.current_node.pheromone_level > 0:
            fidelity_prob = self.get_fidelity_probability(params)
            if random.random() < fidelity_prob:
                self.status = AntStatus.FOLLOWING
            else:
                self.status = AntStatus.LOST
        
        neighbors = lattice.get_neighbors(self.current_node)
        direction_choice: LatticeDir
        if self.status == AntStatus.LOST:
            direction_choice = self.pick_lost(params, neighbors)
        else: # FOLLOWING
            direction_choice = self.pick_following(params, neighbors)
        
        # move!
        self.current_node = neighbors[direction_choice]
        self.velocity = direction_choice

    def pick_following(self, params: WorldParams, neighbors: dict[LatticeDir, LatticeNode]) -> LatticeDir:
        """
        Given a set of possible directions to move, pick one according to
        Fork Algorithm 1 and the world parameters.
        
        :param self: The Ant instance
        :param params: The world parameters
        :type params: WorldParams
        :param options: The possible directions and their corresponding nodes
        :type options: dict[LatticeDir, LatticeNode]
        :return: The chosen direction to move
        :rtype: LatticeDir
        """
        nearby_trails = {dir: node for dir, node in neighbors.items() if node.pheromone_level > 0 and dir != LatticeDir.opposite(self.velocity)}
        
        if len(nearby_trails) == 0:
            # no trails nearby, this shouldn't happen
            raise RuntimeError("Ant in FOLLOWING status found no nearby trails.")

        # if there's a trail in the direction we're going, follow it
        if len(nearby_trails) == 1:
            return list(nearby_trails.keys())[0]
        
        # This is Fork Algorithm 1. Fork Algorithm 2 is not yet implemented.
        if self.velocity in nearby_trails:
            # go forward if possible
            return self.velocity
        
        first_val = next(iter(nearby_trails.values())).pheromone_level
        all_same = all(node.pheromone_level == first_val for node in nearby_trails.values())
        all_saturated = all(node.pheromone_level >= params.C_s for node in nearby_trails.values())
        if all_same or all_saturated:
            # all options have the same pheromone level, act like we're lost
            return self.pick_lost(params, neighbors)
        else:
            # pick the direction with the highest pheromone level
            best_dir = max(nearby_trails.items(), key=lambda item: item[1].pheromone_level)[0]
            return best_dir

    def pick_lost(self, params: WorldParams, neighbors: dict[LatticeDir, LatticeNode]) -> LatticeDir:
        """
        Given a set of possible directions to move, pick one according to
        the Lost Algorithm and the world parameters.
        
        :param self: The Ant instance
        :param params: The world parameters
        :type params: WorldParams
        :param options: The possible directions and their corresponding nodes
        :type options: dict[LatticeDir, LatticeNode]
        :return: The chosen direction to move
        :rtype: LatticeDir
        """
        # again, this won't generalize well to non-square lattices
        # pick a random direction to go, weighted by the turning kernel
        assert len(neighbors) == 8, "Lost algorithm expects all directions to be available."
        direction_ladder: dict[LatticeDir, float] = {}
        total_weight = 0.0
        for increment, weight in params.B.items():
            dir_angle = (self.velocity.value + increment) % 360
            for direction in LatticeDir:
                if direction.value == dir_angle:
                    total_weight += weight
                    direction_ladder[direction] = total_weight
                    break
        # pick a random number and use it to select a direction
        rand_val = random.random()
        for direction, cumulative_weight in direction_ladder.items():
            if rand_val <= cumulative_weight:
                return direction
        # this should be unreachable
        raise RuntimeError("Failed to pick a direction in pick_lost.")

class AntWorld:
    """
    The ant simulation world.
    """

    params: WorldParams
    lattice: Lattice
    nest_node: LatticeNode
    ants: list[Ant]
    timestep: int

    def __init__(self, params: WorldParams):
        """
        Initialize the ant world with the given parameters, nest node, and ants.
        
        :param self: The AntWorld instance
        :param params: The world parameters
        :type params: WorldParams
        :param nest_node: The nest node in the lattice
        :type nest_node: LatticeNode
        :param ants: The list of ants in the world
        :type ants: list[Ant]
        """
        self.params = params
        self.lattice = params.generate_lattice(params.world_size)
        nest_node = self.lattice.get_node_at((params.world_size // 2, params.world_size // 2)) # NOTE: this does not generalize to non-square lattices
        if nest_node is None:
            raise ValueError("Nest node could not be found in the lattice.")
        self.nest_node = nest_node
        self.ants = []
        self.timestep = 0
    
    def step(self):
        """
        Advance the simulation by one time step.
        
        :param self: The AntWorld instance
        """
        # in 1 step:
        # release an ant from the nest
        # move all ants
        # evaporate pheromone levels
        self.timestep += 1

        self.ants.append(Ant(self.nest_node))
        
        # note: this is not time-synchronous; ants move in sequence
        for ant in self.ants:
            ant.move(self.params, self.lattice)
        
        self.lattice.evaporate_all_pheromones(self.params)