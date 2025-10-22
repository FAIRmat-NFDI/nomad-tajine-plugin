#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nomad.datamodel.data import (
        ArchiveSection,
    )
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )


def get_reference(upload_id: str, entry_id: str) -> str:
    return f'../uploads/{upload_id}/archive/{entry_id}#data'


def get_entry_id_from_file_name(file_name: str, archive: 'EntryArchive') -> str:
    from nomad.utils import hash

    return hash(archive.metadata.upload_id, file_name)


def create_archive(
    entity: 'ArchiveSection',
    archive: 'EntryArchive',
    file_name: str,
    overwrite: bool = False,
) -> str:
    if overwrite or not archive.m_context.raw_path_exists(file_name):
        with archive.m_context.update_entry(
            file_name, write=True, process=True
        ) as entry:
            entry['data'] = entity.m_to_dict(with_root_def=True)
    return get_reference(
        archive.metadata.upload_id, get_entry_id_from_file_name(file_name, archive)
    )
