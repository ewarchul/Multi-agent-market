from main_cli import main_loop
from agentNet.agent_net import AgentNet
from config.agent_config import load_agent_config
from agents.Agent import Agent
from agentPlot.display_graph import real_time_plot

import logging

import logger

import argparse
import os, time


def disable_spade_warnings():
    logging.getLogger('spade.Agent').setLevel(logging.ERROR)


def create_agent(agent_id, connections, config_filename):
    """
    load config fromm file and create agent
    :param agent_id: agent id
    :param connections: connections
    :param config_filename: name of the file with config
    :return: created agent
    """
    config = load_agent_config(config_filename)
    return Agent(agent_id, connections, config)


def get_agent_config_filename(agent_config_filename, network_config_filename):
    if os.path.isabs(agent_config_filename):
        return agent_config_filename

    return os.path.join(os.path.dirname(network_config_filename), agent_config_filename)


def visualisation(graph, logger):
    """
    Starts visualisation of the simulation
    :param graph: agent_net graph
    :param logger: system logger
    """
    global eventDict
    eventDict = {}

    def handler(event, **kwargs):
        # print("hello")
        if event in eventDict.keys():
            eventDict[event].append(kwargs)
        else:
            eventDict[event] = []
            eventDict[event].append(kwargs)
    logger.logger.register_event_handler(logger.EVENT_AGENT_STATE_CHANGED, handler)
    logger.logger.register_event_handler(logger.EVENT_MESSAGE_SENT, handler)
    time.sleep(10)
    real_time_plot(graph, eventDict)


def initialize(network_config, network_config_filename):
    """
    initializes system

    :param network_config: object with network and agents configuration
    :param network_config_filename: name of file with network config,
        to get agent config paths as relative to it
    :return: created agents
    """
    agents = {n: None for n in network_config.network.nodes()}

    for n in network_config.network.nodes():
        agent_config = get_agent_config_filename(network_config.agents_policies[n], network_config_filename)
        agents[n] = create_agent(n, network_config.network.edges(n), agent_config)

    for a in agents.values():
        a.start()

    logger.logger.log(logger.EVENT_SYSTEM_INITIALIZED)

    return agents


def run(config_filename, log_filename, vis, log_to_stderr):
    log_file = open(log_filename, 'w') if log_filename else None
    logger.initialize_default_logger(log_file, use_stderr=log_to_stderr)

    disable_spade_warnings()
    
    network_config = AgentNet()
    network_config.load_network(config_filename)

    agents = initialize(network_config, config_filename)
    if vis:
        visualisation(network_config, logger)
    main_loop(agents)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--config', action='store', type=str, required=True)
    parser.add_argument('--log', action='store', type=str, default=None, required=False)
    parser.add_argument('--log_stream', action='store', type=str, choices=('out', 'err'), default='err')
    parser.add_argument('--vis', action='store', type=bool, default=False)

    args = parser.parse_args()

    run(args.config, args.log, args.vis, args.log_stream == 'err')
