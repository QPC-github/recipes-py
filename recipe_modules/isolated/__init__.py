DEPS = [
    'properties',
]

from recipe_engine.recipe_api import Property
from recipe_engine.config import ConfigGroup, Single

PROPERTIES = {
    '$recipe_engine/isolated': Property(
        help='Properties specifically for the isolated module',
        param_name='isolated_properties',
        kind=ConfigGroup(
          server=Single(str),
        ),
        default={},
      ),
}
