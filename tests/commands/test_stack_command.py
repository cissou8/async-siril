import async_siril.command as command
import async_siril.command_types as ct


class TestStackCommand:
    def test_stack_rej_default(self):
        _command = command.stack("sequence")
        assert str(_command) == "stack sequence rej w 3 3 -nonorm"
        assert _command.valid

    def test_stack_for_master_flat_creation(self):
        _command = command.stack(
            base_name="sequence",
            _type=ct.stack_type.STACK_REJ,
            norm=ct.stack_norm.NORM_MUL,
            rejection=ct.stack_rejection.REJECTION_WINSORIZED,
            fast_norm=True,
            rgb_equalization=False,
            out="master_flat",
        )
        assert str(_command) == "stack sequence rej w 3 3 -norm=mul -fastnorm -out=master_flat"
        assert _command.valid

    def test_stack_rej_main_color_stack(self):
        _command = command.stack(
            base_name="sequence",
            _type=ct.stack_type.STACK_REJ,
            norm=ct.stack_norm.NORM_ADD_SCALE,
            rejection=ct.stack_rejection.REJECTION_GESDT,
            lower_rej=3.5,
            higher_rej=3.5,
            filters=[
                command.SequenceFilter(ct.sequence_filter_type.FILTER_FWHM, percent=80),
                command.SequenceFilter(ct.sequence_filter_type.FILTER_ROUNDNESS, value=0.88),
            ],
            filter_included=True,
            fast_norm=True,
            output_norm=True,
            weighting=ct.stack_weighting.WEIGHT_FROM_WFWHM,
            rgb_equalization=True,
        )
        assert (
            str(_command) == "stack sequence rej g 3.5 3.5 -norm=addscale "
            "-filter-fwhm=80% -filter-round=0.88 -filter-incl "
            "-fastnorm -output_norm -weight_from_wfwhm -rgb_equal"
        )
        assert _command.valid

    def test_stack_rej_with_maps(self):
        _command = command.stack("sequence", create_rejection_maps=ct.stack_rejmaps.MERGED_REJECTION_MAPS)
        assert str(_command) == "stack sequence rej w 3 3 -rejmap -nonorm"
        assert _command.valid
