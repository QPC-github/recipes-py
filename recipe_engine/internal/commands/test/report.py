# -*- coding: utf-8 -*-
# Copyright 2019 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Internal helpers for reporting test status to stdout."""


from __future__ import print_function


import collections
import datetime
import logging
import os
import sys

from cStringIO import StringIO
from collections import defaultdict
from itertools import groupby, imap

import attr
import coverage

from ...warn.cause import CallSite, ImportSite


@attr.s
class Reporter(object):
  _use_emoji = attr.ib()
  _is_train = attr.ib()
  _fail_tracker = attr.ib()

  _column_count = attr.ib(default=0)
  _long_err_buf = attr.ib(factory=StringIO)
  # store the err msg which may be caused not by the recipe itself, but the
  # discrepancy of supported python version between the recipe and its deps.
  _maybe_soft_failure_buf = attr.ib(factory=StringIO)

  _start_time = attr.ib(factory=datetime.datetime.now)

  # default to 80 cols if we're outputting to not a tty. Otherwise, set this to
  # -1 to allow the terminal to do all wrapping.
  #
  # This allows nice presentation on the bots (i.e. 80 columns), while also
  # allowing full-width display with correct wrapping on terminals/cmd.exe.
  _column_max = attr.ib()
  @_column_max.default
  def _column_max_default(self):
    # 1 == stdout
    return -1 if os.isatty(1) else 80

  _verbose = attr.ib()
  @_verbose.default
  def _verbose_default(self):
    return logging.getLogger().level < logging.WARNING

  def _space_for_columns(self, item_columns):
    """Preemptively ensures we have space to print something which takes
    `item_columns` space.

    Increments self._column_count as a side effect.
    """
    if self._column_max == -1:
      # output is a tty, let it do the wrapping.
      return

    self._column_count += item_columns
    if self._column_count > self._column_max:
      self._column_count = 0
      print()

  def short_report(self, outcome_msg):
    """Prints all test results from `outcome_msg` to stdout.

    Detailed error messages (if any) will be accumulated in this reporter.

    NOTE: Will report and then raise SystemExit if the outcome_msg contains an
    'internal_error', as this indicates that the test harness is in an invalid
    state.

    Args:

      * outcome_msg (Outcome proto) - The message to report.

    Raises SystemExit if outcome_msg has an internal_error.
    """
    # Global error; this means something in the actual test execution code went
    # wrong.
    if outcome_msg.internal_error:
      # This is pretty bad.
      print('ABORT ABORT ABORT')
      print('Global failure(s):')
      for failure in outcome_msg.internal_error:
        print('  ', failure)
      sys.exit(1)

    has_fail = False
    for test_name, test_result in outcome_msg.test_results.iteritems():
      _print_summary_info(
          self._verbose, self._use_emoji, test_name, test_result,
          self._space_for_columns)
      buf = (self._maybe_soft_failure_buf
             if test_result.expect_py_incompatibility else self._long_err_buf)
      _print_detail_info(buf, test_name, test_result)

      has_fail = self._fail_tracker.cache_recent_fails(test_name,
                                                       test_result) or has_fail

    return has_fail


  def final_report(self, cov, outcome_msg, recipe_deps, check_cov_pct=True):
    """Prints all final information about the test run to stdout. Raises
    SystemExit if the tests have failed.

    Args:

      * cov (coverage.Coverage|None) - The accumulated coverage data to report.
        If None, then no coverage analysis/report will be done. Coverage less
        than 100% counts as a test failure.
      * outcome_msg (Outcome proto) - Consulted for uncovered_modules and
        unused_expectation_files. coverage_percent is also populated as a side
        effect. Any uncovered_modules/unused_expectation_files count as test
        failure.
      * recipe_deps (RecipeDeps) - The loaded recipe repo dependencies.
      * check_cov_pct (bool) - If True, treating the coverage percentage < 100
        as a hard failure.

    Side-effects: Populates outcome_msg.coverage_percent.

    Raises SystemExit if the tests failed.
    """
    self._fail_tracker.cleanup()

    soft_fail = self._maybe_soft_failure_buf.tell() > 0
    fail = self._long_err_buf.tell() > 0

    print()
    sys.stdout.write(self._long_err_buf.getvalue())

    # For some integration tests we have repos which don't actually have any
    # recipe files at all. We skip coverage measurement if cov has no data.
    if cov and cov.get_data().measured_files():
      covf = StringIO()
      try:
        outcome_msg.coverage_percent = cov.report(
            file=covf, show_missing=True, skip_covered=True)
      except coverage.CoverageException as ex:
        print('%s: %s' % (ex.__class__.__name__, ex))
      if int(outcome_msg.coverage_percent) != 100:
        fail = True if check_cov_pct and not soft_fail else fail
        # Print detailed coverage report only if hard or soft failures exist.
        print(covf.getvalue() if fail or soft_fail else '')
        print('%s: Insufficient coverage (%.2f%%)' % (
            'FATAL' if fail else 'WARNING',
            outcome_msg.coverage_percent))
        print()

    if outcome_msg.uncovered_modules:
      fail = True
      print('------')
      print('ERROR: The following modules lack any form of test coverage:')
      for modname in outcome_msg.uncovered_modules:
        print('  ', modname)
      print()
      print('Please add test recipes for them (e.g. recipes in the module\'s')
      print('"tests" subdirectory).')
      print()

    if outcome_msg.unused_expectation_files:
      fail = True
      print('------')
      print('ERROR: The below expectation files have no associated test case:')
      for expect_file in outcome_msg.unused_expectation_files:
        print('  ', expect_file)
      print()

    if fail:
      print('------')
      print('FAILED')
      print()
      if not self._is_train:
        print('NOTE: You may need to re-train the expectation files by running')
        print()
        print('  ./recipes.py test train')
        print()
        print('This will update all the .json files to have content which')
        print('matches the current recipe logic. Review them for correctness')
        print('and include them with your CL.')
      sys.exit(1)

    warning_result = _collect_warning_result(outcome_msg)
    if warning_result:
      _print_warnings(warning_result, recipe_deps)
      print('------')
      print('TESTS OK with %d warnings' % len(warning_result))
    elif soft_fail:
      print('\n=======Possible Soft Failures Below=======')
      sys.stdout.write(self._maybe_soft_failure_buf.getvalue())
      print('------')
      print('TESTS OK with some soft failures as above. Those failures need')
      print('human inspection to determine the real causes. It may because of')
      print('a real bug in your recipe or the discrepancy between the claimed')
      print('PYTHON_VERSION_COMPATIBILITY of a recipe and its dependencies.')
      print('They are ignored for now and will not block your CL submit.')
    else:
      print('TESTS OK')

    # clean up reporter buf value
    self._long_err_buf.truncate(0)
    self._maybe_soft_failure_buf.truncate(0)



# Internal helper stuff


FIELD_TO_DISPLAY = collections.OrderedDict([
  # pylint: disable=bad-whitespace
  ('internal_error', (False, 'internal testrunner error',           '🆘', '!')),

  ('bad_test',       (False, 'test specification was bad/invalid',  '🛑', 'S')),
  ('crash_mismatch', (False, 'recipe crashed in an unexpected way', '🔥', 'E')),
  ('check',          (False, 'failed post_process check(s)',        '❌', 'X')),
  ('diff',           (False, 'expectation file has diff',           '⚡', 'D')),

  ('warnings',       (True,  'encounter warning(s)',                '🟡', 'W')),
  ('removed',        (True,  'removed expectation file',            '🌟', 'R')),
  ('written',        (True,  'updated expectation file',            '💾', 'D')),

  # We use '.' even in emoji mode as this is the vast majority of outcomes when
  # training recipes. This makes the other icons pop much better.
  (None,             (True,  '',                                    '.', '.'))
])


def _check_field(test_result, field_name):
  if field_name is None:
    return FIELD_TO_DISPLAY[field_name], None

  for descriptor, value in test_result.ListFields():
    if descriptor.name == field_name:
      return FIELD_TO_DISPLAY[field_name], value

  return (None, None, None, None), None


def _print_summary_info(verbose, use_emoji, test_name, test_result,
                        space_for_columns):
  # Pick the first populated field in the TestResults.Results
  for field_name in FIELD_TO_DISPLAY:
    (success, verbose_msg, emj, txt), _ = _check_field(test_result, field_name)
    icon = emj if use_emoji else txt
    if icon:
      break

  if verbose:
    msg = '' if not verbose_msg else ' (%s)' % verbose_msg
    print('%s ... %s%s' % (test_name, 'ok' if success else 'FAIL', msg))
  else:
    space_for_columns(1 if len(icon) == 1 else 2)
    sys.stdout.write(icon)
  sys.stdout.flush()


def _print_detail_info(err_buf, test_name, test_result):
  verbose_msg = None

  def _header():
    print('=' * 70, file=err_buf)
    print('FAIL (%s) - %s' % (verbose_msg, test_name), file=err_buf)
    print('-' * 70, file=err_buf)

  for field in ('internal_error', 'bad_test', 'crash_mismatch'):
    (_, verbose_msg, _, _), lines = _check_field(test_result, field)
    if lines:
      _header()
      for line in lines:
        print(line, file=err_buf)
      print(file=err_buf)

  (_, verbose_msg, _, _), lines_groups = _check_field(test_result, 'check')
  if lines_groups:
    _header()
    for group in lines_groups:
      for line in group.lines:
        print(line, file=err_buf)
      print(file=err_buf)

  (_, verbose_msg, _, _), lines = _check_field(test_result, 'diff')
  if lines:
    _header()
    for line in lines.lines:
      print(line, file=err_buf)
    print(file=err_buf)


@attr.s
class PerWarningResult(object):
  call_sites = attr.ib(factory=set)
  import_sites = attr.ib(factory=set)


def _collect_warning_result(outcome_msg):
  """Collects issued warnings from all test outcomes and dedupes causes for
  each warning.
  """
  result = defaultdict(PerWarningResult)
  for _, test_result in outcome_msg.test_results.iteritems():
    for name, causes in test_result.warnings.iteritems():
      for cause in causes.causes:
        if cause.WhichOneof('oneof_cause') == 'call_site':
          result[name].call_sites.add(CallSite.from_cause_pb(cause))
        else:
          result[name].import_sites.add(ImportSite.from_cause_pb(cause))
  return result


def _print_warnings(warning_result, recipe_deps):
  def print_bug_links(definition):
    def construct_monorail_link(bug):
      return 'https://%s/p/%s/issues/detail?id=%d' % (
          bug.host, bug.project, bug.id)

    if definition.monorail_bug:
      if len(definition.monorail_bug) == 1:
        print('Bug Link: %s' % (
            construct_monorail_link(definition.monorail_bug[0]),))
      else:
        print('Bug Links:')
        for bug in definition.monorail_bug:
          print('  %s' % construct_monorail_link(bug))

  def print_call_sites(call_sites):
    def stringify_frame(frame):
      return ':'.join((os.path.normpath(frame.file), str(frame.line)))

    if not call_sites:
      return
    print('Call Sites:')
    sorted_sites = sorted(call_sites,
                          key=lambda s: (s.site.file, s.site.line))
    if sorted_sites[0].call_stack:
      # call site contains the full stack.
      for call_site in sorted_sites:
        print('  site: %s' % stringify_frame(call_site.site))
        print('  stack:')
        for f in call_site.call_stack:
          print('    ' +stringify_frame(f))
        print()
    else:
      for file_name, sites in groupby(sorted_sites, key=lambda s: s.site.file):
        # Print sites that have the same file in a single line.
        # E.g. /path/to/site:123 (and 456, 789)
        site_iter = iter(sites)
        line = stringify_frame(next(site_iter).site)
        additional_lines = ', '.join(
            imap(lambda s: str(s.site.line), site_iter))
        if additional_lines:
          line =  '%s (and %s)' % (line, additional_lines)
        print('  ' + line)

  def print_import_sites(import_sites):
    if not import_sites:
      return
    print('Import Sites:')
    for import_site in sorted(import_sites,
                              key=lambda s: (s.repo, s.module, s.recipe)):
      repo = recipe_deps.repos[import_site.repo]
      if import_site.module:
        mod_path = repo.modules[import_site.module].path
        print('  %s' % os.path.normpath(os.path.join(mod_path, '__init__.py')))
      else:
        print('  %s' % os.path.normpath(repo.recipes[import_site.recipe].path))

  for warning_name in sorted(warning_result):
    causes = warning_result[warning_name]
    print('*' * 70)
    print('{:^70}'.format('WARNING: %s' % warning_name))
    print('{:^70}'.format('Found %d call sites and %d import sites' % (
        len(causes.call_sites), len(causes.import_sites),)))
    print('*' * 70)
    definition = recipe_deps.warning_definitions[warning_name]
    if definition.description:
      print('Description:')
      for desc in definition.description:
        print('  %s' % desc)
    if definition.deadline:
      print('Deadline: %s' % definition.deadline)
    print_bug_links(definition)
    print_call_sites(causes.call_sites)
    print_import_sites(causes.import_sites)
