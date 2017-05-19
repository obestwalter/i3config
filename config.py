from pathlib import Path


if __name__ == '__main__':
    projectPath = Path(__file__).parent
    tplPath = projectPath / 'mine'
    acc = []
    for f in [d for d in tplPath.iterdir()]:
        if f.suffix != '.i3conf':
            continue
        acc.append("# %s\n\n%s" % (f, f.read_text()))
    configPath = projectPath / 'config'
    configPath.write_text("\n\n".join(acc))
