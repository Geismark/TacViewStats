import unittest
from src.classes.DCSObject import DCSObject
from src.classes.FileData import FileData
from src.data.coordReferences import death_coords


class TestClasses(unittest.TestCase):
    def setUp(self):
        pass

    def test_FileData(self):
        # FileData init
        test_obj = FileData()
        test_obj.file_name = "TEST_DIR.txt.acmi"
        self.assertEqual(test_obj.file_name, "TEST_DIR.txt.acmi")

        # FileData init time-stamps
        self.assertEqual(test_obj.time_stamp, 0)
        self.assertEqual(test_obj.first_time_stamp, None)
        # FileData set time stamp & first time stamp
        test_obj.set_time(3.47)
        self.assertEqual(test_obj.time_stamp, 3.47)
        self.assertEqual(test_obj.first_time_stamp, 3.47)
        # FileData maintaining first time stamp
        test_obj.set_time(51.12)
        self.assertEqual(test_obj.time_stamp, 51.12)
        self.assertEqual(test_obj.first_time_stamp, 3.47)
        # FileData time stamp input must be int/float
        with self.assertRaises(TypeError):
            test_obj.set_time("72")
        # FileData time stamp is always a float
        test_obj.set_time(int(52))
        self.assertEqual(test_obj.time_stamp, float(52))
        test_obj.set_time(float(53))
        self.assertEqual(test_obj.time_stamp, float(53))
        # FileData time stamp must increase (cannot jump backwards)
        with self.assertRaises(ValueError):
            test_obj.set_time(2.0)

        # FileData init objects -> len = 0 & type dict
        self.assertEqual(test_obj.objects, dict())
        # FileData new object id must be string
        with self.assertRaises(TypeError):
            test_obj.new_obj(123)
        # FileData creating and adding new DCS Objects
        test_unit = test_obj.new_obj("test_unit")
        self.assertTrue(isinstance(test_unit, DCSObject))
        self.assertEqual(test_obj.objects, {"test_unit": test_unit})
        # FUTUREDO ensure id is valid (e.g.: only 0-9 and a-z)? (a-Z? believe may be hex)
        # FileData adding more than 1 object
        test_unit_2 = test_obj.new_obj("test_unit2")
        self.assertEqual(
            test_obj.objects, {"test_unit": test_unit, "test_unit2": test_unit_2}
        )
        # FileData coord reference before set
        with self.assertRaises(ValueError):
            test_obj.get_coord_reference()
        # FileData coord reference partially set
        test_obj.latitude_reference = 21
        with self.assertRaises(TypeError):
            test_obj.get_coord_reference()
        # FileData reference coordinates
        test_obj.longitude_reference = 50
        self.assertEqual(test_obj.get_coord_reference(), [21, 50])

        # FileData remove objects
        # test_obj.remove_obj(test_unit_2)
        # self.assertEqual(test_unit_2.state, "Dying")
        # self.assertEqual(test_unit_2.death_time_stamp, test_obj.time_stamp)
        # self.assertEqual(test_unit_2.get_pos(), [100, 100, -1])
        test_alive_coords = test_unit_2.get_pos()
        test_unit_2.update_to_dying()
        self.assertTrue(test_unit_2.check_state("Dying"))
        self.assertEqual(test_unit_2.death_time_stamp, test_obj.time_stamp)
        self.assertEqual(test_unit_2.get_pos(), death_coords)
        self.assertEqual(test_unit_2.get_death_pos(), test_alive_coords)
        test_unit_2.update_to_dead()
        self.assertTrue(test_unit_2.check_state("Dead"))
        self.assertEqual(test_unit_2.death_time_stamp, test_obj.time_stamp)
        self.assertEqual(test_unit_2.get_pos(), death_coords)
        self.assertEqual(test_unit_2.get_death_pos(), test_alive_coords)
