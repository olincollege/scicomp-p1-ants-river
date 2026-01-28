"""
model.py
This module defines the core ant model, including data structures and behavoir.
It doesn't include any interface or input/output code.
"""
from typing import Callable
from enum import Enum

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
        # TODO
        pass

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
    
class AntStatus(Enum):
    LOST = 0
    FOLLOWING = 1

class Ant:
    """
    An ant agent in the lattice.
    """
    current_node: LatticeNode
    status: AntStatus

    def __init__(self, start_node: LatticeNode):
        """
        Initialize an Ant at the given starting node.
        
        :param self: The Ant instance
        :param start_node: The starting LatticeNode for the ant
        :type start_node: LatticeNode
        """
        self.current_node = start_node
        self.status = AntStatus.LOST
    
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
        # TODO
        pass

    def pick_fork(self, params: WorldParams, options: dict[LatticeDir, LatticeNode]) -> LatticeDir:
        """
        Given a set of possible directions to move, pick one according to
        the Fork Algorithm and the world parameters.
        
        :param self: The Ant instance
        :param params: The world parameters
        :type params: WorldParams
        :param options: The possible directions and their corresponding nodes
        :type options: dict[LatticeDir, LatticeNode]
        :return: The chosen direction to move
        :rtype: LatticeDir
        """
        # TODO
        pass

    def pick_lost(self, params: WorldParams, options: dict[LatticeDir, LatticeNode]) -> LatticeDir:
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
        # TODO
        pass


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
        # TODO
        pass