from flask import Flask, render_template, request
from warehouse_optimizer import load_warehouse_layout, a_star_search

app = Flask(__name__)

def generate_warehouse_svg(warehouse_layout):
    svg = []
    aisle_positions = {}
    max_aisle = 63
    aisle_width = 100
    bay_height = 50
    svg_width = (max_aisle + 2) * aisle_width  # +2 for FW and BW
    svg_height = 1200  # Increased height to accommodate more bays

    # Calculate x-positions for all aisles
    for aisle in range(1, max_aisle + 1):
        aisle_positions[str(aisle)] = aisle * aisle_width

    # Special handling for FW, BW, and non-integer aisles
    aisle_positions['FW'] = 0
    aisle_positions['BW'] = (max_aisle + 1) * aisle_width
    
    for (aisle, bay) in warehouse_layout.keys():
        if '.' in aisle:
            main_aisle = int(float(aisle))
            aisle_positions[aisle] = main_aisle * aisle_width + aisle_width // 2

    for (aisle, bay), info in warehouse_layout.items():
        x = aisle_positions[aisle]
        if bay.isdigit():
            y = int(bay) * bay_height
        elif bay == 'EC1':
            y = 0
        elif bay == 'EC2':
            y = svg_height - bay_height
        elif bay == 'EC3':
            y = svg_height // 2
        else:
            y = svg_height // 2  # Default position for unknown bays

        svg.append(f'<rect x="{x-aisle_width//2}" y="{y}" width="{aisle_width}" height="{bay_height}" class="bay" />')
        svg.append(f'<text x="{x}" y="{y+bay_height//2}" text-anchor="middle" dominant-baseline="middle">{aisle},{bay}</text>')

    return f'<svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}">' + ''.join(svg) + '</svg>'

def generate_path_svg(path, warehouse_layout):
    svg = []
    aisle_positions = {}
    max_aisle = 63
    aisle_width = 100
    bay_height = 50
    svg_width = (max_aisle + 2) * aisle_width  # +2 for FW and BW
    svg_height = 1200

    # Calculate x-positions for all aisles
    for aisle in range(1, max_aisle + 1):
        aisle_positions[str(aisle)] = aisle * aisle_width

    # Special handling for FW, BW, and non-integer aisles
    aisle_positions['FW'] = 0
    aisle_positions['BW'] = (max_aisle + 1) * aisle_width
    
    for (aisle, bay) in warehouse_layout.keys():
        if '.' in aisle:
            main_aisle = int(float(aisle))
            aisle_positions[aisle] = main_aisle * aisle_width + aisle_width // 2

    for i, step in enumerate(path):
        aisle, bay = step['Move to']
        x = aisle_positions[aisle]
        if bay.isdigit():
            y = int(bay) * bay_height + bay_height // 2
        elif bay == 'EC1':
            y = bay_height // 2
        elif bay == 'EC2':
            y = svg_height - bay_height // 2
        elif bay == 'EC3':
            y = svg_height // 2
        else:
            y = svg_height // 2  # Default position for unknown bays

        if i == 0:
            svg.append(f'<circle cx="{x}" cy="{y}" r="5" class="start" />')
        elif i == len(path) - 1:
            svg.append(f'<circle cx="{x}" cy="{y}" r="5" class="end" />')
        if i > 0:
            prev_aisle, prev_bay = path[i-1]['Move to']
            prev_x = aisle_positions[prev_aisle]
            if prev_bay.isdigit():
                prev_y = int(prev_bay) * bay_height + bay_height // 2
            elif prev_bay == 'EC1':
                prev_y = bay_height // 2
            elif prev_bay == 'EC2':
                prev_y = svg_height - bay_height // 2
            elif prev_bay == 'EC3':
                prev_y = svg_height // 2
            else:
                prev_y = svg_height // 2  # Default position for unknown bays
            svg.append(f'<line x1="{prev_x}" y1="{prev_y}" x2="{x}" y2="{y}" class="path" />')
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
