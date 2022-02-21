#!/bin/env python3

from werkzeug.security import generate_password_hash
import getpass
import tbsnippets




def updateuserpassword(pwd,shpwd):
    print("This is the current password: {}".format(pwd))
    print("This is the pbkdf2 hash value: {}".format(shpwd[20:]))
    # create generation SQL
    return

def createdatauser(ufn,usn,udn,aid,ua):
    newusersql= ''' INSERT into datauser(userforname,usersurname,userdisplayname,useraccessid,useragency) VALUES (%s,%s,%s,%s,%s) '''
    valuestuple= (ufn,usn,udn,aid,ua) 
    print(valuestuple)
    try:
            thisdbh=tbsnippets.sbxdbconnect('10.100.200.3','sbxuser','someP@SSwerd','tbsbx')
            thiscur=thisdbh.cursor()
            result=thiscur.execute(newusersql, valuestuple)
            thisdbh.commit()
            thisdbh.close()
            return result
    except Exception as err:
            print(err)
            return None






def main():
    quit=False
    while(not quit):
        #  Do all the intial user information collection
        print("Creating new user account for SFR")
        print("-----------------------------------\n")
        print("Collecting User information first:")
        userforename=input("User's legal forename (first, formal)? :")
        usersurname=input("User's legal surname (last)? :")
        userdisplayname=input("Name user commonly goes by, first or first last:")
        print("create user's access id in the following format:\n 2 character code for space agency \n 3 digits,first inital,2 digits, last inital")
        useraccessid=input("Access ID for user, AAdddIddi")  # 10 character string high entropy
        print("Space agency user is affiliated with, Canada,Eurpope,Japan,Russia,USA ")
        useragency=input("Space agency affiliation")
        # insert into DB
        nduresult=createdatauser(userforename,usersurname,userdisplayname,useraccessid,useragency)
        if nduresult is not None:
            print(dir(nduresult))
        # get the numeric user identifier
        # prompt for password


        print("Creating new user creds for SFR")
        pwd = getpass.getpass(prompt="Enter min 10 character password")
        if len(pwd) < 10:
            print('password is too short')
        else:
            shpwd=generate_password_hash(pwd, method='pbkdf2:sha256',salt_length=16)
            updateuserpassword(pwd,shpwd)
        

        answer=input("continue creating users? (y/n):")
        if answer[:1].lower() == 'y':
            quit=True




  

if __name__ == '__main__':
    main()