class Agent:
    def __init__(self, name: str, purpose: str):
        self.name = name
        self.purpose = purpose

    def run(self):
        print(f"Running agent {self.name}: {self.purpose}")
