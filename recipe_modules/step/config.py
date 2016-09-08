# Copyright 2013 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import collections

from recipe_engine.config import (config_item_context, ConfigGroup, ConfigList,
                                  Dict, Single, Set, List)
from recipe_engine.config_types import Path
from recipe_engine.util import Placeholder


def BaseConfig(**_kwargs):
  def render_cmd(lst):
    return [(x if isinstance(x, Placeholder) else str(x)) for x in lst]

  return ConfigGroup(
    # For compatibility with buildbot, the step name must be ascii, which is why
    # this is a 'str' and not a 'basestring'.
    name = Single(str),
    cmd = List(inner_type=(int,long,basestring,Path,Placeholder),
               jsonish_fn=render_cmd),
    timeout = Single(int, required=False),

    # optional
    env = Dict(item_fn=lambda (k, v): (k, v if v is None else str(v)),
               value_type=(basestring,int,Path,type(None))),
    cwd = Single(Path, jsonish_fn=str, required=True),

    stdout = Single(Placeholder, required=False),
    stderr = Single(Placeholder, required=False),
    stdin = Single(Placeholder, required=False),

    allow_subannotations = Single(bool, required=False),

    trigger_specs = ConfigList(
        lambda: ConfigGroup(
            bucket=Single(basestring),
            builder_name=Single(basestring),
            properties=Dict(value_type=object),
            buildbot_changes=List(dict),
            tags=List(basestring),
        ),
    ),

    step_test_data = Single(collections.Callable, required=False),

    ok_ret = Set(int),
    infra_step = Single(bool, required=False),
    step_nest_level = Single(int, required=False),
  )


config_ctx = config_item_context(BaseConfig)

@config_ctx()
def test(c):  # pragma: no cover
  c.name = 'test'
  c.cmd = [Path('[CHECKOUT]', 'build', 'tools', 'cool_script.py')]
