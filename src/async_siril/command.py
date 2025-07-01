import enum
import structlog.stdlib
import typing as t

from enum import Enum

log = structlog.stdlib.get_logger()

class CommandArgument:
    def __init__(self, value):
        self.value = value

    @property
    def valid(self) -> bool:
        return self.value is not None

    def __str__(self):
        if not self.valid:
            return None
        if isinstance(self.value, str) and (" " in self.value):
            return f"'{self.value}'"
        elif isinstance(self.value, enum.Enum):
            return str(self.value.value)
        else:
            return str(self.value)


class CommandFlag:
    def __init__(self, name: str, value: bool):
        self.name = name
        self.value = value

    @property
    def valid(self) -> bool:
        return self.value is True

    def __str__(self):
        return f"-{self.name}"


class CommandOptional(CommandArgument):
    def __init__(self, value: t.Optional[t.Any]):
        super().__init__(value)


class CommandOption:
    def __init__(self, name: str, value: t.Optional[t.Any]):
        self.name = name
        self.value = value

    @property
    def valid(self) -> bool:
        return self.value is not None

    def __str__(self):
        if not self.valid:
            return None
        if isinstance(self.value, str) and (" " in self.value):
            return f"'-{self.name}={self.value}'"
        elif isinstance(self.value, enum.Enum):
            return f"-{self.name}={self.value.value}"
        else:
            return f"-{self.name}={self.value}"


class BaseCommand:
    def __init__(self):
        self.name = type(self).__name__
        self.args = []

    def __str__(self):
        result = self.name
        result += " " if len(self.args) > 0 else ""
        result += " ".join(self.args)
        return result

    @property
    def valid(self) -> bool:
        # return all([o.valid for o in self.args])
        return True

    def append(self, _input: t.Union[CommandArgument, CommandFlag, CommandOptional, CommandOption]):
        if isinstance(_input, CommandArgument) and _input.valid:
            self.args.append(str(_input))
        elif isinstance(_input, CommandFlag) and _input.valid:
            self.args.append(str(_input))
        elif isinstance(_input, CommandOptional) and _input.valid:
            self.args.append(_input.value)
        elif isinstance(_input, CommandOption) and _input.valid:
            self.args.append(str(_input))

####################################################
# Siril CLI Commands
####################################################

class cd(BaseCommand):
    """
    Sets the new current working directory.
    The argument <b>directory</b> can contain the ~ token, expanded as the
    home directory, directories with spaces in the name can be protected using single or double quotes
    """

    def __init__(self, directory: str):
        super().__init__()
        self.append(CommandArgument(directory))


class close(BaseCommand):
    """Properly closes the opened image and the opened sequence, if any"""


class convert(BaseCommand):
    """
    Converts all images in a known format into Siril's FITS images.

    The argument <b>basename</b> is the basename of the new sequence. For FITS images, Siril will try to make a
    symbolic link. If not possible, files will be copied.
    The flags <b>-fitseq</b> and <b>-ser</b> can be used to specify an alternative output format, other than the
    default FITS.
    The option <b>-debayer</b> applies demosaicing to images. In this case no symbolic link are done.
    <b>-start=index</b> sets the starting index number and the <b>-out=</b> option converts files into the
    directory <b>out</b>
    """

    def __init__(
        self,
        base_name: str,
        debayer: bool = False,
        use_fitseq: bool = False,
        use_ser: bool = False,
        start_index: t.Optional[int] = None,
        output_dir: t.Optional[str] = None,
    ):
        super().__init__()
        self.append(CommandArgument(base_name))
        self.append(CommandFlag("debayer", debayer))
        self.append(CommandFlag("fitseq", use_fitseq))
        self.append(CommandFlag("ser", use_ser))
        self.append(CommandOption("start", start_index))
        self.append(CommandOption("out", output_dir))


class exit(BaseCommand):
    """Quits the application"""


class capabilities(BaseCommand):
    """Lists compilation and runtime capabilities"""

    """Format: https://gitlab.com/free-astro/siril/-/issues/846#note_1088624462 """


class get(BaseCommand):
    """
    Get a setting value, using its variable name, or list all with -a (name and value list) or -A (detailed list).

    See also the SET command to update values.
    """

    def __init__(self, list_all: bool = False, detailed: bool = False, variable: t.Optional[str] = None):
        super().__init__()
        if variable is not None:
            self.append(CommandArgument(variable))
        elif list_all and not detailed:
            self.append(CommandFlag("a", list_all))
        elif list_all and detailed:
            self.append(CommandFlag("A", detailed))


class load(BaseCommand):
    """
    Loads the image <b>filename</b>

    It first attempts to load <b>filename</b>, then <b>filename</b>.fit, finally <b>filename</b>.fits and finally
    all supported formats, aborting if none of these are found.
    This scheme is applicable to every Siril command that involves reading files.
    Fits headers MIPS-HI and MIPS-LO are read and their values given to the current viewing levels.
    Writing a known extension <b>.ext</b> at the end of <b>filename</b> will load specifically the image
    <b>filename.ext</b>: this is used when numerous files have the same name but not the same extension
    """

    def __init__(self, filename: str):
        super().__init__()
        self.append(CommandArgument(filename))


class ping(BaseCommand):
    """Pings Siril for keep live-ness status."""


class preprocess(BaseCommand):
    """
    Preprocesses the sequence <b>sequencename</b> using bias, dark and flat given in argument.

    For bias, a uniform level can be specified instead of an image, by entering a quoted expression starting with
    an = sign, such as -bias=\"=256\" or -bias=\"=64*$OFFSET\".
    By default, cosmetic correction is not activated. If you wish to apply some, you will need to specify it
    with <b>-cc=</b> option.
    You can use <b>-cc=dark</b> to detect hot and cold pixels from the masterdark (a masterdark must be given with
    the <b>-dark=</b> option), optionally followed by <b>siglo</b> and <b>sighi</b> for cold and hot pixels
    respectively. A value of 0 deactivates the correction. If sigmas are not provided, only hot pixels detection
    with a sigma of 3 will be applied.
    Alternatively, you can use <b>-cc=bpm</b> followed by the path to your Bad Pixel Map to specify which pixels must
    be corrected. An example file can be obtained with a <i>find_hot</i> command on a masterdark.
    It is possible to specify if images are CFA for cosmetic correction purposes with the option <b>-cfa</b> and also
    to demosaic images at the end of the process with <b>-debayer</b>.
    The <b>-fix_xtrans</b> option is dedicated to X-Trans files by applying a correction on darks and biases to remove
    an ugly square pattern.
    The <b>-equalize_cfa</b> option equalizes the mean intensity of RGB layers of the CFA flat master.
    It is also possible to optimize the dark subtraction with <b>-opt</b>.
    The output sequence name starts with the prefix \"pp_\" unless otherwise specified with option <b>-prefix=</b>.
    If <b>-fitseq</b> is provided, the output sequence will be a FITS sequence (single file).
    """

    def __init__(
        self,
        base_name: str,
        bias: t.Optional[str] = None,
        dark: t.Optional[str] = None,
        flat: t.Optional[str] = None,
        cfa: bool = False,
        debayer: bool = False,
        fix_xtrans: bool = False,
        equalize_cfa: bool = False,
        dark_optimization: bool = False,
        prefix: t.Optional[str] = None,
        create_fitsseq: bool = False,
        cosmetic_correction_from_dark: bool = False,
        cosmetic_correction_from_bad_pixel_map: t.Optional[str] = None,
    ):
        super().__init__()
        self.append(CommandArgument(base_name))
        self.append(CommandOption("bias", bias))
        self.append(CommandOption("dark", dark))
        self.append(CommandOption("flat", flat))
        if dark is not None and cosmetic_correction_from_dark and cosmetic_correction_from_bad_pixel_map is None:
            self.append(CommandArgument("-cc=dark"))
        if cosmetic_correction_from_bad_pixel_map is not None:
            self.append(CommandOption("cc", "bpm"))
            self.append(CommandArgument(cosmetic_correction_from_bad_pixel_map))
        self.append(CommandFlag("cfa", cfa))
        self.append(CommandFlag("debayer", debayer))
        self.append(CommandFlag("fix_xtrans", fix_xtrans))
        self.append(CommandFlag("equalize_cfa", equalize_cfa))
        self.append(CommandFlag("opt", dark_optimization))
        self.append(CommandOption("prefix", prefix))
        self.append(CommandFlag("fitseq", create_fitsseq))


class preprocess_single(BaseCommand):
    """
    Preprocesses the image <b>imagename</b> using bias, dark and flat given in argument.

    For bias, a uniform level can be specified instead of an image, by entering a quoted expression starting
    with an = sign, such as -bias=\"=256\" or -bias=\"=64*$OFFSET\".
    It is possible to specify if images are CFA for cosmetic correction purposes with the option <b>-cfa</b> and also
    to demosaic images at the end of the process with <b>-debayer</b>. The <b>-fix_xtrans</b> option is
    dedicated to X-Trans files by applying a correction on darks and biases to remove an ugly square pattern.
    The <b>-equalize_cfa</b> option equalizes the mean intensity of RGB layers of the CFA flat master.
    It is also possible to optimize the dark subtraction with <b>-opt</b>.
    The output sequence name starts with the prefix \"pp_\" unless otherwise specified with option <b>-prefix=</b>.

    Note that only hot pixels are corrected in cosmetic correction process
    """

    def __init__(
        self,
        imagename: str,
        bias: t.Optional[str] = None,
        dark: t.Optional[str] = None,
        flat: t.Optional[str] = None,
        cfa: bool = False,
        debayer: bool = False,
        fix_xtrans: bool = False,
        equalize_cfa: bool = False,
        opt: bool = False,
        prefix: t.Optional[str] = None,
    ):
        super().__init__()
        self.append(CommandArgument(imagename))
        self.append(CommandOption("bias", bias))
        self.append(CommandOption("dark", dark))
        self.append(CommandOption("flat", flat))
        self.append(CommandFlag("cfa", cfa))
        self.append(CommandFlag("debayer", debayer))
        self.append(CommandFlag("fix_xtrans", fix_xtrans))
        self.append(CommandFlag("equalize_cfa", equalize_cfa))
        self.append(CommandFlag("opt", opt))
        self.append(CommandOption("prefix", prefix))


class seqextract_HaOIII(BaseCommand):
    """
    Extracts H-alpha and O-III signals from the currently loaded CFA image. It reads the Bayer matrix information
    from the image or the preferences and exports only the red filter data for H-alpha and an average of the three
    others as a new half-sized FITS files. The output sequences names start with the prefixes "Ha_" and "OIII_". Only
    selected images in the sequence are processed.
    """

    def __init__(self, base_name: str):
        super().__init__()
        self.append(CommandArgument(base_name))


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


class register(BaseCommand):
    """
    Finds and optionally performs geometric transforms on images of the sequence given in argument so that they may be
    superimposed on the reference image. Using stars for registration, this algorithm only works with deep sky images.
    Star detection options can be changed using <b>SETFINDSTAR</b> or the <i>Dynamic PSF</i> dialog. The detection is
    done on the green layer for colour images, unless specified by the <b>-layer=</b> option with an argument ranging
    from 0 to 2 for red to blue.

    The <b>-2pass</b> and <b>-noout</b> options will only compute the transforms but not generate the transformed
    images, <b>-2pass</b> adds a preliminary pass to the algorithm to find a good reference image before computing the
    transforms.<b>-nostarlist</b> disables saving the star lists to disk.

    The option <b>-transf=</b> specifies the use of either <b>shift</b>, <b>similarity</b>, <b>affine</b> or
    <b>homography</b> (default) transformations respectively.
    The option <b>-drizzle</b> activates the sub-pixel stacking by up-scaling by 2 the generated images.
    The option <b>-minpairs=</b> will specify the minimum number of star pairs a frame must have with the reference
    frame, otherwise the frame will be dropped and excluded from the sequence.
    The option <b>-maxstars=</b> will specify the maximum number of star to find within each frame (must be between
    100 and 2000). With more stars, a more accurate registration can be computed, but will take more time to run.

    The pixel interpolation method can be specified with the <b>-interp=</b> argument followed by one of the methods
    in the list <b>no</b>[ne], <b>ne</b>[arest], <b>cu</b>[bic], <b>la</b>[nczos4], <b>li</b>[near], <b>ar</b>[ea]}.
    If <b>none</b> is passed, the transformation is forced to shift and a pixel-wise shift is applied to each image
    without any interpolation.

    All images of the sequence will be registered unless the option <b>-selected</b> is passed, in that case the
    excluded images will not be processed
    """

    def __init__(
        self,
        base_name: str,
        no_out: bool = False,
        two_pass: bool = False,
        drizzle: bool = False,
        selected: bool = False,
        prefix: t.Optional[str] = None,
        min_pairs: t.Optional[int] = None,
        trans_func: t.Optional[registration_transformation] = None,
        layer: t.Optional[int] = None,
        max_stars: t.Optional[int] = None,
        interp: t.Optional[pixel_interpolation] = None,
    ):
        super().__init__()
        self.append(CommandArgument(base_name))
        self.append(CommandFlag("noout", no_out))
        self.append(CommandFlag("2pass", two_pass))
        self.append(CommandFlag("drizzle", drizzle))
        self.append(CommandFlag("selected", selected))
        self.append(CommandOption("layer", layer))
        self.append(CommandOption("minpairs", min_pairs))
        self.append(CommandOption("maxstars", max_stars))
        self.append(CommandOption("transf", trans_func))
        if not no_out and not two_pass:
            self.append(CommandOption("interp", interp))
            self.append(CommandOption("prefix", prefix))


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


class sequence_filter_with_value:
    def __init__(self, _type: sequence_filter_type, value: t.Optional[float] = None, percent: t.Optional[float] = None):
        self.filter_type = _type
        if (value is None and percent is None) or (value is not None and percent is not None):
            raise ValueError("A filter must either have a value or percent argument")
        self.value = value
        self.percent = percent

    def value_str(self):
        if self.value is not None:
            return str(self.value)
        return f"{self.percent}%"


class seqapplyreg(BaseCommand):
    """
    Applies geometric transforms on images of the sequence given in argument so that they may be superimposed on the
    reference image, using registration data previously computed.

    The output sequence name starts with the prefix <b>\"r_\"</b> unless otherwise specified with <b>-prefix=</b>
    option.

    The option <b>-drizzle</b> activates up-scaling by 2 the images created in the transformed sequence.

    The pixel interpolation method can be specified with the <b>-interp=</b> argument followed by one of the methods
    in the list <b>no</b>[ne], <b>ne</b>[arest], <b>cu</b>[bic], <b>la</b>[nczos4], <b>li</b>[near], <b>ar</b>[ea]}.
    If <b>none</b> is passed, the transformation is forced to shift and a pixel-wise shift is applied to each image
    without any interpolation.

    The registration is done on the first layer for which data exists for RGB images unless specified by
    <b>-layer=</b> option (0, 1 or 2 for R, G and B respectively.

    Automatic framing of the output sequence can be specified using <b>-framing=</b> keyword followed by one of the
    methods in the list { current | min | max | cog } :
    <b>-framing=max</b> (bounding box) adds a black border around each image as required so that no part of the image
    is cropped when registered.
    <b>-framing=min</b> (common area) crops each image to the area it has in common with all images of the sequence.
    <b>-framing=cog</b> determines the best framing position as the center of gravity (cog) of all the images.

    Filtering out images:
    Images to be registered can be selected based on some filters, like those selected or with best FWHM, with some of
    the <b>-filter-*</b> options.
    See the command reference for the complete documentation on this command
    """

    def __init__(
        self,
        base_name: str,
        drizzle: bool = False,
        layer: t.Optional[int] = None,
        prefix: t.Optional[str] = None,
        interp: t.Optional[pixel_interpolation] = None,
        filters: t.Optional[t.List[sequence_filter_with_value]] = None,
        filter_included: bool = False,
        framing: t.Optional[sequence_framing] = None,
    ):
        super().__init__()
        self.append(CommandArgument(base_name))
        self.append(CommandFlag("drizzle", drizzle))
        self.append(CommandOption("layer", layer))
        self.append(CommandOption("prefix", prefix))
        self.append(CommandOption("interp", interp))
        self.append(CommandOption("framing", framing))
        if filters is not None:
            for f in filters:
                self.append(CommandOption(f.filter_type.value, f.value_str()))
        self.append(CommandFlag("filter-incl", filter_included))


class requires(BaseCommand):
    """Returns an error if the version of Siril is older than the one passed in argument"""

    def __init__(self, version: str):
        super().__init__()
        self.append(CommandArgument(version))


class save(BaseCommand):
    """
    Saves current image to <b>filename</b>.fit (or .fits, depending on your preferences, see SETEXT). Fits headers
    MIPS-HI and MIPS-LO are added with values corresponding to the current viewing levels
    """

    def __init__(self, filename: str):
        super().__init__()
        self.append(CommandArgument(filename))


class set16bits(BaseCommand):
    """Disables images to be saved with 32 bits per channel on processing. It uses 16 bits instead"""


class set32bits(BaseCommand):
    """Allows images to be saved with 32 bits per channel on processing"""


class compression_type(Enum):
    COMPRESSION_RICE = "rice"
    COMPRESSION_GZIP1 = "gzip1"
    COMPRESSION_GZIP2 = "gzip2"


class setcompress(BaseCommand):
    """
    Defines if images are compressed or not.
    <b>0</b> means no compression while <b>1</b> enables compression.
    If compression is enabled, the type must be explicitly written in the option <b>-type=</b>
    (\"rice\", \"gzip1\", \"gzip2\").

    Associated to the compression, the quantization value must be within [0, 256] range.
    For example, \"setcompress 1 -type=rice 16\" sets the rice compression with a quantization of 16
    """

    def __init__(self, enable: bool, _type: t.Optional[compression_type] = None, quantization: t.Optional[int] = None):
        super().__init__()
        if enable:
            self.append(CommandArgument("1"))
            self.append(CommandOption("type", _type))
            self.append(CommandArgument(quantization))
        else:
            self.append(CommandArgument("0"))


class fits_extension(Enum):
    FITS_EXT_FIT = "fit"
    FITS_EXT_FITS = "fits"
    FITS_EXT_FTS = "fts"


class setext(BaseCommand):
    """
    Sets the extension used and recognized by sequences.

    The argument <b>extension</b> can be \"fit\", \"fts\" or \"fits\"
    """

    def __init__(self, extension: fits_extension):
        super().__init__()
        self.append(CommandArgument(extension))


class setcpu(BaseCommand):
    """
    Defines the number of processing threads used for calculation. Can be as high as the number of virtual threads
    existing on the system, which is the number of CPU cores or twice this number if hyper-threading (Intel HT) is
    available. The default value is the maximum number of threads available, so this should mostly be used to limit
    processing power. See also SETMEM.

    Warning: this command does not persist over siril restarts, contrary to SETMEM which is saved in settings.
    """

    def __init__(self, count: int):
        super().__init__()
        self.append(CommandArgument(count))


class setmem(BaseCommand):
    """
    Sets a new ratio of free memory on memory used for stacking.
    <b>Ratio</b> value should be between 0.05 and 2, depending on other activities of the machine. A higher ratio
    should allow siril to stack faster, but setting the ratio of memory used for stacking above 1 will require the
    use of on-disk memory, which is very slow and unrecommended
    """

    """
    For an absolute memory limit, use these commands instead (here 5GB):
    set core.mem_mode=1
    set core.mem_amount=5
    """

    def __init__(self, ratio: float):
        super().__init__()
        self.append(CommandArgument(ratio))


class set(BaseCommand):
    """
    Update a setting value, using its variable name, with the given value, or a set of values using an existing
    ini file with <b>-import=</b> option.
    See <b>get</b> to get values or the list of variables
    """

    def __init__(self, variable: str, value: str):
        super().__init__()
        self.append(CommandArgument(f"{variable}={value}"))


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


class stack(BaseCommand):
    """
    stack seqfilename
        stack seqfilename { sum | min | max } [filtering] [-output_norm] [-out=filename]
    stack seqfilename { med | median } [-nonorm, -norm=] [filtering] [-fastnorm] [-rgb_equal]
        [-output_norm] [-out=filename]
    stack seqfilename { rej | mean } [rejection type] [sigma_low sigma_high] [-nonorm, -norm=] [filtering] [-fastnorm]
        [-weight_from_noise | -weight_from_nbstack | -weight_from_wfwhm | -weight_from_nbstars ] [-rgb_equal]
        [-output_norm] [-out=filename]

    with filtering being any of these options, in no particular order or number:

    [-filter-fwhm=value[%|k]] [-filter-wfwhm=value[%|k]] [-filter-round=value[%|k]] [-filter-bkg=value[%|k]]
    [-filter-nbstars=value[%|k]] [-filter-quality=value[%|k]] [-filter-incl[uded]]

    Stacks the seqfilename sequence, using options.

    The allowed types are: sum, max, min, med or median (these two are the same), mean or rej (same here).

    The rejection type is one of n[one], p[ercentile], s[igma], m[edian], w[insorized], l[inear], g[eneralized] or
    [m]a[d] for no rejection or Percentile, Sigma, Median, Winsorized, Linear-Fit, Generalized Extreme Studentized
    Deviate Test and k-MAD clipping. If omitted, the default (Winsorized) is used. The sigma_low and high parameters of
    rejection are mandatory if rejection is not set to none. Optionally, rejection maps can be created, showing where
    pixels were rejected in one (-rejmap) or two (-rejmaps, for low and high rejections) newly created images. Rejection
    map files will be named like the original file, with suffixes _low+high_rejmap, _low_rejmap or _high_rejmap
    depending on the case.

    See the tooltips in the stacking tab for more information about the stacking methods and rejection types, or see the
    documentation.

    Best images from the sequence can be stacked by using the filtering arguments. Each of these arguments can remove
    bad images based on a property their name contains, taken from the registration data, with either of the three types
    of argument values:
        * a numeric value for the worse image to keep depending on the type of data used (between 0 and 1 for roundness
        and quality, absolute values otherwise),
        * a percentage of best images to keep if the number is followed by a % sign,
        * or a k value for the k.sigma of the worse image to keep if the number is followed by a k sign.

    It is also possible to use manually selected images, either previously from the GUI or with the select or unselect
    commands, using the -filter-included argument.

    If several filters are added to the command, only images that pass all the filters will be stacked. There is
    consequently no order. If a filter is badly declared, because it has no registration data or a too low threshold,
    nothing will be stacked.

    Normalization can be enabled for median and mean stacking methods using the -norm=normalization option. The allowed
    normalization are: add, addscale, mul or mulscale. For other methods, or with the use of the -nonorm flag,
    normalization is disabled. The additional flag -fastnorm will enable the use of faster estimators for location
    (median) and scale (MAD) than the default IKSS, which in a few cases may give less good results. -rgb_equal will
    change how color images are normalized to equalize their own channels, making their background more gray than the
    usual green. This is useful if no pcc can be made, or if no unlinked autostretch is to be used.

    Weighting the images in the mean computation (after rejection if enabled) is possible using either the noise level
    computed from each image (option -weight_from_noise), the FWHM weighted by the number of stars common with the
    reference image (option -weight_from_wfwhm), the number of stars in the image (option -weight_from_nbstars) (the
    last two computed during registration), or using the number of images previously used to stack the input images,
    indicated by the STACKCNT or NCOMBINE FITS header keywords (option -weight_from_nbstack), the latter being used for
    live or iterative stacking.  These options can only be enabled with mean or rejection stacking, when normalization
    has been enabled.

    -output_norm applies a normalization at the end of the stacking to rescale result in the [0, 1] range.

    Stacked image for the sequence is created with the name provided in the optional argument -out, or with the name of
    the sequence suffixed "_stacked" and the configured FITS file extension. If a file with this name already exists, it
    will be overwritten without warning.
    """

    def __init__(
        self,
        base_name: str,
        _type: stack_type = stack_type.STACK_REJ,
        norm: stack_norm = stack_norm.NO_NORM,
        rejection: stack_rejection = stack_rejection.REJECTION_WINSORIZED,
        lower_rej: float = 3,
        higher_rej: float = 3,
        create_rejection_maps: stack_rejmaps = stack_rejmaps.NO_REJECTION_MAPS,
        filters: t.Optional[t.List[sequence_filter_with_value]] = None,
        filter_included: bool = False,
        fast_norm: bool = False,
        output_norm: bool = False,
        weighting: stack_weighting = stack_weighting.NO_WEIGHT,
        rgb_equalization: bool = False,
        out: t.Optional[str] = None,
    ):
        super().__init__()
        self.append(CommandArgument(base_name))
        self.append(CommandArgument(_type))
        if _type == stack_type.STACK_REJ:
            # we'll provide all optional arguments for simplicity
            self.append(CommandArgument(rejection))
            if rejection != stack_rejection.REJECTION_NONE:
                self.append(CommandArgument(lower_rej))
                self.append(CommandArgument(higher_rej))
                if create_rejection_maps is not stack_rejmaps.NO_REJECTION_MAPS:
                    self.append(CommandArgument(create_rejection_maps))
        self.append(CommandArgument(norm))
        if filters is not None:
            for f in filters:
                self.append(CommandOption(f.filter_type.value, f.value_str()))
        self.append(CommandFlag("filter-incl", filter_included))
        self.append(CommandFlag("fastnorm", fast_norm))
        self.append(CommandFlag("output_norm", output_norm))
        if weighting is not stack_weighting.NO_WEIGHT:
            self.append(CommandArgument(weighting))
        self.append(CommandFlag("rgb_equal", rgb_equalization))
        self.append(CommandOption("out", out))


class subsky(BaseCommand):
    """
    Computes the level of the local sky background thanks to a polynomial function of an order <b>degree</b>
    and subtracts it from the image
    """

    def __init__(
        self,
        use_rbf: bool = False,
        degree: int = 4,
        samples: t.Optional[int] = None,
        tolerance: t.Optional[float] = None,
        smooth: t.Optional[float] = None,
    ):
        super().__init__()
        if use_rbf:
            self.append(CommandFlag("rbf", use_rbf))
            self.append(CommandOption("smooth", smooth))
        else:
            self.append(CommandArgument(degree))
        self.append(CommandOption("samples", samples))
        self.append(CommandOption("tolerance", tolerance))


class seqsubsky(BaseCommand):
    """
    Same command as SUBSKY but for the sequence <b>sequencename</b>.
    The output sequence name strts with the prefix \"bkg_\" unless otherwise specified with <b>-prefix=</b> option
    """

    def __init__(
        self,
        base_name: str,
        samples: t.Optional[int] = None,
        tolerance: t.Optional[float] = None,
        prefix: t.Optional[str] = None,
    ):
        super().__init__()
        self.append(CommandArgument(base_name))
        # polynomial version with degree 1 should always be used in sequence processing
        self.append(CommandArgument("1"))
        self.append(CommandOption("samples", samples))
        self.append(CommandOption("tolerance", tolerance))
        self.append(CommandOption("prefix", prefix))


#################### POST PROCESSING COMMANDS ########################## noqa: E266
class autostretch(BaseCommand):
    """
    Auto-stretches the currently loaded image, with different parameters for
    each channel (unlinked) unless <b>-linked</b> is passed.
    Arguments are optional, <b>shadowclip</b> is the shadows clipping point,
    measured in sigma units from the main histogram peak (default is -2.8),
    <b>targetbg</b> is the target background value, giving a final brightness
    to the image, range [0, 1], default is 0.25
    """

    def __init__(
        self,
        linked: t.Optional[bool] = None,
        shadows_clipping: t.Optional[float] = None,
        target_background: t.Optional[float] = None,
    ):
        super().__init__()
        self.append(CommandFlag("linked", linked is not None and linked is True))
        if target_background is not None and shadows_clipping is not None:
            self.append(CommandArgument(shadows_clipping))
            self.append(CommandArgument(target_background))


class asinh(BaseCommand):
    """
    asinh [-human] stretch [offset]
    Stretches the image to show faint objects using an hyperbolic arcsin transformation. The
    mandatory argument <b>stretch</b>, typically between 1 and 1000, will give the strength of the
    stretch. The black point can be offset by providing an optional <b>offset</b> argument in the
    normalized pixel value of [0, 1]. Finally the option <b>-human</b> enables using human eye
    luminous efficiency weights to compute the luminance used to compute the stretch value for each
    pixel, instead of the simple mean of the channels pixel values
    """

    def __init__(self, stretch: float, human_weighting: t.Optional[bool] = None, offset: t.Optional[float] = None):
        super().__init__()
        self.append(CommandFlag("human", human_weighting is not None and human_weighting is True))
        self.append(CommandArgument(stretch))
        self.append(CommandArgument(offset))


class rgbcomp(BaseCommand):
    """
    rgbcomp [-lum=image [rgb_image]] [red green blue] [-out=result_filename]
    Create an RGB composition using three independent images, or an LRGB composition using
    the optional luminance image and three monochrome images or a color image.
    Result image is called composed_rgb.fit or composed_lrgb.fit unless another name
    is provided in the optional argument
    """

    def __init__(
        self,
        luminance: t.Optional[str] = None,
        rgb_image: t.Optional[str] = None,
        red_image: t.Optional[str] = None,
        green_image: t.Optional[str] = None,
        blue_image: t.Optional[str] = None,
        out: t.Optional[str] = None,
    ):
        super().__init__()
        using_rgb_image = False
        if luminance is not None:
            self.append(CommandOption("lum", luminance))
            if rgb_image is not None:
                self.append(CommandArgument(rgb_image))
                using_rgb_image = True
        if not using_rgb_image:
            if red_image is None or green_image is None or blue_image is None:
                raise ValueError("The three input images are required for rgbcomp")
            self.append(CommandArgument(red_image))
            self.append(CommandArgument(green_image))
            self.append(CommandArgument(blue_image))
        self.append(CommandOption("out", out))


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


class pcc(BaseCommand):
    """
    pcc [image_center_coords] [-noflip] [-platesolve] [-focal=] [-pixelsize=] [-limitmag=[+-]] [-catalog=] [-downscale]

    Run the Photometric Color Correction on the loaded image.
    If the image has already been plate solved, the PCC can reuse the astrometric solution, otherwise, or if WCS or
    other image metadata is erroneous or missing, arguments for the plate solving must be passed:
    the approximate image center coordinates can be provided in decimal degrees or degree/hour minute second values
    (J2000 with colon separators), with right ascension and declination values separated by a comma or a space.
    focal length and pixel size can be passed with <b>-focal=</b> (in mm) and <b>-pixelsize=</b> (in microns),
    overriding values from image and settings.
    you can force the plate solving to be remade using the <b>-platesolve</b> flag.
    Unless <b>-noflip</b> is specified and the image is detected as being upside-down, the image will be flipped if a
    plate solving is run.
    For faster star detection in big images, downsampling the image is possible with <b>-downscale</b>.
    The limit magnitude of stars used for plate solving and PCC is automatically computed from the size of the field of
    view, but can be altered by passing a +offset or -offset value to <b>-limitmag=</b>, or simply an absolute positive
    value for the limit magnitude.
    The star catalog used is NOMAD by default, it can be changed by providing <b>-catalog=apass</b>. If installed
    locally, the remote NOMAD can be forced by providing <b>-catalog=nomad</b>
    """

    def __init__(
        self,
        image_center: t.Optional[str] = None,
        noflip: bool = False,
        force_plate_solve: bool = False,
        downscale: bool = False,
        focal_length: t.Optional[float] = None,
        pixel_size: t.Optional[float] = None,
        limit_mag: magnitude_option = magnitude_option.DEFAULT_MAGNITUDE,
        magnitude_value: float = 0.0,
        catalog: star_catalog = None,
    ):
        super().__init__()
        self.append(CommandArgument(image_center))
        self.append(CommandFlag("noflip", noflip))
        self.append(CommandFlag("platesolve", force_plate_solve))
        self.append(CommandOption("focal", focal_length))
        self.append(CommandOption("pixelsize", pixel_size))
        if limit_mag == magnitude_option.MAGNITUDE_OFFSET and magnitude_value != 0.0:
            if magnitude_value > 0.0:
                self.append(CommandOption("limitmag", f"+{magnitude_value}"))
            else:
                self.append(CommandOption("limitmag", magnitude_value))
        elif limit_mag == magnitude_option.ABSOLUTE_MAGNITUDE:
            self.append(CommandOption("limitmag", magnitude_value))
        self.append(CommandOption("catalog", catalog))
        self.append(CommandFlag("downscale", downscale))


class platesolve(BaseCommand):
    """
    platesolve [image_center_coords] [-noflip] [-platesolve] [-focal=] [-pixelsize=] [-limitmag=[+-]] [-catalog=]
    [-localasnet] [-downscale]

    Plate solve the loaded image.
    If the image has already been plate solved nothing will be done, unless the <b>-platesolve</b> argument is passed to
    force a new solve. If WCS or other image metadata is erroneous or missing, arguments must be passed:
    the approximate image center coordinates can be provided in decimal degrees or degree/hour minute second values
    (J2000 with colon separators), with right ascension and declination values separated by a comma or a space (not
    mandatory for astrometry.net).
    focal length and pixel size can be passed with <b>-focal=</b> (in mm) and <b>-pixelsize=</b> (in microns),
    overriding values from image and settings.
    Unless <b>-noflip</b> is specified, if the image is detected as being upside-down, it will be flipped.
    For faster star detection in big images, downsampling the image is possible with <b>-downscale</b>.
    Images can be either plate solved by Siril using a star catalogue and the global registration algorithm or by
    astrometry.net's local solve-field command (enabled with <b>-localasnet</b>).
    The following options apply to Siril's plate solve only.
    The limit magnitude of stars used for plate solving is automatically computed from the size of the field of view,
    but can be altered by passing a +offset or -offset value to <b>-limitmag=</b>, or simply an absolute positive value
    for the limit magnitude.
    The choice of the star catalog is automatic unless the <b>-catalog=</b> option is passed: if local catalogs are
    installed, they are used, otherwise the choice is based on the field of view and limit magnitude. If the option is
    passed, it forces the use of the remote catalog given in argument, with possible values: tycho2, nomad, gaia, ppmxl,
    brightstars, apass
    """

    def __init__(
        self,
        image_center: t.Optional[str] = None,
        noflip: bool = False,
        force_plate_solve: bool = False,
        local_asnet: bool = False,
        downscale: bool = False,
        focal_length: t.Optional[float] = None,
        pixel_size: t.Optional[float] = None,
        limit_mag: magnitude_option = magnitude_option.DEFAULT_MAGNITUDE,
        magnitude_value: float = 0.0,
        catalog: star_catalog = None,
    ):
        super().__init__()
        self.append(CommandArgument(image_center))
        self.append(CommandFlag("noflip", noflip))
        self.append(CommandFlag("platesolve", force_plate_solve))
        self.append(CommandOption("focal", focal_length))
        self.append(CommandOption("pixelsize", pixel_size))
        if limit_mag == magnitude_option.MAGNITUDE_OFFSET and magnitude_value != 0.0:
            if magnitude_value > 0.0:
                self.append(CommandOption("limitmag", f"+{magnitude_value}"))
            else:
                self.append(CommandOption("limitmag", magnitude_value))
        elif limit_mag == magnitude_option.ABSOLUTE_MAGNITUDE:
            self.append(CommandOption("limitmag", magnitude_value))
        if local_asnet and catalog is not None:
            raise ValueError("catalog cannot be changed when using astrometry.net")
        self.append(CommandOption("catalog", catalog))
        self.append(CommandFlag("localasnet", local_asnet))
        self.append(CommandFlag("downscale", downscale))


class seqplatesolve(BaseCommand):
    """
    seqplatesolve sequencename [image_center_coords] [-noflip] [-platesolve] [-focal=] [-pixelsize=]
        [-limitmag=[+-]] [-catalog=] [-downscale]

    See platesolve, but for the sequence
    A new sequence will be created with the prefix "ps_".
    """

    def __init__(
        self,
        sequence: str,
        image_center: t.Optional[str] = None,
        noflip: bool = False,
        force_plate_solve: bool = False,
        local_asnet: bool = False,
        downscale: bool = False,
        focal_length: t.Optional[float] = None,
        pixel_size: t.Optional[float] = None,
        limit_mag: magnitude_option = magnitude_option.DEFAULT_MAGNITUDE,
        magnitude_value: float = 0.0,
        catalog: star_catalog = None,
    ):
        super().__init__()
        self.append(CommandArgument(sequence))
        self.append(CommandArgument(image_center))
        self.append(CommandFlag("noflip", noflip))
        self.append(CommandFlag("platesolve", force_plate_solve))
        self.append(CommandOption("focal", focal_length))
        self.append(CommandOption("pixelsize", pixel_size))
        if limit_mag == magnitude_option.MAGNITUDE_OFFSET and magnitude_value != 0.0:
            if magnitude_value > 0.0:
                self.append(CommandOption("limitmag", f"+{magnitude_value}"))
            else:
                self.append(CommandOption("limitmag", magnitude_value))
        elif limit_mag == magnitude_option.ABSOLUTE_MAGNITUDE:
            self.append(CommandOption("limitmag", magnitude_value))
        if local_asnet and catalog is not None:
            raise ValueError("catalog cannot be changed when using astrometry.net")
        self.append(CommandOption("catalog", catalog))
        self.append(CommandFlag("localasnet", local_asnet))
        self.append(CommandFlag("downscale", downscale))


class rmgreen_protection(Enum):
    AVERAGE_NEUTRAL = 0
    MAXIMUM_NEUTRAL = 1


class rmgreen(BaseCommand):
    """
    rmgreen [type]
    Applies a chromatic noise reduction filter. It removes green tint in the current image. This
    filter is based on PixInsight's SCNR Average Neutral algorithm and it is the same filter used by
    HLVG plugin in Photoshop.
    With the command, lightness is always preserved. For image processing without L* preservation,
    use the graphical tool and uncheck the corresponding box.
    <b>Type</b> can take values 0 for Average Neutral Protection or 1 for Maximum Neutral
    Protection, defaulting to 0
    """

    def __init__(self, protection: t.Optional[rmgreen_protection] = None):
        super().__init__()
        self.append(CommandArgument(protection))


class saturation_hue_range(Enum):
    PINK_ORANGE = 0
    ORANGE_YELLOW = 1
    YELLOW_CYAN = 2
    CYAN = 3
    CYAN_MAGENTA = 4
    MAGENTA_PINK = 5
    ALL = 6


class satu(BaseCommand):
    """
    satu amount [background_factor [hue_range_index]]
    Enhances the color saturation of the loaded image. Try iteratively to obtain best results.
    <b>amount</b> can be a positive number to increase color saturation, negative to decrease it, 0
    would do nothing, 1 would increase it by 100%
    <b>background_factor</b> is a factor to (median + sigma) used to set a threshold for which only
    pixels above it would be modified. This allows background noise to not be color saturated, if
    chosen carefully. Defaults to 1. Setting 0 disables the threshold.
    <b>hue_range_index</b> can be [0, 6], meaning: 0 for pink to orange, 1 for orange to yellow, 2
    for yellow to cyan, 3 for cyan, 4 for cyan to magenta, 5 for magenta to pink, 6 for all
    (default)")
    """

    def __init__(
        self,
        amount: float,
        background_factor: t.Optional[float] = None,
        hue_range: t.Optional[saturation_hue_range] = None,
    ):
        super().__init__()
        self.append(CommandArgument(amount))
        self.append(CommandArgument(background_factor))
        if background_factor is not None:
            self.append(CommandArgument(hue_range))


class savejpg(BaseCommand):
    """
    savejpg filename [quality]
    Saves current image into a JPG file: <b>filename</b>.jpg.

    You have the possibility to adjust the quality of the compression. A value 100 for <b>quality</b> parameter offers
    best fidelity while a low value increases the compression ratio. If no value is specified, a default value of 100
    is applied
    """

    def __init__(self, filename: str, quality: t.Optional[int] = None):
        super().__init__()
        self.append(CommandArgument(filename))
        self.append(CommandOptional(quality))


class savepng(BaseCommand):
    """
    Saves current image as a PNG file, with 16 bits per channel if the loaded image is 16 or 32 bits, and 8 bits per
    channel if the loaded image is 8 bits.
    """

    def __init__(self, filename: str):
        super().__init__()
        self.append(CommandArgument(filename))


class savetif(BaseCommand):
    """
    Saves current image under the form of a uncompressed TIFF file with 16-bit per channel: <b>filename</b>.tif
    """

    def __init__(self, filename: str):
        super().__init__()
        self.append(CommandArgument(filename))


class resample(BaseCommand):
    """
    Resamples image, either with a factor <b>factor</b> or for the target width or height provided by either of
    <b>-width=</b> or <b>-height=</b>. This is generally used to resize images, a factor of 0.5 divides size by 2.
    In the graphical user interface, we can see that several interpolation algorithms are proposed.

    The pixel interpolation method can be specified with the <b>-interp=</b> argument followed by one of the methods in
    the list <b>no</b>[ne], <b>ne</b>[arest], <b>cu</b>[bic], <b>la</b>[nczos4], <b>li</b>[near], <b>ar</b>[ea]}. If
    <b>none</b> is passed, the transformation is forced to shift and a pixel-wise shift is applied to each image without
    any interpolation.
    Clamping of the bicubic and lanczos4 interpolation methods is the default, to avoid artefacts, but can be disabled
    with the <b>-noclamp</b> argument
    """

    def __init__(
        self,
        factor: t.Optional[float] = None,
        target_width: t.Optional[int] = None,
        target_height: t.Optional[int] = None,
        interp: t.Optional[pixel_interpolation] = None,
    ):
        super().__init__()
        if factor is None and target_width is None and target_height is None:
            raise ValueError("Some indication about the size must be given")
        if target_width is not None and target_height is not None:
            raise ValueError("Only one indication about the target size can be given")
        self.append(CommandArgument(factor))
        self.append(CommandOption("width", target_width))
        self.append(CommandOption("height", target_height))
        self.append(CommandOption("interp", interp))


class crop(BaseCommand):
    """
    It can be used with the GUI: if a selection has been made with the mouse, calling the crop command without
    arguments crops it on this selection. Otherwise, or in scripts, arguments have to be given, with x and y being the
    coordinates of the top left corner, and width and height the size of the selection.
    """

    def __init__(self, x, y, width, height):
        super().__init__()
        self.append(CommandArgument(f"{x} {y} {width} {height}"))


class seqcrop(BaseCommand):
    """
    Crops the sequence given in the seqname argument. The output sequence name starts with the prefix "cropped_"
    unless otherwise specified with -prefix= option. Only selected images in the sequence are processed.
    """

    def __init__(self, seq: str, x, y, width, height, prefix: t.Optional[str] = None):
        super().__init__()
        self.append(CommandArgument(seq))
        self.append(CommandArgument(f"{x} {y} {width} {height}"))
        self.append(CommandOption("prefix", prefix))


class dumpheader(BaseCommand):
    """
    Prints the FITS header of the currently loaded image, if any.
    """

    def __init__(self):
        super().__init__()


class neg(BaseCommand):
    """
    Changes pixel values of the currently loaded image to a negative view, like 1-value for 32 bits, 65535-value for 16
    bits. This does not change the display mode
    """

    def __init__(self):
        super().__init__()


class mirrorx(BaseCommand):
    """
    Flips the image about the vertical axis. Option <b>-bottomup</b> will only flip it if it's not already bottom-up
    """

    def __init__(self, bottom_up: bool = True):
        super().__init__()
        self.append(CommandFlag("bottomup", bottom_up))


class mirrorx_single(BaseCommand):
    """
    Flips the image about the vertical axis, only if needed (if it's not already bottom-up). It takes the image file
    name as argument, allowing it to avoid reading image data entirely if no flip is required
    """

    def __init__(self, imagename: str):
        super().__init__()
        self.append(CommandArgument(imagename))


class jsonmetadata(BaseCommand):
    """
    jsonmetadata FITS_file [-stats_from_loaded] [-nostats] [-out=]
    Dumps metadata and statistics of the currently loaded image in JSON form. The file name is required, even if the
    image is already loaded. Statistics can be disabled by providing the <b>-nostats</b> option. A file containing the
    JSON data is created with default file name out.json and can be changed with the <b>-out=</b> option
    """

    def __init__(
        self, filename: str, stats_from_loaded: bool = False, no_stats: bool = False, out: t.Optional[str] = None
    ):
        super().__init__()
        self.append(CommandArgument(filename))
        self.append(CommandFlag("stats_from_loaded", stats_from_loaded))
        self.append(CommandFlag("nostats", no_stats))
        self.append(CommandOption("out", out))


class split(BaseCommand):
    """
    Splits the color image into three distinct files (one for each color) and save them in <b>fileR</b>.fit,
    <b>fileG</b>.fit and <b>fileB</b>.fit files
    """

    def __init__(self, red: str = "r", green: str = "g", blue: str = "b"):
        super().__init__()
        self.append(CommandArgument(red))
        self.append(CommandArgument(green))
        self.append(CommandArgument(blue))


class light_curve(BaseCommand):
    """
    light_curve sequencename channel [-autoring] { -at=x,y | -wcs=ra,dec } { -refat=x,y | -refwcs=ra,dec } ...
    light_curve sequencename channel [-autoring] -ninastars=file
    Analyse several stars with aperture photometry in a sequence of images and produce a light curve for one, calibrated
    by the others. The first coordinates, in pixels if -at= is used or in degrees if -wcs= is used, are for the star
    whose light will be plotted, the others for the reference stars.

    Alternatively, a list of target and reference stars can be passed in the format of the NINA exolpanet plugin star
    list, with the -ninastars= option. Siril will verify that all reference stars can be used before actually using
    them. A data file is created in the current directory named light_curve.dat, gnuplot plots the result to a PNG image
    if available.

    The ring radii for aperture photometry can either be configured in the settings or set to a factor of the reference
    image's FWHM if <b>-autoring</b> is passed.

    See also SEQPSF for operations on single star.
    """

    def __init__(self, seq: str, nina_file: str, auto_ring_size: bool = False):
        super().__init__()
        self.append(CommandArgument(seq))
        self.append(CommandArgument(0))
        self.append(CommandFlag("autoring", auto_ring_size))
        self.append(CommandOption("ninastars", nina_file))


class setfindstar(BaseCommand):
    """
    setfindstar [reset] [-radius=] [-sigma=] [-roundness=] [-focal=] [-pixelsize=] [-convergence=] [ [-gaussian] |
    [-moffat] ] [-minbeta=] [-relax=on|off] [-minA=] [-maxA=]

    Defines stars detection parameters for FINDSTAR and REGISTER commands.
    Passing no parameter lists the current values.
    Passing <b>reset</b> resets all values to defaults. You can then still pass values after this keyword.
    Configurable values:
    <b>-radius=</b> defines the radius of the initial search box and must be between 3 and 50.
    <b>-sigma=</b> defines the threshold above noise and must be greater or equal to 0.05.
    <b>-roundness=</b> defines minimum star roundness and must between 0 and 0.95.
    <b>-minA</b> and <b>-maxA</b> define limits for the minimum and maximum amplitude of stars to keep, normalized
    between 0 and 1.
    <b>-focal=</b> defines the focal length of the telescope.
    <b>-pixelsize=</b> defines the pixel size of the sensor.
    <b>-gaussian</b> and <b>-moffat</b> configure the solver model to be used (Gaussian is the default).
    If Moffat is selected, <b>-minbeta=</b> defines the minimum value of beta for which candidate stars will be accepted
    and must be greater or equal to 0.0 and less than 10.0.
    <b>-convergence=</b> defines the number of iterations performed to fit PSF and should be set between 1 and 3 (more
    tolerant).
    <b>-relax=</b> relaxes the checks that are done on star candidates to assess if they are stars or not, to allow
    objects not shaped like stars to still be accepted (off by default)
    """

    def __init__(
        self,
        reset: bool = None,
        radius: float = None,
        sigma: float = None,
        roundness: float = None,
        focal: float = None,
        pixsize: float = None,
        convergence: int = None,
        gaussian: bool = False,
        moffat: bool = False,
        min_beta: float = None,
        relax: bool = None,
        minA: float = None,
        maxA: float = None,
    ):
        super().__init__()
        if reset is not None and reset:
            self.append(CommandArgument("reset"))
        self.append(CommandOption("radius", radius))
        self.append(CommandOption("sigma", sigma))
        if roundness is not None and (roundness < 0 or roundness >= 1):
            raise ValueError("roundness can be between 0 and 0.95")
        self.append(CommandOption("roundness", roundness))
        self.append(CommandOption("focal", focal))
        self.append(CommandOption("pixelsize", pixsize))
        if convergence is not None and (convergence < 1 or convergence > 3):
            raise ValueError("convergence can only have a value between 1 and 3")
        self.append(CommandOption("convergence", convergence))
        if moffat and gaussian:
            raise ValueError("only one of Moffat or Gaussian model can be used")
        self.append(CommandFlag("moffat", moffat))
        self.append(CommandFlag("gaussian", gaussian))
        if min_beta is not None and not moffat:
            raise ValueError("min_beta is only for the Moffat profile")
        self.append(CommandOption("minbeta", min_beta))
        if relax is not None:
            if relax:
                self.append(CommandOption("relax", "yes"))
            else:
                self.append(CommandOption("relax", "no"))
        self.append(CommandOption("minA", minA))
        self.append(CommandOption("maxA", maxA))


class findstar(BaseCommand):
    """
    findstar [-out=] [-layer=] [-maxstars=]

    Detects stars in the currently loaded image, having a level greater than a threshold computed by Siril.
    After that, a PSF is applied and Siril rejects all detected structures that don't fulfill a set of prescribed
    detection criteria, that can be tuned with command SETFINDSTAR.
    Finally, a circle is drawn around detected stars.
    Optional parameter <b>-out=</b> enables to save the results to the given path.
    Option <b>-layer=</b> specifies the layer onto which the detection is performed (for color images only).
    You can also limit the max number of stars detected by passing a value to option <b>-maxstars=</b>.
    See also the command CLEARSTAR
    """

    def __init__(self, out: t.Optional[str] = None, layer: int = None, max_stars: int = None):
        super().__init__()
        self.append(CommandOption("out", out))
        self.append(CommandOption("layer", layer))
        self.append(CommandOption("maxstars", max_stars))


class seqfindstar(BaseCommand):
    """
    seqfindstar sequencename [-layer=] [-maxstars=]

    Same command as FINDSTAR but for the sequence <b>sequencename</b>.
    The option <b>-out=</b> is not available for this process as all the star list files are saved with the default name
    <i>seqname_seqnb.lst</i>
    """

    def __init__(self, sequence: str, layer: int = None, max_stars: int = None):
        super().__init__()
        self.append(CommandArgument(sequence))
        self.append(CommandOption("layer", layer))
        self.append(CommandOption("maxstars", max_stars))


class seqextract_Green(BaseCommand):
    """
    seqextract_Green sequencename [-prefix=]

    Same command as EXTRACT_GREEN (extracts green signal from a CFA image) but for the sequence <b>sequencename</b>.
    The output sequence name starts with the prefix \"Green_\" unless otherwise specified with option <b>-prefix=</b>
    """

    def __init__(self, sequence: str, prefix: t.Optional[str] = None):
        super().__init__()
        self.append(CommandArgument(sequence))
        self.append(CommandOption("prefix", prefix))


class seqfind_cosme(BaseCommand):
    """
    seqfind_cosme sequencename cold_sigma hot_sigma [-prefix=]

    Same command as FIND_COSME but for the sequence sequencename.
    The output sequence name starts with the prefix "cc_" unless otherwise specified with -prefix= option
    """

    def __init__(self, sequence: str, sigma_low: float, sigma_high: float, prefix: t.Optional[str] = None):
        super().__init__()
        self.append(CommandArgument(sequence))
        self.append(CommandArgument(sigma_low))
        self.append(CommandArgument(sigma_high))
        self.append(CommandOption("prefix", prefix))


#
# Siril SDA-specific commands (non-published)
#


class seqdetect_trail(BaseCommand):
    """
    sedetect_trail sequencename [{ -include | -exclude }] [-resume] [-test] [-out=csv_file]

    Same command as DETECT_TRAIL but for the sequence <b>sequencename</b>.
    Depending on the optional argument <b>-include</b> or <b>-exclude</b>, the images detected with streaks can be the
    only one left included or excluded in the sequence. If detection was first done on images without an astrometric
    solution that created the .streaks file and the concerned images were plate solved since, the <b>-resume</b> option
    can be used to remake a pass on the sequence and convert the streaks into data
    """

    def __init__(
        self,
        sequence: str,
        include: bool = False,
        exclude: bool = False,
        resume: bool = False,
        out: t.Optional[str] = None,
    ):
        if include and exclude:
            raise ValueError("include and exclude are mutually exclusive for command seqdetect_trail")
        super().__init__()
        self.append(CommandArgument(sequence))
        self.append(CommandFlag("include", include))
        self.append(CommandFlag("exclude", exclude))
        self.append(CommandFlag("resume", resume))
        self.append(CommandOption("out", out))


class detect_trail(BaseCommand):
    """
    detect_trail [-test]

    Automatically detect between one and three streaks in the loaded image, saving the coordinates in pixels in a CSV
    .streaks file or the equatorial coordinates in a CSV file if it has an astrometric solution. <b>-test</b> only tests
    streak detection, does not save results.
    """


class gaiacompare(BaseCommand):
    """
    gaiacompare [limit_magnitude]

    Compares positions of stars in the image with stars in the Gaia DR3 catalog, outputs a CSV containing both and more.
    Optional argument is the limit magnitude of the catalog to download, defaults to 12.0
    """

    def __init__(self, limit_mag: t.Optional[float] = None):
        super().__init__()
        self.append(CommandArgument(limit_mag))


class seqgaiacompare(BaseCommand):
    """
    gaiacompare sequencename [limit_magnitude]

    Same as GAIACOMPARE but for the sequence <b>sequencename</b>.
    """

    def __init__(self, sequence: str, limit_mag: t.Optional[float] = None):
        super().__init__()
        self.append(CommandArgument(sequence))
        self.append(CommandArgument(limit_mag))
