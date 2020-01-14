from spade import quit_spade

import logger
import threading
import tkinter


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


def run_command(command, agents):
    command_list = command.split(" ")
    if command_list[0] == "kill":
        kill_agent(agents, command_list[1:])
    elif command_list[0] == "shutdown":
        return False
    elif command_list[0] == "restore":
        restore_agent(agents, command_list[1:])
    elif command_list[0] == "log":
        show_log()
    return True


def run_ui(agents):
    def runner():
        tk = tkinter.Tk()
        l = tkinter.Label(tk, text='Enter command...')
        l.pack()
        e = tkinter.Entry(tk)
        e.pack(fill="x")

        tk.geometry("300x63")

        def on_click():
            if not run_command(e.get(), agents):
                tk.destroy()
            else:
                e.delete(0, 'end')

        b = tkinter.Button(tk, text='Run', command=on_click, default="active")
        b.pack(fill="both")
        tk.mainloop()

        shutdown()

    threading.Thread(target=runner, daemon=True).start()
