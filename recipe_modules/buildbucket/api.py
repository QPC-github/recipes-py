# Copyright 2017 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""API for interacting with the buildbucket service.

Depends on 'buildbucket' binary available in PATH:
https://godoc.org/go.chromium.org/luci/buildbucket/client/cmd/buildbucket
"""

import base64
import json

from recipe_engine import recipe_api

from .proto import build_pb2
from .proto import common_pb2
from . import util


class BuildbucketApi(recipe_api.RecipeApi):
  """A module for interacting with buildbucket."""

  # Expose protobuf messages to the users of buildbucket module.
  build_pb2 = build_pb2
  common_pb2 = common_pb2

  def __init__(
      self, property, legacy_property, mastername, buildername, buildnumber,
      revision, parent_got_revision, patch_storage, patch_gerrit_url,
      patch_project, patch_issue, patch_set, issue, patchset, *args, **kwargs):
    super(BuildbucketApi, self).__init__(*args, **kwargs)
    self._service_account_key = None
    self._host = 'cr-buildbucket.appspot.com'

    legacy_property = legacy_property or {}
    if isinstance(legacy_property, basestring):
      legacy_property = json.loads(legacy_property)
    self._legacy_property = legacy_property

    self._build = build_pb2.Build()
    if property.get('build'):
      self._build.ParseFromString(base64.b64decode(property.get('build')))
    else:
      # Legacy mode.
      build_dict = legacy_property.get('build', {})
      self.build.number = int(buildnumber or 0)
      if 'id' in build_dict:
        self._build.id = int(build_dict['id'])
      build_sets = list(util._parse_buildset_tags(build_dict.get('tags', [])))
      _legacy_builder_id(
          build_dict, mastername, buildername, self._build.builder)
      _legacy_input_gerrit_changes(
          self._build.input.gerrit_changes, build_sets, patch_storage,
          patch_gerrit_url, patch_project, patch_issue or issue,
          patch_set or patchset)
      _legacy_input_gitiles_commit(
          self._build.input.gitiles_commit, build_dict, build_sets,
          revision or parent_got_revision)
      _legacy_tags(build_dict, self._build)

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
  def build(self):
    """Returns current build as a buildbucket.v2.Build protobuf message.

    See Build message in
    https://chromium.googlesource.com/infra/luci/luci-go/+/master/buildbucket/proto/build.proto.

    DO NOT MODIFY the returned value.
    Do not implement conditional logic on returned tags; they are for indexing.
    Use returned build.input instead.

    Pure Buildbot support: to simplify transition to buildbucket, returns a
    message even if the current build is not a buildbucket build. Provides as
    much information as possible. Some fields may be left empty, violating
    the rules described in the .proto files.
    If the current build is not a buildbucket build, returned build.id is 0.
    """
    return self._build

  @property
  def tags_for_child_build(self):
    """A dict of tags (key -> value) derived from current (parent) build for a
    child build."""
    original_tags = {t.key: t.value for t in self.build.tags}
    new_tags = {'user_agent': 'recipe'}

    # TODO(nodir): switch to ScheduleBuild API where we don't have to convert
    # build input back to tags.
    # This function returns a dict, so there can be only one buildset, although
    # we can have multiple sources.
    # Priority: CL buildset, commit buildset, custom buildset.
    commit = self.build.input.gitiles_commit
    if self.build.input.gerrit_changes:
      cl = self.build.input.gerrit_changes[0]
      new_tags['buildset'] = 'patch/gerrit/%s/%d/%d' % (
          cl.host, cl.change, cl.patchset)

    # Note: an input gitiles commit with ref without id is valid
    # but such commit cannot be used to construct a valid commit buildset.
    elif commit.host and commit.project and commit.id:
      new_tags['buildset'] = (
          'commit/gitiles/%s/%s/+/%s' % (
              commit.host, commit.project, commit.id))
      if commit.ref:
        new_tags['gitiles_ref'] = commit.ref
    else:
      buildset = original_tags.get('buildset')
      if buildset:
        new_tags['buildset'] = buildset

    if self.build.number:
      new_tags['parent_buildnumber'] = str(self.build.number)
    if self.build.builder.builder:
      new_tags['parent_buildername'] = str(self.build.builder.builder)
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

  # DEPRECATED API.

  @property
  def properties(self):  # pragma: no cover
    """DEPRECATED, use build attribute instead."""
    return self._legacy_property

  @property
  def build_id(self):  # pragma: no cover
    """DEPRECATED, use build.id instead."""
    return self.build.id or None

  @property
  def build_input(self):  # pragma: no cover
    """DEPRECATED, use build.input instead."""
    return self.build.input

  @property
  def builder_id(self):  # pragma: no cover
    """Deprecated. Use build.builder instead."""
    return self.build.builder


# Legacy support.


def _legacy_tags(build_dict, build_msg):
  for t in build_dict.get('tags', []):
    k, v = t.split(':', 1)
    if k =='buildset' and v.startswith(('patch/gerrit/', 'commit/gitiles')):
      continue
    if k in ('build_address', 'builder'):
      continue
    build_msg.tags.add(key=k, value=v)


def _legacy_input_gerrit_changes(
    dest_repeated, build_sets,
    patch_storage, patch_gerrit_url, patch_project, patch_issue, patch_set):
  for bs in build_sets:
    if isinstance(bs, common_pb2.GerritChange):
      dest_repeated.add().CopyFrom(bs)

  if not dest_repeated and patch_storage == 'gerrit' and patch_project:
    host, path = util.parse_http_host_and_path(patch_gerrit_url)
    if host and (not path or path == '/'):
      try:
        patch_issue = int(patch_issue or 0)
        patch_set = int(patch_set or 0)
      except ValueError:
        pass
      else:
        if patch_issue and patch_set:
          dest_repeated.add(
              host=host,
              project=patch_project,
              change=patch_issue,
              patchset=patch_set)


def _legacy_input_gitiles_commit(dest, build_dict, build_sets, revision):
  commit = None
  for bs in build_sets:
    if isinstance(bs, common_pb2.GitilesCommit):
      commit = bs
      break
  if commit:
    dest.CopyFrom(commit)

    ref_prefix = 'gitiles_ref:'
    for t in build_dict.get('tags', []):
      if t.startswith(ref_prefix):
        dest.ref = t[len(ref_prefix):]
        break

    return

  if util.is_sha1_hex(revision):
    dest.id = revision


def _legacy_builder_id(build_dict, mastername, buildername, builder_id):
  builder_id.project = build_dict.get('project') or ''
  builder_id.bucket = build_dict.get('bucket') or ''

  if builder_id.bucket:
    luci_prefix = 'luci.%s.' % builder_id.project
    if builder_id.bucket.startswith(luci_prefix):
      builder_id.bucket = builder_id.bucket[len(luci_prefix):]
  if not builder_id.bucket and mastername:
    builder_id.bucket = 'master.%s' % mastername

  tags_dict = dict(t.split(':', 1) for t in build_dict.get('tags', []))
  builder_id.builder = tags_dict.get('builder') or buildername or ''
