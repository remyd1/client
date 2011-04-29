#!/bin/sh -e

#Site Policy : policy.cfg
#Verify, email black/white list endorsers, Black/White list cheksum

#By defaut, validate signature and hash
#For test purpuses, it could be deactivated. 
#===>Change activate to no 


#Test1 : 
#ID : GOaxJFdoEXvqAm9ArJgnZ0_ky6F
#Image: http://appliances.stratuslab.eu/images/base/ttylinux-9.7-i486-base/1.2/ttylinux-9.7-i486-base-1.2.img.gz

../../../cli/sysadmin/src/main/python/stratus-policy-image GOaxJFdoEXvqAm9ArJgnZ0_ky6F policy.cfg

#Test2:
#ID : GOaxJFdoEXvqAm9ArJgnZ0_ky6F
#Image: http://appliances.stratuslab.eu/images/base/ttylinux-9.7-i486-base/1.2/ttylinux-9.7-i486-base-1.2.img.gz


echo "Now changing activate to no"

sed  's/yes/no/g' policy.cfg > policy.tmp ; mv policy.tmp policy.cfg

#In policy.cfg change activate to no
../../../cli/sysadmin/src/main/python/stratus-policy-image GOaxJFdoEXvqAm9ArJgnZ0_ky6F policy.cfg 
