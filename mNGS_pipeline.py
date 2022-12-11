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
    qc = conn.get('parameters', 'qc')
    fastqc = conn.get('parameters', 'fastqc')
    adapters = conn.get('parameters', 'adapters')
    jobsNumber = conn.get('parameters', 'jobsNumber')
    threadsNumber = conn.get('parameters', 'threadsNumber')
    sampleDescFilePath = conn.get('parameters', 'sampleDescFilePath')
    kraken2 = conn.get('parameters', 'kraken2')
    customDb = conn.get('parameters', 'customDb')
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
        print("default parallel number 1!")
        jobsNumber = 1
    if not threadsNumber:
        print("default threads Number 4!")
        threadsNumber = 1

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
      #remove intermediate file
      os.system("source ~/.bashrc ; conda activate QC;"
                "for i in `tail -n+2 " + sampleDescFilePath + " ` | cut -f 1; do"
                "rm -rf " + work_Dir+"/temp/qc/${i}/*contam* "
                + work_Dir + "/temp/qc/${i}/*unmatched* ; done"
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
        print("run Kraken2 analyse")
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
        "sed \"1 s/^/Taxonomy\n/\" >  "+work_Dir+"temp/kraken2/0header_count")
        os.system("paste" + work_Dir + "kraken2/temp/*count > " + work_Dir + "/kraken2/result/tax_count.mpa")

        print(" run Bracken !")
        os.system("mkdir -p" + work_Dir + "/bracken/temp/")
        species = ["D", "P", "C", "O", "F", "G", "S"]
        for i in species:
            os.system("source ~/.bashrc ; conda activate kraken2;"
                      "for i in `tail -n+2`" + sampleDescFilePath + " | cut -f 1`; do"
                      "bracken -d" + customDb + " -i " + work_Dir + "/kraken2/temp/${i}.report "
                      "-r 100 -l "+i+"-t 0 -o" + work_Dir + "/bracken/temp/${i};done")
        print(" run visualization !")

        os.system(" parallel -j " + jobsNumber +
                  "tail -n+2 " + work_Dir + "/bracken/temp/{1}/{1}.mpa | LC_ALL=C sort |"
                  " cut -f 2 | sed '1 s/^/{1}\n/' > " + work_Dir + "/bracken/temp/{1}/{1}_count"
                  "::: `tail -n+2 " + sampleDescFilePath + " | cut -f1`")

        os.system("header=`tail -n1 " + sampleDescFilePath + " +|cut -f1`"
                 " 'tail -n+2 bracken/temp/{1} | LC_ALL=C sort | cut -f6 | sed \"1 s/^/{1}\n/\" > " "/bracken/{1}.count'")

        for i in species:
            os.system("paste " + work_Dir + " bracken/temp/*count > " + work_Dir + "/kraken2/result/bracken."+i+".txt;"
            " grep 'Homo sapiens' " + work_Dir + "result/kraken2/result/bracken." + i + ".txt")
            os.system("grep -v 'Homo sapiens' " + work_Dir + "/kraken2/result/bracken." + i + ".txt > " + work_Dir + "/kraken2/result/bracken." + i + ".-H ")

        # visualization
        os.system("Rscript  /home/script/kraken2alpha.R"
                  "--input " + work_Dir + "/kraken2/result/tax_count.mpa"
                  "--depth 0 "
                  "--species " + work_Dir + "/kraken2/result/tax_count.norm"
                  "--output " + work_Dir + "/kraken2/result/tax_count.alpha")
        os.system("mkdir -p " + work_Dir + "/kraken2/result/alpha-kraken2")

        alpha_diversity = ["chao1", "shannon", "invsimpson", "richness", "ACE",  "simpson"]
        for i in alpha_diversity:
            os.system("Rscript  /home/script/alpha_boxplot.R"
                  "-i" + work_Dir + "/kraken2/result/tax_count.alpha"
                  "-a" + i + "-d" + sampleDescFilePath + "-n Group -w 90 -e 60 -o " + work_Dir + "/kraken2/result/alpha;done")

        print(" visualization for bracken! ")

        for i in species:
            os.system("Rscript /home/script/otutab_rare.R"
            "--input " + work_Dir + "/kraken2/result/bracken." + i + ".-H"
            "--depth 0 --seed 1"
            "--normalize" + work_Dir + "/kraken2/result/bracken." + i + ".norm"
            "--output " + work_Dir + "/kraken2/result/bracken." + i + ".alpha")

        os.system("mkdir -p " + work_Dir + "/kraken2/result/alpha-bracken")
        for i in alpha_diversity:
            os.system("Rscript  /home/speedy-micro/script/alpha_boxplot.R"
            "-i" + work_Dir + "/kraken2/result/bracken." + i + ".alpha"
            "-a" + i + "-d" + sampleDescFilePath + "-n Group -w 90 -e 60 -o " + work_Dir + "/kraken2/result/alpha-bracken;done")

        os.system("mkdir -p " + work_Dir + "/kraken2/result/beta")

        beta_distance = ["euclidean", "manhattan", "jaccard", "bary_curtis"]
        for i in beta_distance:
            os.system("/home/speed-micro/program/usearch "
            "-beta_div " + work_Dir + "kraken2/result/bracken." + i + ".norm"
            "-filename_prefix" + work_Dir + "kraken2/result/beta")
            os.system("Rscript /home/speedy-micro/script/beta_pcoa.R"
                      "--input" + work_Dir + "kraken2/result/beta/"+i+".txt"
                      "--design "+sampleDescFilePath + " --group Group"
                      "--width 90 --height 60"
                      "--output " + work_Dir + "kraken2/result/beta/")

    #
    if metaphlan4 == "yes":
        print("run metaphlan4 for species annotation, please wait")
        os.system("source ~/.bashrc ; conda activate mpa4;"
                  " ")

    # merge the data
    if qc == "yes":
        os.system(" for i in `tail -n+2 " + sampleDescFilePath + " | cut -f 1`; do "
        " mkdir -p " + work_Dir + "/temp/merge"
        " cat" + work_Dir + "/temp/qc/${i}/${i}_?.fastq "
                                                     " > " + " ")

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




if __name__ == "__main__":
    main(sys.argv[1:])
