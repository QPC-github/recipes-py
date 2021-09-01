# Copyright 2017 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

PYTHON_VERSION_COMPATIBILITY = 'PY2+3'

DEPS = [
  'json',
  'path',
  'platform',
  'raw_io',
  'runtime',
  'step',
  'uuid',
]

from recipe_engine.recipe_api import Property
from recipe_engine.config import ConfigGroup, Dict, Single

from PB.recipe_modules.recipe_engine.buildbucket import properties

PROPERTIES = properties.InputProperties
# Deprecated.
GLOBAL_PROPERTIES = properties.LegacyInputProperties
