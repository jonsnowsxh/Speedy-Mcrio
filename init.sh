yum install wget -y

wget -c https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -f

source ~/.bashrc

conda config --add channels conda-forge
conda config --add channels bioconda

conda install conda-pack -c conda-forge -y

cd /dockr-packages/

mkdir -p /root/miniconda3/envs/humann3
tar -xzf humann3.tar.gz /root/miniconda3/envs/humann3

mkdir -p /root/miniconda3/envs/kneaddata
tar -xzf kneaddata.tar.gz /root/miniconda3/envs/kneaddata

mkdir -p /root/miniconda3/envs/kraken2
tar -xzf kraken2.tar.gz /root/miniconda3/envs/kraken2

mkdir -p /root/miniconda3/envs/lefse
tar -xzf lefse.tar.gz /root/miniconda3/envs/lefse

mkdir -p /root/miniconda3/envs/mpa4
tar -xzf mpa4.tar.gz /root/miniconda3/envs/mpa4

mkdir -p /root/miniconda3/envs/qc
tar -xzf qc.tar.gz /root/miniconda3/envs/qc



