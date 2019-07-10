# multichain-util create chaindemo
# multichaind chaindemo -daemon
# multichain-cli chaindemo create stream DATA true
# multichain-cli chaindemo create stream PUBKEY true
# multichain-cli chaindemo create stream REQUEST true

import os
import sys
import subprocess
import json
import shutil
import yaml
from datetime import datetime
import pytz
from pytz import timezone
import tzlocal

############################################################################
#                        Storj
#--------------------------------------------------
#                    Documentation
#    https://storj.io/blog/2019/01/getting-started-with-the-storj-v3-test-network-storj-sdk/
    
#                    Prerequisites

#    Before configuring the storj-sim V3 testnet, you must have the following:
#     The latest release of Git (https://git-scm.com/downloads)
#     Go, at least version 1.11 (https://golang.org/doc/install)
#     The AWS CLI tool (https://docs.aws.amazon.com/cli/latest/userguide/installing.html)
#----------------------------------------------------

storjsim_path = '~/go/bin/storj-sim'
uplink_path = '~/go/bin/uplink'
identity_path = '~/go/bin/identity'

#Run process
def run(command):
    # run process 
    temp = subprocess.run(command, stdout=subprocess.PIPE)
    # while(True):
    #     if (threading.currentThread().isAlive() == False):
    #         break
    return temp

#Convert from local time to UTC time
def local2utc(dt):
    local_timezone = tzlocal.get_localzone()    
    naive = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
    local_dt = local_timezone.localize(naive, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    
    return utc_dt.strftime ("%Y-%m-%dT%H:%M:%SZ")

def utc2local(dt):
    local_timezone = tzlocal.get_localzone() 
    naive = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%SZ")
    utc_dt = pytz.utc.localize(naive, is_dst=None)
    local_dt = utc_dt.astimezone(local_timezone)

    return local_dt.strftime("%Y-%m-%d %H:%M:%S")

#----------------------------------------------
#                  Storj Server (AWS S3)

class StorjServer:
    def __init__(self):
        self._gateway_addr = self.get_gateway_addr()
        self._gateway_access_key = self.get_access_key()
        self._gateway_secret_key = self.get_secret_key()
        self._gateway_api_key = self.get_api_key()

    # Get gateway address
    def get_gateway_addr(self):
        command = [os.path.expanduser(storjsim_path), 'network', 'env', 'GATEWAY_0_ADDR'] 
        gateway_addr = run(command)
        temp = gateway_addr.stdout.decode('utf-8')

        GATEWAY_ADDR = temp.strip()
        return GATEWAY_ADDR

    #Get gateway access key
    def get_access_key(self):
        command = [os.path.expanduser(storjsim_path), 'network', 'env', 'GATEWAY_0_ACCESS_KEY'] 
        gateway_access_key = run(command)
        temp = gateway_access_key.stdout.decode('utf-8')

        GATEWAY_ACCESS_KEY = temp.strip()
        return GATEWAY_ACCESS_KEY

    #Get gateway secret key
    def get_secret_key(self):
        command = [os.path.expanduser(storjsim_path), 'network', 'env', 'GATEWAY_0_SECRET_KEY']
        gateway_secret_key = run(command)
        temp = gateway_secret_key.stdout.decode('utf-8')

        GATEWAY_SECRET_KEY = temp.strip()
        return GATEWAY_SECRET_KEY

    #Get gateway api key
    def get_api_key(self):
        command = [os.path.expanduser(storjsim_path), 'network', 'env', 'GATEWAY_0_API_KEY']
        gateway_api_key = run(command)
        temp = gateway_api_key.stdout.decode('utf-8')

        GATEWAY_API_KEY = temp.strip()
        return GATEWAY_API_KEY

    def configure(self):
        # configure gateway access key
        command = ['aws', 'configure', 'set', 'aws_access_key_id', self._gateway_access_key] 
        run(command)

        # configure gateway secret key
        command = ['aws', 'configure', 'set', 'aws_secret_access_key', self._gateway_secret_key] 
        run(command)

    def list_buckets(self):
        # list current buckets
        command = ['aws', 's3', '--endpoint=http://' + self._gateway_addr, 'ls']
        buckets = run(command)

        str = buckets.stdout.decode('utf-8')
        BUCKETS = []
        while(str != ''):
            info = {
                'date': '',
                'time': '',
                'name': ''
            }
            # get date
            index = str.find(' ')
            temp = slice(index)
            info['date'] = str[temp]
            str = str[index + 1:]

            # get time
            index = str.find(' ')
            temp = slice(index)
            info['time'] = str[temp]
            str = str[index + 1:]
            # get name
            index = str.find('\n')
            temp = slice(index)
            info['name'] = str[temp]
            str = str[index + 1:]

            BUCKETS.append(info)

        return BUCKETS

    def list_bucket_files(self, bucket_name):
        # list current files in bucket
        command = ['aws', 's3', '--endpoint=http://' + self._gateway_addr, 'ls', 's3://' + bucket_name]
        files = run(command)

        str = files.stdout.decode('utf-8')
        FILES = []
        while(str != ''):
            info = {
                'date': '',
                'time': '',
                'size': '',
                'name': ''
            }
            # get date
            index = str.find(' ')
            temp = slice(index)
            info['date'] = str[temp]
            str = str[index + 1:]

            # get time
            index = str.find(' ')
            temp = slice(index)
            info['time'] = str[temp]
            str = str[index + 1:]

            # get size
            str = str.strip() + '\n'
            index = str.find(' ')
            temp = slice(index)
            info['size'] = str[temp]
            str = str[index + 1:]

            # get name
            index = str.find('\n')
            temp = slice(index)
            info['name'] = str[temp]
            str = str[index + 1:]

            FILES.append(info)

        return FILES

    def generate_bucket_name(self, user_id):
        return str(hash(user_id) % ((sys.maxsize + 1) * 2))

    def make_bucket(self, bucket_name):
        # make a bucket
        # command = ['aws', 's3', '--endpoint=http://' + self._gateway_addr, 'mb', 's3://' + bucket_name] 
        # run(command)
        command = [os.path.expanduser(uplink_path), 'mb', 'sj://' + bucket_name]

        output = run(command).stdout.decode('utf-8')
        print(output)

        if(output.lower().find('error') == -1):
            return 0

        return 1

    def upload(self, path, file_name, bucket_name):
        # upload the file from the path to the bucket
        command = ['aws', 's3', '--endpoint=http://' + self._gateway_addr, 'cp', path + '/' + file_name,'s3://' + bucket_name] 
        run(command)

    def download(self, bucket_name, path, file_name):
        # download the file from the bucket to the path
        command = ['aws', 's3', '--endpoint=http://' + self._gateway_addr, 'cp','s3://' + bucket_name + '/' + file_name, path] 
        run(command)

    def remove_bucket(self, bucket_name):
        # remove a bucket
        command = ['aws', 's3', '--endpoint=http://' + self._gateway_addr, 'rb', 's3://' + bucket_name] 
        run(command)

    def remove_file(self, bucket_name, file_name):
        # remove a file
        command = ['aws', 's3', '--endpoint=http://' + self._gateway_addr, 'rm', 's3://' + bucket_name + '/' + file_name] 
        run(command)

    def presign(self, bucket_name, file_name):
        # export a link
        command = ['aws', 's3', '--endpoint=http://' + self._gateway_addr, 'presign', 's3://' + bucket_name + '/' + file_name] 
        presign = run(command)
        temp = presign.stdout.decode('utf-8')

        LINK = temp.strip()
        return LINK

#-----------------------------------------------------
#                   Storj Client (Uplink)

class StorjClient:
    def __init__(self, satellite_addr, gateway_api_key, gateway_access_key, gateway_secret_key):
        self._satellite_addr = satellite_addr
        self._gateway_api_key = gateway_api_key
        self._gateway_access_key = gateway_access_key
        self._gateway_secret_key = gateway_secret_key

    def setup(self):
        command = [os.path.expanduser(uplink_path), 'setup', '--non-interactive', 
                   '--satellite-addr', self._satellite_addr,
                   '--api-key', self._gateway_api_key,
                   '--enc.key', self._gateway_secret_key]
        check = 1
        uplink_config_path = '~/.local/share/storj/uplink'
        if(os.path.isfile(os.path.expanduser(uplink_config_path + '/config.yaml'))) == True:
            temp = yaml.load(open(os.path.expanduser(uplink_config_path + '/config.yaml')))
            check = 0
            if (temp['satellite-addr'] != self._satellite_addr or
                temp['enc.key'] != self._gateway_secret_key or
                temp['api-key'] != self._gateway_api_key):

                check = 1
                shutil.rmtree(os.path.expanduser(uplink_config_path))

        if check:
            print(run(command).stdout.decode('utf-8'))

        # check cert
        uplink_identity_path = '~/.local/share/storj/identity/uplink'
        if(os.path.exists(os.path.expanduser(uplink_identity_path + '/identity.cert')) == False or
           os.path.exists(os.path.expanduser(uplink_identity_path + '/identity.key')) == False):
            
            if (os.path.exists(os.path.expanduser(uplink_identity_path))) == True:
                shutil.rmtree(os.path.expanduser(uplink_identity_path))

            command = [os.path.expanduser(identity_path), 'create', 'uplink', '--difficulty', '1']
            print(run(command).stdout.decode('utf-8'))

        # make sure the identity path is correct
        temp = yaml.load(open(os.path.expanduser(uplink_config_path + '/config.yaml')))

        if ((os.path.expanduser(temp['identity.cert-path']) != os.path.expanduser(uplink_identity_path + '/identity.cert')) or
            (os.path.expanduser(temp['identity.key-path']) != os.path.expanduser(uplink_identity_path + '/identity.key'))):
            temp['identity.cert-path'] = os.path.expanduser(uplink_identity_path + '/identity.cert')
            temp['identity.key-path'] = os.path.expanduser(uplink_identity_path + '/identity.key')

            s = open(os.path.expanduser(uplink_config_path) + '/config.yaml').read()
            s = s.replace('/identity.cert', os.path.expanduser(uplink_identity_path + '/identity.cert'))
            s = s.replace('/identity.key', os.path.expanduser(uplink_identity_path + '/identity.key'))
            f = open(os.path.expanduser(uplink_config_path) + '/config.yaml', 'w')
            f.write(s)
            f.close()

    def upload(self, dir_path, file_name, bucket_name, expires_time):
        command = [os.path.expanduser(uplink_path), 'cp', dir_path + '/' + file_name, 'sj://' + bucket_name]

        if(expires_time != ""):
            expires_dt = local2utc(expires_time)
            exp_dt = '--expires=' + expires_dt
            command.insert(2, exp_dt)
        # if(os.path.exists(os.path.expanduser(dir_path + '/' + file_name))) == False:
        #     print(dir_path + '/' + file_name + ": No such file or directory.")
        #     return 0

        output = run(command).stdout.decode('utf-8')
        print(output)

        if(output.lower().find('error') != -1):
            return 0

        return 'sj://' + bucket_name + '/' + file_name

    def download(self, file_addr, dir_path):
        command = [os.path.expanduser(uplink_path), 'cp', file_addr, dir_path]

        # if(os.path.isdir(os.path.expanduser(dir_path))) == False:
        #     print(dir_path + ": No such file or directory.")
        #     return 0

        output = run(command).stdout.decode('utf-8')

        if(output.lower().find('error') != -1):
            return 0

        return 1

if __name__ == "__main__":

    # server = StorjServer()
    satellite_addr = "localhost:10000"

    # client = StorjClient(satellite_addr, server._gateway_api_key, server._gateway_access_key, server._gateway_secret_key)
    # client.setup()
    # abc = client.upload('/home/hainguyen/Desktop', 'Do_an2.pdf', 'cde', '2019-05-22 23:25:00')
    #client.download('sj://demobucket/Do_an2.pdf', '/home/hainguyen/Desktop')
    format_time = "%Y-%m-%dT%H:%M:%SZ"
    abc = datetime.now(timezone('UTC')).strftime(format_time)
    cde = utc2local(abc)
    print(cde)
    
    