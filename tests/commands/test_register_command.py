import async_siril.command as command
import async_siril.command_types as ct


class TestRegisterCommand:
    def test_register_default(self):
        _command = command.register("sequence")
        assert str(_command) == "register sequence"
        assert _command.valid

    def test_register_one_pass_all_options(self):
        _command = command.register(
            "sequence",
            two_pass=False,
            drizzle=True,
            selected=True,
            prefix="registered_",
            min_pairs=12,
            trans_func=ct.registration_transformation.REG_TRANSF_AFFINE,
            layer=1,
            max_stars=600,
            interp=ct.pixel_interpolation.INTERP_LANCZOS4,
        )
        assert (
            str(_command) == "register sequence -selected -prefix=registered_ -layer=1 "
            "-transf=affine -minpairs=12 -maxstars=600 -interp=lanczos4 -drizzle"
        )
        assert _command.valid

    def test_register_shift_only(self):
        _command = command.register(
            "sequence",
            selected=True,
            trans_func=ct.registration_transformation.REG_TRANSF_SHIFT,
            max_stars=600,
            interp=ct.pixel_interpolation.INTERP_NONE,
        )
        assert str(_command) == "register sequence -selected -transf=shift -maxstars=600 -interp=none"
        assert _command.valid

    def test_register_noout(self):
        _command = command.register(
            "sequence",
            prefix="unused",
            layer=1,
            trans_func=ct.registration_transformation.REG_TRANSF_SIMILARITY,
            interp=ct.pixel_interpolation.INTERP_AREA,
        )
        assert str(_command) == "register sequence -prefix=unused -layer=1 -transf=similarity -interp=area"
        assert _command.valid

    def test_register_2pass(self):
        _command = command.register(
            "sequence", two_pass=True, prefix="unused", max_stars=1000, interp=ct.pixel_interpolation.INTERP_AREA
        )
        assert str(_command) == "register sequence -2pass -prefix=unused -maxstars=1000"
        assert _command.valid


class TestSeqApplyRegCommand:
    def test_seqapplyreg_simple(self):
        _command = command.seqapplyreg("sequence", prefix="registered_")
        assert str(_command) == "seqapplyreg sequence -prefix=registered_"
        assert _command.valid

    def test_seqapplyreg_full(self):
        _command = command.seqapplyreg(
            "sequence",
            prefix="prefix",
            layer=1,
            framing=ct.sequence_framing.FRAME_COG,
            interp=ct.pixel_interpolation.INTERP_CUBIC,
            drizzle=True,
            filters=[
                command.SequenceFilter(ct.sequence_filter_type.FILTER_WFWHM, percent=80),
                command.SequenceFilter(ct.sequence_filter_type.FILTER_INCLUSION),
            ],
        )
        assert (
            str(_command) == "seqapplyreg sequence -prefix=prefix -layer=1 -framing=cog -interp=cubic "
            "-drizzle -filter-wfwhm=80% -filter-incl"
        )
        assert _command.valid


class TestPlatesolveCommand:
    def test_platesolve_simple(self):
        _command = command.platesolve(
            noflip=True, force_plate_solve=False, limit_mag=ct.magnitude_option.MAGNITUDE_OFFSET, magnitude_value=2
        )
        assert str(_command) == "platesolve -noflip -limitmag=+2"
        assert _command.valid

    def test_platesolve_asnet(self):
        _command = command.platesolve(local_asnet=True, downscale=True)
        assert str(_command) == "platesolve -downscale -localasnet"
        assert _command.valid

    def test_platesolve_with_data(self):
        _command = command.platesolve(
            image_center="270.675000,-22.971667", force_plate_solve=True, focal_length=1800, pixel_size=5.4
        )
        assert str(_command) == "platesolve -force 270.675000,-22.971667 -focal=1800 -pixelsize=5.4"
        assert _command.valid


class TestSeqPlatesolveCommand:
    def test_seqplatesolve(self):
        _command = command.seqplatesolve("theseq", local_asnet=True)
        assert str(_command) == "seqplatesolve theseq -localasnet"
        assert _command.valid
