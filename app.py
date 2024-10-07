from flask import Flask, render_template, request
from warehouse_optimizer import load_warehouse_layout, a_star_search

app = Flask(__name__)

def generate_warehouse_svg(warehouse_layout):
    svg = []
    aisle_positions = {}
    current_x = 50

    # First pass to determine x-positions for all aisles
    for (aisle, bay) in warehouse_layout.keys():
        if aisle not in aisle_positions:
            if aisle == 'FW':
                aisle_positions[aisle] = 0
            elif aisle == 'BW':
                aisle_positions[aisle] = 6400  # Assuming 63 aisles, 63 * 100 + 100
            elif '.' in aisle:  # Handle non-integer aisles (e.g., 1.5)
                main_aisle = int(float(aisle))
                aisle_positions[aisle] = main_aisle * 100 + 50
            else:
                aisle_positions[aisle] = int(aisle) * 100

    max_y = 0
    for (aisle, bay), info in warehouse_layout.items():
        x = aisle_positions[aisle]
        if bay.isdigit():
            y = int(bay) * 50
        elif bay == 'EC1':
            y = 0
        elif bay == 'EC2':
            y = 550
        elif bay == 'EC3':
            y = 1100
        else:
            y = 550  # Default position for unknown bays

        max_y = max(max_y, y)

        svg.append(f'<rect x="{x-50}" y="{y}" width="100" height="50" class="bay" />')
        svg.append(f'<text x="{x}" y="{y+25}" text-anchor="middle" dominant-baseline="middle">{aisle},{bay}</text>')

    svg_width = max(aisle_positions.values()) + 100
    svg_height = max_y + 100

    return f'<svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}">' + ''.join(svg) + '</svg>'

def generate_path_svg(path, warehouse_layout):
    svg = []
    aisle_positions = {}
    current_x = 50

    # First pass to determine x-positions for all aisles
    for (aisle, bay) in warehouse_layout.keys():
        if aisle not in aisle_positions:
            if aisle == 'FW':
                aisle_positions[aisle] = 0
            elif aisle == 'BW':
                aisle_positions[aisle] = 6400  # Assuming 63 aisles, 63 * 100 + 100
            elif '.' in aisle:  # Handle non-integer aisles (e.g., 1.5)
                main_aisle = int(float(aisle))
                aisle_positions[aisle] = main_aisle * 100 + 50
            else:
                aisle_positions[aisle] = int(aisle) * 100

    for i, step in enumerate(path):
        aisle, bay = step['Move to']
        x = aisle_positions[aisle]
        if bay.isdigit():
            y = int(bay) * 50 + 25
        elif bay == 'EC1':
            y = 25
        elif bay == 'EC2':
            y = 575
        elif bay == 'EC3':
            y = 1125
        else:
            y = 575  # Default position for unknown bays

        if i == 0:
            svg.append(f'<circle cx="{x}" cy="{y}" r="5" class="start" />')
        elif i == len(path) - 1:
            svg.append(f'<circle cx="{x}" cy="{y}" r="5" class="end" />')
        if i > 0:
            prev_aisle, prev_bay = path[i-1]['Move to']
            prev_x = aisle_positions[prev_aisle]
            if prev_bay.isdigit():
                prev_y = int(prev_bay) * 50 + 25
            elif prev_bay == 'EC1':
                prev_y = 25
            elif prev_bay == 'EC2':
                prev_y = 575
            elif prev_bay == 'EC3':
                prev_y = 1125
            else:
                prev_y = 575  # Default position for unknown bays
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
