

### Step 1: install docker

install docker need Administrator privileges

### Step 2: pull docker images

```
docker push sidney123/sidreposit:Speedy-Mcrio
```

### Step 3: Entering the docker container, download source code

```
wget  https://github.com/jonsnowsxh/Speedy-Mcrio/archive/refs/heads/master.zip
unzip master.zip
```

### Step 4:  init environment

```
./init.sh
```

### Step 5: run script

```
python mNGS_pipeline.py
```

