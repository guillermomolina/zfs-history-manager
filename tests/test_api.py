# Copyright 2021, Guillermo Adrián Molina
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from zhm.api.manager import Manager
from zhm.exceptions import ZHMError
from pathlib import Path
from zhm.api.zfs import zfs_exists, zfs_get, zfs_is_filesystem, zfs_is_snapshot

zfs = 'rpool/my/cool/zfs/directory'
directory = '/my_cool_zfs_directory'


class TestAPI(unittest.TestCase):
    def setUp(self):
        try:
            Manager.initialize_zfs(zfs, directory)
        except ZHMError:
            pass
        return super().setUp()

    def tearDown(self):
        try:
            Manager(directory).destroy()
        except ZHMError:
            pass
        return super().tearDown()

    def test_initialize(self):
        with self.assertRaises(ZHMError):
            Manager.initialize_zfs(zfs, directory)
        manager = None
        try:
            manager = Manager(directory)
        except ZHMError as e:
            self.fail('Instantiation should not raise exceptions')

        self.assertEqual(manager.path, Path(directory))
        self.assertEqual(manager.zfs, zfs)
        self.assertEqual(manager.active, manager.instances[0])
        self.assertEqual(manager.next_id, '00000001')

        filesystem = zfs
        path = Path(directory, '.clones')
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000000'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory)
        self.assertEqual(manager.instances[0]['id'], id)
        self.assertEqual(manager.instances[0]['name'], filesystem)
        self.assertIsNone(manager.instances[0]['origin'])
        self.assertIsNone(manager.instances[0]['origin_id'])
        self.assertEqual(manager.instances[0]['mountpoint'], path)
        self.assertIsInstance(manager.instances[0]['creation'], int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

    def test_create_1(self):
        manager = None
        try:
            manager = Manager(directory)
        except ZHMError as e:
            self.fail('Instantiation should not raise exceptions')
        try:
            manager.clone()
        except ZHMError as e:
            self.fail('Creation should not raise exceptions')

        self.assertEqual(manager.path, Path(directory))
        self.assertEqual(manager.zfs, zfs)
        self.assertEqual(manager.active, manager.instances[0])
        self.assertEqual(manager.next_id, '00000002')

        filesystem = zfs
        path = Path(directory, '.clones')
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000000'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory)
        self.assertEqual(manager.instances[0]['id'], id)
        self.assertEqual(manager.instances[0]['name'], filesystem)
        self.assertIsNone(manager.instances[0]['origin'])
        self.assertIsNone(manager.instances[0]['origin_id'])
        self.assertEqual(manager.instances[0]['mountpoint'], path)
        self.assertIsInstance(manager.instances[0]['creation'], int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000001'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory, '.clones', id)
        self.assertEqual(manager.instances[1]['id'], id)
        self.assertEqual(manager.instances[1]['name'], filesystem)
        self.assertEqual(manager.instances[1]['origin'], '%s/%s@%s' % (zfs, '00000000', id))
        self.assertEqual(manager.instances[1]['origin_id'], '00000000')
        self.assertEqual(manager.instances[1]['mountpoint'], path)
        self.assertIsInstance(manager.instances[1]['creation'], int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

    def test_activate_1(self):
        manager = None
        try:
            manager = Manager(directory)
        except ZHMError as e:
            self.fail('Instantiation should not raise exceptions')
        try:
            manager.clone()
        except ZHMError as e:
            self.fail('Creation should not raise exceptions')
        try:
            manager.activate('00000001')
        except ZHMError as e:
            self.fail('Creation should not raise exceptions')
        with self.assertRaises(ZHMError):
            manager.remove('00000001')

        self.assertEqual(manager.path, Path(directory))
        self.assertEqual(manager.zfs, zfs)
        self.assertEqual(manager.active, manager.instances[1])
        self.assertEqual(manager.next_id, '00000002')

        filesystem = zfs
        path = Path(directory, '.clones')
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000000'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory, '.clones', id)
        self.assertEqual(manager.instances[0]['id'], id)
        self.assertEqual(manager.instances[0]['name'], filesystem)
        self.assertIsNone(manager.instances[0]['origin'])
        self.assertIsNone(manager.instances[0]['origin_id'])
        self.assertEqual(manager.instances[0]['mountpoint'], path)
        self.assertIsInstance(manager.instances[0]['creation'], int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000001'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory)
        self.assertEqual(manager.instances[1]['id'], id)
        self.assertEqual(manager.instances[1]['name'], filesystem)
        self.assertEqual(manager.instances[1]['origin'], '%s/%s@%s' % (zfs, '00000000', id))
        self.assertEqual(manager.instances[1]['origin_id'], '00000000')
        self.assertEqual(manager.instances[1]['mountpoint'], path)
        self.assertIsInstance(manager.instances[1]['creation'], int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

    def test_remove_newer_1(self):
        manager = None
        try:
            manager = Manager(directory)
        except ZHMError as e:
            self.fail('Instantiation should not raise exceptions')
        try:
            manager.clone()
        except ZHMError as e:
            self.fail('Creation should not raise exceptions')
        try:
            manager.remove('00000001')
        except ZHMError as e:
            self.fail('Creation should not raise exceptions')

        self.assertEqual(manager.path, Path(directory))
        self.assertEqual(manager.zfs, zfs)
        self.assertEqual(manager.active, manager.instances[0])
        self.assertEqual(manager.next_id, '00000001')

        filesystem = zfs
        path = Path(directory, '.clones')
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000000'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory)
        self.assertEqual(manager.instances[0]['id'], id)
        self.assertEqual(manager.instances[0]['name'], filesystem)
        self.assertIsNone(manager.instances[0]['origin'])
        self.assertIsNone(manager.instances[0]['origin_id'])
        self.assertEqual(manager.instances[0]['mountpoint'], path)
        self.assertIsInstance(manager.instances[0]['creation'], int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000001'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory, '.clones', id)
        self.assertFalse(zfs_exists(filesystem))
        self.assertFalse(path.exists())

    def test_remove_older_1(self):
        manager = None
        try:
            manager = Manager(directory)
        except ZHMError as e:
            self.fail('Instantiation should not raise exceptions')
        try:
            manager.clone()
        except ZHMError as e:
            self.fail('Creation should not raise exceptions')
        try:
            manager.activate('00000001')
        except ZHMError as e:
            self.fail('Creation should not raise exceptions')
        try:
            manager.remove('00000000')
        except ZHMError as e:
            self.fail('Creation should not raise exceptions')

        self.assertEqual(manager.path, Path(directory))
        self.assertEqual(manager.zfs, zfs)
        self.assertEqual(manager.active, manager.instances[0])
        self.assertEqual(manager.next_id, '00000002')

        filesystem = zfs
        path = Path(directory, '.clones')
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000000'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory, '.clones', id)
        self.assertFalse(zfs_exists(filesystem))
        self.assertFalse(path.exists())

        id = '00000001'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory)
        self.assertEqual(manager.instances[0]['id'], id)
        self.assertEqual(manager.instances[0]['name'], filesystem)
        self.assertIsNone(manager.instances[0]['origin'])
        self.assertIsNone(manager.instances[0]['origin_id'])
        self.assertEqual(manager.instances[0]['mountpoint'], path)
        self.assertIsInstance(manager.instances[0]['creation'], int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

    def test_create_2(self):
        manager = None
        try:
            manager = Manager(directory)
        except ZHMError as e:
            self.fail('Instantiation should not raise exceptions')
        try:
            manager.clone()
        except ZHMError as e:
            self.fail('Creation should not raise exceptions')
        try:
            manager.clone()
        except ZHMError as e:
            self.fail('Creation should not raise exceptions')

        self.assertEqual(manager.path, Path(directory))
        self.assertEqual(manager.zfs, zfs)
        self.assertEqual(manager.active, manager.instances[0])
        self.assertEqual(manager.next_id, '00000003')

        filesystem = zfs
        path = Path(directory, '.clones')
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000000'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory)
        self.assertEqual(manager.instances[0]['id'], id)
        self.assertEqual(manager.instances[0]['name'], filesystem)
        self.assertIsNone(manager.instances[0]['origin'])
        self.assertIsNone(manager.instances[0]['origin_id'])
        self.assertEqual(manager.instances[0]['mountpoint'], path)
        self.assertIsInstance(manager.instances[0]['creation'], int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000001'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory, '.clones', id)
        self.assertEqual(manager.instances[1]['id'], id)
        self.assertEqual(manager.instances[1]['name'], filesystem)
        self.assertEqual(manager.instances[1]['origin'], '%s/%s@%s' % (zfs, '00000000', id))
        self.assertEqual(manager.instances[1]['origin_id'], '00000000')
        self.assertEqual(manager.instances[1]['mountpoint'], path)
        self.assertIsInstance(manager.instances[1]['creation'], int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000002'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory, '.clones', id)
        self.assertEqual(manager.instances[2]['id'], id)
        self.assertEqual(manager.instances[2]['name'], filesystem)
        self.assertEqual(manager.instances[2]['origin'], '%s/%s@%s' % (zfs, '00000000', id))
        self.assertEqual(manager.instances[2]['origin_id'], '00000000')
        self.assertEqual(manager.instances[2]['mountpoint'], path)
        self.assertIsInstance(manager.instances[1]['creation'], int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

    def test_activate_2(self):
        manager = None
        try:
            manager = Manager(directory)
        except ZHMError as e:
            self.fail('Instantiation should not raise exceptions')
        try:
            manager.clone()
        except ZHMError as e:
            self.fail('Creation should not raise exceptions')
        try:
            manager.clone()
        except ZHMError as e:
            self.fail('Creation should not raise exceptions')
        try:
            manager.activate('00000001')
        except ZHMError as e:
            self.fail('Creation should not raise exceptions')
        with self.assertRaises(ZHMError):
            manager.remove('00000001')

        self.assertEqual(manager.path, Path(directory))
        self.assertEqual(manager.zfs, zfs)
        self.assertEqual(manager.active, manager.instances[1])
        self.assertEqual(manager.next_id, '00000003')

        filesystem = zfs
        path = Path(directory, '.clones')
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000000'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory, '.clones', id)
        self.assertEqual(manager.instances[0]['id'], id)
        self.assertEqual(manager.instances[0]['name'], filesystem)
        self.assertIsNone(manager.instances[0]['origin'])
        self.assertIsNone(manager.instances[0]['origin_id'])
        self.assertEqual(manager.instances[0]['mountpoint'], path)
        self.assertIsInstance(manager.instances[0]['creation'], int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000001'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory)
        self.assertEqual(manager.instances[1]['id'], id)
        self.assertEqual(manager.instances[1]['name'], filesystem)
        self.assertEqual(manager.instances[1]['origin'], '%s/%s@%s' % (zfs, '00000000', id))
        self.assertEqual(manager.instances[1]['origin_id'], '00000000')
        self.assertEqual(manager.instances[1]['mountpoint'], path)
        self.assertIsInstance(manager.instances[1]['creation'], int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000002'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory, '.clones', id)
        self.assertEqual(manager.instances[2]['id'], id)
        self.assertEqual(manager.instances[2]['name'], filesystem)
        self.assertEqual(manager.instances[2]['origin'], '%s/%s@%s' % (zfs, '00000000', id))
        self.assertEqual(manager.instances[2]['origin_id'], '00000000')
        self.assertEqual(manager.instances[2]['mountpoint'], path)
        self.assertIsInstance(manager.instances[2]['creation'], int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

    def test_remove_newer_2(self):
        manager = None
        try:
            manager = Manager(directory)
        except ZHMError as e:
            self.fail('Instantiation should not raise exceptions')
        try:
            manager.clone()
        except ZHMError as e:
            self.fail('Creation should not raise exceptions')
        try:
            manager.clone()
        except ZHMError as e:
            self.fail('Creation should not raise exceptions')
        try:
            manager.activate('00000001')
        except ZHMError as e:
            self.fail('Creation should not raise exceptions')
        try:
            manager.remove('00000002')
        except ZHMError as e:
            self.fail('Creation should not raise exceptions')

        self.assertEqual(manager.path, Path(directory))
        self.assertEqual(manager.zfs, zfs)
        self.assertEqual(manager.active, manager.instances[1])
        self.assertEqual(manager.next_id, '00000002')

        filesystem = zfs
        path = Path(directory, '.clones')
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000000'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory, '.clones', id)
        self.assertEqual(manager.instances[0]['id'], id)
        self.assertEqual(manager.instances[0]['name'], filesystem)
        self.assertIsNone(manager.instances[0]['origin'])
        self.assertIsNone(manager.instances[0]['origin_id'])
        self.assertEqual(manager.instances[0]['mountpoint'], path)
        self.assertIsInstance(manager.instances[0]['creation'], int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000001'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory)
        self.assertEqual(manager.instances[1]['id'], id)
        self.assertEqual(manager.instances[1]['name'], filesystem)
        self.assertEqual(manager.instances[1]['origin'], '%s/%s@%s' % (zfs, '00000000', id))
        self.assertEqual(manager.instances[1]['origin_id'], '00000000')
        self.assertEqual(manager.instances[1]['mountpoint'], path)
        self.assertIsInstance(manager.instances[1]['creation'], int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000002'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory, '.clones', id)
        self.assertFalse(zfs_exists(filesystem))
        self.assertFalse(path.exists())

    def test_remove_older_2(self):
        manager = None
        try:
            manager = Manager(directory)
        except ZHMError as e:
            self.fail('Instantiation should not raise exceptions')
        try:
            manager.clone()
        except ZHMError as e:
            self.fail('Creation should not raise exceptions')
        try:
            manager.clone()
        except ZHMError as e:
            self.fail('Creation should not raise exceptions')
        try:
            manager.activate('00000001')
        except ZHMError as e:
            self.fail('Creation should not raise exceptions')
        try:
            manager.remove('00000000')
        except ZHMError as e:
            self.fail('Creation should not raise exceptions')

        self.assertEqual(manager.path, Path(directory))
        self.assertEqual(manager.zfs, zfs)
        self.assertEqual(manager.active, manager.instances[0])
        self.assertEqual(manager.next_id, '00000003')

        filesystem = zfs
        path = Path(directory, '.clones')
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000000'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory, '.clones', id)
        self.assertFalse(zfs_exists(filesystem))
        self.assertFalse(path.exists())

        id = '00000001'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory)
        self.assertEqual(manager.instances[0]['id'], id)
        self.assertEqual(manager.instances[0]['name'], filesystem)
        self.assertEqual(manager.instances[0]['origin'], '%s/%s@%s' % (zfs, '00000002', id))
        self.assertEqual(manager.instances[0]['origin_id'], '00000002')
        self.assertEqual(manager.instances[0]['mountpoint'], path)
        self.assertIsInstance(manager.instances[0]['creation'], int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000002'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory, '.clones', id)
        self.assertEqual(manager.instances[1]['id'], id)
        self.assertEqual(manager.instances[1]['name'], filesystem)
        self.assertIsNone(manager.instances[1]['origin'])
        self.assertIsNone(manager.instances[1]['origin_id'])
        self.assertEqual(manager.instances[1]['mountpoint'], path)
        self.assertIsInstance(manager.instances[1]['creation'], int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())


if __name__ == '__main__':
    unittest.main()
