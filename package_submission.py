"""Gera ZIP por lista permitida, sem .env e sem sobrescrever entregas."""
import argparse
import zipfile
from pathlib import Path


def package(destination):
    root=Path(__file__).resolve().parent
    destination=Path(destination)
    paths=[root/name for name in ('README.md','requirements.txt','.env.example','.gitignore','package_submission.py')]
    for directory in ('app','tests','evidence'):
        paths.extend(p for p in (root/directory).rglob('*') if p.is_file()
                     and '__pycache__' not in p.parts and p.suffix!='.pyc'
                     and not p.name.startswith('.env'))
    with zipfile.ZipFile(destination,'x',zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(set(paths)):
            archive.write(path,path.relative_to(root))
    with zipfile.ZipFile(destination) as archive:
        assert archive.testzip() is None
        assert all(Path(name).name!='.env' for name in archive.namelist())
    print('ZIP criado. Revise integrantes, evidencias e ausencia de segredos antes de entregar.')


if __name__=='__main__':
    cli=argparse.ArgumentParser()
    cli.add_argument('--output',default='CKP01_fleet_charge_intelligence_grupo.zip')
    package(cli.parse_args().output)
