from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA512, SHA384, SHA256, SHA, MD5
from Crypto import Random
from base64 import b64encode, b64decode

hash = "SHA-512"

def newkeys(keysize):
    random_generator = Random.new().read
    key = RSA.generate(keysize, random_generator)
    private, public = key, key.publickey()
    return public, private

# def importKey(externKey):
#     return RSA.importKey(externKey)

# def getpublickey(priv_key):
#     return priv_key.publickey()

# def encrypt(message, pub_key): 
#     return pub_key.encrypt(message,32)

# def decrypt(message, priv_key): 
#     return priv_key.decrypt(message)

def sign(message, priv_key, hashAlg="SHA-512"):
    global hash
    hash = hashAlg
    signer = PKCS1_v1_5.new(priv_key)
    if (hash == "SHA-512"):
        digest = SHA512.new()
    elif (hash == "SHA-384"):
        digest = SHA384.new()
    elif (hash == "SHA-256"):
        digest = SHA256.new()
    elif (hash == "SHA-1"):
        digest = SHA.new()
    else:
        digest = MD5.new()
    digest.update(message)
    return signer.sign(digest)

def verify(message, signature, pub_key):
    signer = PKCS1_v1_5.new(pub_key)
    if (hash == "SHA-512"):
        digest = SHA512.new()
    elif (hash == "SHA-384"):
        digest = SHA384.new()
    elif (hash == "SHA-256"):
        digest = SHA256.new()
    elif (hash == "SHA-1"):
        digest = SHA.new()
    else:
        digest = MD5.new()
    digest.update(message)
    #return signer.verify(digest, signature)
    if signer.verify(digest,b64decode(signature)):
        return True
    return False
# datau = open('file2.pdf', 'rb').read()
# keysize = 2048
# (public, private) = newkeys(keysize)
# encrypted = encrypt(datau, public)
# decrypted = decrypt(encrypted, private)
# decrypted == datau

# signature = b64encode(sign(datau, private, "SHA-512"))
# with open("file2_signed.pdf", "wb") as myfile:
#     myfile.write(datau)
#     myfile.write(signature)
# da = open('file2_signed.pdf', 'rb').read()
# da.find(e)
# signature2 = da[da.find(e)+len(e):] 
# datau2 = da[:da.find(e)+len(e)] 
# e = b'%%EOF\n' 

# verified = verify(datau2, b64decode(signature2), public)

