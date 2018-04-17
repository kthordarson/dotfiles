#ffmpeg aliases v1.0
#ffmpeg -framerate 12 -f image2   -pix_fmt yuv420p -i <dirin>/image-%08d.jpg <out>.mp4
#ffmpeg -r 1 -i <filein>.mp4 -r 1 "<outdir>/image-%08d.jpg"

#alias fmakevid='echo ffmpeg -framerate 24 -f image2 -pix_fmt yuv420p -i "$1/image-%08d.jpg" $2'
#alias fextract='echo ffmpeg -r 1 -i $1 -r 1 "$2/image-%08d.jpg"'
function fmakevid(){
    if [ -z $1 ]
    then
        echo "usage: fmakevid <input folder> <output filename"
        echo "missing input folder"
        return 1
    fi
    if [ -z $2 ]
    then
        echo "usage: fmakevid <input folder> <output filename"
        echo "missing output filename"
        return 1
    fi
    inputfolder=$1
    outputfolder=$2
    echo ffmpeg -framerate 24 -f image2 -pix_fmt yuv420p -i "$inputfolder/image-%08d.jpg" $outputfolder
}

function fextract(){
     if [ -z $1 ]
    then
        echo "usage: fextract <video file> <output folder>"
        echo "missing input file"
        return 1
    fi
    if [ -z $2 ]
    then
        echo "usage: fextract <video file> <output folder>"
        echo "missing output folder"
        return 1
    fi
    inputfile=$1
    outputfolder=$2
    echo ffmpeg -r 1 -i $inputfile -r 1 $outputfolder/image-%08d.jpg
}


