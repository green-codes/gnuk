init
reset halt
mdb 0x1ffff800 12
sleep 100
mww 0x40022004 0x45670123
sleep 100
mww 0x40022004 0xcdef89ab
sleep 100
mww 0x40022008 0x45670123
sleep 100
mww 0x40022008 0xcdef89ab
sleep 100
mww 0x40022010 0x00000260
sleep 100
mww 0x40022010 0x00000210
sleep 100
mwh 0x1ffff800 0x00ff
sleep 100
shutdown
