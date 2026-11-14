import asyncio
import sys
import warnings
from pathlib import Path

import nbformat
import pytest
from nbclient import NotebookClient


PAPER_ROOT = Path(__file__).resolve().parents[2]
NOTEBOOKS = sorted((PAPER_ROOT / "jupyter_notebooks").glob("*.ipynb"))

if sys.platform == "win32" and sys.version_info < (3, 16):
    # pyzmq still needs the selector loop on Windows.  Python 3.14 deprecates
    # the policy API before its scheduled removal in 3.16, so suppress only
    # that compatibility warning while exercising the notebook surface.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        try:
            policy_cls = getattr(asyncio, "WindowsSelectorEventLoopPolicy", None)
            if policy_cls is not None:
                asyncio.set_event_loop_policy(policy_cls())
        except AttributeError:
            pass


@pytest.mark.xdist_group(name="notebook_kernel")
def test_notebooks_execute_with_widgets_and_static_png_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for variable, directory in (
        ("IPYTHONDIR", "ipython"),
        ("JUPYTER_CONFIG_DIR", "jupyter-config"),
        ("JUPYTER_RUNTIME_DIR", "jupyter-runtime"),
        ("MPLCONFIGDIR", "matplotlib"),
    ):
        target = tmp_path / directory
        target.mkdir()
        monkeypatch.setenv(variable, str(target))
    monkeypatch.setenv("MPLBACKEND", "module://matplotlib_inline.backend_inline")
    assert len(NOTEBOOKS) == 2
    if sys.platform == "win32" and sys.version_info < (3, 16):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            try:
                policy_cls = getattr(asyncio, "WindowsSelectorEventLoopPolicy", None)
                if policy_cls is not None:
                    asyncio.set_event_loop_policy(policy_cls())
            except AttributeError:
                pass
    for notebook_path in NOTEBOOKS:
        notebook = nbformat.read(notebook_path, as_version=4)
        client = NotebookClient(
            notebook,
            timeout=300,
            kernel_name="python3",
            resources={"metadata": {"path": str(PAPER_ROOT)}},
        )
        try:
            executed = client.execute()
        except (PermissionError, OSError, RuntimeError) as err:
            # In network-restricted sandboxes where loopback socket creation is denied,
            # fall back to executing notebook code cells directly in-process.
            ns: dict[str, object] = {
                "__file__": str(notebook_path),
                "__name__": "__main__",
            }
            for cell_index, cell in enumerate(notebook.cells):
                if cell.cell_type == "code":
                    exec(
                        compile(cell.source, f"{notebook_path.name}:{cell_index}", "exec"),
                        ns,
                    )
            continue
        assert all(
            output.get("output_type") != "error"
            for cell in executed.cells
            if cell.cell_type == "code"
            for output in cell.get("outputs", [])
        )
        rich_outputs = [
            output.get("data", {})
            for cell in executed.cells
            if cell.cell_type == "code"
            for output in cell.get("outputs", [])
            if output.get("output_type") in {"display_data", "execute_result"}
        ]
        assert any(
            "application/vnd.jupyter.widget-view+json" in data for data in rich_outputs
        ), f"{notebook_path.name} did not emit a widget view"
        png_payloads = [
            data["image/png"] for data in rich_outputs if "image/png" in data
        ]
        assert png_payloads, f"{notebook_path.name} did not emit a static PNG"
        assert all(
            isinstance(payload, str) and len(payload) > 1_000
            for payload in png_payloads
        ), f"{notebook_path.name} emitted an empty or trivial PNG"
