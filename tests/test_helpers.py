import pytest
import pathlib

from async_siril.helpers import BestRejection
from async_siril.command_types import stack_rejection


class TestBestRejection:
    def test_best_rejection_creation(self):
        rejection = BestRejection(method=stack_rejection.REJECTION_SIGMA, low_threshold=2.5, high_threshold=3.0)

        assert rejection.method == stack_rejection.REJECTION_SIGMA
        assert rejection.low_threshold == 2.5
        assert rejection.high_threshold == 3.0

    def test_best_rejection_creation_with_different_method(self):
        rejection = BestRejection(method=stack_rejection.REJECTION_WINSORIZED, low_threshold=1.0, high_threshold=2.0)

        assert rejection.method == stack_rejection.REJECTION_WINSORIZED
        assert rejection.low_threshold == 1.0
        assert rejection.high_threshold == 2.0

    def test_best_rejection_creation_zero_thresholds(self):
        rejection = BestRejection(method=stack_rejection.REJECTION_NONE, low_threshold=0.0, high_threshold=0.0)

        assert rejection.method == stack_rejection.REJECTION_NONE
        assert rejection.low_threshold == 0.0
        assert rejection.high_threshold == 0.0

    def test_best_rejection_creation_negative_thresholds(self):
        rejection = BestRejection(method=stack_rejection.REJECTION_MAD, low_threshold=-1.0, high_threshold=-0.5)

        assert rejection.method == stack_rejection.REJECTION_MAD
        assert rejection.low_threshold == -1.0
        assert rejection.high_threshold == -0.5

    def test_find_with_empty_list_raises_error(self):
        with pytest.raises(ValueError, match="At least 1 image is required to find the best rejection"):
            BestRejection.find([])

    def test_find_with_one_image_uses_percentile(self):
        images = [pathlib.Path("image1.fits")]
        result = BestRejection.find(images)

        assert result.method == stack_rejection.REJECTION_PERCENTILE
        assert result.low_threshold == 0.2
        assert result.high_threshold == 0.1

    def test_find_with_six_images_uses_percentile(self):
        images = [pathlib.Path(f"image{i}.fits") for i in range(1, 7)]
        result = BestRejection.find(images)

        assert result.method == stack_rejection.REJECTION_PERCENTILE
        assert result.low_threshold == 0.2
        assert result.high_threshold == 0.1

    def test_find_with_seven_images_uses_winsorized(self):
        images = [pathlib.Path(f"image{i}.fits") for i in range(1, 8)]
        result = BestRejection.find(images)

        assert result.method == stack_rejection.REJECTION_WINSORIZED
        assert result.low_threshold == 3
        assert result.high_threshold == 3

    def test_find_with_fifteen_images_uses_winsorized(self):
        images = [pathlib.Path(f"image{i}.fits") for i in range(1, 16)]
        result = BestRejection.find(images)

        assert result.method == stack_rejection.REJECTION_WINSORIZED
        assert result.low_threshold == 3
        assert result.high_threshold == 3

    def test_find_with_thirty_images_uses_winsorized(self):
        images = [pathlib.Path(f"image{i}.fits") for i in range(1, 31)]
        result = BestRejection.find(images)

        assert result.method == stack_rejection.REJECTION_WINSORIZED
        assert result.low_threshold == 3
        assert result.high_threshold == 3

    def test_find_with_thirty_one_images_uses_linear_fit(self):
        images = [pathlib.Path(f"image{i}.fits") for i in range(1, 32)]
        result = BestRejection.find(images)

        assert result.method == stack_rejection.REJECTION_LINEAR_FIT
        assert result.low_threshold == 5
        assert result.high_threshold == 5

    def test_find_with_fifty_images_uses_linear_fit(self):
        images = [pathlib.Path(f"image{i}.fits") for i in range(1, 51)]
        result = BestRejection.find(images)

        assert result.method == stack_rejection.REJECTION_LINEAR_FIT
        assert result.low_threshold == 5
        assert result.high_threshold == 5

    def test_find_with_hundred_images_uses_linear_fit(self):
        images = [pathlib.Path(f"image{i}.fits") for i in range(1, 101)]
        result = BestRejection.find(images)

        assert result.method == stack_rejection.REJECTION_LINEAR_FIT
        assert result.low_threshold == 5
        assert result.high_threshold == 5

    def test_find_boundary_conditions(self):
        # Test exact boundary conditions

        # 6 images should still use percentile
        images_6 = [pathlib.Path(f"image{i}.fits") for i in range(1, 7)]
        result_6 = BestRejection.find(images_6)
        assert result_6.method == stack_rejection.REJECTION_PERCENTILE

        # 7 images should use winsorized
        images_7 = [pathlib.Path(f"image{i}.fits") for i in range(1, 8)]
        result_7 = BestRejection.find(images_7)
        assert result_7.method == stack_rejection.REJECTION_WINSORIZED

        # 30 images should still use winsorized
        images_30 = [pathlib.Path(f"image{i}.fits") for i in range(1, 31)]
        result_30 = BestRejection.find(images_30)
        assert result_30.method == stack_rejection.REJECTION_WINSORIZED

        # 31 images should use linear fit
        images_31 = [pathlib.Path(f"image{i}.fits") for i in range(1, 32)]
        result_31 = BestRejection.find(images_31)
        assert result_31.method == stack_rejection.REJECTION_LINEAR_FIT

    def test_find_with_different_path_types(self):
        # Test with different path formats
        images = [
            pathlib.Path("/absolute/path/image1.fits"),
            pathlib.Path("relative/path/image2.fits"),
            pathlib.Path("image3.fits"),
            pathlib.Path("/another/absolute/path/image4.fits"),
        ]
        result = BestRejection.find(images)

        # 4 images should use percentile
        assert result.method == stack_rejection.REJECTION_PERCENTILE
        assert result.low_threshold == 0.2
        assert result.high_threshold == 0.1

    def test_find_with_mixed_file_extensions(self):
        # Test with different file extensions
        images = [
            pathlib.Path("image1.fits"),
            pathlib.Path("image2.fit"),
            pathlib.Path("image3.fts"),
            pathlib.Path("image4.FITS"),
            pathlib.Path("image5.jpg"),  # Even non-FITS files should work
        ]
        result = BestRejection.find(images)

        # 5 images should use percentile
        assert result.method == stack_rejection.REJECTION_PERCENTILE
        assert result.low_threshold == 0.2
        assert result.high_threshold == 0.1

    def test_find_with_duplicate_paths(self):
        # Test behavior with duplicate paths (should still count as separate images)
        images = [
            pathlib.Path("image1.fits"),
            pathlib.Path("image1.fits"),  # Duplicate
            pathlib.Path("image2.fits"),
            pathlib.Path("image2.fits"),  # Duplicate
        ]
        result = BestRejection.find(images)

        # 4 images should use percentile
        assert result.method == stack_rejection.REJECTION_PERCENTILE
        assert result.low_threshold == 0.2
        assert result.high_threshold == 0.1

    def test_dataclass_equality(self):
        rejection1 = BestRejection(method=stack_rejection.REJECTION_SIGMA, low_threshold=2.0, high_threshold=3.0)
        rejection2 = BestRejection(method=stack_rejection.REJECTION_SIGMA, low_threshold=2.0, high_threshold=3.0)
        rejection3 = BestRejection(method=stack_rejection.REJECTION_WINSORIZED, low_threshold=2.0, high_threshold=3.0)

        assert rejection1 == rejection2
        assert rejection1 != rejection3

    def test_dataclass_repr(self):
        rejection = BestRejection(method=stack_rejection.REJECTION_SIGMA, low_threshold=2.5, high_threshold=3.0)
        repr_str = repr(rejection)

        assert "BestRejection" in repr_str
        assert "REJECTION_SIGMA" in repr_str
        assert "2.5" in repr_str
        assert "3.0" in repr_str

    def test_dataclass_fields_exist(self):
        rejection = BestRejection(method=stack_rejection.REJECTION_NONE, low_threshold=0.0, high_threshold=0.0)

        # Test that the dataclass has the expected fields
        assert hasattr(rejection, "method")
        assert hasattr(rejection, "low_threshold")
        assert hasattr(rejection, "high_threshold")

    def test_find_static_method_independence(self):
        # Test that multiple calls to find() are independent
        images1 = [pathlib.Path("image1.fits")]
        images2 = [pathlib.Path(f"image{i}.fits") for i in range(1, 11)]

        result1 = BestRejection.find(images1)
        result2 = BestRejection.find(images2)

        assert result1.method == stack_rejection.REJECTION_PERCENTILE
        assert result2.method == stack_rejection.REJECTION_WINSORIZED
        assert result1 is not result2

    def test_threshold_types(self):
        # Test that thresholds can be different numeric types
        rejection_int = BestRejection(
            method=stack_rejection.REJECTION_SIGMA,
            low_threshold=2,  # int
            high_threshold=3,  # int
        )
        rejection_float = BestRejection(
            method=stack_rejection.REJECTION_SIGMA,
            low_threshold=2.0,  # float
            high_threshold=3.0,  # float
        )

        assert rejection_int.low_threshold == 2
        assert rejection_int.high_threshold == 3
        assert rejection_float.low_threshold == 2.0
        assert rejection_float.high_threshold == 3.0
