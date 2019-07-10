import lib.data_structure as ds
import lib.sub as sub

if __name__ == "__main__":
    
    user = ds.User() # tao user
    txid = ''

    print("##########################################################")
    print("--                                                      --")
    print("--       Welcome to DEMO Decentralized CA System        --")
    print("--                                                      --")
    print("##########################################################")
    print("\n")
    print("         You are logging in to an user account!            ")  
    
    choose = 2
    while (choose != 0 ):
        print("\n")
        print("Options: ")
        print("1: Request a certificate.")
        print("2: Check if the request is accepted or not.")
        print("0: Exit")
        print('\n')
        print('Input your choice: ')
        choose = int(input())
        print('\n')

        if choose != 0 and choose != 1 and choose != 2: 
            print('Wrong input!')
            continue

        if choose == 0:
            sub.api.stop()

        elif choose == 1:
            sub_info = 'getCert'
            while True:
                    
                print("What is the domain of organization: ")
                sp1_domain = input()
                print("\n")

                print("What is your id in " + sp1_domain + ": ")
                id_user_in_sp1 = input()

                if sub.GetIdByDomain(sp1_domain) != False:
                    break

                print("\n")
                print(sp1_domain + " does not exist!")

            txid = user.UpRequest(sp1_domain,id_user_in_sp1,sub_info) # user dang request
            print("\n")
            print('Request sent!') 

        elif choose == 2:
            is_accepted = ''
            is_accepted = user.CheckResponse(txid) # user kiem tra request co duoc sp1 dong y hay ko

            if is_accepted == False:
                print("Your request was rejected")

            elif is_accepted == True:
                print("Your request was accepted")
                print("\n")
                # user lay id info cua cert_info tren chain = txid cua cert_info do
                id_cert_info = user.GetResponseIdInfo(txid)  
                print("This is your Certificate Infomation ID on chain: "+id_cert_info + "\nYou can send it to anyone!")
            
            else:
                print('The request has not responded yet!')

    