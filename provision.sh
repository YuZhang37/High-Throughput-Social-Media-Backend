#!/usr/bin/env bash

echo 'Start!'

echo "Install python 3.9"
# install python 3.9
# https://techviewleo.com/how-to-install-python-on-ubuntu-linux/
# https://cloudbytes.dev/snippets/upgrade-python-to-latest-version-on-ubuntu-linux
sudo apt update
sudo apt install -y software-properties-common
# https://askubuntu.com/questions/250861/auto-confirm-when-running-bash-scripts
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt install -y python3.9
# python3.9 --version
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.9 2
# https://cloudbytes.dev/snippets/upgrade-python-to-latest-version-on-ubuntu-linux
# sudo update-alternatives --config python3
# https://linuxconfig.org/how-to-change-from-default-to-alternative-python-version-on-debian-linux
echo "python 3.9 was installed"

echo "Install pip3"
# install pip3
# https://linuxize.com/post/how-to-install-pip-on-ubuntu-20.04/
# https://stackoverflow.com/questions/44455001/how-to-change-pip3-command-to-be-pip
sudo apt install -y python3-pip
# sudo python -m pip uninstall pip
# pip3 --version
# /usr/lib/python3/dist-packages is the system python3 version, it does not include pip by default, but if we install pip, it will install version 9 which is decided by the system.
# https://github.com/pypa/pip/issues/5356
# https://askubuntu.com/questions/1292972/importerror-cannot-import-name-sysconfig-from-distutils-usr-lib-python3-9
sudo apt install -y python3.9-distutils
# the soft link is actually not necessary with 
# sudo python -m pip install --no-input --upgrade --force-reinstall pip
sudo ln -s /usr/bin/pip3 /usr/bin/pip
# sudo update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1
# can use sudo ln -s /usr/bin/pip3 /usr/bin/pip, since pip doesn't exist 
# python -m pip install --upgrade pip
# https://superuser.com/questions/816143/how-to-run-pip-in-non-interactive-mode

# the commands location can be cached by terminal, close the session will remove the cache.
sudo python -m pip install --no-input --upgrade --force-reinstall pip
# can't find a better way to solve this problem, 
# pip 9.0.1 from /usr/lib/python3/dist-packages (python 3.9)
# looks like this is the system dependent pip, can't be changed,
# we can only use python -m pip to specify a specific version of pip instead of using the system pip
# or 
# sudo python -m pip install --no-input --upgrade --force-reinstall pip
# WARNING: pip is being invoked by an old script wrapper. This will fail in a future version of pip.
# Please see https://github.com/pypa/pip/issues/5599 for advice on fixing the underlying issue.
# To avoid this problem you can invoke Python with '-m pip' instead of running pip directly.
# pip 22.0.3 from /usr/local/lib/python3.9/dist-packages/pip (python 3.9)
# or
# curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
# python3.9 get-pip.py
# echo 'PATH="/home/vagrant/.local/lib/python3.9/site-packages/:$PATH"' >> ~/.bashrc

# https://stackoverflow.com/questions/56382958/pip-install-uninstall-recursively-in-non-interactive-mode

# sudo apt install -y python3-pip
# pip3 --version
# pip 9.0.1 from /usr/lib/python3/dist-packages (python 3.9)

# python -m pip install --upgrade pip
# pip 22.0.3 from /home/vagrant/.local/lib/python3.9/site-packages/pip (python 3.9)

# python -m pip install --upgrade --force-reinstall pip
# pip 22.0.3 from /home/vagrant/.local/lib/python3.9/site-packages/pip (python 3.9)

# sudo python -m pip install --upgrade pip
# The directory '/home/vagrant/.cache/pip/http' or its parent directory is not owned by the current user and the cache has been disabled. Please check the permissions and owner of that directory. If executing pip with sudo, you may want sudo's -H flag.
# The directory '/home/vagrant/.cache/pip' or its parent directory is not owned by the current user and caching wheels has been disabled. check the permissions and owner of that directory. If executing pip with sudo, you may want sudo's -H flag.

# https://stackoverflow.com/questions/43847317/cant-remove-python-pip
# sudo python -m pip install --upgrade --force-reinstall pip
# pip 22.0.3 from /usr/local/lib/python3.9/dist-packages/pip (python 3.9)
# sudo apt-get --purge autoremove python3-pip
# sudo python -m pip uninstall pip
echo "pip was installed"

echo "install pipenv"
# install pipenv
# https://pipenv-es.readthedocs.io/es/stable/
echo "cd /vagrant" >> /home/vagrant/.bashrc
echo 'export PATH="/home/vagrant/.local/bin:$PATH"' >> /home/vagrant/.bashrc
pip install pipenv
pip install --upgrade setuptools
echo "pipenv was installed"
# The scripts pipenv and pipenv-resolver are installed in '/home/vagrant/.local/bin' which is not on PATH.
#   Consider adding this directory to PATH or, if you prefer to suppress this warning, use --no-warn-script-location.
# sudo apt install software-properties-common python-software-properties
# sudo add-apt-repository ppa:pypa/ppa
# sudo apt update
# sudo apt install pipenv

echo "install command tree"
# install tree
# https://askubuntu.com/questions/572093/how-to-install-tree-with-command-line
sudo apt install tree
echo "command tree was installed"
# install mysql 8
# can't figure out a way to configure it without interaction
# https://dev.mysql.com/doc/mysql-apt-repo-quick-guide/en/#apt-repo-fresh-install
# https://dev.mysql.com/downloads/repo/apt/
# https://smallbusiness.chron.com/use-wget-ubuntu-52172.html
cd /vagrant
wget -c https://dev.mysql.com/get/mysql-apt-config_0.8.22-1_all.deb



# need to install manually

# sudo dpkg -i mysql-apt-config_0.8.22-1_all.deb
# # looks like it starts another process to deal with the selections. It doesn't block the current process. NO
# sudo apt update
# # https://manpages.ubuntu.com/manpages/bionic/man8/apt.8.html
# # sudo apt install -y mysql-server
# sudo DEBIAN_FRONTEND=noninteractivate apt install -y mysql-server
# # https://cppget.org/libmysqlclient
# # sudo apt install -y libmysqlclient-dev
# libmysqlclient-dev is necessary for django package mysqlclient
# # https://stackoverflow.com/questions/2500436/how-does-cat-eof-work-in-bash
# # In your case, "EOF" is known as a "Here Tag". Basically <<Here tells the shell that you are going to enter a multiline string until the "tag" Here. You can name this tag as you want, it's often EOF or STOP.
# # 设置mysql的root账户的密码为yourpassword
# # 创建名为twitter的数据库
# sudo mysql -u root << EOF
#   ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'yourpassword';
#   flush privileges;
#   show databases;
#   CREATE DATABASE IF NOT EXISTS twitter;
# EOF
# fi

# # superuser名字
# USER="admin"
# # superuser密码
# PASS="admin"
# # superuser邮箱
# MAIL="admin@mytwitter.com"
# script="
# from django.contrib.auth.models import User;
# username = '$USER';
# password = '$PASS';
# email = '$MAIL';
# if not User.objects.filter(username=username).exists():
#     User.objects.create_superuser(username, email, password);
#     print('Superuser created.');
# else:
#     print('Superuser creation skipped.');
# "
# printf "$script" | python manage.py shell

echo 'All Done!'


# pipenv --python 3.9
# pipenv shell
# pipenv install Django
# https://docs.djangoproject.com/en/4.0/intro/tutorial01/
# python -m django --version
