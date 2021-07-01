# Copyright 2015 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

from future.utils import iterkeys
from future.utils import itervalues

from recipe_engine import recipe_test_api

class RawIOTestApi(recipe_test_api.RecipeTestApi): # pragma: no cover
  @recipe_test_api.placeholder_step_data
  @staticmethod
  def output(data, retcode=None, name=None):
    return data, retcode, name

  @recipe_test_api.placeholder_step_data
  @staticmethod
  def output_text(data, retcode=None, name=None):
    return data, retcode, name

  @recipe_test_api.placeholder_step_data
  @staticmethod
  def output_dir(files_dict, retcode=None, name=None):
    """Use to mock an `output_dir` placeholder.

    Note that slashes should match the platform that this test is targeting.
    i.e. if this test is targeting Windows, you need to use backslashes.

    Example:

       yield api.test('tname') + api.step_data('sname', api.raw_io.output_dir({
         "some/file": "contents of some/file",
       }))
    """
    assert type(files_dict) is dict
    assert all(type(key) is str for key in iterkeys(files_dict))
    assert all(type(value) is str for value in itervalues(files_dict))
    return files_dict, retcode, name

  def stream_output(self, data, stream='stdout', retcode=None, name=None):
    ret = recipe_test_api.StepTestData()
    assert stream in ('stdout', 'stderr')
    step_data = self.output(data, retcode=retcode, name=name)
    setattr(ret, stream, step_data.unwrap_placeholder())
    if retcode:
      ret.retcode = retcode
    return ret

  @recipe_test_api.placeholder_step_data('output')
  @staticmethod
  def backing_file_missing(retcode=None, name=None):
    """Simulates a missing backing file.

    Only valid if the corresponding placeholder has `leak_to` specified.
    """
    # Passing None as the data of a placeholder causes the placeholder to
    # behave during testing as if its backing file was missing.
    return None, retcode, name
