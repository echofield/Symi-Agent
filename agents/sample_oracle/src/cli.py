import typer
from .agent import OracleAgent

app = typer.Typer()

@app.command()
def run(limit: int = 10):
    agent = OracleAgent({})
    result = agent.run(limit)
    print(result)

if __name__ == "__main__":
    app()
