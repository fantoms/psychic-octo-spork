#!/bin/sh
#zookeeper on w01 and w02 
declare -a workers=( "w03" "w04" "w05" "w06" "w07" "w08" "w09" "w10" "w11" "w12" "w13" "w14" "w15" "w16" "w17" "w18" "w19" "w20" "w21" "w22" "w23" "w24" "w25" "w26" "w27" "w28" "w29" "w30" "w31" "w32" "w33" "w34" )
#push files with scp to each machine name in array
for i in "${workers[@]}"
do
	scp worker-iptables $i:
done
#now push the explicit zookeeper rules to w01 and w02
declare -a zookeeper_workers=( "w01" "w02" )
for i in "${zookeeper_workers[@]}"
do
        scp zookeeper-iptables $i:worker-iptables
done

