import async_siril.command as command

from async_siril.command import SequenceFilter
from async_siril.command_types import pixel_interpolation
from async_siril.command_types import registration_transformation
from async_siril.command_types import sequence_framing
from async_siril.command_types import sequence_filter_type


def test_register_default():
    _command = command.register("sequence")
    assert str(_command) == "register sequence"
    assert _command.valid


def test_register_one_pass_all_options():
    _command = command.register(
        "sequence",
        two_pass=False,
        drizzle=True,
        selected=True,
        prefix="registered_",
        min_pairs=12,
        trans_func=registration_transformation.REG_TRANSF_AFFINE,
        layer=1,
        max_stars=600,
        interp=pixel_interpolation.INTERP_LANCZOS4,
    )
    assert (
        str(_command) == "register sequence -selected -prefix=registered_ -layer=1 "
        "-transf=affine -minpairs=12 -maxstars=600 -interp=lanczos4 -drizzle"
    )
    assert _command.valid


def test_register_shift_only():
    _command = command.register(
        "sequence",
        selected=True,
        trans_func=registration_transformation.REG_TRANSF_SHIFT,
        max_stars=600,
        interp=pixel_interpolation.INTERP_NONE,
    )
    assert str(_command) == "register sequence -selected -transf=shift -maxstars=600 -interp=none"
    assert _command.valid


def test_register_noout():
    _command = command.register(
        "sequence",
        prefix="unused",
        layer=1,
        trans_func=registration_transformation.REG_TRANSF_SIMILARITY,
        interp=pixel_interpolation.INTERP_AREA,
    )
    assert str(_command) == "register sequence -prefix=unused -layer=1 -transf=similarity -interp=area"
    assert _command.valid


def test_register_2pass():
    _command = command.register(
        "sequence", two_pass=True, prefix="unused", max_stars=1000, interp=pixel_interpolation.INTERP_AREA
    )
    assert str(_command) == "register sequence -2pass -prefix=unused -maxstars=1000"
    assert _command.valid


def test_seqapplyreg_simple():
    _command = command.seqapplyreg("sequence", prefix="registered_")
    assert str(_command) == "seqapplyreg sequence -prefix=registered_"
    assert _command.valid


def test_seqapplyreg_full():
    _command = command.seqapplyreg(
        "sequence",
        prefix="prefix",
        layer=1,
        framing=sequence_framing.FRAME_COG,
        interp=pixel_interpolation.INTERP_CUBIC,
        drizzle=True,
        filters=[
            SequenceFilter(sequence_filter_type.FILTER_WFWHM, percent=80),
            SequenceFilter(sequence_filter_type.FILTER_INCLUSION),
        ],
    )
    assert (
        str(_command) == "seqapplyreg sequence -prefix=prefix -layer=1 -framing=cog -interp=cubic "
        "-drizzle -filter-wfwhm=80% -filter-incl"
    )
    assert _command.valid
