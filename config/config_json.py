import json
import os


def get_config_json(key, default=None, return_path=False):
    for env in os.environ.get('CONFIG_PATH', '').split(os.pathsep):
        path = os.path.join(env, 'config.json')
        if os.path.exists(path):
            try:
                dict = {}
                with open(path) as config_json:
                    dict = json.load(config_json)
                if dict[key]:
                    if return_path:
                        return os.path.join(env, dict[key])
                    return dict[key]
            except:
                pass

    return os.environ.get(key, default)
