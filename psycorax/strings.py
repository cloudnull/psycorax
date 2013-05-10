config_file = """
# ================================= NOTES ======================================
# Use this configuration file to store sensitive information
# The config file REQUIRES at least ONE section for functionality
# Section names don't matter, however they are nice for oganizing data
# This is a sample file not all variables are needed. Use what you want too.

# Place me in "/etc/psycorax/" with permissions "0600" or "0400"

# Not all variables are needed, simply use what you need to.

# Basic System variables :
# ------------------------------------------------------------------------------
# test                           Does Nothing to anything, just performs a
#                                simple run test as if we were going to
#                                attack our environment

# ssh_port [PORT_NUMBER]         If using SSH, you can specify an SSH Port
#                                By Default this is "22"

# ssh_user [USER_NAME]           If using SSH, you can specify an SSH User
#                                By Default this is "root"

# ssh_key [PATH_TO_PRIVATE_KEY]  If you want me to monkey with instances
#                                from within the instances, I will need an
#                                SSH key. This is the path to the key file
#                                that you would like to use.

# time [time]                    Time is expressed in Minutes. As Such
#                                provide A Time that you would like the
#                                system to run between. Note that the time
#                                is a range, and A Random time will be used
#                                from the integer you choose. The Minimum
#                                Range is 1 minute.

# cc-attack [ATTACKS]            This operations makes the system attack a
#                                range between 1 and X number of instances
#                                simultaniously Default is 1.

# start                          Start The PsycoRax
# restart                        Restart The PsycoRax
# stop                           Stop The PsycoRax
# status                         Get the Status of The PsycoRax
# debug                          Turn up verbosity to over 9000
# log_level                      {debug, info, warn, critical, error}

# OpenStack variables :
# ------------------------------------------------------------------------------
# os_user [USERNAME]             Defaults to env[OS_USERNAME]
# os_apikey [API_KEY]            Defaults to env[OS_API_KEY]
# os_password [PASSWORD]         Defaults to env[OS_PASSWORD]
# os_region [REGION]             Defaults to env[OS_REGION_NAME]
# os_auth-url [AUTH_URL]         Defaults to env[OS_AUTH_URL]
# os_rax-auth {dfw,ord,lon}      Rackspace Cloud Authentication
# os_version [VERSION_NUM]       env[OS_VERSION]
# os_verbose                     Make the OpenStack Authentication Verbose
# ================================= NOTES ======================================

[basic]
log_level = info
OPENSTACK_AUTH_URL = https://10.0.0.0/tokens/v2.0
RACKSPACE_AUTH_URL = https://identity.api.rackspacecloud.com/v2.0/tokens
DB_USERNAME = databaseUsername
DB_PASSWORD = superSecretInformation
DB_HOST = localhost
DB_PORT = portNumber
DB_NAME = databaseName
DB_ENGINE = mysql

"""
