import importlib

import yaml


def default_production_limit(time, dt, *args):
    return 0


def default_needs(time, dt, *args):
    return 0


def default_income(time, dt, *args):
    return 0


def get_func(module, name):
    m = importlib.import_module(module)
    f = getattr(m, name)
    return f


DEFAULT_NUMERICAL_PARAM = 0
DEFAULT_FUN_ARGS = []


class AgentConfig(object):
    def __init__(self):
        self.initial_resource = DEFAULT_NUMERICAL_PARAM
        self.production_cost = DEFAULT_NUMERICAL_PARAM  # per resource unit
        self.storage_limit = DEFAULT_NUMERICAL_PARAM
        self.utilization_cost = DEFAULT_NUMERICAL_PARAM
        self.needs_satisfaction_timeout = DEFAULT_NUMERICAL_PARAM
        self.initial_money = DEFAULT_NUMERICAL_PARAM
        self._production_limit = default_production_limit
        self._production_limit_args = DEFAULT_FUN_ARGS
        self._needs = default_needs
        self._needs_args = DEFAULT_FUN_ARGS
        self._income = default_income
        self._income_args = DEFAULT_FUN_ARGS

    def production_limit(self, time, dt):
        return self._production_limit(time, dt, *self._production_limit_args)

    def needs(self, time, dt):
        return self._needs(time, dt, *self._needs_args)

    def income(self, time, dt):
        return self._income(time, dt, *self._income_args)

    def save(self, file_name):
        with open(file_name, 'w') as f:
            yaml.dump({
                'initial-resource': self.initial_resource,
                'production-cost': self.production_cost,
                'storage-limit': self.storage_limit,
                'utilization-cost': self.utilization_cost,
                'needs-satisfaction-timeout': self.needs_satisfaction_timeout,
                'initial-money': self.initial_money,
                'production-limit': {
                    'module': self._production_limit.__module__,
                    'fun': self._production_limit.__name__,
                    'args': self._production_limit_args
                },
                'needs': {
                    'module': self._needs.__module__,
                    'fun': self._needs.__name__,
                    'args': self._needs_args
                },
                'income': {
                    'module': self._income.__module__,
                    'fun': self._income.__name__,
                    'args': self._income_args
                }
            }, f)

    def load(self, file_name):
        with open(file_name, 'r') as f:
            yaml_file = yaml.load(f)

            self.initial_resource = yaml_file.get('initial-resource', DEFAULT_NUMERICAL_PARAM)
            self.production_cost = yaml_file.get('production-cost', DEFAULT_NUMERICAL_PARAM)
            self.storage_limit = yaml_file.get('storage-limit', DEFAULT_NUMERICAL_PARAM)
            self.utilization_cost = yaml_file.get('utilization-cost', DEFAULT_NUMERICAL_PARAM)
            self.needs_satisfaction_timeout = yaml_file.get('needs-satisfaction-timeout', DEFAULT_NUMERICAL_PARAM)
            self.initial_money = yaml_file.get('initial-money', DEFAULT_NUMERICAL_PARAM)

            production_limit = yaml_file.get('production_limit', None)
            if production_limit:
                self._production_limit = get_func(
                    production_limit.get('module'),
                    production_limit.get('fun')
                )
                self._production_limit_args = production_limit.get('args', DEFAULT_FUN_ARGS)
            else:
                self._production_limit = default_production_limit
                self._production_limit_args = DEFAULT_FUN_ARGS

            needs = yaml_file.get('production_limit', None)
            if needs:
                self._needs = get_func(
                    needs.get('module'),
                    needs.get('fun')
                )
                self._needs_args = needs.get('args', DEFAULT_FUN_ARGS)
            else:
                self._needs = default_needs
                self._needs_args = DEFAULT_FUN_ARGS

            income = yaml_file.get('production_limit', None)
            if income:
                self._income = get_func(
                    income.get('module'),
                    income.get('fun')
                )
                self._income_args = income.get('args', DEFAULT_FUN_ARGS)
            else:
                self._income = default_income
                self._income_args = DEFAULT_FUN_ARGS


def load_agent_config(file_name):
    config = AgentConfig()
    config.load(file_name)

    return config
