index_file_path := "\tmp\cnt.txt"
chars_file_path := ".\tmp\chars.txt"
suspended_file_path := "\tmp\suspended.txt"
sync_file_path := "\tmp\sync.txt"
FileRead, variable_value, %chars_file_path%
longString :=variable_value
myArray := StrSplit(longString, "`n")
for index, element in myArray
{
	myArray[index] := StrReplace(element, "`r", "")
}

index:=1
Locked := False
LockDuration := 30


$q::
$w::
$e::
$r::
$t::
$y::
$u::
$i::
$o::
$p::
$a::
$s::
$d::
$f::
$g::
$h::
$j::
$k::
$l::
$z::
$x::
$c::
$v::
$b::
$n::
$m::
If !Locked {
	Locked := true
	TryReadIndex()
	Send, % myArray[index]
	IncreaseIndex()
	SetTimer, UnlockInput, % -LockDuration
	return
} else {
	return
}
UnlockInput:
	Locked := false
	SetTimer, UnlockInput, off
	Return
Suspended := False

^p::
	Suspend
	Suspended := !Suspended
	SetSuspended(Suspended)
	Return

^r::Reload
return

^Left::DecreaseIndex()
^Right::IncreaseIndex()

IncreaseIndex()
{
	global index
	SetIndex(index+1)
}

DecreaseIndex()
{
	global index
	SetIndex(index-1)
}

SetIndex(newIndex)
{
	global index
	index:=newIndex
	global index_file_path
	FileDelete, %index_file_path%
	FileAppend, %index%, %index_file_path%
}

SetSuspended(val)
{
	global suspended_file_path
	FileDelete, %suspended_file_path%
	FileAppend, %val%, %suspended_file_path%
}

TryReadIndex()
{
	global index
	global sync_file_path
	FileRead, variable_value, %sync_file_path%
	if RegExMatch(variable_value, "^\d+$") {
		index:=variable_value
		FileDelete, %sync_file_path%
		return true
	}
	return false
}