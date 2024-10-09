import pandas as pd
import heapq
from typing import List, Tuple, Dict, Set, FrozenSet

class Gate:
    def __init__(self):
        self.built_in_closed: Set[str] = set()  # Set of aisles with built-in gates closed
        self.rolly_gates: Set[Tuple[str, str]] = set()  # Set of (aisle, bay) tuples where rolly gates are set up

    def copy(self):
        new_gate = Gate()
        new_gate.built_in_closed = self.built_in_closed.copy()
        new_gate.rolly_gates = self.rolly_gates.copy()
        return new_gate

    def __hash__(self):
        return hash((frozenset(self.built_in_closed), frozenset(self.rolly_gates)))

    def __eq__(self, other):
        return (self.built_in_closed == other.built_in_closed and
                self.rolly_gates == other.rolly_gates)

class State:
    def __init__(self, location: Tuple[str, str], remaining_pallets: Set[Tuple[str, str]],
                 gates: Gate, cost: int, path: List[Dict], side: str):
        self.location = location
        self.remaining_pallets = remaining_pallets
        self.gates = gates
        self.cost = cost
        self.path = path
        self.side = side  # 'even' or 'odd'

    def __lt__(self, other):
        return self.cost < other.cost

def load_warehouse_layout(csv_file: str) -> Dict[Tuple[str, str], Dict[str, str]]:
    warehouse_df = pd.read_csv(csv_file, sep='\t')
    warehouse_layout = {}
    for _, row in warehouse_df.iterrows():
        aisle = str(row['Aisle']).strip()
        bay = str(row['Bay']).strip()
        requires_rolly = row['Requires Rolly Gate']
        adjacent_blocked = str(row['Adjacent Aisle Blocked']).strip()
        warehouse_layout[(aisle, bay)] = {
            'Requires Rolly Gate': requires_rolly,
            'Adjacent Aisle Blocked': adjacent_blocked
        }
    return warehouse_layout

def determine_side(bay: str) -> str:
    """
    Determines the side of the aisle based on the bay number.
    Even bays are on the 'even' side, odd bays on the 'odd' side.
    Endcaps are considered 'even' side.
    """
    if bay.isdigit():
        bay_num = int(bay)
        return 'even' if bay_num % 2 == 0 else 'odd'
    else:
        # Assuming endcaps are on the 'even' side
        return 'even'

def calculate_travel_time(current_location: Tuple[str, str], next_location: Tuple[str, str]) -> int:
    current_aisle, current_bay = current_location
    next_aisle, next_bay = next_location

    if current_aisle == next_aisle:
        if current_bay.isdigit() and next_bay.isdigit():
            bay_diff = abs(int(current_bay) - int(next_bay))
        else:
            bay_diff = 1  # Assuming moving to an endcap or non-numeric bay
        return bay_diff  # 1 minute per bay
    else:
        # Special handling for FW, BW, and non-integer aisles
        if current_aisle in ['FW', 'BW'] or next_aisle in ['FW', 'BW']:
            return 10  # Assuming it takes longer to move to/from FW or BW
        elif '.' in current_aisle or '.' in next_aisle:
            return 3  # Assuming it's quicker to move between half-aisles
        else:
            return 5  # Standard move between aisles

def calculate_gate_cost(current_gates: Gate, required_gates_next: Dict[str, List], side_switch: bool) -> int:
    cost = 0
    # Handle built-in gates
    aisles_to_close = set(required_gates_next['built_in_close']) - current_gates.built_in_closed
    aisles_to_open = current_gates.built_in_closed - set(required_gates_next['built_in_close'])

    # Each aisle has 2 built-in gates to close or open
    cost += (len(aisles_to_close) * 2) * 1  # 1 minute per gate
    cost += (len(aisles_to_open) * 2) * 1

    # Handle rolly gates
    rolly_to_set = set(required_gates_next['rolly_set']) - current_gates.rolly_gates
    rolly_to_remove = current_gates.rolly_gates - set(required_gates_next['rolly_set'])

    cost += len(rolly_to_set) * 1  # 1 minute per rolly gate setup
    cost += len(rolly_to_remove) * 1  # 1 minute per rolly gate removal

    # Handle side switching cost
    if side_switch:
        cost += 2  # 1 minute to take down gate + 1 minute to put up gate

    return cost

def heuristic(state: State) -> int:
    if not state.remaining_pallets:
        return 0

    # Incorporate minimal gate and side switching costs
    min_cost = float('inf')
    for pallet in state.remaining_pallets:
        travel_time = calculate_travel_time(state.location, pallet)
        side_switch = determine_side(pallet[1]) != state.side
        estimated_gate_cost = 2 if side_switch else 0  # 2 minutes for side switch
        total_estimate = travel_time + estimated_gate_cost
        if total_estimate < min_cost:
            min_cost = total_estimate

    return min_cost

def get_adjacent_aisles(aisle: str) -> List[str]:
    if '.' in aisle:  # Endcap
        base_aisle = int(float(aisle))
        return [str(base_aisle), str(base_aisle + 1)]
    else:
        return [aisle]

def a_star_search(pallet_list: List[Tuple[str, str]], warehouse_layout: Dict[Tuple[str, str], Dict[str, str]]):
    possible_start_locations = set(pallet_list)
    best_start_location = None
    min_total_cost = float('inf')
    best_path = None

    for start_location in possible_start_locations:
        initial_gates = Gate()
        initial_side = determine_side(start_location[1])
        initial_state = State(
            location=start_location,
            remaining_pallets=set(pallet_list) - {start_location},
            gates=initial_gates,
            cost=0,
            path=[{
                'Move to': start_location,
                'Travel Time': 0,
                'Gate Cost': 0,
                'Gates Closed': [],
                'Rolly Gates Set': []
            }],
            side=initial_side
        )

        frontier = []
        heapq.heappush(frontier, (heuristic(initial_state), initial_state))
        explored: Set[Tuple[Tuple[str, str], FrozenSet[Tuple[str, str]], FrozenSet[str], FrozenSet[Tuple[str, str]], str]] = set()

        while frontier:
            _, current_state = heapq.heappop(frontier)

            if not current_state.remaining_pallets:
                total_cost = current_state.cost
                if total_cost < min_total_cost:
                    min_total_cost = total_cost
                    best_start_location = start_location
                    best_path = current_state.path
                break

            state_id = (
                current_state.location,
                frozenset(current_state.remaining_pallets),
                frozenset(current_state.gates.built_in_closed),
                frozenset(current_state.gates.rolly_gates),
                current_state.side  # Include side in state_id
            )
            if state_id in explored:
                continue
            explored.add(state_id)

            for pallet in current_state.remaining_pallets:
                next_location = pallet

                travel_time = calculate_travel_time(current_state.location, next_location)

                pallet_info = warehouse_layout.get(next_location, {})
                requires_rolly = pallet_info.get('Requires Rolly Gate', 'No')
                adjacent_blocked = pallet_info.get('Adjacent Aisle Blocked', 'N/A')

                required_gates_next = {
                    'built_in_close': [],
                    'rolly_set': []
                }

                # Handle endcaps and adjacent aisle blocking
                current_aisles = get_adjacent_aisles(next_location[0])
                for aisle in current_aisles:
                    required_gates_next['built_in_close'].append(aisle)

                if adjacent_blocked not in ['Wall', 'N/A']:
                    adjacent_aisles = get_adjacent_aisles(adjacent_blocked)
                    required_gates_next['built_in_close'].extend(adjacent_aisles)

                if requires_rolly == 'Yes':
                    required_gates_next['rolly_set'].append(next_location)

                # Determine the side of the next location
                next_side = determine_side(next_location[1])
                side_switch = (current_state.side != next_side)

                gate_cost = calculate_gate_cost(current_state.gates, required_gates_next, side_switch)

                new_gates = current_state.gates.copy()
                new_gates.built_in_closed.update(required_gates_next['built_in_close'])
                new_gates.rolly_gates.update(required_gates_next['rolly_set'])

                new_remaining = current_state.remaining_pallets.copy()
                new_remaining.remove(pallet)

                new_path = current_state.path.copy()
                new_path.append({
                    'Move to': next_location,
                    'Travel Time': travel_time,
                    'Gate Cost': gate_cost,
                    'Gates Closed': required_gates_next['built_in_close'],
                    'Rolly Gates Set': required_gates_next['rolly_set']
                })

                new_cost = current_state.cost + travel_time + gate_cost

                new_state = State(
                    location=next_location,
                    remaining_pallets=new_remaining,
                    gates=new_gates,
                    cost=new_cost,
                    path=new_path,
                    side=next_side
                )

                total_cost = new_cost + heuristic(new_state)
                heapq.heappush(frontier, (total_cost, new_state))

    if best_path is not None:
        return best_start_location, best_path, min_total_cost
    else:
        return None, None, float('inf')

if __name__ == "__main__":
    warehouse_layout = load_warehouse_layout('warehouse_layout.csv')
    pallet_list = [
        ('1', '5'),
        ('2', '7'),
        ('3', 'EC2'),
        ('FW', '1'),
        ('BW', '3')
    ]
    start_location, path, total_cost = a_star_search(pallet_list, warehouse_layout)

    if path is not None:
        print(f"Best Starting Location: {start_location}")
        print("Optimal Path:")
        for idx, step in enumerate(path, start=1):
            move_to = step['Move to']
            travel = step['Travel Time']
            gate = step['Gate Cost']
            gates_closed = step['Gates Closed']
            rolly_set = step['Rolly Gates Set']
            print(f"{idx}. Move to {move_to}, Travel Time: {travel} min, Gate Cost: {gate} min")
            print(f"   Gates Closed: {gates_closed}")
            print(f"   Rolly Gates Set: {rolly_set}")
        print(f"Total Cost: {total_cost} minutes")
    else:
        print("No valid path found.")
