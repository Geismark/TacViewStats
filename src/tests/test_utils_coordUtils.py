import unittest
from src.utils.coordUtils import (
    coords_to_euclidean_distance,
    coords_to_haversine_distance,
)


class TestCoordUtils(unittest.TestCase):
    def setUp(self):
        pass

    def test_coords_to_euclidean_distance(self):
        allowed_TV_nm_delta = 0.4
        round_decimal = None
        point0 = [0, 0, 0]
        # distance units error testing
        with self.assertRaises(AttributeError):
            coords_to_euclidean_distance(point0, point0, 404)
        with self.assertRaises(ValueError):
            coords_to_euclidean_distance(point0, point0, "induce_error")
        # same point -> distance should == 0
        self.assertEqual(coords_to_euclidean_distance(point0, point0, "nm"), 0)
        # testing points at same altitude (MSL1 == MSL2 == 0)
        point1 = [44.2305133, 37.2661646, 0]
        point2 = [44.498904, 37.1760557, 0]
        TV_shown = 16.58  # nm
        results = {
            "nm": 16.571957494701714,
            "km": 30.69125410857108,
            "mi": 19.07065525669692,
            "m": 30691.25410857108,
            "ft": 100693.09412956434,
        }
        for unit, expected_dist in results.items():
            eud_distance = coords_to_euclidean_distance(point1, point2, unit)
            self.assertEqual(eud_distance, expected_dist)
            if unit == "nm":
                self.assertAlmostEqual(
                    eud_distance,
                    TV_shown,
                    round_decimal,
                    f"{TV_shown=}\n{eud_distance=}",
                    allowed_TV_nm_delta,
                )
        # testing 1 air and 1 sea point (MSL1 == 0 != MSL2 > 0)
        point1 = [44.1756191, 37.8692512, 0]
        point2 = [44.4734395, 39.7265547, 9801.65]
        TV_shown = 82.32  # nm
        results = {
            "nm": 81.92261249467842,
            "km": 151.7206231138376,
            "mi": 94.27479530486839,
            "m": 151720.62311383762,
            "ft": 497771.089136803,
        }
        for unit, expected_dist in results.items():
            eud_distance = coords_to_euclidean_distance(point1, point2, unit)
            self.assertEqual(eud_distance, expected_dist)
            if unit == "nm":
                self.assertAlmostEqual(
                    eud_distance,
                    TV_shown,
                    round_decimal,
                    f"{TV_shown=}\n{eud_distance=}",
                    allowed_TV_nm_delta,
                )
        # testing 2 air points (MSL != 0)
        point1 = [29.4973704, 54.8285196, 4869.91]
        point2 = [25.9652969, 51.4766983, 10058.56]
        TV_shown = 277.01  # nm
        results = {
            "nm": 276.85540206008,
            "km": 512.7360179793576,
            "mi": 318.59929222785144,
            "m": 512736.0179793576,
            "ft": 1682204.8372273957,
        }
        for unit, expected_dist in results.items():
            eud_distance = coords_to_euclidean_distance(point1, point2, unit)
            print(f"{eud_distance=} {TV_shown}")
            self.assertEqual(eud_distance, expected_dist)
            if unit == "nm":
                self.assertAlmostEqual(
                    eud_distance,
                    TV_shown,
                    round_decimal,
                    f"{TV_shown=}\n{eud_distance=}",
                    allowed_TV_nm_delta,
                )

    def test_coords_to_haversine_distance(self):
        pass

    def test_coords_to_distance(self):
        pass
        d1 = [-133230.23, 381191.19, 2969.81]
        d2 = [-478482.09, -5420.09, 10058.4]
        # 279.9026765261852


if __name__ == "__main__":
    unittest.main()
