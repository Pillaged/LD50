from pathlib import Path
file = Path('./../proto/rpc_twirp.py')
file.write_text(file.read_text().replace('/.DeathOrTaxes', '/DeathOrTaxes'))
