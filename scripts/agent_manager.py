from uuid import uuid4 as uuid

import new_bing as nbing

agents = {}  # key, (agent, task, full_message_history)


def create_agent(task, prompt):
    """Create a new agent and return its key"""
    global next_key
    global agents

    # Start a new agent
    key = str(uuid())
    agent = nbing.new_bot()
    agent_reply = nbing.ask_question(prompt, agent)

    # Update full message history
    history = [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": agent_reply}
    ]

    # Update agent dict
    agents[key] = (agent, task, history)

    return key, agent_reply


def message_agent(key, message):
    """Send a message to an agent and return its response"""
    global agents

    agent, _, history = agents[key]

    # Add user message to message history before sending to agent
    history.append({"role": "user", "content": message})

    # Message the agent
    agent_reply = nbing.ask_question(message, agent)

    # Update full message history
    history.append({"role": "assistant", "content": agent_reply})

    return agent_reply


def has_agent(key):
    """Return if there exists a agent with key"""
    return isinstance(key, str) and key in agents


def list_agents():
    """Return a list of all agents"""
    global agents

    # Return a list of agent keys and their tasks
    return [(key, task) for key, (_, task, _) in agents.items()]


def delete_agent(key):
    """Delete an agent and return True if successful, False otherwise"""
    global agents

    try:
        nbing.close_bot(agents[key][0])
        del agents[key]
        return True
    except KeyError:
        return False
