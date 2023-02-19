import sys
from configparser import ConfigParser
import os
import time

import print


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
    customDb = conn.get('parameters', 'Kraken2_db_Path')
    metaphlan4 = conn.get('parameters', 'metaphlan4')
    humann3 = conn.get('parameters', 'humann3')
    databasePath = conn.get('parameters', 'databasePath')
    pathwayDesPath = conn.get('parameters', 'pathwayDesPath')
    host_genome = conn.get('host_genome_path', 'host_genome_path')

    # process
    if not fqFilePath:
        print("error! please input Rawdata file path !")
        return
    if not sampleDescFilePath:
        print("error! please input sampleDescFile file path !")
        return
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


    # default database download
    if customDb == "default":
        print("using Kraken2  default database")
        print("-------------------------------")
        # Kraken2 database download
        os.system("mkdir -p /root/database/kraken2")
        os.system("cd /root/database/kraken2;"
        "wget https://genome-idx.s3.amazonaws.com/kraken/k2_pluspfp_16gb_20221209.tar.gz")

    # human genome download

    if host_genome == "default":
        print("human gene download!")
        os.system("mkdir -p /root/database/kneaddata/human_genome;"
              "cd /root/database/kneaddata/human_genome;"
              "wget -c ftp://hgdownload.soe.ucsc.edu/goldenPath/hg38/chromosomes/*fa.gz;"
              "gunzip *fa.gz;"
              "cat *fa > hg38.fa;"
              "rm chr*.fa")
    if host_genome == "default":
        host_genome == "/root/database/kneaddata/human_genome"


    # quality control, kneaddata, trimmomatic + bowtie2
    print("step1:running quality control! ")

    if qc == 'yes':
      os.system("source ~/.bashrc ; conda activate qc;"
      "kneaddata --version;"
      "trimmomatic --version;"
      "bowtie2 --version;"
      "time parallel -j "+jobsNumber +
      "kneaddata -i " + fqFilePath + "/{1}_1.fq.gz -i " + fqFilePath + "/{1}_2.fq.gz"
      "-o " + work_Dir + "/qc/temp/{1} -v -t " + threadsNumber + " --remove-intermediate-output"
      "--trimmomatic "+envirs+"/fastqc/share/trimmomatic/ "
      "--trimmomatic-options 'ILLUMINACLIP:"+envirs+"/fastqc/share/trimmomatic/adapters/" + adapters + ":2:40:15 "
      "SLIDINGWINDOW:10:20 MINLEN:50 -threads " + threadsNumber + "'"
      "--reorder --bowtie2-options '--very-sensitive --dovetail'"
      "-db "+host_genome+""
      "::: `tail -n+2 " + sampleDescFilePath + " | cut -f 1`; "
      "conda deactivate qc")
      # remove intermediate file
      os.system("source ~/.bashrc ; conda activate qc;"
                "for i in `tail -n+2 " + sampleDescFilePath + " ` | cut -f 1; do"
                "rm -rf " + work_Dir+"/qc/temp/${i}/*contam* "
                + work_Dir + "/qc/temp/${i}/*unmatched* ; done"
                "conda deactivate qc ")
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
                  "fastqc " + work_Dir + "/qc/temp/{1}/*_paired_?.fastq -t 4; "
                  "::: `tail -n+2 " + sampleDescFilePath + " | cut -f 1`;"
                  "mkdir -p " + work_Dir + "/qc_report ;"
                  "for i in `tail -n+2 " + sampleDescFilePath + " ` | cut -f 1; do"
                  "mv " + work_Dir + "/qc/temp/{1}/*_fastqc.zip " + work_Dir + "qc_report;")
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
        os.system(" mkdir -p " + work_Dir + "/kraken2/temp")

        if qc == 'yes':
            os.system("source ~/.bashrc ; conda activate kraken2;"
            "parallel -j "+jobsNumber+" "
            "kraken2 --db"+db+"/kraken2 --paired "+work_Dir+"/temp/qc/{1}/{1}_1_kneaddata_paired_?.fastq"
            "--threads " + threadsNumber + " --use-names --report-zero-counts"
            "--report "+work_Dir+"/kraken2/temp/{1}/{1}.report"
            "--output "+work_Dir+"/kraken2/temp/{1}/{1}.output"
            "::: `tail -n+2 " + sampleDescFilePath + " | cut -f1`"
            "conda deactivate kraken2")
        else:
            os.system("source ~/.bashrc ; conda activate kraken2;"
            "parallel -j " + jobsNumber + " "
            "kraken2 --db" + db + "/kraken2 --paired " + fqFilePath + "/{1}_paired_?.fastq"
            "--threads " + threadsNumber + " --use-names --report-zero-counts"
            "--report " + work_Dir + "/kraken2/temp/{1}/{1}.report"
            "--output " + work_Dir + "/kraken2/temp/{1}/{1}.output"
            "::: `tail -n+2 " + sampleDescFilePath + " | cut -f1`"
            "conda deactivate kraken2")

        os.system(" for i in `tail -n+2 " + sampleDescFilePath + " | cut -f 1`;do "
        "kreport2mpa.py -r +"+work_Dir+"/kraken2/temp/${i}/${i}.report"
        "--display-header"
        "-o "+work_Dir+"/kraken2/temp/${i}/${i}.mpa;done")

        os.system(" parallel -j "+jobsNumber +
        "tail -n+2 "+work_Dir+"/kraken2/temp/{1}/{1}.mpa | LC_ALL=C sort | cut -f 2 | sed '1 s/^/{1}\n/' > "+work_Dir+"/kraken2/temp/{1}/{1}_count" 
        "::: `tail -n+2 " + sampleDescFilePath + " | cut -f1`")

        os.system("header=`tail -n 1 "+sampleDescFilePath + " | cut -f 1` ")
        os.system("tail -n+2 "+work_Dir+"/kraken2/temp/${header}.mpa | LC_ALL=C sort | cut -f 1 | "
        "sed \"1 s/^/Taxonomy\n/\" >  "+work_Dir+"/kraken2/temp/0header_count")
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
            " grep 'Homo sapiens' " + work_Dir + "/kraken2/result/bracken." + i + ".txt")
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
            os.system("Rscript  /home/Speedy-Mcrio/script/alpha_boxplot.R"
            "-i" + work_Dir + "/kraken2/result/bracken." + i + ".alpha"
            "-a" + i + "-d" + sampleDescFilePath + "-n Group -w 90 -e 60 -o " + work_Dir + "/kraken2/result/alpha-bracken;done")

        os.system("mkdir -p " + work_Dir + "/kraken2/result/beta")

        beta_distance = ["euclidean", "manhattan", "jaccard", "bary_curtis"]
        for i in beta_distance:
            os.system("/home/speed-micro/program/usearch "
            "-beta_div " + work_Dir + "kraken2/result/bracken." + i + ".norm"
            "-filename_prefix" + work_Dir + "kraken2/result/beta")
            os.system("Rscript /home/Speedy-Mcrio/script/beta_pcoa.R"
                      "--input" + work_Dir + "kraken2/result/beta/"+i+".txt"
                      "--design "+sampleDescFilePath + " --group Group"
                      "--width 90 --height 60"
                      "--output " + work_Dir + "kraken2/result/beta/")


    if metaphlan4 == "yes":
        print("run metaphlan4 for species annotation, please wait!")
        os.system("mkdir -p" + work_Dir + "/metaphlan4/result")
        os.system("mkdir -p" + work_Dir + "/metaphlan4/temp")
        os.system("mkdir -p" + work_Dir + "/metaphlan4/refse ")
        os.system("source ~/.bashrc; conda activate mpa4;"
                  "metaphlan --version;"
                  "parallel - j" + jobsNumber + ""
                  " \" metaphlan + " + fqFilePath + "\{1}_1.fastq\"" + fqFilePath + "\{1}_2.fastq"
                  "--bowtie2out {1}_metagenome.bowtie2.bz2  --input_type fastq -o  " + work_Dir + "/metaphlan4/temp/{1}_profiled_metagenome.txt "
                  " ::: `tail -n+2 " + sampleDescFilePath + " | cut -f1` ")

        os.system("source ~/.bashrc; conda activate mpa4; merge_metaphlan_tables.py " + work_Dir + "/metaphlan4/temp/{1}.merged_abundance_table.txt  sed 's/_metaphlan_bugs_list//g' > " + work_Dir + "metaphlan4/result/merged_abundance_table.txt")
        os.system("source ~/.bashrc; conda activate mpa4; metaphlan_to_stamp.pl " + work_Dir + "  /metaphlan4/result/taxonomy.tsv > "+work_Dir+" metaphlan4/result/taxonomy.spf ")

        #visualization
        os.system("hclust2.py \
        -i  " + work_Dir + "metaphlan4/result/merged_abundance_table.txt\
        -o " + work_Dir + "metaphlan4/result/merged_abundance_table.txt \
        --skip_rows 1 --ftop 50  --f_dist_f correlation --s_dist_f braycurtis \
        --cell_aspect_ratio 9 -s --fperc 99 --flabel_size 4 \
        --legend_file HMP.sqrt_scale.legend.png --max_flabel_len 100 \
        --metadata_height 0.075 --minv 0.01 \
        --no_slabels --dpi 300 --slinkage complete ")

        # species annotation
        # lefse
        print("lefse analysis")
        os.system("source ~/.bashrc; conda activate lefse;"
                  "mkdir -p" + work_Dir + "/metaphlan4/lefse "
                  "lefse_format_input.py " + work_Dir + "/metaphlan4/result/lefse.txt" + work_Dir + "/metaphlan4/temp/input.in"
                  "-c 1 -o 1000000")
        os.system("run_lefse.py " + work_Dir + "/metaphlan4/temp/input.in" + work_Dir + "/metaphlan4/temp/input.res")
        os.system("lefse_plot_cladogram.py" + work_Dir + "/metaphlan4/temp/input.res" + work_Dir + "/metaphlan4/refse/lefse_res.pdf --format pdf")
        os.system(" mkdir -p" + work_Dir + "/metaphlan4/refse_all")
        os.system("lefse_plot_feature.py -f diff "
                  "--archive none --format pdf"
                  + work_Dir + "/metaphlan4/temp/input.in"
                  + work_Dir + "/metaphlan4/temp/input.res")

    # merge the data
    if qc == "yes":
        os.system(" for i in `tail -n+2 " + sampleDescFilePath + " | cut -f 1`; do "
        " mkdir -p " + work_Dir + "/temp/merge"
        " cat" + work_Dir + "/temp/qc/${i}/${i}_?.fastq " " > " + " ")

    #  run humann3
    if humann3 == "yes":
        print("run humann3 for function annotation, please wait")
        # paired reads merge
        os.system("mkdir -p " + work_Dir + "/humann3;"
                  "mkdir -p " + work_Dir + "/humann3/temp;"
                  "mkdir -p " + work_Dir + "/humann3/result;")

        os.system("source ~/.bashrc ; conda activate humann3;"
                  "humann --version;"
                  "humann_config;"
                  "parallel -j " + jobsNumber +
                  " \"humann --input   \"  " + fqFilePath + "/{1}.fastq" 
                  "--output " + work_Dir + "/humann3/temp"
                  "--threads " + threadsNumber + " --metaphlan-options=\"--bowtie2db /root/db/mpa4 \" "
                  "::: `tail -n+2 " + sampleDescFilePath + "| cut -f1 `;"
                  "source deactivate")

        os.system("humann_join_tables"
                  "--input " + work_Dir + "/humann3/temp;"
                  "--file_name pathabundance"
                  "--output " + work_Dir + "/humann3/result/pathabundance.tsv;")
        os.system("humann_renorm_table"
              "--input " + work_Dir + "/humann3/result/pathabundance.tsv;"
              "--inits relab"
              "--output " + work_Dir + "/humann3/result/pathabundance_relab.tsv;")

    # run visualization
        os.system(" head -n1  " + work_Dir + "/humann3/result/pathabundance.tsv | sed 's/# Pathway/SampleID/' | tr '\t' '\n' " + work_Dir + " /humann3/result/header ")
        os.system(" awk 'BEGIN{FS=OFS=\"\t\"}NR==FNR{a[$1]=$2}NR>FNR{print a[$1]}' " + sampleDescFilePath + " " + work_Dir + "/humann3/result/header " + " | tr '\n' '\t'|sed 's/\t$/\n/' > " + work_Dir + " /humann3/result/group")
        os.system(" cat <(head -n1 " + work_Dir + "humann3/result/pathabundance.tsv) " + work_Dir + "/humann3/result/group <(tail -n+2 " + work_Dir+" humann3/result/pathabundance.tsv) \
      > " + work_Dir + "humann3/result/pathabundance.pcl  ")

    # barplot pathway composition
        os.system(" for i in `tail -n+2 " + pathwayDesPath + " | cut -f1`;do     humann_barplot --sort sum metadata \
        --input " + work_Dir + "humann3/result/pathabundance.pcl " + "--focal-feature ${i} \
        --focal-metadata Group \
        --output " + work_Dir + " humann3/result/barplot_${i}.pdf")


if __name__ == "__main__":
    main(sys.argv[1:])
