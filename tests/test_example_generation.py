from tools.generate_examples import main as generate_examples


def test_example_generator_creates_independent_delivery_directories(tmp_path):
    outputs = generate_examples(output_root=tmp_path)
    assert len(outputs) == 6
    for folder in outputs:
        assert (folder / "plot.py").exists()
        assert (folder / "config.py").exists()
        assert (folder / "data_manifest.json").exists()
        assert (folder / "README.md").exists()
        assert (folder / "figure.png").exists()
        assert (folder / "figure.svg").exists()
        assert (folder / "figure.pdf").exists()
        assert (folder / "generation_manifest.json").exists()
