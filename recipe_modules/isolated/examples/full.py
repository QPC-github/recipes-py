# Copyright 2018 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

DEPS = [
    'file',
    'isolated',
    'json',
    'path',
    'runtime',
    'step',
]


def RunSteps(api):
  # Inspect the associated isolated server.
  api.isolated.isolate_server

  # Prepare files.
  temp = api.path.mkdtemp('isolated-example')
  api.step('touch a', ['touch', temp.join('a')])
  api.step('touch b', ['touch', temp.join('b')])
  api.step('touch c', ['touch', temp.join('c')])
  api.file.ensure_directory('mkdirs', temp.join('sub', 'dir'))
  api.step('touch d', ['touch', temp.join('sub', 'dir', 'd')])

  # Create an isolated.
  isolated = api.isolated.isolated(temp)
  isolated.add_file(temp.join('a'))
  isolated.add_files([temp.join('b'), temp.join('c')])
  isolated.add_dir(temp.join('sub', 'dir'))


  # Archive with the default isolate server.
  isolated.archive('archiving')

  # Or try isolating the whole root directory - and doing so to another server.
  isolated = api.isolated.isolated(temp)
  isolated.add_dir(temp)
  isolated.archive(
      'archiving root directory elsewhere',
      isolate_server='other-isolateserver.appspot.com',
  )



def GenTests(api):
  yield api.test('basic')
  yield api.test('experimental') + api.runtime(is_experimental=True)
  yield (api.test('override isolated') +
    api.isolated.properties(server='bananas.example.com', version='release')
  )
