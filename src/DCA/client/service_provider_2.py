import lib.data_structure as ds
import lib.sub as sub

if __name__ == "__main__":

    print("##########################################################")
    print("--                                                      --")
    print("--       Welcome to DEMO Decentralized CA System        --")
    print("--                                                      --")
    print("##########################################################")
    print("\n")
    print("    You are logging in to a service provider account!     ")  
    
    sp2 = ds.Ser_Provider_2() # tao sp2

    is_continue = ''
    while is_continue.lower() != 'n':
        print("\n")
        print("Do you want to continue to check a certificate (Y/N): ")
        is_continue = input()
        print("\n")

        if is_continue.lower() != 'y' and is_continue.lower() != 'n':
            print('Wrong input!')
            continue

        if is_continue.lower() == 'y':
            print("Input a Certificate Information ID: ")
            id_cert_info = input()

            # sp2 lay info cua Cert tren storj tu txid (id_cert_info)
            cert_info = sp2.GetCert(id_cert_info)

            print("\nCertificate Information:\n")
            print('\t Organization ID: ' + cert_info['id_sp1_in_dca'])
            print('\t Certificate ID:  ' + cert_info['link_cert'])
            print('\t Domain name:     ' + cert_info['sp1_domain'])
            print('\t Created time:    ' + cert_info['time_start'])
            print('\t Expiration time: ' + cert_info['time_end'])
            print('\t Valid votes:     ' + str(cert_info['valid_votes']))
            print('\t Invalid votes:   ' + str(cert_info['invalid_votes']))
            
            is_download = ''
            while True:
                print("\nDo you want to download this certificate (Y/N): ")
                is_download = input()
                print("\n")

                if is_download.lower() == 'y' or is_download.lower() == 'n':
                    break
            
            if is_download.lower() == 'y':
                print('Downloading...')
                file_name = cert_info['link_cert']+'.pdf'
                bucket_name = sub.GetBucketNameByDomain(cert_info['sp1_domain'])
                dir_path = sub.os.path.expanduser('~/Downloads/')
                sub.acc_Storj.download('sj://'+bucket_name+'/'+file_name, dir_path)

         
