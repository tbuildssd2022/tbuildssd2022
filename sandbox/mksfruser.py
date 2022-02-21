#!/bin/env python3

from werkzeug.security import generate_password_hash
import getpass
import tbsnippets




def updateuserpassword(pwd,shpwd):
    print("This is the current password: {}".format(pwd))
    print("This is the pbkdf2 hash value: {}".format(shpwd[20:]))
    # create generation SQL
    return





def main():
    quit=False
    while(not quit):
        print("Creating new user account for SFR")
        #  Do all the user collection
        # insert into DB
        # get the numeric user identifier
        # prompt for password


        print("Creating new user creds for SFR")
        pwd = getpass.getpass(prompt="Enter min 10 character password")
        if len(pwd) < 10:
            print('password is too short')
        else:
            shpwd=generate_password_hash(pwd, method='pbkdf2:sha256',salt_length=16)
            updateuserpassword(pwd,shpwd)
        

        answer=raw_input("continue creating users? (y/n):")
        if answer[:1].lower() == y:
            quit=True




  

if __name__ == '__main__':
    main()