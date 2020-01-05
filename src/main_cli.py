def initialize():
    """initializes system"""
    pass


def shutdown():
    """turns the system off"""
    return False


def show_log():
    """Shows log of the system"""
    pass


def kill_agent(agents):
    """ kills the specified agent"""
    for agent in agents:
        print("you killed: " + agent)


def restore_agent(agents):
    """ restores the specified agent"""

    for agent in agents:
        print("you restored: "+agent)
        # agents.append(int(arg))


def main_loop():
    run = True
    while run:
        initialize()
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


if __name__ == "__main__":
    main_loop()

