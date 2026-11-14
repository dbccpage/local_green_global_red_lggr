from pathlib import Path

import matplotlib.image as mpimg
import numpy as np

from generate_figures import generate_all


PAPER_ROOT = Path(__file__).resolve().parents[2]


def test_publication_figures_are_generated_reproducibly(tmp_path: Path) -> None:
    outputs = generate_all(tmp_path / "nested")
    assert [path.name for path in outputs] == [
        "figure_1_kernel_and_adjoint.png",
        "figure_1_kernel_and_adjoint.pdf",
        "figure_2_sign_probe_error.png",
        "figure_2_sign_probe_error.pdf",
    ]
    assert all(path.stat().st_size > 1_000 for path in outputs)
    first = generate_all(tmp_path / "first")
    second = generate_all(tmp_path / "second")
    for f, s in zip(first, second):
        assert f.stat().st_size > 1_000 and s.stat().st_size > 1_000
        if f.suffix == ".png":
            np.testing.assert_allclose(mpimg.imread(f), mpimg.imread(s), atol=1e-3)
        elif f.suffix == ".pdf":
            assert f.read_bytes().startswith(b"%PDF")
            assert s.read_bytes().startswith(b"%PDF")

    generated = generate_all(tmp_path)
    for gen_path in generated:
        committed_path = PAPER_ROOT / "figures" / gen_path.name
        assert committed_path.is_file()
        assert gen_path.stat().st_size > 1_000
        assert committed_path.stat().st_size > 1_000
        if gen_path.suffix == ".png":
            np.testing.assert_allclose(
                mpimg.imread(gen_path), mpimg.imread(committed_path), atol=1e-3
            )
        elif gen_path.suffix == ".pdf":
            assert gen_path.read_bytes().startswith(b"%PDF")
            assert committed_path.read_bytes().startswith(b"%PDF")
