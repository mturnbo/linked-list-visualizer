from main import main


def test_main_raises_without_values_or_ops_file(monkeypatch):
    monkeypatch.setattr("sys.argv", ["main.py", "print"])
    with pytest.raises(ValueError, match="Must specify either values or operations file"):
        main()
