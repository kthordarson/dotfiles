function whileloop
{
number=1
while [ $number -le 10 ]
do
 echo "while $number"
 number=$((number+1))
done
}
function c_loop
{
for (( i=1; i<11; i=i+1 ))
do
  echo "cloop $i"
done
}
function python_loop
{
for i in {1..10}
do
  echo "pyloop $i"
done
}
function select_loop
{
select foo in spliff donk gengja
do
    case $foo in "spliff")
    echo "select $foo"
    ;;
"donk" | "gengja")
    echo "plesk"
    ;;
*)
    echo "invalid"
    break
    ;;
esac
done
}

python_loop
