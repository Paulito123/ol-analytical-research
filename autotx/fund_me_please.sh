#!/usr/bin/expect -f

set timeout -1

set payee [lindex $argv 0]
set mnem [lindex $argv 1]

spawn txs transfer -c 1 -a $payee

expect "Enter your 0L mnemonic:\r"
send -- "$mnem\r"

expect eof