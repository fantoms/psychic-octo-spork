#!/bin/sh
#zookeeper on w01 and w02 
declare -a workers=( "w01" "w02" "w03" "w04" "w05" "w06" "w07" "w08" "w09" "w10" "w11" "w12" "w13" "w14" "w15" "w16" "w17" "w18" "w19" "w20" "w21" "w22" "w23" "w24" "w25" "w26" "w27" "w28" "w29" "w30" "w31" "w32" "w33" "w34" )

#for each worker, we will ssh in and use sudo to append the "vm.swappiness=1" to the end
for i in "${workers[@]}"
do
	ssh -tt $i sudo ./append-local-sysctl.conf.sh
done

