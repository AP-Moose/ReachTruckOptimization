# Warehouse Route Optimization Using A* Search Algorithm

An advanced application to optimize reach truck routes within a warehouse using the A* search algorithm, minimizing total travel time and gate adjustment costs.

---

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Introduction

This project implements an optimization tool for reach truck drivers in a warehouse setting. By applying the A* search algorithm, it determines the most efficient route to drop off a list of pallets, considering both travel time and gate adjustment costs. The application includes a visual interface to display the optimized path within the warehouse layout.

---

## Features

- **Optimal Route Calculation**: Determines the most efficient route for pallet drop-offs using the A* search algorithm.
- **Gate Adjustment Management**: Accounts for the time required to open or close built-in and rolly gates.
- **Dynamic Starting Point**: Automatically selects the best starting location based on the pallet list.
- **Warehouse Visualization**: Generates an interactive SVG map of the warehouse, displaying aisles, bays, and the optimized path.
- **User-Friendly Interface**: Provides a web-based interface for inputting pallet lists and viewing results.
- **Detailed Path Information**: Offers both simplified and detailed views of the path, including gate operations.

---

## Technologies Used

- **Programming Language**: Python 3.x
- **Web Framework**: Flask
- **Data Manipulation**: Pandas
- **Visualization**: SVG for warehouse layout rendering
- **Frontend**: HTML, CSS, JavaScript

---

## Project Structure

```
warehouse-route-optimization/
├── app.py
├── warehouse_optimizer.py
├── warehouse_layout.csv
├── templates/
│   ├── index.html
│   ├── visualization.html
│   └── result.html
├── static/
│   └── [Static files like CSS or JavaScript if any]
├── README.md
└── requirements.txt
```

- **app.py**: The main Flask application file handling routes and rendering templates.
- **warehouse_optimizer.py**: Contains the implementation of the A* search algorithm and related functions.
- **warehouse_layout.csv**: CSV file containing warehouse data (aisles, bays, gate requirements).
- **templates/**: HTML templates for rendering the web pages.
- **static/**: Directory for static files (optional).

---

## Installation

### Prerequisites

- Python 3.x installed on your system.
- Pip package manager.

### Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/warehouse-route-optimization.git
   cd warehouse-route-optimization
   ```

2. **Create a Virtual Environment (Optional but Recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Required Packages**

   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare the Warehouse Data**

   - Ensure the `warehouse_layout.csv` file is in the project root directory.
   - Verify that the CSV file is correctly formatted with tab separators (`\t`).

---

## Usage

1. **Run the Application**

   ```bash
   python app.py
   ```

2. **Access the Web Interface**

   - Open your web browser and navigate to `http://localhost:5000/`.

3. **Input Pallet List**

   - Enter the list of pallets in the specified format: `aisle,bay` separated by spaces.
     - Example: `1,5 2,7 3,EC2`

4. **View Optimization Results**

   - After submitting, the application displays:
     - **Optimal Starting Location**: The best aisle and bay to start from.
     - **Warehouse Visualization**: An SVG map showing the optimized path.
     - **Path Details**: A simplified list of the route steps.
     - **Detailed Information**: Expandable section with gate operations and costs.

5. **Interpreting the Visualization**

   - **Green Circle**: Starting location.
   - **Red Circle**: Final destination.
   - **Blue Lines**: Path taken by the reach truck.
   - **Rectangles**: Bays and aisles in the warehouse.

6. **Adjusting the Pallet List**

   - Use the "Back to input" link to enter a new pallet list and rerun the optimization.

---

## Screenshots

![Warehouse Visualization](screenshots/warehouse_visualization.png)
*Figure 1: Warehouse layout with the optimized path.*

![Path Details](screenshots/path_details.png)
*Figure 2: Simplified path details with expandable detailed information.*

---

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository**

   - Click on the "Fork" button at the top right of the repository page.

2. **Create a New Branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Commit Your Changes**

   ```bash
   git commit -am 'Add a feature'
   ```

4. **Push to the Branch**

   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request**

   - Navigate to your forked repository.
   - Click on "Compare & pull request" and submit your pull request for review.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contact

For any questions or support, please contact:

- **Name**: [Dave Sousa]
- **Email**: [4davidsousajr@gmail.com]
- **GitHub**: [https://github.com/ap-moose](https://github.com/ap-moose)

---

## Acknowledgments

- **AIMA Book**: Concepts and algorithms are based on "Artificial Intelligence: A Modern Approach" by Stuart Russell and Peter Norvig.
- **OpenAI's ChatGPT**: Assistance in developing and refining the application.

---
