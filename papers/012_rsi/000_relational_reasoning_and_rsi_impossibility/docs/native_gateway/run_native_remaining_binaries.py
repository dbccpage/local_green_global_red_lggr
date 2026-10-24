from pathlib import Path
import hashlib
import json
import os
import subprocess
import time

V = Path(__file__).parent
R = Path(r'C:\Users\a343o\source\repos\the_symbol_game\omega_engine\crates_rs')
names = {
    'omega_solvers': 'omega_solvers-a08614dfbe8a9747.exe',
    'omega_symbol_game': 'omega_symbol_game-1103560ec7394259.exe',
    'omega_symbol_game_runtime': 'omega_symbol_game_runtime-9dc2cb10f4ab2f10.exe',
    'omega_wdp': 'omega_wdp-74e73de435bb439a.exe',
    'omega_woland': 'omega_woland-aeeed4194264c52d.exe',
}
records = []
with (V / 'native_rust_remaining.log').open('w', encoding='utf-8') as log:
    for crate, name in names.items():
        exe = R / 'target/debug/deps' / name
        digest = hashlib.file_digest(exe.open('rb'), 'sha256').hexdigest()
        env = dict(os.environ, CARGO_MANIFEST_DIR=str(R / crate))
        print('START', crate, flush=True)
        log.write(f'Running {exe}\n')
        log.flush()
        start = time.time()
        p = subprocess.run([str(exe)], cwd=R / crate, env=env, stdout=log,
            stderr=subprocess.STDOUT, timeout=900)
        records.append(dict(command=[str(exe)], cwd=str(R / crate), sha256=digest,
            exit_code=p.returncode, seconds=time.time()-start))
        assert digest == hashlib.file_digest(exe.open('rb'), 'sha256').hexdigest()
        print('END', crate, p.returncode, flush=True)
receipt = dict(command='Execute the five remaining already compiled Rust library test binaries',
    producer='cargo test --locked --offline --lib with the 13 selected packages, recorded in native_rust_libs.json',
    invocations=records, exit_code=max(row['exit_code'] for row in records))
(V / 'native_rust_remaining.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
raise SystemExit(receipt['exit_code'])
