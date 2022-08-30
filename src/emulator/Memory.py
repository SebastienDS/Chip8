class Memory:
    def __init__(self, memory_size: int):
        self.memory = [0] * memory_size
    
    def __str__(self) -> str:
        return f"Memory({self.memory})"

    def get(self, position: int) -> int:
        return self.memory[position]

    def set(self, position: int, value: int):
        self.memory[position] = value
        