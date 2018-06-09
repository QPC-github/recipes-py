# Copyright 2017 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""API for interacting with the buildbucket service.

Depends on 'buildbucket' binary available in PATH:
https://godoc.org/go.chromium.org/luci/buildbucket/client/cmd/buildbucket
"""

import collections
import re

from recipe_engine import recipe_api

"""A collections.namedtuple identifying a builder configuration.

See `message Builder.ID` at: https://chromium.googlesource.com/infra/infra/+/83f40c82f9c9a176bd89ced280e55b9b9637dd23/appengine/cr-buildbucket/proto/build.proto#206
"""
BuilderID = collections.namedtuple('BuilderID', [
  # Project ID, e.g. "chromium". Unique within a LUCI deployment.
  'project',
  # Bucket name, e.g. "try". Unique within the project.
  # Together with project, defines an ACL.
  'bucket',
  # Builder name, e.g. "linux-rel". Unique within the bucket.
  'builder',
])


# A Gerrit patchset.
# Subset of GerritChange message in
# https://chromium.googlesource.com/infra/infra/+/331dbdf84ea76d9d974395bf731ca53ab886ed58/appengine/cr-buildbucket/proto/common.proto#28
GerritChange = collections.namedtuple('GerritChange', [
  # Gerrit hostname, e.g. "chromium-review.googlesource.com".
  'host',
  # Change number, e.g. 12345.
  'change',
  # Patch set number, e.g. 1.
  'patchset',
])


# A Gitiles commit.
# Subset GitilesCommit message in
# https://chromium.googlesource.com/infra/infra/+/331dbdf84ea76d9d974395bf731ca53ab886ed58/appengine/cr-buildbucket/proto/common.proto#40
GitilesCommit = collections.namedtuple('GitilesCommit', [
  # Gitiles hostname, e.g. "chromium.googlesource.com".
  'host',
  # Repository name on the host, e.g. "chromium/src".
  'project',
  # Commit HEX SHA1.
  'id',
])


def _parse_build_set(bs_string):
  """Parses a buildset string to GerritChange or GitilesCommit.

  A port of
  https://chromium.googlesource.com/infra/luci/luci-go/+/fe4e304639d11ca00537768f8bfbf20ffecf73e6/buildbucket/buildset.go#105
  """
  assert isinstance(bs_string, basestring)
  p = bs_string.split('/')
  if '' in p:
    return None

  n = len(p)

  if n == 5 and p[0] == 'patch' and p[1] == 'gerrit':
    return GerritChange(
        host=p[2],
        change=int(p[3]),
        patchset=int(p[4])
    )

  if n >= 5 and p[0] == 'commit' and p[1] == 'gitiles':
    if p[n-2] != '+' or not re.match('^[0-9a-f]{40}$', p[n-1]):
      return None
    return GitilesCommit(
        host=p[2],
        project='/'.join(p[3:n-2]), # exclude plus
        id=p[n-1],
    )

  return None


# Defines what to build/test.
# A subset of Build.Input message in
# https://chromium.googlesource.com/infra/infra/+/331dbdf84ea76d9d974395bf731ca53ab886ed58/appengine/cr-buildbucket/proto/build.proto#27
# See its comments for documentation.
BuildInput = collections.namedtuple(
    'BuildInput', ['gitiles_commit', 'gerrit_changes'])


class BuildbucketApi(recipe_api.RecipeApi):
  """A module for interacting with buildbucket."""

  def __init__(self, buildername, buildnumber, *args, **kwargs):
    super(BuildbucketApi, self).__init__(*args, **kwargs)
    self._buildername = buildername
    self._buildnumber = buildnumber
    self._properties = None
    self._service_account_key = None
    self._host = 'cr-buildbucket.appspot.com'
    self._build_input = None

  def set_buildbucket_host(self, host):
    """Changes the buildbucket backend hostname used by this module.

    Args:
      host (str): buildbucket server host (e.g. 'cr-buildbucket.appspot.com').
    """
    self._host = host

  def use_service_account_key(self, key_path):
    """Tells this module to start using given service account key for auth.

    Otherwise the module is using the default account (when running on LUCI or
    locally), or no auth at all (when running on Buildbot).

    Exists mostly to support Buildbot environment. Recipe for LUCI environment
    should not use this.

    Args:
      key_path (str): a path to JSON file with service account credentials.
    """
    self._service_account_key = key_path

  @property
  def properties(self):
    """Returns (dict-like or None): The BuildBucket properties, if present."""
    if self._properties is None:
      # Not cached, load and deserialize from properties.
      props = self.m.properties.get('buildbucket')
      if props is not None:
        if isinstance(props, basestring):
          props = self.m.json.loads(props)
        self._properties = props
    return self._properties

  @property
  def _tags(self):
    return (self.properties or {}).get('build', {}).get('tags', [])

  @property
  def _build_sets(self):
    prefix = 'buildset:'
    return [t[len(prefix):] for t in self._tags if t.startswith(prefix)]

  @property
  def build_input(self):
    if self._build_input is None:
      build_sets = filter(None, map(_parse_build_set, self._build_sets))
      commit = None
      for bs in build_sets:
        if isinstance(bs, GitilesCommit):
          commit = bs
          break
      self._build_input = BuildInput(
          gitiles_commit=commit,
          gerrit_changes=
              [bs for bs in build_sets if isinstance(bs, GerritChange)],
      )
    return self._build_input

  @property
  def build_id(self):
    """Returns int64 identifier of the current build.

    It is unique per buildbucket instance.
    In practice, it means globally unique.

    May return None if it is not a buildbucket build.
    """
    id = (self.properties or {}).get('build', {}).get('id')
    if isinstance(id, basestring):
      # JSON cannot hold int64 as a number
      id = int(id)
    return id

  @property
  def builder_id(self):
    """A BuilderID identifying the current builder configuration.

    Any of the returned Builder's properties is set to None if no information
    for that property is found.
    """
    build_info = (self.properties or {}).get('build', {})
    project = build_info.get('project')
    bucket = build_info.get('bucket')

    if bucket:
      luci_prefix = 'luci.%s.' % project
      if bucket.startswith(luci_prefix):
        bucket = bucket[len(luci_prefix):]

    tags_dict = dict(t.split(':', 1) for t in self._tags)
    builder = tags_dict.get('builder')

    return BuilderID(project=project, bucket=bucket, builder=builder)

  @property
  def tags_for_child_build(self):
    """A dict of tags (key -> value) derived from current (parent) build for a
    child build."""
    buildbucket_info = self.properties or {}

    original_tags = dict(t.split(':', 1) for t in self._tags)
    new_tags = {'user_agent': 'recipe'}

    for tag in ['buildset', 'gitiles_ref']:
      if tag in original_tags:
        new_tags[tag] = original_tags[tag]

    if self._buildnumber is not None:
      new_tags['parent_buildnumber'] = str(self._buildnumber)
    if self._buildername is not None:
      new_tags['parent_buildername'] = str(self._buildername)
    return new_tags

  # RPCs.

  def put(self, builds, **kwargs):
    """Puts a batch of builds.

    Args:
      builds (list): A list of dicts, where keys are:
        'bucket': (required) name of the bucket for the request.
        'parameters' (dict): (required) arbitrary json-able parameters that a
          build system would be able to interpret.
        'tags': (optional) a dict(str->str) of tags for the build. These will
          be added to those generated by this method and override them if
          appropriate. If you need to remove a tag set by default, set its value
          to None (for example, tags={'buildset': None} will ensure build is
          triggered without 'buildset' tag).

    Returns:
      A step that as its .stdout property contains the response object as
      returned by buildbucket.
    """
    build_specs = []
    for build in builds:
      build_specs.append(self.m.json.dumps({
        'bucket': build['bucket'],
        'parameters_json': self.m.json.dumps(build['parameters']),
        'tags': self._tags_for_build(build['bucket'], build['parameters'],
                                     build.get('tags')),
        'experimental': self.m.runtime.is_experimental,
      }))
    return self._call_service('put', build_specs, **kwargs)

  def cancel_build(self, build_id, **kwargs):
    return self._call_service('cancel', [build_id], **kwargs)

  def get_build(self, build_id, **kwargs):
    return self._call_service('get', [build_id], **kwargs)

  # Internal.

  def _call_service(self, command, args, **kwargs):
    step_name = kwargs.pop('name', 'buildbucket.' + command)
    if self._service_account_key:
      args = ['-service-account-json', self._service_account_key] + args
    args = ['buildbucket', command, '-host', self._host] + args
    kwargs.setdefault('infra_step', True)
    return self.m.step(step_name, args, stdout=self.m.json.output(), **kwargs)

  def _tags_for_build(self, bucket, parameters, override_tags=None):
    new_tags = self.tags_for_child_build
    builder_name = parameters.get('builder_name')
    if builder_name:
      new_tags['builder'] = builder_name
    # TODO(tandrii): remove this Buildbot-specific code.
    if bucket.startswith('master.'):
      new_tags['master'] = bucket[7:]
    new_tags.update(override_tags or {})
    return sorted(
        '%s:%s' % (k, v)
        for k, v in new_tags.iteritems()
        if v is not None)
