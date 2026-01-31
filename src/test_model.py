from model import *

class TestLatticeBuilder:
    def test_square_lattice_small(self):
        lattice = LatticeBuilders.square_lattice(4)
        assert len(lattice.nodes) == 16
        assert lattice.get_node_at((3, 3)) is not None
        assert lattice.get_node_at((4, 4)) is None
        node = lattice.get_node_at((0, 0))
        assert node is not None
        neighbors = lattice.get_neighbors(node)
        assert len([neighbor for neighbor in neighbors.values() if neighbor is not None]) == 3  # Only south, east, and southeast neighbors
        assert len(neighbors) == 8  # All directions should be present, some as None
        expected_positions = {LatticeDir.SOUTH: (0, 1), LatticeDir.EAST: (1, 0), LatticeDir.SOUTHEAST: (1, 1)}
        for direction, pos in expected_positions.items():
            assert neighbors[direction] is not None
            assert neighbors[direction].position == pos # type: ignore # pylint isn't picking up the is not None check
    
    def test_square_lattice_large(self):
        lattice = LatticeBuilders.square_lattice(256)
        assert len(lattice.nodes) == 256**2
        assert lattice.get_node_at((255, 255)) is not None
        assert lattice.get_node_at((256, 256)) is None
        node = lattice.get_node_at((128, 128))
        assert node is not None
        neighbors = lattice.get_neighbors(node)
        assert len(neighbors) == 8
        expected_positions = {
            LatticeDir.NORTH: (128, 127),
            LatticeDir.NORTHEAST: (129, 127),
            LatticeDir.EAST: (129, 128),
            LatticeDir.SOUTHEAST: (129, 129),
            LatticeDir.SOUTH: (128, 129),
            LatticeDir.SOUTHWEST: (127, 129),
            LatticeDir.WEST: (127, 128),
            LatticeDir.NORTHWEST: (127, 127)
        }
        for direction, pos in expected_positions.items():
            assert neighbors[direction] is not None
            assert neighbors[direction].position == pos # type: ignore # pylint isn't picking up the is not None check

class TestLatticeAndNodes:
    def test_node_positions(self):
        lattice = LatticeBuilders.square_lattice(10)
        for x in range(10):
            for y in range(10):
                node = lattice.get_node_at((x, y))
                assert node is not None
                assert node.position == (x, y)
    def test_node_neighbors(self):
        # also mostly covered by LatticeBuiler above
        lattice = LatticeBuilders.square_lattice(3)
        center_node = lattice.get_node_at((1, 1))
        assert center_node is not None
        neighbors = lattice.get_neighbors(center_node)
        assert lattice.get_node_at((0, 1)) == neighbors[LatticeDir.WEST]

    def test_pheromone_levels(self):
        lattice = LatticeBuilders.square_lattice(2)
        node = lattice.get_node_at((0, 0))
        assert node is not None
        assert node.pheromone_level == 0
        node.add_pheromone(5)
        assert node.pheromone_level == 5
        node.add_pheromone(3)
        assert node.pheromone_level == 8
        node.remove_pheromone(4)
        assert node.pheromone_level == 4
        node.remove_pheromone(10)
        assert node.pheromone_level == 0
    
    def test_global_evaporation(self):
        lattice = LatticeBuilders.square_lattice(2)
        node1 = lattice.get_node_at((0, 0))
        node2 = lattice.get_node_at((1, 1))
        assert node1 is not None and node2 is not None
        node1.add_pheromone(10)
        node2.add_pheromone(20)
        lattice.evaporate_all_pheromones(params=WorldParams.default())
        assert node1.pheromone_level == 9
        assert node2.pheromone_level == 19
    
    def test_opposite_directions(self):
        assert LatticeDir.opposite(LatticeDir.NORTH) == LatticeDir.SOUTH
        assert LatticeDir.opposite(LatticeDir.NORTHEAST) == LatticeDir.SOUTHWEST
        assert LatticeDir.opposite(LatticeDir.EAST) == LatticeDir.WEST
        assert LatticeDir.opposite(LatticeDir.SOUTHEAST) == LatticeDir.NORTHWEST
        assert LatticeDir.opposite(LatticeDir.SOUTH) == LatticeDir.NORTH
        assert LatticeDir.opposite(LatticeDir.SOUTHWEST) == LatticeDir.NORTHEAST
        assert LatticeDir.opposite(LatticeDir.WEST) == LatticeDir.EAST
        assert LatticeDir.opposite(LatticeDir.NORTHWEST) == LatticeDir.SOUTHEAST

class TestAnt:
    def test_initialization(self):
        lattice = LatticeBuilders.square_lattice(4)
        node = lattice.get_node_at((1, 1))
        assert node is not None
        ant = Ant(node)
        assert ant.current_node == node
    
    def test_fidelity_probability(self):
        params = WorldParams.default()
        lattice = LatticeBuilders.square_lattice(params.world_size)
        node = lattice.get_node_at((1, 1))
        assert node is not None
        ant = Ant(node)
        prob = ant.get_fidelity_probability(params)
        assert prob == params.phi_low # since there's no pheromone yet
        node.add_pheromone(8)
        prob = ant.get_fidelity_probability(params)
        assert prob == params.phi_low + params.delta_phi * (8 / params.C_s)
        node.add_pheromone(1_000)
        prob = ant.get_fidelity_probability(params)
        assert prob == params.phi_low + params.delta_phi
    
    def test_following_one_option(self):
        params = WorldParams.default()
        lattice = LatticeBuilders.square_lattice(params.world_size)
        node = lattice.get_node_at((1, 1))
        assert node is not None
        ant = Ant(node)
        ant.velocity = LatticeDir.NORTH
        neighbors = lattice.get_neighbors(node)
        # Set pheromone levels so that only one neighbor has pheromone
        neighbors[LatticeDir.EAST].add_pheromone(10) 
        chosen_dir = ant.pick_following(params, neighbors)
        assert chosen_dir == LatticeDir.EAST
    
    def test_following_options_saturated(self):
        params = WorldParams.default()
        lattice = LatticeBuilders.square_lattice(params.world_size)
        node = lattice.get_node_at((1, 1))
        assert node is not None
        ant = Ant(node)
        ant.velocity = LatticeDir.NORTH
        neighbors = lattice.get_neighbors(node)
        # Set pheromone levels to saturation
        neighbors[LatticeDir.NORTHWEST].add_pheromone(params.C_s + 10)
        neighbors[LatticeDir.EAST].add_pheromone(params.C_s + 20)
        # Since both are saturated, should act like lost
        num_trials = 100
        # should see all directions get picked
        direction_counts = {dir: 0 for dir in LatticeDir}
        for _ in range(num_trials):
            dir = ant.pick_following(params, neighbors)
            direction_counts[dir] += 1
        
        assert all(count > 0 for count in direction_counts.values())
    
    def test_following_options_same_level(self):
        params = WorldParams.default()
        lattice = LatticeBuilders.square_lattice(params.world_size)
        node = lattice.get_node_at((1, 1))
        assert node is not None
        ant = Ant(node)
        ant.velocity = LatticeDir.NORTH
        neighbors = lattice.get_neighbors(node)
        # Set pheromone levels on multiple neighbors to the same level
        neighbors[LatticeDir.EAST].add_pheromone(10)
        neighbors[LatticeDir.SOUTH].add_pheromone(10)
        neighbors[LatticeDir.WEST].add_pheromone(10)
        num_trials = 100
        # should see all directions get picked
        direction_counts = {dir: 0 for dir in LatticeDir}
        for _ in range(num_trials):
            dir = ant.pick_following(params, neighbors)
            direction_counts[dir] += 1
        
        assert all(count > 0 for count in direction_counts.values())
    
    def test_following_forward_fork(self):
        params = WorldParams.default()
        lattice = LatticeBuilders.square_lattice(params.world_size)
        node = lattice.get_node_at((1, 1))
        assert node is not None
        ant = Ant(node)
        ant.velocity = LatticeDir.NORTH
        neighbors = lattice.get_neighbors(node)
        # Set pheromone levels on multiple neighbors including forward
        neighbors[LatticeDir.NORTH].add_pheromone(2)
        neighbors[LatticeDir.EAST].add_pheromone(5)
        neighbors[LatticeDir.SOUTH].add_pheromone(15)
        neighbors[LatticeDir.WEST].add_pheromone(10)
        chosen_dir = ant.pick_following(params, neighbors)
        assert chosen_dir == LatticeDir.NORTH  # should prefer going forward
    
    def test_following_options_fork(self):
        params = WorldParams.default()
        lattice = LatticeBuilders.square_lattice(params.world_size)
        node = lattice.get_node_at((1, 1))
        assert node is not None
        ant = Ant(node)
        ant.velocity = LatticeDir.NORTH
        neighbors = lattice.get_neighbors(node)
        # Set pheromone levels on multiple neighbors
        neighbors[LatticeDir.EAST].add_pheromone(5)
        neighbors[LatticeDir.SOUTH].add_pheromone(15)
        neighbors[LatticeDir.WEST].add_pheromone(10)
        chosen_dir = ant.pick_following(params, neighbors)
        assert chosen_dir == LatticeDir.WEST  # we can't turn around, so SOUTH is not an option
    
    def test_lost_algorithm(self):
        params = WorldParams.default()
        lattice = LatticeBuilders.square_lattice(params.world_size)
        node = lattice.get_node_at((1, 1))
        assert node is not None
        ant = Ant(node)
        ant.velocity = LatticeDir.NORTH
        neighbors = lattice.get_neighbors(node)
        direction_counts = {dir: 0 for dir in LatticeDir}
        num_trials = 10_000
        for _ in range(num_trials):
            chosen_dir = ant.pick_lost(params, neighbors)
            direction_counts[chosen_dir] += 1
        # Check that directions are chosen with roughly correct proportions
        total_weight = sum(params.B.values())
        for dir, weight in params.B.items():
            expected_prob = weight / total_weight
            actual_prob = direction_counts[LatticeDir((dir % 360))] / num_trials
            assert abs(expected_prob - actual_prob) < 0.05  # Allow 5% error margin
    
    def test_move_loses_fidelity_sometimes(self):
        params = WorldParams.default()
        trials = 100
        fidelity_losses = 0
        for _ in range(trials):
            lattice = LatticeBuilders.square_lattice(params.world_size)
            node = lattice.get_node_at((1, 1))
            assert node is not None
            ant = Ant(node)
            ant.status = AntStatus.FOLLOWING
            ant.velocity = LatticeDir.NORTH
            # Add some pheromone to our node to increase fidelity chance
            node.add_pheromone(7)
            # Give a direction with pheromone to follow
            lattice.get_neighbors(node)[LatticeDir.NORTH].add_pheromone(10)
            ant.move(params, lattice)
            if ant.status == AntStatus.LOST:
                fidelity_losses += 1 
    
    def test_ant_can_move_off_grid(self):
        params = WorldParams.default()
        lattice = LatticeBuilders.square_lattice(4)
        node = lattice.get_node_at((0, 0))
        assert node is not None
        num_trials = 100
        off_grid_moves = 0
        for _ in range(num_trials):
            ant = Ant(node)
            ant.velocity = LatticeDir.NORTHWEST
            result = ant.move(params, lattice)
            if result == MoveResult.OFF_GRID:
                off_grid_moves += 1
        assert off_grid_moves > 0

class TestAntWorld:
    def test_initialization(self):
        params = WorldParams.default()
        world = AntWorld(params)
        assert world.params == params
        assert len(world.lattice.nodes) == 16
        assert world.nest_node == world.lattice.get_node_at((2, 2))
        assert len(world.ants) == 0
        assert world.timestep == 0
    
    def test_timestep_progression(self):
        params = WorldParams.default()
        world = AntWorld(params)
        initial_timestep = world.timestep
        world.step()
        assert world.timestep == initial_timestep + 1
        assert len(world.ants) == 1  # One ant should be released each step
    
    def test_pheromone_evaporation(self):
        params = WorldParams.default()
        world = AntWorld(params)
        nest_node = world.nest_node
        assert nest_node is not None
        nest_node.add_pheromone(10)
        world.lattice.evaporate_all_pheromones(params)
        assert nest_node.pheromone_level == 9
    
    def test_multiple_timesteps(self):
        params = WorldParams.default()
        num_trials = 50
        for _ in range(num_trials):
            world = AntWorld(params)
            num_steps = 10
            for _ in range(num_steps):
                world.step()
            assert world.timestep == num_steps
            assert len(world.ants) <= num_steps  # One ant per step, some may have moved off-grid
            # Check that pheromone levels are reasonable
            total_pheromone = sum(node.pheromone_level for node in world.lattice.nodes)
            assert total_pheromone > 0
            assert total_pheromone < num_steps * num_steps * params.tau # Should have evaporated some
    
    def test_large_world(self):
        params = WorldParams.default()
        params.world_size = 256
        num_trials = 10
        for _ in range(num_trials):
            world = AntWorld(params)
            num_steps = 100
            for _ in range(num_steps):
                world.step()
            assert world.timestep == num_steps
            assert len(world.ants) == num_steps  # no ants should have moved off-grid
            # Check that pheromone levels are reasonable
            total_pheromone = sum(node.pheromone_level for node in world.lattice.nodes)
            assert total_pheromone > 0
            assert total_pheromone < num_steps * num_steps * params.tau # Should have evaporated some
            # check that ants are reasonably distributed
            positions = {ant.current_node.position for ant in world.ants}
            assert len(positions) > num_steps // 40  # at least 40% of ants in unique positions
            