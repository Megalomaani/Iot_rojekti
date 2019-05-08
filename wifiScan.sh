#!/bin/bash
#nmap -sP 192.168.86.0/24 | grep android*
androidConnection=false
x=1
while [ $x -le 5 ]
do

result=$(nmap -sP 192.168.86.0/24 | grep android*)
if [ "$result" = "" ]
then
  echo vit
else
  androidConnection=true
fi
x=$(( $x + 1 ))
echo "$x"
done

if [ $androidConnection=true ]
then
  echo Android connected
else
  echo Android not connected
fi

#result=$(grep android* result)
#echo $result
