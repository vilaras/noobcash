# Cryptographic imports
import Crypto.Random
from Crypto.PublicKey import RSA

'''
Params:
	public_key: my address known to every node
		Type <string>. Example "id0"
	private_key: my crypto key only known to me
		Type <string???>
	transactions: valid UTXOs
		Type <dict>
'''
class Wallet:
	def __init__(self):
		self.public_key, self.private_key = self.keys()
		# self.UTXOs = {}

	'''
	Returns private, public key pair in PEM form
	'''
	def keys(self):
		random_gen = Crypto.Random.new().read
		keypair = RSA.generate(2048, random_gen)

		privkey = keypair.exportKey('PEM').decode()
		pubkey = keypair.publickey().exportKey('PEM').decode()

		return pubkey, privkey
