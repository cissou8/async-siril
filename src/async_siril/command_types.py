from __future__ import annotations

import typing as t
from enum import Enum


class sequence_filter_with_value:
    def __init__(
        self,
        _type: sequence_filter_type,
        value: t.Optional[float] = None,
        percent: t.Optional[float] = None,
    ):
        self.filter_type = _type
        if (value is None and percent is None) or (value is not None and percent is not None):
            raise ValueError("A filter must either have a value or percent argument")
        self.value = value
        self.percent = percent

    def value_str(self):
        if self.value is not None:
            return str(self.value)
        return f"{self.percent}%"


class fits_extension(Enum):
    FITS_EXT_FIT = "fit"
    FITS_EXT_FITS = "fits"
    FITS_EXT_FTS = "fts"

class registration_transformation(Enum):
    REG_TRANSF_SHIFT = "shift"
    REG_TRANSF_SIMILARITY = "similarity"
    REG_TRANSF_AFFINE = "affine"
    REG_TRANSF_HOMOGRAPHY = "homography"


class pixel_interpolation(Enum):
    INTERP_NONE = "none"
    INTERP_NEAREST = "nearest"
    INTERP_CUBIC = "cubic"
    INTERP_LANCZOS4 = "lanczos4"
    INTERP_LINEAR = "linear"
    INTERP_AREA = "area"

class sequence_framing(Enum):
    FRAME_CURRENT = "current"
    FRAME_MIN = "min"
    FRAME_MAX = "max"
    FRAME_COG = "cog"


class sequence_filter_type(Enum):
    FILTER_NONE = ""
    FILTER_FWHM = "filter-fwhm"
    FILTER_WFWHM = "filter-wfwhm"
    FILTER_ROUNDNESS = "filter-round"
    FILTER_QUALITY = "filter-quality"
    FILTER_INCLUSION = "filter-incl"
    FILTER_BACKGROUND = "filter-bkg"
    FILTER_STAR_COUNT = "filter-nbstars"

class compression_type(Enum):
    COMPRESSION_RICE = "rice"
    COMPRESSION_GZIP1 = "gzip1"
    COMPRESSION_GZIP2 = "gzip2"

class stack_type(Enum):
    STACK_SUM = "sum"
    STACK_REJ = "rej"
    STACK_MED = "med"
    STACK_MIN = "min"
    STACK_MAX = "max"


class stack_norm(Enum):
    NO_NORM = "-nonorm"
    NORM_ADD = "-norm=add"
    NORM_ADD_SCALE = "-norm=addscale"
    NORM_MUL = "-norm=mul"
    NORM_MUL_SCALE = "-norm=mulscale"


class stack_rejection(Enum):
    REJECTION_NONE = "n"
    REJECION_PERCENTILE = "p"
    REJECTION_SIGMA = "s"
    REJECTION_MEDIAN = "m"
    REJECTION_WINSORIZED = "w"
    REJECTION_LINEAR_FIT = "l"
    REJECTION_GESDT = "g"
    REJECTION_MAD = "a"


class stack_weighting(Enum):
    NO_WEIGHT = ""
    WEIGHT_FROM_NOISE = "-weight_from_noise"
    WEIGHT_FROM_WFWHM = "-weight_from_wfwhm"
    WEIGHT_FROM_NBSTARS = "-weight_from_nbstars"
    WEIGHT_FROM_NBSTACK = "-weight_from_nbstack"


class stack_rejmaps(Enum):
    NO_REJECTION_MAPS = ""
    TWO_REJECTION_MAPS = "-rejmaps"
    MERGED_REJECTION_MAPS = "-rejmap"

class magnitude_option(Enum):
    DEFAULT_MAGNITUDE = 1
    MAGNITUDE_OFFSET = 2
    ABSOLUTE_MAGNITUDE = 3


class star_catalog(Enum):
    TYCHO2 = "tycho2"
    NOMAD = "nomad"
    GAIA = "gaia"
    PPMXL = "ppmxl"
    BRIGHTSTARS = "brightstars"
    APASS = "apass"

class rmgreen_protection(Enum):
    AVERAGE_NEUTRAL = 0
    MAXIMUM_NEUTRAL = 1

class saturation_hue_range(Enum):
    PINK_ORANGE = 0
    ORANGE_YELLOW = 1
    YELLOW_CYAN = 2
    CYAN = 3
    CYAN_MAGENTA = 4
    MAGENTA_PINK = 5
    ALL = 6

class catalog_option(Enum):
    APASS = "apass"
    LOCAL_GAIA = "localgaia"
    GAIA = "gaia"
