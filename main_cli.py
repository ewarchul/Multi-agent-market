import click

# potrzebne funkcje:
# 1. odpalenie programu
# 2. zabicie określonego agenta
# 3. podniesienie agenta
# 4. zwrócenie logu


@click.group()
def main_cli():
    """Command line tool for deploingmultiagent system"""
    pass


@click.command(help="initialising the system")
def startSystem():
    print("multi agent system started")


@click.command(help="simulating agent failure")
@click.option('--agent_id', default=1, help="podaj id agenta do wyłączenia")
def killAgent(agent_id):
    print("zabiles agenta "+str(agent_id))


@click.command(help="simulating agent restoration")
@click.option('--agent_id', default=1, help="podaj id agenta do przywrócenia")
def restoreAgent(agent_id):
    print("agent with id {} restored".format(agent_id))


@click.command(help="showing saved logs")
def showLog():
    print("log")


main_cli.add_command(showLog)
main_cli.add_command(restoreAgent)
main_cli.add_command(startSystem)
main_cli.add_command(killAgent)


if __name__ == "__main__":
    main_cli()
