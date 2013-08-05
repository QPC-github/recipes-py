# Copyright 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from slave import recipe_api

import textwrap

class PythonApi(recipe_api.RecipeApi):
  def __call__(self, name, script, args=None, unbuffered=True, **kwargs):
    """Return a step to run a python script with arguments."""
    cmd = ['python']
    if unbuffered:
      cmd.append('-u')
    cmd.append(script)
    return self.m.step(name, cmd + list(args or []), **kwargs)

  def inline(self, name, program, **kwargs):
    """Run an inline python program as a step.

    Program is output to a temp file and run when this step executes.
    """
    program = textwrap.dedent(program)
    compile(program, '<string>', 'exec', dont_inherit=1)

    @recipe_api.wrap_followup(kwargs)
    def inline_followup(step_result):
      step_result.presentation.logs['python.inline'] = program.splitlines()

    return self(name, recipe_api.InputDataPlaceholder(program, '.py'),
                followup_fn=inline_followup, **kwargs)
