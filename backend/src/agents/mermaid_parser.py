"""
Mermaid Diagram Parser

This module provides functionality to parse mermaid diagram strings and extract
nodes and connections information.
"""

import re
from typing import Dict, List, Optional


def parse_mermaid_diagram(mermaid_string: str) -> Dict[str, List[Dict[str, str]]]:
    """
    Parse a mermaid diagram string and extract nodes and connections.

    This parser is designed to be robust and will silently skip invalid nodes
    or malformed entries without throwing errors.

    Args:
        mermaid_string: A string containing a mermaid diagram with the format:
            graph TB
                subgraph "Phase 1"
                    NODE_VAR1[<title>...</title><description>...</description>]
                end
                NODE_VAR1 --> NODE_VAR2

    Returns:
        A dictionary with two keys:
            - "nodes": List of node dictionaries with id, title, description, and phase
            - "connections": List of connection dictionaries with from and to node ids

    Example:
        >>> diagram = '''
        ... graph TB
        ...     subgraph "Phase 1"
        ...         NODE1[<title>First</title><description>First node</description>]
        ...     end
        ... '''
        >>> result = parse_mermaid_diagram(diagram)
        >>> len(result["nodes"])
        1
    """
    nodes = []
    connections = []
    current_phase = None

    # Handle empty or None input
    if not mermaid_string:
        return {"nodes": nodes, "connections": connections}

    try:
        # Split the diagram into lines
        lines = mermaid_string.strip().split('\n')
    except Exception:
        # If splitting fails, return empty result
        return {"nodes": nodes, "connections": connections}

    for line in lines:
        try:
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Check for subgraph to identify phase
            subgraph_match = re.search(r'subgraph\s+"([^"]+)"', line)
            if subgraph_match:
                current_phase = subgraph_match.group(1)
                continue

            # Check for end of subgraph
            if line == "end":
                # Keep the current_phase as nodes can be defined after subgraph
                continue

            # Parse node definition
            # Pattern: NODE_ID[<title>...</title><description>...</description>]
            node_match = re.search(
                r'(\w+)\[<title>([^<]*)</title><description>([^<]*)</description>\]',
                line
            )
            if node_match:
                node_id = node_match.group(1)
                title = node_match.group(2)
                description = node_match.group(3)

                nodes.append({
                    "id": node_id,
                    "title": title,
                    "description": description,
                    "phase": current_phase if current_phase else "Unknown"
                })
                continue

            # Parse connection
            # Pattern: NODE_ID1 --> NODE_ID2
            connection_match = re.search(r'(\w+)\s*-->\s*(\w+)', line)
            if connection_match:
                from_node = connection_match.group(1)
                to_node = connection_match.group(2)

                connections.append({
                    "from": from_node,
                    "to": to_node
                })
                continue

        except Exception:
            # Silently skip any line that causes an error
            continue

    return {
        "nodes": nodes,
        "connections": connections
    }


def main() -> None:
    """
    Demonstration of the mermaid parser with a sample diagram.
    """
    sample_mermaid = """
graph TB
    subgraph "Phase 1"
        NODE_VAR1[<title>Initial Planning</title><description>Define project scope and objectives</description>]
        NODE_VAR2[<title>Research</title><description>Gather requirements and research solutions</description>]
    end
    subgraph "Phase 2"
        NODE_VAR3[<title>Design</title><description>Create system architecture and design</description>]
        NODE_VAR4[<title>Implementation</title><description>Develop the solution</description>]
    end
    subgraph "Phase 3"
        NODE_VAR5[<title>Testing</title><description>Test and validate the solution</description>]
        NODE_VAR6[<title>Deployment</title><description>Deploy to production</description>]
    end
    NODE_VAR1 --> NODE_VAR2
    NODE_VAR2 --> NODE_VAR3
    NODE_VAR3 --> NODE_VAR4
    NODE_VAR4 --> NODE_VAR5
    NODE_VAR5 --> NODE_VAR6
"""

    result = parse_mermaid_diagram(sample_mermaid)

    print("=== Mermaid Diagram Parser Demo ===\n")

    print("Nodes:")
    for node in result["nodes"]:
        print(f"  - ID: {node['id']}")
        print(f"    Title: {node['title']}")
        print(f"    Description: {node['description']}")
        print(f"    Phase: {node['phase']}")
        print()

    print("Connections:")
    for conn in result["connections"]:
        print(f"  - {conn['from']} --> {conn['to']}")

    print(f"\nTotal Nodes: {len(result['nodes'])}")
    print(f"Total Connections: {len(result['connections'])}")


if __name__ == "__main__":
    main()
