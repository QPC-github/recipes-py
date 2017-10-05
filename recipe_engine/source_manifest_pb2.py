# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: source_manifest.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='source_manifest.proto',
  package='milo',
  syntax='proto3',
  serialized_pb=_b('\n\x15source_manifest.proto\x12\x04milo\"\xa7\x05\n\x08Manifest\x12\x0f\n\x07version\x18\x01 \x01(\x05\x12\x34\n\x0b\x64irectories\x18\x02 \x03(\x0b\x32\x1f.milo.Manifest.DirectoriesEntry\x1aW\n\x0bGitCheckout\x12\x10\n\x08repo_url\x18\x01 \x01(\t\x12\x11\n\tfetch_url\x18\x02 \x01(\t\x12\x10\n\x08revision\x18\x03 \x01(\t\x12\x11\n\tfetch_ref\x18\x04 \x01(\t\x1aL\n\x0b\x43IPDPackage\x12\x17\n\x0fpackage_pattern\x18\x01 \x01(\t\x12\x13\n\x0binstance_id\x18\x02 \x01(\t\x12\x0f\n\x07version\x18\x03 \x01(\t\x1a+\n\x08Isolated\x12\x11\n\tnamespace\x18\x01 \x01(\t\x12\x0c\n\x04hash\x18\x02 \x01(\t\x1a\xb1\x02\n\tDirectory\x12\x30\n\x0cgit_checkout\x18\x01 \x01(\x0b\x32\x1a.milo.Manifest.GitCheckout\x12\x18\n\x10\x63ipd_server_host\x18\x02 \x01(\t\x12?\n\x0c\x63ipd_package\x18\x04 \x03(\x0b\x32).milo.Manifest.Directory.CipdPackageEntry\x12\x1c\n\x14isolated_server_host\x18\x05 \x01(\t\x12)\n\x08isolated\x18\x06 \x03(\x0b\x32\x17.milo.Manifest.Isolated\x1aN\n\x10\x43ipdPackageEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12)\n\x05value\x18\x02 \x01(\x0b\x32\x1a.milo.Manifest.CIPDPackage:\x02\x38\x01\x1aL\n\x10\x44irectoriesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\'\n\x05value\x18\x02 \x01(\x0b\x32\x18.milo.Manifest.Directory:\x02\x38\x01\"+\n\x0cManifestLink\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\x0e\n\x06sha256\x18\x02 \x01(\x0c\x62\x06proto3')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_MANIFEST_GITCHECKOUT = _descriptor.Descriptor(
  name='GitCheckout',
  full_name='milo.Manifest.GitCheckout',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='repo_url', full_name='milo.Manifest.GitCheckout.repo_url', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='fetch_url', full_name='milo.Manifest.GitCheckout.fetch_url', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='revision', full_name='milo.Manifest.GitCheckout.revision', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='fetch_ref', full_name='milo.Manifest.GitCheckout.fetch_ref', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=115,
  serialized_end=202,
)

_MANIFEST_CIPDPACKAGE = _descriptor.Descriptor(
  name='CIPDPackage',
  full_name='milo.Manifest.CIPDPackage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='package_pattern', full_name='milo.Manifest.CIPDPackage.package_pattern', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='instance_id', full_name='milo.Manifest.CIPDPackage.instance_id', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='version', full_name='milo.Manifest.CIPDPackage.version', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=204,
  serialized_end=280,
)

_MANIFEST_ISOLATED = _descriptor.Descriptor(
  name='Isolated',
  full_name='milo.Manifest.Isolated',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='namespace', full_name='milo.Manifest.Isolated.namespace', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='hash', full_name='milo.Manifest.Isolated.hash', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=282,
  serialized_end=325,
)

_MANIFEST_DIRECTORY_CIPDPACKAGEENTRY = _descriptor.Descriptor(
  name='CipdPackageEntry',
  full_name='milo.Manifest.Directory.CipdPackageEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='milo.Manifest.Directory.CipdPackageEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='value', full_name='milo.Manifest.Directory.CipdPackageEntry.value', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=_descriptor._ParseOptions(descriptor_pb2.MessageOptions(), _b('8\001')),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=555,
  serialized_end=633,
)

_MANIFEST_DIRECTORY = _descriptor.Descriptor(
  name='Directory',
  full_name='milo.Manifest.Directory',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='git_checkout', full_name='milo.Manifest.Directory.git_checkout', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='cipd_server_host', full_name='milo.Manifest.Directory.cipd_server_host', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='cipd_package', full_name='milo.Manifest.Directory.cipd_package', index=2,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='isolated_server_host', full_name='milo.Manifest.Directory.isolated_server_host', index=3,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='isolated', full_name='milo.Manifest.Directory.isolated', index=4,
      number=6, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_MANIFEST_DIRECTORY_CIPDPACKAGEENTRY, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=328,
  serialized_end=633,
)

_MANIFEST_DIRECTORIESENTRY = _descriptor.Descriptor(
  name='DirectoriesEntry',
  full_name='milo.Manifest.DirectoriesEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='milo.Manifest.DirectoriesEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='value', full_name='milo.Manifest.DirectoriesEntry.value', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=_descriptor._ParseOptions(descriptor_pb2.MessageOptions(), _b('8\001')),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=635,
  serialized_end=711,
)

_MANIFEST = _descriptor.Descriptor(
  name='Manifest',
  full_name='milo.Manifest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='version', full_name='milo.Manifest.version', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='directories', full_name='milo.Manifest.directories', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_MANIFEST_GITCHECKOUT, _MANIFEST_CIPDPACKAGE, _MANIFEST_ISOLATED, _MANIFEST_DIRECTORY, _MANIFEST_DIRECTORIESENTRY, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=32,
  serialized_end=711,
)


_MANIFESTLINK = _descriptor.Descriptor(
  name='ManifestLink',
  full_name='milo.ManifestLink',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='url', full_name='milo.ManifestLink.url', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='sha256', full_name='milo.ManifestLink.sha256', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=713,
  serialized_end=756,
)

_MANIFEST_GITCHECKOUT.containing_type = _MANIFEST
_MANIFEST_CIPDPACKAGE.containing_type = _MANIFEST
_MANIFEST_ISOLATED.containing_type = _MANIFEST
_MANIFEST_DIRECTORY_CIPDPACKAGEENTRY.fields_by_name['value'].message_type = _MANIFEST_CIPDPACKAGE
_MANIFEST_DIRECTORY_CIPDPACKAGEENTRY.containing_type = _MANIFEST_DIRECTORY
_MANIFEST_DIRECTORY.fields_by_name['git_checkout'].message_type = _MANIFEST_GITCHECKOUT
_MANIFEST_DIRECTORY.fields_by_name['cipd_package'].message_type = _MANIFEST_DIRECTORY_CIPDPACKAGEENTRY
_MANIFEST_DIRECTORY.fields_by_name['isolated'].message_type = _MANIFEST_ISOLATED
_MANIFEST_DIRECTORY.containing_type = _MANIFEST
_MANIFEST_DIRECTORIESENTRY.fields_by_name['value'].message_type = _MANIFEST_DIRECTORY
_MANIFEST_DIRECTORIESENTRY.containing_type = _MANIFEST
_MANIFEST.fields_by_name['directories'].message_type = _MANIFEST_DIRECTORIESENTRY
DESCRIPTOR.message_types_by_name['Manifest'] = _MANIFEST
DESCRIPTOR.message_types_by_name['ManifestLink'] = _MANIFESTLINK

Manifest = _reflection.GeneratedProtocolMessageType('Manifest', (_message.Message,), dict(

  GitCheckout = _reflection.GeneratedProtocolMessageType('GitCheckout', (_message.Message,), dict(
    DESCRIPTOR = _MANIFEST_GITCHECKOUT,
    __module__ = 'source_manifest_pb2'
    # @@protoc_insertion_point(class_scope:milo.Manifest.GitCheckout)
    ))
  ,

  CIPDPackage = _reflection.GeneratedProtocolMessageType('CIPDPackage', (_message.Message,), dict(
    DESCRIPTOR = _MANIFEST_CIPDPACKAGE,
    __module__ = 'source_manifest_pb2'
    # @@protoc_insertion_point(class_scope:milo.Manifest.CIPDPackage)
    ))
  ,

  Isolated = _reflection.GeneratedProtocolMessageType('Isolated', (_message.Message,), dict(
    DESCRIPTOR = _MANIFEST_ISOLATED,
    __module__ = 'source_manifest_pb2'
    # @@protoc_insertion_point(class_scope:milo.Manifest.Isolated)
    ))
  ,

  Directory = _reflection.GeneratedProtocolMessageType('Directory', (_message.Message,), dict(

    CipdPackageEntry = _reflection.GeneratedProtocolMessageType('CipdPackageEntry', (_message.Message,), dict(
      DESCRIPTOR = _MANIFEST_DIRECTORY_CIPDPACKAGEENTRY,
      __module__ = 'source_manifest_pb2'
      # @@protoc_insertion_point(class_scope:milo.Manifest.Directory.CipdPackageEntry)
      ))
    ,
    DESCRIPTOR = _MANIFEST_DIRECTORY,
    __module__ = 'source_manifest_pb2'
    # @@protoc_insertion_point(class_scope:milo.Manifest.Directory)
    ))
  ,

  DirectoriesEntry = _reflection.GeneratedProtocolMessageType('DirectoriesEntry', (_message.Message,), dict(
    DESCRIPTOR = _MANIFEST_DIRECTORIESENTRY,
    __module__ = 'source_manifest_pb2'
    # @@protoc_insertion_point(class_scope:milo.Manifest.DirectoriesEntry)
    ))
  ,
  DESCRIPTOR = _MANIFEST,
  __module__ = 'source_manifest_pb2'
  # @@protoc_insertion_point(class_scope:milo.Manifest)
  ))
_sym_db.RegisterMessage(Manifest)
_sym_db.RegisterMessage(Manifest.GitCheckout)
_sym_db.RegisterMessage(Manifest.CIPDPackage)
_sym_db.RegisterMessage(Manifest.Isolated)
_sym_db.RegisterMessage(Manifest.Directory)
_sym_db.RegisterMessage(Manifest.Directory.CipdPackageEntry)
_sym_db.RegisterMessage(Manifest.DirectoriesEntry)

ManifestLink = _reflection.GeneratedProtocolMessageType('ManifestLink', (_message.Message,), dict(
  DESCRIPTOR = _MANIFESTLINK,
  __module__ = 'source_manifest_pb2'
  # @@protoc_insertion_point(class_scope:milo.ManifestLink)
  ))
_sym_db.RegisterMessage(ManifestLink)


_MANIFEST_DIRECTORY_CIPDPACKAGEENTRY.has_options = True
_MANIFEST_DIRECTORY_CIPDPACKAGEENTRY._options = _descriptor._ParseOptions(descriptor_pb2.MessageOptions(), _b('8\001'))
_MANIFEST_DIRECTORIESENTRY.has_options = True
_MANIFEST_DIRECTORIESENTRY._options = _descriptor._ParseOptions(descriptor_pb2.MessageOptions(), _b('8\001'))
# @@protoc_insertion_point(module_scope)
