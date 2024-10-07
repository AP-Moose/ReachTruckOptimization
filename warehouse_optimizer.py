import pandas as pd
import heapq
from typing import List, Tuple, Dict, Set, FrozenSet

class Gate:
    def __init__(self):
        self.built_in_closed: Set[str] = set()
        self.rolly_gates: Set[Tuple[str, str]] = set()

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
                 gates: Gate, cost: int, path: List[Dict]):
        self.location = location
        self.remaining_pallets = remaining_pallets
        self.gates = gates
        self.cost = cost
        self.path = path

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

def calculate_travel_time(current_location: Tuple[str, str], next_location: Tuple[str, str]) -> int:
    current_aisle, current_bay = current_location
    next_aisle, next_bay = next_location

    if current_aisle == next_aisle:
        if current_bay.isdigit() and next_bay.isdigit():
            bay_diff = abs(int(current_bay) - int(next_bay))
        else:
            bay_diff = 1  # Assuming moving to an endcap or non-numeric bay
        return bay_diff
    else:
        return 5  # Moving between aisles

def calculate_gate_cost(current_gates: Gate, required_gates_next: Dict[str, List]) -> int:
    cost = 0
    aisles_to_close = set(required_gates_next['built_in_close']) - current_gates.built_in_closed
    aisles_to_open = current_gates.built_in_closed - set(required_gates_next['built_in_close'])

    cost += (len(aisles_to_close) * 2) * 1  # 1 minute per gate, 2 gates per aisle
    cost += (len(aisles_to_open) * 2) * 1

    rolly_to_set = set(required_gates_next['rolly_set']) - current_gates.rolly_gates
    rolly_to_remove = current_gates.rolly_gates - set(required_gates_next['rolly_set'])

    cost += len(rolly_to_set) * 5  # 5 minutes per rolly gate
    cost += len(rolly_to_remove) * 5

    return cost

def heuristic(state: State) -> int:
    if not state.remaining_pallets:
        return 0

    return min(calculate_travel_time(state.location, pallet) for pallet in state.remaining_pallets)

def a_star_search(pallet_list: List[Tuple[str, str]], warehouse_layout: Dict[Tuple[str, str], Dict[str, str]]):
    possible_start_locations = set(pallet_list)
    best_start_location = None
    min_total_cost = float('inf')
    best_path = None

    for start_location in possible_start_locations:
        initial_gates = Gate()
        initial_state = State(
            location=start_location,
            remaining_pallets=set(pallet_list) - {start_location},
            gates=initial_gates,
            cost=0,
            path=[]
        )

        frontier = []
        heapq.heappush(frontier, (heuristic(initial_state), initial_state))
        explored: Set[Tuple[Tuple[str, str], FrozenSet[Tuple[str, str]], FrozenSet[str], FrozenSet[Tuple[str, str]]]] = set()

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
                frozenset(current_state.gates.rolly_gates)
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

                required_gates_next['built_in_close'].append(next_location[0])

                if adjacent_blocked not in ['Wall', 'N/A']:
                    required_gates_next['built_in_close'].append(adjacent_blocked)

                if requires_rolly == 'Yes':
                    required_gates_next['rolly_set'].append(next_location)

                gate_cost = calculate_gate_cost(current_state.gates, required_gates_next)

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
                    path=new_path
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
        for step in path:
            move_to = step['Move to']
            travel = step['Travel Time']
            gate = step['Gate Cost']
            gates_closed = step['Gates Closed']
            rolly_set = step['Rolly Gates Set']
            print(f"Move to {move_to}, Travel Time: {travel} min, Gate Cost: {gate} min")
            print(f"  Gates Closed: {gates_closed}")
            print(f"  Rolly Gates Set: {rolly_set}")
        print(f"Total Cost: {total_cost} minutes")
    else:
        print("No valid path found.")
