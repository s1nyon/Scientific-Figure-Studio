import matplotlib.pyplot as plt

from figure_studio.fonts import resolve_fonts
from figure_studio.style import figure_style


def test_chinese_math_figure_is_nonblank(tmp_path):
    report = resolve_fonts()
    with figure_style("minimal_editorial", canvas="compact"):
        figure, axis = plt.subplots(figsize=(3.2, 2.2))
        axis.set(xlabel="时间 (小时)", ylabel="误差 $E$", title="中文字体测试")
        axis.plot([0, 1], [1, 0], color="#166A8F")
        path = tmp_path / "font-test.png"
        figure.savefig(path, dpi=200, bbox_inches="tight")
        plt.close(figure)
    assert path.stat().st_size > 0
    assert report.english_family
    assert isinstance(report.warnings, tuple)

