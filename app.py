from flask import Flask, render_template, request
from warehouse_optimizer import load_warehouse_layout, a_star_search

app = Flask(__name__)

def generate_warehouse_svg(warehouse_layout):
    svg = []
    aisle_positions = {}
    max_aisle = 63
    aisle_width = 20  # Increased width for better readability
    bay_height = 15  # Increased height for better readability
    svg_width = (max_aisle + 2) * aisle_width  # +2 for FW and BW
    svg_height = 2000  # Increased height to accommodate all bays

    # Calculate x-positions for all aisles, including endcaps
    for aisle in range(1, max_aisle + 1):
        aisle_positions[str(aisle)] = aisle * aisle_width
        # Endcap positions
        aisle_positions[f"{aisle}.5"] = (aisle * aisle_width) + (aisle_width // 2)

    # Special handling for FW and BW
    aisle_positions['FW'] = 0
    aisle_positions['BW'] = (max_aisle + 1) * aisle_width

    for (aisle, bay), info in warehouse_layout.items():
        x = aisle_positions[aisle]
        if bay.isdigit():
            y = int(bay) * bay_height
        elif bay in ['EC1', 'EC2', 'EC3']:
            y = svg_height // 2
        else:
            y = svg_height // 2  # Default position for unknown bays

        # Different colors for FW, BW, and endcaps
        if aisle in ['FW', 'BW']:
            fill_color = "#FFB3BA" if aisle == 'FW' else "#BAFFC9"
        elif '.' in aisle:  # Endcap
            fill_color = "#FFFFBA"
        else:
            fill_color = "#ffffff"

        svg.append(f'<rect x="{x-aisle_width//2}" y="{y}" width="{aisle_width}" height="{bay_height}" class="bay" fill="{fill_color}" stroke="#000" />')
        svg.append(f'<text x="{x}" y="{y+bay_height//2}" text-anchor="middle" dominant-baseline="middle" font-size="10">{aisle},{bay}</text>')

    # Add aisle labels at the top
    for aisle, x in aisle_positions.items():
        if '.' not in aisle:  # Don't show labels for endcaps
            svg.append(f'<text x="{x}" y="5" text-anchor="middle" dominant-baseline="hanging" font-size="12" font-weight="bold">{aisle}</text>')

    return f'<svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}">' + ''.join(svg) + '</svg>'

def generate_path_svg(path, warehouse_layout):
    svg = []
    aisle_positions = {}
    max_aisle = 63
    aisle_width = 20  # Matching the width in generate_warehouse_svg
    bay_height = 15  # Matching the height in generate_warehouse_svg
    svg_width = (max_aisle + 2) * aisle_width  # +2 for FW and BW
    svg_height = 2000  # Matching the height in generate_warehouse_svg

    # Calculate x-positions for all aisles, including endcaps
    for aisle in range(1, max_aisle + 1):
        aisle_positions[str(aisle)] = aisle * aisle_width
        aisle_positions[f"{aisle}.5"] = (aisle * aisle_width) + (aisle_width // 2)

    # Special handling for FW and BW
    aisle_positions['FW'] = 0
    aisle_positions['BW'] = (max_aisle + 1) * aisle_width

    for i, step in enumerate(path):
        aisle, bay = step['Move to']
        x = aisle_positions[aisle]
        if bay.isdigit():
            y = int(bay) * bay_height + bay_height // 2
        elif bay in ['EC1', 'EC2', 'EC3']:
            y = svg_height // 2
        else:
            y = svg_height // 2  # Default position for unknown bays

        if i == 0:
            svg.append(f'<circle cx="{x}" cy="{y}" r="5" class="start" fill="#00ff00" />')
        elif i == len(path) - 1:
            svg.append(f'<circle cx="{x}" cy="{y}" r="5" class="end" fill="#ff0000" />')
        if i > 0:
            prev_aisle, prev_bay = path[i-1]['Move to']
            prev_x = aisle_positions[prev_aisle]
            if prev_bay.isdigit():
                prev_y = int(prev_bay) * bay_height + bay_height // 2
            elif prev_bay in ['EC1', 'EC2', 'EC3']:
                prev_y = svg_height // 2
            else:
                prev_y = svg_height // 2  # Default position for unknown bays
            svg.append(f'<line x1="{prev_x}" y1="{prev_y}" x2="{x}" y2="{y}" class="path" stroke="#0000ff" stroke-width="3" />')
    
    return ''.join(svg)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        pallet_list = request.form.get('pallet_list').split()
        pallet_list = [tuple(pallet.split(',')) for pallet in pallet_list]
        
        warehouse_layout = load_warehouse_layout('warehouse_layout.csv')
        start_location, path, total_cost = a_star_search(pallet_list, warehouse_layout)
        
        warehouse_svg = generate_warehouse_svg(warehouse_layout)
        path_svg = generate_path_svg(path, warehouse_layout)
        
        return render_template('visualization.html', 
                               start_location=start_location, 
                               path=path, 
                               total_cost=total_cost, 
                               warehouse_svg=warehouse_svg, 
                               path_svg=path_svg)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
