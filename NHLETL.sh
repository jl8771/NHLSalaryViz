#! /bin/bash
if [[ $# != 1 ]]
then
  echo "NHLETL.sh season_to_edit (eg. 20122013)"
  exit
fi

season_to_edit = $1

echo "Editing: $1"

echo "Starting Extract & Transform Phase"

python3 "NHLAPIETL.py" "20192020"

echo "Completed Extract & Transform Phase"

echo "Started Load Phase"

python3 "NHLCombineStats.py"

mv "~/project/nhl/stagedcsv/combinedstats.csv" "~project/nhl/processedcsv/"

echo "Completed Load Phase"