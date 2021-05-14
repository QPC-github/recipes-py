# -*- coding: utf-8 -*-
# Copyright 2014 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

DEPS = [
  'path',
  'platform',
  'properties',
  'python',
  'raw_io',
  'step',
]


def RunSteps(api):
  # Read command's stdout and stderr.
  step_result = api.step('echo', ['echo', 'Hello World'],
      stdout=api.raw_io.output(),
      stderr=api.raw_io.output())
  assert step_result.stdout == 'Hello World\n'
  assert step_result.stderr == ''

  # Pass stuff to command's stdin, read it from stdout.
  step_result = api.step('cat', ['cat'],
      stdin=api.raw_io.input_text(data='hello'),
      stdout=api.raw_io.output('out'))
  assert step_result.stdout == 'hello'

  step_result = api.step('cat', ['cat', api.raw_io.input_text(data='hello')],
      stdout=api.raw_io.output('out'))
  assert step_result.stdout == 'hello'

  step_result = api.step(
      'cat (unicode)',
      ['cat', api.raw_io.input_text(data=u'hello 💩')],
      stdout=api.raw_io.output_text('out'))
  assert step_result.stdout == u'hello 💩'

  # \xe2 is not encodable by utf-8 (and has shown up in actual recipe data)
  # so test that input correctly doesn't try to encode it as utf-8.
  step_result = api.step('cat', ['cat'],
      stdin=api.raw_io.input(data='\xe2hello'),
      stdout=api.raw_io.output())
  assert step_result.stdout == '\xe2hello'

  # Example of auto-mocking stdout. '\n' appended to mock 'echo' behavior.
  step_result = api.step('automock', ['echo', 'huh'],
                 stdout=api.raw_io.output('out'),
                 step_test_data=(
                   lambda: api.raw_io.test_api.stream_output('huh\n')))
  assert step_result.stdout == 'huh\n'

  # Example of auto-mocking stdout + stderr.
  step_result = api.step(
    'automock (fail)', ['bash', '-c', 'echo blah && echo fail 1>&2'],
    stdout=api.raw_io.output('out'),
    stderr=api.raw_io.output('err'),
    step_test_data=(
      lambda: (
        api.raw_io.test_api.stream_output('blah\n') +
        api.raw_io.test_api.stream_output('fail\n', 'stderr')
      ))
  )
  assert step_result.stdout == 'blah\n'
  assert step_result.stderr == 'fail\n'

  # leak_to coverage.
  step_result = api.step(
      'leak stdout', ['echo', 'leaking'],
      stdout=api.raw_io.output(leak_to=api.path['tmp_base'].join('out.txt')),
      step_test_data=(
        lambda: api.raw_io.test_api.stream_output('leaking\n')))
  assert step_result.stdout == 'leaking\n'

  api.step('list temp dir', ['ls', api.raw_io.output_dir()])
  api.step('leak dir', ['ls', api.raw_io.output_dir(
      leak_to=api.path['tmp_base'].join('out'))])

  step_result = api.step(
      'dump output_dir',
      ['python', api.resource('dump_files.py'), api.raw_io.output_dir()])
  outdir = step_result.raw_io.output_dir
  some_file = api.path.join('some', 'file')
  assert set(outdir) == {some_file, 'other_file'}
  assert outdir[some_file] == 'cool contents'
  assert 'not_here' not in outdir

  del outdir['some/file']  # delete to save memory
  assert 'some/file' not in outdir

  # Fail to write to leak_to file
  step_result = api.step(
      'nothing leaked to leak_to',
      ['echo',
       api.raw_io.output(leak_to=api.path['tmp_base'].join('missing.txt'))])

  # Example of overriding default mocked output for a single named output.
  step_result = api.python.inline(
      'override_default_mock',
      """
      import sys
      with open(sys.argv[1], 'w') as f:
        f.write(%r)
      """ % api.properties.get('some_prop', 'good_value'),
      args=[api.raw_io.output_text(name='test')],
      step_test_data=(
          lambda: api.raw_io.test_api.output_text(
              'second_bad_value', name='test')))
  assert step_result.raw_io.output_texts['test'] == 'good_value'
  assert step_result.raw_io.output_text == 'good_value'

  # Example of add_output_log
  step_result = api.python.inline(
      'success output log',
      """
      import sys
      with open(sys.argv[1], 'w') as f:
        f.write('sucess')
      """,
      args=[api.raw_io.output(name='success_log', add_output_log=True)],
      step_test_data=(
          lambda: api.raw_io.test_api.output(
              'sucess', name='success_log')))
  assert (['sucess'] ==
          step_result.presentation.logs['raw_io.output[success_log]'])

  # Example of add_output_log on failure
  try:
    api.python.inline(
        'failure output log',
        """
        import sys
        with open(sys.argv[1], 'w') as f:
          f.write('failure')
        exit(1)
        """,
        args=[api.raw_io.output(name='failure_log',
                                add_output_log='on_failure')],
        step_test_data=(
            lambda: api.raw_io.test_api.output(
                'failure', name='failure_log')))
  except api.step.StepFailure:
    pass # This step is expected to fail.
  finally:
    step_result = api.step.active_result
    assert (['failure'] ==
            step_result.presentation.logs['raw_io.output[failure_log]'])

  # Example of the placeholder backing file being missing at the time the
  # result is retrieved.
  step_result = api.step(
      'missing backing file', [
          'cat',
          api.raw_io.output(
              suffix='.txt',
              name='outfile',
              leak_to='/this/file/doesnt/exist',
          )
      ],
      ok_ret=(1,))
  assert step_result.raw_io.output is None


def GenTests(api):
  # This test shows that you can override a specific placeholder, even with
  # default `step_test_data`. However, since this recipe is ACTUALLY run in
  # the presubmit, we need to do a trick with properties:
  #   When run for real, "some_prop" will be "good_value" and pass.
  #   When run for simulation, we override this property to provide a bad value,
  #     AND the default step_test_data in RunSteps above ALSO provides another
  #     bad value, the simulation passes ONLY because of the
  #     'override_default_mock' below.
  for osname in ('linux', 'win'):
    sep = '/' if osname == 'linux' else '\\'
    yield (api.test('basic_'+osname) +
        api.properties(some_prop='bad_value') +
        api.platform.name(osname) +
        api.step_data('echo',
            stdout=api.raw_io.output('Hello World\n'),
            stderr=api.raw_io.output('')) +
        api.step_data('cat',
            stdout=api.raw_io.output('hello')) +
        api.step_data('cat (2)',
            stdout=api.raw_io.output('hello')) +
        api.step_data('cat (3)',
            stdout=api.raw_io.output('\xe2hello')) +
        api.step_data('cat (unicode)',
            stdout=api.raw_io.output_text(u'hello 💩')) +
        api.step_data('dump output_dir', api.raw_io.output_dir({
          sep.join(['some', 'file']): 'cool contents',
          'other_file': 'whatever',
        })) +
        api.step_data('override_default_mock',
            api.raw_io.output_text('good_value', name='test')) +
        api.step_data('failure output log', retcode=1) +
        api.step_data('missing backing file',
            api.raw_io.backing_file_missing(name='outfile'), retcode=1)
    )
