#!/bin/sh -e

#Site Policy : policy.cfg
#Verify, email black/white list endorsers, Black/White list cheksum

#By defaut, validate signature and hash
#For test purpuses, it could be deactivated. 
#===>Change activate to no 


#Test1 : 
#ID : GOaxJFdoEXvqAm9ArJgnZ0_ky6F
#Image: http://appliances.stratuslab.eu/images/base/ttylinux-9.7-i486-base/1.2/ttylinux-9.7-i486-base-1.2.img.gz

#../../../cli/sysadmin/src/main/python/stratus-policy-image https://marketplace.stratuslab.eu/metadata/OMd8M7ixG3toGqm8C1MhUphMJWF policy.cfg
#../../../cli/sysadmin/src/main/python/stratus-policy-image https://marketplace.stratuslab.eu/metadata/GOaxJFdoEXvqAm9ArJgnZ0_ky6F policy.cfg
../../../cli/sysadmin/src/main/python/stratus-policy-image https://marketplace.stratuslab.eu/metadata/GOaxJFdoEXvqAm9ArJgnZ0_ky6F policy.cfg
