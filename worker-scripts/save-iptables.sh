#!/bin/sh
declare -a workers=( "w01" "w02" "w03" "w04" "w05" "w06" "w07" "w08" "w09" "w10" "w11" "w12" "w13" "w14" "w15" "w16" "w17" "w18" "w19" "w20" "w21" "w22" "w23" "w24" "w25" "w26" "w27" "w28" "w29" "w30" "w31" "w32" "w33" "w34" )
#load the iptables with iptables-restore
#note that this does not save tables so they will be loast on restart/power failure
for i in "${workers[@]}"
do
	ssh -tt $i sudo /sbin/service iptables save
done
