# Copyright 2014 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

DEPS = [
  'json',
  'path',
  'platform',
  'properties',
  'step',
]

from builtins import range, zip

from recipe_engine.config_types import Path

def RunSteps(api):
  api.step('step1', ['/bin/echo', str(api.path['tmp_base'].join('foo'))])

  # module.resource(...) demo.
  api.step('print resource',
           ['echo', api.path.resource('dir', 'file.py')])

  # module.repo_resource() demo.
  api.step('print package dir',
           ['echo', api.path.repo_resource('dir', 'file.py')])

  assert 'start_dir' in api.path
  assert api.path['start_dir'].join('.') == api.path['start_dir']
  assert 'checkout' not in api.path
  api.path['checkout'] = api.path['tmp_base'].join('checkout')
  assert 'checkout' in api.path

  # Test missing/default value.
  assert 'nonexistent' not in api.path
  assert api.path.get('nonexistent') is None
  try:
    raise Exception('Should never raise: %s' % (api.path['nonexistent'],))
  except KeyError:
    pass

  # Global dynamic paths (see config.py example for declaration):
  dynamic_path = api.path['checkout'].join('jerky')
  api.step('checkout path', ['/bin/echo', dynamic_path])

  # Methods from python os.path are available via api.path. For testing, we
  # asserted that this file existed in the test description below.
  assert api.path.exists(api.path['tmp_base'])

  temp_dir = api.path.mkdtemp('kawaab')
  assert api.path.exists(temp_dir)

  temp_file = api.path.mkstemp('kawaac')
  assert api.path.exists(temp_file)

  file_path = api.path['tmp_base'].join('new_file')
  abspath = api.path.abspath(file_path)
  api.path.assert_absolute(abspath)
  try:
    api.path.assert_absolute("not/abs")
    assert False, "assert_absolute failed to catch relative path"
  except AssertionError:
    pass

  assert api.path.pardir == '..'
  if api.platform.is_win:
    assert api.path.sep == '\\'
    assert api.path.pathsep == ';'
  else:
    assert api.path.sep == '/'
    assert api.path.pathsep == ':'

  assert api.path.basename(file_path) == 'new_file'
  assert api.path.dirname(file_path) == api.path['tmp_base']
  assert api.path.split(file_path) == (api.path['tmp_base'], 'new_file')

  thing_bat = api.path['tmp_base'].join('thing.bat')
  thing_bat_mkv = api.path['tmp_base'].join('thing.bat.mkv')
  assert api.path.splitext(thing_bat_mkv) == (thing_bat, '.mkv')

  assert api.path.abs_to_path(api.path['tmp_base']) == api.path['tmp_base']

  assert api.path.relpath(file_path, api.path['tmp_base']) == 'new_file'

  assert api.path.splitext('abc.xyz') == ('abc', '.xyz')
  assert api.path.split('abc/xyz') == ('abc', 'xyz')
  assert api.path.dirname('abc/xyz') == 'abc'

  api.step('touch me', ['touch', api.path.abspath(file_path)])
  # Assert for testing that a file exists.
  api.path.mock_add_paths(file_path)
  assert api.path.exists(file_path)

  # Assert that we can mock filesystem paths.
  root_path = ('C:\\Windows' if api.platform.is_win else '/bin')
  api.path.mock_add_paths(root_path)
  assert api.path.exists(root_path)

  realpath = api.path.realpath(file_path)
  assert api.path.exists(realpath)

  normpath = api.path.normpath(file_path)
  assert api.path.exists(normpath)

  directory = api.path['start_dir'].join('directory')
  filepath = directory.join('filepath')
  api.step('rm directory (initial)', ['rm', '-rf', directory])
  assert not api.path.exists(directory)
  assert not api.path.isdir(directory)
  assert not api.path.exists(filepath)
  assert not api.path.isfile(filepath)

  api.path.mock_add_file(filepath)
  api.step('mkdir directory', ['mkdir', '-p', directory])
  api.step('touch filepath', ['touch', filepath])
  assert api.path.exists(directory)
  assert api.path.isdir(directory)
  assert not api.path.isfile(directory)
  assert api.path.exists(filepath)
  assert not api.path.isdir(filepath)
  assert api.path.isfile(filepath)

  api.path.mock_remove_paths(directory)
  api.step('rm directory', ['rm', '-rf', directory])
  assert not api.path.exists(directory)
  assert not api.path.isdir(directory)
  assert not api.path.exists(filepath)
  assert not api.path.isfile(filepath)

  api.path.mock_add_directory(directory)
  api.step('mkdir directory', ['mkdir', '-p', directory])
  assert api.path.exists(directory)
  assert api.path.isdir(directory)
  assert not api.path.isfile(directory)

  # We can mock copy paths. See the file module to do this for real.
  copy1 = api.path['start_dir'].join('copy1')
  copy10 = api.path['start_dir'].join('copy10')
  copy2 = api.path['start_dir'].join('copy2')
  copy20 = api.path['start_dir'].join('copy20')
  api.step('rm copy2 (initial)', ['rm', '-rf', copy2])
  api.step('rm copy20 (initial)', ['rm', '-rf', copy20])

  api.step('mkdirs', ['mkdir', '-p', copy1.join('foo', 'bar')])
  api.path.mock_add_paths(copy1.join('foo', 'bar'))
  api.step('touch copy10', ['touch', copy10])
  api.path.mock_add_paths(copy10)
  api.step('cp copy1 copy2', ['cp', '-a', copy1, copy2])
  api.path.mock_copy_paths(copy1, copy2)
  assert api.path.exists(copy2.join('foo', 'bar'))
  assert not api.path.exists(copy20)

  # We can mock remove paths. See the file module to do this for real.
  api.step('rm copy2/foo', ['rm', '-rf', copy2.join('foo')])
  api.path.mock_remove_paths(str(copy2)+api.path.sep)
  assert not api.path.exists(copy2.join('foo', 'bar'))
  assert not api.path.exists(copy2.join('foo'))
  assert api.path.exists(copy2)

  api.step('touch copy20', ['touch', copy20])
  api.path.mock_add_paths(copy20)
  api.step('rm copy2', ['rm', '-rf', copy2])
  api.path.mock_remove_paths(copy2)
  assert not api.path.exists(copy2)
  assert api.path.exists(copy20)

  result = api.step('base paths', ['echo'] + [
      api.path[name] for name in sorted(api.path.c.base_paths.keys())
  ])
  result.presentation.logs['result'] = [
      'base_paths: %s' % (api.json.dumps(api.path.c.base_paths.as_jsonish()),),
  ]

  # Convert strings to Paths.
  def _mk_paths():
    return [
      api.path['start_dir'].join('some', 'thing'),
      api.path['start_dir'],
      api.path.resource("module_resource.py"),
      api.path.resource(),
      api.resource("recipe_resource.py"),
      api.resource(),
    ]
  static_paths = _mk_paths()
  for p in static_paths:
    after = api.path.abs_to_path(str(p))
    api.step('converted path %s' % p, ['echo', after])
    assert after == p, (after, p)

  # All paths are comparable and hashable.
  for i, (static_path, new_path) in enumerate(zip(static_paths, _mk_paths())):
    assert static_path == new_path
    assert hash(static_path) == hash(new_path)
    # Now ensure that our new_path doesn't accidentally match any of the
    # static_paths which it shouldn't.
    for j in range(len(static_paths)):
      if j == i:
        continue
      assert static_paths[j] != new_path
      assert hash(static_paths[j]) != hash(new_path)

  try:
    api.path.abs_to_path('non/../absolute')
    assert False, "this should have thrown"  # pragma: no cover
  except ValueError as ex:
    assert "is not absolute" in str(ex), ex

  try:
    if api.platform.is_win:
      api.path.abs_to_path(r'C:\some\other\root\non\absolute')
    else:
      api.path.abs_to_path('/some/other/root/non/absolute')
    assert False, "this should have thrown"  # pragma: no cover
  except ValueError as ex:
    assert "could not figure out" in str(ex), ex

  start_dir = api.path['start_dir']
  tmp_base = api.path['tmp_base']
  assert start_dir < tmp_base
  assert not (tmp_base < start_dir)

  a = start_dir.join('a')
  b = start_dir.join('b')
  assert a < b
  assert not (b < a)

  foo = start_dir.join('ab', platform_ext=dict(foo='.foo'))
  bar = start_dir.join('ab', platform_ext=dict(bar='.bar'))
  assert bar < foo
  assert not (foo < bar)


def GenTests(api):
  for platform in ('linux', 'win', 'mac'):
    yield (api.test(platform) + api.platform.name(platform) +
           # Test when a file already exists
           api.path.exists(api.path['tmp_base']))

    # We have support for chromium swarming built in to the engine for some
    # reason. TODO(phajdan.jr) remove it.
    yield (api.test('%s_swarming' % platform) +
           api.platform.name(platform) +
           api.properties(path_config='swarming') +
           api.path.exists(api.path['tmp_base']))

    yield (api.test('%s_kitchen' % platform) +
           api.platform.name(platform) +
           api.properties(path_config='kitchen') +
           api.path.exists(api.path['tmp_base']))

    yield (api.test('%s_luci' % platform) +
           api.platform.name(platform) +
           api.properties(**{
              '$recipe_engine/path': {
                'cache_dir': '/c',
                'temp_dir': '/t',
                'cleanup_dir': '/build.dead',
              },
           }) +
           api.path.exists(api.path['tmp_base']))
