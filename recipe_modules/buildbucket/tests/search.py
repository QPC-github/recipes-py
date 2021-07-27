# Copyright 2019 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

from google.protobuf import json_format

from PB.go.chromium.org.luci.buildbucket.proto import build as build_pb2
from PB.go.chromium.org.luci.buildbucket.proto import common as common_pb2
from PB.go.chromium.org.luci.buildbucket.proto \
  import builds_service as builds_service_pb2

DEPS = [
  'buildbucket',
  'properties',
  'raw_io',
  'runtime',
  'step'
]


def RunSteps(api):
  limit = api.properties.get('limit')
  builds = api.buildbucket.search(
      builds_service_pb2.BuildPredicate(
        gerrit_changes=list(api.buildbucket.build.input.gerrit_changes),
      ),
      limit=limit,
      fields=['builder', 'id', 'status', 'create_time'],
  )
  assert limit is None or len(builds) <= limit
  pres = api.step.active_result.presentation
  for b in builds:
    pres.logs['build %s' % b.id] = json_format.MessageToJson(b).splitlines()


def GenTests(api):
  def test(test_name, tags=None, **req):
    return (
      api.test(test_name) +
      api.runtime(is_experimental=False) +
      api.buildbucket.try_build(
          project='chromium',
          builder='Builder',
          git_repo='https://chromium.googlesource.com/chromium/src',
      )
    )

  yield (
      test('basic')
  )

  yield (
      test('two builds') +
      api.buildbucket.simulated_search_results([
        build_pb2.Build(id=1, status=common_pb2.SUCCESS),
        build_pb2.Build(id=2, status=common_pb2.FAILURE),
      ])
  )

  yield (
      test('search failed') +
      api.step_data(
          'buildbucket.search',
          api.raw_io.stream_output('there was a problem'),
          retcode = 1
        )
  )
