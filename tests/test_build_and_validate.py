import subprocess
from pathlib import Path


def test_build_creates_backtest(tmp_path):
    # run build script
    res = subprocess.run(['python3', 'scripts/build_pine.py'], capture_output=True, text=True)
    assert res.returncode == 0, f"build_pine failed: {res.stdout}\n{res.stderr}"
    out = Path('pine/backtest.pine')
    assert out.exists()
    text = out.read_text(encoding='utf-8')
    assert len(text) > 1000


def test_validate_backtest():
    # run validate script
    res = subprocess.run(['./scripts/validate_pine.sh', 'pine/backtest.pine'], capture_output=True, text=True)
    assert res.returncode == 0, f"validate failed: {res.stdout}\n{res.stderr}"
    assert 'Basic validation OK' in res.stdout
