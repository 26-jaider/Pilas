class Stack:
    """Basic LIFO stack."""

    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if self.is_empty():
            return None
        return self.items.pop()

    def top(self):
        if self.is_empty():
            return None
        return self.items[-1]

    def is_empty(self):
        return len(self.items) == 0

    def contains(self, item):
        return item in self.items

    def clear(self):
        self.items.clear()

    def show(self):
        return list(reversed(self.items))


class Tunnel:
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
    def __init__(self):
        self.tunnels = {}
        self.stack = Stack()
        self.visited = []
        self.current_tunnel = None
        self.finished = False
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

        for tunnel in (tunnel_a, tunnel_b, tunnel_c, tunnel_d, tunnel_e):
            self.tunnels[tunnel.tunnel_id] = tunnel

    def reset(self):
        self.stack.clear()
        self.visited.clear()
        self.current_tunnel = None
        self.finished = False
        for tunnel in self.tunnels.values():
            tunnel.state = "Unvisited"

    def push_tunnel(self, tunnel_id):
        tunnel = self.tunnels.get(tunnel_id)
        if tunnel is None:
            return "Tunnel does not exist. Use A, B, C, D or E."
        if tunnel.state == "Visited" or self.stack.contains(tunnel):
            return f"{tunnel.name} is already visited or pending."

        self.stack.push(tunnel)
        tunnel.state = "Pending"
        return f"PUSH -> {tunnel.name}"

    def pop_tunnel(self):
        tunnel = self.stack.pop()
        if tunnel is None:
            return "POP -> Stack is empty."
        tunnel.state = "Visited"
        return f"POP -> {tunnel.name}"

    def top_tunnel(self):
        tunnel = self.stack.top()
        if tunnel is None:
            return "TOP -> Stack is empty."
        return f"TOP -> {tunnel.name} (not removed)"

    def explore_step(self):
        if self.finished:
            return "Exploration finished. Use RESET to start again."

        if self.stack.is_empty() and not self.visited:
            return self.push_tunnel("A")

        tunnel = self.stack.pop()
        if tunnel is None:
            self.finished = True
            return "Stack is empty. The rescue zone was not found."

        tunnel.state = "Visited"
        self.current_tunnel = tunnel
        self.visited.append(tunnel)
        message = f"POP -> {tunnel.name}"

        if tunnel.tunnel_id == "E":
            self.finished = True
            return message + "\nRescue zone found!"

        new_tunnels = [
            neighbor
            for neighbor in tunnel.neighbors
            if neighbor.state == "Unvisited"
        ]
        if not new_tunnels:
            return message + "\nDead end detected."

        for neighbor in reversed(new_tunnels):
            self.stack.push(neighbor)
            neighbor.state = "Pending"
        names = ", ".join(neighbor.name for neighbor in new_tunnels)
        return message + "\nPUSH -> " + names

    def show_stack(self):
        print("\nSTACK (TOP -> BOTTOM)")
        if self.stack.is_empty():
            print("[Stack is empty]")
            return
        for tunnel in self.stack.show():
            print(f"| {tunnel.name} |")
        print("---------")

    def show_tunnels(self):
        print("\nTUNNELS")
        for tunnel in self.tunnels.values():
            neighbors = ", ".join(neighbor.tunnel_id for neighbor in tunnel.neighbors)
            print(f"{tunnel.tunnel_id}: {tunnel.name} -> {neighbors or 'No exit'}")


def print_menu():
    print("\n" + "=" * 45)
    print("MINE RESCUE SYSTEM")
    print("Stack-Based Tunnel Exploration")
    print("=" * 45)
    print("1. PUSH a tunnel")
    print("2. POP the top tunnel")
    print("3. TOP tunnel")
    print("4. EXPLORE one step")
    print("5. RESET simulation")
    print("6. Show tunnels")
    print("0. EXIT")


def main():
    rescue = MineRescue()
    print("Academic demonstration of Stack and LIFO")

    while True:
        print_menu()
        rescue.show_stack()
        option = input("Choose an option: ").strip()

        if option == "1":
            tunnel_id = input("Tunnel ID (A-E): ").strip().upper()
            print(rescue.push_tunnel(tunnel_id))
        elif option == "2":
            print(rescue.pop_tunnel())
        elif option == "3":
            print(rescue.top_tunnel())
        elif option == "4":
            print(rescue.explore_step())
        elif option == "5":
            rescue.reset()
            print("Simulation reset.")
        elif option == "6":
            rescue.show_tunnels()
        elif option == "0":
            print("Program finished.")
            break
        else:
            print("Invalid option. Choose a number from 0 to 6.")


if __name__ == "__main__":
    main()
