# multichain-util create chaindemo
# multichaind chaindemo -daemon
# multichain-cli chaindemo create stream REQUEST true
# multichain-cli chaindemo create stream RESPONSE true
# multichain-cli chaindemo create stream CERT true
# multichain-cli chaindemo create stream PUBKEY true
# multichain-cli chaindemo create stream VOTE true
# multichain-cli chaindemo create stream DOMAIN true
# multichain-cli chaindemo create stream STORJKEY true
# multichain-cli chaindemo create stream KEY_CERT true

import os
import sys
import subprocess
import json
import binascii 
import socket 
import string 
import Crypto
import ast
import copy
import time 
import shutil
import pyAesCrypt
import codecs
import hashlib 
import numpy as np
from Savoir import Savoir
from pathlib import Path
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto import Random
from datetime import timedelta
import lib.create_pdf as cp
import lib.storj as st
import lib.sign_ver as sv


STREAM_REQUEST = 'REQUEST'
STREAM_RESPONSE = 'RESPONSE'
STREAM_CERT = 'CERT'
STREAM_PUBKEY = 'PUBKEY'
STREAM_VOTE = 'VOTE'
STREAM_DOMAIN = 'DOMAIN'
STREAM_STORJKEY = 'STORJKEY'
STREAM_KEY_CERT = 'KEY_CERT'

NUM_ITEMS_PER_GET_FROM_STREAM = 100
RSAKEYLENGTH = 1024
FORMAT_TIME = "%Y-%m-%dT%H:%M:%SZ"
DELTA_TIME = timedelta(seconds=10000)
KEY_STORJ_INFO = 'STORJ_INFO'
KEY_OLD_KEY = 'OLD_KEY'

path = Path(__file__).resolve().parent.parent.__str__()
PUBKEY_PATH = path + '/rsakey/public_key.pem' #'/rsakey/public_key.pem'
PRIKEY_PATH = path + '/rsakey/private_key.pem'

chain_name = 'chaindemo' # ten chain
rpchost = 'localhost'   # tên localhost của chain

print("Input server ip address: ")
ip_address = input()
print("Input server port: ")
port_connect = input()

str_rpc_default_host = 'default-rpc-port'
satellite_addr = ip_address+':10000'

''' lấy API để thực hiện trên multichain 
'''
#####################################
def GetAPI(): 
    if (os.path.isfile(os.path.expanduser('~/.multichain/'+chain_name+'/params.dat'))) == False:
        with subprocess.Popen(['multichaind',chain_name+'@'+ip_address+':'+port_connect]) as p:
            try:
                p.wait(timeout=10) 
            except:
                p.kill()
                p.wait() 
    rpc_info = {}
    with open(os.path.expanduser('~/.multichain/'+chain_name+'/multichain.conf')) as f:
        for line in f:
            line = line.rstrip('\n')
            (key,val) = line.split('=')
            rpc_info[key] = val  

    with open(os.path.expanduser('~/.multichain/'+chain_name+'/params.dat')) as f:
        for line in f:
            line = line.rstrip('\n')
            if(str_rpc_default_host in line):
                tline = line.split(' ')
                rpc_info[tline[0]] = tline[2]
    #print(rpc_info)
    rpcuser = rpc_info['rpcuser']
    rpcpasswd = rpc_info['rpcpassword']
    rpcport = rpc_info['default-rpc-port']
    api = Savoir(rpcuser, rpcpasswd, rpchost, rpcport, chain_name)
    try :
        api.help()
    except:#kiem tra node da chay chua
        subprocess.call(['multichaind',chain_name,'-daemon'])
    return api

api = GetAPI()
api.subscribe(STREAM_REQUEST)
api.subscribe(STREAM_RESPONSE)
api.subscribe(STREAM_CERT)
api.subscribe(STREAM_PUBKEY)
api.subscribe(STREAM_VOTE)
api.subscribe(STREAM_DOMAIN)
api.subscribe(STREAM_STORJKEY)
api.subscribe(STREAM_KEY_CERT)

###
#...
###
########################################

''' Lấy id trên hệ thống multichain DCA
'''
def GetMyIdDCA():    
    return api.getaddresses()[0]
########################################

''' Hàm lấy id của 1 service provider bằng tên domain (tên domain phải khác nhau giữa các SP
    ...
'''
def GetIdByDomain(sp_domain):
    list_domain = GetData(STREAM_DOMAIN,[sp_domain])
    if len(list_domain) == 0:
        return False
    return list_domain[0]['keys'][1]
########################################
''' Hàm lấy bucket name của 1 service provider bằng tên domain (tên domain phải khác nhau giữa các SP
    ...
'''
def GetBucketNameByDomain(sp_domain):
    list_domain = GetData(STREAM_DOMAIN,[sp_domain])
    if len(list_domain) == 0:
        return False
    return list_domain[0]['keys'][2]
###########################################
'''
'''
def GetPubKeyByDomainOrId(sp_domain_or_id_in_dca):
    list_pubkey = GetData(STREAM_PUBKEY,[sp_domain_or_id_in_dca])
    if len(list_pubkey) == 0:
        return False
    return RSA.importKey(bytes.fromhex(list_pubkey[0]['data']['json']['hex_pub_key']).decode())

###########################################

''' Hàm đăng dữ liệu lên multichain 
     string      stream : tên stream (kênh) muốn đăng 
     list_array  key    : tag của dữ liệu
     json        data   : data muốn đăng
    return txid (transaction id) 
'''
def PublishData(stream,keys,data):
    if len(keys) == 0:
        keys = ['None']
    return api.publish(stream,keys,{'json':data})
#############################################
''' Hàm lấy dữ liệu trên multichain 
     string      stream : tên stream (kênh) muốn đăng 
     list_array  key    : tag của dữ liệu
    return list_array các data 
'''
def GetData(stream,keys):
    if len(keys) == 0:
        list_data = api.liststreamitems(stream,False,NUM_ITEMS_PER_GET_FROM_STREAM)
        list_data.reverse()
        return list_data
    list_data = api.liststreamkeyitems(stream,keys[0],False,NUM_ITEMS_PER_GET_FROM_STREAM)
    list_data.reverse()
    if len(keys) > 1 :
        return_list = []
        for i in list_data:
            if set(keys[1:]).issubset(i['keys']):
                return_list.append(i)
        return return_list
    else: 
        return list_data
def GetDataByTxid(stream,txid):
    return api.getstreamitem(stream,txid,False)
################################################
'''asdad
'''
def GenRsaKey():
    random_generator = Random.new().read
    RSAKEY = RSA.generate(RSAKEYLENGTH, random_generator) #generate pub and priv key
    f = open(PUBKEY_PATH, 'wb')
    f.write(RSAKEY.publickey().exportKey('PEM'))
    f.close()
    f = open(PRIKEY_PATH, 'wb')
    f.write(RSAKEY.exportKey('PEM'))
    f.close()  
################################################
'''
   info: bien json luu cac thong tin id_sp1_in_dca, sp1_domain, id_user_in_sp1,user_name,hash_all_info. 
'''
def ExportCert(info):
    content = 'this is a cert'
    org_file = 'cert.pdf'
    cp.createWithText(content,org_file)
    with open(org_file,'ab') as f:
        f.write(b'%%___CERT_INFO___%%')
        f.write(json.dumps(info).encode('utf-8'))
        f.write(b'%%___END_CERT_INFO___%%')
    f = open(PRIKEY_PATH, 'rb')
    prikey = RSA.importKey(f.read())
    f.close()
    if prikey:
        sign_file = hashlib.sha1(open(org_file,'rb').read()).hexdigest()
        if cp.exportPDFwithSig(org_file,prikey,sign_file+'.pdf'):
            os.remove(org_file)
            # up qua storj
            #check = acc_Storj.upload(fs.CRPATH, newfile,bucket_name)
            # if check:
            #     os.remove(org_file)
            
            #print(check) 
            return sign_file
    return False
    # raise 'ERR: private key not found'
#################################################
'''
'''
def LoadInfoFromPDFCert(file_in):
    if os.path.isfile(file_in):
        data = open(file_in, 'rb').read()
        b_si = b'%%___CERT_INFO___%%' 
        e_si = b'%%___END_CERT_INFO___%%'
        b_pos = data.find(b_si)+len(b_si)
        e_pos = data.find(e_si)
        if e_pos > 0:    
            info = data[b_pos:e_pos]
            return json.loads(info)
    return False
##################################################
def CheckPermission():
    list_pe = api.listpermissions()
   
    for p in list_pe:
        if GetMyIdDCA() == p['address']:
            return True
    return False
################################################
#####################################
def SendAddressForGrantingPermission(ip_address,port_connect):
    BUFFER_SIZE = 1024 
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip_address, int(port_connect)-1))
    s.send(bytes(GetMyIdDCA(), "utf-8"))
    data = 0
    data = data + int.from_bytes(s.recv(BUFFER_SIZE),"big")
    s.close()
    #print(data)
    #print(int.from_bytes(data,"big"))
    return data
######################################
def GetStorjKeyAndBucket():
    tx = GetData(STREAM_STORJKEY,[GetMyIdDCA()])
    if len(tx) > 0:
        return tx[0]['data']['json']
    return False
    tx = api.liststreamkeyitems(STREAM_STORJKEY,KEY_STORJ_INFO,False,NUM_ITEMS_PER_GET_FROM_STREAM)
    tx.reverse()
    for t in tx:
        if set([GetMyIdDCA()]).issubset(t['keys']):
            return t['data']['json']
#########################################
'''
 keys list
 key string
'''
def CreateOldKeyCert(new_prikey,old_pubkey,keys):
    keys.append(KEY_OLD_KEY)
    signature = sv.b64encode(sv.sign(old_pubkey.exportKey('PEM'), new_prikey, "SHA-512")) 

    data = {}
    data['old_pubkey'] = old_pubkey.exportKey('PEM').hex()
    data['signature'] = signature.hex() 
    return PublishData(STREAM_KEY_CERT,keys,json.dumps(data))

def GetListOldPubkey(new_pubkey,keys): 
    keys.append(KEY_OLD_KEY) 
     
    list_data = GetData(STREAM_KEY_CERT,keys)
    if len(list_data) == 0:
        return False
    list_key = [] 

    for i in list_data:
        jsondata = json.loads(i['data']['json']) 
        old_pubkey = bytes.fromhex(jsondata['old_pubkey'])
        sign = bytes.fromhex(jsondata['signature'])
        if sv.verify(old_pubkey,sign,new_pubkey):
            rsa_key = RSA.importKey(old_pubkey)
            list_key.append(rsa_key)
            new_pubkey = RSA.importKey(old_pubkey)
    return list_key

##########################################################
time.sleep(3)
if CheckPermission() == False:
    SendAddressForGrantingPermission(ip_address,port_connect)
if CheckPermission() == False:
    raise 'Permission error'

time.sleep(2)
keyStorj = GetStorjKeyAndBucket()

acc_Storj = st.StorjClient(satellite_addr, keyStorj['api_key'],keyStorj['access_key'], keyStorj['secret_key'])
acc_Storj.setup()



