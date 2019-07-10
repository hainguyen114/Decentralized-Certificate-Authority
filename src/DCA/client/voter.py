import lib.data_structure as ds
import lib.sub as sub

if __name__ == "__main__":

    print("##########################################################")
    print("--                                                      --")
    print("--       Welcome to DEMO Decentralized CA System        --")
    print("--                                                      --")
    print("##########################################################")
    print("\n")
    print("          You are logging in to a voter account!          ")  
    print("\n")

    voter = ds.Voter() # tao voter

    print("List of Certificate:\n")

    # voter lay list cac cert_info duoc up len chain
    list_cert_info = voter.GetListCertInfo() 

    i = 0
    while(i < len(list_cert_info)):
        print("CERT " + str(i))
        print("\t Organization ID: " + str(list_cert_info[i].id_sp1_in_dca))
        print("\t Domain name:     " + str(list_cert_info[i].sp1_domain))
        print("\t Created time:    " + str(list_cert_info[i].time_start))
        print("\t Expiration time  " + str(list_cert_info[i].time_end))
        print("\t Certificate ID:  " + str(list_cert_info[i].link_cert))
        print('\n')
        i += 1

    while True:
        print("\nChoose one Certificate to vote!")
        print("\n")
        print("Input a Certificate ID: ")
        link_cert_voter = input()
        print("\n")
        print("Input a Domain name: ")
        sp1_domain = input()
        dir_path = sub.path + '/temp/'

        print("\nVerifying...\n")

        # voter check cert tren storj co hop le voi pubkey tren chain
        is_valid = voter.VerifyCert(link_cert_voter,sp1_domain,sub.GetPubKeyByDomainOrId(sp1_domain),dir_path)

        if is_valid == False:
            # cac danh sach cac key cu cua sp1
            list_old_pub_key = sub.GetListOldPubkey(sub.GetPubKeyByDomainOrId(sp1_domain),[sp1_domain]) 

            i = 0
            while i < len(list_old_pub_key):
                # voter check cert tren storj co hop le voi pubkey tren chain
                is_valid = voter.VerifyCert(link_cert_voter,sp1_domain,list_old_pub_key[i], dir_path) 
                sub.os.remove(dir_path + link_cert_voter +'.pdf')
                if is_valid == True:
                    break
                i += 1
            
        print("This certificate is valid? " + str(is_valid))

        print("What kind of vote do you want to have? (Valid[V]/Invalid[I]): ")
        kind_vote = input()
        if kind_vote.lower() == 'v':
            is_valid = True
        else:
            is_valid = False

        print("Number of votes: ")
        num_vote = input()

        voter.VoteOnCert(link_cert_voter,is_valid,num_vote) # voter vote cho tung cert

        print("\nVoting done!\n")
        print("Do you want to continue to vote? (Y/N): ")
        is_continue = input()

        if is_continue.lower() == 'n':
            break
