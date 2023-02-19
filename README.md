

### Step 1: install docker

  install Docker (Administrator privileges are required)

### Step 2: pull docker images

```
docker pull sidney123/sidreposit:Speedy-Mcrio
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

### Step 5: config file

```
revise the config file according to your goal
```
### Step 6:  run script

```
python mNGS_pipeline.py
```
