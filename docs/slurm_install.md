# Slrum Installation with source code
## Prerequisite
```
apt-get install git gcc make ruby ruby-dev libpam0g-dev libmariadb-dev  mariadb-server build-essential libssl-dev -y
apt install libcgroup-dev libpam-cgroup libdbus-1-dev
```
## Steps
1. install mysql
```
apt install mysql-server
```

2. build and install libjwt
dependency: apt install openssl libjansson-dev -y
```
git clone --depth 1 --single-branch -b v1.12.0 https://gitee.com/mirrors_benmcollins/libjwt  libjwt
cd libjwt
autoreconf --force --install
./configure --prefix=/usr/local
make -j
make install
```
3. install json-c http-parser
```
git clone --depth 1 --single-branch -b json-c-0.15-20200726 https://github.com/json-c/json-c.git json-c
mkdir json-c-build
cd json-c-build
cmake ../json-c
make
sudo make install
cd ..
git clone --depth 1 --single-branch -b v2.9.4 https://gitee.com/xzgan/http-parser http_parser
cd http_parser
make
sudo make install
```

4. install munge
reference: https://www.cnblogs.com/liwanliangblog/p/9194032.html
```
git clone -b munge-0.5.15  https://gitee.com/xzgan/munge
cd munge
./bootstrap
./configure --prefix=/usr/local/munge  --sysconfdir=/usr/local/munge/etc --localstatedir=/usr/local/munge/local --with-runstatedir=/usr/local/var/run --libdir=/usr/local/munge/lib64
make -j 4
make install
export PATH=/usr/local/munge/sbin/:$PATH
useradd -s /sbin/nologin -u 601 munge
sudo -u munge mkdir -p /usr/local/var/run/munge
chmod g-w /usr/local/munge/run/munge
chown -R munge.munge /usr/local/munge/
chmod 700 /usr/local/munge/etc/
chmod 711 /usr/local/munge/local/ 
chmod 755 /usr/local/var/run/munge/
chmod 711 /usr/local/munge/lib

#create key
sudo -u munge /usr/local/munge/sbin/mungekey --verbose
chmod 600 /usr/local/munge/etc/munge/munge.key
#create service
ln -s /usr/local/munge/lib/systemd/system/munge.service /usr/lib/systemd/system/munge.service
systemctl daemon-reload
systemctl start munge
systemctl status munge
```

5. Install slurm
wget https://download.schedmd.com/slurm/slurm-23.02.6.tar.bz2
Configure Slurm
```
./configure -sysconfdir=/etc/slurm/ --libdir=/usr/local/lib --with-munge=/usr/local/munge --with-jwt=/usr/local/ --with-http-parser=/usr/local/ --enable-slurmrestd
CORES=$(grep processor /proc/cpuinfo | wc -l)
make -j $CORES
make install
```

6. check 
/usr/sbin/slurmd
plugin so: 
/usr/local/lib/slurm

7. slurm auth
```
mkdir -p /var/spool/slurm
chown slurm: /var/spool/slurm
mkdir -p /var/log/slurm
chown slurm: /var/log/slurm
mkdir /var/spool/slurmctld
chown slurm.slurm /var/spool/slurm/ctld
mkdir -p  /var/spool/slurm/ctld/
cp $llm-scheduler-api/slurm/jwt_hs256.key /var/spool/slurm/ctld/
```

8. refer $llm-scheduler-api/slurm/conf and configure /etc/slurm/slurm.conf, /etc/slurm/slurmdbd.conf, /etc/slurm/slurmrestd.conf
9. start slrum daemon on every node
```
slurmdbd
slurmd
slurmctrl
```

10. config ldap for all nodes: https://computingforgeeks.com/how-to-configure-ubuntu-as-ldap-client/

11. start slurm slurmrestd in head node and configure slurm api to .env
```
slurmrestd -f /etc/slurm/slurmrestd.conf -a rest_auth/jwt 0.0.0.0:3000 -vvvv 2>&1 >> slurm.log &
```
