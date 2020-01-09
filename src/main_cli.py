from run import global_agents
import logger


def shutdown():
    """turns the system off"""
    for a in global_agents.values():
        a.stop()

    logger.logger.log(logger.EVENT_SYSTEM_CLOSE)

    return False


def show_log():
    """Shows log of the system"""
    pass


def kill_agent(agents):
    """ kills the specified agent"""
    for agent in agents:
        print("you killed: " + agent)
        agent_id = int(agent)
        global_agents[agent_id].pause()


def restore_agent(agents):
    """ restores the specified agent"""

    for agent in agents:
        print("you restored: "+agent)
        agent_id = int(agent)
        global_agents[agent_id].restore()


def main_loop():
    run = True
    while run:
        command = input("waiting for command ...\n")
        command_list = command.split(" ")
        print(command_list)
        if command_list[0] == "kill":
            kill_agent(command_list[1:])
        elif command_list[0] == "shutdown":
            run = shutdown()
        elif command_list[0] == "restore":
            restore_agent(command_list[1:])
        elif command_list[0] == "log":
            show_log()
        else:
            pass



