import yaml

from policies import Policy
from config.helpers import serialize_func, deserialize_func


def default_production_limit(time, dt, *args):
    """
    Production limit method stub
    :param time: current simulation time
    :param dt: time step for which production limits are calculated
    :param args: additional arguments
    :return: 0
    """
    return 0


def default_needs(time, dt, *args):
    """
    Needs method stub
    :param time: current simulation time
    :param dt: time step for which production limits are calculated
    :param args: additional arguments
    :return: 0
    """
    return 0


def default_income(time, dt, *args):
    """
    Income method stub
    :param time: current simulation time
    :param dt: time step for which production limits are calculated
    :param args: additional arguments
    :return: 0
    """
    return 0


DEFAULT_NUMERICAL_PARAM = 0
DEFAULT_FUN_ARGS = []


class AgentConfig(object):
    """
    Class with agent configuration
    """
    def __init__(self):
        """
        Creates agent configuration with default parameters
        """
        self.initial_resource = DEFAULT_NUMERICAL_PARAM
        self.production_cost = DEFAULT_NUMERICAL_PARAM  # per resource unit
        self.storage_limit = DEFAULT_NUMERICAL_PARAM
        self.utilization_cost = DEFAULT_NUMERICAL_PARAM
        self.needs_satisfaction_timeout = DEFAULT_NUMERICAL_PARAM
        self.needs_satisfaction_cost = DEFAULT_NUMERICAL_PARAM
        self.initial_money = DEFAULT_NUMERICAL_PARAM
        self._production_limit = default_production_limit
        self._production_limit_args = DEFAULT_FUN_ARGS
        self._needs = default_needs
        self._needs_args = DEFAULT_FUN_ARGS
        self._income = default_income
        self._income_args = DEFAULT_FUN_ARGS
        self._policy_builder = Policy
        self._policy_builder_args = []

    def production_limit(self, time, dt):
        """
        Production limit function to be used by agents
        :param time: current time
        :param dt: time step for which the production limit is calculated
        :return: production limit
        """
        return self._production_limit(time, dt, *self._production_limit_args)

    def needs(self, time, dt):
        """
        Needs function to be used by agents
        :param time: current time
        :param dt: time step for which the production limit is calculated
        :return: the needs
        """
        return self._needs(time, dt, *self._needs_args)

    def income(self, time, dt):
        """
        Income function to be used by agents
        :param time: current time
        :param dt: time step for which the production limit is calculated
        :return: the income
        """
        return self._income(time, dt, *self._income_args)

    def build_policy(self, agent):
        """
        A function that builds agent policy
        :param agent: the agent
        :return: created policy
        """
        return self._policy_builder(agent, *self._policy_builder_args)

    def save(self, file_name):
        """
        Saves current agent configuration as YAML file

        :param file_name: name of the config file
        :return: None
        """
        with open(file_name, 'w') as f:
            yaml.dump({
                'initial-resource': self.initial_resource,
                'production-cost': self.production_cost,
                'storage-limit': self.storage_limit,
                'utilization-cost': self.utilization_cost,
                'needs-satisfaction-timeout': self.needs_satisfaction_timeout,
                'needs-satisfaction-cost': self.needs_satisfaction_cost,
                'initial-money': self.initial_money,
                'production-limit': serialize_func(self._production_limit, self._production_limit_args),
                'needs': serialize_func(self._needs, self._needs_args),
                'income': serialize_func(self._income, self._income_args),
                'policy_builder': serialize_func(self._policy_builder, self._policy_builder_args),
            }, f)

    def load(self, file_name):
        """
        Loads agent configuration from YAML file

        Missing values will be filled with default values

        :param file_name: name of the config file
        :return: None
        """
        with open(file_name, 'r') as f:
            yaml_file = yaml.safe_load(f)
            if yaml_file is None:
                yaml_file = {}

            self.initial_resource = yaml_file.get('initial-resource', DEFAULT_NUMERICAL_PARAM)
            self.production_cost = yaml_file.get('production-cost', DEFAULT_NUMERICAL_PARAM)
            self.storage_limit = yaml_file.get('storage-limit', DEFAULT_NUMERICAL_PARAM)
            self.utilization_cost = yaml_file.get('utilization-cost', DEFAULT_NUMERICAL_PARAM)
            self.needs_satisfaction_timeout = yaml_file.get('needs-satisfaction-timeout', DEFAULT_NUMERICAL_PARAM)
            self.needs_satisfaction_cost = yaml_file.get('needs-satisfaction-cost', DEFAULT_NUMERICAL_PARAM)
            self.initial_money = yaml_file.get('initial-money', DEFAULT_NUMERICAL_PARAM)

            self._production_limit, self._production_limit_args = deserialize_func(
                yaml_file.get('production_limit', None),
                default_production_limit,
                DEFAULT_FUN_ARGS
            )

            self._needs, self._needs_args = deserialize_func(
                yaml_file.get('needs', None),
                default_production_limit,
                DEFAULT_FUN_ARGS
            )

            self._income, self._income_args= deserialize_func(
                yaml_file.get('income', None),
                default_production_limit,
                DEFAULT_FUN_ARGS
            )

            self._policy_builder, self._policy_builder_args = deserialize_func(
                yaml_file.get('policy_builder', None),
                Policy,
                DEFAULT_FUN_ARGS
            )

    def get_policy_name(self):
        """
        :return: policy as string
        """
        return f'{self._policy_builder.__module__}.' \
               f'{self._policy_builder.__name__}' \
               f'({", ".join(map(str, self._policy_builder_args))})'


def load_agent_config(file_name):
    """
    Loads agent config from YAML file

    :param file_name: the name of the config file
    :return: loaded configuration
    """
    config = AgentConfig()
    config.load(file_name)

    return config
