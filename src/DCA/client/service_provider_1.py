import lib.data_structure as ds
import lib.sub as sub

if __name__ == "__main__":

    print("\n")
    print("##########################################################")
    print("--                                                      --")
    print("--       Welcome to DEMO Decentralized CA System        --")
    print("--                                                      --")
    print("##########################################################")
    print("\n")
    print("    You are logging in to a service provider account!     ")  
    
    
    choose = 2
    while (choose != 0 ):
        print("\n")
        print("Options: ")
        print("1: Sign up.")
        print("2: Sign in.")
        print("0: Exit")
        print("\n")
        print('Input your choice: ')
        choose = int(input())
        print('\n')

        if choose != 0 and choose != 1 and choose != 2: 
            print('Wrong input!\n')
            continue

        if choose == 0:
            sub.api.stop()

        elif choose == 1:
            print("What is your domain: ")
            sp1_domain = input()
            print("\n")

            sp1 = ds.Ser_Provider_1(sp1_domain)

            if sp1.UpDomain() != False:
                print("Create new domain " + sp1_domain)
                sub.GenRsaKey()
                pubkey = sp1.PutPubKey()
                print("This is your public key: " + pubkey)
        
            if sub.GetIdByDomain(sp1_domain) != False:
                print("Sign up for " + sp1_domain + " successfully!")
            else:
                print(sp1_domain + ' has already existed!')

        elif choose == 2:
            print("What is your domain: ")
            sp1_domain = input()
            print("\n")

            sp1 = ds.Ser_Provider_1(sp1_domain) 
            if sub.GetIdByDomain(sp1_domain) != False:
                print("Sign in to " + sp1_domain + " successfully!")
                
                
                choose1 = 1
                while choose1 != 0:
                    print('\n')
                    print("Options for " + sp1_domain + ": ")
                    print("1: Respond to requests.")
                    print("2: Change key.")
                    print("0: Sign out.")
                    print('\n')
                    print('Input your choice: ')
                    choose1 = int(input())
                    print('\n')

                    if choose1 != 0 and choose1 != 1 and choose1 != 2: 
                        print('Wrong input!')
                        continue

                    if choose1 == 0:
                        break

                    elif choose1 == 1:
                        l = sp1.GetListRequest() # sp1 lay list cac request
                        if len(l) > 0 :
                            print('Respond to Certificate ID:')
                            # dang thong tin response dong y hoac ko dong y len chain cua request do
                            sp1.AcceptOrReject(l[0]['id_request'],l[0]['request_cert']) 
                        else:
                            print('No request currently!')

                    elif choose1 == 2:
                        sub.GenRsaKey() # sp1 tao cap key moi
                        pubkey = sp1.PutPubKey() # dang cap key moi len chain
                        print("This is your new public key: " + pubkey)

            else:
                print('Log in failed!')



        