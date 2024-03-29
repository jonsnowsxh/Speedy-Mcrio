import os
import sys


def main(argv):
    print(" download database, please wait ")
    # mpa4 marker gene database download
    print(" metaphlan4 database download! ")
    os.system("source ~/.bashrc ; conda activate mpa4;"
              "metaphlan --install --bowtie2db /root/database/mpa4/")

    # humann3 database download
    print("utility_mapping database download!")
    os.system("source ~/.bashrc ; conda activate mpa4;"
              "humann_databases --download utility_mapping full root/db/humann3/utility_mapping ")
    print("chocophlan database download!")
    os.system("source ~/.bashrc ; conda activate mpa4;"
              "humann_databases --download chocophlan full root/db/humann3/chocophlan")
    print("uniref90_diamond database download!")
    os.system("source ~/.bashrc ; conda activate mpa4;"
              "humann_databases --download uniref uniref90_diamond  root/db/humann3/uniref")
    print("database download successful!")



if __name__ == "__main__":
    main(sys.argv[1:])
