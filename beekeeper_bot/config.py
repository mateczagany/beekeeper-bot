import yaml

with open('config.yml', 'r') as config_file:
    CONFIG = yaml.load(config_file, Loader=yaml.BaseLoader)
