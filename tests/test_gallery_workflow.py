import json

from PIL import Image

from figure_studio.gallery import GalleryIndex, search_references
from tests.test_task_runner import _write_brief, _write_manifest, _write_renderer
from tools.run_figure_task import run_figure_task


def test_selected_gallery_reference_is_recorded_separately_from_nature_context(tmp_path):
    gallery_root = tmp_path / "gallery"
    image = gallery_root / "04_my_favorites" / "accepted.png"
    image.parent.mkdir(parents=True)
    Image.new("RGB", (80, 60), "#166A8F").save(image)
    gallery = GalleryIndex(gallery_root)
    records = gallery.scan()
    records[0].favorite = True
    records[0].chart_type = "convergence"
    records[0].application = "algorithm comparison"
    gallery.write_index(records)

    selected = search_references(
        gallery_root,
        query="algorithm",
        chart_type="convergence",
        application="algorithm comparison",
    )
    assert selected[0].relative_path == "04_my_favorites/accepted.png"

    source = tmp_path / "source"
    source.mkdir()
    renderer = _write_renderer(source)
    data_path = source / "practice.csv"
    data_path.write_text("x,y\n0,2\n1,1\n2,0.8\n", encoding="utf-8")
    manifest = _write_manifest(source, data_path)
    brief = source / "figure_brief.json"
    _write_brief(brief)
    payload = json.loads(brief.read_text(encoding="utf-8"))
    payload["gallery_references"] = ["04_my_favorites/accepted.png"]
    payload["code_references"] = ["plot.py"]
    brief.write_text(json.dumps(payload), encoding="utf-8")

    output = tmp_path / "output"
    run_figure_task(
        renderer=renderer,
        brief_path=brief,
        output_dir=output,
        data_path=data_path,
        manifest_path=manifest,
        gallery_root=gallery_root,
    )
    receipt = json.loads((output / "design_receipt.json").read_text(encoding="utf-8"))
    assert receipt["references"]["gallery"][0]["relative_path"] == (
        "04_my_favorites/accepted.png"
    )
    assert receipt["references"]["code"] == ["plot.py"]
    assert receipt["references"]["code_records"][0]["sha256"]
    assert receipt["nature"]["requested"] is False
