# Copyright 2019 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import json

from google.protobuf import json_format
from recipe_engine import recipe_test_api

from . import common

from PB.go.chromium.org.luci.resultdb.proto.rpc.v1 import test_result as test_result_pb2


class ResultDBTestApi(recipe_test_api.RecipeTestApi):

  def query(self, results, step_name=None):
    """Emulates query() return value.

    Args:
      results: a dict {invocation_id: [messages]} where a message must be
        test_result_pb2.TestResult or test_result_pb2.TestExoneration.
      step_name: the name of the step to simulate.
    """
    step_name = step_name or 'rdb ls'
    lines = []
    for inv, messages in results.iteritems():
      for m in messages:
        d = json_format.MessageToDict(m)
        key = common.KINDS_REVERSE[type(m)]
        lines.append(json.dumps({
          'invocationId': inv,
          key: d,
        }))
    return self.step_data(
        step_name, self.m.raw_io.stream_output('\n'.join(lines)))

  def chromium_derive(self, results, step_name=None):
    """Emulates chromium_derive() output value.

    For arguments, see query().
    """
    return self.query(results, step_name=step_name or 'rdb chromium-derive')
