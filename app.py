from flask import Flask, render_template, request
from warehouse_optimizer import load_warehouse_layout, a_star_search

app = Flask(__name__)

def generate_warehouse_svg(warehouse_layout):
    svg = []
    for (aisle, bay), info in warehouse_layout.items():
        x = int(aisle) * 100 - 50
        y = int(bay) * 50 if bay.isdigit() else 550
        svg.append(f'<rect x="{x}" y="{y}" width="100" height="50" class="bay" />')
        svg.append(f'<text x="{x+50}" y="{y+25}" text-anchor="middle" dominant-baseline="middle">{aisle},{bay}</text>')
    return ''.join(svg)

def generate_path_svg(path):
    svg = []
    for i, step in enumerate(path):
        aisle, bay = step['Move to']
        x = int(aisle) * 100
        y = int(bay) * 50 + 25 if bay.isdigit() else 575
        if i == 0:
            svg.append(f'<circle cx="{x}" cy="{y}" r="5" class="start" />')
        elif i == len(path) - 1:
            svg.append(f'<circle cx="{x}" cy="{y}" r="5" class="end" />')
        if i > 0:
            prev_aisle, prev_bay = path[i-1]['Move to']
            prev_x = int(prev_aisle) * 100
            prev_y = int(prev_bay) * 50 + 25 if prev_bay.isdigit() else 575
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
        path_svg = generate_path_svg(path)
        
        return render_template('visualization.html', 
                               start_location=start_location, 
                               path=path, 
                               total_cost=total_cost, 
                               warehouse_svg=warehouse_svg, 
                               path_svg=path_svg)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
