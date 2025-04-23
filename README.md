# Norm-based Plan in Concepts (NPC)

NPC is a system designed to enhance AI foundation models by explicitly separating and enforcing norms and task settings. It provides a structured approach to ensure AI systems operate within defined norms while maintaining flexibility for specific task scenarios.

## Core Features

- **Explicit Norm Encoding**: Structurally enforced norms for increased robustness and verifiability
- **Dynamic Adaptability**: Norm graphs can be updated without retraining
- **Collaborative Governance**: Combines expert domain knowledge with AI scalability

## Architecture

The NPC system consists of four core components:

1. **Concepts**: Fundamental building blocks representing different types of conceptual entities
2. **References**: Tensor-like data structures that organize and store concept instances
3. **Inferences**: Define and manage relationships between concepts
4. **Plan**: The final executable object that combines concepts and inferences

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Xin-Guan-HolisticAI/npc_agent.git
cd npc_agent
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

[Usage instructions will be added here]

## Project Structure

- `core/`: Contains the main implementation of the NPC system
- `example/`: Example implementations and use cases
- `example_workflow.md`: Detailed documentation of the system's workflow

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[License information will be added here] 