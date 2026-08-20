import tkinter as tk
from tkinter import messagebox


class Stack:
    """A simple LIFO stack used by the tunnel exploration."""

    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        return None

    def top(self):
        if not self.is_empty():
            return self.items[-1]
        return None

    def is_empty(self):
        return len(self.items) == 0

    def contains(self, item):
        return item in self.items

    def clear(self):
        self.items.clear()

    def to_list(self):
        return list(reversed(self.items))


class Tunnel:
    """Represents one tunnel in the mine."""

    def __init__(self, tunnel_id, name):
        self.tunnel_id = tunnel_id
        self.name = name
        self.neighbors = []
        self.state = "Unvisited"

    def connect_to(self, tunnel):
        self.neighbors.append(tunnel)

    def __str__(self):
        return self.name


class MineRescue:
    """Controls the mine exploration and uses Stack for pending tunnels."""

    def __init__(self):
        self.tunnels = {}
        self.pending_tunnels = Stack()
        self.visited_tunnels = []
        self.current_tunnel = None
        self.exploration_finished = False
        self.create_mine()

    def create_mine(self):
        tunnel_a = Tunnel("A", "Tunnel A - Entrance")
        tunnel_b = Tunnel("B", "Tunnel B - Main Passage")
        tunnel_c = Tunnel("C", "Tunnel C - North Passage")
        tunnel_d = Tunnel("D", "Tunnel D - Dead End")
        tunnel_e = Tunnel("E", "Tunnel E - Rescue Zone")

        tunnel_a.connect_to(tunnel_b)
        tunnel_a.connect_to(tunnel_c)
        tunnel_b.connect_to(tunnel_d)
        tunnel_c.connect_to(tunnel_e)

        self.tunnels = {
            tunnel.tunnel_id: tunnel
            for tunnel in (tunnel_a, tunnel_b, tunnel_c, tunnel_d, tunnel_e)
        }

    def reset(self):
        self.pending_tunnels.clear()
        self.visited_tunnels.clear()
        self.current_tunnel = None
        self.exploration_finished = False
        for tunnel in self.tunnels.values():
            tunnel.state = "Unvisited"

    def push_tunnel(self, tunnel_id):
        tunnel = self.tunnels[tunnel_id]
        if tunnel.state == "Visited" or self.pending_tunnels.contains(tunnel):
            return False, f"{tunnel.name} is already visited or pending."
        self.pending_tunnels.push(tunnel)
        tunnel.state = "Pending"
        return True, f"PUSH -> {tunnel.name} added to the stack."

    def pop_tunnel(self):
        tunnel = self.pending_tunnels.pop()
        if tunnel is None:
            return None, "Stack is empty. No tunnels available."
        return tunnel, f"POP -> {tunnel.name} removed from the stack."

    def top_tunnel(self):
        tunnel = self.pending_tunnels.top()
        if tunnel is None:
            return None, "TOP -> Stack is empty."
        return tunnel, f"TOP -> {tunnel.name} is at the top."

    def explore_step(self):
        if self.exploration_finished:
            return "Exploration is already finished. Press RESET to start again."

        if self.pending_tunnels.is_empty() and not self.visited_tunnels:
            self.push_tunnel("A")
            return "PUSH -> Tunnel A added. Press EXPLORE again to continue."

        tunnel, pop_message = self.pop_tunnel()
        if tunnel is None:
            self.exploration_finished = True
            return "Exploration stopped: Stack is empty. Target not found."

        self.current_tunnel = tunnel
        tunnel.state = "Visited"
        if tunnel not in self.visited_tunnels:
            self.visited_tunnels.append(tunnel)

        if tunnel.tunnel_id == "E":
            self.exploration_finished = True
            return f"{pop_message}\nRescue zone found at {tunnel.name}!"

        unvisited_neighbors = [
            neighbor
            for neighbor in tunnel.neighbors
            if neighbor.state == "Unvisited"
        ]
        if not unvisited_neighbors:
            return f"{pop_message}\nDead end detected at {tunnel.name}."

        for neighbor in reversed(unvisited_neighbors):
            self.push_tunnel(neighbor.tunnel_id)
        pushed_names = ", ".join(neighbor.name for neighbor in unvisited_neighbors)
        return f"{pop_message}\nPUSH -> {pushed_names}."


class MineRescueApp:
    """Tkinter interface for demonstrating the Stack operations."""

    def __init__(self, root):
        self.root = root
        self.root.title("Mine Rescue System")
        self.root.geometry("900x620")
        self.root.minsize(760, 540)
        self.root.configure(bg="#eef2f3")

        self.rescue = MineRescue()
        self.selected_tunnel_id = tk.StringVar(value="A")
        self.status_text = tk.StringVar(value="Ready. Select a tunnel and use PUSH.")
        self.top_text = tk.StringVar(value="TOP")

        self.create_widgets()
        self.refresh_view()

    def create_widgets(self):
        title_frame = tk.Frame(self.root, bg="#173b4d", padx=20, pady=18)
        title_frame.pack(fill="x")
        tk.Label(
            title_frame,
            text="MINE RESCUE SYSTEM",
            font=("Georgia", 24, "bold"),
            fg="white",
            bg="#173b4d",
        ).pack()
        tk.Label(
            title_frame,
            text="Stack-Based Tunnel Exploration | LIFO Demonstration",
            font=("Arial", 11),
            fg="#c8dce2",
            bg="#173b4d",
        ).pack(pady=(5, 0))

        content = tk.Frame(self.root, bg="#eef2f3", padx=24, pady=20)
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(0, weight=1)

        map_frame = tk.LabelFrame(
            content,
            text=" MINE MAP / TUNNELS ",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#173b4d",
            padx=14,
            pady=12,
        )
        map_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        map_frame.rowconfigure(0, weight=1)
        map_frame.columnconfigure(0, weight=1)

        self.map_canvas = tk.Canvas(map_frame, bg="#fbfcfc", highlightthickness=0)
        self.map_canvas.grid(row=0, column=0, sticky="nsew")
        self.map_canvas.bind("<Configure>", lambda event: self.draw_map())
        tk.Label(
            map_frame,
            text="Select a tunnel below, then press PUSH.",
            font=("Arial", 10),
            bg="white",
            fg="#52646b",
        ).grid(row=1, column=0, pady=(10, 0))
        tunnel_menu = tk.OptionMenu(
            map_frame,
            self.selected_tunnel_id,
            *self.rescue.tunnels.keys(),
        )
        tunnel_menu.config(width=18, font=("Arial", 10), bg="#dce8eb", relief="flat")
        tunnel_menu.grid(row=2, column=0, pady=(6, 0))

        stack_frame = tk.LabelFrame(
            content,
            text=" STACK (LIFO) ",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#173b4d",
            padx=14,
            pady=12,
        )
        stack_frame.grid(row=0, column=1, sticky="nsew")
        stack_frame.rowconfigure(1, weight=1)
        stack_frame.columnconfigure(0, weight=1)
        tk.Label(
            stack_frame,
            textvariable=self.top_text,
            font=("Arial", 11, "bold"),
            bg="#f4c95d",
            fg="#173b4d",
            pady=7,
        ).grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.stack_list = tk.Listbox(
            stack_frame,
            font=("Courier New", 11),
            justify="center",
            activestyle="none",
            bg="#f8faf9",
            fg="#173b4d",
            selectbackground="#4d8b91",
            relief="solid",
            borderwidth=1,
        )
        self.stack_list.grid(row=1, column=0, sticky="nsew")
        tk.Label(
            stack_frame,
            text="The top item leaves first.",
            font=("Arial", 10, "italic"),
            bg="white",
            fg="#52646b",
        ).grid(row=2, column=0, pady=(10, 0))

        controls = tk.Frame(self.root, bg="#d7e2e5", padx=24, pady=14)
        controls.pack(fill="x")
        button_specs = [
            ("PUSH", self.push_action, "#4d8b91"),
            ("POP", self.pop_action, "#4d8b91"),
            ("TOP", self.top_action, "#4d8b91"),
            ("EXPLORE", self.explore_action, "#d28b45"),
            ("RESET", self.reset_action, "#68777c"),
        ]
        for label, command, color in button_specs:
            tk.Button(
                controls,
                text=label,
                command=command,
                width=12,
                font=("Arial", 10, "bold"),
                fg="white",
                bg=color,
                activebackground="#173b4d",
                activeforeground="white",
                relief="flat",
                cursor="hand2",
                pady=8,
            ).pack(side="left", expand=True, padx=5)

        status_frame = tk.Frame(self.root, bg="#173b4d", padx=24, pady=12)
        status_frame.pack(fill="x")
        tk.Label(
            status_frame,
            text="STATUS:",
            font=("Arial", 10, "bold"),
            fg="#f4c95d",
            bg="#173b4d",
        ).pack(side="left")
        tk.Label(
            status_frame,
            textvariable=self.status_text,
            font=("Arial", 10),
            justify="left",
            anchor="w",
            fg="white",
            bg="#173b4d",
        ).pack(side="left", fill="x", expand=True, padx=(8, 0))

    def push_action(self):
        success, message = self.rescue.push_tunnel(self.selected_tunnel_id.get())
        self.status_text.set(message)
        if not success:
            messagebox.showinfo("PUSH", message)
        self.refresh_view()

    def pop_action(self):
        tunnel, message = self.rescue.pop_tunnel()
        self.status_text.set(message)
        if tunnel is None:
            messagebox.showinfo("POP", message)
        self.refresh_view()

    def top_action(self):
        tunnel, message = self.rescue.top_tunnel()
        self.status_text.set(message)
        if tunnel is None:
            messagebox.showinfo("TOP", message)
        self.refresh_view()

    def explore_action(self):
        self.status_text.set(self.rescue.explore_step())
        self.refresh_view()

    def reset_action(self):
        self.rescue.reset()
        self.selected_tunnel_id.set("A")
        self.status_text.set("Simulation reset. Select a tunnel or press EXPLORE.")
        self.refresh_view()

    def refresh_view(self):
        self.stack_list.delete(0, tk.END)
        stack_items = self.rescue.pending_tunnels.to_list()
        for tunnel in stack_items:
            self.stack_list.insert(tk.END, tunnel.name)
        self.top_text.set("TOP  |  " + (stack_items[0].name if stack_items else "Stack is empty"))
        self.draw_map()

    def draw_map(self):
        if not hasattr(self, "map_canvas"):
            return
        self.map_canvas.delete("all")
        width = max(self.map_canvas.winfo_width(), 360)
        positions = {
            "A": (width * 0.50, 55),
            "B": (width * 0.28, 145),
            "C": (width * 0.72, 145),
            "D": (width * 0.28, 245),
            "E": (width * 0.72, 245),
        }
        for tunnel in self.rescue.tunnels.values():
            start_x, start_y = positions[tunnel.tunnel_id]
            for neighbor in tunnel.neighbors:
                end_x, end_y = positions[neighbor.tunnel_id]
                self.map_canvas.create_line(
                    start_x, start_y + 22, end_x, end_y - 22,
                    fill="#9aabb0", width=2,
                )
        for tunnel in self.rescue.tunnels.values():
            x, y = positions[tunnel.tunnel_id]
            color = {
                "Unvisited": "#dce8eb",
                "Pending": "#f4c95d",
                "Visited": "#8fc4b8",
            }[tunnel.state]
            if self.rescue.current_tunnel is tunnel:
                color = "#d28b45"
            self.map_canvas.create_oval(
                x - 42, y - 22, x + 42, y + 22,
                fill=color, outline="#173b4d", width=2,
            )
            self.map_canvas.create_text(
                x, y - 3, text=f"Tunnel {tunnel.tunnel_id}",
                font=("Arial", 10, "bold"), fill="#173b4d",
            )
            self.map_canvas.create_text(
                x, y + 11, text=tunnel.state,
                font=("Arial", 8), fill="#173b4d",
            )
        self.map_canvas.create_text(
            width / 2, 315,
            text="Orange = current | Yellow = pending | Green = visited",
            font=("Arial", 9), fill="#52646b",
        )


def main():
    root = tk.Tk()
    MineRescueApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
