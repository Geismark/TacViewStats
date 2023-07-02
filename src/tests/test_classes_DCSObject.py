import unittest
from src.classes.DCSEvent import DCSEvent
from src.classes.DCSObject import DCSObject
from src.classes.FileData import FileData


class TestClasses(unittest.TestCase):
    def setUp(self):
        pass

    def test_DCSObject(self):
        # FileData required for DCSObject init
        file_obj = FileData()
        # DCSObject init
        test_unit = DCSObject(file_obj=file_obj, id="123")
        self.assertEqual(test_unit.id, "123")
        self.assertEqual(test_unit.get_pos(), [None, None, 0])
        # DCSObject update position empty
        test_unit.update_transform("", "", "")
        self.assertEqual(test_unit.get_pos(), [None, None, 0])
        self.assertEqual(
            [test_unit.lat_old, test_unit.long_old, test_unit.alt_old], [None, None, 0]
        )
        # DCSObject update position string
        test_unit.update_transform("10", "10", "1000")
        self.assertEqual(test_unit.get_pos(), [10, 10, 1_000])
        self.assertEqual(
            [test_unit.lat_old, test_unit.long_old, test_unit.alt_old], [None, None, 0]
        )
        # DCSObject update position numeric
        test_unit.update_transform(20, 20, 3_000)
        self.assertEqual(test_unit.get_pos(), [20, 20, 3_000])
        self.assertEqual(
            [test_unit.lat_old, test_unit.long_old, test_unit.alt_old], [10, 10, 1_000]
        )
        # DCSObject partial update position
        test_unit.update_transform(0, 0, 0)
        updates_pos_list = [
            [[0, 0, 0], [0, 0, 0]],
            [[1, "", ""], [1, 0, 0]],
            [["", 1, ""], [1, 1, 0]],
            [["", "", 10], [1, 1, 10]],
            [[2, 2, ""], [2, 2, 10]],
            [[3, "", 30], [3, 2, 30]],
            [["", 4, 40], [3, 4, 40]],
        ]
        for index, updates_pos in enumerate(updates_pos_list):
            test_unit.update_transform(
                updates_pos[0][0], updates_pos[0][1], updates_pos[0][2]
            )
            self.assertEqual(test_unit.get_pos(), updates_pos[1])
            if index == 0:
                self.assertEqual(
                    [test_unit.lat_old, test_unit.long_old, test_unit.alt_old],
                    [0, 0, 0],
                )
            else:
                self.assertEqual(
                    [test_unit.lat_old, test_unit.long_old, test_unit.alt_old],
                    updates_pos_list[index - 1][1],
                )
        # DCSObject real pos -> requires FileData set
        with self.assertRaises(ValueError):
            test_unit.get_real_pos()
        # DCSObject:FileData coord reference partially set
        file_obj.latitude_reference = 21
        with self.assertRaises(TypeError):
            test_unit.get_real_pos()
        # DCSObject:FileData reference coordinates
        file_obj.longitude_reference = 50
        self.assertEqual(file_obj.get_coord_reference(), [21, 50])
        self.assertEqual(test_unit.get_real_pos(), [21 + 3, 50 + 4, 40])

        # DCSObject test munition init
        test_munition = DCSObject(file_obj, "munition")
        # DCSObject add munition - much be DCSObject
        with self.assertRaises(TypeError):
            test_unit.add_launch("null")
        # DCSObject add munition - munition cannot already have launcher
        test_munition.launcher = DCSObject(file_obj, "null")
        with self.assertRaises(ValueError):
            test_unit.add_launch(test_munition)
        test_munition.launcher = None
        # DCSObject add munition - both DCSObjects must have the same FileData
        test_munition.file_obj = FileData()
        with self.assertRaises(ValueError):
            test_unit.add_launch(test_munition)
        test_munition.file_obj = file_obj
        # DCSObject add munition
        test_unit.add_launch(test_munition)
        self.assertEqual(test_unit.launches, [test_munition])
        self.assertEqual(test_munition.launcher, test_unit)
        # DCSObject add munition - cannot have already launched
        with self.assertRaises(ValueError):
            test_unit.add_launch(test_munition)
        # DCSObject add multiple munitions
        test_munition2 = DCSObject(file_obj, "munition2")
        test_unit.add_launch(test_munition2)
        self.assertEqual(test_unit.launches, [test_munition, test_munition2])
        self.assertEqual(test_munition2.launcher, test_unit)

        # DCSObject die
        test_unit.die()
        self.assertEqual(test_unit.state, "Dying")
        self.assertEqual(test_unit.file_obj.time_stamp, file_obj.time_stamp)
        self.assertEqual(test_unit.death_time_stamp, file_obj.time_stamp)
        self.assertEqual(test_unit.get_pos(), [100, 100, -1])
