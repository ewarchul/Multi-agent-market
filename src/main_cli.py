from spade import quit_spade

import logger


def shutdown():
    """
    turns the system off
    """
    quit_spade()

    logger.logger.log(logger.EVENT_SYSTEM_CLOSE)

    return False


def show_log():
    """Shows log of the system"""
    pass


def kill_agent(all_agents, agents):
    """
    kills the specified agent

    :param all_agents: A dict of all agents in a system by id
    :param agents: agents to kill
    """
    for agent in agents:
        print("you killed: " + agent)
        agent_id = int(agent)
        all_agents[agent_id].pause()


def restore_agent(all_agents, agents):
    """
    restores the specified agent

    :param all_agents: A dict of all agents in a system by id
    :param agents: agents to restore
    """

    for agent in agents:
        print("you restored: "+agent)
        agent_id = int(agent)
        all_agents[agent_id].restore()


def main_loop(agents):
    run = True
    while run:
        command = input("waiting for command ...\n")
        command_list = command.split(" ")
        print(command_list)
        if command_list[0] == "kill":
            kill_agent(agents, command_list[1:])
        elif command_list[0] == "shutdown":
            run = shutdown()
        elif command_list[0] == "restore":
            restore_agent(agents, command_list[1:])
        elif command_list[0] == "log":
            show_log()
        else:
            pass



