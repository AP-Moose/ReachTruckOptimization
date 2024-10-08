from flask import Flask, render_template, request
from warehouse_optimizer import load_warehouse_layout, a_star_search

app = Flask(__name__)

def generate_warehouse_svg(warehouse_layout):
    svg = []
    aisle_positions = {}
    bay_positions = {}
    aisle_list = set()
    bay_list = set()

    # First, collect all aisles and bays to determine dimensions
    for (aisle, bay) in warehouse_layout.keys():
        aisle_list.add(aisle)
        bay_list.add(bay)

    # Convert aisle labels to numbers for sorting
    def aisle_to_num(aisle_label):
        if aisle_label == 'FW':
            return 0
        elif aisle_label == 'BW':
            return 9999  # Assign a large number for BW to place it at the end
        elif '.' in aisle_label:
            return float(aisle_label)
        else:
            return int(aisle_label)

    sorted_aisles = sorted(aisle_list, key=aisle_to_num)
    sorted_bays = sorted(bay_list, key=lambda x: int(x) if x.isdigit() else 0)

    aisle_width = 50  # Increased width for better readability
    bay_height = 30  # Increased height for better readability
    svg_width = (len(sorted_aisles) + 1) * aisle_width
    svg_height = (len(sorted_bays) + 1) * bay_height + 100  # Added extra space for labels

    # Assign x positions to aisles
    for idx, aisle in enumerate(sorted_aisles):
        aisle_positions[aisle] = idx * aisle_width + aisle_width

    # Assign y positions to bays
    for idx, bay in enumerate(sorted_bays):
        bay_positions[bay] = idx * bay_height + bay_height

    # Draw bays
    for (aisle, bay), info in warehouse_layout.items():
        x = aisle_positions.get(aisle, 0)
        y = bay_positions.get(bay, 0)

        # Determine fill color based on special aisles
        if aisle in ['FW', 'BW']:
            fill_color = "#FFB3BA" if aisle == 'FW' else "#BAFFC9"
        elif '.' in aisle:  # Endcap
            fill_color = "#FFFFBA"
        else:
            fill_color = "#ffffff"

        svg.append(f'<rect x="{x}" y="{y}" width="{aisle_width - 5}" height="{bay_height - 5}" class="bay" fill="{fill_color}" stroke="#000" />')
        svg.append(f'<text x="{x + (aisle_width - 5)/2}" y="{y + (bay_height - 5)/2}" text-anchor="middle" dominant-baseline="middle" font-size="10">{aisle},{bay}</text>')

    # Add aisle labels at the top
    for aisle in sorted_aisles:
        x = aisle_positions[aisle]
        svg.append(f'<text x="{x + (aisle_width - 5)/2}" y="15" text-anchor="middle" font-size="12" font-weight="bold">{aisle}</text>')

    # Add bay labels on the side
    for bay in sorted_bays:
        y = bay_positions[bay]
        svg.append(f'<text x="5" y="{y + (bay_height - 5)/2}" text-anchor="start" dominant-baseline="middle" font-size="12" font-weight="bold">{bay}</text>')

    return f'<svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}">' + ''.join(svg) + '</svg>'
    
def generate_path_svg(path, warehouse_layout):
    svg_elements = []
    aisle_positions = {}
    bay_positions = {}
    aisle_list = set()
    bay_list = set()

    # Collect all aisles and bays
    for (aisle, bay) in warehouse_layout.keys():
        aisle_list.add(aisle)
        bay_list.add(bay)

    # Same sorting and positioning as in warehouse_svg
    def aisle_to_num(aisle_label):
        if aisle_label == 'FW':
            return 0
        elif aisle_label == 'BW':
            return 9999
        elif '.' in aisle_label:
            return float(aisle_label)
        else:
            return int(aisle_label)

    sorted_aisles = sorted(aisle_list, key=aisle_to_num)
    sorted_bays = sorted(bay_list, key=lambda x: int(x) if x.isdigit() else 0)

    aisle_width = 50
    bay_height = 30
    svg_width = (len(sorted_aisles) + 1) * aisle_width
    svg_height = (len(sorted_bays) + 1) * bay_height + 100

    for idx, aisle in enumerate(sorted_aisles):
        aisle_positions[aisle] = idx * aisle_width + aisle_width

    for idx, bay in enumerate(sorted_bays):
        bay_positions[bay] = idx * bay_height + bay_height

    # Draw the path
    for i, step in enumerate(path):
        aisle, bay = step['Move to']
        x = aisle_positions.get(aisle, 0) + (aisle_width - 5) / 2
        y = bay_positions.get(bay, 0) + (bay_height - 5) / 2

        if i == 0:
            svg_elements.append(f'<circle cx="{x}" cy="{y}" r="5" class="start" fill="#00ff00" />')
        elif i == len(path) - 1:
            svg_elements.append(f'<circle cx="{x}" cy="{y}" r="5" class="end" fill="#ff0000" />')
        else:
            svg_elements.append(f'<circle cx="{x}" cy="{y}" r="3" class="path_point" fill="#0000ff" />')

        if i > 0:
            prev_aisle, prev_bay = path[i-1]['Move to']
            prev_x = aisle_positions.get(prev_aisle, 0) + (aisle_width - 5) / 2
            prev_y = bay_positions.get(prev_bay, 0) + (bay_height - 5) / 2
            svg_elements.append(f'<line x1="{prev_x}" y1="{prev_y}" x2="{x}" y2="{y}" class="path" stroke="#0000ff" stroke-width="2" />')

    return ''.join(svg_elements)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        pallet_list_input = request.form.get('pallet_list').split()
        pallet_list = [tuple(pallet.strip().split(',')) for pallet in pallet_list_input]

        warehouse_layout = load_warehouse_layout('warehouse_layout.csv')
        start_location, path, total_cost = a_star_search(pallet_list, warehouse_layout)

        warehouse_svg_content = generate_warehouse_svg(warehouse_layout)
        path_svg_content = generate_path_svg(path, warehouse_layout)

        # Combine the SVG contents
        combined_svg = warehouse_svg_content.replace('</svg>', f'{path_svg_content}</svg>')

        # Format the optimal starting location
        formatted_start_location = f"Aisle {start_location[0]}, Bay {start_location[1]}"

        return render_template('visualization.html',
                               start_location=formatted_start_location,
                               path=path,
                               total_cost=total_cost,
                               combined_svg=combined_svg)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
