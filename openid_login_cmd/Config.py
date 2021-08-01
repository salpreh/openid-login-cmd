from pathlib import Path
import shutil

import yaml
from clinlog import get_logger


class Config:

    DEFAULT_FOLDER = '.openid-cmd'
    DEFAULT_FILENAME = 'config.yml'
    DEFAULT_FILE = 'config/default.yml'

    def __init__(self, config_path:Path=None):
        if not config_path:
            config_path = self._get_default_config_path()
        self._config_path = config_path

    def load_config(self):
        config = {} # type: dict
        with open(self._config_path.resolve(), 'r', encoding='utf-8') as f:
            try:
                config = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise RuntimeError('Unable to load config') from e

        for k, v in config.items():
            setattr(self, k, v)

    def config_file_exists(self):
        return self._config_path.exists()

    def create_default_config(self):
        default_config = Path(__file__).parent / self.DEFAULT_FILE
        self._get_default_config_path().parent.mkdir()

        shutil.copy2(default_config.resolve(), self._get_default_config_path().resolve())

    def _get_default_config_path(self) -> Path:
        return Path.home() / self.DEFAULT_FOLDER / self.DEFAULT_FILENAME