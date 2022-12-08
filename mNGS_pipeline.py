import sys
from configparser import ConfigParser
import os
import time


def main(argv):

    # parse the configuration file
    conn = ConfigParser()
    file_path = os.path.join(os.path.abspath('.'), 'configFile.ini')
    if not os.path.exists(file_path):
        raise FileNotFoundError("file not found!")

    # get parameters
    conn.read(file_path, encoding='utf-8')
    fqFilePath = conn.get('parameters', 'fqFilePath')
    qc = conn.get('parameters','qc')
    fastqc = conn.get('parameters', 'fastqc')
    adapters = conn.get('parameters', 'adapters')
    jobsNumber = conn.get('parameters', 'jobsNumber')
    sampleDescFilePath = conn.get('parameters', 'sampleDescFilePath')
    kraken2 = conn.get('parameters', 'kraken2')
    metaphlan4 = conn.get('parameters', 'metaphlan4')
    humann3 = conn.get('parameters', 'humann3')
    databasePath = conn.get('parameters', 'databasePath')

    # process
    if not fqFilePath:
        print("error! please input Rawdata file path !")
        return
    if not sampleDescFilePath:
        print("error! please input sampleDescFile file path !")
        return
    if not databasePath:
        print("error! please input database path !")
    if not jobsNumber:
        print("error! please input jobNumber !")

    # create workDir
    curDir = os.getcwd()
    curtime = time.strftime("%Y-%m-%d", time.localtime())
    work_Dir = curDir + '/' + curtime
    print(work_Dir)
    os.system("mkdir -p " + work_Dir)

    # env variable
    os.environ["envirs"] = "/root/miniconda3/envs"
    os.environ["db"] = databasePath
    envirs = os.getenv["envirs"]
    db = os.getenv["db"]

    # database download
    # default database
    if databasePath == "yes":

        print("use default database")
        print("download database, it will take a lot of time, please wait!")
        print("--------------------------------------------------------------")
        # humann3 database download
        os.system("sudo mkdir -p root/humann3")
        os.system("sudo mkdir -p root/humann3/utility_mapping")
        os.system("sudo mkdir -p root/humann3/chocophlan")
        os.system("sudo mkdir -p root/humann3/uniref")

        os.system("humann_databases --download utility_mapping full root/db/humann3/utility_mapping ")
        os.system("humann_databases --download chocophlan full root/db/humann3/chocophlan")
        os.system("humann_databases --download uniref uniref90_diamond  root/db/humann3/uniref")

    # quality control, kneaddata, trimmomatic + bowtie2
    print("step1:running quality control! ")

    if qc == 'yes':
      os.system("source ~/.bashrc ; conda activate QC;"
      "kneaddata --version;"
      "trimmomatic --version;"
      "bowtie2 --version;"
      "time parallel -j "+jobsNumber +
      "kneaddata -i " + fqFilePath + "/{1}_1.fq.gz -i " + fqFilePath + "/{1}_2.fq.gz"
      "-o " + work_Dir + "/temp/qc/{1} -v -t 4 --remove-intermediate-output"
      "--trimmomatic "+envirs+"/fastqc/share/trimmomatic/ "
      "--trimmomatic-options 'ILLUMINACLIP:"+envirs+"/fastqc/share/trimmomatic/adapters/" + adapters + ":2:40:15 "
      "SLIDINGWINDOW:10:20 MINLEN:50 -threads 4'"
      "--reorder --bowtie2-options '--very-sensitive --dovetail'"
      "-db "+db+"/kneaddata/human_genome"
      "::: `tail -n+2 " + sampleDescFilePath + " | cut -f 1`; "
      "conda deactivate QC")
      # remove intermediate file
      os.system("source ~/.bashrc ; conda activate QC;"
                "for i in `tail -n+2 " + sampleDescFilePath + " ` | cut -f 1; do"
                "rm -rf "+ work_Dir+"/temp/qc/${i}/*contam* "
                + work_Dir +"/temp/qc/${i}/*unmatched* ; done"
                "conda deactivate QC ")
    print("quality control ends!")

    # run fastqc,checking quality control, generate report
    os.system(" mkdir -p" + work_Dir)
    if fastqc == 'yes':
        print("run fastqc!")
        if qc == 'yes':
            print("run fastqc !")
            os.system("source ~/.bashrc ; conda activate fastqc;"
                  "fastqc --version;"
                  "time parallel -j "+jobsNumber +
                  "fastqc " + work_Dir + "/temp/qc/{1}/*_paired_?.fastq -t 4; "
                  "::: `tail -n+2 " + sampleDescFilePath + " | cut -f 1`;"
                  "mkdir -p " + work_Dir + "/qc_report ;"
                  "for i in `tail -n+2 " + sampleDescFilePath + " ` | cut -f 1; do"
                  "mv " + work_Dir + "/temp/qc/{1}/*_fastqc.zip " + work_Dir + "qc_report;" )
        else:
            print("run fastqc!")
            os.system("source ~/.bashrc ; conda activate fastqc;"
                      "fastqc --version;"
                      "time parallel -j " + jobsNumber +
                      "fastqc " + fqFilePath + "/*.gz -t 4; "
                      "::: `tail -n+2 " + sampleDescFilePath + " | cut -f 1`;")
        print("run multiqc !")

        if fastqc == 'yes':
            if qc == 'yes':
                os.system("source ~/.bashrc ; conda activate fastqc;"
                      "multiqc --version;"
                      "multiqc " + work_Dir + "/qc_report ;")
            else:
                os.system("source ~/.bashrc ; conda activate fastqc;"
                     "multiqc --version;"
                     "for i in `tail -n+2 " + sampleDescFilePath + " ` | cut -f 1; do"
                     "multiqc -d " + fqFilePath + "/ -o" + work_Dir + "/qc_report")

        print(" fast qc ends, generate report! ")


    # run kraken2 and Braken
    if kraken2 == "yes":
        print("run kraken2 analyse")
        os.system(" mkdir -p " + work_Dir + "/temp/kraken2")

        if qc == 'yes':
            os.system("source ~/.bashrc ; conda activate kraken2;"
            "parallel -j "+jobsNumber+" "
            "kraken2 --db"+db+"/kraken2 --paired "+work_Dir+"/temp/qc/{1}/{1}_1_kneaddata_paired_?.fastq"
            "--threads 10 --use-names --report-zero-counts"
            "--report "+work_Dir+"/temp/kraken2/{1}/{1}.report"
            "--output "+work_Dir+"/temp/kraken2/{1}/{1}.output"
            "::: `tail -n+2 " + sampleDescFilePath + " | cut -f1`"
            "conda deactivate kraken2")
        else:
            os.system("source ~/.bashrc ; conda activate kraken2;"
            "parallel -j " + jobsNumber + " "
            "kraken2 --db" + db + "/kraken2 --paired " + fqFilePath + "/{1}_paired_?.fastq"
            "--threads 10 --use-names --report-zero-counts"
            "--report " + work_Dir + "/temp/kraken2/{1}/{1}.report"
            "--output " + work_Dir + "/temp/kraken2/{1}/{1}.output"
            "::: `tail -n+2 " + sampleDescFilePath + " | cut -f1`"
            "conda deactivate kraken2")

        os.system(" for i in `tail -n+2 " + sampleDescFilePath + " | cut -f 1`;do "
        "kreport2mpa.py -r +"+work_Dir+"/temp/kraken2/${i}/${i}.report"
        "--display-header"
        "-o "+work_Dir+"/temp/kraken2/${i}/${i}.mpa;done")

        os.system(" parallel -j "+jobsNumber +
        "tail -n+2 "+work_Dir+"/temp/kraken2/{1}/{1}.mpa | LC_ALL=C sort | cut -f 2 | sed '1 s/^/{1}\n/' > "+work_Dir+"/temp/kraken2/{1}/{1}_count" 
        "::: `tail -n+2 " + sampleDescFilePath + " | cut -f1`")

        os.system("header=`tail -n 1 "+sampleDescFilePath + " | cut -f 1` ")
        os.system("tail -n+2 "+work_Dir+"/temp/kraken2/${header}.mpa | LC_ALL=C sort | cut -f 1 | "
        "sed \"1 s/^/Taxonomy\n/\" > temp/kraken2/0header_count")




    # merge the data
    if qc == "yes":
        os.system(" for i in `tail -n+2 " + sampleDescFilePath + " | cut -f`; do "
                  " mkdir -p " + work_Dir + "/temp/merge"
                  " cat" + work_Dir + "/temp/qc/${i}/${i}_?.fastq "
                  " > " + " ")

    #
    if metaphlan4 == "yes":
        print("run metaphlan4 for species annotation, please wait")
        os.system("source ~/.bashrc ; conda activate mpa4; ")

    #  run humann3
    if humann3 == "yes":
        print("run humann3 for function annotation, please wait")
        # paired reads merge

        os.system("source ~/.bashrc ; conda activate humann3;"
                  "     "
                  "     "
                  "     "
                  "     ")


        os.system("conda deactivate")


    # run visualization

    # lefse




# test for github



if __name__ == "__main__":
    main(sys.argv[1:])
