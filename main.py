import tkinter as tk
from tkinter import messagebox
from queue import PriorityQueue
import math
# AI Labyrinth Game based on searching algorithms
class RobotGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Robot Game")
        self.master.geometry("600x600")

        self.rooms = {
            'A': {'B', 'D'},
            'B': {'A', 'C', 'E'},
            'C': {'B', 'F'},
            'D': {'A', 'E', 'G'},
            'E': {'B', 'D', 'F', 'H'},
            'F': {'C', 'E', 'I'},
            'G': {'D', 'H'},
            'H': {'E', 'G', 'I'},
            'I': {'F', 'H'}
        }

        self.room_buttons = {}

        self.initialize_grid()
        self.create_widgets()

    def initialize_grid(self):
        row, col = 0, 0
        for room in self.rooms.keys():
            btn = tk.Button(self.master, text=room, width=5, height=2)
            btn.grid(row=row, column=col)
            self.room_buttons[room] = btn
            col += 1
            if col == 3:
                col = 0
                row += 1

    def create_widgets(self):
        tk.Label(self.master, text="Initial State:").grid(row=3, column=0)
        tk.Label(self.master, text="Goal State:").grid(row=4, column=0)
        tk.Label(self.master, text="Walls:").grid(row=5, column=0)
        tk.Label(self.master, text="Search Algorithm:").grid(row=6, column=0)

        self.initial_state_entry = tk.Entry(self.master)
        self.initial_state_entry.grid(row=3, column=1)

        self.goal_state_entry = tk.Entry(self.master)
        self.goal_state_entry.grid(row=4, column=1)

        self.walls_entry = tk.Entry(self.master)
        self.walls_entry.grid(row=5, column=1)

        self.algorithm_var = tk.StringVar()
        self.algorithm_var.set("Uniform Cost")
        algorithm_menu = tk.OptionMenu(self.master, self.algorithm_var, "Uniform Cost", "A*")
        algorithm_menu.grid(row=6, column=1)

        start_button = tk.Button(self.master, text="Start Search", command=self.start_search)
        start_button.grid(row=7, column=0, columnspan=2)

        self.canvas = tk.Canvas(self.master, width=400, height=300, borderwidth=2, relief="ridge")
        self.canvas.grid(row=8, column=0, columnspan=2)

    def start_search(self):
        initial_state = self.initial_state_entry.get().upper()
        goal_state = self.goal_state_entry.get().upper()
        walls_input = self.walls_entry.get().upper().replace(" ", "")
        walls = [walls_input[i:i + 2] for i in range(0, len(walls_input), 2)]
        algorithm = self.algorithm_var.get()

        if not self.validate_input(initial_state, goal_state, walls):
            return

        if algorithm == "Uniform Cost":
            path, cost = self.uniform_cost_search(initial_state, goal_state, walls)
        elif algorithm == "A*":
            path, cost = self.a_star_search(initial_state, goal_state, walls)
        else:
            messagebox.showerror("Error", "Invalid search algorithm.")
            return

        if path:
            messagebox.showinfo("Result", f"Path: {path}\nCost: {cost}")
            self.visualize_search(path)
        else:
            messagebox.showinfo("Result", "No path found.")

    def heuristic_cost(self, state, goal_state):
        current_row, current_col = divmod(list(self.rooms.keys()).index(state), 3)
        goal_row, goal_col = divmod(list(self.rooms.keys()).index(goal_state), 3)

        # Calculate hamming distance
        distance = math.sqrt((goal_row - current_row)**2 + (goal_col - current_col)**2)
        return distance

    def get_neighbors(self, current_state, walls):
        neighbors = []
        for neighbor in self.rooms[current_state]:
            move_cost = self.calculate_move_cost(current_state, neighbor)
            if current_state + neighbor not in walls and neighbor + current_state not in walls:
                neighbors.append((neighbor, move_cost))
        return neighbors

    def calculate_move_cost(self, current_state, neighbor):
        current_row, current_col = divmod(list(self.rooms.keys()).index(current_state), 3)
        neighbor_row, neighbor_col = divmod(list(self.rooms.keys()).index(neighbor), 3)

        # Calculate the absolute differences in row and column
        row_diff = current_row - neighbor_row
        col_diff = current_col - neighbor_col


        if row_diff == 0 and col_diff != 0:
            return 2  # Moving right or left
        elif col_diff == 0 and row_diff != 0:
            return 1  # Moving up or down
        else:
            return 0

    def uniform_cost_search(self, initial_state, goal_state, walls):
        fringe = PriorityQueue()
        fringe.put((0, initial_state, []))  # (total_cost, state, path)
        explored = set()

        while not fringe.empty():
            total_cost, current_state, path = fringe.get()

            if current_state == goal_state:
                return path + [(current_state, 0)], total_cost

            explored.add(current_state)

            neighbors = self.get_neighbors(current_state, walls)
            neighbors.sort(key=lambda x: x[1])

            for neighbor, move_cost in neighbors:
                if neighbor not in explored:
                    new_total_cost = total_cost + move_cost
                    fringe.put((new_total_cost, neighbor, path + [(current_state, move_cost)]))

        return [], 0

    def a_star_search(self, initial_state, goal_state, walls):
        fringe = PriorityQueue()
        heuristic_cost = self.heuristic_cost(initial_state, goal_state)
        fringe.put((heuristic_cost, 0, initial_state, []))
        explored = set()

        while not fringe.empty():
            heuristic, total_cost, current_state, path = fringe.get()

            if current_state == goal_state:
                return path + [(current_state, 0)], total_cost

            explored.add(current_state)

            neighbors = self.get_neighbors(current_state, walls)
            neighbors.sort(key=lambda x: x[1])

            for neighbor, move_cost in neighbors:
                new_total_cost = total_cost + move_cost
                heuristic_cost = self.heuristic_cost(neighbor, goal_state)
                priority = heuristic_cost + new_total_cost
                if neighbor not in explored:
                    fringe.put((priority, new_total_cost, neighbor, path + [(current_state, move_cost)]))

        return [], 0

    def visualize_search(self, path):

        self.canvas.delete("all")


        for i in range(len(path) - 1):
            start_room = path[i][0]
            end_room = path[i + 1][0]
            start_row, start_col = divmod(list(self.rooms.keys()).index(start_room), 3)
            end_row, end_col = divmod(list(self.rooms.keys()).index(end_room), 3)
            self.canvas.create_line(start_col * 100 + 50, start_row * 100 + 50,
                                    end_col * 100 + 50, end_row * 100 + 50, fill="green", width=2)


        for room, _ in path:
            row, col = divmod(list(self.rooms.keys()).index(room), 3)
            self.canvas.create_oval(col * 100 + 40, row * 100 + 40,
                                    col * 100 + 60, row * 100 + 60, fill="red")

    def validate_input(self, initial_state, goal_state, walls):
        valid_states = set(self.rooms.keys())

        if initial_state not in valid_states or goal_state not in valid_states:
            messagebox.showerror("Error", "Invalid initial or goal state.")
            return False

        for wall in walls:
            if len(wall) != 2 or not (all(c in valid_states for c in wall)):
                messagebox.showerror("Error", "Invalid wall input.")
                return False

            if wall[0] not in self.rooms[wall[1]] or wall[1] not in self.rooms[wall[0]]:
                messagebox.showerror("Error", "Wall does not connect neighboring rooms.")
                return False

        return True


if __name__ == "__main__":
    root = tk.Tk()
    game = RobotGame(root)
    root.mainloop()
