import async_siril.command as command
from async_siril.command_types import fits_extension
from async_siril.command_types import compression_type


def test_setext():
    _command = command.setext(fits_extension.FITS_EXT_FITS)
    assert str(_command) == "setext fits"
    assert _command.valid


def test_set16bits():
    _command = command.set16bits()
    assert str(_command) == "set16bits"
    assert _command.valid


def test_cd():
    _command = command.cd("/tmp/tmp-a5cab44")
    assert str(_command) == "cd /tmp/tmp-a5cab44"
    assert _command.valid


def test_setcomp_off():
    _command = command.setcompress(False)
    assert str(_command) == "setcompress 0"
    assert _command.valid


def test_setcomp_on():
    _command = command.setcompress(True, compression_type.COMPRESSION_GZIP1, 16)
    assert str(_command) == "setcompress 1 -type=gzip1 16"
    assert _command.valid


def test_subsky():
    _command = command.subsky(degree=2, samples=30)
    assert str(_command) == "subsky 2 -samples=30"
    assert _command.valid


def test_seqsubsky():
    _command = command.seqsubsky(sequence="pp_light_", tolerance=0.5)
    assert str(_command) == "seqsubsky pp_light_ 1 -tolerance=0.5"
    assert _command.valid


def test_set():
    _command = command.set(key="core.mem_mode", value="1")
    assert str(_command) == "set core.mem_mode=1"
    assert _command.valid


def test_seqextract_HaOIII():
    _command = command.seqextract_HaOIII("pp_light")
    assert str(_command) == "seqextract_HaOIII pp_light"
    assert _command.valid


def test_jsonmetadata():
    _command = command.jsonmetadata("test", out="dump.json")
    assert str(_command) == "jsonmetadata test -out=dump.json"
    assert _command.valid
