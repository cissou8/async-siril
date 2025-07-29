import async_siril.command as command
from async_siril.command_types import saturation_hue_range
from async_siril.command_types import pixel_interpolation
from async_siril.command_types import magnitude_option
from async_siril.command_types import star_catalog


def test_autostretch():
    _command = command.autostretch(linked=True, target_background=0.15, shadows_clipping=-10)
    assert str(_command) == "autostretch -linked -10 0.15"
    assert _command.valid


def test_autostretch_default():
    _command = command.autostretch()
    assert str(_command) == "autostretch"
    assert _command.valid


def test_asinh():
    _command = command.asinh(100)
    assert str(_command) == "asinh 100"
    assert _command.valid


def test_asinh_all():
    _command = command.asinh(100, True, 0.001)
    assert str(_command) == "asinh -human 100 0.001"
    assert _command.valid


def test_rgbcomp():
    _command = command.rgbcomp(red_image="r", green_image="g", blue_image="b")
    assert str(_command) == "rgbcomp r g b"
    assert _command.valid


def test_rgbcomp_all():
    _command = command.rgbcomp(luminance="L_stacked", red_image="r", green_image="g", blue_image="b", out="supercompo")
    assert str(_command) == "rgbcomp -lum=L_stacked r g b -out=supercompo"
    assert _command.valid


def test_pcc():
    _command = command.pcc()
    assert str(_command) == "pcc"
    assert _command.valid


def test_pcc_with_ps():
    _command = command.pcc(catalog=star_catalog.GAIA)
    assert str(_command) == "pcc -catalog=gaia"
    assert _command.valid


def test_platesolve_simple():
    _command = command.platesolve(
        noflip=True, force_plate_solve=False, limit_mag=magnitude_option.MAGNITUDE_OFFSET, magnitude_value=2
    )
    assert str(_command) == "platesolve -noflip -limitmag=+2"
    assert _command.valid


def test_platesolve_asnet():
    _command = command.platesolve(local_asnet=True, downscale=True)
    assert str(_command) == "platesolve -downscale -localasnet"
    assert _command.valid


def test_platesolve_with_data():
    _command = command.platesolve(
        image_center="270.675000,-22.971667", force_plate_solve=True, focal_length=1800, pixel_size=5.4
    )
    assert str(_command) == "platesolve -force 270.675000,-22.971667 -focal=1800 -pixelsize=5.4"
    assert _command.valid


def test_seqplatesolve():
    _command = command.seqplatesolve("theseq", local_asnet=True)
    assert str(_command) == "seqplatesolve theseq -localasnet"
    assert _command.valid


def test_rmgreen():
    _command = command.rmgreen()
    assert str(_command) == "rmgreen"
    assert _command.valid


def test_saturation():
    _command = command.satu(1.5, 0.5, saturation_hue_range.ALL)
    assert str(_command) == "satu 1.5 0.5 6"
    assert _command.valid


def test_savejpg():
    _command = command.savejpg("superfile", 94)
    assert str(_command) == "savejpg superfile 94"
    assert _command.valid


def test_savetiff():
    _command = command.savetif("superfile")
    assert str(_command) == "savetif superfile"
    assert _command.valid


def test_neg():
    _command = command.neg()
    assert str(_command) == "neg"
    assert _command.valid


def test_mirrorx():
    _command = command.mirrorx()
    assert str(_command) == "mirrorx -bottomup"


def test_mirrorx_single():
    _command = command.mirrorx_single("myimage.fit")
    assert str(_command) == "mirrorx_single myimage.fit"


def test_split():
    _command = command.split("r", "g", "b")
    assert str(_command) == "split r g b"
    assert _command.valid


def test_resample_ratio():
    _command = command.resample(factor=0.4)
    assert str(_command) == "resample 0.4"
    assert _command.valid


def test_resample_target():
    _command = command.resample(target_height=400, interp=pixel_interpolation.INTERP_AREA)
    assert str(_command) == "resample -height=400 -interp=area"
    assert _command.valid


def test_resample_2targets():
    failed = False
    try:
        command.resample(target_height=800, target_width=600)
    except ValueError:
        failed = True
    assert failed


def test_light_curve():
    _command = command.light_curve("the_sequence", "0", ninastars="TYC 2688-1839-1.csv")
    assert str(_command) == "light_curve the_sequence 0 '-ninastars=TYC 2688-1839-1.csv'"
    assert _command.valid


def test_light_curve_auto():
    _command = command.light_curve("the_sequence", "0", autoring=True, ninastars="TYC 2688-1839-1.csv")
    assert str(_command) == "light_curve the_sequence 0 -autoring '-ninastars=TYC 2688-1839-1.csv'"
    assert _command.valid


def test_findstar():
    _command = command.findstar(out="stars.lst", layer=1)
    assert str(_command) == "findstar -out=stars.lst -layer=1"
    assert _command.valid


def test_seqfindstar():
    _command = command.seqfindstar("the_sequence", 1, 1500)
    assert str(_command) == "seqfindstar the_sequence -layer=1 -maxstars=1500"
    assert _command.valid
