from pathlib import Path
file = Path('./../proto/baddle_twirp.py')
file.write_text(file.read_text().replace('/.Baddle', '/Baddle'))
