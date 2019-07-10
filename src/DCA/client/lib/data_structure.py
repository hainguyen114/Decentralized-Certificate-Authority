import lib.sub as sub
import lib.storj as st

class Request_Cert:
    
    ''' Hàm khởi tạo:
        Các thuộc tính:
        - id_user_in_dca  : id của user trong toàn bộ hệ thống dca
        - id_sp1_in_dca   : ...
        ...
    '''
    def __init__(self,id_user_in_dca,id_sp1_in_dca,sp1_domain,id_user_in_sp1,sub_info = None):
        self.id_user_in_dca = id_user_in_dca
        self.id_sp1_in_dca = id_sp1_in_dca
        self.sp1_domain = sp1_domain
        self.id_user_in_sp1 = id_user_in_sp1
        self.sub_info = sub_info
    ###########################################

    ''' Hàm lấy thuộc tính
        return: list các thuộc tính theo thứ tự : id_user_in_dca,id_sp1_in_dca,sp1_domain,id_user_in_sp1,sub_info
    '''
    def GetAllValue(self):
        return self.id_user_in_dca,self.id_sp1_in_dca,self.sp1_domain,self.id_user_in_sp1,self.sub_info
    ############################################
    '''
    '''
    def UpOnChain(self):
        keys = [self.id_sp1_in_dca]
        data = {}
        data['id_user_in_dca'] = self.id_user_in_dca
        data['id_sp1_in_dca'] = self.id_sp1_in_dca
        data['sp1_domain'] = self.sp1_domain
        data['id_user_in_sp1'] = self.id_user_in_sp1
        data['sub_info'] = self.sub_info
        
        return sub.PublishData(sub.STREAM_REQUEST,keys,data)

class Response_Request:

    ''' Hàm khởi tạo
         accept : true/false
    '''
    def __init__(self,id_request,accept,id_info = None):
        self.id_request = id_request
        self.accept = accept
        self.id_info = id_info
    '''
    '''
    def GetAllValue(self):
        return self.id_request,self.accept,self.id_info

    '''
    '''
    def UpOnChain(self):
        keys = [self.id_request]
        data = {}
        data['id_request'] = self.id_request
        data['is_accepted'] = self.accept
        data['id_info'] = self.id_info
        return sub.PublishData(sub.STREAM_RESPONSE,keys,data)

class Cert_Info:
    def __init__(self,id_sp1_in_dca,sp1_domain,time_start,time_end,link_cert):
        self.id_sp1_in_dca = id_sp1_in_dca
        self.sp1_domain = sp1_domain
        self.time_start = time_start
        self.time_end = time_end
        self.link_cert = link_cert
    def UpOnChain(self):
        keys = []
        data = {} 
        data['id_sp1_in_dca'] = self.id_sp1_in_dca
        data['sp1_domain'] = self.sp1_domain
        data['time_start'] = self.time_start
        data['time_end'] = self.time_end
        data['link_cert'] = self.link_cert
        return sub.PublishData(sub.STREAM_CERT,keys,data)

class Pub_Key:
    def __init__(self,id_sp1_in_dca,sp1_domain,pub_key):
        self.id_sp1_in_dca = id_sp1_in_dca
        self.sp1_domain = sp1_domain
        self.pub_key = pub_key
    def UpOnChain(self):
        keys = [self.id_sp1_in_dca,self.sp1_domain]
        data = {} 
        data['id_sp1_in_dca'] = self.id_sp1_in_dca
        data['sp1_domain'] = self.sp1_domain
        data['hex_pub_key'] = self.pub_key.exportKey('PEM').hex()
        return sub.PublishData(sub.STREAM_PUBKEY,keys,data)

class Vote:
    def __init__(self, link_cert, is_valid):
        self.id_voter_in_dca = sub.GetMyIdDCA()
        self.link_cert = link_cert
        self.is_valid = is_valid 

    def UpOnChain(self):            
        key = [self.link_cert, self.is_valid]
        content = {}
        content['id_voter_in_dca'] = self.id_voter_in_dca
        content['link_cert'] = self.link_cert
        content['is_valid'] = self.is_valid 
        tx = sub.PublishData(sub.STREAM_VOTE, key, content)
        return tx


############################################################################

class User:
    ''' Hàm khởi tạo:
        Các thuộc tính:
        - id_user_in_dca  : id của user trong toàn bộ hệ thống dca
        ...
    '''
    def __init__(self):
        sub.api.subscribe([sub.STREAM_REQUEST,sub.STREAM_RESPONSE,sub.STREAM_CERT,sub.STREAM_VOTE,sub.STREAM_DOMAIN])
        self.id_user_in_dca = sub.GetMyIdDCA()
    
    ''' Hàm gửi request Certificate lên chain cho sp1
    '''
    def UpRequest(self,sp1_domain,id_user_in_sp1,sub_info):
        id_sp1_in_dca = sub.GetIdByDomain(sp1_domain)
        request = Request_Cert(self.id_user_in_dca,id_sp1_in_dca,sp1_domain,id_user_in_sp1,sub_info)
        return request.UpOnChain()
    
    ''' Hàm lấy về response của sp1 accept hay reject request đã gửi trước đó 
         id_request: txid của request trước đó
         return 
              json data: data kiểu json gồm (id_request, is_accepted, id_info)
    '''
    def CheckResponse(self,id_request):
        keys = [id_request]
        l = sub.GetData(sub.STREAM_RESPONSE,keys)
        if len(l) <= 0:
            return -1
        response = l[0]['data']['json']
        return response['is_accepted']
    
    def GetResponseIdInfo(self,id_request):
        keys = [id_request]
        response = sub.GetData(sub.STREAM_RESPONSE,keys)[0]['data']['json']
        return response['id_info']
 
class Ser_Provider_1:
    ''' Hàm khởi tạo:
        Các thuộc tính:
        - id_sp1_in_dca  : id của service provider trong toàn bộ hệ thống dca
        ...
    '''
    def __init__(self,domain):
        sub.api.subscribe([sub.STREAM_REQUEST,sub.STREAM_RESPONSE,sub.STREAM_CERT,sub.STREAM_VOTE,sub.STREAM_PUBKEY,sub.STREAM_DOMAIN])
        self.domain = domain 
        self.id_sp1_in_dca = sub.GetMyIdDCA()
        
    '''
    '''
    def GetMyPubkey(self):
        if not sub.os.path.isfile(sub.PUBKEY_PATH): 
            return False
        fpub = open(sub.PUBKEY_PATH, 'rb') 
        pub_key = sub.RSA.importKey(fpub.read())
        fpub.close()
        return pub_key

    '''
    '''
    def UpDomain(self):
        if sub.GetIdByDomain(self.domain) == False:
            keys = [self.domain,self.id_sp1_in_dca, sub.keyStorj['bucket_name']]
            data = ''
            return sub.PublishData(sub.STREAM_DOMAIN,keys,data)
        return False

    '''
    '''
    # def UpPubKey(self):
    #     if sub.GetIdByDomain(self.domain) == False:
    #         return False
    #     hex_pubkey = self.GetMyPubkey()
    #     if hex_pubkey == False:
    #         raise 'public key does not exist'
    #     pubkey = Pub_Key(self.id_sp1_in_dca,self.domain,hex_pubkey)
    #     return pubkey.UpOnChain()
        
    '''
    '''
    def PutPubKey(self): 
        if sub.GetIdByDomain(self.domain) == False:
            return False
        pubkey = self.GetMyPubkey()
        old_pubkey = sub.GetPubKeyByDomainOrId(self.id_sp1_in_dca)
        if old_pubkey :
            f = open(sub.PRIKEY_PATH, 'rb')
            new_pri_key = sub.RSA.importKey(f.read())
            f.close()
            # f = open(sub.PUBKEY_PATH, 'rb')
            # new_pub_key = sub.RSA.importKey(f.read())
            # f.close()
            sub.CreateOldKeyCert(new_pri_key,old_pubkey,[self.id_sp1_in_dca,self.domain])
        pubkey = Pub_Key(self.id_sp1_in_dca,self.domain,pubkey)
        return pubkey.UpOnChain()
    
    ''' Hàm lấy list các request
    '''
    def GetListRequest(self):
        keys = [self.id_sp1_in_dca]
        list_request = sub.GetData(sub.STREAM_REQUEST,keys)
        return_list = []
        for i in list_request:

            content = {}
            content['id_request'] = i['txid']
            data = i['data']['json']
            request_cert = Request_Cert(data['id_user_in_dca'], data['id_sp1_in_dca'], data['sp1_domain'], data['id_user_in_sp1'], data['sub_info'])
            content['request_cert'] = request_cert

            if len(sub.GetData(sub.STREAM_RESPONSE,[content['id_request']])) == 0:
                return_list.append(content)
        return return_list
    
    ''' Hàm kiểm tra request có hợp lệ
    '''
    def CheckRequest(self,request_cert):
        return True

    '''
    '''
    def ExportCert(self,request_cert):
        info = {}
        info['id_sp1_in_dca'] = request_cert.id_sp1_in_dca
        info['sp1_domain'] = request_cert.sp1_domain
        info['id_user_in_sp1'] = request_cert.id_user_in_sp1 #########
        info['user_name'] = 'trang' ###############
        hash_all_info = sub.hashlib.sha1(sub.json.dumps(info).encode('utf-8')).hexdigest()
        info['hash_all_info'] = hash_all_info
        link_cert = sub.ExportCert(info)
        return link_cert

    '''
    '''
    def AcceptOrReject(self,id_request,request_cert):
        rp_id_request = id_request
        rp_accept = False
        rp_id_info = None
        if self.CheckRequest(request_cert)== True:
            link_cert = self.ExportCert(request_cert)
            print(link_cert)
            rp_accept = True
            time_now = st.datetime.now(st.timezone('UTC'))
            time_start = time_now.strftime(sub.FORMAT_TIME)
            time_end = (time_now + sub.DELTA_TIME).strftime(sub.FORMAT_TIME)
            
            print('\nUploading...')
            if sub.acc_Storj.upload(sub.os.getcwd(),link_cert+'.pdf', sub.keyStorj['bucket_name'],sub.st.utc2local(time_end)):
                sub.os.remove(link_cert+'.pdf')
                print('Certificate ' + link_cert + ' is stored on Storj network.')
            else:
                return False
            cert_info  = Cert_Info(self.id_sp1_in_dca,self.domain,time_start,time_end,link_cert)
            rp_id_info = cert_info.UpOnChain()

        response = Response_Request(rp_id_request,rp_accept,rp_id_info)
        return response.UpOnChain()
        

class Ser_Provider_2:

    def __init__(self):
        self.id_sp2_in_dca = sub.GetMyIdDCA()

    def CountNumVotes(self, link_cert, is_valid):
        keys = [link_cert, bool(is_valid).__str__()]
        list_cert = sub.GetData(sub.STREAM_VOTE, keys)

        return len(list_cert)

    def GetCert(self, id_info):
        cert_info = sub.GetDataByTxid(sub.STREAM_CERT, id_info)['data']['json']

        if(len(cert_info) < 1):
            return None

        valid_votes = self.CountNumVotes(cert_info['link_cert'], True)
        invalid_votes = self.CountNumVotes(cert_info['link_cert'], False)

        result = {}
        result['id_sp1_in_dca'] = cert_info['id_sp1_in_dca']
        result['link_cert'] = cert_info['link_cert']
        result['sp1_domain'] = cert_info['sp1_domain']
        result['time_start'] = st.utc2local(cert_info['time_start'])
        result['time_end'] = st.utc2local(cert_info['time_end'])
        result['valid_votes'] = valid_votes
        result['invalid_votes'] = invalid_votes

        return result

class Voter:

    def __init__(self):
        self.id_user_in_dca = sub.GetMyIdDCA()

    def VerifyCert(self,link_cert,sp1_domain,sp1_pubkey,dir_path): 
        file_name = link_cert+'.pdf'

        bucket_name = sub.GetBucketNameByDomain(sp1_domain)
        sub.acc_Storj.download('sj://'+bucket_name+'/'+file_name,dir_path) 
        
        return sub.cp.verifyPDF(dir_path + file_name,sp1_pubkey)

    def VoteOnCert(self, link_cert, is_valid, num_votes):
        #ID_voter_DCA = sub.GetMyIdDCA()
        vote = Vote(link_cert, bool(is_valid).__str__())
        
        for i in range(0, int(num_votes)):
            vote.UpOnChain()

        #return vote.UpOnChain()
    
    def GetListCertInfo(self):
        cert_arr = sub.GetData(sub.STREAM_CERT, '')

        list_cert_info = [] # 

        for cert in cert_arr:
            info = cert['data']['json']
            time_end = info['time_end']
            time_now = st.datetime.now(st.timezone('UTC')).strftime(sub.FORMAT_TIME)
            if(time_now > time_end):
                continue

            cert_info = Cert_Info(info['id_sp1_in_dca'], info['sp1_domain'], st.utc2local(info['time_start']),
                             st.utc2local(info['time_end']), info['link_cert'])
                             
            list_cert_info.append(cert_info)

        return list_cert_info
#######################

#abc = acc_Storj.upload('/home/thanhtrang/Desktop', 'a2.py', '16253830804574847541','')

# 0fb50e206516d2d660946fbdeca29a3f5c268f3de657b83d4202477f6ea07897
# user = User() # tao user 
# sp1_domain = 'hcmus' 
# id_user_in_sp1 = '1512587'
# sub_info = 'getCert'

# sp1 = Ser_Provider_1(sp1_domain) # tao sp1
# sp1.UpDomain() # dang ki domain name
# sub.GenRsaKey()
# sp1.PutPubKey() # dang public key 
# #sub.GetData(sub.STREAM_PUBKEY,[sp1.domain])
# #sub.GetPubKeyByDomainOrId(sp1_domain)
# sub.GetIdByDomain(sp1_domain) # kiem tra sp1 co ton tai sp1 

# txid = user.UpRequest(sp1_domain,id_user_in_sp1,sub_info) # user dang request 


# l = sp1.GetListRequest() # sp1 lay list cac request

# #sp1.CheckRequest(l[0]['request_cert']) # kiem tra request co hop le

# sp1.AcceptOrReject(l[0]['id_request'],l[0]['request_cert']) # dang thong tin response dong y hoac ko dong y len chain cua request do

# user.CheckResponse(txid) # user kiem tra request co duoc sp1 dong y hay ko

# id_cert_info = user.GetResponseIdInfo(txid) # user lay id info cua cert_info tren chain = txid cua cert_info do 

# sp2 = Ser_Provider_2() # tao sp2

# link_cert = sub.GetDataByTxid(sub.STREAM_CERT,id_cert_info)['data']['json']['link_cert'] # sp2 lay link_cert tren storj tu txid (id_cert_info)

# sp2.CountNumVotes(link_cert,True) # sp2 lay so luong vote 
# sp2.CountNumVotes(link_cert,False)

# voter = Voter() # tao voter

# list_cert_info = voter.GetListCertInfo() # voter lay list cac cert_info duoc up len chain

# link_cert_voter = list_cert_info[0].link_cert # 0 la link moi nhat

# voter.VerifyCert(link_cert_voter,sp1_domain,sub.GetPubKeyByDomainOrId(sp1_domain),'/home/thanhtrang/Documents/DCA/') # voter check cert tren storj co hop le voi pubkey tren chain

# voter.VoteOnCert(link_cert_voter,True,3) # voter vote cho tung cert
# voter.VoteOnCert(link_cert_voter,False,3)

# sub.GenRsaKey() # sp1 tao cap key moi
# sp1.PutPubKey() # dang cap key moi len chain

# voter.VerifyCert(link_cert_voter,sp1_domain,sub.GetPubKeyByDomainOrId(sp1_domain),'/home/thanhtrang/Documents/DCA/') # voter check cert tren storj co hop le voi pubkey tren chain

# list_old_pub_key = sub.GetListOldPubkey(sub.GetPubKeyByDomainOrId(sp1_domain),[sp1_domain]) # cac danh sach cac key cu cua sp1
# voter.VerifyCert(link_cert_voter,sp1_domain,list_old_pub_key[0],'/home/thanhtrang/Documents/DCA/') # voter check cert tren storj co hop le voi pubkey tren chain
# voter.VerifyCert(link_cert_voter,sp1_domain,list_old_pub_key[1],'/home/thanhtrang/Documents/DCA/') # voter check cert tren storj co hop le voi pubkey tren chain
# voter.VerifyCert(link_cert_voter,sp1_domain,list_old_pub_key[2],'/home/thanhtrang/Documents/DCA/') # voter check cert tren storj co hop le voi pubkey tren chain


#sub.api.liststreamitems(sub.STREAM_REQUEST,False,sub.NUM_ITEMS_PER_GET_FROM_STREAM)
#sub.GetData(sub.STREAM_PUBKEY,[])
#data_pubkey = {}
#data_pubkey['pubkey'] = 'pubkey'
#txid = sub.PublishData(sub.STREAM_PUBKEY,[sp1.id_sp1_in_dca,sp1.domain],data_pubkey)
#sub.PublishData(sub.STREAM_REQUEST,['a'],'no')

    
    
        


    
