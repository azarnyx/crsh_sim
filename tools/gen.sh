: ${URL=http://0.0.0.0:8000}
# : ${URL=http://35.198.180.180:80}
: ${DATA=$HOME/startgallen/data/raw}

f () {
    i="$1"; shift
    offset="$1"; shift
    output=$i.`printf '%+06d' $offset`.png
    input=$DATA/$i.json
    
    curl -H "Content-Type: application/json" -X POST -d @$input  \
	 $URL/api/v1/getCrashImage?timeOffsetMS=$offset --output $output

    echo "$output" >&2
}

for i in 1 2 3 4 5
do
    for ms in -2000 -1000 0 1000 2000
    do  f $i $ms
    done
done
