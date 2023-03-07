

cd /dockr-packages/

wget https://speedy-mcrio.oss-cn-hangzhou.aliyuncs.com/humann3.tar.gz

wget https://speedy-mcrio.oss-cn-hangzhou.aliyuncs.com/kneaddata.tar.gz

wget https://speedy-mcrio.oss-cn-hangzhou.aliyuncs.com/kraken2.tar.gz

wget https://speedy-mcrio.oss-cn-hangzhou.aliyuncs.com/lefse.tar.gz

wget https://speedy-mcrio.oss-cn-hangzhou.aliyuncs.com/qc.tar.gz

mkdir -p /root/miniconda3/envs/humann3
tar -xzf humann3.tar.gz -C /root/miniconda3/envs/humann3

mkdir -p /root/miniconda3/envs/kneaddata
tar -xzf kneaddata.tar.gz -C /root/miniconda3/envs/kneaddata

mkdir -p /root/miniconda3/envs/kraken2
tar -xzf kraken2.tar.gz -C /root/miniconda3/envs/kraken2

mkdir -p /root/miniconda3/envs/lefse
tar -xzf lefse.tar.gz -C /root/miniconda3/envs/lefse

mkdir -p /root/miniconda3/envs/qc
tar -xzf qc.tar.gz -C /root/miniconda3/envs/qc

python db_download.py

