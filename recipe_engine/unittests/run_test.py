#!/usr/bin/env python
# Copyright 2014 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import json
import os
import re
import subprocess
import unittest
import tempfile
import time

import test_env
from test_env import BASE_DIR

import recipe_engine.run
import recipe_engine.step_runner
from recipe_engine import requests_ssl

class RunTest(unittest.TestCase):
  def _run_cmd(self, recipe, properties=None, engine_args=None):
    script_path = os.path.join(BASE_DIR, 'recipes.py')

    if properties:
      proplist = [ '%s=%s' % (k, json.dumps(v))
                   for k,v in properties.iteritems() ]
    else:
      proplist = []

    eng_args = ['--package', os.path.join(
        BASE_DIR, 'infra', 'config', 'recipes.cfg')]
    if engine_args:
      eng_args.extend(engine_args)

    prev_ignore = os.environ.pop(requests_ssl.ENV_VAR_IGNORE, '0')
    os.environ[requests_ssl.ENV_VAR_IGNORE] = '1'
    try:
      return (
          ['python', script_path] + eng_args + ['run', recipe] + proplist)
    finally:
      os.environ[requests_ssl.ENV_VAR_IGNORE] = prev_ignore

  def _test_recipe(self, recipe, properties=None):
    exit_code = subprocess.call(
        self._run_cmd(recipe, properties), stdout=subprocess.PIPE)
    self.assertEqual(0, exit_code, '%d != %d when testing %s' % (
        0, exit_code, recipe))

  def test_examples(self):
    tests = [
      ['step:example'],
      ['path:example'],
      ['raw_io:example'],
      ['python:example'],
      ['json:example'],
      ['uuid:example'],

      ['engine_tests/depend_on/top', {'to_pass': 42}],
      ['engine_tests/functools_partial'],
    ]
    for test in tests:
      self._test_recipe(*test)

  def test_bad_subprocess(self):
    now = time.time()
    self._test_recipe('engine_tests/bad_subprocess')
    after = time.time()

    # Test has a daemon that holds on to stdout for 30s, but the daemon's parent
    # process (e.g. the one that recipe engine actually runs) quits immediately.
    # If this takes longer than 5 seconds to run, we consider it failed.
    self.assertLess(after - now, 5)


  def test_nonexistent_command(self):
    subp = subprocess.Popen(
        self._run_cmd('engine_tests/nonexistent_command'),
        stdout=subprocess.PIPE)
    stdout, _ = subp.communicate()
    self.assertRegexpMatches(stdout, '(?m)^@@@STEP_EXCEPTION@@@$')
    self.assertRegexpMatches(stdout, 'OSError')
    self.assertEqual(255, subp.returncode, stdout)

  def test_nonexistent_command_new(self):
    _, path = tempfile.mkstemp('args_pb')
    with open(path, 'w') as f:
      json.dump({
        'engine_flags': {
            'use_result_proto': True
        }
      }, f)

    try:
      subp = subprocess.Popen(
          self._run_cmd(
              'engine_tests/nonexistent_command',
              engine_args=['--operational-args-path', path]),
          stdout=subprocess.PIPE)
      stdout, _ = subp.communicate()

      self.assertRegexpMatches(stdout, '(?m)^@@@STEP_EXCEPTION@@@$')
      self.assertRegexpMatches(stdout, 'OSError')
      self.assertEqual(1, subp.returncode, stdout)
    finally:
      if os.path.exists(path):
        os.unlink(path)

  def test_trigger(self):
    subp = subprocess.Popen(
        self._run_cmd('engine_tests/trigger'),
        stdout=subprocess.PIPE)
    stdout, _ = subp.communicate()
    self.assertEqual(0, subp.returncode)
    m = re.compile(r'^@@@STEP_TRIGGER@(.*)@@@$', re.MULTILINE).search(stdout)
    self.assertTrue(m)
    blob = m.group(1)
    json.loads(blob) # Raises an exception if the blob is not valid json.

  def test_trigger_no_such_command(self):
    """Tests that trigger still happens even if running the command fails."""
    subp = subprocess.Popen(
        self._run_cmd(
            'engine_tests/trigger', properties={'command': ['na-huh']}),
        stdout=subprocess.PIPE)
    stdout, _ = subp.communicate()
    self.assertRegexpMatches(stdout, r'(?m)^@@@STEP_TRIGGER@(.*)@@@$')
    self.assertEqual(255, subp.returncode)

  def test_trigger_no_such_command_new(self):
    """Tests that trigger still happens even if running the command fails."""
    _, path = tempfile.mkstemp('args_pb')
    with open(path, 'w') as f:
      json.dump({
        'engine_flags': {
            'use_result_proto': True
        }
      }, f)

    try:
      subp = subprocess.Popen(
          self._run_cmd(
              'engine_tests/trigger', properties={'command': ['na-huh']},
              engine_args=['--operational-args-path', path]),
          stdout=subprocess.PIPE)
      stdout, _ = subp.communicate()

      self.assertRegexpMatches(stdout, r'(?m)^@@@STEP_TRIGGER@(.*)@@@$')
      self.assertEqual(1, subp.returncode)
    finally:
      if os.path.exists(path):
        os.unlink(path)

  def test_shell_quote(self):
    # For regular-looking commands we shouldn't need any specialness.
    self.assertEqual(
        recipe_engine.step_runner._shell_quote('/usr/bin/python-wrapper.bin'),
        '/usr/bin/python-wrapper.bin')

    STRINGS = [
        'Simple.Command123/run',
        'Command with spaces',
        'Command with "quotes"',
        "I have 'single quotes'",
        'Some \\Esc\ape Seque\nces/',
        u'Unicode makes me \u2609\u203f\u2299',
    ]

    for s in STRINGS:
      quoted = recipe_engine.step_runner._shell_quote(s)

      # We shouldn't ever get an actual newline in a command, that's awful
      # for copypasta.
      self.assertNotRegexpMatches(quoted, '\n')

      # We should be able to paste any argument into bash & zsh and get
      # exactly what subprocess did.
      bash_output = subprocess.check_output([
          'bash', '-c', '/bin/echo %s' % quoted])
      self.assertEqual(bash_output.decode('utf-8'), s + '\n')

      # zsh is untested because zsh isn't provisioned on our bots. (luqui)
      # zsh_output = subprocess.check_output([
      #     'zsh', '-c', '/bin/echo %s' % quoted])
      # self.assertEqual(zsh_output.decode('utf-8'), s + '\n')

  def test_subannotations(self):
    proc = subprocess.Popen(
        self._run_cmd('engine_tests/subannotations'),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, _ = proc.communicate()
    self.assertRegexpMatches(stdout, r'(?m)^!@@@BUILD_STEP@steppy@@@$')
    self.assertRegexpMatches(stdout, r'(?m)^@@@BUILD_STEP@pippy@@@$')
    # Before 'Subannotate me' we expect an extra STEP_CURSOR to reset the
    # state.
    self.assertRegexpMatches(stdout,
        r'(?m)^@@@STEP_CURSOR@Subannotate me@@@\n@@@STEP_CLOSED@@@$')


if __name__ == '__main__':
  unittest.TestCase.maxDiff = None
  unittest.main()
