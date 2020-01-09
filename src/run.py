from main_cli import main_loop
from agentNet.agent_net import AgentNet
from config.agent_config import load_agent_config
from agents.Agent import Agent
import logger

import argparse


global_agents = None


def create_agent(agent_id, connections, config_filename):
    """
    load config fromm file and create agent
    :param agent_id: agent id
    :param connections: connections
    :param config_filename: name of the file with config
    :return: created agent
    """
    config = load_agent_config(config_filename)
    return Agent(agent_id, connections, config).stop()


def initialize(network_config):
    """
    initializes system

    :param network_config: object with network and agents configuration
    """
    global global_agents
    global_agents = {n: None for n in network_config.network.nodes()}

    for n in network_config.network.nodes():
        global_agents[n] = create_agent(n, network_config.network.edges(n), network_config.agents_policies[n])

    for a in global_agents.values():
        a.start()

    logger.logger.log(logger.EVENT_SYSTEM_INITIALIZED)


def run(config_filename, log_filename):
    log_file = open(log_filename, 'w') if log_filename else None
    logger.initialize_default_logger(log_file)

    network_config = AgentNet()
    network_config.load_network(config_filename)

    initialize(network_config)
    main_loop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--config', action='store', type=str, required=True)
    parser.add_argument('--log', action='store', type=str, default=None, required=False)

    args = parser.parse_args()

    run(args.config, args.log)
